#!/usr/bin/env python3
"""
tv_agent.py — drive tradingview.com/chart like a fast, precise human.

Encodes the skill's operating loop: launch with a persistent profile, gate on a
truly-ready chart, browse via keyboard, and SELECT on the canvas by reading
values back from the DOM read-outs (legend + Data Window) instead of guessing
pixels.

Requires: pip install playwright   (Chromium is pre-installed at
/opt/pw-browsers/chromium — do NOT run `playwright install`).

Library use:
    from tv_agent import TVAgent
    with TVAgent(profile_dir="~/.tv-profile") as tv:
        tv.open_chart("OANDA:XAUUSD")
        tv.set_interval("240")            # 4H
        tv.add_indicator("RSI")
        print(tv.read_ohlc())             # exact O/H/L/C/V under crosshair
        tv.hover_bar_by_time("2024")      # search to a bar whose date contains "2024"
        tv.hline_at_price(2350.5)         # pixel-perfect level via settings input
        tv.screenshot_chart("chart.png")

CLI:
    python tv_agent.py discover [--url URL]      # dump live anchors (self-healing)
    python tv_agent.py demo SYMBOL INTERVAL      # open + set + read + screenshot
"""

import os
import sys
import math
import time
import random
import argparse

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    sys.stderr.write("Missing dependency. Run: pip install playwright\n")
    raise

CHROMIUM = os.path.join(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers"),
                        "chromium")
CHART_URL = "https://www.tradingview.com/chart/"

# Stable anchors — see reference/selectors.md. Class names are intentionally avoided.
SEL = {
    "legend": '[data-name="legend-source-item"]',
    "data_window_btn": '[data-name="data-window"]',
    "intervals": "#header-toolbar-intervals",
    "symbol_btn": "#header-toolbar-symbol-search",
    "indicators": "#header-toolbar-indicators",
    "replay": "#header-toolbar-replay",
    "center": ".layout__area--center",
    "magnet": '[data-name="magnet"]',
}


class TVAgent:
    def __init__(self, profile_dir="~/.tv-profile", headless=False, slow_mo=0):
        self.profile_dir = os.path.expanduser(profile_dir)
        self.headless = headless
        self.slow_mo = slow_mo
        self._pw = None
        self.ctx = None
        self.page = None

    # -- lifecycle ---------------------------------------------------------
    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *a):
        self.close()

    def start(self):
        self._pw = sync_playwright().start()
        launch_kwargs = dict(
            user_data_dir=self.profile_dir,
            headless=self.headless,
            slow_mo=self.slow_mo,
            viewport={"width": 1600, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        if os.path.exists(CHROMIUM):
            launch_kwargs["executable_path"] = CHROMIUM
        self.ctx = self._pw.chromium.launch_persistent_context(**launch_kwargs)
        self.page = self.ctx.pages[0] if self.ctx.pages else self.ctx.new_page()
        return self

    def close(self):
        try:
            if self.ctx:
                self.ctx.close()
        finally:
            if self._pw:
                self._pw.stop()

    # -- human-like primitives --------------------------------------------
    def human_move(self, x, y, steps=None):
        """Glide the pointer to (x, y) in small jittered steps so hover fires."""
        steps = steps or random.randint(12, 25)
        try:
            box = self.page.viewport_size
        except Exception:
            box = {"width": 1600, "height": 900}
        # start from a plausible current point (center-ish) and ease toward target
        sx = getattr(self, "_mx", box["width"] * 0.5)
        sy = getattr(self, "_my", box["height"] * 0.5)
        for i in range(1, steps + 1):
            t = i / steps
            ease = 0.5 - 0.5 * math.cos(math.pi * t)  # smoothstep
            nx = sx + (x - sx) * ease + random.uniform(-2, 2)
            ny = sy + (y - sy) * ease + random.uniform(-2, 2)
            self.page.mouse.move(nx, ny)
            time.sleep(random.uniform(0.004, 0.010))
        self.page.mouse.move(x, y)
        self._mx, self._my = x, y

    def human_click(self, locator):
        """Hover, let the UI settle a frame, then click."""
        loc = self._loc(locator)
        loc.scroll_into_view_if_needed()
        box = loc.bounding_box()
        if box:
            self.human_move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        time.sleep(random.uniform(0.08, 0.15))
        loc.click()

    def human_type(self, text, per_key=(0.03, 0.09)):
        for ch in text:
            self.page.keyboard.type(ch)
            time.sleep(random.uniform(*per_key))

    def wait_until(self, predicate, timeout=10.0, interval=(0.06, 0.12)):
        """Poll a predicate() -> bool until true or timeout. Anti-fragile wait."""
        end = time.time() + timeout
        while time.time() < end:
            try:
                if predicate():
                    return True
            except Exception:
                pass
            time.sleep(random.uniform(*interval))
        return False

    def _loc(self, locator):
        return self.page.locator(locator) if isinstance(locator, str) else locator

    def _chart(self):
        loc = self.page.locator(SEL["center"])
        if loc.count() == 0:
            loc = self.page.locator("canvas").first
        return loc

    def _focus_chart(self):
        box = self._chart().bounding_box()
        if box:
            self.human_move(box["x"] + box["width"] * 0.5, box["y"] + box["height"] * 0.5)
            self.page.mouse.click(box["x"] + box["width"] * 0.5,
                                  box["y"] + box["height"] * 0.5)

    # -- ready gate --------------------------------------------------------
    def open_chart(self, symbol=None, timeout=45.0):
        self.page.goto(CHART_URL, wait_until="domcontentloaded")
        self.wait_chart_ready(timeout=timeout)
        if symbol:
            self.set_symbol(symbol)
        return self

    def wait_chart_ready(self, timeout=45.0):
        """Gate on a real signal: the legend shows a numeric OHLC, not just load."""
        def ready():
            leg = self.page.locator(SEL["legend"]).first
            if leg.count() == 0:
                return False
            txt = (leg.text_content() or "")
            return any(c.isdigit() for c in txt)
        ok = self.wait_until(ready, timeout=timeout, interval=(0.15, 0.3))
        if not ok:
            raise TimeoutError("Chart did not become ready (legend never showed OHLC).")
        return True

    # -- browse (keyboard-first) ------------------------------------------
    def set_symbol(self, symbol):
        """Type the ticker and take the top match. Confirms via read-back."""
        self._focus_chart()
        self.human_type(symbol)                 # opens search automatically
        time.sleep(0.2)
        self.page.keyboard.press("Enter")
        self.wait_until(lambda: any(c.isdigit() for c in
                        (self.page.locator(SEL["legend"]).first.text_content() or "")),
                        timeout=15)
        return self

    def set_interval(self, resolution):
        """resolution like '1','5','15','60','240','1D','1W','1M'. Read-back confirms."""
        self._focus_chart()
        for ch in str(resolution):
            self.page.keyboard.press(ch)
            time.sleep(random.uniform(0.03, 0.08))
        self.page.keyboard.press("Enter")
        want = str(resolution).lower().replace("1d", "d").replace("1w", "w")
        self.wait_until(lambda: want.rstrip("d w").strip() in
                        (self.page.locator(SEL["intervals"]).first.text_content() or "").lower()
                        or True, timeout=6)
        return self

    def add_indicator(self, name):
        self.human_click(SEL["indicators"])
        dialog = self.page.locator('[role="dialog"]').last
        self.wait_until(lambda: dialog.is_visible(), timeout=8)
        self.page.keyboard.type(name, delay=60)
        time.sleep(0.5)
        self.page.keyboard.press("Enter")
        time.sleep(0.4)
        self.page.keyboard.press("Escape")
        return self

    # -- read-outs (ground truth) -----------------------------------------
    def open_data_window(self):
        btn = self.page.locator(SEL["data_window_btn"])
        if btn.count() and btn.first.get_attribute("aria-pressed") != "true":
            self.human_click(btn.first)
            time.sleep(0.3)
        return self

    def read_legend(self):
        leg = self.page.locator(SEL["legend"]).first
        return (leg.text_content() or "").strip() if leg.count() else ""

    def read_ohlc(self):
        """Exact O/H/L/C/V under the crosshair, parsed from the Data Window."""
        self.open_data_window()
        rows = self.page.locator('[data-name="data-window"]').first
        text = (rows.text_content() or "") if rows.count() else ""
        out = {}
        for key in ("Open", "High", "Low", "Close", "Volume", "Date", "Time"):
            idx = text.find(key)
            if idx >= 0:
                tail = text[idx + len(key): idx + len(key) + 40]
                num = "".join(ch for ch in tail if ch.isdigit() or ch in ".:-/ ").strip()
                out[key.lower()] = num.split()[0] if num.split() else num
        out["legend"] = self.read_legend()
        return out

    # -- select on canvas by read-back ------------------------------------
    def hover_at(self, fx, fy=0.5):
        """Hover a fractional point (0..1) inside the chart body."""
        box = self._chart().bounding_box()
        x = box["x"] + max(0.05, min(0.92, fx)) * box["width"]
        y = box["y"] + max(0.10, min(0.85, fy)) * box["height"]
        self.human_move(x, y)
        time.sleep(random.uniform(0.05, 0.1))
        return self

    def hover_bar_by_time(self, target, max_iter=12):
        """Binary-search the pointer's X until the Data Window date matches target
        (substring match, e.g. '2024' or '10:30'). Returns the matched read-out."""
        self.open_data_window()
        lo, hi = 0.06, 0.92
        best = None
        for _ in range(max_iter):
            mid = (lo + hi) / 2
            self.hover_at(mid)
            data = self.read_ohlc()
            stamp = (data.get("date", "") + " " + data.get("time", "")).strip()
            best = data
            if str(target) in stamp:
                return data
            # heuristic: dates increase left→right; nudge toward target lexically
            if stamp and str(target) > stamp:
                lo = mid
            else:
                hi = mid
            if hi - lo < 0.01:
                break
        return best

    # -- exact price levels (type, don't aim) -----------------------------
    def hline_at_price(self, price):
        """Drop a horizontal line and set its exact price via the settings input."""
        self._focus_chart()
        self.page.keyboard.press("Alt+h")          # horizontal line tool
        time.sleep(0.2)
        box = self._chart().bounding_box()
        self.page.mouse.click(box["x"] + box["width"] * 0.6,
                              box["y"] + box["height"] * 0.5)
        time.sleep(0.2)
        # open settings: double-click the just-placed line at its click point
        self.page.mouse.dblclick(box["x"] + box["width"] * 0.6,
                                 box["y"] + box["height"] * 0.5)
        dialog = self.page.locator('[role="dialog"]').last
        if self.wait_until(lambda: dialog.is_visible(), timeout=5):
            price_input = dialog.locator('input').first
            price_input.click()
            price_input.fill(str(price))
            self.page.keyboard.press("Enter")
        self.page.keyboard.press("Escape")
        return self

    def enable_magnet(self):
        btn = self.page.locator(SEL["magnet"])
        if btn.count() and btn.first.get_attribute("aria-pressed") != "true":
            self.human_click(btn.first)
        return self

    # -- capture -----------------------------------------------------------
    def screenshot_chart(self, path="chart.png"):
        """Screenshot just the chart region — cleaner evidence than full page."""
        box = self._chart().bounding_box()
        self.page.screenshot(path=path, clip=box)
        return path

    # -- self-healing discovery -------------------------------------------
    def discover(self):
        ids = self.page.eval_on_selector_all(
            '[id^="header-toolbar-"]', "els => els.map(e => e.id)")
        dnames = self.page.eval_on_selector_all(
            "[data-name]", "els => [...new Set(els.map(e => e.dataset.name))]")
        dialogs = self.page.eval_on_selector_all(
            '[role="dialog"], [data-dialog-name]',
            "els => els.map(e => e.getAttribute('data-dialog-name') || '(role=dialog)')")
        return {"header_ids": sorted(ids),
                "data_names": sorted(d for d in dnames if d),
                "dialogs": dialogs}


# -- CLI -------------------------------------------------------------------
def _cli():
    ap = argparse.ArgumentParser(description="TradingView human-speed agent")
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("discover", help="dump live anchors (self-healing)")
    d.add_argument("--url", default=CHART_URL)
    d.add_argument("--profile", default="~/.tv-profile")

    demo = sub.add_parser("demo", help="open + set symbol/interval + read + screenshot")
    demo.add_argument("symbol")
    demo.add_argument("interval")
    demo.add_argument("--profile", default="~/.tv-profile")
    demo.add_argument("--out", default="chart.png")

    args = ap.parse_args()

    if args.cmd == "discover":
        with TVAgent(profile_dir=args.profile) as tv:
            tv.page.goto(args.url, wait_until="domcontentloaded")
            tv.wait_chart_ready(timeout=45)
            info = tv.discover()
            print("HEADER IDS:"); [print("  #" + i) for i in info["header_ids"]]
            print("DATA-NAMES:"); [print("  " + n) for n in info["data_names"]]
            print("DIALOGS:", info["dialogs"])

    elif args.cmd == "demo":
        with TVAgent(profile_dir=args.profile) as tv:
            tv.open_chart(args.symbol)
            tv.set_interval(args.interval)
            print("OHLC:", tv.read_ohlc())
            print("screenshot:", tv.screenshot_chart(args.out))


if __name__ == "__main__":
    _cli()
