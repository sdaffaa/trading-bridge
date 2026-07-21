import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring} from 'remotion';
import {Particles, GlowPulse} from '../../components/Overlays';
import {KineticText, Diamond} from '../shared';
import {TEAL} from '../data';

export const Closing: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const brand = spring({frame, fps, delay: 150, config: {damping: 20}});
  const lineW = interpolate(frame, [70, 110], [0, 320], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{backgroundColor: '#03060b'}}>
      <AbsoluteFill style={{background: 'radial-gradient(70% 50% at 50% 42%, rgba(8,20,30,0.6), rgba(3,6,11,1))'}} />
      <GlowPulse cx={540} cy={860} />
      <Particles n={20} seed="closing" />

      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', gap: 8}}>
        <KineticText text="الصفقة الناجحة لا تبدأ بالدخول" size={64} weight={800} color="#e9f7fa" delay={10} />
        <div style={{height: 18}} />
        <KineticText text="تبدأ بالانتظار" size={104} weight={900} delay={44} glowColor="rgba(79,208,224,0.6)" />
        <div
          style={{
            marginTop: 30,
            width: lineW,
            height: 4,
            background: `linear-gradient(90deg, rgba(79,208,224,0), ${TEAL}, rgba(79,208,224,0))`,
            borderRadius: 2,
          }}
        />
      </AbsoluteFill>

      {/* brand mark */}
      <div
        style={{
          position: 'absolute',
          bottom: 190,
          left: 0,
          right: 0,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          gap: 18,
          opacity: interpolate(brand, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(brand, [0, 1], [16, 0])}px)`,
        }}
      >
        <Diamond size={12} />
        <div style={{fontFamily: 'Tajawal', fontWeight: 600, fontSize: 34, letterSpacing: 8, color: 'rgba(200,225,235,0.92)'}}>LIQUIDITY STATE</div>
        <Diamond size={12} />
      </div>
    </AbsoluteFill>
  );
};
