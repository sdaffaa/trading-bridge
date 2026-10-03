"""Position-size feasibility: can the smallest allowed order respect the risk limit?

usage: python scripts/feasibility.py --spec configs/instrument_xauusd_TEMPLATE.json \
           --capital 1000 --risk 0.005 --stops 2 5 10 20 --spread 0.30
Output is CONDITIONAL on the spec file; if spec.verified is false the result is labelled UNVERIFIED.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tbot.instrument import load_instrument  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--capital", type=float, nargs="+", required=True)
    ap.add_argument("--risk", type=float, required=True, help="fraction of equity per trade, e.g. 0.005")
    ap.add_argument("--stops", type=float, nargs="+", required=True, help="stop distances in price units ($/oz)")
    ap.add_argument("--spread", type=float, default=0.0, help="spread+slippage allowance in price units")
    a = ap.parse_args()
    s = load_instrument(a.spec)
    tag = "" if s.verified else "  [UNVERIFIED SPEC - illustrative only]"
    print(f"{s.symbol}: contract {s.contract_size}, min lot {s.volume_min}, step {s.volume_step}, "
          f"commission/side/lot {s.commission_per_lot_side}{tag}")
    print(f"{'capital':>9} {'stop':>6} {'budget':>8} {'risk@minlot':>12} {'vol':>6} {'eff.risk%':>9}  verdict")
    for cap in a.capital:
        for st in a.stops:
            budget = a.risk * cap
            per_lot = (st + a.spread) * s.value_per_price_unit(1.0) + 2 * s.commission_per_lot_side
            vol = s.floor_volume(budget / per_lot)
            minrisk = per_lot * s.volume_min
            eff = vol * per_lot / cap * 100 if vol else minrisk / cap * 100
            verdict = "OK" if vol > 0 else "INFEASIBLE (min lot exceeds risk budget)"
            print(f"{cap:9.0f} {st:6.2f} {budget:8.2f} {minrisk:12.2f} {vol:6.2f} {eff:9.3f}  {verdict}")
        min_cap = [(st, ((st + a.spread) * s.value_per_price_unit(s.volume_min)
                         + 2 * s.commission_per_lot_side * s.volume_min) / a.risk) for st in a.stops]
        print("  minimum capital for 1 min-lot at this risk: " + ", ".join(f"stop {st}: {c:.0f}" for st, c in min_cap))


if __name__ == "__main__":
    main()
