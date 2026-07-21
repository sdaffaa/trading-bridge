import React from 'react';
import {AbsoluteFill, useCurrentFrame, interpolate} from 'remotion';
import {Particles} from '../../components/Overlays';
import {BrandChip, KineticText, useCountUp} from '../shared';
import {TEAL, RED, GREEN, TRADE} from '../data';

// hand-crafted close path: downtrend -> sweep low -> reversal to target
const CLOSES = [
  2376, 2372, 2374, 2368, 2365, 2367, 2361, 2358, 2360, 2354,
  2350, 2352, 2347, 2344, 2346, 2342, 2345, 2341, 2344, /* sweep idx 19 */ 2343,
  2347, 2351, 2349, 2355, 2360, 2358, 2364, 2369, 2367, 2373, 2378,
];
const SWEEP_IDX = 19; // candle with long lower wick (liquidity grab)

const PMAX = 2383, PMIN = 2333;
const CW = 880, CH = 560, CX0 = 20, CY0 = 12;
const yOf = (p: number) => CY0 + ((PMAX - p) / (PMAX - PMIN)) * CH;

type Candle = {o: number; h: number; l: number; c: number};
const buildCandles = (): Candle[] =>
  CLOSES.map((c, i) => {
    const prev = i === 0 ? c + 2 : CLOSES[i - 1];
    const o = prev;
    let h = Math.max(o, c) + 1.4;
    let l = Math.min(o, c) - 1.4;
    if (i === SWEEP_IDX) l = 2337.2; // sweep spike below the stop
    return {o, h, l, c};
  });

const Line: React.FC<{price: number; color: string; label: string; op: number; dash?: boolean}> = ({price, color, label, op, dash}) => {
  const y = yOf(price);
  return (
    <g opacity={op}>
      <line x1={CX0} y1={y} x2={CX0 + CW} y2={y} stroke={color} strokeWidth={2.5} strokeDasharray={dash ? '10 8' : undefined} style={{filter: `drop-shadow(0 0 5px ${color})`}} />
      <rect x={CX0 + CW - 210} y={y - 21} width={200} height={42} rx={8} fill={color} opacity={0.16} />
      <text x={CX0 + CW - 110} y={y + 8} textAnchor="middle" fontFamily="Tajawal" fontWeight={800} fontSize={24} fill={color}>
        {label}
      </text>
    </g>
  );
};

export const Execution: React.FC = () => {
  const frame = useCurrentFrame();
  const candles = buildCandles();
  const n = candles.length;
  const visible = interpolate(frame, [12, 185], [0, n], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const cw = (CW / n) * 0.6;

  const linesOp = interpolate(frame, [150, 180], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const cardOp = interpolate(frame, [200, 226], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const cardY = interpolate(frame, [200, 226], [30, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const result = useCountUp(TRADE.resultPips, 70, 236, 0);

  return (
    <AbsoluteFill style={{backgroundColor: '#04070d'}}>
      <AbsoluteFill style={{background: 'radial-gradient(90% 70% at 50% 34%, rgba(8,16,26,0.5), rgba(3,6,11,0.96))'}} />
      <Particles n={12} seed="exec" />
      <BrandChip delay={6} />

      <AbsoluteFill style={{top: 300, justifyContent: 'flex-start', alignItems: 'center'}}>
        <KineticText text="تطبيق حي على الصفقة" size={58} weight={800} delay={8} color="#bfeaf1" />
      </AbsoluteFill>

      {/* candlestick chart */}
      <div style={{position: 'absolute', top: 470, left: 90, width: 900, height: 600}}>
        <svg width={920} height={CH + 24} style={{overflow: 'visible'}}>
          {/* grid */}
          {[2340, 2350, 2360, 2370, 2380].map((p) => (
            <g key={p}>
              <line x1={CX0} y1={yOf(p)} x2={CX0 + CW} y2={yOf(p)} stroke="rgba(120,150,170,0.12)" strokeWidth={1} />
              <text x={CX0 + CW + 6} y={yOf(p) + 7} fontFamily="Tajawal" fontSize={20} fill="rgba(140,165,180,0.6)">{p}</text>
            </g>
          ))}
          {candles.map((cd, i) => {
            if (i >= visible) return null;
            const appear = interpolate(visible - i, [0, 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
            const x = CX0 + (i + 0.5) * (CW / n);
            const up = cd.c >= cd.o;
            const isSweep = i === SWEEP_IDX;
            const col = isSweep ? RED : up ? GREEN : '#c9d6de';
            const bodyTop = yOf(Math.max(cd.o, cd.c));
            const bodyBot = yOf(Math.min(cd.o, cd.c));
            return (
              <g key={i} opacity={appear}>
                <line x1={x} y1={yOf(cd.h)} x2={x} y2={yOf(cd.l)} stroke={col} strokeWidth={2} />
                <rect x={x - cw / 2} y={bodyTop} width={cw} height={Math.max(2, bodyBot - bodyTop)} fill={col} rx={1.5}
                  style={isSweep ? {filter: `drop-shadow(0 0 6px ${RED})`} : undefined} />
              </g>
            );
          })}
          {/* sweep marker */}
          {visible > SWEEP_IDX + 1 ? (
            <g opacity={interpolate(frame, [120, 150], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}>
              <text x={CX0 + (SWEEP_IDX + 0.5) * (CW / n) - 26} y={yOf(2337.2) + 40} fontFamily="Tajawal" fontWeight={800} fontSize={24} fill={RED}>SWEEP</text>
            </g>
          ) : null}
          <Line price={TRADE.entry} color={TEAL} label={`دخول ${TRADE.entry.toFixed(1)}`} op={linesOp} />
          <Line price={TRADE.stop} color={RED} label={`وقف ${TRADE.stop.toFixed(1)}`} op={linesOp} dash />
          <Line price={TRADE.target} color={GREEN} label={`هدف ${TRADE.target.toFixed(1)}`} op={linesOp} dash />
        </svg>
      </div>

      {/* result card */}
      <div style={{position: 'absolute', left: 90, right: 90, top: 1230, opacity: cardOp, transform: `translateY(${cardY}px)`}}>
        <div style={{display: 'flex', gap: 20, justifyContent: 'center'}}>
          <Stat label="المخاطرة" value={`${(TRADE.entry - TRADE.stop).toFixed(0)} نقطة`} color="#c9d6de" />
          <Stat label="العائد / المخاطرة" value={TRADE.rr} color={TEAL} />
        </div>
        <div
          style={{
            marginTop: 22,
            padding: '30px 20px',
            borderRadius: 24,
            background: 'linear-gradient(180deg, rgba(20,40,32,0.7), rgba(8,18,14,0.6))',
            border: `2px solid rgba(57,217,138,0.6)`,
            boxShadow: '0 0 40px rgba(57,217,138,0.2)',
            textAlign: 'center',
          }}
        >
          <div dir="rtl" style={{fontFamily: 'Tajawal', fontWeight: 600, fontSize: 34, color: 'rgba(180,210,195,0.9)'}}>النتيجة</div>
          <div style={{fontFamily: 'Tajawal', fontWeight: 900, fontSize: 96, color: GREEN, textShadow: `0 0 24px rgba(57,217,138,0.5)`, direction: 'ltr'}}>
            +{result} <span style={{fontSize: 44}}>نقطة</span>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const Stat: React.FC<{label: string; value: string; color: string}> = ({label, value, color}) => (
  <div style={{flex: 1, padding: '18px 20px', borderRadius: 18, background: 'rgba(10,18,28,0.8)', border: '1px solid rgba(79,208,224,0.22)', textAlign: 'center'}}>
    <div dir="rtl" style={{fontFamily: 'Tajawal', fontWeight: 500, fontSize: 28, color: 'rgba(160,190,205,0.85)'}}>{label}</div>
    <div dir="rtl" style={{fontFamily: 'Tajawal', fontWeight: 800, fontSize: 44, color, marginTop: 4}}>{value}</div>
  </div>
);
