import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame, interpolate} from 'remotion';
import {LightSweep, Particles} from '../../components/Overlays';
import {BottomCaption} from '../shared';

export const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  // fast horizontal pan settling — "chart moving fast"
  const panX = interpolate(frame, [0, 40, 150], [150, 12, -26], {extrapolateRight: 'clamp'});
  const scale = interpolate(frame, [0, 150], [1.34, 1.22], {extrapolateRight: 'clamp'});
  const blur = interpolate(frame, [0, 16, 32], [8, 3, 0], {extrapolateRight: 'clamp'});
  const flash = interpolate(frame, [0, 8, 22], [0.45, 0.15, 0], {extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{backgroundColor: '#03060b'}}>
      <AbsoluteFill style={{transform: `scale(${scale}) translateX(${panX}px)`, filter: `blur(${blur}px)`}}>
        <Img src={staticFile('trade/chart.png')} style={{width: 1080, height: 1920, objectFit: 'cover'}} />
      </AbsoluteFill>

      <AbsoluteFill style={{background: `radial-gradient(80% 50% at 50% 45%, rgba(255,60,80,${flash}) 0%, rgba(255,60,80,0) 70%)`}} />
      <Particles n={14} seed="hook" />
      <LightSweep />

      <BottomCaption text="هالصفقة كانت واضحة قبل ما تصير بـ 20 دقيقة" delay={14} size={58} emphasis />
    </AbsoluteFill>
  );
};
