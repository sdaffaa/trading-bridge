# -*- coding: utf-8 -*-
"""مُشغّل تشغيلة ٣١: يسند نافذة حقيقية وصيغة لكل وحدة ثم يبني الخمس.

النوافذ اختيرت بعد فحص كم حالة تثبت على كل واحدة (`run31_charts` يطبعها)،
ولا تتكرر أداة/فريم/تاريخ بين وحدتين. الوحدتان الفنيتان ريلان — أولوية
الريل للفني لأن قصته تتحرك على الجارت (§12).
"""
import run31_build as B

# slug: (فهرس النافذة، الصيغة، الفئة)
PLAN = {
    "value":   (0,  "reel",     "فنية"),      # الأسترالي/الدولار ساعة — ٦/٦ حالات
    "expan":   (10, "reel",     "فنية"),      # الذهب ٣٠د 2026-07-02 — ٥/٦
    "watch":   (12, "carousel", "نفسية"),     # الذهب ١٥د 2026-07-02 — ٥/٦
    "plan":    (2,  "carousel", "أساسية"),    # الجنيه/الدولار ساعة — ٥/٦
    "partial": (13, "carousel", "مالية"),     # الذهب ١٥د 2026-05-29 — ٤/٦
}
for k, (w, m, _) in PLAN.items():
    B.WINDOWS[k] = w
    B.MEDIA[k] = m

if __name__ == "__main__":
    B._unregister()
    import run32_desk as D                  # محرّك الريل بعد التعميم (§11 بند ٤)
    reels = []
    for k, (_, m, _c) in PLAN.items():
        try:
            B.build_unit(k)
        except Exception as e:
            print(f"✗ {k}: {type(e).__name__}: {e}"); continue
        if m != "reel":
            continue
        # بناء الريل صار جزءاً من التشغيلة لا خطوة يدوية. سقوط الريل لا
        # يُسقط وحدته: دليلها بُني، ويُذكر النقص في الملخص.
        try:
            D.build(k); reels.append(k)
        except Exception as e:
            print(f"✗ ريل {k}: {type(e).__name__}: {e}")
    if reels:
        print("\nللرندر والمؤثرات:  python3 run32_post.py " + " ".join(reels))
