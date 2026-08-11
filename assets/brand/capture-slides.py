#!/usr/bin/env python3
"""Render every .ls-c page of a carousel to a PNG, and refuse to do it quietly
if any chart on the page failed its own accuracy rules.

    python3 capture-slides.py carousel-demo.html out/

Chromium is the only renderer used anywhere in this pipeline for a reason: it
shapes and bidi-orders Arabic correctly. Nothing here pre-reshapes text, and
nothing should — hand raw Arabic to a smart renderer and leave it alone.
"""
import base64, json, os, shutil, subprocess, sys, time, urllib.request

# websocket-client honours proxy env vars — loopback must bypass the agent proxy
os.environ["no_proxy"] = os.environ["NO_PROXY"] = "127.0.0.1,localhost"

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
PORT = 9334
PAGE = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else "slides"
SCALE = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
W, H = 1160, 1420          # viewport: one page plus room for the deck gutter

os.makedirs(OUT, exist_ok=True)

proc = subprocess.Popen(
    [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
     "--allow-file-access-from-files", "--force-device-scale-factor=1",
     "--force-color-profile=srgb",
     f"--remote-debugging-port={PORT}", "--remote-allow-origins=*",
     f"--window-size={W},{H}", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

ws = None
last = None
for _ in range(60):
    try:
        t = [x for x in json.loads(
            opener.open(f"http://127.0.0.1:{PORT}/json", timeout=5).read())
            if x["type"] == "page"][0]
        import websocket
        ws = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=30)
        break
    except Exception as exc:
        last = exc
        time.sleep(0.5)
if ws is None:
    proc.kill(); sys.exit(f"could not attach to chromium: {last!r}")

_id = [0]
def cmd(method, params=None):
    _id[0] += 1
    ws.send(json.dumps({"id": _id[0], "method": method, "params": params or {}}))
    while True:
        m = json.loads(ws.recv())
        if m.get("id") == _id[0]:
            if "error" in m:
                raise RuntimeError(f"{method}: {m['error']}")
            return m.get("result", {})

def ev(expr):
    r = cmd("Runtime.evaluate", {"expression": expr, "returnByValue": True})
    if "exceptionDetails" in r:
        raise RuntimeError(r["exceptionDetails"].get("text", "js error"))
    return r.get("result", {}).get("value")

cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",
    {"width": W, "height": H, "deviceScaleFactor": 1, "mobile": False})
cmd("Page.navigate", {"url": f"file://{os.path.abspath(PAGE)}"})

for _ in range(120):
    time.sleep(0.25)
    if ev("window.LS_READY === true"):
        break
else:
    proc.kill(); sys.exit("page never signalled LS_READY "
                          "(webfonts must resolve before anything is measured)")

# A drawing that broke its own rule is a bug in the slide, not a rendering
# note — say so loudly, before the PNGs make it look finished.
viol = ev("JSON.stringify(window.LS_VIOLATIONS || [])")
corr = ev("JSON.stringify(window.LS_CORRECTIONS || [])")
viol, corr = json.loads(viol), json.loads(corr)
print(f"violations: {len(viol)}   corrections: {len(corr)}")
for v in viol:
    print("  ✗", json.dumps(v, ensure_ascii=False))
for c in corr:
    print("  ~", json.dumps(c, ensure_ascii=False))

boxes = ev("""JSON.stringify([...document.querySelectorAll('.ls-c')].map(e => {
  const r = e.getBoundingClientRect();
  return {x: r.x + scrollX, y: r.y + scrollY, w: r.width, h: r.height};
}))""")
boxes = json.loads(boxes)
print(f"{len(boxes)} pages")

for i, b in enumerate(boxes, 1):
    shot = cmd("Page.captureScreenshot", {
        "format": "png", "captureBeyondViewport": True,
        "clip": {"x": b["x"], "y": b["y"], "width": b["w"],
                 "height": b["h"], "scale": SCALE}})
    path = os.path.join(OUT, f"slide{i}.png")
    with open(path, "wb") as fh:
        fh.write(base64.b64decode(shot["data"]))
    print(f"  {i}: {b['w']:.0f}x{b['h']:.0f} → {path}")

ws.close(); proc.terminate(); proc.wait(timeout=10)
sys.exit(1 if viol else 0)
