import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame, interpolate} from 'remotion';
import {Particles, GlowPulse, LightSweep} from '../components/Overlays';
import {KineticText} from '../trade/shared';
import {TEAL} from './data';
import type {AScene, Beat} from './data';
import {WallPulse, RallyGlow} from './specials';

const CapWin: React.FC<{beat: Beat}> = ({beat}) => {
  const frame = useCurrentFrame();
  const {a, b, c, d, text, size, emph} = beat;
  const op = interpolate(frame, [a, b, c, d], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const ty = interpolate(frame, [a, b], [28, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', left: 60, right: 60, top: 1662, display: 'flex', justifyContent: 'center', opacity: op, transform: `translateY(${ty}px)`}}>
      <KineticText text={text} size={size} weight={emph ? 900 : 800} delay={a + 4} glowColor={emph ? 'rgba(79,208,224,0.5)' : undefined} />
    </div>
  );
};

export const AbsScene: React.FC<{scene: AScene}> = ({scene}) => {
  const frame = useCurrentFrame();
  const {kb, dur} = scene;
  const scale = interpolate(frame, [0, dur], [kb.s0, kb.s1], {extrapolateRight: 'clamp'});
  const tx = interpolate(frame, [0, dur], [kb.x0, kb.x1], {extrapolateRight: 'clamp'});
  const ty = interpolate(frame, [0, dur], [kb.y0, kb.y1], {extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{backgroundColor: '#03060b'}}>
      <AbsoluteFill style={{transform: `scale(${scale}) translate(${tx}px, ${ty}px)`, transformOrigin: `${kb.ox || '50%'} ${kb.oy || '50%'}`}}>
        <Img src={staticFile(scene.img)} style={{width: 1080, height: 1920, objectFit: 'cover'}} />
      </AbsoluteFill>

      {/* per-kind motion */}
      {scene.kind === 'wall' ? <WallPulse /> : null}
      {scene.kind === 'chart' ? <RallyGlow /> : null}
      {scene.kind === 'shield' ? <GlowPulse cx={540} cy={980} /> : null}
      {scene.kind === 'hook' ? <LightSweep /> : null}

      <Particles n={scene.kind === 'shield' ? 22 : 12} seed={`abs${scene.page}`} />

      {/* bottom caption bar */}
      {scene.bar ? (
        <>
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
          {scene.beats.map((bt, i) => (
            <CapWin key={i} beat={bt} />
          ))}
          {/* counter + progress */}
          <div style={{position: 'absolute', left: 0, right: 0, top: 1812, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12}}>
            <div style={{fontFamily: 'Tajawal', fontWeight: 500, fontSize: 30, color: 'rgba(160,185,200,0.9)', letterSpacing: 2}}>{scene.page} / 5</div>
            <div style={{display: 'flex', gap: 10}}>
              {Array.from({length: 5}).map((_, i) => {
                const active = i + 1 <= scene.page;
                const cur = i + 1 === scene.page;
                const glow = cur ? 0.6 + 0.4 * Math.abs(Math.sin(frame / 12)) : 0;
                return <div key={i} style={{width: 58, height: 5, borderRadius: 3, background: active ? TEAL : 'rgba(60,78,90,0.9)', boxShadow: cur ? `0 0 ${8 * glow}px ${TEAL}` : 'none'}} />;
              })}
            </div>
          </div>
        </>
      ) : null}
    </AbsoluteFill>
  );
};
