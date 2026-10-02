# -*- coding: utf-8 -*-
"""يطبع حمولة `used.json` للصندوق: كل نافذة نملكها، لا المنشورة فقط.

الصندوق يقبل أربع نوافذ ثم يتوقّف. فإن لم يعرف ما نملكه أنفق الحصّة على
نوافذ عندنا أصلاً وعاد فارغاً — وقع هذا سبع دورات متتالية. المفتاح
(الرمز، المرساة) نفسه في الطرفين، فالإسقاط هنا توفيرُ حصّةِ بحثٍ لا
تخفيفُ عتبة: الطبقات الخمس تُطبَّق على ما يعود كما هي.

المصدران: `used_setups.json` (المنشور) و`raw_windows/` (كل ما على القرص،
ومنه ما تعذّر بناؤه لفجوةٍ أو ضيقِ لوحة — وهذا لا يُعاد جلبه).

    python3 sandbox_used.py > u.b64      # ثم md5sum u.b64 حارساً للنقل
"""
import base64, glob, gzip, hashlib, json, os, sys, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))

keys = set()
with open(os.path.join(HERE, "used_setups.json"), encoding="utf-8") as f:
    for u in json.load(f):
        keys.add((u["sym"], u["anchor"]))
for p in glob.glob(os.path.join(HERE, "raw_windows", "*.json")):
    with open(p, encoding="utf-8") as f:
        w = json.load(f)
    # ملفٌّ قديمٌ واحدٌ سلسلةُ شموعٍ لا نافذة — لا مرساةَ فيه فيُتخطّى.
    if isinstance(w, dict) and "sym" in w and "anchor_utc" in w:
        keys.add((w["sym"], w["anchor_utc"]))

rows = [{"sym": s, "anchor": a} for s, a in sorted(keys)]
raw = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode()
b64 = textwrap.fill(base64.b64encode(gzip.compress(raw, 9)).decode(), 76) + "\n"
sys.stdout.write(b64)
print(f"{len(rows)} مفتاحاً · md5 {hashlib.md5(b64.encode()).hexdigest()}",
      file=sys.stderr)
