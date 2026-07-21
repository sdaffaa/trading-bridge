#!/usr/bin/env python3
# Generate transparent 1080x1920 caption overlays (bottom scrim + Arabic caption)
# PIL has libraqm here -> use RAW text + direction="rtl" (no reshaping).
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FONT_BOLD = "fonts/Tajawal-Bold.ttf"
FONT_XB = "fonts/Tajawal-ExtraBold.ttf"
FONT_MED = "fonts/Tajawal-Medium.ttf"
TEAL = (79, 208, 224, 255)

# key takeaway caption per page (short, punchy reels style)
CAPTIONS = {
    1:  "متى يجب أن تبتعد عن الجارت؟",
    2:  "بعد 3 خسائر متتالية… ابتعد",
    3:  "لا تتداول انتقامًا من الخسارة",
    4:  "ما في Setup واضح؟ لا تدخل",
    5:  "الملل يصنع صفقات عشوائية",
    6:  "متعب أو مشتت؟ ابتعد",
    7:  "قبل الأخبار القوية… راقب فقط",
    8:  "كسرت خطتك؟ اخرج فورًا",
    9:  "بعد ربح كبير… خذ استراحة",
    10: "الجودة قبل عدد الصفقات",
}

def rounded_rect(d, box, r, fill):
    d.rounded_rectangle(box, radius=r, fill=fill)

def draw_caption(page, text):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # opaque lower-third bar: soft feather in, then solid to fully hide
    # the slide's own bottom takeaway line and page number.
    feather_top = 1508
    solid_at = 1600
    for y in range(feather_top, H):
        if y >= solid_at:
            a = 252
        else:
            t = (y - feather_top) / (solid_at - feather_top)
            a = int(252 * (t ** 1.1))
        d.line([(0, y), (W, y)], fill=(3, 6, 11, a))
    # subtle teal hairline at the top edge of the bar
    d.line([(90, feather_top+2), (W-90, feather_top+2)], fill=(79, 208, 224, 40), width=2)

    # fit font
    fs = 58
    font = ImageFont.truetype(FONT_XB, fs)
    max_w = W - 230
    while font.getlength(text) > max_w and fs > 34:
        fs -= 2
        font = ImageFont.truetype(FONT_XB, fs)

    cy = 1710
    tw = font.getlength(text)
    # caption "pill" — opaque, fully covers underlying text, subtle teal border
    pad_x, pad_y = 46, 26
    ph = fs + pad_y * 2
    pw = tw + pad_x * 2
    x0, y0 = (W - pw) / 2, cy - ph / 2
    x1, y1 = (W + pw) / 2, cy + ph / 2
    # glow
    rounded_rect(d, [x0-3, y0-3, x1+3, y1+3], (ph+6)//2, (79, 208, 224, 60))
    # body
    rounded_rect(d, [x0, y0, x1, y1], ph//2, (8, 14, 22, 245))
    # thin teal ring
    d.rounded_rectangle([x0, y0, x1, y1], radius=ph//2, outline=(79, 208, 224, 180), width=2)

    # text
    d.text((W//2, cy+2), text, font=font, fill=(0, 0, 0, 180),
           anchor="mm", direction="rtl", language="ar")
    d.text((W//2, cy), text, font=font, fill=(240, 250, 252, 255),
           anchor="mm", direction="rtl", language="ar")

    # small teal accent diamond to the right edge inside pill
    ds = 7
    dx = x1 - 30
    d.polygon([(dx, cy-ds), (dx+ds, cy), (dx, cy+ds), (dx-ds, cy)], fill=TEAL)
    dx2 = x0 + 30
    d.polygon([(dx2, cy-ds), (dx2+ds, cy), (dx2, cy+ds), (dx2-ds, cy)], fill=TEAL)

    # progress counter "page / 10" under the pill
    cf = ImageFont.truetype(FONT_MED, 30)
    ctxt = f"{page} / 10"
    d.text((W//2, 1832), ctxt, font=cf, fill=(150, 175, 190, 235),
           anchor="mm", direction="ltr")
    # progress ticks
    seg_w = 34; gap = 8; total = 10
    tw2 = total*seg_w + (total-1)*gap
    sx = (W - tw2)/2; ty = 1866
    for i in range(total):
        col = TEAL if (i+1) <= page else (60, 78, 90, 255)
        d.rounded_rectangle([sx+i*(seg_w+gap), ty, sx+i*(seg_w+gap)+seg_w, ty+5], radius=2, fill=col)

    img.save(f"captions/cap{page:02d}.png")
    return fs

os.makedirs("captions", exist_ok=True)
for p, t in CAPTIONS.items():
    fs = draw_caption(p, t)
    print(f"cap{p:02d}: fs={fs}  '{t}'")
print("done")
