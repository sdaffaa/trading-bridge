# -*- coding: utf-8 -*-
"""
artext.py — correct Arabic text rendering for dumb rasterizers (PIL, node-canvas).
Requires: pip install arabic-reshaper python-bidi pillow

Golden rule: use these helpers ONLY when the engine does NOT shape Arabic itself.
Browsers, Remotion, libass (.ass/.srt), and PIL-with-libraqm must receive RAW text.
"""
import os
import urllib.request

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import ImageFont

# Reshaper that keeps harakat (tashkeel). For fonts that render marks poorly,
# build one with delete_harakat=True.
_reshaper = arabic_reshaper.ArabicReshaper(
    configuration={"delete_harakat": False, "support_ligatures": True}
)


def ar(text: str) -> str:
    """Shape + bidi-reorder a (possibly mixed AR/EN/number) string for draw.text."""
    return get_display(_reshaper.reshape(text))


def draw_ar(draw, xy, text, font, fill, anchor="mm", shadow=None, shadow_fill=(0, 0, 0, 140)):
    """Draw Arabic text correctly in one call. Optional pixel-offset shadow, e.g. shadow=(2,2)."""
    t = ar(text)
    if shadow:
        draw.text((xy[0] + shadow[0], xy[1] + shadow[1]), t, font=font, fill=shadow_fill, anchor=anchor)
    draw.text(xy, t, font=font, fill=fill, anchor=anchor)


def wrap_ar(text: str, font, max_width: int):
    """RTL-safe wrapping: wrap RAW text by words first, then shape each line.
    Returns display-ready lines (pass each straight to draw.text)."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        cand = (cur + " " + w).strip()
        if font.getlength(ar(cand)) <= max_width or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return [ar(l) for l in lines]


def missing_glyphs(font_path: str, text: str):
    """Return the set of characters the font cannot render (tofu risk: ✓ ✅ 📄 …).
    Draw those manually or composite an emoji font for them."""
    from fontTools.ttLib import TTFont  # pip install fonttools
    cmap = set()
    for table in TTFont(font_path)["cmap"].tables:
        cmap.update(table.cmap.keys())
    return {c for c in set(text) if not c.isspace() and ord(c) not in cmap}


def load_font(path: str, size: int, weight_axis=None):
    """Load a TTF; for variable fonts pass weight_axis, e.g. 700 for Cairo."""
    f = ImageFont.truetype(path, size)
    if weight_axis is not None:
        f.set_variation_by_axes([weight_axis])
    return f


TAJAWAL_WEIGHTS = ["Regular", "Medium", "Bold", "ExtraBold", "Black"]


def download_tajawal(dest_dir: str = "fonts"):
    """Fetch the Tajawal family (Arabic+Latin, static TTFs) from google/fonts."""
    os.makedirs(dest_dir, exist_ok=True)
    base = "https://raw.githubusercontent.com/google/fonts/main/ofl/tajawal/Tajawal-{}.ttf"
    out = {}
    for w in TAJAWAL_WEIGHTS:
        p = os.path.join(dest_dir, f"Tajawal-{w}.ttf")
        if not os.path.exists(p):
            urllib.request.urlretrieve(base.format(w), p)
        out[w] = p
    return out


if __name__ == "__main__":
    # Self-test: shows shaped output ordering for a mixed string.
    sample = "BOS · كسر الهيكل يأكد الصعود 3327.8"
    print("raw    :", sample)
    print("display:", ar(sample))
