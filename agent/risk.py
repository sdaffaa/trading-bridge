"""Risk management — turn a directional call into a sized trade plan.

Given entry / stop-loss / take-profit, computes reward:risk and (when the
account balance + risk% are configured) the dollar risk and a rough position
size. Kept separate so both the data-mode tool and the vision coordinator use
the same math.
"""
from . import config


def compute(action: str, entry: float, sl: float, tp: float) -> dict:
    out = {"entry": entry or None, "stop_loss": sl or None,
           "take_profit": tp or None, "risk_reward": None}
    if action not in ("long", "short") or not entry or not sl:
        return out
    stop_dist = abs(entry - sl)
    out["stop_distance"] = round(stop_dist, 5)
    out["risk_percent"] = config.RISK_PERCENT
    if tp and stop_dist:
        out["risk_reward"] = round(abs(tp - entry) / stop_dist, 2)
        out["meets_min_rr"] = out["risk_reward"] >= config.MIN_RR
    if config.ACCOUNT_BALANCE > 0 and stop_dist > 0:
        risk_amt = config.ACCOUNT_BALANCE * config.RISK_PERCENT / 100.0
        out["risk_amount"] = round(risk_amt, 2)
        # rough size: units such that a full-stop move loses risk_amount
        out["suggested_units"] = round(risk_amt / stop_dist, 2)
    return out
