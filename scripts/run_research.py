"""Run the pre-registered research pipeline.

  python scripts/run_research.py --data data/processed/XAUUSD --spec configs/instrument_xauusd_TEMPLATE.json
  python scripts/run_research.py --synthetic   # pipeline dry-run on a random walk (expected: no edge)

Never touches the hold-out period (it is sliced away here; see scripts/run_holdout.py).
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tbot.data.bars import trading_day  # noqa: E402
from tbot.data.quality import quality_report, sha256_frame  # noqa: E402
from tbot.data.synthetic import random_walk_bars  # noqa: E402
from tbot.instrument import load_instrument  # noqa: E402
from tbot.metrics.robustness import deflated_sharpe, holm  # noqa: E402
from tbot.research.pipeline import decide, evaluate  # noqa: E402
from tbot.strategies.hypotheses import ALL  # noqa: E402


def load_parquets(d: Path, start, end_excl) -> pd.DataFrame:
    """Bars whose TRADING DAY (17:00 NY cutoff) is in [start, end_excl)."""
    files = sorted(d.glob("*.parquet"))
    df = pd.concat(pd.read_parquet(f) for f in files).sort_index()
    df = df[~df.index.duplicated()]
    td = pd.to_datetime(trading_day(df.index))
    return df[(td >= pd.Timestamp(start)) & (td < pd.Timestamp(end_excl))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data")
    ap.add_argument("--spec", default=str(ROOT / "configs/instrument_xauusd_TEMPLATE.json"))
    ap.add_argument("--config", default=str(ROOT / "configs/research.json"))
    ap.add_argument("--acceptance", default=str(ROOT / "configs/acceptance.json"))
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--synthetic-edge", action="store_true",
                    help="positive control: inject +drift 03:00-08:00 NY; H5 long (3,8) must be detected")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=str(ROOT / "reports"))
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text())
    acc = json.loads(Path(a.acceptance).read_text())
    cfg["_spec"] = load_instrument(a.spec)
    out = Path(a.out)
    if a.synthetic:
        cfg.update({"dev_start": "2019-01-01", "wf_start": "2020-01-01", "wf_end": "2023-07-01", "train_months": 12})
        days = (pd.Timestamp(cfg["wf_end"]) - pd.Timestamp(cfg["dev_start"])).days
        drift = (3, 8, 0.004) if a.synthetic_edge else None
        bars = random_walk_bars(days=days, seed=42, start=cfg["dev_start"], price=1800.0, drift=drift)
        phase = "pipeline-test-synthetic" + ("-edge" if drift else "")
        out = out / ("synthetic_edge" if drift else "synthetic_dryrun")
    else:
        bars = load_parquets(Path(a.data), cfg["dev_start"], cfg["wf_end"])
        assert pd.to_datetime(trading_day(bars.index)).max() < pd.Timestamp(cfg["holdout_start"]), \
            "hold-out leaked into research data"
        phase = "research-wf"
    out.mkdir(parents=True, exist_ok=True)
    qa = quality_report(bars)
    (out / "data_quality.json").write_text(json.dumps(qa, indent=1, default=str))
    print("QA verdict:", qa["verdict"], "coverage", round(qa.get("coverage", 0), 4))
    if qa["verdict"] == "FAIL" and not a.synthetic:
        sys.exit("Data quality FAIL — stop (see data_quality.json)")
    data_sha = qa["sha256"]
    classes = [c for c in ALL if not a.only or c.name in a.only]
    n_trials = sum(len(c.grid()) for c in ALL)   # all pre-registered grid points count as trials
    results = []
    for cls in classes:
        print("evaluating", cls.name, len(cls.grid()), "configs", flush=True)
        res = evaluate(cls, bars, cfg, acc, data_sha, phase, n_trials, None, a.workers)
        results.append(res)
        print("  ->", res["verdict"], {k: res["oos"][k] for k in ("n_trades", "net_profit", "profit_factor")},
              flush=True)
    # pooled multiple-testing corrections
    all_sr = np.concatenate([r["_grid_sharpes"] for r in results])
    var_sr = float(np.var(all_sr, ddof=1)) if len(all_sr) > 1 else 0.0
    # Holm family is ALWAYS the 5 pre-registered hypotheses; unevaluated ones enter with p=1
    pv = {c.name: 1.0 for c in ALL}
    pv.update({r["hypothesis"]: r["p_value"] for r in results})
    names = list(pv)
    adj = dict(zip(names, holm([pv[n] for n in names])))
    ps = [adj[r["hypothesis"]] for r in results]
    for r, ph in zip(results, ps):
        x = np.array(r.pop("_oos_ret"))
        if len(x) > 30:
            r["dsr"] = deflated_sharpe(x, n_trials)          # null variance (D-009)
            r["dsr"]["empirical_cross_trial_var"] = var_sr   # reported for transparency only
            if r["gates"].get("dsr") is not None:
                r["gates"]["dsr"] = bool(r["dsr"]["dsr"] >= acc["oos"]["min_dsr"])
        r["holm_p"] = ph
        r["gates"]["holm"] = bool(ph <= acc["oos"]["max_holm_p"])
        r["verdict"] = decide(r)
        r.pop("_grid_sharpes")
        (out / f"wf_{r['hypothesis']}.json").write_text(json.dumps(r, indent=1, default=str))
    summary = [{"hypothesis": r["hypothesis"], "verdict": r["verdict"], **{k: r["oos"][k] for k in
               ("n_trades", "net_profit", "profit_factor", "expectancy_R", "max_dd", "positive_fold_share",
                "pct_profitable_days_all", "pct_profitable_days_active")},
                "p_boot": r["p_value"], "holm_p": r["holm_p"], "dsr": r.get("dsr", {}).get("dsr")}
               for r in results]
    pd.DataFrame(summary).to_csv(out / "summary.csv", index=False)
    print(pd.DataFrame(summary).to_string())


if __name__ == "__main__":
    main()
