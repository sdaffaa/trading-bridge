import React from 'react';
import {useCurrentFrame, interpolate} from 'remotion';
import {FOOT, SWEEP_ROWS, TEAL, RED, GREEN} from './data';

const ROW_H = 76;
const MAXV = 631;

// Animated footprint ladder: [sell | price | buy] per level.
export const Footprint: React.FC<{
  revealStart: number;   // frame numbers appear
  revealEnd: number;
  highlight: boolean;    // box + glow the sweep zone
}> = ({revealStart, revealEnd, highlight}) => {
  const frame = useCurrentFrame();
  const n = FOOT.length;
  const vis = interpolate(frame, [revealStart, revealEnd], [0, n], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const W = 760;
  const cx = W / 2;
  const pulse = 0.5 + 0.5 * Math.sin(frame / 8);

  return (
    <svg width={W} height={n * ROW_H + 10} style={{overflow: 'visible', fontFamily: 'Tajawal'}}>
      {highlight ? (
        <rect
          x={-6}
          y={SWEEP_ROWS[0] * ROW_H - 4}
          width={W + 12}
          height={SWEEP_ROWS.length * ROW_H + 8}
          rx={14}
          fill="rgba(255,91,106,0.06)"
          stroke={RED}
          strokeOpacity={0.5 + 0.4 * pulse}
          strokeWidth={2.5}
          style={{filter: `drop-shadow(0 0 ${10 + 10 * pulse}px rgba(255,91,106,0.5))`}}
        />
      ) : null}
      {FOOT.map((r, i) => {
        const shown = i < vis;
        const ap = interpolate(vis - i, [0, 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        const y = i * ROW_H + ROW_H / 2;
        const sellW = (r.s / MAXV) * (cx - 90);
        const buyW = (r.b / MAXV) * (cx - 90);
        const inZone = SWEEP_ROWS.includes(i);
        return (
          <g key={i} opacity={shown ? ap : 0}>
            {/* sell bar (left) */}
            <rect x={cx - 74 - sellW} y={y - 24} width={sellW} height={48} rx={4} fill={RED} opacity={inZone ? 0.85 : 0.4} />
            <text x={cx - 84} y={y + 9} textAnchor="end" fontWeight={inZone ? 800 : 600} fontSize={inZone ? 34 : 27} fill={inZone ? '#ff9aa4' : 'rgba(255,140,150,0.8)'}>{r.s}</text>
            {/* price center */}
            <rect x={cx - 62} y={y - 26} width={124} height={52} rx={7} fill="rgba(10,18,28,0.85)" stroke="rgba(120,150,170,0.25)" />
            <text x={cx} y={y + 8} textAnchor="middle" fontWeight={700} fontSize={26} fill="#dfe9ee">{r.p}</text>
            {/* buy bar (right) */}
            <rect x={cx + 74} y={y - 24} width={buyW} height={48} rx={4} fill={GREEN} opacity={0.5} />
            <text x={cx + 84} y={y + 9} textAnchor="start" fontWeight={600} fontSize={27} fill="rgba(120,230,170,0.85)">{r.b}</text>
          </g>
        );
      })}
    </svg>
  );
};

// Big delta readout that flips from heavy-negative to an absorption/reversal state.
export const DeltaReadout: React.FC<{flipAt: number}> = ({flipAt}) => {
  const frame = useCurrentFrame();
  const val = interpolate(frame, [0, flipAt - 10], [0, -1920], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const flipped = frame >= flipAt;
  const flipS = interpolate(frame, [flipAt, flipAt + 14], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, fontFamily: 'Tajawal'}}>
      <div style={{fontSize: 30, fontWeight: 600, color: 'rgba(160,185,200,0.85)', letterSpacing: 2}}>DELTA</div>
      {!flipped ? (
        <div style={{fontSize: 84, fontWeight: 900, color: RED, textShadow: `0 0 20px rgba(255,91,106,0.5)`}}>
          {(val / 1000).toFixed(2)}K
        </div>
      ) : (
        <div style={{display: 'flex', alignItems: 'center', gap: 14, opacity: flipS, transform: `scale(${0.8 + 0.2 * flipS})`}}>
          <div style={{fontSize: 64, fontWeight: 900, color: GREEN, textShadow: `0 0 22px rgba(57,217,138,0.6)`}}>▲ امتصاص</div>
        </div>
      )}
    </div>
  );
};
