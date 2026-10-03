import React, { useEffect, useState } from "react";
import {
  AbsoluteFill, Sequence, interpolate, useCurrentFrame, Easing,
  staticFile, delayRender, continueRender,
} from "remotion";

export const FPS = 30;
export const WIDTH = 1080;
export const HEIGHT = 1920;
export const LOOP_RUNTIME_S = 35.4;

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
  <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: 720, zIndex: 3, background: "linear-gradient(180deg, rgba(10,12,16,0) 0%, rgba(10,12,16,0.72) 58%, rgba(10,12,16,0.9) 100%)", pointerEvents: "none" }} />
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
  const flash = interpolate(f, [F(24.9), F(25.05), F(25.4)], [0, 0.4, 0], clamp);   // failure-loop peak flash (~25.0s)
  const vig = interpolate(f, [F(24.4), F(25.1)], [0, 1], clamp);
  return (
    <>
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(18,58,68,0.12) 0%, rgba(0,0,0,0) 45%, rgba(86,64,42,0.07) 100%)", mixBlendMode: "soft-light", pointerEvents: "none", zIndex: 20 }} />
      <AbsoluteFill style={{ boxShadow: `inset 0 0 ${320 + vig * 200}px ${90 + vig * 90}px rgba(0,0,0,${0.34 + vig * 0.16})`, pointerEvents: "none", zIndex: 20 }} />
      {flash > 0.001 && <AbsoluteFill style={{ background: `rgba(255,238,235,${flash})`, mixBlendMode: "screen", pointerEvents: "none", zIndex: 22 }} />}
    </>
  );
};

// ------------------------------------------------------------------ prop-firm dashboard
const Meter: React.FC<{ label: string; sub: string; value: string; fill: number; tone: "red" | "teal"; w?: number }> = ({ label, sub, value, fill, tone, w = 800 }) => {
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
const Dashboard: React.FC<{ dd: number; target: number; days?: number; trades?: number; failed?: boolean; dim?: number; highlightDD?: boolean }> = ({ dd, target, days = 21, trades = 14, failed, dim = 1, highlightDD }) => {
  const equity = 100000 * (1 - dd * 0.10);
  return (
    <div style={{ position: "absolute", left: "50%", top: 330, transform: "translateX(-50%)", width: 880, opacity: dim, zIndex: 4,
      borderRadius: 30, padding: "34px 42px 30px",
      background: "linear-gradient(165deg, rgba(27,58,69,0.62), rgba(14,30,36,0.55))",
      border: `1.5px solid ${failed ? "rgba(225,90,90,0.6)" : "rgba(159,180,188,0.26)"}`,
      boxShadow: failed ? "0 30px 90px rgba(225,90,90,0.28)" : "0 34px 90px rgba(0,0,0,0.55)", backdropFilter: "blur(3px)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", direction: "rtl", marginBottom: 22 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          <span style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 38, color: C.white }}>حساب ممول · التحدي</span>
          <span style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 18, color: "rgba(159,180,188,0.6)", letterSpacing: 2, direction: "ltr" }}>FUNDED TRADING CHALLENGE</span>
        </div>
        <span style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 24, color: failed ? C.red : C.teal, direction: "ltr", padding: "8px 18px", borderRadius: 999, border: `1.5px solid ${failed ? C.red : C.teal}`, background: failed ? "rgba(225,90,90,0.12)" : "rgba(46,204,154,0.10)" }}>{failed ? "FAILED" : "PHASE 1"}</span>
      </div>
      <div style={{ direction: "rtl", marginBottom: 26 }}>
        <span style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 26, color: C.grey }}>الرصيد</span>
        <div style={{ display: "flex", alignItems: "baseline", gap: 18, direction: "ltr" }}>
          <span style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 88, color: C.white, lineHeight: 1, ...TAB }}>{usd(equity)}</span>
          <span style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 30, color: C.red, ...TAB }}>▼ {(dd * 10).toFixed(1)}%</span>
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 22, alignItems: "center" }}>
        <div style={{ position: "relative" }}>
          {highlightDD && <div style={{ position: "absolute", inset: -12, borderRadius: 16, border: `2px solid ${C.red}`, boxShadow: `0 0 30px ${C.red}` }} />}
          <Meter label="حد السحب" sub="MAX DRAWDOWN" value={`−${(dd * 10).toFixed(1)}% / −10%`} fill={dd} tone="red" />
        </div>
        <Meter label="الهدف" sub="PROFIT TARGET" value={`+${(target * 5).toFixed(1)}% / +5%`} fill={target} tone="teal" />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", direction: "rtl", marginTop: 26, paddingTop: 20, borderTop: "1px solid rgba(159,180,188,0.14)" }}>
        <span style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 26, color: C.grey }}>الأيام المتبقية <span style={{ color: C.white, ...TAB }}>{days}</span></span>
        <span style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 26, color: C.grey }}>الصفقات <span style={{ color: C.white, ...TAB }}>{trades}</span></span>
      </div>
    </div>
  );
};

const Card: React.FC<{ top: number; ry?: number; w: number; h: number; accent: string; lit?: boolean; dim?: number; children: React.ReactNode }> = ({ top, ry = 0, w, h, accent, lit, dim = 1, children }) => (
  <div style={{ position: "absolute", left: "50%", top, width: w, height: h, opacity: dim, zIndex: 5,
    transform: `translateX(-50%) perspective(1500px) rotateY(${ry}deg)`, borderRadius: 22,
    background: lit ? "linear-gradient(160deg, rgba(46,204,154,0.16), rgba(27,58,69,0.5))" : "linear-gradient(160deg, rgba(27,58,69,0.62), rgba(14,30,36,0.5))",
    border: `1.5px solid ${lit ? accent : "rgba(159,180,188,0.28)"}`,
    boxShadow: lit ? `0 18px 60px ${accent}55` : "0 26px 70px rgba(0,0,0,0.5)",
    display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", fontFamily: "Tajawal", fontWeight: 800, direction: "rtl", padding: 30 }}>{children}</div>
);

// rule chip (small pill)
const Chip: React.FC<{ cx: number; top: number; tone: "red" | "teal"; big: string; small: string; dim?: number }> = ({ cx, top, tone, big, small, dim = 1 }) => {
  const col = tone === "red" ? C.red : C.teal;
  return (
    <div style={{ position: "absolute", left: `calc(50% + ${cx}px)`, top, transform: "translateX(-50%)", opacity: dim, zIndex: 5,
      width: 380, borderRadius: 20, padding: "24px 26px", direction: "rtl", textAlign: "center",
      background: `linear-gradient(160deg, ${col}22, rgba(14,30,36,0.5))`, border: `1.5px solid ${col}`, boxShadow: `0 18px 50px ${col}33` }}>
      <div style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 60, color: col, ...TAB }}>{big}</div>
      <div style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 30, color: C.white, marginTop: 6 }}>{small}</div>
    </div>
  );
};

// the FAILURE LOOP — doubling the lot after each loss, cycling to a blown account
const FailureLoop: React.FC = () => {
  const f = useCurrentFrame();
  const steps = [
    { lot: "0.5", dd: "−1%" }, { lot: "1", dd: "−3%" }, { lot: "2", dd: "−7%" }, { lot: "4", dd: "−10%" },
  ];
  const cxc = 540, cyc = 700, R = 210;
  const shown = Math.min(4, Math.floor(interpolate(f, [F(0.4), F(3.4)], [0, 4], clamp)));
  const angs = [-90, 0, 90, 180];
  const rot = f * 2.2; // rotating loop
  const done = shown >= 4;
  return (
    <>
      {/* rotating dashed loop ring */}
      <div style={{ position: "absolute", left: cxc - R, top: cyc - R, width: R * 2, height: R * 2, borderRadius: "50%",
        border: `3px dashed ${done ? C.red : "rgba(225,90,90,0.5)"}`, transform: `rotate(${rot}deg)`, opacity: 0.8,
        boxShadow: done ? `0 0 50px ${C.red}` : "none", zIndex: 4 }} />
      {/* center readout */}
      <div style={{ position: "absolute", left: cxc - 150, top: cyc - 70, width: 300, textAlign: "center", zIndex: 6 }}>
        <div style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: done ? 64 : 40, color: C.red, ...TAB }}>{done ? "FAILED" : "حلقة الفشل"}</div>
        <div style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 26, color: C.grey, marginTop: 6, direction: "rtl" }}>{done ? "الاختبار راح" : "دبل اللوت"}</div>
      </div>
      {/* nodes */}
      {steps.map((s, i) => {
        const a = (angs[i] * Math.PI) / 180;
        const x = cxc + Math.cos(a) * R, y = cyc + Math.sin(a) * R;
        const on = i < shown;
        return (
          <div key={i} style={{ position: "absolute", left: x - 90, top: y - 46, width: 180, height: 92, zIndex: 5,
            opacity: on ? 1 : 0.12, transform: `scale(${on ? 1 : 0.8})`,
            borderRadius: 16, background: `linear-gradient(160deg, ${shade(C.red, 6 - i * 4)}, ${shade(C.red, -30)})`,
            border: "1.5px solid rgba(255,255,255,0.15)", boxShadow: on ? `0 0 26px ${C.red}` : "none",
            display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", direction: "rtl" }}>
            <span style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 32, color: C.white, ...TAB, direction: "ltr" }}>{s.lot} لوت</span>
            <span style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 26, color: "#ffd9d9", ...TAB, direction: "ltr" }}>{s.dd}</span>
          </div>
        );
      })}
    </>
  );
};

// ================================================================== reel
export const ReelLoop: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: C.bg }}>
    <FontLoader />
    <Bg />
    <Sequence from={F(0.0)} durationInFrames={F(3.4)}><B1 /></Sequence>
    <Sequence from={F(3.4)} durationInFrames={F(1.4)}><B2 /></Sequence>
    <Sequence from={F(4.8)} durationInFrames={F(3.6)}><B3 /></Sequence>
    <Sequence from={F(8.4)} durationInFrames={F(2.4)}><B4 /></Sequence>
    <Sequence from={F(10.8)} durationInFrames={F(4.4)}><B5 /></Sequence>
    <Sequence from={F(15.2)} durationInFrames={F(2.0)}><B6 /></Sequence>
    <Sequence from={F(17.2)} durationInFrames={F(3.0)}><B7 /></Sequence>
    <Sequence from={F(20.2)} durationInFrames={F(5.4)}><B8 /></Sequence>
    <Sequence from={F(25.6)} durationInFrames={F(4.0)}><B9 /></Sequence>
    <Sequence from={F(29.6)} durationInFrames={F(2.8)}><B10 /></Sequence>
    <Sequence from={F(32.4)} durationInFrames={F(3.0)}><B11 /></Sequence>
    <Finish />
  </AbsoluteFill>
);

const B1: React.FC = () => {
  const f = useCurrentFrame();
  const dd = interpolate(f, [0, F(3.4)], [0.5, 0.68], clamp);
  return (
    <AbsoluteFill>
      <Kicker />
      <Stage from={1} to={1.04} dur={3.4}><Dashboard dd={dd} target={0.28} /></Stage>
      {/* 95% stat */}
      <div style={{ position: "absolute", top: 980, left: 0, width: WIDTH, textAlign: "center", zIndex: 6, direction: "rtl" }}>
        <span style={{ fontFamily: "Tajawal", fontWeight: 800, fontSize: 40, color: C.red, ...TAB }}>95% </span>
        <span style={{ fontFamily: "Tajawal", fontWeight: 700, fontSize: 34, color: C.grey }}>ما يجتازون التحدي</span>
      </div>
      <Scrim />
      <Hero text="ليش 95% ما يجتازون الاختبار الممول؟" size={72} top={1150} />
      <Subtitle text="تبي تعرف ليش أغلب المتداولين غير مؤهّلين يعدّون التحدي؟" />
      <Gem />
    </AbsoluteFill>
  );
};

const B2: React.FC = () => (
  <AbsoluteFill>
    <Stage from={1.03} to={1} dur={1.4}><Dashboard dd={0.68} target={0.28} dim={0.45} /></Stage>
    <Scrim />
    <Hero text="تعال أقولك" size={110} top={900} />
    <Gem />
  </AbsoluteFill>
);

const B3: React.FC = () => (
  <AbsoluteFill>
    <Kicker text="السبب الأول" />
    <Stage from={1} to={1.05} dur={3.6}><Dashboard dd={0.68} target={0.28} highlightDD /></Stage>
    <Scrim />
    <Hero text="هامش الخسارة ضيّق جداً" color={C.red} size={82} top={1150} />
    <Subtitle text="يجبرك تلتزم بإدارة رأس مال صارمة" />
    <Gem />
  </AbsoluteFill>
);

const B4: React.FC = () => (
  <AbsoluteFill>
    <Stage from={1} to={1.03} dur={2.4}><Dashboard dd={0.68} target={0.28} dim={0.4} /></Stage>
    <Scrim />
    <Hero text="والأغلب ما عنده الانضباط" size={84} top={1120} />
    <Subtitle text="هنا بالضبط يطيح أغلب المتداولين" />
    <Gem />
  </AbsoluteFill>
);

const B5: React.FC = () => {
  const f = useCurrentFrame();
  const a1 = interpolate(f, [F(0.2), F(0.8)], [0, 1], clamp);
  const a2 = interpolate(f, [F(1.4), F(2.0)], [0, 1], clamp);
  return (
    <AbsoluteFill>
      <Kicker text="الحل الأول" />
      <Chip cx={-236} top={470} tone="teal" big="0.5%" small="أقصى مخاطرة للصفقة" dim={a1} />
      <Chip cx={236} top={470} tone="red" big="1%" small="وقف يومي — تصكر" dim={a2} />
      <Scrim />
      <Hero text="لا تخاطر أكثر من 0.5% بالصفقة" color={C.teal} size={70} top={1120} />
      <Subtitle text="وأول ما توصل 1% خسارة يومية… وقّف التداول" />
      <Gem />
    </AbsoluteFill>
  );
};

const B6: React.FC = () => (
  <AbsoluteFill>
    <Scrim />
    <Hero text="بس الموضوع مو بس إدارة رأس مال" size={78} top={860} />
    <Gem />
  </AbsoluteFill>
);

const B7: React.FC = () => (
  <AbsoluteFill>
    <Kicker text="السبب الثاني · الأقوى" />
    <Stage from={1} to={1.04} dur={3.0}><Dashboard dd={0.4} target={0.28} days={2} /></Stage>
    <Scrim />
    <Hero text="تبي تخلّص التحدي بيوم أو يومين" size={78} top={1150} />
    <Subtitle text="وهنا يبدأ أخطر شي — حلقة الفشل" />
    <Gem />
  </AbsoluteFill>
);

const B8: React.FC = () => (
  <AbsoluteFill>
    <Kicker text="حلقة الفشل" />
    <Stage from={1} to={1.06} dur={5.4}><FailureLoop /></Stage>
    <Scrim />
    <Hero text="تخسر… تدبل اللوت… وراح الاختبار" color={C.red} size={72} top={1150} />
    <Subtitle text="كل خسارة تدبل فيها اللوت — لين ينفجر الحساب" />
    <Gem />
  </AbsoluteFill>
);

const B9: React.FC = () => (
  <AbsoluteFill>
    <Kicker text="الحل الثاني" />
    <Card top={520} ry={8} w={840} h={260} accent={C.teal} lit>
      <div style={{ direction: "rtl" }}>
        <div style={{ fontSize: 52, color: C.white, lineHeight: 1.3 }}>خذ صفقاتك من أسعار</div>
        <div style={{ fontSize: 52, color: C.teal, lineHeight: 1.3 }}>تتوقّع منها ردة فعل</div>
      </div>
    </Card>
    <Scrim />
    <Hero text="مو تتداول لأنك فاضي وزهقان" size={78} top={1150} />
    <Subtitle text="الصفقة تجيك من مستوى — مو من الملل" />
    <Gem />
  </AbsoluteFill>
);

const B10: React.FC = () => (
  <AbsoluteFill>
    <Card top={540} ry={0} w={820} h={230} accent="rgba(159,180,188,0.4)">
      <div style={{ direction: "rtl" }}>
        <div style={{ fontSize: 50, color: C.white }}>ما فيه setup واضح اليوم؟</div>
        <div style={{ fontSize: 44, color: C.teal, marginTop: 10 }}>دوّره باليوم اللي بعده</div>
      </div>
    </Card>
    <Scrim />
    <Hero text="لا تجبر السوق" size={92} top={1150} />
    <Subtitle text="الصبر جزء من اجتياز التحدي" />
    <Gem />
  </AbsoluteFill>
);

const B11: React.FC = () => {
  const f = useCurrentFrame();
  const dd = interpolate(f, [0, F(3.0)], [0.5, 0.6], clamp);
  return (
    <AbsoluteFill>
      <Kicker />
      <Stage from={1} to={1.04} dur={3.0}><Dashboard dd={dd} target={0.3} /></Stage>
      <Scrim />
      <Hero text="اكتب «ممول» بالكومنت" color={C.teal} size={84} top={1150} />
      <Subtitle text="تبي الجزء الثاني من هالمحتوى؟" />
      <Gem />
    </AbsoluteFill>
  );
};
