import React from 'react';
import {Composition} from 'remotion';
import {VPReel} from './VPReel';
import {FPS, DURATION_S, W, H, s} from './theme';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="VPReel"
        component={VPReel}
        durationInFrames={s(DURATION_S)}
        fps={FPS}
        width={W}
        height={H}
        defaultProps={{withVO: false}}
      />
      <Composition
        id="VPReelVO"
        component={VPReel}
        durationInFrames={s(DURATION_S)}
        fps={FPS}
        width={W}
        height={H}
        defaultProps={{withVO: true}}
      />
    </>
  );
};
