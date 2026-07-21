import React from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame, interpolate} from 'remotion';
import {TransitionSeries, springTiming, linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {slide} from '@remotion/transitions/slide';
import {wipe} from '@remotion/transitions/wipe';
import {SLIDES, TRANSITION, totalFrames} from './data';
import {Scene} from './components/Scene';
import './fonts';

const transitionFor = (i: number) => {
  const mod = i % 3;
  if (mod === 0) return {presentation: slide({direction: 'from-bottom'}), timing: springTiming({config: {damping: 200}, durationInFrames: TRANSITION})};
  if (mod === 1) return {presentation: fade(), timing: linearTiming({durationInFrames: TRANSITION})};
  return {presentation: wipe({direction: 'from-right'}), timing: linearTiming({durationInFrames: TRANSITION})};
};

export const Reel: React.FC = () => {
  const frame = useCurrentFrame();
  // global fade in/out
  const vig = interpolate(
    frame,
    [0, 14, totalFrames - 16, totalFrames],
    [0, 1, 1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );

  return (
    <AbsoluteFill style={{backgroundColor: '#03060b'}}>
      <AbsoluteFill style={{opacity: vig}}>
        <TransitionSeries>
          {SLIDES.map((s, i) => (
            <React.Fragment key={s.page}>
              <TransitionSeries.Sequence durationInFrames={s.dur}>
                <Scene slide={s} />
              </TransitionSeries.Sequence>
              {i < SLIDES.length - 1 ? (
                <TransitionSeries.Transition {...transitionFor(i)} />
              ) : null}
            </React.Fragment>
          ))}
        </TransitionSeries>
      </AbsoluteFill>
      <Audio src={staticFile('music/bed.wav')} volume={0.9} />
    </AbsoluteFill>
  );
};
