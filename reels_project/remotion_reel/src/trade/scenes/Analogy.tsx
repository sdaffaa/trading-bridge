import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame, interpolate} from 'remotion';
import {Particles} from '../../components/Overlays';
import {KineticText} from '../shared';
import {TEAL} from '../data';
import {FONT as F} from '../../fonts';

const CapWin: React.FC<{a: number; b: number; c: number; d: number; text: string; size: number; emphasis?: boolean}> = ({a, b, c, d, text, size, emphasis}) => {
  const frame = useCurrentFrame();
  const op = interpolate(frame, [a, b, c, d], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const ty = interpolate(frame, [a, b], [26, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 60, right: 60, top: 1660, display: 'flex', justifyContent: 'center', opacity: op, transform: `translateY(${ty}px)`}}>
      <KineticText text={text} size={size} weight={emphasis ? 900 : 800} delay={a + 4} glowColor={emphasis ? 'rgba(79,208,224,0.5)' : undefined} />
    </div>
  );
};

export const Analogy: React.FC = () => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, 570], [1.12, 1.42], {extrapolateRight: 'clamp'});

  const hx = 518, hy = 1230, hs = 350;
  const boxIn = interpolate(frame, [372, 404], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const pulse = 0.5 + 0.5 * Math.sin(frame / 9);

  return (
    <AbsoluteFill style={{backgroundColor: '#03060b'}}>
      <AbsoluteFill style={{transform: `scale(${scale})`, transformOrigin: '48% 64%'}}>
        <Img src={staticFile('trade/chart.png')} style={{width: 1080, height: 1920, objectFit: 'cover'}} />
      </AbsoluteFill>

      <Particles n={12} seed="analogy" />

      {/* absorption highlight (beat 3) */}
      <AbsoluteFill style={{opacity: boxIn}}>
        <div
          style={{
            position: 'absolute',
            left: hx - hs / 2,
            top: hy - hs / 2,
            width: hs,
            height: hs,
            borderRadius: 22,
            border: `3px solid rgba(79,208,224,${0.55 + 0.4 * pulse})`,
            boxShadow: `0 0 ${26 + 22 * pulse}px rgba(79,208,224,0.55), inset 0 0 40px rgba(79,208,224,0.12)`,
          }}
        />
        <div style={{position: 'absolute', left: 0, right: 0, top: hy - hs / 2 - 78, display: 'flex', justifyContent: 'center'}}>
          <div
            dir="rtl"
            style={{
              fontFamily: F,
              fontWeight: 800,
              fontSize: 38,
              color: TEAL,
              padding: '8px 24px',
              borderRadius: 8,
              background: 'rgba(4,10,16,0.82)',
              border: `1px solid rgba(79,208,224,0.5)`,
              textShadow: '0 0 10px rgba(79,208,224,0.6)',
            }}
          >
            منطقة الامتصاص
          </div>
        </div>
      </AbsoluteFill>

      {/* bottom caption bar */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          bottom: 0,
          height: 430,
          background: 'linear-gradient(180deg, rgba(3,6,11,0) 0%, rgba(3,6,11,0.72) 26%, rgba(3,6,11,0.96) 52%, #03060b 100%)',
        }}
      />
      <div style={{position: 'absolute', left: 70, right: 70, top: 1560, height: 2, background: 'linear-gradient(90deg, rgba(79,208,224,0) 0%, rgba(79,208,224,0.55) 50%, rgba(79,208,224,0) 100%)'}} />

      <CapWin a={8} b={30} c={176} d={196} text="السيولة مثل الطُعم" size={76} emphasis />
      <CapWin a={196} b={218} c={358} d={378} text="السوق ما يتحرك إلا بعد ما ياكله" size={58} />
      <CapWin a={392} b={414} c={560} d={570} text="هنا صار الامتصاص… ثم الانعكاس" size={56} emphasis />
    </AbsoluteFill>
  );
};
