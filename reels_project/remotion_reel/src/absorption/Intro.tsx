import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig, interpolate, spring} from 'remotion';
import {Particles, GlowPulse} from '../components/Overlays';
import {FONT_PLEX} from '../fonts';
import {TEAL} from './data';

// Kinetic RTL line in IBM Plex Sans Arabic (has چ).
const PlexLine: React.FC<{text: string; size: number; weight: number; color: string; delay: number; glow?: boolean}> = ({text, size, weight, color, delay, glow}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const words = text.split(' ');
  return (
    <div dir="rtl" style={{direction: 'rtl', fontFamily: FONT_PLEX, fontWeight: weight, fontSize: size, color, textAlign: 'center', lineHeight: 1.3, maxWidth: 960, textShadow: '0 3px 20px rgba(0,0,0,0.7)'}}>
      {words.map((w, i) => {
        const s = spring({frame, fps, delay: delay + i * 2, config: {damping: 16, mass: 0.4}});
        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              marginInlineStart: i === 0 ? 0 : 16,
              opacity: interpolate(s, [0, 1], [0, 1]),
              transform: `translateY(${interpolate(s, [0, 1], [24, 0])}px)`,
              filter: glow ? `drop-shadow(0 0 16px ${TEAL})` : 'none',
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};

export const Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const flash = interpolate(frame, [0, 6, 16], [0.5, 0.2, 0], {extrapolateRight: 'clamp'});
  const line = interpolate(frame, [30, 52], [0, 340], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{backgroundColor: '#03060b'}}>
      {/* blurred chart texture (no readable text), slowly drifting */}
      <AbsoluteFill style={{opacity: 0.16, transform: `scale(${1.15 + 0.05 * Math.sin(frame / 40)}) translateY(${interpolate(frame, [0, 72], [30, -30])}px)`}}>
        <Img src={staticFile('absorption/s1.png')} style={{width: 1080, height: 1920, objectFit: 'cover', filter: 'blur(14px)'}} />
      </AbsoluteFill>
      <AbsoluteFill style={{background: 'radial-gradient(75% 55% at 50% 45%, rgba(8,20,30,0.5), rgba(3,6,11,0.96))'}} />
      <GlowPulse cx={540} cy={880} />
      <Particles n={20} seed="intro" />
      {/* entry flash */}
      <AbsoluteFill style={{background: `radial-gradient(70% 45% at 50% 45%, rgba(79,208,224,${flash}) 0%, rgba(79,208,224,0) 70%)`}} />

      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', gap: 14, padding: '0 60px'}}>
        <PlexLine text="راح تبلش تربح" size={104} weight={700} color="#f2fbfd" delay={4} glow />
        <PlexLine text="إذا عرفت اللي قاعد يصير ورا الچارت" size={56} weight={600} color="#bfeaf1" delay={16} />
        <div style={{marginTop: 26, width: line, height: 4, background: `linear-gradient(90deg, rgba(79,208,224,0), ${TEAL}, rgba(79,208,224,0))`, borderRadius: 2}} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
