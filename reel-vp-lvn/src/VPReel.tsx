import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig, Audio, staticFile, interpolate} from 'remotion';
import {COLORS, W, H} from './theme';
import {Chart} from './Chart';
import {Captions} from './Captions';
import {useTajawal} from './fonts';

const Gem: React.FC<{size: number}> = ({size}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <polygon points="50,6 82,32 68,50 32,50 18,32" fill="#D7DEE3" opacity="0.9" />
    <polygon points="32,50 68,50 50,94" fill="#AEBAC1" opacity="0.85" />
    <polygon points="18,32 32,50 50,94" fill="#C6CFD5" opacity="0.6" />
    <polygon points="82,32 68,50 50,94" fill="#9AA7AE" opacity="0.6" />
  </svg>
);

export const VPReel: React.FC<{withVO?: boolean}> = ({withVO = false}) => {
  useTajawal();
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;

  return (
    <AbsoluteFill style={{backgroundColor: COLORS.bgTop}}>
      {/* gradient bg */}
      <AbsoluteFill style={{background: `linear-gradient(160deg, ${COLORS.bgTop} 0%, ${COLORS.bgBot} 55%, #0b1a20 100%)`}} />
      {/* faint HUD grid */}
      <svg width={W} height={H} style={{position: 'absolute', opacity: 0.05}}>
        {Array.from({length: 12}).map((_, i) => (
          <line key={'v' + i} x1={(i * W) / 12} x2={(i * W) / 12} y1={0} y2={H} stroke="#8fd6e0" strokeWidth={1} />
        ))}
        {Array.from({length: 20}).map((_, i) => (
          <line key={'h' + i} x1={0} x2={W} y1={(i * H) / 20} y2={(i * H) / 20} stroke="#8fd6e0" strokeWidth={1} />
        ))}
      </svg>

      {/* top: educational tag */}
      <div style={{position: 'absolute', top: 250, left: 0, right: 0, textAlign: 'center',
        direction: 'rtl', fontFamily: 'Tajawal', fontWeight: 500, fontSize: 30, color: COLORS.grey, letterSpacing: 1}}>
        صفقة موثقة · لغرض تعليمي
      </div>

      {/* chart */}
      <Chart t={t} />

      {/* captions */}
      <Captions t={t} />

      {/* vignette */}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 42%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.42) 100%)', pointerEvents: 'none'}} />

      {/* bottom brand */}
      <div style={{position: 'absolute', bottom: 96, left: 0, right: 0, display: 'flex',
        flexDirection: 'column', alignItems: 'center', gap: 8, opacity: 0.92}}>
        <Gem size={40} />
        <div style={{fontFamily: 'Tajawal', fontWeight: 500, fontSize: 26, color: COLORS.grey}}>@liquidity.state</div>
      </div>

      {/* audio */}
      <Audio src={staticFile('audio/sfx.wav')} volume={(f) => interpolate(f, [0, 10], [0, 0.5], {extrapolateRight: 'clamp'})} />
      {withVO && <Audio src={staticFile('audio/vo.mp3')} volume={1} />}
    </AbsoluteFill>
  );
};
