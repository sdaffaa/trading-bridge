# -*- coding: utf-8 -*-
"""قارئ شموع من تصدير المتداول — لريل «الصفقة تنرسم جدامك».

🔒 القاعدة الصفرية في بريف فهد: «شموع حقيقية من تريدنق فيو فقط… ممنوع
منعاً باتاً اختراع أي شمعة أو سعر». فهذا الملف **يقرأ ولا يولّد**، ويرفض
كل ما لا يستطيع التحقّق منه بدل أن يُصلحه بالتخمين:

  · صفٌّ ناقص عمودًا أو فيه قيمة غير رقمية      ← يُرفض الملف كله
  · high < low أو الإغلاق خارج [low, high]      ← يُرفض (شمعة مستحيلة)
  · فجوة زمنية غير منتظمة بين شمعتين            ← يُرفض ويُذكر موضعها
  · تكرار طابع زمني                              ← يُرفض

لماذا يُرفض الملف كله لا الصفّ وحده: حذف صفٍّ يجعل الشموع تُرسم متلاصقة
فتوهم أن السعر تحرّك بلا انقطاع — وهي القاعدة نفسها التي ترفض بها
`scan_setups` النوافذَ ذات الفجوات.

الصيغ المقبولة:
  · CSV بترويسة تحوي time/date + open/high/low/close (تصدير تريدنق فيو)
  · JSON: قائمة كائنات بمفاتيح d/o/h/l/c أو time/open/high/low/close

    python3 xau_load.py <ملف> [--tf 15m]
"""
import csv
import datetime as dt
import json
import os
import sys

_T = ("time", "date", "datetime", "timestamp", "d")
_O = ("open", "o"); _H = ("high", "h"); _L = ("low", "l"); _C = ("close", "c")
TF_MIN = {"1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30, "1h": 60, "4h": 240}


def _pick(row, names):
    for k in row:
        if k and k.strip().lower().lstrip("﻿") in names:
            return row[k]
    return None


def _ts(v):
    """طابع زمني من نصٍّ أو رقم. الأرقام تُقرأ ثوانيَ منذ الحقبة."""
    s = str(v).strip()
    if s.replace(".", "", 1).isdigit() and len(s.split(".")[0]) >= 9:
        n = float(s)
        if n > 1e11:                       # مللي ثانية
            n /= 1000.0
        return dt.datetime.utcfromtimestamp(n)
    s = s.replace("T", " ").replace("Z", "").strip()
    for f in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d",
              "%d/%m/%Y %H:%M", "%m/%d/%Y %H:%M", "%Y/%m/%d %H:%M"):
        try:
            return dt.datetime.strptime(s[:len(f) + 2].strip(), f)
        except ValueError:
            pass
    raise ValueError(f"طابع زمني غير مفهوم: {v!r}")


def _rows_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096); f.seek(0)
        try:
            dial = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dial = csv.excel
        return list(csv.DictReader(f, dialect=dial))


def load(path, tf=None):
    """يُرجع (شموع، تقرير). الشموع بصيغة المحرّك: d/o/h/l/c مع `utc`."""
    raw = (json.load(open(path, encoding="utf-8"))
           if path.lower().endswith(".json") else _rows_csv(path))
    if isinstance(raw, dict):
        raw = raw.get("candles") or raw.get("rows") or raw.get("data") or []
    if not raw:
        raise ValueError("الملف فارغ — لا صفوف")

    out = []
    for i, r in enumerate(raw):
        got = [_pick(r, _T), _pick(r, _O), _pick(r, _H), _pick(r, _L), _pick(r, _C)]
        if any(v is None or str(v).strip() == "" for v in got):
            raise ValueError(f"الصف {i+1}: عمود ناقص — الأعمدة المطلوبة "
                             f"time/open/high/low/close (الموجود: {list(r)})")
        t = _ts(got[0])
        try:
            o, h, l, c = (float(str(v).replace(",", "")) for v in got[1:])
        except ValueError as e:
            raise ValueError(f"الصف {i+1}: قيمة غير رقمية — {e}")
        if not (l <= o <= h and l <= c <= h and h >= l):
            raise ValueError(f"الصف {i+1} ({t}): شمعة مستحيلة "
                             f"o={o} h={h} l={l} c={c}")
        out.append(dict(utc=t, d=t.strftime("%H:%M"), o=o, h=h, l=l, c=c))

    out.sort(key=lambda k: k["utc"])
    ts = [k["utc"] for k in out]
    if len(set(ts)) != len(ts):
        raise ValueError("طوابع زمنية مكرّرة — التصدير فيه صفوف مضاعفة")

    # انتظام الفريم: الفارق الأغلب هو الفريم، وأي فارق يخالفه فجوة
    gaps = [(ts[i + 1] - ts[i]).total_seconds() / 60 for i in range(len(ts) - 1)]
    step = min(set(gaps), key=lambda g: (-gaps.count(g), g)) if gaps else 0
    if tf and TF_MIN.get(tf) and abs(step - TF_MIN[tf]) > 1e-6:
        raise ValueError(f"الفريم المطلوب {tf} ({TF_MIN[tf]}د) والفارق الأغلب "
                         f"في الملف {step:g}د — الملف ليس على هذا الفريم")
    bad = [i for i, g in enumerate(gaps) if abs(g - step) > 1e-6]
    if bad:
        j = bad[0]
        raise ValueError(f"فجوة زمنية: {ts[j]:%Y-%m-%d %H:%M} ← "
                         f"{ts[j+1]:%Y-%m-%d %H:%M} ({gaps[j]:g}د بدل {step:g}د) "
                         f"· مجموع الفجوات {len(bad)} — لا يُبنى على نافذة مثقوبة")

    rep = dict(n=len(out), step_min=step,
               start=ts[0].strftime("%Y-%m-%d %H:%M"),
               end=ts[-1].strftime("%Y-%m-%d %H:%M"),
               lo=min(k["l"] for k in out), hi=max(k["h"] for k in out))
    return out, rep


def assert_levels(W, **lv):
    """كل سعر يُرسم يجب أن يقع داخل مدى النافذة — وإلا فهو خارج الشاشة.

    الوقف فوق القمة أو الهدف تحت القاع يعني أن الأرقام لا تخصّ هذه
    النافذة، وهو خطأ يُكتشف الآن لا بعد الرندر."""
    lo = min(c["l"] for c in W); hi = max(c["h"] for c in W)
    bad = {k: v for k, v in lv.items() if v is not None and not (lo <= v <= hi)}
    if bad:
        raise ValueError(f"أسعار خارج مدى النافذة [{lo:g} … {hi:g}]: {bad}")


if __name__ == "__main__":
    p = sys.argv[1]
    tf = sys.argv[sys.argv.index("--tf") + 1] if "--tf" in sys.argv else None
    W, rep = load(p, tf)
    print(f'✅ {os.path.basename(p)} — {rep["n"]} شمعة · فريم {rep["step_min"]:g} دقيقة\n'
          f'   من {rep["start"]} إلى {rep["end"]} (UTC كما في الملف)\n'
          f'   المدى {rep["lo"]:g} … {rep["hi"]:g}')
