import React from "react";
import { Composition } from "remotion";
import { Reel, FPS, WIDTH, HEIGHT, RUNTIME_S } from "./Reel";
import { Reel3D } from "./Reel3D";
import { ReelTank } from "./ReelTank";
import { ReelDash } from "./ReelDash";
import { ReelLoop, LOOP_RUNTIME_S } from "./ReelLoop";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="LiquidityStateReelLoop"
        component={ReelLoop}
        durationInFrames={Math.round(LOOP_RUNTIME_S * FPS)}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="LiquidityStateReelDash"
        component={ReelDash}
        durationInFrames={Math.round(RUNTIME_S * FPS)}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="LiquidityStateReelTank"
        component={ReelTank}
        durationInFrames={Math.round(RUNTIME_S * FPS)}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="LiquidityStateReel"
        component={Reel}
        durationInFrames={Math.round(RUNTIME_S * FPS)}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      <Composition
        id="LiquidityStateReel3D"
        component={Reel3D}
        durationInFrames={Math.round(RUNTIME_S * FPS)}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
    </>
  );
};
