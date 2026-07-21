import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame, interpolate} from 'remotion';
import type {Slide} from '../data';
import {GlowPulse, RadarRing, Particles, LightSweep} from './Overlays';
import {Caption} from './Caption';

export const Scene: React.FC<{slide: Slide}> = ({slide}) => {
  const frame = useCurrentFrame();
  const d = slide.dur;

  // Ken Burns: continuous scale + slow drift; alternate direction.
  const s0 = slide.zoomIn ? 1.06 : 1.15;
  const s1 = slide.zoomIn ? 1.15 : 1.06;
  const scale = interpolate(frame, [0, d], [s0, s1], {extrapolateRight: 'clamp'});
  const driftY = interpolate(frame, [0, d], [slide.zoomIn ? -14 : 14, slide.zoomIn ? 14 : -14], {extrapolateRight: 'clamp'});
  const driftX = interpolate(frame, [0, d], [8, -8], {extrapolateRight: 'clamp'}) * (slide.page % 2 ? 1 : -1);

  return (
    <AbsoluteFill style={{backgroundColor: '#03060b'}}>
      {/* moving image */}
      <AbsoluteFill style={{transform: `scale(${scale}) translate(${driftX}px, ${driftY}px)`, transformOrigin: '50% 46%'}}>
        <Img src={staticFile(slide.img)} style={{width: 1080, height: 1920, objectFit: 'cover'}} />
      </AbsoluteFill>

      {/* motion-graphic layers anchored to the crystal */}
      <RadarRing cx={slide.cx} cy={slide.cyRing} />
      <GlowPulse cx={slide.cx} cy={slide.cyGlow} />
      <Particles n={22} seed={`p${slide.page}`} />
      <LightSweep />

      {/* subtle top vignette for depth */}
      <AbsoluteFill
        style={{
          background: 'radial-gradient(120% 60% at 50% 40%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.35) 100%)',
          pointerEvents: 'none',
        }}
      />

      <Caption text={slide.caption} page={slide.page} />
    </AbsoluteFill>
  );
};
