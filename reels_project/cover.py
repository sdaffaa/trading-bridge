#!/usr/bin/env python3
# StopHunt reel cover (1080x1920). PIL has libraqm -> raw text + direction=rtl.
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
TEAL = (79, 208, 224, 255)
RED = (255, 91, 106, 255)
img = Image.new("RGB", (W, H), (4, 7, 13))
d = ImageDraw.Draw(img, "RGBA")

# vertical gradient
for y in range(H):
    t = y / H
    r = int(6 + 4 * (1 - t)); g = int(12 + 8 * (1 - t)); b = int(20 + 12 * (1 - t))
    d.line([(0, y), (W, y)], fill=(r, g, b))
# radial-ish glow center
for i in range(260, 0, -6):
    a = int(30 * (i / 260) ** 2)
    d.ellipse([W//2 - i*2, 760 - i, W//2 + i*2, 760 + i], fill=(79, 208, 224, max(0, 8 - i//40)))

FB = "remotion_reel/public/fonts/Tajawal-Bold.ttf"
FX = "remotion_reel/public/fonts/Tajawal-ExtraBold.ttf"
FBL = "fonts/Tajawal-Black.ttf"
FM = "remotion_reel/public/fonts/Tajawal-Medium.ttf"

def T(x, y, s, f, sz, fill, anchor="mm", sh=True):
    fo = ImageFont.truetype(f, sz)
    if sh:
        d.text((x+3, y+4), s, font=fo, fill=(0, 0, 0, 200), anchor=anchor, direction="rtl", language="ar")
    d.text((x, y), s, font=fo, fill=fill, anchor=anchor, direction="rtl", language="ar")

# REC badge (top)
d.rounded_rectangle([W-330, 90, W-70, 168], radius=14, fill=(20, 6, 8, 220), outline=RED, width=2)
d.ellipse([W-140, 116, W-116, 140], fill=RED)
T(W-175, 129, "تسجيل", FB, 34, (255, 180, 186, 255), anchor="rm", sh=False)

# candlestick silhouette + red dashed stop line + green rally hint (lower third)
import math
base = 1300
xs = 90
cw = 26; gap = 20
seq = [0,-1,-2,-1,-3,-4,-3,-5,-6,-7,-6, -8, 6, 12, 18, 24, 30, 34]
sweep = 11
for i, v in enumerate(seq):
    x = xs + i * (cw + gap)
    cy = base - v * 12
    up = i > sweep
    col = RED if i == sweep else ((57, 217, 138, 220) if up else (150, 165, 175, 150))
    d.line([(x+cw//2, cy-26), (x+cw//2, cy+26)], fill=col, width=3)
    d.rounded_rectangle([x, cy-18, x+cw, cy+18], radius=3, fill=col)
# stop line
sy = base + 96
for x in range(70, W-70, 30):
    d.line([(x, sy), (x+16, sy)], fill=RED, width=3)
d.polygon([(xs+sweep*(cw+gap)+cw//2-12, sy+8), (xs+sweep*(cw+gap)+cw//2+12, sy+8), (xs+sweep*(cw+gap)+cw//2, sy+30)], fill=RED)
T(W-120, sy+58, "ستوبك", FB, 34, RED, anchor="rm")

# headline
T(W//2, 560, "اللحظة اللي انضرب", FX, 92, (245, 251, 253, 255))
T(W//2, 672, "فيها ستوبك", FBL, 104, (245, 251, 253, 255))
# accent badge "مصوّرة"
bw = 360
d.rounded_rectangle([(W-bw)//2, 812, (W+bw)//2, 908], radius=48, fill=(8, 20, 28, 235), outline=TEAL, width=3)
# play triangle
d.polygon([(W//2+118, 860-20), (W//2+118, 860+20), (W//2+150, 860)], fill=TEAL)
T(W//2-24, 860, "مصوّرة", FX, 56, TEAL)

# bottom brand
T(W//2, H-140, "LIQUIDITY  STATE", FM, 40, (200, 225, 235, 235), sh=False)

img.save("output/cover_stophunt.png")
print("saved output/cover_stophunt.png")
