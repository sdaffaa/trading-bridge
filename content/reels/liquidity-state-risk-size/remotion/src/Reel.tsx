import React, { useEffect, useState } from "react";
import {
  AbsoluteFill,
  Sequence,
  interpolate,
  useCurrentFrame,
  Easing,
  staticFile,
  delayRender,
  continueRender,
} from "remotion";

export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const RUNTIME_S = 21.0;

// ---- palette (Liquidity State) ----
const C = {
  bg: "#0E1E24",
  bg2: "#0A0C10",
  teal: "#2E9E8F",
  silver: "#C9D1D6",
  gold: "#D6A94A",
  text: "#F2F5F7",
  red: "#E15A5A",
  up: "#26A69A",
  down: "#EF5350",
  panel: "#0F1A20",
};

const clamp = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
const F = (s: number) => Math.round(s * FPS);

// ============================================================= fonts
const FontLoader: React.FC = () => {
  const [handle] = useState(() => delayRender("load-fonts"));
  useEffect(() => {
    const run = async () => {
      try {
        await Promise.all([
          (document as any).fonts.load('400 100px Tajawal', 'اختبار0123'),
          (document as any).fonts.load('700 100px Tajawal', 'اختبار0123'),
          (document as any).fonts.load('800 100px Tajawal', 'اختبار0123'),
        ]);
        await (document as any).fonts.ready;
      } catch (e) {}
      continueRender(handle);
    };
    run();
  }, [handle]);
  return <link rel="stylesheet" href={staticFile("fonts.css")} />;
};

// ============================================================= background
const Bg: React.FC = () => {
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(120% 90% at 50% 38%, #12303a 0%, ${C.bg} 42%, ${C.bg2} 100%)`,
      }}
    >
      {/* vignette */}
      <AbsoluteFill
        style={{
          boxShadow: "inset 0 0 420px 90px rgba(0,0,0,0.55)",
          pointerEvents: "none",
        }}
      />
    </AbsoluteFill>
  );
};

// ============================================================= candles
type Candle = { o: number; h: number; l: number; c: number };
function genCandles(): Candle[] {
  // deterministic LCG — brand-style illustrative candles (educational lesson)
  let seed = 20260727;
  const rnd = () => {
    seed = (seed * 1103515245 + 12345) & 0x7fffffff;
    return seed / 0x7fffffff;
  };
  const out: Candle[] = [];
  let price = 2360;
  for (let i = 0; i < 46; i++) {
    // choppy zone in the middle to read as "consecutive losses"
    const chop = i > 16 && i < 30 ? 1.9 : 1.0;
    const drift = i > 16 && i < 34 ? -0.35 : 0.12;
    const o = price;
    const move = (rnd() - 0.5) * 9 * chop + drift;
    const c = o + move;
    const h = Math.max(o, c) + rnd() * 4 * chop;
    const l = Math.min(o, c) - rnd() * 4 * chop;
    out.push({ o, h, l, c });
    price = c;
  }
  return out;
}
const CANDLES = genCandles();
const PX = { x: 70, y: 380, w: 940, h: 560 };

const ChartPanel: React.FC<{
  reveal: number; // 0..1 how many candles shown
  dim?: number; // 0..1 (1 = full bright)
  hud?: number; // 0..1 drawdown fill
  failed?: boolean;
  showDDLine?: boolean;
}> = ({ reveal, dim = 1, hud = 0, failed = false, showDDLine = true }) => {
  const vals = CANDLES.flatMap((c) => [c.h, c.l]);
  const min = Math.min(...vals) - 2;
  const max = Math.max(...vals) + 2;
  const Y = (v: number) => PX.y + PX.h - ((v - min) / (max - min)) * PX.h;
  const n = CANDLES.length;
  const cw = PX.w / n;
  const shown = Math.floor(reveal * n);
  const ddY = PX.y + PX.h * 0.86; // "10% drawdown" line near lower area

  return (
    <div style={{ opacity: dim }}>
      <svg width={WIDTH} height={HEIGHT} style={{ position: "absolute", inset: 0 }}>
        {/* panel frame */}
        <rect x={PX.x - 14} y={PX.y - 40} width={PX.w + 28} height={PX.h + 80} rx={22}
          fill={C.panel} stroke="rgba(201,209,214,0.12)" strokeWidth={2} />
        {/* grid */}
        {[0.2, 0.4, 0.6, 0.8].map((g, i) => (
          <line key={i} x1={PX.x} x2={PX.x + PX.w} y1={PX.y + PX.h * g} y2={PX.y + PX.h * g}
            stroke="rgba(201,209,214,0.06)" strokeWidth={1} />
        ))}
        {/* candles */}
        {CANDLES.slice(0, shown).map((cd, i) => {
          const cx = PX.x + i * cw + cw / 2;
          const up = cd.c >= cd.o;
          const col = up ? C.up : C.down;
          const bodyTop = Y(Math.max(cd.o, cd.c));
          const bodyBot = Y(Math.min(cd.o, cd.c));
          const isLast3 = i >= shown - 3 && reveal < 0.999;
          return (
            <g key={i} opacity={isLast3 ? 0.9 : 1}>
              <line x1={cx} x2={cx} y1={Y(cd.h)} y2={Y(cd.l)} stroke={col} strokeWidth={2} />
              <rect x={cx - cw * 0.32} y={bodyTop} width={cw * 0.64}
                height={Math.max(2, bodyBot - bodyTop)} fill={col} rx={1} />
            </g>
          );
        })}
        {/* 10% drawdown line */}
        {showDDLine && (
          <>
            <line x1={PX.x} x2={PX.x + PX.w} y1={ddY} y2={ddY}
              stroke={C.red} strokeWidth={3} strokeDasharray="10 8" opacity={0.9} />
            <text x={PX.x + PX.w - 8} y={ddY - 12} textAnchor="end"
              fontFamily="Tajawal" fontWeight={700} fontSize={26} fill={C.red}>
              -10% حد السحب
            </text>
          </>
        )}
      </svg>
      {/* HUD drawdown meter top-right */}
      <div style={{
        position: "absolute", top: PX.y - 30, right: PX.x, width: 240, height: 30,
        borderRadius: 8, background: "rgba(255,255,255,0.06)",
        border: "1px solid rgba(201,209,214,0.2)", overflow: "hidden",
      }}>
        <div style={{
          position: "absolute", left: 0, top: 0, bottom: 0,
          width: `${Math.min(100, hud * 100)}%`,
          background: failed ? C.red : `linear-gradient(90deg, ${C.gold}, ${C.red})`,
        }} />
      </div>
      <div style={{
        position: "absolute", top: PX.y - 34, right: PX.x + 252,
        fontFamily: "Tajawal", fontWeight: 700, fontSize: 24,
        color: failed ? C.red : C.silver, direction: "rtl",
      }}>
        {failed ? "FAILED" : "Drawdown"}
      </div>
    </div>
  );
};

// ============================================================= equity paths
const EquityPaths: React.FC<{
  reveal: number; showLabels?: boolean; only05?: boolean; dim?: number;
}> = ({ reveal, showLabels = true, only05 = false, dim = 1 }) => {
  // two curves: red (2%) breaks below the 10% line, teal (0.5%) stays safe
  const x0 = PX.x + 20, x1 = PX.x + PX.w - 20;
  const baseY = PX.y + 120;
  const ddY = PX.y + PX.h * 0.86;
  const seg = 40;
  const pts = (kind: "red" | "teal") => {
    const arr: string[] = [];
    for (let i = 0; i <= seg; i++) {
      const t = i / seg;
      const x = x0 + (x1 - x0) * t;
      let y;
      if (kind === "red") {
        y = baseY + Math.sin(t * 7) * 26 + t * (ddY - baseY + 70);
      } else {
        y = baseY + Math.sin(t * 5) * 14 + t * (ddY - baseY - 90) * 0.55;
      }
      arr.push(`${x.toFixed(1)},${y.toFixed(1)}`);
    }
    const cut = Math.max(1, Math.floor(reveal * (seg + 1)));
    return arr.slice(0, cut).join(" ");
  };
  return (
    <div style={{ opacity: dim }}>
      <svg width={WIDTH} height={HEIGHT} style={{ position: "absolute", inset: 0 }}>
        {!only05 && <polyline points={pts("red")} fill="none" stroke={C.red} strokeWidth={6}
          strokeLinejoin="round" strokeLinecap="round" />}
        <polyline points={pts("teal")} fill="none" stroke={C.teal} strokeWidth={6}
          strokeLinejoin="round" strokeLinecap="round" />
        {showLabels && (
          <>
            {!only05 && <text x={x1} y={ddY + 60} textAnchor="end" fontFamily="Tajawal"
              fontWeight={800} fontSize={40} fill={C.red}>2%</text>}
            <text x={x1} y={baseY + 40} textAnchor="end" fontFamily="Tajawal"
              fontWeight={800} fontSize={40} fill={C.teal}>0.5%</text>
          </>
        )}
      </svg>
    </div>
  );
};

// ============================================================= risk blocks (beat 8)
const RiskBlocks: React.FC<{ redCount: number; tealCount: number; flash: number }> = ({
  redCount, tealCount, flash,
}) => {
  const lineY = 250;
  const redBlockW = 150, redBlockH = 40;
  const tealBlockW = 40, tealBlockH = 40;
  return (
    <div style={{ position: "absolute", top: 560, left: 0, width: WIDTH, textAlign: "center" }}>
      {/* the 10% ceiling line */}
      <div style={{
        position: "relative", width: 900, margin: "0 auto",
      }}>
        <div style={{
          position: "absolute", top: lineY, left: 0, right: 0, height: 4,
          background: C.red, opacity: flash, boxShadow: `0 0 24px ${C.red}`,
        }} />
        <div style={{
          position: "absolute", top: lineY - 44, right: 0, fontFamily: "Tajawal",
          fontWeight: 700, fontSize: 30, color: C.red, direction: "rtl",
        }}>خط الـ 10%</div>
        {/* red row: 5 x 2% growing up to the line */}
        <div style={{ position: "absolute", top: lineY - redBlockH, left: 60, display: "flex", flexDirection: "column-reverse", gap: 6 }}>
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} style={{
              width: redBlockW, height: redBlockH, borderRadius: 6,
              background: C.red, opacity: i < redCount ? 1 : 0.08,
              display: "flex", alignItems: "center", justifyContent: "center",
              fontFamily: "Tajawal", fontWeight: 700, color: "#2a0d0d", fontSize: 22,
            }}>2%</div>
          ))}
        </div>
        {/* teal row: 20 x 0.5% */}
        <div style={{ position: "absolute", top: lineY - tealBlockH, left: 420, display: "flex", flexDirection: "column-reverse", gap: 1 }}>
          {Array.from({ length: 20 }).map((_, i) => (
            <div key={i} style={{
              width: tealBlockW, height: 11, borderRadius: 3,
              background: C.teal, opacity: i < tealCount ? 1 : 0.08,
            }} />
          ))}
          <div style={{ marginTop: 8, fontFamily: "Tajawal", fontWeight: 700, color: C.teal, fontSize: 22 }}>0.5%</div>
        </div>
      </div>
    </div>
  );
};

// ============================================================= two panels (beat 7)
const TwoPanels: React.FC<{ p: number }> = ({ p }) => {
  return (
    <div style={{
      position: "absolute", top: 560, left: 90, right: 90,
      display: "flex", flexDirection: "column", gap: 26, direction: "rtl",
    }}>
      <div style={{
        padding: "34px 40px", borderRadius: 18, background: "rgba(46,158,143,0.10)",
        border: "1px solid rgba(46,158,143,0.3)", opacity: interpolate(p, [0, 1], [1, 0.32], clamp),
        fontFamily: "Tajawal", fontWeight: 700, fontSize: 46, color: C.silver, textAlign: "center",
      }}>الهدف 5% — بدون سقف زمني</div>
      <div style={{
        padding: "34px 40px", borderRadius: 18, background: "rgba(225,90,90,0.12)",
        border: `2px solid ${C.red}`, opacity: 1,
        boxShadow: `0 0 ${interpolate(p, [0, 1], [0, 40], clamp)}px rgba(225,90,90,0.4)`,
        fontFamily: "Tajawal", fontWeight: 800, fontSize: 50, color: C.text, textAlign: "center",
      }}>
        حد الخسارة 10% — <span style={{ color: C.gold }}>نهائي</span>
      </div>
    </div>
  );
};

// ============================================================= messy indicators (beat 5+6)
const Indicators: React.FC<{ count: number }> = ({ count }) => {
  const items = ["EMA 50", "EMA 200", "RSI", "زون طلب", "أسهم دخول"];
  return (
    <svg width={WIDTH} height={HEIGHT} style={{ position: "absolute", inset: 0, opacity: 0.6 }}>
      {items.slice(0, count).map((label, i) => {
        const yb = PX.y + 60 + i * 90;
        return (
          <g key={i}>
            <path d={`M ${PX.x} ${yb} q 200 ${i % 2 ? -70 : 70} 460 ${i % 2 ? 20 : -20} t 460 ${i % 2 ? -30 : 30}`}
              fill="none" stroke={i % 2 ? C.gold : C.silver} strokeWidth={3} opacity={0.7} />
            <text x={PX.x + 10} y={yb - 10} fontFamily="Tajawal" fontWeight={700} fontSize={26}
              fill={i % 2 ? C.gold : C.silver} direction="rtl">{label}</text>
          </g>
        );
      })}
    </svg>
  );
};

// ============================================================= equations (beat 10)
const Equations: React.FC<{ reveal: number }> = ({ reveal }) => {
  const rows = [
    { a: "2%", n: "× 5", eq: "= 10%", col: C.red },
    { a: "0.5%", n: "× 20", eq: "= 10%", col: C.teal },
  ];
  return (
    <div style={{
      position: "absolute", top: 720, left: 0, width: WIDTH,
      display: "flex", flexDirection: "column", alignItems: "center", gap: 30,
    }}>
      {rows.map((r, i) => (
        <div key={i} style={{
          opacity: interpolate(reveal, [i * 0.5, i * 0.5 + 0.35], [0, 1], clamp),
          transform: `translateY(${interpolate(reveal, [i * 0.5, i * 0.5 + 0.35], [18, 0], clamp)}px)`,
          fontFamily: "Tajawal", fontWeight: 800, fontSize: 86, color: C.silver,
          letterSpacing: 2, display: "flex", gap: 18, alignItems: "baseline",
        }}>
          <span style={{ color: r.col }}>{r.a}</span>
          <span style={{ color: C.silver, opacity: 0.7 }}>{r.n}</span>
          <span style={{ color: C.gold }}>{r.eq}</span>
        </div>
      ))}
    </div>
  );
};

// ============================================================= big headline text
type Motion = "wipe" | "rise" | "stamp" | "scale-in";
const BigText: React.FC<{
  text: string; color: string; size: number; motion: Motion; inAt: number; center?: boolean;
}> = ({ text, color, size, motion, inAt, center }) => {
  const frame = useCurrentFrame();
  const t = frame - F(inAt);
  let style: React.CSSProperties = {};
  if (motion === "wipe") {
    const p = interpolate(t, [0, 12], [100, 0], clamp);
    style = { clipPath: `inset(0 0 0 ${p}%)`, opacity: interpolate(t, [0, 4], [0, 1], clamp) };
  } else if (motion === "rise") {
    style = {
      transform: `translateY(${interpolate(t, [0, 9], [22, 0], clamp)}px)`,
      opacity: interpolate(t, [0, 9], [0, 1], clamp),
    };
  } else if (motion === "stamp") {
    style = {
      transform: `scale(${interpolate(t, [0, 3, 6], [1.14, 0.98, 1], clamp)})`,
      opacity: interpolate(t, [0, 2], [0, 1], clamp),
    };
  } else {
    style = {
      transform: `scale(${interpolate(t, [0, 9], [0.96, 1], clamp)})`,
      opacity: interpolate(t, [0, 9], [0, 1], clamp),
    };
  }
  return (
    <div style={{
      position: "absolute", left: 70, right: 70,
      top: center ? 760 : 1120,
      textAlign: "center", direction: "rtl",
    }}>
      <div style={{
        display: "inline-block",
        fontFamily: "Tajawal", fontWeight: 800, fontSize: size, lineHeight: 1.15,
        color, textShadow: "0 4px 30px rgba(0,0,0,0.7)", ...style,
      }}>{text}</div>
    </div>
  );
};

// ============================================================= caption (burned VO)
const Caption: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [0, 6], [0, 1], clamp);
  return (
    <div style={{
      position: "absolute", left: 80, right: 80, top: 1500, textAlign: "center",
      direction: "rtl", opacity: op,
    }}>
      <span style={{
        fontFamily: "Tajawal", fontWeight: 700, fontSize: 40, color: C.text,
        lineHeight: 1.4, background: "rgba(10,12,16,0.55)", padding: "8px 20px",
        borderRadius: 12, boxDecorationBreak: "clone",
        WebkitBoxDecorationBreak: "clone",
        textShadow: "0 2px 8px rgba(0,0,0,0.9)",
      }}>{text}</span>
    </div>
  );
};

const EduTag: React.FC = () => (
  <div style={{
    position: "absolute", top: 232, left: 0, width: WIDTH, textAlign: "center",
    fontFamily: "Tajawal", fontWeight: 500, fontSize: 24, color: "rgba(201,209,214,0.55)",
    direction: "rtl", letterSpacing: 1,
  }}>لغرض تعليمي · الحساب على حد سحب 10% ثابت</div>
);

// ============================================================= camera rig
type Cam =
  | { kind: "push"; pct: number; dur: number }
  | { kind: "pull"; pct: number; dur: number }
  | { kind: "locked" }
  | { kind: "trackDown"; px: number; dur: number }
  | { kind: "shake"; px: number; hz: number; dur: number };

const CameraRig: React.FC<{ cam: Cam; children: React.ReactNode }> = ({ cam, children }) => {
  const frame = useCurrentFrame();
  let transform = "";
  const ease = Easing.bezier(0.16, 1, 0.3, 1);
  if (cam.kind === "push") {
    const s = interpolate(frame, [0, F(cam.dur)], [1, 1 + cam.pct / 100], { ...clamp, easing: ease });
    transform = `scale(${s})`;
  } else if (cam.kind === "pull") {
    const s = interpolate(frame, [0, F(cam.dur)], [1 + cam.pct / 100, 1], { ...clamp, easing: ease });
    transform = `scale(${s})`;
  } else if (cam.kind === "trackDown") {
    const y = interpolate(frame, [0, F(cam.dur)], [0, cam.px], { ...clamp, easing: ease });
    transform = `translateY(${-y}px)`;
  } else if (cam.kind === "shake") {
    const active = frame < F(cam.dur) ? 1 : 0;
    const dx = Math.sin(frame * cam.hz) * cam.px * active;
    const dy = Math.cos(frame * cam.hz * 1.3) * cam.px * active;
    transform = `translate(${dx}px, ${dy}px)`;
  }
  return (
    <AbsoluteFill style={{ transform, transformOrigin: "center center" }}>{children}</AbsoluteFill>
  );
};

// ============================================================= scenes per beat
const useLocal = () => useCurrentFrame();

const Scene: React.FC<{ id: string; dur: number; children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill>{children}</AbsoluteFill>
);

// ============================================================= the reel
export const Reel: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: C.bg }}>
      <FontLoader />
      <Bg />
      <EduTag />

      {/* BEAT 1 · HOOK 0.0-2.6 */}
      <Sequence from={F(0)} durationInFrames={F(2.6)}>
        <CameraRig cam={{ kind: "push", pct: 4, dur: 2.4 }}>
          <B1 />
        </CameraRig>
      </Sequence>

      {/* BEAT 2 · PARADOX 2.6-4.2 */}
      <Sequence from={F(2.6)} durationInFrames={F(1.6)}>
        <CameraRig cam={{ kind: "locked" }}><B2 /></CameraRig>
      </Sequence>

      {/* BEAT 3 · PIVOT 4.2-5.0 */}
      <Sequence from={F(4.2)} durationInFrames={F(0.8)}>
        <CameraRig cam={{ kind: "locked" }}><B3 /></CameraRig>
      </Sequence>

      {/* BEAT 4 · INVITE 5.0-6.2 */}
      <Sequence from={F(5.0)} durationInFrames={F(1.2)}>
        <CameraRig cam={{ kind: "pull", pct: 6, dur: 1.2 }}><B4 /></CameraRig>
      </Sequence>

      {/* BEAT 5+6 · BELIEF+WHY 6.2-8.6 */}
      <Sequence from={F(6.2)} durationInFrames={F(2.4)}>
        <CameraRig cam={{ kind: "push", pct: 4, dur: 2.4 }}><B56 /></CameraRig>
      </Sequence>

      {/* BEAT 7 · TURN 8.6-10.6 */}
      <Sequence from={F(8.6)} durationInFrames={F(2.0)}>
        <CameraRig cam={{ kind: "locked" }}><B7 /></CameraRig>
      </Sequence>

      {/* BEAT 8 · TURN(number) 10.6-13.2 */}
      <Sequence from={F(10.6)} durationInFrames={F(2.6)}>
        <CameraRig cam={{ kind: "trackDown", px: 90, dur: 2.6 }}><B8 /></CameraRig>
      </Sequence>

      {/* BEAT 9 · VERDICT 13.2-13.9 (peak) */}
      <Sequence from={F(13.2)} durationInFrames={F(0.7)}>
        <CameraRig cam={{ kind: "shake", px: 3, hz: 3, dur: 0.4 }}><B9 /></CameraRig>
      </Sequence>

      {/* BEAT 10 · PROOF 13.9-16.6 */}
      <Sequence from={F(13.9)} durationInFrames={F(2.7)}>
        <CameraRig cam={{ kind: "pull", pct: 8, dur: 2.7 }}><B10 /></CameraRig>
      </Sequence>

      {/* BEAT 11 · CARE 16.6-18.0 (silent) */}
      <Sequence from={F(16.6)} durationInFrames={F(1.4)}>
        <CameraRig cam={{ kind: "locked" }}><B11 /></CameraRig>
      </Sequence>

      {/* BEAT 12 · LOOP 18.0-21.0 */}
      <Sequence from={F(18.0)} durationInFrames={F(3.0)}>
        <CameraRig cam={{ kind: "push", pct: 3, dur: 2.4 }}><B12 /></CameraRig>
      </Sequence>
    </AbsoluteFill>
  );
};

// ---- individual beats ----
const B1: React.FC = () => {
  const f = useLocal();
  const reveal = interpolate(f, [0, F(2.6)], [0.72, 0.94], clamp);
  const hud = interpolate(f, [0, F(2.6)], [0.35, 0.62], clamp);
  return (
    <Scene id="1" dur={2.6}>
      <ChartPanel reveal={reveal} hud={hud} />
      <BigText text="چم اختبار دفعت فلوسه… وطحت؟" color={C.text} size={78} motion="wipe" inAt={0.3} />
      <Caption text="چم اختبار ممول دفعت فلوسه … وطحت؟" />
    </Scene>
  );
};

const B2: React.FC = () => {
  return (
    <Scene id="2" dur={1.6}>
      {/* split screen: left rising green equity, right broken red */}
      <div style={{ position: "absolute", inset: 0 }}>
        <ChartPanel reveal={0.94} hud={0.62} dim={1} />
      </div>
      <div style={{
        position: "absolute", top: PX.y, left: WIDTH / 2, width: 3, height: PX.h,
        background: "rgba(201,209,214,0.25)",
      }} />
      <BigText text="رابح بحسابك · طايح بالاختبار" color={C.silver} size={64} motion="rise" inAt={0.2} />
      <Caption text="بحسابك الشخصي رابح… وبالاختبار تطيح" />
    </Scene>
  );
};

const B3: React.FC = () => {
  return (
    <Scene id="3" dur={0.8}>
      <ChartPanel reveal={0.94} hud={0.62} dim={0.45} />
      <BigText text="شلون؟" color={C.gold} size={140} motion="stamp" inAt={0.08} center />
    </Scene>
  );
};

const B4: React.FC = () => {
  const f = useLocal();
  const reveal = interpolate(f, [0, F(1.2)], [0, 1], clamp);
  return (
    <Scene id="4" dur={1.2}>
      <ChartPanel reveal={0.94} hud={0.62} dim={0.5} showDDLine />
      <EquityPaths reveal={reveal} showLabels={f > F(0.6)} />
      <Caption text="تعال اقولك" />
    </Scene>
  );
};

const B56: React.FC = () => {
  const f = useLocal();
  const count = Math.min(5, Math.floor(interpolate(f, [0, F(2.0)], [0, 5], clamp)) + 1);
  return (
    <Scene id="56" dur={2.4}>
      <ChartPanel reveal={0.94} hud={0.62} dim={0.8} />
      <Indicators count={count} />
      <BigText text="استراتيجية أقوى؟" color={C.silver} size={76} motion="wipe" inAt={0.3} />
      <Caption text="الكل يقول لازم استراتيجية أقوى… ويدور نموذج دخول يضبط بالباك تست" />
    </Scene>
  );
};

const B7: React.FC = () => {
  const f = useLocal();
  const p = interpolate(f, [0, F(1.2)], [0, 1], clamp);
  return (
    <Scene id="7" dur={2.0}>
      <ChartPanel reveal={0.94} hud={0.62} dim={0.28} showDDLine={false} />
      <TwoPanels p={p} />
      <BigText text="مو اختبار ربح — اختبار خسارة" color={C.red} size={80} motion="wipe" inAt={0.3} />
      <Caption text="لكن بالواقع؟ الاختبار مو اختبار ربح… اهو اختبار خسارة" />
    </Scene>
  );
};

const B8: React.FC = () => {
  const f = useLocal();
  const redCount = Math.min(5, Math.floor(interpolate(f, [F(0.1), F(1.1)], [0, 5], clamp)));
  const tealCount = Math.min(20, Math.floor(interpolate(f, [F(1.1), F(2.4)], [0, 20], clamp)));
  const flash = redCount >= 5 ? interpolate(Math.sin(f * 0.8), [-1, 1], [0.4, 1]) : 0.5;
  return (
    <Scene id="8" dur={2.6}>
      <ChartPanel reveal={0.94} hud={0.62} dim={0.16} showDDLine={false} />
      <RiskBlocks redCount={redCount} tealCount={tealCount} flash={flash} />
      <BigText text="5 خسائر ← ولا 20؟" color={C.gold} size={96} motion="scale-in" inAt={0.3} />
      <Caption text="بمخاطرة 2%… خمس خسائر تبخّر حسابك. بمخاطرة 0.5% تحتاج 20 خسارة" />
    </Scene>
  );
};

const B9: React.FC = () => {
  return (
    <Scene id="9" dur={0.7}>
      <ChartPanel reveal={0.94} hud={1} failed dim={1} showDDLine />
      <div style={{ position: "absolute", inset: 0, background: "rgba(225,90,90,0.10)" }} />
      <BigText text="تدفع فلوسه… وتطيح" color={C.text} size={92} motion="stamp" inAt={0.02} center />
    </Scene>
  );
};

const B10: React.FC = () => {
  const f = useLocal();
  const reveal = interpolate(f, [0, F(2.4)], [0, 1.05], clamp);
  return (
    <Scene id="10" dur={2.7}>
      <ChartPanel reveal={0.94} hud={0.62} dim={0.18} showDDLine={false} />
      <div style={{
        position: "absolute", top: 470, left: 0, width: WIDTH, textAlign: "center",
        fontFamily: "Tajawal", fontWeight: 700, fontSize: 44, color: C.silver, direction: "rtl",
      }}>شوف الأرقام</div>
      <Equations reveal={reveal} />
      <Caption text="شوف الأرقام" />
    </Scene>
  );
};

const B11: React.FC = () => {
  return (
    <Scene id="11" dur={1.4}>
      <ChartPanel reveal={0.94} hud={0.4} dim={0.4} showDDLine />
      <EquityPaths reveal={1} showLabels only05 dim={1} />
      <BigText text="مخاطرتك اهي اللي تعدّيك — مو نموذجك" color={C.teal} size={78} motion="wipe" inAt={0.3} />
    </Scene>
  );
};

const B12: React.FC = () => {
  const f = useLocal();
  const reveal = interpolate(f, [F(1.2), F(3.0)], [0.72, 0.95], clamp);
  return (
    <Scene id="12" dur={3.0}>
      <ChartPanel reveal={reveal} hud={0.4} />
      <div style={{
        position: "absolute", top: 1300, left: 0, width: WIDTH, textAlign: "center",
        fontFamily: "Tajawal", fontWeight: 800, fontSize: 44, color: C.silver, direction: "ltr",
      }}>@liquidity.state</div>
      <BigText text="اكتب «ممول» بالتعليقات" color={C.gold} size={80} motion="rise" inAt={0.3} />
      <Caption text="بس چم صفقة باليوم… وچم خسارة توقفك؟ اكتب «ممول» ويوصلك الملف" />
    </Scene>
  );
};
