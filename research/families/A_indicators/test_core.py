import time, numpy as np
from core import *
t=time.time(); E=Engine(); print("tree",time.time()-t)
i0,i1=E.rng("IS"); print(i0,i1)
a=H.atr(H.bars("1h")); dist=2*H.htf_to_m1(a,"1h")
t=time.time(); lx,lw,sx,sw=E.tables(dist,i0,i1); print("tables",time.time()-t)
n=len(E.m1); rng=np.random.default_rng(1)
for name,d in (("long",np.ones(n)),("rand",rng.choice([-1.,1.],n))):
    d=d.copy(); d[:i0]=0
    t=time.time(); nn,w=walk_m1(d.astype(np.int8),lx,lw,sx,sw,i0,i1); t1=time.time()-t
    st=H.stats(H.run_consecutive(d,dist))
    print(name,nn,round(100*w/nn,2),t1, st["IS"])
d=np.full(n,5.0); t=time.time(); E.tables(d,i0,i1); print("tables $5",time.time()-t)
d=np.full(n,60.0); t=time.time(); E.tables(d,i0,i1); print("tables $60",time.time()-t)
