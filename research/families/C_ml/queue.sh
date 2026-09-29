while pgrep -f "ml_run.py 5min lgb" >/dev/null || pgrep -f "ml_run.py 15min lgb" >/dev/null || pgrep -f "ml_run.py 1h lgb" >/dev/null; do sleep 20; done
S="atr:1:1h;atr:2:1h;atr:3:1h;atr:2:15min;atr:3:15min;usd:5;usd:10"
for M in lr et mlp rf; do python ml_run.py 1h $M "$S"; python ml_run.py 15min $M "$S"; done
python run_picture.py 15min mlp 48 "$S"
python run_picture.py 1h mlp 48 "$S"
python run_picture.py 15min lgb 48 "$S"
python knn.py 15min 200 32 "$S"
python knn.py 1h 100 32 "$S"
python knn.py 15min 200 32 "atr:2:1h;atr:3:1h" 1
python m1_level.py "atr:1:1h;atr:2:1h;atr:3:1h;usd:5;usd:10" 5
python ml_run.py 5min lgb "atr:1:1h;atr:2:1h;atr:3:1h;atr:2:15min;usd:5;usd:10"
python ensemble.py > log_ens.txt 2>&1
