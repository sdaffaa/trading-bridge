import React from 'react';
import {useCurrentFrame, useVideoConfig, interpolate, spring} from 'remotion';
import {TEAL} from './data';
import {FONT} from '../fonts';

// RTL-correct kinetic Arabic line with per-word stagger.
export const KineticText: React.FC<{
  text: string;
  size?: number;
  weight?: number;
  color?: string;
  delay?: number;
  stagger?: number;
  shadow?: boolean;
  glowColor?: string;
}> = ({text, size = 72, weight = 800, color = '#f2fbfd', delay = 0, stagger = 3, shadow = true, glowColor}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const words = text.split(' ');
  return (
    <div
      dir="rtl"
      style={{
        direction: 'rtl',
        fontFamily: FONT,
        fontWeight: weight,
        fontSize: size,
        color,
        lineHeight: 1.28,
        textAlign: 'center',
        textShadow: shadow ? '0 3px 18px rgba(0,0,0,0.7)' : 'none',
        maxWidth: 940,
      }}
    >
      {words.map((w, i) => {
        const s = spring({frame, fps, delay: delay + i * stagger, config: {damping: 18, mass: 0.5}});
        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              marginInlineStart: i === 0 ? 0 : 18,
              opacity: interpolate(s, [0, 1], [0, 1]),
              transform: `translateY(${interpolate(s, [0, 1], [26, 0])}px)`,
              filter: glowColor ? `drop-shadow(0 0 14px ${glowColor})` : 'none',
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};

// Brand chip top ("Liquidity State")
export const BrandChip: React.FC<{delay?: number}> = ({delay = 0}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame, fps, delay, config: {damping: 20}});
  return (
    <div
      style={{
        position: 'absolute',
        top: 96,
        left: 0,
        right: 0,
        display: 'flex',
        justifyContent: 'center',
        opacity: interpolate(s, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(s, [0, 1], [-14, 0])}px)`,
      }}
    >
      <div
        style={{
          padding: '12px 40px',
          border: `1px solid rgba(79,208,224,0.5)`,
          borderRadius: 6,
          color: 'rgba(200,225,235,0.9)',
          fontFamily: FONT,
          fontWeight: 500,
          fontSize: 30,
          letterSpacing: 6,
          background: 'rgba(6,12,20,0.35)',
          boxShadow: `0 0 20px rgba(79,208,224,0.12)`,
        }}
      >
        LIQUIDITY&nbsp;&nbsp;STATE
      </div>
    </div>
  );
};

// count-up number
export const useCountUp = (to: number, dur: number, delay = 0, decimals = 0) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [delay, delay + dur], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const eased = 1 - Math.pow(1 - p, 3);
  return (to * eased).toFixed(decimals);
};

export const Diamond: React.FC<{size?: number; color?: string}> = ({size = 12, color = TEAL}) => (
  <div style={{width: size, height: size, background: color, transform: 'rotate(45deg)', boxShadow: `0 0 8px ${color}`, flexShrink: 0}} />
);

// Opaque lower-third caption bar (keeps MY narration off the chart's own text).
export const BottomCaption: React.FC<{
  text: string;
  delay?: number;
  size?: number;
  color?: string;
  emphasis?: boolean;
}> = ({text, delay = 4, size = 60, color = '#f2fbfd', emphasis}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame, fps, delay, config: {damping: 18, mass: 0.7}});
  return (
    <>
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          bottom: 0,
          height: 430,
          background:
            'linear-gradient(180deg, rgba(3,6,11,0) 0%, rgba(3,6,11,0.72) 26%, rgba(3,6,11,0.96) 52%, #03060b 100%)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: 70,
          right: 70,
          top: 1560,
          height: 2,
          background: 'linear-gradient(90deg, rgba(79,208,224,0) 0%, rgba(79,208,224,0.55) 50%, rgba(79,208,224,0) 100%)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: 60,
          right: 60,
          top: 1660,
          display: 'flex',
          justifyContent: 'center',
          opacity: interpolate(s, [0, 1], [0, 1]),
          transform: `translateY(${interpolate(s, [0, 1], [30, 0])}px)`,
        }}
      >
        <KineticText
          text={text}
          size={size}
          weight={emphasis ? 900 : 800}
          color={color}
          delay={delay + 6}
          glowColor={emphasis ? 'rgba(79,208,224,0.5)' : undefined}
        />
      </div>
    </>
  );
};
