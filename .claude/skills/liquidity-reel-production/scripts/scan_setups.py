# -*- coding: utf-8 -*-
"""البوّابة النهائية: يُخضع كل نافذة مرشّحة للطبقات الخمس كاملةً قبل قبولها.

`sandbox_scan.py` يجلب ويقصّ فقط، وشرطه أدنى عمداً. هنا يُعاد الحكم كاملاً
عبر `topdown.build` نفسه الذي يبني الريل — فلا يمكن أن يُروى في الفيديو
شرطٌ لم يُختبر هنا، لأن المصدر واحد.

النافذة المرفوضة تُحذف ويُطبع سبب رفضها. المقبولة تُحفظ في `raw_windows/`
ولا تُعاد: `used_setups.json` سجلّ ما نُشر، والتكرار على الجمهور أسوأ من
الصمت.

    python3 scan_setups.py accept < نوافذ.json     # فحص وحفظ وترتيب
    python3 scan_setups.py queue                   # المقبول الذي لم يُنشر بعد
    python3 scan_setups.py claim gc_td3_....json   # تسجيل ما نُشر
    python3 scan_setups.py list                    # ما في السجلّ

المسح يحتاج الشبكة، والشبكة تحتاج صندوقاً خارجياً قد لا يتوفّر في كل
تشغيلة. لذلك يفصل `queue` بين المرحلتين: المسح يملأ المخزون حين يستطيع،
والإنتاج يسحب منه حين لا يستطيع. فلا تتوقّف السلسلة لأن الجلب تعذّر.
"""
import datetime as dt, json, os, sys

import topdown

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw_windows")
REG = os.path.join(HERE, "used_setups.json")
SLUG = {"GC=F": "gc", "SI=F": "si", "CL=F": "cl", "BZ=F": "bz", "NG=F": "ng",
        "HG=F": "hg", "BTC-USD": "btc", "ETH-USD": "eth", "EURUSD=X": "eur",
        "GBPUSD=X": "gbp", "USDJPY=X": "jpy", "^GSPC": "spx"}


def reg():
    return json.load(open(REG, encoding="utf-8")) if os.path.exists(REG) else []


def save_reg(r):
    json.dump(r, open(REG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def name(w):
    s = SLUG.get(w["sym"], w["sym"].lower().replace("=", "").replace("^", ""))
    return f'{s}_sc_{w["anchor_utc"].replace(" ", "_").replace(":", "")}.json'


MIN_R = 0.0006          # ٦ نقاط أساس: أصغر مخاطرة تستحق أن تُروى


def gaps(w):
    """الشموع الناقصة في إطار التنفيذ — كل قفزة أكبر من خطوة الإطار.

    أمر فهد 2026-08-06: «لا تجعل فراغات بالجارت — يجب أن تكون الشموع
    متتالية». الجارت يرسم بالفهرس لا بالزمن، فنافذةٌ ينقصها بوكت تُرسم
    متلاصقة وتوهم أن السعر تحرّك بلا انقطاع. تُردّ من الباب لا تُجمَّل."""
    tf = w.get("exec_tf", "5m")
    step = dt.timedelta(minutes=int(tf[:-1]))
    r = w[tf]["rows"]
    f = "%Y-%m-%d %H:%M"
    return [(r[i][0], r[i + 1][0]) for i in range(len(r) - 1)
            if dt.datetime.strptime(r[i + 1][0], f)
            - dt.datetime.strptime(r[i][0], f) != step]


def accept(windows):
    used = {(u["sym"], u["anchor"]) for u in reg()}
    ok, bad = [], []
    for w in windows:
        f = name(w)
        if (w["sym"], w["anchor_utc"]) in used:
            bad.append((f, "منشور سابقاً")); continue
        g = gaps(w)
        if g:
            bad.append((f, f"{len(g)} فجوة زمنية في الشموع — أوّلها "
                           f"{g[0][0]} ← {g[0][1]}")); continue
        p = os.path.join(RAW, f)
        json.dump(w, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        try:
            D, L, P = topdown.build(f)
        except AssertionError as e:
            os.remove(p); bad.append((f, str(e))); continue
        except Exception as e:
            os.remove(p); bad.append((f, f"{type(e).__name__}: {e}")); continue
        # النمط قد يصحّ والصفقة لا تستحق النشر: وقفٌ ثلاث نقاط على الين
        # يساوي ٠٫٠٣٪ من السعر — داخل الفارق السعري نفسه. `topdown` يحكم
        # على الشكل، وهذا يحكم على الجدوى. فصلهما مقصود.
        rr = (P["ENT"] - P["STP"]) / P["ENT"]
        if rr < MIN_R:
            os.remove(p)
            bad.append((f, f"المخاطرة {rr*1e4:.1f} نقطة أساس — دون عتبة "
                           f"{MIN_R*1e4:.0f}؛ حركةٌ داخل الضجيج"))
            continue
        ok.append(dict(file=f, sym=w["sym"], anchor=w["anchor_utc"],
                       layers=[x["detail"] for x in L], titles=[x["title"] for x in L],
                       ent=P["ENT"], stp=P["STP"], tgt=P["TGT"],
                       bars=P["hit"] - P["fill"], eq=len(L[3]["eq"]),
                       wick=round(L[4]["wick"], 3), dp=P["dp"]))
    # الأقوى: قيعان أكثر عند المستوى، ثم ذيل رفض أعمق، ثم بلوغ أسرع للهدف
    ok.sort(key=lambda r: (-r["eq"], -r["wick"], r["bars"]))
    return ok, bad


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "accept"
    if cmd == "list":
        for u in reg():
            print(f'{u["sym"]:<9} {u["anchor"]}  {u["file"]}')
        raise SystemExit
    if cmd == "queue":
        used = {u["file"] for u in reg()}
        rows = []
        for f in sorted(os.listdir(RAW)):
            if not f.endswith(".json") or f in used:
                continue
            try:
                D, L, P = topdown.build(f)
            except Exception:
                continue                       # نوافذ قديمة لا تجتاز — تُتجاهل
            g = gaps(json.load(open(os.path.join(RAW, f), encoding="utf-8")))
            # النوافذ المقبولة قبل بوابة التتابع قد تحمل فجوات — تُعلَن ولا
            # تُبنى: جارتٌ ينقصه بوكت يكذب على العين وإن صحّ تحليله.
            rows.append((len(L[3]["eq"]), L[4]["wick"], -(P["hit"] - P["fill"]),
                         f, D, L, P, g))
        rows.sort(key=lambda r: r[:3], reverse=True)
        clean = [r for r in rows if not r[7]]
        for _, _, _, f, D, L, P, g in rows:
            DP = P["dp"]
            print(f'\n{f}   {D["sym"]} · {D["anchor_utc"]}'
                  + (f'\n   ⚠ {len(g)} فجوة زمنية ({g[0][0]} ← {g[0][1]}) — لا يُبنى'
                     if g else ''))
            for x in L:
                print(f'   · {x["title"]}: {x["detail"]}')
            print(f'   ← دخول {P["ENT"]:,.{DP}f} · وقف {P["STP"]:,.{DP}f} · هدف '
                  f'{P["TGT"]:,.{DP}f} · تحقّق بعد {P["hit"] - P["fill"]} شمعة')
        print(f'\nفي المخزون: {len(clean)} صالح'
              + (f' · {len(rows)-len(clean)} بفجوات زمنية' if len(rows) > len(clean) else ''))
        rows = clean
        if rows:
            print(f'LS_SET={rows[0][3]}')
        raise SystemExit(0 if rows else 3)
    if cmd == "claim":
        import reason_pool
        r = reg()
        for f in sys.argv[2:]:
            w = json.load(open(os.path.join(RAW, f), encoding="utf-8"))
            r.append(dict(file=f, sym=w["sym"], anchor=w["anchor_utc"]))
            # وأسباب الريل تدخل سجلّها هنا لا عند البناء: هذه اللحظة وحدها
            # تعني «نُشر»، فلا تزيح تجربةُ بناءٍ دورانَ الأسباب.
            k = reason_pool.register_staged(f.replace(".json", ""))
            if k:
                print("   أسباب: " + " · ".join(k))
        save_reg(r)
        print(f"سُجّل {len(sys.argv) - 2} · المجموع {len(r)}")
        raise SystemExit

    txt = sys.stdin.read()
    if "===WINDOWS_GZ_B64===" in txt:
        txt = txt.split("===WINDOWS_GZ_B64===", 1)[1]
    txt = txt.strip()
    if not txt.startswith("["):                 # مضغوطة من الصندوق
        import base64, gzip
        txt = gzip.decompress(base64.b64decode(txt)).decode()
    ok, bad = accept(json.loads(txt))
    for f, why in bad:
        print(f"✗ {f}\n   {why}")
    if not ok:
        print("\nلا شيء اجتاز الطبقات الخمس.")
        raise SystemExit(3)
    print(f"\n✓ اجتاز {len(ok)}:")
    for r in ok:
        DP = r["dp"]
        print(f'\n  {r["file"]}   {r["sym"]} · {r["anchor"]}')
        for t, d in zip(r["titles"], r["layers"]):
            print(f'    · {t}: {d}')
        print(f'    ← دخول {r["ent"]:,.{DP}f} · وقف {r["stp"]:,.{DP}f} · هدف '
              f'{r["tgt"]:,.{DP}f} · تحقّق بعد {r["bars"]} شمعة')
    print(f'\nLS_SET={ok[0]["file"]}')
