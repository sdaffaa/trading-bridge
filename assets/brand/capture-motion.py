#!/usr/bin/env python3
"""Frame-accurate capture of an LSChart motion page via Chrome DevTools Protocol."""
import base64, json, os, shutil, subprocess, sys, time, urllib.request

# websocket-client honours proxy env vars — loopback must bypass the agent proxy
os.environ["no_proxy"] = os.environ["NO_PROXY"] = "127.0.0.1,localhost"

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
PORT = 9333
PAGE = sys.argv[1]
OUT = sys.argv[2]
FPS = int(sys.argv[3]) if len(sys.argv) > 3 else 30
W, H = 1080, 1350

frames = os.path.join(os.path.dirname(OUT), "_frames")
shutil.rmtree(frames, ignore_errors=True)
os.makedirs(frames, exist_ok=True)

proc = subprocess.Popen(
    [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
     "--allow-file-access-from-files", "--force-device-scale-factor=1",
     f"--remote-debugging-port={PORT}", "--remote-allow-origins=*", f"--window-size={W},{H}", "about:blank"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # never proxy localhost

def targets():
    return json.loads(opener.open(f"http://127.0.0.1:{PORT}/json", timeout=5).read())

ws = None
last = None
for _ in range(60):
    try:
        t = [x for x in targets() if x["type"] == "page"][0]
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
    return r.get("result", {}).get("value")

cmd("Page.enable")
cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",
    {"width": W, "height": H, "deviceScaleFactor": 1, "mobile": False})
cmd("Page.navigate", {"url": f"file://{os.path.abspath(PAGE)}?static"})

for _ in range(120):
    time.sleep(0.25)
    if ev("window.LS_READY === true"):
        break
else:
    proc.kill(); sys.exit("page never signalled LS_READY")

dur = float(ev("window.LS_DURATION") or 0)
total = dur + 1.5                      # hold the finished chart for a beat
n = int(total * FPS)
print(f"timeline {dur:.2f}s → capturing {n} frames at {FPS}fps ({total:.2f}s)")

for k in range(n):
    t = k / FPS
    ev(f"window.seekTo({t})")
    shot = cmd("Page.captureScreenshot", {"format": "jpeg", "quality": 92})
    with open(os.path.join(frames, f"f{k:05d}.jpg"), "wb") as fh:
        fh.write(base64.b64decode(shot["data"]))
    if k % 60 == 0:
        print(f"  {t:5.1f}s  frame {k}/{n}")

ws.close(); proc.terminate(); proc.wait(timeout=10)
print("frames done")

FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
subprocess.run([FF, "-y", "-framerate", str(FPS), "-i", os.path.join(frames, "f%05d.jpg"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                "-movflags", "+faststart", OUT], check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
shutil.rmtree(frames, ignore_errors=True)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
