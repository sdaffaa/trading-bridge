import React from 'react';
import {Composition} from 'remotion';
import {Reel} from './Reel';
import {FPS, totalFrames} from './data';
import {TradeReel} from './trade/TradeReel';
import {totalTradeFrames} from './trade/data';

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
      id="TradeReel"
      component={TradeReel}
      durationInFrames={totalTradeFrames}
      fps={30}
      width={1080}
      height={1920}
    />
  </>
);
