import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, random} from 'remotion';
import {TEAL} from '../data';

// Pulsing radial glow anchored on the crystal — makes it "breathe".
export const GlowPulse: React.FC<{cx: number; cy: number}> = ({cx, cy}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const pulse = 0.5 + 0.5 * Math.sin(t * Math.PI * 2 * 0.42);
  const op = 0.22 + 0.30 * pulse;
  const size = 520 + 120 * pulse;
  return (
    <AbsoluteFill>
      <div
        style={{
          position: 'absolute',
          left: cx - size / 2,
          top: cy - size / 2,
          width: size,
          height: size,
          borderRadius: '50%',
          background: `radial-gradient(circle, rgba(120,225,240,${op}) 0%, rgba(79,208,224,${op * 0.5}) 32%, rgba(79,208,224,0) 68%)`,
          filter: 'blur(6px)',
          mixBlendMode: 'screen',
        }}
      />
    </AbsoluteFill>
  );
};

// Rotating radar rings at the crystal base (SVG).
export const RadarRing: React.FC<{cx: number; cy: number}> = ({cx, cy}) => {
  const frame = useCurrentFrame();
  const rot = frame * 0.35;
  const rot2 = -frame * 0.22;
  const breathe = 1 + 0.03 * Math.sin(frame / 22);
  const R = 300;
  const ticks = Array.from({length: 48});
  return (
    <AbsoluteFill style={{opacity: 0.5, mixBlendMode: 'screen'}}>
      <svg
        width={R * 2}
        height={R * 2}
        style={{position: 'absolute', left: cx - R, top: cy - R, transform: `scale(${breathe})`}}
      >
        <g transform={`rotate(${rot} ${R} ${R})`}>
          <circle cx={R} cy={R} r={R - 10} fill="none" stroke={TEAL} strokeOpacity={0.35} strokeWidth={1.5} strokeDasharray="2 10" />
          <circle cx={R} cy={R} r={R - 70} fill="none" stroke={TEAL} strokeOpacity={0.25} strokeWidth={1} strokeDasharray="1 14" />
          {ticks.map((_, i) => {
            const a = (i / ticks.length) * Math.PI * 2;
            const r1 = R - 4;
            const r2 = i % 4 === 0 ? R - 22 : R - 12;
            return (
              <line
                key={i}
                x1={R + Math.cos(a) * r1}
                y1={R + Math.sin(a) * r1}
                x2={R + Math.cos(a) * r2}
                y2={R + Math.sin(a) * r2}
                stroke={TEAL}
                strokeOpacity={0.3}
                strokeWidth={1}
              />
            );
          })}
        </g>
        <g transform={`rotate(${rot2} ${R} ${R})`}>
          <circle cx={R} cy={R} r={R - 130} fill="none" stroke={TEAL} strokeOpacity={0.28} strokeWidth={1} strokeDasharray="6 8" />
          {/* sweeping beam */}
          <defs>
            <linearGradient id="beam" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor={TEAL} stopOpacity="0" />
              <stop offset="100%" stopColor={TEAL} stopOpacity="0.5" />
            </linearGradient>
          </defs>
          <path d={`M ${R} ${R} L ${R + (R - 12)} ${R} A ${R - 12} ${R - 12} 0 0 0 ${R + (R - 12) * Math.cos(-0.5)} ${R + (R - 12) * Math.sin(-0.5)} Z`} fill="url(#beam)" opacity={0.25} />
        </g>
      </svg>
    </AbsoluteFill>
  );
};

// Rising particle dots for tech ambiance (deterministic).
export const Particles: React.FC<{n?: number; seed?: string}> = ({n = 22, seed = 's'}) => {
  const frame = useCurrentFrame();
  const {height} = useVideoConfig();
  return (
    <AbsoluteFill style={{mixBlendMode: 'screen'}}>
      {Array.from({length: n}).map((_, i) => {
        const x = random(`${seed}x${i}`) * 1080;
        const speed = 0.5 + random(`${seed}s${i}`) * 1.4;
        const size = 2 + random(`${seed}z${i}`) * 3.5;
        const base = random(`${seed}b${i}`) * height;
        const y = (base - frame * speed * 6) % (height + 200);
        const yy = y < -100 ? y + height + 200 : y;
        const tw = 0.3 + 0.7 * Math.abs(Math.sin((frame + i * 20) / 18));
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x,
              top: yy,
              width: size,
              height: size,
              borderRadius: '50%',
              background: TEAL,
              opacity: tw * 0.5,
              boxShadow: `0 0 ${size * 2}px ${TEAL}`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

// One-shot diagonal light sweep on scene entrance.
export const LightSweep: React.FC = () => {
  const frame = useCurrentFrame();
  const x = interpolate(frame, [0, 26], [-700, 1780], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const op = interpolate(frame, [0, 6, 20, 30], [0, 0.5, 0.5, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{overflow: 'hidden', mixBlendMode: 'screen', opacity: op}}>
      <div
        style={{
          position: 'absolute',
          top: -200,
          left: x,
          width: 260,
          height: 2400,
          transform: 'rotate(18deg)',
          background: 'linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(180,240,250,0.28) 50%, rgba(255,255,255,0) 100%)',
          filter: 'blur(8px)',
        }}
      />
    </AbsoluteFill>
  );
};
