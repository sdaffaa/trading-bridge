import numpy as np
from numba import njit
@njit
def sim(o, h, l, idx, dirs, dists, spread):
    out = np.zeros(len(idx), np.int8); endj = np.zeros(len(idx), np.int64)
    n = len(o)
    for k in range(len(idx)):
        i, d, dist = idx[k], dirs[k], dists[k]
        e = o[i] + spread if d > 0 else o[i]  # bars are BID: buy at ask, sell at bid
        for j in range(i, n):
            if d > 0:
                if l[j] <= e - dist: out[k] = -1; break
                if h[j] >= e + dist: out[k] = 1; break
            else:
                if h[j] + spread >= e + dist: out[k] = -1; break
                if l[j] + spread <= e - dist: out[k] = 1; break
        endj[k] = j
    return out, endj

