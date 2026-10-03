"""Trading methodology — encodes the user's defined method for the agent.

Mirrors the repo's methodology skills (ict / smc / volume-profile / footprint /
chart-confluence-analysis) as concise, actionable analysis instructions injected
into the agent's system prompt. Selected via AGENT_METHODOLOGY.
"""
from . import config

ICT = (
    "ICT lens: treat recent swing highs/lows (liquidity_above / liquidity_below) "
    "as liquidity pools; a sweep of that liquidity followed by displacement is a "
    "high-quality signal. Prefer entries into an unfilled Fair Value Gap aligned "
    "with the higher-timeframe direction (fair_value_gaps). Favor optimal-trade-"
    "entry pullbacks, not chasing mid-move.")

SMC = (
    "SMC lens: read market_structure — a valid long needs bullish structure "
    "(HH/HL) or a confirmed change of character (CHoCH) up; short is the mirror. "
    "Enter on a pullback into a point of interest (order block / demand-supply near "
    "a swing), not into open space. Inducement/liquidity sweeps before the move "
    "strengthen the setup.")

VOLUME_PROFILE = (
    "Volume Profile lens: use volume_profile (POC, VAH, VAL). Longs are stronger "
    "from value rejection at VAL or a retest above VAH; shorts mirror. Beware "
    "trading into the POC (high-volume magnet) or a high-volume node ceiling. "
    "Acceptance outside value signals continuation; rejection signals reversion.")

FOOTPRINT = (
    "Footprint/order-flow lens: use volume_state as a proxy — expansion in the "
    "trade direction confirms; contraction or expansion against it warns of "
    "absorption/exhaustion. If volume_state is no_volume_data, say order-flow "
    "confirmation is unavailable and lean on the other lenses.")

CONFLUENCE = (
    "Apply ALL FOUR schools in layered confluence and produce ONE graded plan:\n"
    f"- {SMC}\n- {ICT}\n- {VOLUME_PROFILE}\n- {FOOTPRINT}\n"
    "GRADE the setup by agreement: A-setup = 3-4 schools align (confidence ~0.8), "
    "B-setup = 2 align (~0.6), C-setup = 1 (~0.4). If schools conflict, choose "
    "no_trade or alert_human.\n"
    "DEFINE THE TRADE with risk: entry at the POI/FVG/value edge; stop-loss beyond "
    "the structural invalidation (past the swing that would break the idea); "
    "take-profit at the opposing liquidity or value-area edge. Require reward:risk "
    ">= the configured minimum or downgrade to no_trade. In your reason, name which "
    "schools aligned and the exact levels (entry, invalidation, target).")

_MAP = {"ict": ICT, "smc": SMC, "volume_profile": VOLUME_PROFILE,
        "footprint": FOOTPRINT, "confluence": CONFLUENCE}


def instructions() -> str:
    picks = [m.strip().lower() for m in config.METHODOLOGY if m.strip()]
    if not picks or "confluence" in picks:
        return CONFLUENCE
    if len(picks) == 1 and picks[0] in _MAP:
        return _MAP[picks[0]]
    # a custom subset of schools: stack the selected lenses + a grading note
    chosen = [_MAP[p] for p in picks if p in _MAP]
    if not chosen:
        return CONFLUENCE
    return ("Apply these lenses in confluence and grade by agreement "
            "(more lenses aligned => higher confidence; conflict => no_trade):\n- "
            + "\n- ".join(chosen))
