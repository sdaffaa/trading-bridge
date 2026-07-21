import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring} from 'remotion';
import {TEAL, FONT} from '../data';

const Diamond: React.FC = () => (
  <div
    style={{
      width: 12,
      height: 12,
      background: TEAL,
      transform: 'rotate(45deg)',
      boxShadow: `0 0 8px ${TEAL}`,
      flexShrink: 0,
    }}
  />
);

export const Caption: React.FC<{text: string; page: number}> = ({text, page}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const enter = spring({frame, fps, delay: 5, config: {damping: 16, mass: 0.7}});
  const pillY = interpolate(enter, [0, 1], [46, 0]);
  const pillOp = interpolate(enter, [0, 1], [0, 1]);

  const words = text.split(' ');

  return (
    <AbsoluteFill>
      {/* opaque lower-third bar hides the slide's own bottom line */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          bottom: 0,
          height: 430,
          background:
            'linear-gradient(180deg, rgba(3,6,11,0) 0%, rgba(3,6,11,0.75) 26%, rgba(3,6,11,0.97) 55%, #03060b 100%)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          left: 90,
          right: 90,
          top: 1497,
          height: 2,
          background:
            'linear-gradient(90deg, rgba(79,208,224,0) 0%, rgba(79,208,224,0.5) 50%, rgba(79,208,224,0) 100%)',
        }}
      />

      {/* caption pill */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: 1656,
          display: 'flex',
          justifyContent: 'center',
          transform: `translateY(${pillY}px)`,
          opacity: pillOp,
        }}
      >
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 16,
            padding: '20px 42px',
            borderRadius: 100,
            background: 'rgba(8,14,22,0.96)',
            border: '2px solid rgba(79,208,224,0.7)',
            boxShadow: '0 0 30px rgba(79,208,224,0.25), inset 0 0 20px rgba(79,208,224,0.05)',
          }}
        >
          <Diamond />
          <div
            dir="rtl"
            style={{
              fontFamily: FONT,
              fontWeight: 800,
              fontSize: 56,
              color: '#f0fafc',
              whiteSpace: 'nowrap',
              direction: 'rtl',
              textAlign: 'center',
            }}
          >
            {words.map((w, i) => {
              const ws = spring({frame, fps, delay: 12 + i * 3, config: {damping: 18, mass: 0.5}});
              return (
                <span
                  key={i}
                  style={{
                    display: 'inline-block',
                    marginInlineStart: i === 0 ? 0 : 16,
                    opacity: interpolate(ws, [0, 1], [0, 1]),
                    transform: `translateY(${interpolate(ws, [0, 1], [18, 0])}px)`,
                  }}
                >
                  {w}
                </span>
              );
            })}
          </div>
          <Diamond />
        </div>
      </div>

      {/* counter + progress ticks */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: 1808,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 12,
          opacity: pillOp,
        }}
      >
        <div style={{fontFamily: FONT, fontWeight: 500, fontSize: 30, color: 'rgba(160,185,200,0.92)', letterSpacing: 2}}>
          {page} / 10
        </div>
        <div style={{display: 'flex', gap: 8}}>
          {Array.from({length: 10}).map((_, i) => {
            const active = i + 1 <= page;
            const isCurrent = i + 1 === page;
            const glow = isCurrent ? 0.6 + 0.4 * Math.abs(Math.sin(frame / 12)) : 0;
            return (
              <div
                key={i}
                style={{
                  width: 34,
                  height: 5,
                  borderRadius: 3,
                  background: active ? TEAL : 'rgba(60,78,90,0.9)',
                  boxShadow: isCurrent ? `0 0 ${8 * glow}px ${TEAL}` : 'none',
                }}
              />
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
