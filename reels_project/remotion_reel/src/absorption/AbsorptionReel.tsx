import React from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame, interpolate} from 'remotion';
import {TransitionSeries, springTiming, linearTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {slide} from '@remotion/transitions/slide';
import {wipe} from '@remotion/transitions/wipe';
import {SCENES, TRANS, INTRO_DUR, INTRO_TRANS, totalAbsFrames} from './data';
import {AbsScene} from './AbsScene';
import {Intro} from './Intro';
import '../fonts';

const trans = (i: number) => {
  const m = i % 3;
  if (m === 0) return {presentation: fade(), timing: linearTiming({durationInFrames: TRANS})};
  if (m === 1) return {presentation: slide({direction: 'from-right'}), timing: springTiming({config: {damping: 200}, durationInFrames: TRANS})};
  return {presentation: wipe({direction: 'from-bottom'}), timing: linearTiming({durationInFrames: TRANS})};
};

export const AbsorptionReel: React.FC = () => {
  const frame = useCurrentFrame();
  const vig = interpolate(frame, [0, 14, totalAbsFrames - 18, totalAbsFrames], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{backgroundColor: '#03060b'}}>
      <AbsoluteFill style={{opacity: vig}}>
        <TransitionSeries>
          <TransitionSeries.Sequence durationInFrames={INTRO_DUR}>
            <Intro />
          </TransitionSeries.Sequence>
          <TransitionSeries.Transition presentation={fade()} timing={linearTiming({durationInFrames: INTRO_TRANS})} />
          {SCENES.map((s, i) => (
            <React.Fragment key={s.page}>
              <TransitionSeries.Sequence durationInFrames={s.dur}>
                <AbsScene scene={s} />
              </TransitionSeries.Sequence>
              {i < SCENES.length - 1 ? <TransitionSeries.Transition {...trans(i)} /> : null}
            </React.Fragment>
          ))}
        </TransitionSeries>
      </AbsoluteFill>
      <Audio src={staticFile('music/bed62.wav')} volume={0.85} />
    </AbsoluteFill>
  );
};
