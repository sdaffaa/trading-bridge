"""Draw the trade markup ONTO the chart screenshot before it is sent.

The vision coordinator produces the trade (entry / stop / target) and a locator
call gives the vertical position of each level on the image; this module renders
them as a TradingView-style long/short position box — a green profit zone, a red
stop zone, dashed level lines, and labelled prices — so the picture the user
receives already carries the markup, not just the caption.

Labels use Latin text + numbers (Entry / SL / TP) on purpose: they render
crisply in any rasteriser, whereas Arabic on an image needs shaping. The Arabic
explanation stays in the Telegram caption.
"""
import io

from .logging_setup import jlog

_GREEN = (34, 197, 94)
_RED = (239, 68, 68)
_INK = (17, 17, 17)
_PAPER = (250, 250, 250)


def _font(size: int):
    from PIL import ImageFont
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:                      # Pillow < 10.1 has no size arg
        return ImageFont.load_default()


def _dash(draw, y: int, w: int, color, dash=18, gap=12, width=2):
    x = 0
    while x < w:
        draw.line([(x, y), (min(x + dash, w), y)], fill=color, width=width)
        x += dash + gap


def _label(draw, x: int, y: int, text: str, fg, bg, font):
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    tw, th = r - l, b - t
    pad = max(4, th // 3)
    draw.rectangle([x, y - th // 2 - pad, x + tw + 2 * pad, y + th // 2 + pad],
                   fill=bg)
    draw.text((x + pad, y - th // 2 - t), text, fill=fg, font=font)


def _price_to_y(anchors):
    """Least-squares fit of price -> y-fraction from the (price, y) trade anchors.
    Returns a function price->fraction, or None if the prices are degenerate."""
    pts = [(p, y) for p, y in anchors if p is not None and y is not None]
    if len(pts) < 2:
        return None
    n = len(pts)
    sp = sum(p for p, _ in pts)
    sy = sum(y for _, y in pts)
    spp = sum(p * p for p, _ in pts)
    spy = sum(p * y for p, y in pts)
    denom = n * spp - sp * sp
    if denom == 0:
        return None
    a = (n * spy - sp * sy) / denom
    b = (sy - a * sp) / n
    return lambda price: a * price + b


def _kind_color(kind):
    return {"bull": _GREEN, "bear": _RED}.get(kind, (96, 165, 250))   # neutral = blue


def render(png: bytes, decision: dict, ys: dict, key_levels=None) -> bytes:
    """Return a PNG with the trade markup drawn on it (or the original on any issue).

    Draws the position box (entry/SL/TP) plus, when the schools supplied them,
    their key levels/zones (FVG, order blocks, POC, liquidity) mapped onto the
    chart by fitting price->pixel from the trade anchors.
    """
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return png
    try:
        action = decision.get("action")
        entry, sl, tp = (decision.get("entry"), decision.get("stop_loss"),
                         decision.get("take_profit"))
        ey, sy, ty = ys.get("entry_y"), ys.get("stop_y"), ys.get("target_y")
        if action not in ("long", "short") or None in (entry, sl, tp, ey, sy, ty):
            return png

        base = Image.open(io.BytesIO(png)).convert("RGBA")
        w, h = base.size
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)

        # --- the schools' key levels/zones (drawn first, under the trade box) ---
        p2y = _price_to_y([(entry, ey), (sl, sy), (tp, ty)])
        drawn_levels = 0
        if p2y and key_levels:
            sf = _font(max(11, int(h * 0.018)))
            for lvl in key_levels[:6]:
                price = lvl.get("price")
                if price is None:
                    continue
                col = _kind_color(lvl.get("kind"))
                yv = int(min(1.0, max(0.0, p2y(price))) * h)
                p2 = lvl.get("price2")
                if p2 is not None:                       # a zone
                    yv2 = int(min(1.0, max(0.0, p2y(p2))) * h)
                    d.rectangle([0, min(yv, yv2), w, max(yv, yv2)], fill=col + (28,))
                _dash(d, yv, w, col + (170,), dash=10, gap=10, width=1)
                # right-align the label so a long one never runs off the edge
                label = lvl.get("label", "")
                bb = d.textbbox((0, 0), label, font=sf)
                lx = max(8, w - (bb[2] - bb[0]) - int(w * 0.03))
                _label(d, lx, yv, label, (255, 255, 255, 255), col + (210,), sf)
                drawn_levels += 1

        # --- the position box (entry / SL / TP), drawn on top ---
        pe, ps, pt = int(ey * h), int(sy * h), int(ty * h)
        x0 = int(w * 0.58)                 # box sits on the right, like the position tool

        d.rectangle([x0, min(pe, pt), w, max(pe, pt)], fill=_GREEN + (55,))   # profit
        d.rectangle([x0, min(pe, ps), w, max(pe, ps)], fill=_RED + (55,))     # stop

        _dash(d, pe, w, _PAPER + (235,))
        _dash(d, pt, w, _GREEN + (235,))
        _dash(d, ps, w, _RED + (235,))

        f = _font(max(13, int(h * 0.022)))
        _label(d, 8, pe, f"Entry {entry}", _INK + (255,), _PAPER + (235,), f)
        _label(d, 8, pt, f"TP {tp}", (255, 255, 255, 255), _GREEN + (235,), f)
        _label(d, 8, ps, f"SL {sl}", (255, 255, 255, 255), _RED + (235,), f)

        rr = decision.get("risk_reward")
        tag = f"{action.upper()}  {decision.get('grade', '-')}"
        if rr:
            tag += f"  R:R {rr}"
        _label(d, 8, max(int(h * 0.03), 18), tag, (255, 255, 255, 255),
               _INK + (220,), _font(max(15, int(h * 0.026))))

        out = Image.alpha_composite(base, overlay).convert("RGB")
        buf = io.BytesIO()
        out.save(buf, format="PNG")
        jlog("annotate_ok", action=action, key_levels=drawn_levels)
        return buf.getvalue()
    except Exception as e:                 # markup must never block the send
        jlog("annotate_error", error=str(e)[:200])
        return png
