import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig, interpolate, spring} from 'remotion';
import {Particles, GlowPulse} from '../../components/Overlays';
import {BrandChip, KineticText} from '../shared';
import {TEAL} from '../data';

const ROWS = [
  {n: 1, title: 'السويب', sub: 'كسر السيولة أسفل القاع'},
  {n: 2, title: 'تأكيد فوت برنت', sub: 'امتصاص ضغط البيع'},
  {n: 3, title: 'الدخول ضد السويب', sub: 'مع أول انعكاس مؤكَّد'},
];

const Row: React.FC<{n: number; title: string; sub: string; delay: number}> = ({n, title, sub, delay}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame, fps, delay, config: {damping: 17, mass: 0.8}});
  const x = interpolate(s, [0, 1], [80, 0]);
  const op = interpolate(s, [0, 1], [0, 1]);
  const check = spring({frame, fps, delay: delay + 16, config: {damping: 14}});
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'row-reverse',
        alignItems: 'center',
        gap: 30,
        width: 900,
        padding: '26px 34px',
        borderRadius: 22,
        background: 'linear-gradient(90deg, rgba(10,18,28,0.9), rgba(8,14,22,0.6))',
        border: `1px solid rgba(79,208,224,0.28)`,
        boxShadow: '0 10px 40px rgba(0,0,0,0.5)',
        transform: `translateX(${x}px)`,
        opacity: op,
      }}
    >
      {/* number chip */}
      <div
        style={{
          width: 92,
          height: 92,
          borderRadius: 20,
          background: `radial-gradient(circle at 30% 25%, rgba(79,208,224,0.35), rgba(8,20,28,0.9))`,
          border: `2px solid ${TEAL}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontFamily: 'Tajawal',
          fontWeight: 900,
          fontSize: 52,
          color: '#eafcff',
          boxShadow: `0 0 22px rgba(79,208,224,0.4)`,
          flexShrink: 0,
        }}
      >
        {n}
      </div>
      {/* texts */}
      <div dir="rtl" style={{flex: 1, textAlign: 'right'}}>
        <div style={{fontFamily: 'Tajawal', fontWeight: 800, fontSize: 50, color: '#f2fbfd'}}>{title}</div>
        <div style={{fontFamily: 'Tajawal', fontWeight: 500, fontSize: 32, color: 'rgba(160,190,205,0.9)', marginTop: 4}}>{sub}</div>
      </div>
      {/* check */}
      <svg width="60" height="60" style={{flexShrink: 0}}>
        <circle cx="30" cy="30" r="26" fill="none" stroke={TEAL} strokeOpacity={0.5} strokeWidth={2} />
        <path
          d="M18 31 L27 40 L44 21"
          fill="none"
          stroke={TEAL}
          strokeWidth={4}
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeDasharray={44}
          strokeDashoffset={interpolate(check, [0, 1], [44, 0])}
          style={{filter: `drop-shadow(0 0 6px ${TEAL})`}}
        />
      </svg>
    </div>
  );
};

export const Conditions: React.FC = () => {
  return (
    <AbsoluteFill style={{backgroundColor: '#04070d'}}>
      {/* clean tech grid background */}
      <AbsoluteFill
        style={{
          backgroundImage:
            'linear-gradient(rgba(79,208,224,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(79,208,224,0.05) 1px, transparent 1px)',
          backgroundSize: '72px 72px',
          maskImage: 'radial-gradient(80% 70% at 50% 45%, black 30%, transparent 85%)',
          WebkitMaskImage: 'radial-gradient(80% 70% at 50% 45%, black 30%, transparent 85%)',
        }}
      />
      <AbsoluteFill style={{background: 'radial-gradient(90% 70% at 50% 40%, rgba(6,14,22,0.3), rgba(3,6,11,0.9))'}} />
      <GlowPulse cx={540} cy={980} />
      <Particles n={16} seed="cond" />

      <BrandChip delay={6} />

      <AbsoluteFill style={{top: 360, justifyContent: 'flex-start', alignItems: 'center'}}>
        <KineticText text="3 شروط دخلنا فيها" size={78} weight={900} delay={10} glowColor="rgba(79,208,224,0.4)" />
      </AbsoluteFill>

      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', gap: 34, top: 120}}>
        <Row n={ROWS[0].n} title={ROWS[0].title} sub={ROWS[0].sub} delay={54} />
        <Row n={ROWS[1].n} title={ROWS[1].title} sub={ROWS[1].sub} delay={150} />
        <Row n={ROWS[2].n} title={ROWS[2].title} sub={ROWS[2].sub} delay={246} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
