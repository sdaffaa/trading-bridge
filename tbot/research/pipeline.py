"""End-to-end evaluation of one pre-registered hypothesis against frozen criteria."""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from tbot.data.bars import add_spread, stress_spread
from tbot.engine.sim import ExecConfig
from tbot.metrics.performance import max_drawdown
from tbot.metrics.robustness import bootstrap_stats, deflated_sharpe, drop_trades_sim, loss_clustering
from tbot.research import registry
from tbot.research.walkforward import ABSTAIN, _run_one, in_days, make_folds, run_grid, walk_forward
from tbot.risk.engine import RiskConfig


def exec_from(cfg: dict, **over) -> ExecConfig:
    d = dict(cfg["exec_base"])
    d.update(over)
    return ExecConfig(**d)


def risk_from(cfg: dict) -> RiskConfig:
    return RiskConfig(**cfg["risk"])


def oos_trades(grid, wf_table) -> pd.DataFrame:
    out = []
    by = {str(p): t for p, _, t, _ in grid}
    for _, f in wf_table.iterrows():
        if f["chosen"] == ABSTAIN:
            continue
        t = by[f["chosen"]]
        if t.empty:
            continue
        out.append(in_days(t, f["test_start"], f["test_end"]))
    return pd.concat(out) if out else pd.DataFrame()


def wf_stats(grid, cfg, folds, fixed_choice=None) -> dict:
    table, oos = walk_forward(grid, folds, cfg["min_train_trades"], fixed_choice)
    tr = oos_trades(grid, table)
    r = oos["ret"] if len(oos) else pd.Series(dtype=float)
    eq = (1 + r).cumprod() * cfg["initial_balance"] if len(r) else pd.Series(dtype=float)
    net = tr["net"].to_numpy() if len(tr) else np.array([])
    pf = float(net[net > 0].sum() / -net[net < 0].sum()) if (net < 0).any() else (np.inf if len(net) else np.nan)
    s = {"wf_table": table, "oos": oos, "oos_trades": tr, "n_trades": int(len(tr)),
         "net_profit": float(net.sum()), "profit_factor": pf,
         "expectancy_R": float((tr["net"] / tr["planned_risk"]).mean()) if len(tr) else np.nan,
         "total_ret": float(eq.iloc[-1] / cfg["initial_balance"] - 1) if len(eq) else np.nan,
         "max_dd": max_drawdown(eq)[0] if len(eq) else np.nan,
         "positive_fold_share": float((table["test_ret"] > 0).mean()) if len(table) else np.nan,
         "pct_profitable_days_all": float((oos["pnl"] > 0).mean()) if len(oos) else np.nan,
         "pct_profitable_days_active": float((oos.loc[oos["active"], "pnl"] > 0).mean())
         if len(oos) and oos["active"].any() else np.nan,
         "worst_day": float(r.min()) if len(r) else np.nan}
    return s


def evaluate(cls, bars: pd.DataFrame, cfg: dict, acc: dict, data_sha: str, phase: str,
             n_trials_total: int, var_trial_sr: float | None = None, workers: int = 4) -> dict:
    spec = cfg["_spec"]
    bal = cfg["initial_balance"]
    rcfg = risk_from(cfg)
    base_bars = add_spread(bars, cfg.get("extra_spread_base", 0.0))
    folds = make_folds(cfg["dev_start"], cfg["wf_start"], cfg["wf_end"], cfg["test_months"],
                       cfg["train_months"], cfg["embargo_days"])
    grid = run_grid(cls, base_bars, spec, rcfg, exec_from(cfg), bal, workers)
    period = f"{cfg['dev_start']}..{cfg['wf_end']}"
    for params, _, _, m in grid:
        registry.append({"phase": phase, "hypothesis": cls.name, "params": params, "split": "dev+wf full-span",
                         "period": period, "data_sha256": data_sha, "config_hash": registry.config_hash(
                             {k: v for k, v in cfg.items() if not k.startswith("_")}),
                         "seed": cfg["exec_base"]["seed"], "status": "ok", **{k: m.get(k) for k in registry.FIELDS
                                                                             if k in m}})
    base = wf_stats(grid, cfg, folds)
    grid_sr = [float(d["ret"].mean() / d["ret"].std(ddof=1)) if len(d) > 2 and d["ret"].std(ddof=1) > 0 else 0.0
               for _, d, _, _ in grid]
    o, rb = acc["oos"], acc["robust"]
    res = {"hypothesis": cls.name, "n_grid": len(grid), "folds": len(folds)}
    res["oos"] = {k: v for k, v in base.items() if k not in ("wf_table", "oos", "oos_trades")}
    res["wf_table"] = base["wf_table"].to_dict("records")
    r = base["oos"]["ret"].to_numpy() if len(base["oos"]) else np.array([])
    if len(r) > 30:
        bs = bootstrap_stats(r, **{k: cfg["bootstrap"][k] for k in ("n_boot", "mean_block", "seed")})
        dsr = deflated_sharpe(r, n_trials_total, var_trial_sr)
        res["bootstrap"], res["dsr"] = bs, dsr
        res["clustering"] = loss_clustering(base["oos"]["pnl"].to_numpy())
    else:
        bs, dsr = {"p_mean_le_0": 1.0}, {"dsr": 0.0}
    gates = {}
    if base["n_trades"] < o["min_trades"]:
        gates["sample"] = "INCONCLUSIVE"
    gates["profit_factor"] = base["profit_factor"] >= o["min_profit_factor"]
    gates["expectancy_R"] = (base["expectancy_R"] or -1) >= o["min_expectancy_R"]
    gates["net_positive"] = base["net_profit"] > 0
    gates["bootstrap"] = bs["p_mean_le_0"] <= o["max_p_mean_le_0"]
    gates["dsr"] = dsr["dsr"] >= o["min_dsr"]
    gates["folds"] = (base["positive_fold_share"] or 0) >= o["min_positive_fold_share"]
    lim = acc["user_limits"]["max_drawdown_frac"]
    gates["max_dd_vs_user_limit"] = "PENDING_USER_LIMIT" if lim is None else \
        base["max_dd"] <= o["max_dd_share_of_user_limit"] * lim
    core_pass = all(v is True for k, v in gates.items() if k not in ("sample", "max_dd_vs_user_limit"))
    res["p_value"] = bs["p_mean_le_0"]
    # ---- robustness only for candidates that pass the core OOS gates
    if core_pass and base["n_trades"] >= o["min_trades"]:
        rob = {}
        for name, st in cfg["stress"].items():
            b2 = stress_spread(base_bars, st.get("spread_mult", 1.0))
            ex = dict(cfg["exec_base"])
            if "slippage_mult" in st:
                ex["slippage_fixed"] *= st["slippage_mult"]
                ex["slippage_random"] *= st["slippage_mult"]
            for k in ("latency_bars", "reject_prob", "intrabar"):
                if k in st:
                    ex[k] = st[k]
            # stress the parameters actually SELECTED in the base walk-forward (no re-optimisation)
            choice = list(base["wf_table"]["chosen"])
            chosen_p = [eval(c) for c in dict.fromkeys(choice) if c != ABSTAIN]
            g2 = [_run_one((cls, p_, b2, spec, rcfg, ExecConfig(**ex), bal)) for p_ in chosen_p]
            st_res = wf_stats(g2, cfg, folds, fixed_choice=choice) if g2 else {"net_profit": 0.0,
                                                                                "expectancy_R": np.nan}
            rob[name] = st_res["net_profit"]
            rob[name + "_expectancy_R"] = st_res["expectancy_R"]
        res["stress_net"] = rob
        for name in rb["stress_net_positive"]:
            gates[f"stress_{name}"] = rob[name] > 0
        chosen = pd.Series([f for f in base["wf_table"]["chosen"] if f != ABSTAIN]).mode()[0]
        params = eval(chosen)  # str(dict) of our own grid values
        by = {str(p): (d, t) for p, d, t, _ in grid}
        nb = cls.neighbors(params)
        missing = [n for n in nb if str(n) not in by]
        for p_, d_, t_, _ in (_run_one((cls, n, base_bars, spec, rcfg, exec_from(cfg), bal)) for n in missing):
            by[str(p_)] = (d_, t_)
        wf_net = lambda d: d.loc[cfg["wf_start"]:cfg["wf_end"], "pnl"].sum()
        nets = {str(n): float(wf_net(by[str(n)][0])) for n in nb}
        share = float(np.mean([v > 0 for v in nets.values()])) if nb else None
        res["neighbors"] = {"center": chosen, "n": len(nb), "positive_share": share, "nets": nets}
        gates["neighbors"] = "N/A_NO_ORDINAL_PARAMS" if share is None else share >= rb["min_neighbor_positive_share"]
        tr = base["oos_trades"]["net"].to_numpy()
        srt = np.sort(tr)[::-1]
        k = max(1, int(np.ceil(0.05 * len(srt))))
        gates["ex_top5pct"] = srt[k:].sum() >= rb["net_ex_top5pct_trades_min"]
        d10 = drop_trades_sim(tr, 0.10, seed=cfg["bootstrap"]["seed"])
        res["drop10"] = d10
        gates["drop10"] = d10["p5"] > rb["drop10_p5_min"]
        yr = base["oos"]["pnl"].groupby(base["oos"].index.year).sum()
        pos = yr[yr > 0]
        res["by_year"] = {int(k): float(v) for k, v in yr.items()}
        gates["year_concentration"] = (pos.max() / yr.sum() <= rb["max_single_year_profit_share"]) \
            if yr.sum() > 0 else False
        gates["positive_years"] = (yr > 0).mean() >= rb["min_positive_year_share"]
    res["gates"] = {k: (v if isinstance(v, str) else bool(v)) for k, v in gates.items()}
    res["_grid_sharpes"] = grid_sr
    res["_oos_ret"] = r.tolist()
    res["verdict"] = decide(res)
    return res


def decide(res: dict) -> str:
    g = res["gates"]
    if g.get("sample") == "INCONCLUSIVE":   # brief §9: insufficient sample => undecided, never accept
        return "INCONCLUSIVE"
    if any(v is False for v in g.values()):
        return "REJECT"
    if "stress_net" not in res:
        return "REJECT"
    if any(v == "PENDING_USER_LIMIT" for v in g.values()):
        return "CANDIDATE_PENDING_USER_LIMITS"
    return "CANDIDATE_FOR_HOLDOUT"
