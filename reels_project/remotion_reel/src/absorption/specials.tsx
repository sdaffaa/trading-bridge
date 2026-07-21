import React from 'react';
import {AbsoluteFill, useCurrentFrame, interpolate} from 'remotion';
import {TEAL, RED} from './data';

const softGlow = (x: number, y: number, size: number, color: string, op: number, blur = 10) => (
  <div
    style={{
      position: 'absolute',
      left: x - size / 2,
      top: y - size / 2,
      width: size,
      height: size,
      borderRadius: '50%',
      background: `radial-gradient(circle, ${color} 0%, rgba(0,0,0,0) 68%)`,
      opacity: op,
      filter: `blur(${blur}px)`,
      mixBlendMode: 'screen',
    }}
  />
);

// Scene 2 — red "punches" landing on the wall + blue absorbing shimmer.
export const WallPulse: React.FC = () => {
  const frame = useCurrentFrame();
  const impacts = [790, 930, 1070, 1210, 1350];
  return (
    <AbsoluteFill>
      {impacts.map((y, i) => {
        const ph = (frame * 0.06 + i * 0.9) % (Math.PI * 2);
        const p = Math.max(0, Math.sin(ph));
        return <React.Fragment key={i}>{softGlow(470, y, 150 + 120 * p, `rgba(255,80,95,${0.28 * p})`, 1, 8)}</React.Fragment>;
      })}
      {/* blue absorbing side */}
      {softGlow(610, 1050, 420, `rgba(79,208,224,${0.10 + 0.06 * (0.5 + 0.5 * Math.sin(frame / 14))})`, 1, 14)}
    </AbsoluteFill>
  );
};

// Scene 4 — soft pulse on the absorption low + a glow tracing the rally up-right.
export const RallyGlow: React.FC = () => {
  const frame = useCurrentFrame();
  const lowPulse = 0.5 + 0.5 * Math.sin(frame / 10);
  // rally trace appears late (beat 3 ~ frame 294+)
  const t = interpolate(frame, [294, 350], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const gx = interpolate(t, [0, 1], [560, 760]);
  const gy = interpolate(t, [0, 1], [1170, 760]);
  return (
    <AbsoluteFill>
      {softGlow(545, 1200, 180 + 60 * lowPulse, `rgba(255,80,95,${0.22 * lowPulse})`, 1, 8)}
      {t > 0 ? softGlow(gx, gy, 150, `rgba(79,208,224,${0.5 * t})`, 1, 6) : null}
    </AbsoluteFill>
  );
};
