import React from 'react';
import {Composition} from 'remotion';
import {Reel} from './Reel';
import {FPS, totalFrames} from './data';
import {TradeReel} from './trade/TradeReel';
import {totalTradeFrames} from './trade/data';
import {AbsorptionReel} from './absorption/AbsorptionReel';
import {totalAbsFrames} from './absorption/data';
import {StopHuntReel} from './stophunt/StopHuntReel';
import {totalStopFrames} from './stophunt/data';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="Reel"
      component={Reel}
      durationInFrames={totalFrames}
      fps={FPS}
      width={1080}
      height={1920}
    />
    <Composition
      id="AbsorptionReel"
      component={AbsorptionReel}
      durationInFrames={totalAbsFrames}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="StopHuntReel"
      component={StopHuntReel}
      durationInFrames={totalStopFrames}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="TradeReel"
      component={TradeReel}
      durationInFrames={totalTradeFrames}
      fps={30}
      width={1080}
      height={1920}
    />
  </>
);
