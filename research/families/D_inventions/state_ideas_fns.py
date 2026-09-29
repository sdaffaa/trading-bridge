"""State-dependent consecutive runner (identical fills via harness.trade_once)."""
import numpy as np
from numba import njit
import core  # noqa (sets sys.path)
import harness as H


@njit(cache=True)
def run_state(o, h, l, dist, spread, i0, i1, mode, k):
    n = len(o)
    ent = np.empty(n // 2, np.int64); ex = np.empty(n // 2, np.int64)
    res = np.empty(n // 2, np.int8); side = np.empty(n // 2, np.int8)
    m = 0; i = i0; last_move = 1.0; last_side = 1.0; last_res = 1; streak = 0
    while i < i1:
        d = dist[i]
        if not (d > 0):
            i += 1; continue
        if mode == 0:   s = last_move                      # barrier momentum
        elif mode == 1: s = -last_move                     # barrier reversion
        elif mode == 2: s = last_side if last_res > 0 else -last_side   # win-stay lose-shift
        elif mode == 3: s = -last_side if last_res > 0 else last_side   # win-shift lose-stay
        elif mode == 4: s = -last_move if streak >= k else last_move    # follow, fade after k
        else:           s = last_move if streak >= k else -last_move    # fade, follow after k
        r, j = H.trade_once(o, h, l, i, s, d, spread)
        if r == 0:
            break
        ent[m] = i; ex[m] = j; res[m] = r; side[m] = 1 if s > 0 else -1; m += 1
        mv = s if r > 0 else -s
        streak = streak + 1 if mv == last_move else 1
        last_move = mv; last_side = s; last_res = r
        i = j + 1
    return ent[:m], ex[:m], res[:m], side[:m]


