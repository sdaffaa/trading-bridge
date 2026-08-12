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
# --spec switches to the delivery encode: PNG frames, H.264 High, Rec.709,
# 15-20 Mbps VBR, silent 48k AAC track. The default stays as it was so the
# reels already rendered stay reproducible byte for byte.
SPEC = "--spec" in sys.argv[4:]
# --deliver renders a 2x master (2160x3840 for a 1080x1920 page) by raising the
# device pixel ratio rather than the layout size — every CSS length, font and
# stroke stays exactly where it was, there is just twice the sampling — then
# downscales with lanczos and encodes 2-pass VBR. Supersampling is the one
# "enhancement" that cannot invent a detail, which is why it is the only one
# used on a page whose candles are the subject.
DELIVER = "--deliver" in sys.argv[4:]
if DELIVER:
    SPEC = True
# Default is the 4:5 post canvas; a page that is a different shape says so in
# window.LS_SIZE and the viewport is re-fitted to it after load.
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
    {"width": W, "height": H, "deviceScaleFactor": 2 if DELIVER else 1, "mobile": False})
cmd("Page.navigate", {"url": f"file://{os.path.abspath(PAGE)}?static"})

for _ in range(120):
    time.sleep(0.25)
    if ev("window.LS_READY === true"):
        break
else:
    proc.kill(); sys.exit("page never signalled LS_READY")

size = ev("JSON.stringify(window.LS_SIZE || null)")
if size:
    W, H = json.loads(size)
    cmd("Emulation.setDeviceMetricsOverride",
        {"width": W, "height": H, "deviceScaleFactor": 2 if DELIVER else 1, "mobile": False})
    print(f"canvas {W}x{H}" + (f" → master {W*2}x{H*2}" if DELIVER else ""))

viol = json.loads(ev("JSON.stringify(window.LS_VIOLATIONS || [])"))
if viol:
    # A drawing that broke its own rule is a bug in the page. Say it before
    # spending two minutes rendering it into something that looks finished.
    for v in viol:
        print("  ✗", json.dumps(v, ensure_ascii=False))
    proc.kill(); sys.exit(f"{len(viol)} drawing violation(s) — fix the page first")

dur = float(ev("window.LS_DURATION") or 0)
# A markup page holds on its finished chart for a beat. A looping reel must
# not: the last frame is engineered to match the first, and a tail after it
# is a visible stutter every time the reel repeats.
tail = ev("window.LS_TAIL")
tail = 1.5 if tail is None else float(tail)
total = dur + tail
n = int(total * FPS)
print(f"timeline {dur:.2f}s → capturing {n} frames at {FPS}fps ({total:.2f}s)")

for k in range(n):
    t = k / FPS
    ev(f"window.seekTo({t})")
    shot = cmd("Page.captureScreenshot",
               {"format": "png"} if SPEC else {"format": "jpeg", "quality": 92})
    with open(os.path.join(frames, f"f{k:05d}." + ("png" if SPEC else "jpg")), "wb") as fh:
        fh.write(base64.b64decode(shot["data"]))
    if k % 60 == 0:
        print(f"  {t:5.1f}s  frame {k}/{n}")

ws.close(); proc.terminate(); proc.wait(timeout=10)
print("frames done")

FF = "/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
if SPEC:
    # Delivery profile: H.264 High, Rec.709 tagged, faststart. Frames are
    # captured as PNG in this mode so the encoder is the only generation loss.
    # Silent AAC track so the file carries the declared audio layout even
    # before a music bed exists.
    #
    # The 15-20 Mbps figures below are a CEILING, not a target. Measured: a
    # 32s reel at 1080x1920 comes out around 2.4 Mbps, and re-encoding it with
    # these same flags still lands near 1.6 Mbps — flat dark charts and large
    # areas of solid colour compress far below the cap, and x264 will not pad
    # to a bitrate the picture does not need. Forcing it (nal-hrd=cbr plus
    # filler) would multiply the file size for no visible gain, so the cap
    # stays a cap.
    common = ["-c:v", "libx264", "-profile:v", "high", "-level", "4.0",
              "-pix_fmt", "yuv420p",
              "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
              # a keyframe every second, so scrubbing lands where the viewer aimed
              "-g", str(FPS), "-keyint_min", str(FPS), "-sc_threshold", "0"]
    if DELIVER:
        # 2-pass VBR off the 2x master. The bitrate figures are a CEILING, not a
        # floor — see the note below.
        vf = ["-vf", f"scale={W}:{H}:flags=lanczos"]
        rate = ["-b:v", "14M", "-maxrate", "20M", "-bufsize", "28M"]
        log = os.path.join(os.path.dirname(OUT) or ".", "_x264")
        subprocess.run([FF, "-y", "-framerate", str(FPS), "-i", os.path.join(frames, "f%05d.png")]
                       + vf + common + rate + ["-pass", "1", "-passlogfile", log,
                                               "-an", "-f", "mp4", os.devnull],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        args = ([FF, "-y", "-framerate", str(FPS), "-i", os.path.join(frames, "f%05d.png"),
                 "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
                 "-shortest"] + vf + common + rate
                + ["-pass", "2", "-passlogfile", log,
                   "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
                   "-movflags", "+faststart", OUT])
    else:
        args = ([FF, "-y", "-framerate", str(FPS), "-i", os.path.join(frames, "f%05d.png"),
                 "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
                 "-shortest"] + common
                + ["-b:v", "17M", "-maxrate", "20M", "-minrate", "15M", "-bufsize", "34M",
                   "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
                   "-movflags", "+faststart", OUT])
else:
    args = [FF, "-y", "-framerate", str(FPS), "-i", os.path.join(frames, "f%05d.jpg"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
            "-movflags", "+faststart", OUT]
subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
shutil.rmtree(frames, ignore_errors=True)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
