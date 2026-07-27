import React, { useEffect, useState } from "react";
import {
  AbsoluteFill, Sequence, interpolate, useCurrentFrame, Easing,
  staticFile, delayRender, continueRender,
} from "remotion";

export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const RUNTIME_S = 21.0;

const C = {
  bgTop: "#123039", bg: "#0E1E24", bgFloor: "#0A0C10",
  card: "#1B3A45", white: "#FFFFFF", grey: "#9FB4BC",
  teal: "#2ECC9A", red: "#E15A5A",
};
const clamp = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
const F = (s: number) => Math.round(s * FPS);
const TAB: React.CSSProperties = { fontVariantNumeric: "tabular-nums", fontFeatureSettings: '"tnum" 1' };
const shade = (hex: string, pct: number) => {
  const n = parseInt(hex.slice(1), 16); const r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255; const f = pct / 100;
  const a = (c: number) => Math.max(0, Math.min(255, Math.round(c + (pct > 0 ? 255 - c : c) * f)));
  return `rgb(${a(r)},${a(g)},${a(b)})`;
};
const NOISE = "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")";

const FontLoader: React.FC = () => {
  const [handle] = useState(() => delayRender("fonts"));
  useEffect(() => { (async () => {
    try { await Promise.all([
      (document as any).fonts.load("500 100px Tajawal", "اختبار0123"),
      (document as any).fonts.load("700 100px Tajawal", "اختبار0123"),
      (document as any).fonts.load("800 100px Tajawal", "اختبار0123"),
    ]); await (document as any).fonts.ready; } catch (e) {}
    continueRender(handle);
  })(); }, [handle]);
  return <link rel="stylesheet" href={staticFile("fonts.css")} />;
};

const Constellation: React.FC = () => {
  const pts = [[120,300],[340,210],[520,360],[760,250],[960,420],[180,560],[430,640],[900,700],[240,980],[820,1080],[560,1180],[120,1320],[980,1360],[420,1520],[720,1640]];
  const links = [[0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,2],[4,7],[7,9],[8,10],[10,6],[11,8],[9,12],[10,13],[13,14],[9,14]];
  return (
    <svg width={WIDTH} height={HEIGHT} style={{ position: "absolute", inset: 0, opacity: 0.06 }}>
      {links.map(([a, b], i) => <line key={i} x1={pts[a][0]} y1={pts[a][1]} x2={pts[b][0]} y2={pts[b][1]} stroke={C.teal} strokeWidth={1} />)}
      {pts.map((p, i) => <circle key={i} cx={p[0]} cy={p[1]} r={2.2} fill={C.teal} />)}
    </svg>
  );
};
const Bg: React.FC = () => (
  <>
    <AbsoluteFill style={{ background: `radial-gradient(128% 92% at 50% 30%, ${C.bgTop} 0%, ${C.bg} 48%, ${C.bgFloor} 100%)` }} />
    <Constellation />
    <AbsoluteFill style={{ background: "radial-gradient(46% 30% at 50% 22%, rgba(120,200,190,0.10) 0%, rgba(0,0,0,0) 70%)" }} />
    <AbsoluteFill style={{ boxShadow: "inset 0 0 460px 120px rgba(0,0,0,0.55)", pointerEvents: "none" }} />
    <AbsoluteFill style={{ backgroundImage: NOISE, backgroundSize: "160px 160px", opacity: 0.05, mixBlendMode: "overlay", pointerEvents: "none" }} />
  </>
);
const Gem: React.FC = () => (
  <div style={{ position: "absolute", top: 1812, left: 0, width: WIDTH, display: "flex", justifyContent: "center", alignItems: "center", gap: 14, zIndex: 8, opacity: 0.9 }}>
    <svg width={46} height={46} viewBox="0 0 100 100"><g fill="none" stroke="rgba(255,255,255,0.9)" strokeWidth={3} strokeLinejoin="round">
      <polygon points="50,6 82,32 68,92 32,92 18,32" fill="rgba(201,209,214,0.12)" /><path d="M18,32 L50,44 L82,32 M50,44 L32,92 M50,44 L68,92 M50,6 L50,44" /></g></svg>
    <span style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 30, color: "rgba(255,255,255,0.82)", direction: "ltr", letterSpacing: 1 }}>liquidity.state</span>
  </div>
);
const Kicker: React.FC = () => (
  <div style={{ position: "absolute", top: 230, left: 0, width: WIDTH, textAlign: "center", zIndex: 7 }}>
    <span style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 22, color: "rgba(159,180,188,0.7)", letterSpacing: 3, direction: "rtl" }}>لغرض تعليمي</span>
  </div>
);
const Scrim: React.FC = () => (
  <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 720, zIndex: 3, background: "linear-gradient(180deg, rgba(10,12,16,0) 0%, rgba(10,12,16,0.72) 58%, rgba(10,12,16,0.9) 100%)", pointerEvents: "none" }} />
);
const Hero: React.FC<{ text: string; color?: string; size: number; top?: number }> = ({ text, color = C.white, size, top = 1180 }) => {
  const f = useCurrentFrame();
  const op = interpolate(f, [2, 12], [0, 1], clamp);
  const ty = interpolate(f, [2, 14], [22, 0], clamp);
  return (
    <div style={{ position: "absolute", left: 80, right: 80, top, textAlign: "center", direction: "rtl", zIndex: 6 }}>
      <div style={{ display: "inline-block", fontFamily: "Tajawal", fontWeight: 800, fontSize: size, lineHeight: 1.16, color, textShadow: "0 8px 40px rgba(0,0,0,0.9)", opacity: op, transform: `translateY(${ty}px)` }}>{text}</div>
    </div>
  );
};
const Subtitle: React.FC<{ text: string }> = ({ text }) => {
  const f = useCurrentFrame();
  return (
    <div style={{ position: "absolute", left: 110, right: 110, top: 1560, textAlign: "center", direction: "rtl", zIndex: 6, opacity: interpolate(f, [0, 6], [0, 1], clamp) }}>
      <span style={{ fontFamily: "Tajawal", fontWeight: 500, fontSize: 34, color: C.grey, lineHeight: 1.45 }}>{text}</span>
    </div>
  );
};

// ------------------------------------------------------------------ the tangible object: account tank
const Bubble: React.FC<{ tone: string; delay: number; x: number }> = ({ tone, delay, x }) => {
  const f = useCurrentFrame();
  const t = ((f + delay) % 40) / 40;
  return <div style={{ position: "absolute", left: x, bottom: `${6 + t * 70}%`, width: 8 + (x % 5), height: 8 + (x % 5), borderRadius: "50%", background: shade(tone, 45), opacity: (1 - t) * 0.5 }} />;
};

const Tank: React.FC<{ cx: number; level: number; tone?: "teal" | "red"; name?: string; nameColor?: string; scale?: number; dim?: number; big?: boolean; hideReadout?: boolean }> = ({
  cx, level, tone = "teal", name, nameColor = C.grey, scale = 1, dim = 1, big, hideReadout,
}) => {
  const TW = big ? 340 : 300, TH = big ? 660 : 640;
  const col = tone === "red" ? C.red : C.teal;
  const DANGER = 0.15; // bottom 15% = the −10% failure zone
  return (
    <div style={{ position: "absolute", left: `calc(50% + ${cx}px)`, top: 420, transform: `translateX(-50%) scale(${scale})`, transformOrigin: "50% 50%", width: TW, height: TH, opacity: dim, zIndex: 4 }}>
      {name && (
        <div style={{ position: "absolute", top: -64, left: -40, width: TW + 80, textAlign: "center", fontFamily: "Tajawal", fontWeight: 800, fontSize: 44, color: nameColor, direction: "rtl", ...TAB }}>{name}</div>
      )}
      {/* glass body */}
      <div style={{ position: "absolute", inset: 0, borderRadius: 64, overflow: "hidden",
        background: "linear-gradient(105deg, rgba(255,255,255,0.07), rgba(27,58,69,0.16))",
        border: "2px solid rgba(159,180,188,0.32)",
        boxShadow: "inset 0 2px 34px rgba(0,0,0,0.5), 0 30px 80px rgba(0,0,0,0.5)" }}>
        {/* danger zone */}
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: `${DANGER * 100}%`, background: "linear-gradient(0deg, rgba(225,90,90,0.28), rgba(225,90,90,0))" }} />
        {/* liquid */}
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: `${Math.max(0, level) * 100}%`,
          background: `linear-gradient(180deg, ${shade(col, 22)} 0%, ${col} 34%, ${shade(col, -16)} 100%)`,
          boxShadow: `0 0 46px ${col}`, transition: "none" }}>
          <div style={{ position: "absolute", top: -7, left: 0, right: 0, height: 14, background: shade(col, 40), borderRadius: "50%", opacity: 0.9, boxShadow: `0 0 20px ${col}` }} />
          <Bubble tone={col} delay={0} x={70} /><Bubble tone={col} delay={13} x={150} /><Bubble tone={col} delay={26} x={210} />
        </div>
        {/* glass highlight streak */}
        <div style={{ position: "absolute", top: 30, left: 46, width: 34, height: TH - 150, borderRadius: 18, background: "linear-gradient(180deg, rgba(255,255,255,0.20), rgba(255,255,255,0))" }} />
        {/* tick marks */}
        {[0.25, 0.5, 0.75].map((m) => <div key={m} style={{ position: "absolute", right: 18, bottom: `${m * 100}%`, width: 22, height: 2, background: "rgba(159,180,188,0.35)" }} />)}
      </div>
      {/* −10% danger line + label */}
      <div style={{ position: "absolute", left: -10, right: -10, bottom: `${DANGER * 100}%`, height: 2, background: C.red, boxShadow: `0 0 12px ${C.red}` }} />
      <div style={{ position: "absolute", left: -110, bottom: `${DANGER * 100}%`, transform: "translateY(50%)", fontFamily: "Tajawal", fontWeight: 800, fontSize: 26, color: C.red, ...TAB }}>−10%</div>
      {/* level readout */}
      {!hideReadout && (
        <div style={{ position: "absolute", left: 0, right: 0, top: "40%", textAlign: "center", fontFamily: "Tajawal", fontWeight: 800, fontSize: big ? 82 : 64, color: C.white, textShadow: "0 4px 20px rgba(0,0,0,0.7)", ...TAB }}>
          {Math.round(Math.max(0, level) * 100)}%
        </div>
      )}
    </div>
  );
};

const StatusHud: React.FC<{ fill: number; failed?: boolean }> = ({ fill, failed }) => (
  <div style={{ position: "absolute", top: 288, left: 90, right: 90, height: 74, zIndex: 7, borderRadius: 16,
    background: "linear-gradient(160deg, rgba(27,58,69,0.55), rgba(14,30,36,0.35))", border: "1px solid rgba(159,180,188,0.22)",
    display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 26px", direction: "rtl" }}>
    <span style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 28, color: failed ? C.red : C.white }}>{failed ? "المحفظة سقطت" : "محفظة ممولة"}</span>
    <div style={{ display: "flex", alignItems: "center", gap: 14, direction: "ltr" }}>
      <div style={{ width: 250, height: 20, borderRadius: 10, background: "rgba(255,255,255,0.06)", overflow: "hidden", border: "1px solid rgba(159,180,188,0.2)" }}>
        <div style={{ height: "100%", width: `${Math.min(100, fill * 100)}%`, background: failed ? C.red : `linear-gradient(90deg, ${C.teal}, ${C.red})` }} />
      </div>
      <span style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 26, color: C.red, ...TAB }}>−10%</span>
    </div>
  </div>
);

// glass info card
const Card: React.FC<{ top: number; cx?: number; ry?: number; w: number; h: number; accent: string; lit?: boolean; dim?: number; children: React.ReactNode }> = ({ top, cx = 0, ry = 0, w, h, accent, lit, dim = 1, children }) => (
  <div style={{ position: "absolute", left: "50%", top, width: w, height: h, opacity: dim, zIndex: 5,
    transform: `translateX(calc(-50% + ${cx}px)) perspective(1500px) rotateY(${ry}deg)`, borderRadius: 22,
    background: lit ? "linear-gradient(160deg, rgba(225,90,90,0.18), rgba(27,58,69,0.5))" : "linear-gradient(160deg, rgba(27,58,69,0.62), rgba(14,30,36,0.5))",
    border: `1.5px solid ${lit ? accent : "rgba(159,180,188,0.28)"}`,
    boxShadow: lit ? "0 18px 60px rgba(225,90,90,0.35), inset 0 1px 0 rgba(255,255,255,0.08)" : "0 26px 70px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.06)",
    backdropFilter: "blur(2px)", display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center",
    fontFamily: "Tajawal", fontWeight: 800, direction: "rtl", padding: 24 }}>{children}</div>
);

// discrete "gulp" drain — each loss drops the level one step
const stepDown = (f: number, f0: number, f1: number, steps: number, from: number, to: number) => {
  const p = interpolate(f, [f0, f1], [0, 1], clamp);
  const s = Math.min(steps, Math.floor(p * steps + 1e-6));
  return from + (to - from) * (s / steps);
};

// ================================================================== reel
export const ReelTank: React.FC = () => (
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

// HOOK — the funded account draining into the red
const B1: React.FC = () => {
  const f = useCurrentFrame();
  const level = stepDown(f, 0, F(2.6), 2, 0.42, 0.24);
  const hud = interpolate(f, [0, F(2.6)], [0.55, 0.74], clamp);
  return (
    <AbsoluteFill>
      <Tank cx={0} level={level} tone="red" big />
      <Kicker /><StatusHud fill={hud} /><Scrim />
      <Hero text="چم محفظة ممولة دفعت فلوسها… وطحت؟" size={76} top={1140} />
      <Subtitle text="خزان حسابك ينزل — والمخاطرة اهي اللي تحدد بأي سرعة" />
      <Gem />
    </AbsoluteFill>
  );
};

// PARADOX — personal account full, funded account draining
const B2: React.FC = () => (
  <AbsoluteFill>
    <Tank cx={-252} level={0.9} tone="teal" name="حسابك الشخصي" nameColor={C.teal} scale={0.8} />
    <Tank cx={252} level={0.26} tone="red" name="المحفظة الممولة" nameColor={C.red} scale={0.8} />
    <Kicker /><Scrim />
    <Hero text="رابح بحسابك · طايح بالمحفظة" size={64} top={1150} />
    <Subtitle text="نفس الاستراتيجية — يتغيّر بس حجم المخاطرة" />
    <Gem />
  </AbsoluteFill>
);

// PIVOT
const B3: React.FC = () => (
  <AbsoluteFill>
    <Tank cx={0} level={0.28} tone="red" big dim={0.4} />
    <Scrim />
    <Hero text="ليش؟" size={150} top={830} />
    <Gem />
  </AbsoluteFill>
);

// INVITE — the two tanks reveal, both full, ready to be tested
const B4: React.FC = () => {
  const f = useCurrentFrame();
  const app = interpolate(f, [0, F(0.6)], [0, 1], clamp);
  return (
    <AbsoluteFill>
      <Tank cx={-252} level={1} tone="red" name="مخاطرة 2%" nameColor={C.red} scale={0.8} dim={app} />
      <Tank cx={252} level={1} tone="teal" name="مخاطرة 0.5%" nameColor={C.teal} scale={0.8} dim={app} />
      <Kicker /><Scrim />
      <Hero text="تعال أوريك الفرق" size={86} top={1180} />
      <Gem />
    </AbsoluteFill>
  );
};

// BELIEF+WHY — indicators pile up, the tank (risk) never moves
const B56: React.FC = () => {
  const f = useCurrentFrame();
  const n = Math.min(4, Math.floor(interpolate(f, [0, F(2.0)], [0, 4], clamp)) + 1);
  const labels = ["EMA", "RSI", "زون طلب", "أسهم دخول"];
  return (
    <AbsoluteFill>
      <Tank cx={0} level={0.5} tone="teal" big dim={0.32} hideReadout />
      {labels.slice(0, n).map((l, i) => (
        <Card key={i} top={430 + i * 74} cx={-140 + i * 88} ry={-14 + i * 8} w={400} h={92} accent="rgba(159,180,188,0.4)" dim={0.9}>
          <span style={{ fontSize: 40, color: i % 2 ? C.teal : C.grey }}>{l}</span>
        </Card>
      ))}
      <Scrim />
      <Hero text="استراتيجية أقوى؟" size={78} top={1190} />
      <Subtitle text="تكدّس مؤشرات… والخزان ما يتحرك — المخاطرة اهي نفسها" />
      <Gem />
    </AbsoluteFill>
  );
};

// TURN — profit is optional, the loss limit is final
const B7: React.FC = () => {
  const f = useCurrentFrame();
  const p = interpolate(f, [0, F(1.2)], [0, 1], clamp);
  return (
    <AbsoluteFill>
      <Tank cx={0} level={0.5} tone="red" big dim={0.22} hideReadout />
      <Card top={460} ry={11} w={780} h={148} accent="rgba(46,204,154,0.5)" dim={interpolate(p, [0, 1], [1, 0.4], clamp)}>
        <span style={{ fontSize: 46, color: C.grey }}>الهدف 5% — بدون سقف زمني</span>
      </Card>
      <Card top={676} ry={-9} w={840} h={176} accent={C.red} lit>
        <span style={{ fontSize: 52, color: C.white }}>حد الخسارة 10% — <span style={{ color: C.red }}>نهائي</span></span>
      </Card>
      <Scrim />
      <Hero text="مو اختبار ربح — اختبار خسارة" color={C.red} size={82} top={1210} />
      <Subtitle text="المحفظة تختبر قدرتك إنك ما تخسر — مو إنك تربح" />
      <Gem />
    </AbsoluteFill>
  );
};

// NUMBER — 2% empties in 5 gulps, 0.5% barely sips
const B8: React.FC = () => {
  const f = useCurrentFrame();
  const l2 = stepDown(f, F(0.2), F(1.9), 5, 1, 0.0);
  const l05 = stepDown(f, F(0.2), F(2.4), 5, 1, 0.75);
  return (
    <AbsoluteFill>
      <Tank cx={-252} level={l2} tone="red" name="مخاطرة 2%" nameColor={C.red} scale={0.8} />
      <Tank cx={252} level={l05} tone="teal" name="مخاطرة 0.5%" nameColor={C.teal} scale={0.8} />
      <Kicker /><Scrim />
      <Hero text="5 خسائر تفرّغ الخزان — ولا 20؟" size={80} top={1160} />
      <Subtitle text="بمخاطرة 2% خمس خسائر توقفك · بـ 0.5% تحتاج 20 خسارة" />
      <Gem />
    </AbsoluteFill>
  );
};

// VERDICT — the 2% tank hits empty · FAILED
const B9: React.FC = () => {
  const f = useCurrentFrame();
  const sx = f < F(0.5) ? Math.sin(f * 3.2) * 7 : 0;
  return (
    <AbsoluteFill>
      <div style={{ transform: `translateX(${sx}px)` }}>
        <Tank cx={0} level={0.03} tone="red" big />
      </div>
      <AbsoluteFill style={{ background: "radial-gradient(60% 48% at 50% 40%, rgba(225,90,90,0.24), rgba(225,90,90,0) 70%)", zIndex: 2 }} />
      <StatusHud fill={1} failed /><Scrim />
      <Hero text="تدفع فلوسها… وتطيح" size={98} top={1180} />
      <Gem />
    </AbsoluteFill>
  );
};

// PROOF — the equations
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
      <div style={{ position: "absolute", top: 430, left: 0, width: WIDTH, textAlign: "center", zIndex: 5, fontFamily: "Tajawal", fontWeight: 800, fontSize: 40, color: C.grey, direction: "rtl" }}>نفس الوصول للحد — بمسارين</div>
      <Card top={560} ry={9} w={800} h={158} accent={C.red} dim={r1}>{eq("2%", "× 5", C.red)}</Card>
      <Card top={772} ry={-9} w={800} h={158} accent={C.teal} dim={r2}>{eq("0.5%", "× 20", C.teal)}</Card>
      <Scrim />
      <Subtitle text="شوف الأرقام — نفس الـ 10%، بس عدد الخسائر يفرق" />
      <Gem />
    </AbsoluteFill>
  );
};

// CARE — the 0.5% tank stands safe
const B11: React.FC = () => (
  <AbsoluteFill>
    <Tank cx={0} level={0.75} tone="teal" big />
    <Scrim />
    <Hero text="مخاطرتك اهي اللي تعدّيك — مو نموذجك" color={C.teal} size={78} top={1170} />
    <Gem />
  </AbsoluteFill>
);

// LOOP — mirror the hook + CTA
const B12: React.FC = () => {
  const f = useCurrentFrame();
  const level = stepDown(f, F(0.6), F(3.0), 2, 0.42, 0.26);
  return (
    <AbsoluteFill>
      <Tank cx={0} level={level} tone="red" big />
      <Kicker /><StatusHud fill={0.55} /><Scrim />
      <Hero text="اكتب «ممول» بالتعليقات" color={C.teal} size={82} top={1150} />
      <Subtitle text="وچم صفقة باليوم؟ وچم خسارة توقفك؟ — يوصلك الملف كامل" />
      <Gem />
    </AbsoluteFill>
  );
};
