import React from 'react';
import {AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, spring} from 'remotion';
import {Particles, GlowPulse, LightSweep} from '../components/Overlays';
import {KineticText, BottomCaption, Diamond} from '../trade/shared';
import {CandleChart} from './Candles';
import {Footprint, DeltaReadout} from './Footprint';
import {SCENES, SWEEP_IDX, CLOSES, STOP_PRICE, TEAL, RED, GREEN} from './data';

const bg = '#04070d';

// helper: windowed opacity
const win = (f: number, a: number, b: number, c: number, d: number) =>
  interpolate(f, [a, b, c, d], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

// 1) BLACK HOOK
export const BlackHook: React.FC = () => {
  const frame = useCurrentFrame();
  const flash = interpolate(frame, [0, 5, 16], [0.4, 0.14, 0], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <AbsoluteFill style={{background: `radial-gradient(70% 45% at 50% 48%, rgba(255,70,85,${flash}) 0%, rgba(0,0,0,0) 70%)`}} />
      <Particles n={10} seed="bh" />
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', padding: '0 70px'}}>
        <KineticText text="هذي لحظة انضرب فيها ستوبك" size={82} weight={900} delay={2} stagger={2} glowColor="rgba(255,91,106,0.5)" />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// 2) CHART + STOP CLUSTER
export const ChartLow: React.FC = () => {
  const frame = useCurrentFrame();
  const d = SCENES.chartLow;
  const scale = interpolate(frame, [0, d], [1.02, 1.12], {extrapolateRight: 'clamp'});
  const labOp = interpolate(frame, [40, 60], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{backgroundColor: bg}}>
      <AbsoluteFill style={{background: 'radial-gradient(90% 70% at 50% 40%, rgba(8,16,26,0.5), rgba(3,6,11,0.96))'}} />
      <Particles n={10} seed="cl" />
      <div style={{position: 'absolute', top: 520, left: 80, width: 940, transform: `scale(${scale})`, transformOrigin: '50% 60%'}}>
        <CandleChart revealStart={6} revealEnd={70} toIndex={SWEEP_IDX} showStop stopPrice={STOP_PRICE} />
      </div>
      {/* stop cluster label */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 1310, display: 'flex', justifyContent: 'center', opacity: labOp}}>
        <div dir="rtl" style={{fontFamily: 'Tajawal', fontWeight: 800, fontSize: 40, color: RED, padding: '10px 28px', borderRadius: 10, background: 'rgba(20,6,8,0.7)', border: `1px solid rgba(255,91,106,0.5)`}}>
          تحت هالقاع… آلاف الستوبات
        </div>
      </div>
      <BottomCaption text="تحت القاع… آلاف الستوبات. منها ستوبك" delay={10} size={54} />
    </AbsoluteFill>
  );
};

// 3) FOOTPRINT — sweep + absorption (beats 3+4)
export const FootprintScene: React.FC = () => {
  const frame = useCurrentFrame();
  const flipAt = 190;
  const zoom = interpolate(frame, [0, 40, 320], [0.86, 0.98, 1.06], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{backgroundColor: bg}}>
      <AbsoluteFill style={{background: 'radial-gradient(90% 70% at 50% 42%, rgba(8,16,26,0.5), rgba(3,6,11,0.97))'}} />
      <Particles n={10} seed="fp" />

      {/* title */}
      <div style={{position: 'absolute', top: 130, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
        <div dir="rtl" style={{fontFamily: 'Tajawal', fontWeight: 800, fontSize: 44, color: '#e9f7fa'}}>الفوت برنت لحظة السويب</div>
      </div>
      {/* PAUSED badge (phase A) */}
      <div style={{position: 'absolute', top: 210, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: win(frame, 20, 40, 150, 175)}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 12, padding: '8px 22px', borderRadius: 8, background: 'rgba(8,14,22,0.8)', border: `1px solid ${TEAL}`}}>
          <div style={{display: 'flex', gap: 5}}><div style={{width: 7, height: 22, background: TEAL}} /><div style={{width: 7, height: 22, background: TEAL}} /></div>
          <div style={{fontFamily: 'Tajawal', fontWeight: 700, fontSize: 26, color: TEAL, letterSpacing: 2}}>PAUSED</div>
        </div>
      </div>

      {/* ladder */}
      <div style={{position: 'absolute', top: 320, left: 0, right: 0, display: 'flex', justifyContent: 'center', transform: `scale(${zoom})`, transformOrigin: '50% 30%'}}>
        <Footprint revealStart={24} revealEnd={130} highlight={frame >= 150} />
      </div>

      {/* delta readout */}
      <div style={{position: 'absolute', top: 980, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: interpolate(frame, [110, 140], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
        <DeltaReadout flipAt={flipAt} />
      </div>

      {/* captions (two phases) */}
      <div style={{position: 'absolute', left: 60, right: 60, top: 1662, display: 'flex', justifyContent: 'center', opacity: win(frame, 30, 52, 150, 172)}}>
        <KineticText text="كسر القاع… اقرأ الأرقام معي" size={54} weight={800} delay={34} />
      </div>
      <div style={{position: 'absolute', left: 60, right: 60, top: 1662, display: 'flex', justifyContent: 'center', opacity: win(frame, 176, 200, 315, 320)}}>
        <KineticText text="بيع ضخم والسعر ما ينزل — هذا امتصاص مو دعم" size={48} weight={800} delay={180} glowColor="rgba(79,208,224,0.5)" />
      </div>
      {/* bottom bar scrim */}
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: 360, background: 'linear-gradient(180deg, rgba(4,7,13,0) 0%, rgba(4,7,13,0.9) 55%, #04070d 100%)'}} />
    </AbsoluteFill>
  );
};

// 4) EXPLOSION — price rips up, stop left behind
export const Explosion: React.FC = () => {
  const frame = useCurrentFrame();
  const flash = interpolate(frame, [0, 10, 30], [0.0, 0.22, 0], {extrapolateRight: 'clamp'});
  const scale = interpolate(frame, [0, SCENES.explosion], [1.14, 1.02], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{backgroundColor: bg}}>
      <AbsoluteFill style={{background: 'radial-gradient(90% 70% at 50% 45%, rgba(8,20,16,0.5), rgba(3,6,11,0.96))'}} />
      <AbsoluteFill style={{background: `radial-gradient(70% 50% at 50% 55%, rgba(57,217,138,${flash}) 0%, rgba(0,0,0,0) 70%)`}} />
      <Particles n={12} seed="ex" />
      <LightSweep />
      <div style={{position: 'absolute', top: 470, left: 80, width: 940, transform: `scale(${scale})`, transformOrigin: '55% 60%'}}>
        <CandleChart revealStart={4} revealEnd={64} toIndex={CLOSES.length - 1} showStop stopPrice={STOP_PRICE} glowRally />
      </div>
      <BottomCaption text="انضرب ستوبك… ودخلوا هم بسيولتك" delay={8} size={56} emphasis />
    </AbsoluteFill>
  );
};

// 5) CTA
export const CTA: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const chip = spring({frame, fps, delay: 70, config: {damping: 18}});
  return (
    <AbsoluteFill style={{backgroundColor: '#03060b'}}>
      <AbsoluteFill style={{background: 'radial-gradient(70% 50% at 50% 42%, rgba(8,20,30,0.6), rgba(3,6,11,1))'}} />
      <GlowPulse cx={540} cy={820} />
      <Particles n={20} seed="cta" />
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', gap: 12, padding: '0 70px'}}>
        <KineticText text="ما كان حظ سيء" size={58} weight={800} color="#e9f7fa" delay={6} />
        <KineticText text="كان نموذج عمل… وأنت الوقود" size={74} weight={900} delay={24} glowColor="rgba(79,208,224,0.55)" />
      </AbsoluteFill>
      {/* CTA chip */}
      <div style={{position: 'absolute', bottom: 470, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: interpolate(chip, [0, 1], [0, 1]), transform: `translateY(${interpolate(chip, [0, 1], [24, 0])}px)`}}>
        <div dir="rtl" style={{display: 'flex', alignItems: 'center', gap: 14, padding: '20px 40px', borderRadius: 100, background: 'rgba(8,14,22,0.95)', border: `2px solid ${TEAL}`, boxShadow: `0 0 30px rgba(79,208,224,0.3)`}}>
          <div style={{fontFamily: 'Tajawal', fontWeight: 800, fontSize: 46, color: '#f2fbfd'}}>
            اكتب <span style={{color: TEAL}}>«سيولة»</span> ويوصلك الـ PDF
          </div>
        </div>
      </div>
      <div style={{position: 'absolute', bottom: 180, left: 0, right: 0, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 16}}>
        <Diamond size={12} />
        <div style={{fontFamily: 'Tajawal', fontWeight: 600, fontSize: 34, letterSpacing: 8, color: 'rgba(200,225,235,0.92)'}}>LIQUIDITY STATE</div>
        <Diamond size={12} />
      </div>
    </AbsoluteFill>
  );
};
