"""Rule evaluator shared by rule_search.py and finalize.py."""
import numpy as np
from numba import njit


@njit(cache=True)
def rule_dir(x, kind, f, q, s, K, A, QT):
    if kind == 0:
        v = 0.0
        for k in range(K):
            z = x[f[k]]
            if z == z:
                v += s[k] * (1.0 if z > QT[f[k], q[k]] else -1.0)
        if v == 0.0:
            return 1.0 if s[0] > 0 else -1.0
        return 1.0 if v > 0 else -1.0
    else:
        ok = True
        for k in range(K):
            z = x[f[k]]
            if not (z == z) or s[k] * (z - QT[f[k], q[k]]) <= 0:
                ok = False; break
        if ok:
            return A
        z = x[f[K]]
        if not (z == z):
            return 1.0
        return s[K] * (1.0 if z > QT[f[K], q[K]] else -1.0)



@njit(cache=True)
def rule_dir_all(X, kind, f, q, s, K, A, QT):
    n = X.shape[0]; out = np.zeros(n)
    for i in range(n):
        out[i] = rule_dir(X[i], kind, f, q, s, K, A, QT)
    return out
