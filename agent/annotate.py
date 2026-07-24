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


def render(png: bytes, decision: dict, ys: dict) -> bytes:
    """Return a PNG with the trade markup drawn on it (or the original on any issue)."""
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
        jlog("annotate_ok", action=action)
        return buf.getvalue()
    except Exception as e:                 # markup must never block the send
        jlog("annotate_error", error=str(e)[:200])
        return png
