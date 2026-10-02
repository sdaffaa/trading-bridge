# -*- coding: utf-8 -*-
"""سحب الأسعار من Twelve Data ومقابلتها بالنوافذ المحفوظة، شمعةً بشمعة.

⚠ الشبكة: `api.twelvedata.com` مرفوض من بوابة خروج هذه الجلسة (403). الملف
   مكتوب ليُشغَّل كما هو في بيئة يُسمح فيها بالمضيف — على جهازك أو خادمك.
   لم أمرّره عبر صندوق خارجي: ذلك يلتف على سياسة البيئة **ويسرّب مفتاحك**
   إلى طرف ثالث.

المفتاح يُقرأ من `.env` غير المتعقَّب ولا يُطبع ولا يُمرَّر في أي وسيط.

الاستخدام:
    python3 twelvedata_fetch.py pull  XAU/USD 5min 2026-08-04
    python3 twelvedata_fetch.py check gc_td2_2026-08-04.json XAU/USD
"""
import json, os, sys, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
RAW = os.path.join(HERE, "raw_windows")
BASE = "https://api.twelvedata.com"


def key():
    for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
        if line.startswith("TWELVEDATA_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("لا مفتاح TWELVEDATA_API_KEY في .env")


def get(path, **q):
    q["apikey"] = key()
    url = f"{BASE}/{path}?" + urllib.parse.urlencode(q)
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            d = json.load(r)
    except Exception as e:
        raise SystemExit(f"تعذّر الوصول إلى api.twelvedata.com: {e}\n"
                         "إن كان الرفض من بوابة الخروج فالمضيف غير مسموح هنا.")
    if isinstance(d, dict) and d.get("status") == "error":
        raise SystemExit(f"خطأ من المزوّد: {d.get('message')}")
    return d


def series(symbol, interval, start=None, end=None, n=500):
    q = dict(symbol=symbol, interval=interval, outputsize=n, timezone="UTC",
             order="ASC")
    if start: q["start_date"] = start
    if end: q["end_date"] = end
    d = get("time_series", **q)
    return [dict(d=v["datetime"], o=float(v["open"]), h=float(v["high"]),
                 l=float(v["low"]), c=float(v["close"])) for v in d["values"]]


def check(fname, symbol, tf="5m", interval="5min"):
    """يقابل نافذة محفوظة بسلسلة المزوّد ويطبع الفروق.

    مهم: عقود COMEX (GC=F) ليست الفوري (XAU/USD). الفرق الثابت بينهما
    هو الـbasis وليس خطأ — لذلك يُحسب الوسيط ويُطرح قبل المقارنة، ويُقاس
    **الشكل** لا المستوى: هل القمم والقيعان في مواضعها نفسها.
    """
    w = json.load(open(os.path.join(RAW, fname), encoding="utf-8"))[tf]["rows"]
    a, b = w[0][0], w[-1][0]
    s = series(symbol, interval, start=a, end=b)
    idx = {r["d"][:16]: r for r in s}
    rows, diffs = [], []
    for r in w:
        k = r[0][:16]
        if k not in idx:
            rows.append((k, None)); continue
        m = idx[k]
        diffs.append(m["c"] - r[4])
        rows.append((k, dict(mine=r, theirs=m)))
    hit = [x for _, x in rows if x]
    if not hit:
        print("لا تقاطع زمني بين النافذة والسلسلة"); return
    diffs.sort()
    base = diffs[len(diffs) // 2]                      # الوسيط = الـbasis
    print(f"{fname} · {tf} مقابل {symbol} {interval}")
    print(f"شموع مشتركة: {len(hit)} من {len(w)} | إزاحة المستوى (وسيط الفرق): {base:,.2f}")
    worst = []
    for k, x in rows:
        if not x: continue
        mine, th = x["mine"], x["theirs"]
        d = max(abs(th["h"] - base - mine[2]), abs(th["l"] - base - mine[3]))
        worst.append((d, k, mine, th))
    worst.sort(reverse=True)
    rng = max(r[2] for r in w) - min(r[3] for r in w)
    print(f"مدى النافذة: {rng:,.2f} | أسوأ انحراف بعد طرح الإزاحة: "
          f"{worst[0][0]:,.2f} ({worst[0][0]/rng*100:.1f}٪ من المدى)")
    for d, k, mine, th in worst[:5]:
        print(f"  {k}  عندي H {mine[2]:,.2f} L {mine[3]:,.2f} | "
              f"عندهم H {th['h']-base:,.2f} L {th['l']-base:,.2f}  → فرق {d:,.2f}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); raise SystemExit
    if sys.argv[1] == "pull":
        sym, iv, day = sys.argv[2], sys.argv[3], sys.argv[4]
        s = series(sym, iv, start=f"{day} 00:00:00", end=f"{day} 23:59:00")
        print(json.dumps(s, ensure_ascii=False, indent=1))
    elif sys.argv[1] == "check":
        check(sys.argv[2], sys.argv[3], *(sys.argv[4:6] or []))
