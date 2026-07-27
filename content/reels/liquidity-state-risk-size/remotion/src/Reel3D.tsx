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

const C = {
  bg: "#0E1E24",
  bg2: "#070B0E",
  teal: "#2E9E8F",
  silver: "#C9D1D6",
  gold: "#D6A94A",
  text: "#F2F5F7",
  red: "#E15A5A",
};
const clamp = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
const F = (s: number) => Math.round(s * FPS);
const EASE = Easing.bezier(0.16, 1, 0.3, 1);

const shade = (hex: string, pct: number) => {
  const n = parseInt(hex.slice(1), 16);
  const r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
  const f = pct / 100;
  const adj = (c: number) => Math.max(0, Math.min(255, Math.round(c + (pct > 0 ? 255 - c : c) * f)));
  return `rgb(${adj(r)},${adj(g)},${adj(b)})`;
};

// ---------------------------------------------------------------- fonts
const FontLoader: React.FC = () => {
  const [handle] = useState(() => delayRender("load-fonts"));
  useEffect(() => {
    const run = async () => {
      try {
        await Promise.all([
          (document as any).fonts.load("400 100px Tajawal", "اختبار0123"),
          (document as any).fonts.load("700 100px Tajawal", "اختبار0123"),
          (document as any).fonts.load("800 100px Tajawal", "اختبار0123"),
        ]);
        await (document as any).fonts.ready;
      } catch (e) {}
      continueRender(handle);
    };
    run();
  }, [handle]);
  return <link rel="stylesheet" href={staticFile("fonts.css")} />;
};

// ---------------------------------------------------------------- 3D kit
const Face: React.FC<{ w: number; h: number; bg: string; transform: string; glow?: string }> = ({
  w, h, bg, transform, glow,
}) => (
  <div style={{
    position: "absolute", left: "50%", top: "50%", width: w, height: h,
    marginLeft: -w / 2, marginTop: -h / 2, background: bg, transform,
    backfaceVisibility: "hidden", boxShadow: glow ? `0 0 40px ${glow}` : undefined,
    border: "1px solid rgba(0,0,0,0.22)",
  }} />
);

const Box: React.FC<{ w: number; h: number; d: number; color: string; glow?: string; radius?: number }> = ({
  w, h, d, color, glow,
}) => (
  <div style={{ position: "relative", width: w, height: h, transformStyle: "preserve-3d" }}>
    <Face w={w} h={h} bg={color} transform={`translateZ(${d / 2}px)`} glow={glow} />
    <Face w={w} h={h} bg={shade(color, -32)} transform={`translateZ(${-d / 2}px) rotateY(180deg)`} />
    <Face w={d} h={h} bg={shade(color, -46)} transform={`rotateY(90deg) translateZ(${w / 2}px)`} />
    <Face w={d} h={h} bg={shade(color, -46)} transform={`rotateY(-90deg) translateZ(${w / 2}px)`} />
    <Face w={w} h={d} bg={shade(color, 26)} transform={`rotateX(90deg) translateZ(${h / 2}px)`} />
    <Face w={w} h={d} bg={shade(color, -60)} transform={`rotateX(-90deg) translateZ(${h / 2}px)`} />
  </div>
);

const BASE_Y = 560; // global vertical offset to centre the 3D world in-frame
const At: React.FC<{ x: number; y: number; z?: number; rx?: number; ry?: number; rz?: number; children: React.ReactNode }> = ({
  x, y, z = 0, rx = 0, ry = 0, rz = 0, children,
}) => (
  <div style={{
    position: "absolute", left: "50%", top: "50%", transformStyle: "preserve-3d",
    transform: `translate(-50%,-50%) translate3d(${x}px,${y + BASE_Y}px,${z}px) rotateX(${rx}deg) rotateY(${ry}deg) rotateZ(${rz}deg)`,
  }}>{children}</div>
);

// perspective camera rig
const Cam3D: React.FC<{
  tilt: [number, number]; orbit: [number, number]; dolly: [number, number]; dur: number;
  shake?: { px: number; hz: number; dur: number }; children: React.ReactNode;
}> = ({ tilt, orbit, dolly, dur, shake, children }) => {
  const f = useCurrentFrame();
  const tx = interpolate(f, [0, F(dur)], tilt, { ...clamp, easing: EASE });
  const oy = interpolate(f, [0, F(dur)], orbit, { ...clamp, easing: EASE });
  const dz = interpolate(f, [0, F(dur)], dolly, { ...clamp, easing: EASE });
  let sx = 0, sy = 0;
  if (shake) {
    const a = f < F(shake.dur) ? 1 : 0;
    sx = Math.sin(f * shake.hz) * shake.px * a;
    sy = Math.cos(f * shake.hz * 1.3) * shake.px * a;
  }
  return (
    <AbsoluteFill style={{ perspective: 1600, perspectiveOrigin: "50% 50%" }}>
      <div style={{
        position: "absolute", inset: 0, transformStyle: "preserve-3d", transformOrigin: "50% 50%",
        transform: `translate(${sx}px,${sy}px) translateZ(${dz}px) rotateX(${tx}deg) rotateY(${oy}deg)`,
      }}>{children}</div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- arena (floor + red ceiling)
const FLOOR_Y = 300;
const CEIL_Y = -230;

const Arena: React.FC<{ dim?: number; ceilFlash?: number }> = ({ dim = 1, ceilFlash = 0.55 }) => (
  <div style={{ transformStyle: "preserve-3d", opacity: dim }}>
    {/* floor grid */}
    <At x={0} y={FLOOR_Y} z={-200} rx={90}>
      <div style={{
        width: 2200, height: 2400, transform: "translate(-50%,-50%)", position: "absolute",
        backgroundImage:
          "linear-gradient(rgba(46,158,143,0.16) 2px, transparent 2px), linear-gradient(90deg, rgba(46,158,143,0.16) 2px, transparent 2px)",
        backgroundSize: "120px 120px",
        maskImage: "radial-gradient(60% 60% at 50% 50%, #000 0%, transparent 78%)",
        WebkitMaskImage: "radial-gradient(60% 60% at 50% 50%, #000 0%, transparent 78%)",
      }} />
    </At>
    {/* red -10% ceiling plane */}
    <At x={0} y={CEIL_Y} z={-120} rx={90}>
      <div style={{
        width: 980, height: 620, transform: "translate(-50%,-50%)", position: "absolute",
        background: `rgba(225,90,90,${0.10 + ceilFlash * 0.14})`,
        border: `2px solid rgba(225,90,90,${0.5 + ceilFlash * 0.5})`,
        boxShadow: `0 0 ${40 + ceilFlash * 60}px rgba(225,90,90,${0.4 + ceilFlash * 0.4})`,
      }} />
    </At>
    {/* -10% label riding the ceiling edge */}
    <At x={330} y={CEIL_Y - 60} z={130} ry={-16}>
      <div style={{
        fontFamily: "Tajawal", fontWeight: 800, fontSize: 40, color: C.red,
        direction: "rtl", whiteSpace: "nowrap", textShadow: "0 4px 20px rgba(0,0,0,0.7)",
      }}>−10% حد السحب</div>
    </At>
  </div>
);

// red tower (5 x 2%) — breaks the ceiling when full
const RedTower: React.FC<{ count: number; broken?: boolean; x?: number }> = ({ count, broken, x = -235 }) => {
  const bw = 170, bh = 92, bd = 170, gap = 6;
  return (
    <div style={{ transformStyle: "preserve-3d" }}>
      {Array.from({ length: 5 }).map((_, i) => {
        const on = i < count;
        const y = FLOOR_Y - bh / 2 - i * (bh + gap) - (broken && i === 4 ? 70 : 0);
        return (
          <At key={i} x={x} y={y} z={0}>
            <div style={{ opacity: on ? 1 : 0.08, transformStyle: "preserve-3d" }}>
              <Box w={bw} h={bh} d={bd} color={C.red} glow={broken ? C.red : undefined} />
              <div style={{
                position: "absolute", left: "50%", top: "50%", transform: `translate(-50%,-50%) translateZ(${bd / 2 + 1}px)`,
                fontFamily: "Tajawal", fontWeight: 800, fontSize: 38, color: "#2a0d0d",
              }}>2%</div>
            </div>
          </At>
        );
      })}
    </div>
  );
};

// teal tower (20 x 0.5%) — stays under the ceiling
const TealTower: React.FC<{ count: number; x?: number }> = ({ count, x = 235 }) => {
  const bw = 150, bh = 15, bd = 150, gap = 5;
  return (
    <div style={{ transformStyle: "preserve-3d" }}>
      {Array.from({ length: 20 }).map((_, i) => {
        const on = i < count;
        const y = FLOOR_Y - bh / 2 - i * (bh + gap);
        return (
          <At key={i} x={x} y={y} z={0}>
            <div style={{ opacity: on ? 1 : 0.07, transformStyle: "preserve-3d" }}>
              <Box w={bw} h={bh} d={bd} color={C.teal} />
            </div>
          </At>
        );
      })}
      <At x={x} y={FLOOR_Y + 70} z={90}>
        <div style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 36, color: C.teal }}>0.5%</div>
      </At>
    </div>
  );
};

// screen-positioned tilted 3D card (reliable placement, own perspective)
const CardFlat: React.FC<{ top: number; cx?: number; ry?: number; w: number; h: number; color: string; lit?: boolean; dim?: number; children: React.ReactNode }> = ({
  top, cx = 0, ry = 0, w, h, color, lit, dim = 1, children,
}) => (
  <div style={{
    position: "absolute", left: "50%", top, width: w, height: h, opacity: dim, zIndex: 3,
    transform: `translateX(calc(-50% + ${cx}px)) perspective(1400px) rotateY(${ry}deg)`,
    borderRadius: 20, transformStyle: "preserve-3d",
    background: lit ? "rgba(225,90,90,0.16)" : "rgba(46,158,143,0.10)",
    border: `2px solid ${color}`,
    boxShadow: lit ? "0 18px 60px rgba(225,90,90,0.45)" : "0 26px 70px rgba(0,0,0,0.55)",
    display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center",
    fontFamily: "Tajawal", fontWeight: 800, direction: "rtl", padding: 24,
  }}>{children}</div>
);

// ---------------------------------------------------------------- flat overlays (crisp 2D)
type Motion = "wipe" | "rise" | "stamp" | "scale-in";
const BigText: React.FC<{ text: string; color: string; size: number; motion: Motion; inAt: number; center?: boolean }> = ({
  text, color, size, motion, inAt, center,
}) => {
  const frame = useCurrentFrame();
  const t = frame - F(inAt);
  let s: React.CSSProperties = {};
  if (motion === "wipe") s = { clipPath: `inset(0 0 0 ${interpolate(t, [0, 12], [100, 0], clamp)}%)`, opacity: interpolate(t, [0, 4], [0, 1], clamp) };
  else if (motion === "rise") s = { transform: `translateY(${interpolate(t, [0, 9], [22, 0], clamp)}px)`, opacity: interpolate(t, [0, 9], [0, 1], clamp) };
  else if (motion === "stamp") s = { transform: `scale(${interpolate(t, [0, 3, 6], [1.14, 0.98, 1], clamp)})`, opacity: interpolate(t, [0, 2], [0, 1], clamp) };
  else s = { transform: `scale(${interpolate(t, [0, 9], [0.96, 1], clamp)})`, opacity: interpolate(t, [0, 9], [0, 1], clamp) };
  return (
    <div style={{ position: "absolute", left: 70, right: 70, top: center ? 820 : 1210, textAlign: "center", direction: "rtl", zIndex: 5 }}>
      <div style={{ display: "inline-block", fontFamily: "Tajawal", fontWeight: 800, fontSize: size, lineHeight: 1.15, color, textShadow: "0 6px 34px rgba(0,0,0,0.85)", ...s }}>{text}</div>
    </div>
  );
};

const Caption: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  return (
    <div style={{ position: "absolute", left: 80, right: 80, top: 1520, textAlign: "center", direction: "rtl", opacity: interpolate(frame, [0, 6], [0, 1], clamp), zIndex: 5 }}>
      <span style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 40, color: C.text, lineHeight: 1.4, background: "rgba(7,11,14,0.6)", padding: "8px 20px", borderRadius: 12, WebkitBoxDecorationBreak: "clone", boxDecorationBreak: "clone", textShadow: "0 2px 8px rgba(0,0,0,0.9)" }}>{text}</span>
    </div>
  );
};

const Hud: React.FC<{ fill: number; failed?: boolean }> = ({ fill, failed }) => (
  <div style={{ position: "absolute", top: 300, left: 0, width: WIDTH, display: "flex", justifyContent: "center", gap: 16, alignItems: "center", zIndex: 5 }}>
    <div style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 26, color: failed ? C.red : C.silver }}>{failed ? "FAILED" : "Account Drawdown"}</div>
    <div style={{ width: 300, height: 26, borderRadius: 8, background: "rgba(255,255,255,0.06)", border: "1px solid rgba(201,209,214,0.2)", overflow: "hidden" }}>
      <div style={{ height: "100%", width: `${Math.min(100, fill * 100)}%`, background: failed ? C.red : `linear-gradient(90deg, ${C.gold}, ${C.red})` }} />
    </div>
  </div>
);

const EduTag: React.FC = () => (
  <div style={{ position: "absolute", top: 232, left: 0, width: WIDTH, textAlign: "center", fontFamily: "Tajawal", fontWeight: 500, fontSize: 24, color: "rgba(201,209,214,0.55)", direction: "rtl", letterSpacing: 1, zIndex: 6 }}>
    لغرض تعليمي · المحفظة الممولة على حد سحب 10% ثابت
  </div>
);

// ---------------------------------------------------------------- reel
export const Reel3D: React.FC = () => (
  <AbsoluteFill style={{ background: `radial-gradient(130% 100% at 50% 34%, #123039 0%, ${C.bg} 46%, ${C.bg2} 100%)` }}>
    <FontLoader />
    <EduTag />

    {/* B1 HOOK 0-2.6 */}
    <Sequence from={F(0)} durationInFrames={F(2.6)}><B1 /></Sequence>
    {/* B2 PARADOX 2.6-4.2 */}
    <Sequence from={F(2.6)} durationInFrames={F(1.6)}><B2 /></Sequence>
    {/* B3 PIVOT 4.2-5.0 */}
    <Sequence from={F(4.2)} durationInFrames={F(0.8)}><B3 /></Sequence>
    {/* B4 INVITE 5.0-6.2 */}
    <Sequence from={F(5.0)} durationInFrames={F(1.2)}><B4 /></Sequence>
    {/* B5+6 6.2-8.6 */}
    <Sequence from={F(6.2)} durationInFrames={F(2.4)}><B56 /></Sequence>
    {/* B7 TURN 8.6-10.6 */}
    <Sequence from={F(8.6)} durationInFrames={F(2.0)}><B7 /></Sequence>
    {/* B8 TURN(number) 10.6-13.2 */}
    <Sequence from={F(10.6)} durationInFrames={F(2.6)}><B8 /></Sequence>
    {/* B9 VERDICT 13.2-13.9 */}
    <Sequence from={F(13.2)} durationInFrames={F(0.7)}><B9 /></Sequence>
    {/* B10 PROOF 13.9-16.6 */}
    <Sequence from={F(13.9)} durationInFrames={F(2.7)}><B10 /></Sequence>
    {/* B11 CARE 16.6-18.0 */}
    <Sequence from={F(16.6)} durationInFrames={F(1.4)}><B11 /></Sequence>
    {/* B12 LOOP 18.0-21.0 */}
    <Sequence from={F(18.0)} durationInFrames={F(3.0)}><B12 /></Sequence>
  </AbsoluteFill>
);

const B1: React.FC = () => {
  const f = useCurrentFrame();
  const hud = interpolate(f, [0, F(2.6)], [0.36, 0.6], clamp);
  return (
    <AbsoluteFill>
      <Cam3D tilt={[-6, -4]} orbit={[-3, -1]} dolly={[-60, 0]} dur={2.6}>
        <Arena />
        <RedTower count={3} />
        <TealTower count={11} />
      </Cam3D>
      <Hud fill={hud} />
      <BigText text="چم محفظة ممولة دفعت فلوسها… وطحت؟" color={C.text} size={72} motion="wipe" inAt={0.3} />
      <Caption text="چم محفظة ممولة دفعت فلوسها … وطحت؟" />
    </AbsoluteFill>
  );
};

const B2: React.FC = () => (
  <AbsoluteFill>
    <Cam3D tilt={[-5, -5]} orbit={[1, 1]} dolly={[0, 0]} dur={1.6}>
      <Arena />
      {/* left safe teal, right broken red */}
      <TealTower count={20} x={-235} />
      <RedTower count={5} broken x={235} />
    </Cam3D>
    <Hud fill={0.6} />
    <BigText text="رابح بحسابك · طايح بالمحفظة" color={C.silver} size={64} motion="rise" inAt={0.2} />
    <Caption text="بحسابك الشخصي رابح… وبالمحفظة الممولة تطيح" />
  </AbsoluteFill>
);

const B3: React.FC = () => (
  <AbsoluteFill>
    <Cam3D tilt={[-5, -5]} orbit={[0, 0]} dolly={[0, 0]} dur={0.8}>
      <Arena dim={0.4} ceilFlash={1} />
    </Cam3D>
    <BigText text="شلون؟" color={C.gold} size={140} motion="stamp" inAt={0.08} center />
  </AbsoluteFill>
);

const B4: React.FC = () => {
  const f = useCurrentFrame();
  const red = Math.min(3, Math.floor(interpolate(f, [0, F(1.0)], [0, 3], clamp)));
  const teal = Math.min(6, Math.floor(interpolate(f, [0, F(1.0)], [0, 6], clamp)));
  return (
    <AbsoluteFill>
      <Cam3D tilt={[-5, -5]} orbit={[0, 5]} dolly={[0, -50]} dur={1.2}>
        <Arena dim={0.7} />
        <RedTower count={red} />
        <TealTower count={teal} />
      </Cam3D>
      <Caption text="تعال اقولك" />
    </AbsoluteFill>
  );
};

const B56: React.FC = () => {
  const f = useCurrentFrame();
  const n = Math.min(4, Math.floor(interpolate(f, [0, F(2.0)], [0, 4], clamp)) + 1);
  const labels = ["EMA", "RSI", "زون طلب", "أسهم دخول"];
  return (
    <AbsoluteFill>
      <Cam3D tilt={[-4, -4]} orbit={[-3, 3]} dolly={[-60, 0]} dur={2.4}>
        <Arena dim={0.5} />
      </Cam3D>
      {labels.slice(0, n).map((l, i) => (
        <CardFlat key={i} top={380 + i * 78} cx={-150 + i * 90} ry={-16 + i * 9} w={430} h={104} color="rgba(201,209,214,0.45)" dim={0.9}>
          <span style={{ fontSize: 42, color: i % 2 ? C.gold : C.silver }}>{l}</span>
        </CardFlat>
      ))}
      <BigText text="استراتيجية أقوى؟" color={C.silver} size={76} motion="wipe" inAt={0.3} />
      <Caption text="الكل يقول لازم استراتيجية أقوى… ويدور نموذج دخول يضبط بالباك تست" />
    </AbsoluteFill>
  );
};

const B7: React.FC = () => {
  const f = useCurrentFrame();
  const p = interpolate(f, [0, F(1.2)], [0, 1], clamp);
  return (
    <AbsoluteFill>
      <Cam3D tilt={[-4, -4]} orbit={[0, 0]} dolly={[0, 0]} dur={2.0}>
        <Arena dim={0.3} />
      </Cam3D>
      <CardFlat top={470} ry={12} w={760} h={150} color="rgba(46,158,143,0.45)" dim={interpolate(p, [0, 1], [1, 0.4], clamp)}>
        <span style={{ fontSize: 46, color: C.silver }}>الهدف 5% — بدون سقف زمني</span>
      </CardFlat>
      <CardFlat top={690} ry={-10} w={820} h={175} color={C.red} lit>
        <span style={{ fontSize: 52, color: C.text }}>حد الخسارة 10% — <span style={{ color: C.gold }}>نهائي</span></span>
      </CardFlat>
      <BigText text="مو اختبار ربح — اختبار خسارة" color={C.red} size={80} motion="wipe" inAt={0.3} />
      <Caption text="لكن بالواقع؟ المحفظة الممولة مو اختبار ربح… اهي اختبار خسارة" />
    </AbsoluteFill>
  );
};

const B8: React.FC = () => {
  const f = useCurrentFrame();
  const red = Math.min(5, Math.floor(interpolate(f, [F(0.1), F(1.2)], [0, 5], clamp)));
  const teal = Math.min(20, Math.floor(interpolate(f, [F(1.1), F(2.5)], [0, 20], clamp)));
  const flash = red >= 5 ? interpolate(Math.sin(f * 0.9), [-1, 1], [0.5, 1]) : 0.5;
  return (
    <AbsoluteFill>
      <Cam3D tilt={[-6, -4]} orbit={[-5, 4]} dolly={[-40, 20]} dur={2.6}>
        <Arena ceilFlash={flash} />
        <RedTower count={red} broken={red >= 5} />
        <TealTower count={teal} />
      </Cam3D>
      <BigText text="5 خسائر ← ولا 20؟" color={C.gold} size={96} motion="scale-in" inAt={0.3} />
      <Caption text="بمخاطرة 2%… خمس خسائر تبخّر المحفظة. بمخاطرة 0.5% تحتاج 20 خسارة" />
    </AbsoluteFill>
  );
};

const B9: React.FC = () => (
  <AbsoluteFill>
    <Cam3D tilt={[-6, -4]} orbit={[-5, -5]} dolly={[30, 0]} dur={0.7} shake={{ px: 6, hz: 3, dur: 0.5 }}>
      <Arena ceilFlash={1} />
      <RedTower count={5} broken />
      <TealTower count={20} />
    </Cam3D>
    <AbsoluteFill style={{ background: "rgba(225,90,90,0.12)", zIndex: 2 }} />
    <div style={{ position: "absolute", top: 250, left: 0, width: WIDTH, textAlign: "center", zIndex: 5 }}>
      <span style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 46, color: C.red, letterSpacing: 6, background: "rgba(20,6,6,0.6)", padding: "8px 28px", borderRadius: 10, border: `2px solid ${C.red}` }}>FAILED</span>
    </div>
    <BigText text="تدفع فلوسها… وتطيح" color={C.text} size={96} motion="stamp" inAt={0.02} />
  </AbsoluteFill>
);

const B10: React.FC = () => {
  const f = useCurrentFrame();
  const r1 = interpolate(f, [0, F(0.9)], [0, 1], clamp);
  const r2 = interpolate(f, [F(1.0), F(1.9)], [0, 1], clamp);
  return (
    <AbsoluteFill>
      <Cam3D tilt={[-4, -4]} orbit={[4, -1]} dolly={[20, -40]} dur={2.7}>
        <Arena dim={0.35} />
      </Cam3D>
      <CardFlat top={560} ry={9} w={780} h={155} color={C.red} dim={r1}>
        <span style={{ fontSize: 74, direction: "ltr", display: "inline-block" }}>
          <span style={{ color: C.red }}>2%</span> <span style={{ color: C.silver, opacity: 0.7 }}>× 5</span> <span style={{ color: C.gold }}>= 10%</span>
        </span>
      </CardFlat>
      <CardFlat top={770} ry={-9} w={780} h={155} color={C.teal} dim={r2}>
        <span style={{ fontSize: 74, direction: "ltr", display: "inline-block" }}>
          <span style={{ color: C.teal }}>0.5%</span> <span style={{ color: C.silver, opacity: 0.7 }}>× 20</span> <span style={{ color: C.gold }}>= 10%</span>
        </span>
      </CardFlat>
      <Caption text="شوف الأرقام" />
    </AbsoluteFill>
  );
};

const B11: React.FC = () => (
  <AbsoluteFill>
    <Cam3D tilt={[-5, -5]} orbit={[0, -4]} dolly={[0, 0]} dur={1.4}>
      <Arena dim={0.55} />
      <TealTower count={20} x={0} />
    </Cam3D>
    <BigText text="مخاطرتك اهي اللي تعدّيك — مو نموذجك" color={C.teal} size={78} motion="wipe" inAt={0.3} />
  </AbsoluteFill>
);

const B12: React.FC = () => {
  const f = useCurrentFrame();
  const red = interpolate(f, [F(1.0), F(3.0)], [1, 3], clamp);
  const teal = interpolate(f, [F(1.0), F(3.0)], [4, 11], clamp);
  const hud = 0.45;
  return (
    <AbsoluteFill>
      <Cam3D tilt={[-6, -4]} orbit={[-3, -1]} dolly={[-60, 0]} dur={2.6}>
        <Arena />
        <RedTower count={Math.floor(red)} />
        <TealTower count={Math.floor(teal)} />
      </Cam3D>
      <Hud fill={hud} />
      <div style={{ position: "absolute", top: 1360, left: 0, width: WIDTH, textAlign: "center", fontFamily: "Tajawal", fontWeight: 800, fontSize: 44, color: C.silver, direction: "ltr", zIndex: 5 }}>@liquidity.state</div>
      <BigText text="اكتب «ممول» بالتعليقات" color={C.gold} size={80} motion="rise" inAt={0.3} />
      <Caption text="بس چم صفقة باليوم… وچم خسارة توقفك؟ اكتب «ممول» ويوصلك الملف" />
    </AbsoluteFill>
  );
};
