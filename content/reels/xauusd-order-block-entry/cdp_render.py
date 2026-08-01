#!/usr/bin/env python3
"""Render reel_frame.html to a frame sequence by driving one headless Chromium via the
DevTools Protocol (pure-stdlib websocket). Calls window.render(p) per frame, captures a
screenshot, writes frames/f%05d.png. Usage: cdp_render.py <frames> <seconds>"""
import sys, os, json, time, socket, struct, base64, subprocess, urllib.request, hashlib

HERE=os.path.dirname(os.path.abspath(__file__))
FRAMES=int(sys.argv[1]) if len(sys.argv)>1 else 360
SECONDS=float(sys.argv[2]) if len(sys.argv)>2 else 12.0
CHROME="/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
PORT=9333
HTMLF=sys.argv[3] if len(sys.argv)>3 else "reel_frame.html"
URL="file://"+os.path.join(HERE,HTMLF)
FR=os.path.join(HERE,"frames"); os.makedirs(FR,exist_ok=True)
for f in os.listdir(FR):
    if f.endswith((".png",".jpg")): os.remove(os.path.join(FR,f))

proc=subprocess.Popen([CHROME,"--headless=new","--no-sandbox","--disable-gpu","--hide-scrollbars",
    f"--remote-debugging-port={PORT}","--force-device-scale-factor=1","--window-size=1080,1920",
    f"--user-data-dir=/tmp/cdp-{PORT}",URL],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def get_ws():
    for _ in range(60):
        try:
            j=json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list"))
            for t in j:
                if t.get("type")=="page" and t.get("webSocketDebuggerUrl"):
                    return t["webSocketDebuggerUrl"]
        except Exception: pass
        time.sleep(0.5)
    raise RuntimeError("no devtools page")

wsurl=get_ws()
host,port,path=wsurl.split("/",3)[2].split(":")[0], int(wsurl.split(":")[2].split("/")[0]), "/"+wsurl.split("/",3)[3]
sock=socket.create_connection((host,port)); sock.settimeout(30)
key=base64.b64encode(os.urandom(16)).decode()
req=(f"GET {path} HTTP/1.1\r\nHost: {host}:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
     f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
sock.sendall(req.encode())
buf=b""
while b"\r\n\r\n" not in buf: buf+=sock.recv(4096)

def recvn(n):
    d=b""
    while len(d)<n:
        c=sock.recv(n-len(d))
        if not c: raise RuntimeError("closed")
        d+=c
    return d
def recv_frame():
    b=recvn(2); b0,b1=b[0],b[1]; fin=b0&0x80; ln=b1&0x7f; masked=b1&0x80
    if ln==126: ln=struct.unpack(">H",recvn(2))[0]
    elif ln==127: ln=struct.unpack(">Q",recvn(8))[0]
    mk=recvn(4) if masked else None
    pl=recvn(ln)
    if mk: pl=bytes(pl[i]^mk[i%4] for i in range(ln))
    return fin,pl
def recv_msg():
    fin,pl=recv_frame(); data=pl
    while not fin:
        fin,pl=recv_frame(); data+=pl
    return data
def send(obj):
    data=json.dumps(obj).encode(); l=len(data); mask=os.urandom(4); h=b"\x81"
    if l<126: h+=bytes([0x80|l])
    elif l<65536: h+=bytes([0x80|126])+struct.pack(">H",l)
    else: h+=bytes([0x80|127])+struct.pack(">Q",l)
    h+=mask; sock.sendall(h+bytes(data[i]^mask[i%4] for i in range(l)))

_id=0
def cmd(method,params=None,want=True):
    global _id; _id+=1; mid=_id; send({"id":mid,"method":method,"params":params or {}})
    if not want: return None
    while True:
        m=json.loads(recv_msg())
        if m.get("id")==mid: return m

cmd("Page.enable"); cmd("Runtime.enable")
cmd("Emulation.setDeviceMetricsOverride",{"width":1080,"height":1920,"deviceScaleFactor":1,"mobile":False})
cmd("Runtime.evaluate",{"expression":"document.fonts.ready.then(()=>true)","awaitPromise":True})
time.sleep(0.4)

HOLD=int(FRAMES*0.08)  # hold final frame
total=FRAMES+HOLD
t0=time.time()
for i in range(total):
    p = 1.0 if i>=FRAMES else i/(FRAMES-1)
    cmd("Runtime.evaluate",{"expression":f"render({p:.5f})"})
    r=cmd("Page.captureScreenshot",{"format":"jpeg","quality":93,"captureBeyondViewport":False})
    data=base64.b64decode(r["result"]["data"])
    open(os.path.join(FR,f"f{i:05d}.jpg"),"wb").write(data)
    if i%40==0: print(f"  frame {i}/{total} ({time.time()-t0:.1f}s)")
print(f"captured {total} frames in {time.time()-t0:.1f}s")
try: cmd("Browser.close",want=False)
except Exception: pass
proc.terminate()
print("FPS_TARGET", round(total/SECONDS,2))
