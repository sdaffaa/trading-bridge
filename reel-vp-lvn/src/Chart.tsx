import React from 'react';
import {interpolate, Easing} from 'remotion';
import {CHART, PRICE_LO, PRICE_HI, COLORS, BEATS} from './theme';
import data from './chart.json';

const {candles, profile, levels} = data as any;
const START = 30; // first visible bar index
const bars = candles.slice(START);
const N = bars.length;
const AREA_X = CHART.x;
const AREA_W = CHART.w - CHART.profW;     // candle area width
const PROF_X0 = AREA_X + AREA_W + 6;      // profile left
const PROF_RIGHT = CHART.x + CHART.w;     // profile right edge
const slot = AREA_W / N;
const bodyW = Math.max(7, slot * 0.68);

const yOf = (p: number) =>
  CHART.y + ((PRICE_HI - p) / (PRICE_HI - PRICE_LO)) * CHART.h;
const xOf = (i: number) => AREA_X + i * slot + slot / 2;

const ease = (t: number, a: number[], b: number[]) =>
  interpolate(t, a, b, {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.ease)});

export const Chart: React.FC<{t: number}> = ({t}) => {
  // ---- camera ----
  const scale = ease(t, [0, 3.0, 6.8, 10.0, 14.8, 18.6, 19.8, 22.0],
                        [1.0, 1.04, 1.04, 1.075, 1.075, 0.99, 1.0, 1.0]);
  const gapX = xOf(N * 0.78);
  const gapY = yOf((levels.lvnLo + levels.lvnHi) / 2);
  // micro-shake on VERDICT (13.2–13.6)
  const shakeAmt = interpolate(t, [13.2, 13.4, 13.6], [0, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const sx = Math.sin(t * 90) * 3 * shakeAmt;
  const sy = Math.cos(t * 78) * 3 * shakeAmt;

  // ---- progressive reveal ----
  const revealEndAbs = Math.floor(
    interpolate(t, [0, 3, 10, 13.2, 17, 18.6, 22], [64, 66, 71, 72, 81, 88, 88],
      {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})
  );
  const revealEnd = revealEndAbs - START; // relative index

  // opacities
  const zonesOp = ease(t, [0.2, 1.2], [0, 1]);            // core map (profile, HVN/LVN, target) — visible for the hook
  const detailOp = ease(t, [5.0, 6.2], [0, 1]);           // POC/value detail reveal (explanation)
  const npocOp = zonesOp;
  const lvnPulse = 0.5 + 0.5 * Math.sin(Math.max(0, t) * 4) * interpolate(t, [0, 3, 10, 13.2], [1, 0.5, 0.5, 1], {extrapolateRight: 'clamp'});
  const lvnGlow = interpolate(t, [10, 13.2, 15], [0.25, 0.9, 0.6], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const tradeOp = ease(t, [14.8, 15.4], [0, 1]);
  const maxVol = levels.maxVol;

  return (
    <svg width={1080} height={1920} style={{position: 'absolute', left: 0, top: 0}}>
      <defs>
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="4" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>

      <g transform={`translate(${sx},${sy}) translate(${gapX},${gapY}) scale(${scale}) translate(${-gapX},${-gapY})`}>
        {/* grid */}
        {[3320, 3330, 3340, 3350].map((p) => (
          <line key={p} x1={AREA_X} x2={PROF_RIGHT} y1={yOf(p)} y2={yOf(p)}
            stroke="#ffffff" strokeOpacity={0.05} strokeWidth={1} />
        ))}

        {/* HVN wall band */}
        <rect x={AREA_X} y={yOf(levels.wallHi)} width={CHART.w}
          height={yOf(levels.wallLo) - yOf(levels.wallHi)}
          fill={COLORS.teal} opacity={0.09 * zonesOp} />

        {/* LVN gap band (الفراغ) — the star */}
        <rect x={AREA_X} y={yOf(levels.lvnHi)} width={CHART.w}
          height={yOf(levels.lvnLo) - yOf(levels.lvnHi)}
          fill={COLORS.cyan} opacity={(0.05 + 0.06 * lvnGlow) * zonesOp}
          stroke={COLORS.cyan} strokeOpacity={0.55 * zonesOp * lvnPulse}
          strokeDasharray="7 6" strokeWidth={2} />

        {/* Value area edges + POC */}
        <line x1={AREA_X} x2={PROF_RIGHT} y1={yOf(levels.VAH)} y2={yOf(levels.VAH)}
          stroke={COLORS.grey} strokeOpacity={0.28 * detailOp} strokeWidth={1} strokeDasharray="2 6" />
        <line x1={AREA_X} x2={PROF_RIGHT} y1={yOf(levels.VAL)} y2={yOf(levels.VAL)}
          stroke={COLORS.grey} strokeOpacity={0.28 * detailOp} strokeWidth={1} strokeDasharray="2 6" />
        <line x1={AREA_X} x2={PROF_RIGHT} y1={yOf(levels.POC)} y2={yOf(levels.POC)}
          stroke={COLORS.grey} strokeOpacity={0.6 * detailOp} strokeWidth={1.5} strokeDasharray="9 5" />

        {/* nPOC target line (cyan, glowing) */}
        <line x1={AREA_X} x2={PROF_RIGHT} y1={yOf(levels.nPOC)} y2={yOf(levels.nPOC)}
          stroke={COLORS.cyan} strokeOpacity={npocOp} strokeWidth={2.4} filter="url(#glow)" />

        {/* Profile histogram (right) */}
        {profile.map((row: any, i: number) => {
          const w = (row.vol / maxVol) * (CHART.profW * 0.92);
          const inWall = row.price >= levels.wallLo && row.price <= levels.wallHi;
          const isPOC = Math.abs(row.price - levels.POC) < 0.6;
          const inLVN = row.price >= levels.lvnLo && row.price <= levels.lvnHi;
          const col = isPOC ? '#3ee0aa' : inWall ? COLORS.teal : inLVN ? '#4a6b73' : '#37535c';
          const op = inLVN ? 0.85 : 0.9;
          return (
            <rect key={i} x={PROF_RIGHT - w} y={yOf(row.price) - (CHART.h / profile.length) / 2 - 0.5}
              width={w} height={(CHART.h / profile.length) - 1}
              fill={col} opacity={op * zonesOp} rx={1} />
          );
        })}

        {/* Candles */}
        {bars.map((b: any, i: number) => {
          if (i > revealEnd) return null;
          const up = b.c >= b.o;
          const col = up ? COLORS.candleUp : COLORS.candleDown;
          const x = xOf(i);
          const yO = yOf(b.o), yC = yOf(b.c), yH = yOf(b.h), yL = yOf(b.l);
          const top = Math.min(yO, yC);
          const hgt = Math.max(1.5, Math.abs(yC - yO));
          const printing = i === revealEnd;
          return (
            <g key={i} opacity={printing ? 0.9 : 1}>
              <line x1={x} x2={x} y1={yH} y2={yL} stroke={col} strokeWidth={1.6} />
              <rect x={x - bodyW / 2} y={top} width={bodyW} height={hgt} fill={col} rx={1} />
            </g>
          );
        })}

        {/* Trade box (short position tool) */}
        {tradeOp > 0.01 && (
          <g opacity={tradeOp}>
            {/* reward (TP) zone below entry */}
            <rect x={AREA_X} y={yOf(levels.entry)} width={AREA_W}
              height={yOf(levels.tp) - yOf(levels.entry)} fill={COLORS.teal} opacity={0.10} />
            {/* risk (SL) zone above entry */}
            <rect x={AREA_X} y={yOf(levels.sl)} width={AREA_W}
              height={yOf(levels.entry) - yOf(levels.sl)} fill={COLORS.red} opacity={0.12} />
            <line x1={AREA_X} x2={AREA_X + AREA_W} y1={yOf(levels.entry)} y2={yOf(levels.entry)}
              stroke={COLORS.white} strokeWidth={1.6} strokeDasharray="8 5" />
            <line x1={AREA_X} x2={AREA_X + AREA_W} y1={yOf(levels.sl)} y2={yOf(levels.sl)}
              stroke={COLORS.red} strokeWidth={1.6} />
            <line x1={AREA_X} x2={AREA_X + AREA_W} y1={yOf(levels.tp)} y2={yOf(levels.tp)}
              stroke={COLORS.teal} strokeWidth={1.6} />
          </g>
        )}

        {/* Right-axis level tags */}
        {[
          {p: levels.sl, txt: `SL ${levels.sl}`, c: COLORS.red, op: tradeOp},
          {p: levels.entry, txt: `Entry ${levels.entry}`, c: COLORS.white, op: tradeOp},
          {p: levels.POC, txt: `POC ${levels.POC}`, c: COLORS.grey, op: detailOp},
          {p: levels.nPOC, txt: `nPOC · TP ${levels.nPOC}`, c: COLORS.cyan, op: Math.max(npocOp, tradeOp)},
        ].map((L, k) => (
          <g key={k} opacity={L.op}>
            <rect x={PROF_RIGHT - 158} y={yOf(L.p) - 15} width={158} height={26} rx={5}
              fill={COLORS.black} opacity={0.8} />
            <text x={PROF_RIGHT - 150} y={yOf(L.p) + 4} fill={L.c}
              fontFamily="Tajawal, monospace" fontWeight={700} fontSize={19}>{L.txt}</text>
          </g>
        ))}

        {/* zone labels (latin/number-safe; Arabic zone words handled in captions) */}
        <text x={AREA_X + 10} y={yOf(levels.wallHi) - 8} fill={COLORS.teal}
          fontFamily="Tajawal" fontWeight={700} fontSize={20} opacity={zonesOp}>HVN — الحافة</text>
        <text x={AREA_X + 10} y={yOf((levels.lvnLo + levels.lvnHi) / 2) + 6} fill={COLORS.cyan}
          fontFamily="Tajawal" fontWeight={700} fontSize={22} opacity={zonesOp}
          filter="url(#glow)">LVN — الفراغ</text>
      </g>
    </svg>
  );
};
