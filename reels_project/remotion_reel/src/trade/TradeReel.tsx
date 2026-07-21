import React from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame, interpolate} from 'remotion';
import {TransitionSeries, springTiming, linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {slide} from '@remotion/transitions/slide';
import {wipe} from '@remotion/transitions/wipe';
import {SCENES, TRANS, totalTradeFrames} from './data';
import {Hook} from './scenes/Hook';
import {Analogy} from './scenes/Analogy';
import {Conditions} from './scenes/Conditions';
import {Execution} from './scenes/Execution';
import {Closing} from './scenes/Closing';
import '../fonts';

export const TradeReel: React.FC = () => {
  const frame = useCurrentFrame();
  const vig = interpolate(
    frame,
    [0, 14, totalTradeFrames - 18, totalTradeFrames],
    [0, 1, 1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );
  return (
    <AbsoluteFill style={{backgroundColor: '#03060b'}}>
      <AbsoluteFill style={{opacity: vig}}>
        <TransitionSeries>
          <TransitionSeries.Sequence durationInFrames={SCENES.hook}>
            <Hook />
          </TransitionSeries.Sequence>
          <TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames: TRANS})} />

          <TransitionSeries.Sequence durationInFrames={SCENES.analogy}>
            <Analogy />
          </TransitionSeries.Sequence>
          <TransitionSeries.Transition presentation={slide({direction: 'from-right'})} timing={springTiming({config: {damping: 200}, durationInFrames: TRANS})} />

          <TransitionSeries.Sequence durationInFrames={SCENES.conditions}>
            <Conditions />
          </TransitionSeries.Sequence>
          <TransitionSeries.Transition presentation={wipe({direction: 'from-bottom'})} timing={linearTiming({durationInFrames: TRANS})} />

          <TransitionSeries.Sequence durationInFrames={SCENES.execution}>
            <Execution />
          </TransitionSeries.Sequence>
          <TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames: TRANS})} />

          <TransitionSeries.Sequence durationInFrames={SCENES.closing}>
            <Closing />
          </TransitionSeries.Sequence>
        </TransitionSeries>
      </AbsoluteFill>
      <Audio src={staticFile('music/bed60.wav')} volume={0.85} />
    </AbsoluteFill>
  );
};
