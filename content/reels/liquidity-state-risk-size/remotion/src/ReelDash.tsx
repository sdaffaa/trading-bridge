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
  card: "#12262E", cardHi: "#1B3A45", white: "#FFFFFF", grey: "#9FB4BC",
  teal: "#2ECC9A", red: "#E15A5A",
};
const clamp = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
const F = (s: number) => Math.round(s * FPS);
const TAB: React.CSSProperties = { fontVariantNumeric: "tabular-nums", fontFeatureSettings: '"tnum" 1' };
const DAMP = Easing.bezier(0.4, 0, 0.2, 1);
const shade = (hex: string, pct: number) => {
  const n = parseInt(hex.slice(1), 16); const r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255; const f = pct / 100;
  const a = (c: number) => Math.max(0, Math.min(255, Math.round(c + (pct > 0 ? 255 - c : c) * f)));
  return `rgb(${a(r)},${a(g)},${a(b)})`;
};
const NOISE = "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")";
const usd = (n: number) => "$" + Math.round(n).toLocaleString("en-US");

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
const Bg: React.FC = () => {
  const f = useCurrentFrame();
  const dx = Math.sin(f * 0.010) * 16, dy = Math.cos(f * 0.008) * 12;
  const pool = 0.10 + Math.sin(f * 0.03) * 0.03;
  return (
    <>
      <AbsoluteFill style={{ background: `radial-gradient(128% 92% at 50% 30%, ${C.bgTop} 0%, ${C.bg} 48%, ${C.bgFloor} 100%)` }} />
      <AbsoluteFill style={{ transform: `translate(${dx}px, ${dy}px) scale(1.06)` }}><Constellation /></AbsoluteFill>
      <AbsoluteFill style={{ background: `radial-gradient(46% 30% at 50% 22%, rgba(120,200,190,${pool}) 0%, rgba(0,0,0,0) 70%)` }} />
      <AbsoluteFill style={{ boxShadow: "inset 0 0 460px 120px rgba(0,0,0,0.55)", pointerEvents: "none" }} />
      <AbsoluteFill style={{ backgroundImage: NOISE, backgroundSize: "160px 160px", opacity: 0.05, mixBlendMode: "overlay", pointerEvents: "none" }} />
    </>
  );
};
const Gem: React.FC = () => (
  <div style={{ position: "absolute", top: 1812, left: 0, width: WIDTH, display: "flex", justifyContent: "center", alignItems: "center", gap: 14, zIndex: 8, opacity: 0.9 }}>
    <svg width={46} height={46} viewBox="0 0 100 100"><g fill="none" stroke="rgba(255,255,255,0.9)" strokeWidth={3} strokeLinejoin="round">
      <polygon points="50,6 82,32 68,92 32,92 18,32" fill="rgba(201,209,214,0.12)" /><path d="M18,32 L50,44 L82,32 M50,44 L32,92 M50,44 L68,92 M50,6 L50,44" /></g></svg>
    <span style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 30, color: "rgba(255,255,255,0.82)", direction: "ltr", letterSpacing: 1 }}>liquidity.state</span>
  </div>
);
const Kicker: React.FC<{ text?: string }> = ({ text = "لغرض تعليمي" }) => (
  <div style={{ position: "absolute", top: 224, left: 0, width: WIDTH, textAlign: "center", zIndex: 7 }}>
    <span style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 22, color: "rgba(159,180,188,0.7)", letterSpacing: 3, direction: "rtl" }}>{text}</span>
  </div>
);
const Scrim: React.FC = () => (
  <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 700, zIndex: 3, background: "linear-gradient(180deg, rgba(10,12,16,0) 0%, rgba(10,12,16,0.72) 58%, rgba(10,12,16,0.9) 100%)", pointerEvents: "none" }} />
);
const Hero: React.FC<{ text: string; color?: string; size: number; top?: number }> = ({ text, color = C.white, size, top = 1180 }) => {
  const f = useCurrentFrame();
  return (
    <div style={{ position: "absolute", left: 80, right: 80, top, textAlign: "center", direction: "rtl", zIndex: 6 }}>
      <div style={{ display: "inline-block", fontFamily: "Tajawal", fontWeight: 800, fontSize: size, lineHeight: 1.16, color, textShadow: "0 8px 40px rgba(0,0,0,0.9)", opacity: interpolate(f, [2, 12], [0, 1], clamp), transform: `translateY(${interpolate(f, [2, 14], [22, 0], clamp)}px)` }}>{text}</div>
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
const Stage: React.FC<{ from: number; to: number; dur: number; children: React.ReactNode }> = ({ from, to, dur, children }) => {
  const f = useCurrentFrame();
  const s = interpolate(f, [0, F(dur)], [from, to], { ...clamp, easing: DAMP });
  return <AbsoluteFill style={{ transform: `scale(${s})`, transformOrigin: "50% 42%" }}>{children}</AbsoluteFill>;
};
const Finish: React.FC = () => {
  const f = useCurrentFrame();
  const leak = interpolate(f, [F(12.6), F(13.3), F(14.2)], [0, 0.14, 0], clamp);
  const flash = interpolate(f, [F(13.16), F(13.26), F(13.6)], [0, 0.42, 0], clamp);
  const vig = interpolate(f, [F(12.9), F(13.35)], [0, 1], clamp);
  const loopFlash = interpolate(f, [F(17.9), F(18.02), F(18.3)], [0, 0.3, 0], clamp);
  return (
    <>
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(18,58,68,0.12) 0%, rgba(0,0,0,0) 45%, rgba(86,64,42,0.07) 100%)", mixBlendMode: "soft-light", pointerEvents: "none", zIndex: 20 }} />
      <AbsoluteFill style={{ boxShadow: `inset 0 0 ${320 + vig * 200}px ${90 + vig * 90}px rgba(0,0,0,${0.34 + vig * 0.16})`, pointerEvents: "none", zIndex: 20 }} />
      {leak > 0.001 && <AbsoluteFill style={{ background: `radial-gradient(42% 30% at 80% 12%, rgba(46,204,154,${leak}), rgba(0,0,0,0) 60%)`, mixBlendMode: "screen", pointerEvents: "none", zIndex: 21 }} />}
      {(flash + loopFlash) > 0.001 && <AbsoluteFill style={{ background: `rgba(255,238,235,${flash + loopFlash})`, mixBlendMode: "screen", pointerEvents: "none", zIndex: 22 }} />}
    </>
  );
};

// ------------------------------------------------------------------ prop-firm meter
const Meter: React.FC<{ label: string; sub: string; value: string; fill: number; tone: "red" | "teal"; w?: number }> = ({ label, sub, value, fill, tone, w = 720 }) => {
  const col = tone === "red" ? C.red : C.teal;
  return (
    <div style={{ width: w, direction: "rtl" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 10 }}>
        <div style={{ display: "flex", gap: 12, alignItems: "baseline" }}>
          <span style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 30, color: C.white }}>{label}</span>
          <span style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 18, color: "rgba(159,180,188,0.65)", letterSpacing: 1, direction: "ltr" }}>{sub}</span>
        </div>
        <span style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 34, color: col, direction: "ltr", ...TAB }}>{value}</span>
      </div>
      <div style={{ height: 22, borderRadius: 11, background: "rgba(255,255,255,0.06)", border: "1px solid rgba(159,180,188,0.18)", overflow: "hidden", direction: "ltr" }}>
        <div style={{ height: "100%", width: `${Math.min(100, fill * 100)}%`, background: `linear-gradient(90deg, ${shade(col, 10)}, ${col})`, boxShadow: `0 0 16px ${col}` }} />
      </div>
    </div>
  );
};

// full funded-account challenge dashboard (the recognizable hero)
const Dashboard: React.FC<{ dd: number; target: number; days?: number; trades?: number; failed?: boolean; dim?: number }> = ({
  dd, target, days = 21, trades = 14, failed, dim = 1,
}) => {
  const equity = 100000 * (1 - dd * 0.10);
  return (
    <div style={{ position: "absolute", left: "50%", top: 330, transform: "translateX(-50%)", width: 880, opacity: dim, zIndex: 4,
      borderRadius: 30, padding: "34px 42px 30px",
      background: "linear-gradient(165deg, rgba(27,58,69,0.62), rgba(14,30,36,0.55))",
      border: `1.5px solid ${failed ? "rgba(225,90,90,0.6)" : "rgba(159,180,188,0.26)"}`,
      boxShadow: failed ? "0 30px 90px rgba(225,90,90,0.28), inset 0 1px 0 rgba(255,255,255,0.06)" : "0 34px 90px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.06)",
      backdropFilter: "blur(3px)" }}>
      {/* header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", direction: "rtl", marginBottom: 22 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          <span style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 38, color: C.white }}>حساب ممول · التحدي</span>
          <span style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 18, color: "rgba(159,180,188,0.6)", letterSpacing: 2, direction: "ltr" }}>FUNDED TRADING CHALLENGE</span>
        </div>
        <span style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 24, color: failed ? C.red : C.teal, direction: "ltr",
          padding: "8px 18px", borderRadius: 999, border: `1.5px solid ${failed ? C.red : C.teal}`, background: failed ? "rgba(225,90,90,0.12)" : "rgba(46,204,154,0.10)" }}>
          {failed ? "FAILED" : "PHASE 1"}
        </span>
      </div>
      {/* balance */}
      <div style={{ direction: "rtl", marginBottom: 26 }}>
        <span style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 26, color: C.grey }}>الرصيد</span>
        <div style={{ display: "flex", alignItems: "baseline", gap: 18, direction: "ltr" }}>
          <span style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 88, color: C.white, lineHeight: 1, ...TAB }}>{usd(equity)}</span>
          <span style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 30, color: C.red, ...TAB }}>▼ {(dd * 10).toFixed(1)}%</span>
        </div>
      </div>
      {/* meters */}
      <div style={{ display: "flex", flexDirection: "column", gap: 22, alignItems: "center" }}>
        <Meter label="حد السحب" sub="MAX DRAWDOWN" value={`−${(dd * 10).toFixed(1)}% / −10%`} fill={dd} tone="red" w={800} />
        <Meter label="الهدف" sub="PROFIT TARGET" value={`+${(target * 5).toFixed(1)}% / +5%`} fill={target} tone="teal" w={800} />
      </div>
      {/* footer */}
      <div style={{ display: "flex", justifyContent: "space-between", direction: "rtl", marginTop: 26, paddingTop: 20, borderTop: "1px solid rgba(159,180,188,0.14)" }}>
        <span style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 26, color: C.grey }}>الأيام المتبقية <span style={{ color: C.white, ...TAB }}>{days}</span></span>
        <span style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 26, color: C.grey }}>الصفقات <span style={{ color: C.white, ...TAB }}>{trades}</span></span>
      </div>
    </div>
  );
};

// compact account card for side-by-side comparison
const AccountCard: React.FC<{ cx: number; risk: string; dd: number; failed?: boolean; tone: "red" | "teal"; dim?: number }> = ({ cx, risk, dd, failed, tone, dim = 1 }) => {
  const col = tone === "red" ? C.red : C.teal;
  const equity = 100000 * (1 - dd * 0.10);
  return (
    <div style={{ position: "absolute", left: `calc(50% + ${cx}px)`, top: 400, transform: "translateX(-50%)", width: 430, opacity: dim, zIndex: 4,
      borderRadius: 24, padding: "26px 28px",
      background: "linear-gradient(165deg, rgba(27,58,69,0.6), rgba(14,30,36,0.5))",
      border: `1.5px solid ${failed ? col : "rgba(159,180,188,0.24)"}`,
      boxShadow: failed ? `0 22px 60px rgba(225,90,90,0.3)` : "0 26px 70px rgba(0,0,0,0.5)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", direction: "rtl", marginBottom: 18 }}>
        <span style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 40, color: col }}>مخاطرة {risk}</span>
        <span style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 20, color: failed ? C.red : C.teal, direction: "ltr", padding: "5px 12px", borderRadius: 999, border: `1.4px solid ${failed ? C.red : C.teal}` }}>{failed ? "FAILED" : "LIVE"}</span>
      </div>
      <div style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 52, color: C.white, direction: "ltr", marginBottom: 20, ...TAB }}>{usd(equity)}</div>
      <Meter label="حد السحب" sub="DRAWDOWN" value={`−${(dd * 10).toFixed(1)}%`} fill={dd} tone="red" w={374} />
    </div>
  );
};

const Card: React.FC<{ top: number; ry?: number; w: number; h: number; accent: string; lit?: boolean; dim?: number; children: React.ReactNode }> = ({ top, ry = 0, w, h, accent, lit, dim = 1, children }) => (
  <div style={{ position: "absolute", left: "50%", top, width: w, height: h, opacity: dim, zIndex: 5,
    transform: `translateX(-50%) perspective(1500px) rotateY(${ry}deg)`, borderRadius: 22,
    background: lit ? "linear-gradient(160deg, rgba(225,90,90,0.18), rgba(27,58,69,0.5))" : "linear-gradient(160deg, rgba(27,58,69,0.62), rgba(14,30,36,0.5))",
    border: `1.5px solid ${lit ? accent : "rgba(159,180,188,0.28)"}`,
    boxShadow: lit ? "0 18px 60px rgba(225,90,90,0.35)" : "0 26px 70px rgba(0,0,0,0.5)",
    display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", fontFamily: "Tajawal", fontWeight: 800, direction: "rtl", padding: 24 }}>{children}</div>
);

const stepUp = (f: number, f0: number, f1: number, steps: number, from: number, to: number) => {
  const p = interpolate(f, [f0, f1], [0, 1], clamp);
  const s = Math.min(steps, Math.floor(p * steps + 1e-6));
  return from + (to - from) * (s / steps);
};

// ================================================================== reel
export const ReelDash: React.FC = () => (
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
    <Finish />
  </AbsoluteFill>
);

const B1: React.FC = () => {
  const f = useCurrentFrame();
  const dd = interpolate(f, [0, F(2.6)], [0.55, 0.72], clamp);
  return (
    <AbsoluteFill>
      <Kicker />
      <Stage from={1} to={1.04} dur={2.6}><Dashboard dd={dd} target={0.28} /></Stage>
      <Scrim />
      <Hero text="ليش محفظتك الممولة راحت؟" size={80} top={1150} />
      <Subtitle text="تدري ليش محفظتك الممولة راحت فلوسها؟" />
      <Gem />
    </AbsoluteFill>
  );
};

const B2: React.FC = () => (
  <AbsoluteFill>
    <Kicker />
    <Stage from={1.02} to={1} dur={1.6}>
      <AccountCard cx={-252} risk="شخصي" dd={0.08} tone="teal" />
      <AccountCard cx={252} risk="ممول" dd={0.74} tone="red" />
    </Stage>
    <Scrim />
    <Hero text="رابح بحسابك · طايح بالممولة" size={64} top={1160} />
    <Subtitle text="استراتيجيتك رابحة بحسابك… وبالممولة تطيح" />
    <Gem />
  </AbsoluteFill>
);

const B3: React.FC = () => (
  <AbsoluteFill>
    <Stage from={1} to={1.06} dur={0.8}><Dashboard dd={0.72} target={0.28} dim={0.4} /></Stage>
    <Scrim />
    <Hero text="ليش؟" size={150} top={860} />
    <Gem />
  </AbsoluteFill>
);

const B4: React.FC = () => {
  const f = useCurrentFrame();
  const app = interpolate(f, [0, F(0.6)], [0, 1], clamp);
  return (
    <AbsoluteFill>
      <Kicker />
      <Stage from={1.05} to={1} dur={1.2}>
        <AccountCard cx={-252} risk="2%" dd={0} tone="red" dim={app} />
        <AccountCard cx={252} risk="0.5%" dd={0} tone="teal" dim={app} />
      </Stage>
      <Scrim />
      <Hero text="تعال أوريك" size={92} top={1180} />
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
      <Stage from={1} to={1.03} dur={2.4}><Dashboard dd={0.5} target={0.28} dim={0.34} /></Stage>
      {labels.slice(0, n).map((l, i) => (
        <Card key={i} top={380 + i * 74} ry={-12 + i * 7} w={430} h={92} accent="rgba(159,180,188,0.4)" dim={0.9}>
          <span style={{ fontSize: 40, color: i % 2 ? C.teal : C.grey }}>{l}</span>
        </Card>
      ))}
      <Scrim />
      <Hero text="استراتيجية أقوى؟" size={78} top={1190} />
      <Subtitle text="الكل يقول لازم استراتيجية أقوى… ونموذج يضبط بالباك تست" />
      <Gem />
    </AbsoluteFill>
  );
};

const B7: React.FC = () => {
  const f = useCurrentFrame();
  const p = interpolate(f, [0, F(1.2)], [0, 1], clamp);
  return (
    <AbsoluteFill>
      <Card top={470} ry={11} w={780} h={150} accent="rgba(46,204,154,0.5)" dim={interpolate(p, [0, 1], [1, 0.4], clamp)}>
        <span style={{ fontSize: 46, color: C.grey }}>الهدف +5% — بدون سقف زمني</span>
      </Card>
      <Card top={690} ry={-9} w={840} h={176} accent={C.red} lit>
        <span style={{ fontSize: 50, color: C.white }}>حد السحب −10% — <span style={{ color: C.red }}>نهائي</span></span>
      </Card>
      <Scrim />
      <Hero text="مو اختبار ربح — اختبار خسارة" color={C.red} size={82} top={1210} />
      <Subtitle text="لكن بالواقع؟ الممولة مو اختبار ربح… اهي اختبار خسارة" />
      <Gem />
    </AbsoluteFill>
  );
};

const B8: React.FC = () => {
  const f = useCurrentFrame();
  const dd2 = stepUp(f, F(0.2), F(1.9), 5, 0, 0.9);      // 2% risk → 5 losses fill drawdown to the limit
  const dd05 = stepUp(f, F(0.2), F(2.4), 5, 0, 0.225);   // 0.5% risk → 5 losses barely move it
  return (
    <AbsoluteFill>
      <Kicker />
      <Stage from={1} to={1.05} dur={2.6}>
        <AccountCard cx={-252} risk="2%" dd={dd2} tone="red" failed={dd2 >= 0.88} />
        <AccountCard cx={252} risk="0.5%" dd={dd05} tone="teal" />
      </Stage>
      <Scrim />
      <Hero text="5 خسائر توصّلك −10% — ولا 20؟" size={72} top={1170} />
      <Subtitle text="بمخاطرة 2% خمس خسائر توصّلك حد السحب · بـ 0.5% تحتاج 20" />
      <Gem />
    </AbsoluteFill>
  );
};

const B9: React.FC = () => {
  const f = useCurrentFrame();
  const sx = f < F(0.5) ? Math.sin(f * 3.2) * 6 : 0;
  const wash = interpolate(f, [F(0.0), F(0.3)], [0.1, 0.3], clamp);
  return (
    <AbsoluteFill>
      <Stage from={1.03} to={1.1} dur={0.7}>
        <div style={{ transform: `translateX(${sx}px)` }}><Dashboard dd={1} target={0.28} failed /></div>
      </Stage>
      <AbsoluteFill style={{ background: `radial-gradient(60% 46% at 50% 38%, rgba(225,90,90,${wash}), rgba(225,90,90,0) 70%)`, zIndex: 2 }} />
      <Scrim />
      <Hero text="محفظتك الممولة… راحت" size={92} top={1180} />
      <Gem />
    </AbsoluteFill>
  );
};

const B10: React.FC = () => {
  const f = useCurrentFrame();
  const r1 = interpolate(f, [0, F(0.9)], [0, 1], clamp);
  const r2 = interpolate(f, [F(1.0), F(1.9)], [0, 1], clamp);
  const eq = (a: string, b: string, ac: string) => (
    <span style={{ fontSize: 74, direction: "ltr", display: "inline-block", ...TAB }}>
      <span style={{ color: ac }}>{a}</span> <span style={{ color: C.grey, opacity: 0.75 }}>{b}</span> <span style={{ color: C.white }}>= 10%</span>
    </span>
  );
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", top: 430, left: 0, width: WIDTH, textAlign: "center", zIndex: 5, fontFamily: "Tajawal", fontWeight: 800, fontSize: 40, color: C.grey, direction: "rtl" }}>نفس حد السحب −10% — بمسارين</div>
      <Card top={560} ry={9} w={800} h={158} accent={C.red} dim={r1}>{eq("2%", "× 5", C.red)}</Card>
      <Card top={772} ry={-9} w={800} h={158} accent={C.teal} dim={r2}>{eq("0.5%", "× 20", C.teal)}</Card>
      <Scrim />
      <Subtitle text="شوف الأرقام — نفس الـ 10%، بس عدد الخسائر يفرق" />
      <Gem />
    </AbsoluteFill>
  );
};

const B11: React.FC = () => (
  <AbsoluteFill>
    <Dashboard dd={0.225} target={0.62} />
    <div style={{ position: "absolute", top: 300, left: 0, width: WIDTH, textAlign: "center", zIndex: 5, fontFamily: "Tajawal", fontWeight: 800, fontSize: 30, color: C.teal, direction: "rtl" }}>مخاطرة 0.5% — الحساب صامد</div>
    <Scrim />
    <Hero text="مخاطرتك اهي اللي تعدّيك — مو نموذجك" color={C.teal} size={76} top={1180} />
    <Gem />
  </AbsoluteFill>
);

const B12: React.FC = () => {
  const f = useCurrentFrame();
  const dd = interpolate(f, [0, F(3.0)], [0.55, 0.66], clamp);
  return (
    <AbsoluteFill>
      <Kicker />
      <Stage from={1} to={1.04} dur={2.6}><Dashboard dd={dd} target={0.3} /></Stage>
      <Scrim />
      <Hero text="اكتب «ممول» بالتعليقات" color={C.teal} size={82} top={1150} />
      <Subtitle text="بس چم صفقة باليوم؟ وچم خسارة توقفك؟ — يوصلك الملف كامل" />
      <Gem />
    </AbsoluteFill>
  );
};
