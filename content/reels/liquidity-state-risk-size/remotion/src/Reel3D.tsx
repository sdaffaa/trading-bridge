import React, { useEffect, useState } from "react";
import {
  AbsoluteFill, Sequence, interpolate, useCurrentFrame, Easing,
  staticFile, delayRender, continueRender,
} from "remotion";

export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const RUNTIME_S = 21.0;

// ---- brand palette (liquidity-state-brand · 3-colour budget) ----
const C = {
  bgTop: "#123039", bg: "#0E1E24", bgFloor: "#0A0C10",
  card: "#1B3A45",
  white: "#FFFFFF", grey: "#9FB4BC",
  teal: "#2ECC9A", red: "#E15A5A",
};
const clamp = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
const F = (s: number) => Math.round(s * FPS);
const EASE = Easing.bezier(0.16, 1, 0.3, 1);
const TAB: React.CSSProperties = { fontVariantNumeric: "tabular-nums", fontFeatureSettings: '"tnum" 1' };

const shade = (hex: string, pct: number) => {
  const n = parseInt(hex.slice(1), 16);
  const r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
  const f = pct / 100;
  const a = (c: number) => Math.max(0, Math.min(255, Math.round(c + (pct > 0 ? 255 - c : c) * f)));
  return `rgb(${a(r)},${a(g)},${a(b)})`;
};

const NOISE =
  "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")";

// ------------------------------------------------------------------ fonts
const FontLoader: React.FC = () => {
  const [handle] = useState(() => delayRender("load-fonts"));
  useEffect(() => {
    (async () => {
      try {
        await Promise.all([
          (document as any).fonts.load("500 100px Tajawal", "اختبار0123"),
          (document as any).fonts.load("700 100px Tajawal", "اختبار0123"),
          (document as any).fonts.load("800 100px Tajawal", "اختبار0123"),
        ]);
        await (document as any).fonts.ready;
      } catch (e) {}
      continueRender(handle);
    })();
  }, [handle]);
  return <link rel="stylesheet" href={staticFile("fonts.css")} />;
};

// ------------------------------------------------------------------ background system
const Constellation: React.FC = () => {
  const pts = [
    [120, 300], [340, 210], [520, 360], [760, 250], [960, 420],
    [180, 560], [430, 640], [900, 700], [240, 980], [820, 1080],
    [560, 1180], [120, 1320], [980, 1360], [420, 1520], [720, 1640],
  ];
  const links = [[0, 1], [1, 2], [2, 3], [3, 4], [0, 5], [5, 6], [6, 2], [4, 7], [7, 9], [8, 10], [10, 6], [11, 8], [9, 12], [10, 13], [13, 14], [9, 14]];
  return (
    <svg width={WIDTH} height={HEIGHT} style={{ position: "absolute", inset: 0, opacity: 0.06 }}>
      {links.map(([a, b], i) => (
        <line key={i} x1={pts[a][0]} y1={pts[a][1]} x2={pts[b][0]} y2={pts[b][1]} stroke={C.teal} strokeWidth={1} />
      ))}
      {pts.map((p, i) => <circle key={i} cx={p[0]} cy={p[1]} r={2.2} fill={C.teal} />)}
    </svg>
  );
};

const Bg: React.FC = () => (
  <>
    <AbsoluteFill style={{ background: `radial-gradient(128% 92% at 50% 30%, ${C.bgTop} 0%, ${C.bg} 48%, ${C.bgFloor} 100%)` }} />
    <Constellation />
    {/* top-center key light pool */}
    <AbsoluteFill style={{ background: "radial-gradient(46% 30% at 50% 20%, rgba(120,200,190,0.10) 0%, rgba(0,0,0,0) 70%)" }} />
    {/* vignette */}
    <AbsoluteFill style={{ boxShadow: "inset 0 0 460px 120px rgba(0,0,0,0.55)", pointerEvents: "none" }} />
    {/* grain */}
    <AbsoluteFill style={{ backgroundImage: NOISE, backgroundSize: "160px 160px", opacity: 0.05, mixBlendMode: "overlay", pointerEvents: "none" }} />
  </>
);

// ------------------------------------------------------------------ gem logo (faceted)
const Gem: React.FC<{ y?: number; size?: number; op?: number }> = ({ y = 1812, size = 46, op = 0.9 }) => (
  <div style={{ position: "absolute", top: y, left: 0, width: WIDTH, display: "flex", justifyContent: "center", alignItems: "center", gap: 14, zIndex: 8, opacity: op }}>
    <svg width={size} height={size} viewBox="0 0 100 100">
      <g fill="none" stroke="rgba(255,255,255,0.9)" strokeWidth={3} strokeLinejoin="round">
        <polygon points="50,6 82,32 68,92 32,92 18,32" fill="rgba(201,209,214,0.12)" />
        <path d="M18,32 L50,44 L82,32 M50,44 L32,92 M50,44 L68,92 M50,6 L50,44" />
      </g>
    </svg>
    <span style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 30, color: "rgba(255,255,255,0.82)", direction: "ltr", letterSpacing: 1 }}>liquidity.state</span>
  </div>
);

// ------------------------------------------------------------------ 3D kit
const Face: React.FC<{ w: number; h: number; bg: string; transform: string }> = ({ w, h, bg, transform }) => (
  <div style={{ position: "absolute", left: "50%", top: "50%", width: w, height: h, marginLeft: -w / 2, marginTop: -h / 2, background: bg, transform, backfaceVisibility: "hidden" }} />
);

// lit cube — key light from top: bright top, graded front, dark sides
const Box: React.FC<{ w: number; h: number; d: number; color: string; rim?: boolean }> = ({ w, h, d, color, rim }) => (
  <div style={{ position: "relative", width: w, height: h, transformStyle: "preserve-3d", filter: rim ? `drop-shadow(0 0 26px ${color})` : undefined }}>
    <Face w={w} h={h} bg={`linear-gradient(180deg, ${shade(color, 20)} 0%, ${color} 55%, ${shade(color, -14)} 100%)`} transform={`translateZ(${d / 2}px)`} />
    <Face w={w} h={h} bg={shade(color, -34)} transform={`translateZ(${-d / 2}px) rotateY(180deg)`} />
    <Face w={d} h={h} bg={`linear-gradient(180deg, ${shade(color, -30)}, ${shade(color, -52)})`} transform={`rotateY(90deg) translateZ(${w / 2}px)`} />
    <Face w={d} h={h} bg={`linear-gradient(180deg, ${shade(color, -30)}, ${shade(color, -52)})`} transform={`rotateY(-90deg) translateZ(${w / 2}px)`} />
    <Face w={w} h={d} bg={shade(color, 40)} transform={`rotateX(90deg) translateZ(${h / 2}px)`} />
    <Face w={w} h={d} bg={shade(color, -58)} transform={`rotateX(-90deg) translateZ(${h / 2}px)`} />
  </div>
);

const BASE_Y = 560;
const At: React.FC<{ x: number; y: number; z?: number; rx?: number; ry?: number; children: React.ReactNode }> = ({ x, y, z = 0, rx = 0, ry = 0, children }) => (
  <div style={{ position: "absolute", left: "50%", top: "50%", transformStyle: "preserve-3d", transform: `translate(-50%,-50%) translate3d(${x}px,${y + BASE_Y}px,${z}px) rotateX(${rx}deg) rotateY(${ry}deg)` }}>{children}</div>
);

const Cam3D: React.FC<{ tilt: [number, number]; orbit: [number, number]; dolly: [number, number]; dur: number; shake?: { px: number; hz: number; dur: number }; children: React.ReactNode }> = ({ tilt, orbit, dolly, dur, shake, children }) => {
  const f = useCurrentFrame();
  const tx = interpolate(f, [0, F(dur)], tilt, { ...clamp, easing: EASE });
  const oy = interpolate(f, [0, F(dur)], orbit, { ...clamp, easing: EASE });
  const dz = interpolate(f, [0, F(dur)], dolly, { ...clamp, easing: EASE });
  let sx = 0, sy = 0;
  if (shake) { const a = f < F(shake.dur) ? 1 : 0; sx = Math.sin(f * shake.hz) * shake.px * a; sy = Math.cos(f * shake.hz * 1.3) * shake.px * a; }
  return (
    <AbsoluteFill style={{ perspective: 1600, perspectiveOrigin: "50% 50%" }}>
      <div style={{ position: "absolute", inset: 0, transformStyle: "preserve-3d", transformOrigin: "50% 50%", transform: `translate(${sx}px,${sy}px) translateZ(${dz}px) rotateX(${tx}deg) rotateY(${oy}deg)` }}>{children}</div>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ arena
const FLOOR_Y = 300;
const CEIL_Y = -250;

const ContactShadow: React.FC<{ x: number; w: number }> = ({ x, w }) => (
  <At x={x} y={FLOOR_Y + 8} z={0} rx={90}>
    <div style={{ width: w * 1.4, height: w * 1.1, transform: "translate(-50%,-50%)", position: "absolute", background: "radial-gradient(50% 50% at 50% 50%, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 70%)" }} />
  </At>
);

const Arena: React.FC<{ dim?: number }> = ({ dim = 1 }) => (
  <div style={{ transformStyle: "preserve-3d", opacity: dim }}>
    {/* faint perspective floor */}
    <At x={0} y={FLOOR_Y} z={-160} rx={90}>
      <div style={{
        width: 2400, height: 2400, transform: "translate(-50%,-50%)", position: "absolute",
        backgroundImage: "linear-gradient(rgba(46,204,154,0.10) 1px, transparent 1px), linear-gradient(90deg, rgba(46,204,154,0.10) 1px, transparent 1px)",
        backgroundSize: "150px 150px",
        maskImage: "radial-gradient(52% 52% at 50% 42%, #000 0%, transparent 76%)",
        WebkitMaskImage: "radial-gradient(52% 52% at 50% 42%, #000 0%, transparent 76%)",
      }} />
    </At>
    {/* glowing red −10% danger plane (thin, crisp) */}
    <At x={0} y={CEIL_Y} z={-90} rx={90}>
      <div style={{ width: 1020, height: 520, transform: "translate(-50%,-50%)", position: "absolute", background: "linear-gradient(180deg, rgba(225,90,90,0) 0%, rgba(225,90,90,0.14) 50%, rgba(225,90,90,0) 100%)" }} />
    </At>
    <At x={0} y={CEIL_Y} z={-90} rx={90}>
      <div style={{ width: 1020, height: 3, transform: "translate(-50%,-50%)", position: "absolute", background: C.red, boxShadow: `0 0 22px ${C.red}, 0 0 44px rgba(225,90,90,0.6)` }} />
    </At>
  </div>
);

const RedTower: React.FC<{ count: number; broken?: boolean; x?: number }> = ({ count, broken, x = -232 }) => {
  const bw = 172, bh = 90, bd = 172, gap = 8;
  return (
    <>
      <ContactShadow x={x} w={bw} />
      <div style={{ transformStyle: "preserve-3d" }}>
        {Array.from({ length: 5 }).map((_, i) => {
          const on = i < count;
          const y = FLOOR_Y - bh / 2 - i * (bh + gap) - (broken && i === 4 ? 78 : 0);
          return (
            <At key={i} x={x} y={y} z={0}>
              <div style={{ opacity: on ? 1 : 0.07, transformStyle: "preserve-3d" }}>
                <Box w={bw} h={bh} d={bd} color={C.red} rim={broken && i === 4} />
                <div style={{ position: "absolute", left: "50%", top: "50%", transform: `translate(-50%,-50%) translateZ(${bd / 2 + 1}px)`, fontFamily: "Tajawal", fontWeight: 800, fontSize: 34, color: "rgba(255,255,255,0.92)", ...TAB }}>2%</div>
              </div>
            </At>
          );
        })}
      </div>
    </>
  );
};

const TealTower: React.FC<{ count: number; x?: number }> = ({ count, x = 232 }) => {
  const bw = 150, bh = 20, bd = 150, gap = 7;
  return (
    <>
      <ContactShadow x={x} w={bw} />
      <div style={{ transformStyle: "preserve-3d" }}>
        {Array.from({ length: 20 }).map((_, i) => {
          const on = i < count;
          const y = FLOOR_Y - bh / 2 - i * (bh + gap);
          return (
            <At key={i} x={x} y={y} z={0}>
              <div style={{ opacity: on ? 1 : 0.06, transformStyle: "preserve-3d" }}>
                <Box w={bw} h={bh} d={bd} color={C.teal} />
              </div>
            </At>
          );
        })}
      </div>
    </>
  );
};

// screen-space tilted glass card
const CardFlat: React.FC<{ top: number; cx?: number; ry?: number; w: number; h: number; accent: string; lit?: boolean; dim?: number; children: React.ReactNode }> = ({ top, cx = 0, ry = 0, w, h, accent, lit, dim = 1, children }) => (
  <div style={{
    position: "absolute", left: "50%", top, width: w, height: h, opacity: dim, zIndex: 4,
    transform: `translateX(calc(-50% + ${cx}px)) perspective(1500px) rotateY(${ry}deg)`,
    borderRadius: 22,
    background: lit ? `linear-gradient(160deg, rgba(225,90,90,0.18), rgba(27,58,69,0.5))` : `linear-gradient(160deg, rgba(27,58,69,0.62), rgba(14,30,36,0.5))`,
    border: `1.5px solid ${lit ? accent : "rgba(159,180,188,0.28)"}`,
    boxShadow: lit ? `0 18px 60px rgba(225,90,90,0.35), inset 0 1px 0 rgba(255,255,255,0.08)` : "0 26px 70px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.06)",
    backdropFilter: "blur(2px)",
    display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center",
    fontFamily: "Tajawal", fontWeight: 800, direction: "rtl", padding: 24,
  }}>{children}</div>
);

// ------------------------------------------------------------------ HUD / chrome (2D)
const Kicker: React.FC = () => (
  <div style={{ position: "absolute", top: 230, left: 0, width: WIDTH, textAlign: "center", zIndex: 7 }}>
    <span style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 22, color: "rgba(159,180,188,0.7)", letterSpacing: 3, direction: "rtl" }}>لغرض تعليمي</span>
  </div>
);

const StatusHud: React.FC<{ fill: number; failed?: boolean }> = ({ fill, failed }) => (
  <div style={{ position: "absolute", top: 288, left: 90, right: 90, height: 74, zIndex: 7,
    borderRadius: 16, background: "linear-gradient(160deg, rgba(27,58,69,0.55), rgba(14,30,36,0.35))",
    border: "1px solid rgba(159,180,188,0.22)", boxShadow: "inset 0 1px 0 rgba(255,255,255,0.06)",
    display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 26px", direction: "rtl" }}>
    <span style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 28, color: failed ? C.red : C.white, ...TAB }}>
      {failed ? "المحفظة سقطت" : "محفظة ممولة"}
    </span>
    <div style={{ display: "flex", alignItems: "center", gap: 14, direction: "ltr" }}>
      <div style={{ width: 250, height: 20, borderRadius: 10, background: "rgba(255,255,255,0.06)", overflow: "hidden", border: "1px solid rgba(159,180,188,0.2)" }}>
        <div style={{ height: "100%", width: `${Math.min(100, fill * 100)}%`, background: failed ? C.red : `linear-gradient(90deg, ${C.teal}, ${C.red})`, boxShadow: `0 0 14px ${failed ? C.red : "rgba(225,90,90,0.5)"}` }} />
      </div>
      <span style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 26, color: C.red, ...TAB }}>−10%</span>
    </div>
  </div>
);

// ------------------------------------------------------------------ typography
type Motion = "wipe" | "rise" | "stamp" | "scale-in";
const Scrim: React.FC = () => (
  <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 760, zIndex: 3, background: "linear-gradient(180deg, rgba(10,12,16,0) 0%, rgba(10,12,16,0.72) 58%, rgba(10,12,16,0.9) 100%)", pointerEvents: "none" }} />
);

const Hero: React.FC<{ text: string; color?: string; size: number; motion: Motion; inAt: number; top?: number }> = ({ text, color = C.white, size, motion, inAt, top = 1180 }) => {
  const frame = useCurrentFrame();
  const t = frame - F(inAt);
  let s: React.CSSProperties = {};
  if (motion === "wipe") s = { clipPath: `inset(0 0 0 ${interpolate(t, [0, 12], [100, 0], clamp)}%)`, opacity: interpolate(t, [0, 4], [0, 1], clamp) };
  else if (motion === "rise") s = { transform: `translateY(${interpolate(t, [0, 10], [26, 0], clamp)}px)`, opacity: interpolate(t, [0, 10], [0, 1], clamp) };
  else if (motion === "stamp") s = { transform: `scale(${interpolate(t, [0, 3, 6], [1.12, 0.985, 1], clamp)})`, opacity: interpolate(t, [0, 2], [0, 1], clamp) };
  else s = { transform: `scale(${interpolate(t, [0, 10], [0.955, 1], clamp)})`, opacity: interpolate(t, [0, 10], [0, 1], clamp) };
  return (
    <div style={{ position: "absolute", left: 80, right: 80, top, textAlign: "center", direction: "rtl", zIndex: 6 }}>
      <div style={{ display: "inline-block", fontFamily: "Tajawal", fontWeight: 800, fontSize: size, lineHeight: 1.16, color, textShadow: "0 8px 40px rgba(0,0,0,0.9)", ...s }}>{text}</div>
    </div>
  );
};

const Subtitle: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ position: "absolute", left: 110, right: 110, top: 1560, textAlign: "center", direction: "rtl", zIndex: 6, opacity: interpolate(frame, [0, 6], [0, 1], clamp) }}>
      <span style={{ fontFamily: "Tajawal", fontWeight: 500, fontSize: 34, color: C.grey, lineHeight: 1.45 }}>{text}</span>
    </div>
  );
};

// ================================================================== reel
export const Reel3D: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: C.bg }}>
    <FontLoader />
    <Bg />
    <Sequence from={F(0)} durationInFrames={F(2.6)}><B1 /></Sequence>
    <Sequence from={F(2.6)} durationInFrames={F(1.6)}><B2 /></Sequence>
    <Sequence from={F(4.2)} durationInFrames={F(0.8)}><B3 /></Sequence>
    <Sequence from={F(5.0)} durationInFrames={F(1.2)}><B4 /></Sequence>
    <Sequence from={F(6.2)} durationInFrames={F(2.4)}><B56 /></Sequence>
    <Sequence from={F(8.6)} durationInFrames={F(2.0)}><B7 /></Sequence>
    <Sequence from={F(10.6)} durationInFrames={F(2.6)}><B8 /></Sequence>
    <Sequence from={F(13.2)} durationInFrames={F(0.7)}><B9 /></Sequence>
    <Sequence from={F(13.9)} durationInFrames={F(2.7)}><B10 /></Sequence>
    <Sequence from={F(16.6)} durationInFrames={F(1.4)}><B11 /></Sequence>
    <Sequence from={F(18.0)} durationInFrames={F(3.0)}><B12 /></Sequence>
  </AbsoluteFill>
);

const TowerScene: React.FC<{ red: number; teal: number; broken?: boolean; cam: any; dim?: number }> = ({ red, teal, broken, cam, dim = 1 }) => (
  <Cam3D {...cam}>
    <Arena dim={dim} />
    <RedTower count={red} broken={broken} />
    <TealTower count={teal} />
  </Cam3D>
);

const B1: React.FC = () => {
  const f = useCurrentFrame();
  const hud = interpolate(f, [0, F(2.6)], [0.36, 0.6], clamp);
  return (
    <AbsoluteFill>
      <TowerScene red={3} teal={11} cam={{ tilt: [-6, -4], orbit: [-3, -1], dolly: [-60, 0], dur: 2.6 }} />
      <Kicker /><StatusHud fill={hud} /><Scrim />
      <Hero text="چم محفظة ممولة دفعت فلوسها… وطحت؟" size={76} motion="wipe" inAt={0.3} top={1150} />
      <Subtitle text="نفس الاستراتيجية — يتغيّر بس حجم المخاطرة" />
      <Gem />
    </AbsoluteFill>
  );
};

const B2: React.FC = () => (
  <AbsoluteFill>
    <Cam3D tilt={[-6, -6]} orbit={[1, 1]} dolly={[0, 0]} dur={1.6}>
      <Arena />
      <TealTower count={20} x={-232} />
      <RedTower count={5} broken x={232} />
    </Cam3D>
    <Kicker /><StatusHud fill={0.6} /><Scrim />
    <Hero text="رابح بحسابك · طايح بالمحفظة" color={C.white} size={66} motion="rise" inAt={0.2} top={1180} />
    <Subtitle text="بحسابك الشخصي رابح… وبالمحفظة الممولة تطيح" />
    <Gem />
  </AbsoluteFill>
);

const B3: React.FC = () => (
  <AbsoluteFill>
    <TowerScene red={5} teal={20} cam={{ tilt: [-6, -6], orbit: [0, 0], dolly: [0, 0], dur: 0.8 }} dim={0.35} />
    <Scrim />
    <Hero text="ليش؟" color={C.white} size={150} motion="stamp" inAt={0.08} top={860} />
    <Gem />
  </AbsoluteFill>
);

const B4: React.FC = () => {
  const f = useCurrentFrame();
  const red = Math.min(3, Math.floor(interpolate(f, [0, F(1.0)], [0, 3], clamp)));
  const teal = Math.min(6, Math.floor(interpolate(f, [0, F(1.0)], [0, 6], clamp)));
  return (
    <AbsoluteFill>
      <TowerScene red={red} teal={teal} cam={{ tilt: [-6, -6], orbit: [0, 5], dolly: [0, -50], dur: 1.2 }} dim={0.85} />
      <Scrim />
      <Hero text="تعال أوريك" color={C.white} size={90} motion="scale-in" inAt={0.1} top={1200} />
      <Gem />
    </AbsoluteFill>
  );
};

const B56: React.FC = () => {
  const f = useCurrentFrame();
  const n = Math.min(4, Math.floor(interpolate(f, [0, F(2.0)], [0, 4], clamp)) + 1);
  const labels = ["EMA", "RSI", "زون طلب", "أسهم دخول"];
  return (
    <AbsoluteFill>
      <Cam3D tilt={[-4, -4]} orbit={[-3, 3]} dolly={[-60, 0]} dur={2.4}><Arena dim={0.5} /></Cam3D>
      {labels.slice(0, n).map((l, i) => (
        <CardFlat key={i} top={370 + i * 82} cx={-150 + i * 92} ry={-15 + i * 9} w={430} h={104} accent="rgba(159,180,188,0.45)" dim={0.9}>
          <span style={{ fontSize: 42, color: i % 2 ? C.teal : C.grey }}>{l}</span>
        </CardFlat>
      ))}
      <Scrim />
      <Hero text="استراتيجية أقوى؟" color={C.white} size={78} motion="wipe" inAt={0.3} top={1190} />
      <Subtitle text="الكل يقول لازم نموذج دخول أدق — والإكويتي ما تتحرك" />
      <Gem />
    </AbsoluteFill>
  );
};

const B7: React.FC = () => {
  const f = useCurrentFrame();
  const p = interpolate(f, [0, F(1.2)], [0, 1], clamp);
  return (
    <AbsoluteFill>
      <Cam3D tilt={[-4, -4]} orbit={[0, 0]} dolly={[0, 0]} dur={2.0}><Arena dim={0.3} /></Cam3D>
      <CardFlat top={470} ry={11} w={780} h={150} accent="rgba(46,204,154,0.5)" dim={interpolate(p, [0, 1], [1, 0.4], clamp)}>
        <span style={{ fontSize: 46, color: C.grey }}>الهدف 5% — بدون سقف زمني</span>
      </CardFlat>
      <CardFlat top={690} ry={-9} w={840} h={178} accent={C.red} lit>
        <span style={{ fontSize: 52, color: C.white }}>حد الخسارة 10% — <span style={{ color: C.red }}>نهائي</span></span>
      </CardFlat>
      <Scrim />
      <Hero text="مو اختبار ربح — اختبار خسارة" color={C.red} size={82} motion="wipe" inAt={0.3} top={1210} />
      <Subtitle text="المحفظة الممولة تختبر قدرتك إنك ما تخسر — مو إنك تربح" />
      <Gem />
    </AbsoluteFill>
  );
};

const B8: React.FC = () => {
  const f = useCurrentFrame();
  const red = Math.min(5, Math.floor(interpolate(f, [F(0.1), F(1.2)], [0, 5], clamp)));
  const teal = Math.min(20, Math.floor(interpolate(f, [F(1.1), F(2.5)], [0, 20], clamp)));
  return (
    <AbsoluteFill>
      <TowerScene red={red} teal={teal} broken={red >= 5} cam={{ tilt: [-6, -4], orbit: [-5, 4], dolly: [-40, 20], dur: 2.6 }} />
      <StatusHud fill={red >= 5 ? 1 : 0.6 + red * 0.08} /><Scrim />
      <Hero text="5 خسائر تكفي — ولا 20؟" color={C.white} size={84} motion="scale-in" inAt={0.3} top={1180} />
      <Subtitle text="بمخاطرة 2% خمس خسائر توقفك · بـ 0.5% تحتاج 20 خسارة" />
      <Gem />
    </AbsoluteFill>
  );
};

const B9: React.FC = () => (
  <AbsoluteFill>
    <TowerScene red={5} teal={20} broken cam={{ tilt: [-6, -4], orbit: [-5, -5], dolly: [30, 0], dur: 0.7, shake: { px: 6, hz: 3, dur: 0.5 } }} />
    <AbsoluteFill style={{ background: "radial-gradient(60% 50% at 50% 42%, rgba(225,90,90,0.22), rgba(225,90,90,0) 70%)", zIndex: 2 }} />
    <StatusHud fill={1} failed /><Scrim />
    <Hero text="تدفع فلوسها… وتطيح" color={C.white} size={98} motion="stamp" inAt={0.02} top={1180} />
    <Gem />
  </AbsoluteFill>
);

const B10: React.FC = () => {
  const f = useCurrentFrame();
  const r1 = interpolate(f, [0, F(0.9)], [0, 1], clamp);
  const r2 = interpolate(f, [F(1.0), F(1.9)], [0, 1], clamp);
  const eq = (a: string, b: string, ac: string) => (
    <span style={{ fontSize: 76, direction: "ltr", display: "inline-block", ...TAB }}>
      <span style={{ color: ac }}>{a}</span> <span style={{ color: C.grey, opacity: 0.75 }}>{b}</span> <span style={{ color: C.white }}>= 10%</span>
    </span>
  );
  return (
    <AbsoluteFill>
      <Cam3D tilt={[-4, -4]} orbit={[4, -1]} dolly={[20, -40]} dur={2.7}><Arena dim={0.32} /></Cam3D>
      <div style={{ position: "absolute", top: 430, left: 0, width: WIDTH, textAlign: "center", zIndex: 5, fontFamily: "Tajawal", fontWeight: 800, fontSize: 40, color: C.grey, direction: "rtl" }}>نفس الوصول للحد — بمسارين</div>
      <CardFlat top={560} ry={9} w={800} h={158} accent={C.red} dim={r1}>{eq("2%", "× 5", C.red)}</CardFlat>
      <CardFlat top={772} ry={-9} w={800} h={158} accent={C.teal} dim={r2}>{eq("0.5%", "× 20", C.teal)}</CardFlat>
      <Scrim />
      <Subtitle text="شوف الأرقام — نفس الـ 10%، بس عدد الخسائر يفرق" />
      <Gem />
    </AbsoluteFill>
  );
};

const B11: React.FC = () => (
  <AbsoluteFill>
    <Cam3D tilt={[-6, -6]} orbit={[0, -5]} dolly={[0, 0]} dur={1.4}>
      <Arena dim={0.5} />
      <TealTower count={20} x={0} />
    </Cam3D>
    <Scrim />
    <Hero text="مخاطرتك اهي اللي تعدّيك — مو نموذجك" color={C.teal} size={78} motion="wipe" inAt={0.3} top={1180} />
    <Gem />
  </AbsoluteFill>
);

const B12: React.FC = () => {
  const f = useCurrentFrame();
  const red = Math.floor(interpolate(f, [F(1.0), F(3.0)], [1, 3], clamp));
  const teal = Math.floor(interpolate(f, [F(1.0), F(3.0)], [4, 11], clamp));
  return (
    <AbsoluteFill>
      <TowerScene red={red} teal={teal} cam={{ tilt: [-6, -4], orbit: [-3, -1], dolly: [-60, 0], dur: 2.6 }} />
      <Kicker /><StatusHud fill={0.45} /><Scrim />
      <Hero text="اكتب «ممول» بالتعليقات" color={C.white} size={82} motion="rise" inAt={0.3} top={1170} />
      <Subtitle text="وچم صفقة باليوم؟ وچم خسارة توقفك؟ — يوصلك الملف كامل" />
      <Gem />
    </AbsoluteFill>
  );
};
