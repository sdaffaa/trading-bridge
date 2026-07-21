import React from 'react';
import {useCurrentFrame, interpolate} from 'remotion';
import {CLOSES, SWEEP_IDX, TEAL, RED, GREEN} from './data';

const PMAX = 2389, PMIN = 2327;
const CW = 900, CH = 780, CX0 = 20, CY0 = 10;
const yOf = (p: number) => CY0 + ((PMAX - p) / (PMAX - PMIN)) * CH;

type C = {o: number; h: number; l: number; c: number};
export const buildCandles = (): C[] =>
  CLOSES.map((c, i) => {
    const o = i === 0 ? c + 2 : CLOSES[i - 1];
    let h = Math.max(o, c) + 1.3;
    let l = Math.min(o, c) - 1.3;
    if (i === SWEEP_IDX) l = 2331.6;
    return {o, h, l, c};
  });

export const CandleChart: React.FC<{
  revealStart: number;
  revealEnd: number;
  toIndex: number;         // max candle index to allow
  showStop?: boolean;
  stopPrice?: number;
  glowRally?: boolean;
}> = ({revealStart, revealEnd, toIndex, showStop, stopPrice, glowRally}) => {
  const frame = useCurrentFrame();
  const candles = buildCandles();
  const n = candles.length;
  const visF = interpolate(frame, [revealStart, revealEnd], [0, toIndex + 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const cw = (CW / n) * 0.58;

  return (
    <svg width={940} height={CH + 20} style={{overflow: 'visible'}}>
      {[2335, 2345, 2355, 2365, 2375, 2385].map((p) => (
        <g key={p}>
          <line x1={CX0} y1={yOf(p)} x2={CX0 + CW} y2={yOf(p)} stroke="rgba(120,150,170,0.1)" strokeWidth={1} />
          <text x={CX0 + CW + 8} y={yOf(p) + 7} fontFamily="Tajawal" fontSize={20} fill="rgba(140,165,180,0.55)">{p}</text>
        </g>
      ))}
      {showStop && stopPrice ? (
        <g>
          <line x1={CX0} y1={yOf(stopPrice)} x2={CX0 + CW} y2={yOf(stopPrice)} stroke={RED} strokeWidth={2} strokeDasharray="10 8" style={{filter: `drop-shadow(0 0 6px ${RED})`}} />
          <rect x={CX0} y={yOf(stopPrice)} width={CW} height={yOf(PMIN) - yOf(stopPrice)} fill={RED} opacity={0.07} />
        </g>
      ) : null}
      {candles.map((cd, i) => {
        if (i >= Math.min(visF, toIndex + 1)) return null;
        const appear = interpolate(visF - i, [0, 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        const x = CX0 + (i + 0.5) * (CW / n);
        const up = cd.c >= cd.o;
        const isSweep = i === SWEEP_IDX;
        const col = isSweep ? RED : up ? GREEN : '#c6d3db';
        const bt = yOf(Math.max(cd.o, cd.c));
        const bb = yOf(Math.min(cd.o, cd.c));
        const rally = glowRally && i > SWEEP_IDX && up;
        return (
          <g key={i} opacity={appear}>
            <line x1={x} y1={yOf(cd.h)} x2={x} y2={yOf(cd.l)} stroke={col} strokeWidth={2} />
            <rect x={x - cw / 2} y={bt} width={cw} height={Math.max(2, bb - bt)} fill={col} rx={1.5}
              style={rally ? {filter: `drop-shadow(0 0 7px ${GREEN})`} : isSweep ? {filter: `drop-shadow(0 0 7px ${RED})`} : undefined} />
          </g>
        );
      })}
    </svg>
  );
};
