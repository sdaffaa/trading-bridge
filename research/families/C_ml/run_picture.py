import sys, time, common as C, ml_run as R, picture as P
TF, model, N = sys.argv[1], sys.argv[2], int(sys.argv[3])
b, Xp = P.picture(TF, N)
for s in sys.argv[4].split(";"):
    t = time.time(); R.run(TF, model, R.parse(s), Xextra=Xp, tag=f"_pic{N}"); print("  time", round(time.time() - t), flush=True)
