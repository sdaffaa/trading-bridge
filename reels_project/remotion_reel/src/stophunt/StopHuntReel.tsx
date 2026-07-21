import React from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame, interpolate} from 'remotion';
import {TransitionSeries, linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {SCENES, TRANS, totalStopFrames} from './data';
import {BlackHook, ChartLow, FootprintScene, Explosion, CTA} from './scenes';
import '../fonts';

export const StopHuntReel: React.FC = () => {
  const frame = useCurrentFrame();
  const vig = interpolate(frame, [0, 10, totalStopFrames - 12, totalStopFrames], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const tt = () => linearTiming({durationInFrames: TRANS});
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <AbsoluteFill style={{opacity: vig}}>
        <TransitionSeries>
          <TransitionSeries.Sequence durationInFrames={SCENES.black}><BlackHook /></TransitionSeries.Sequence>
          <TransitionSeries.Transition presentation={fade()} timing={tt()} />
          <TransitionSeries.Sequence durationInFrames={SCENES.chartLow}><ChartLow /></TransitionSeries.Sequence>
          <TransitionSeries.Transition presentation={fade()} timing={tt()} />
          <TransitionSeries.Sequence durationInFrames={SCENES.footprint}><FootprintScene /></TransitionSeries.Sequence>
          <TransitionSeries.Transition presentation={fade()} timing={tt()} />
          <TransitionSeries.Sequence durationInFrames={SCENES.explosion}><Explosion /></TransitionSeries.Sequence>
          <TransitionSeries.Transition presentation={fade()} timing={tt()} />
          <TransitionSeries.Sequence durationInFrames={SCENES.cta}><CTA /></TransitionSeries.Sequence>
        </TransitionSeries>
      </AbsoluteFill>
      <Audio src={staticFile('music/bed25.wav')} volume={0.8} />
    </AbsoluteFill>
  );
};
