"""Chart screenshot — open the TradingView chart headless and capture it.

Uses Playwright + Chromium to load the public TradingView chart for a
symbol/timeframe and screenshot it, so the vision agents can mark it up. No
login needed (public chart shows real candles). Heavy: needs Chromium and
enough RAM — run on a 2GB+ host. Returns PNG bytes or None on failure.
"""
import os

from . import config
from .logging_setup import jlog


def capture(symbol: str, timeframe: str) -> bytes:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        jlog("chartshot_error", reason="playwright not installed")
        return None

    tv_interval = _tv_interval(timeframe)
    url = config.CHART_URL_TEMPLATE.format(
        symbol=symbol.replace(":", "%3A"), interval=tv_interval)
    try:
        with sync_playwright() as p:
            kw = dict(headless=True,
                      args=["--no-sandbox", "--disable-dev-shm-usage",
                            "--disable-gpu", "--window-size=1400,900"])
            if os.path.exists(config.CHROMIUM_PATH):
                kw["executable_path"] = config.CHROMIUM_PATH
            browser = p.chromium.launch(**kw)
            page = browser.new_page(viewport={"width": 1400, "height": 900})
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            # let the chart canvas render, then dismiss any popups
            page.wait_for_timeout(config.SHOT_WAIT_MS)
            _dismiss(page)
            page.wait_for_timeout(1500)
            png = page.screenshot(type="png")
            browser.close()
        jlog("chartshot_ok", symbol=symbol, timeframe=timeframe, bytes=len(png))
        return png
    except Exception as e:
        jlog("chartshot_error", symbol=symbol, error=str(e)[:200])
        return None


def _tv_interval(tf: str) -> str:
    # TradingView URL intervals: 1,2,3,5,10,15,30,60,120,240,1D,1W
    m = {"1": "1", "2": "2", "3": "3", "5": "5", "10": "10", "15": "15",
         "30": "30", "60": "60", "1H": "60", "120": "120", "2H": "120",
         "240": "240", "4H": "240", "1D": "1D", "D": "1D", "1W": "1W", "W": "1W"}
    return m.get(str(tf), str(tf))


def _dismiss(page):
    """Best-effort close of TradingView's sign-in / cookie popups."""
    for sel in ('button[aria-label="Close"]', 'button:has-text("Accept all")',
                '.tv-dialog__close', '[data-name="close"]'):
        try:
            el = page.locator(sel).first
            if el.count() and el.is_visible():
                el.click(timeout=1500)
        except Exception:
            pass
