import React from 'react';
import {interpolate, Easing} from 'remotion';
import {COLORS} from './theme';

type Cap = {t0: number; t1: number; text: string; size: number; color: string; stamp?: boolean};
const CAPS: Cap[] = [
  {t0: 0.3, t1: 3.0, text: 'الفراغ مو دعم', size: 104, color: COLORS.white},
  {t0: 3.0, t1: 4.6, text: 'دعم؟ لا… منزلق', size: 72, color: COLORS.grey},
  {t0: 4.6, t1: 5.4, text: 'شلون؟', size: 116, color: COLORS.cyan, stamp: true},
  {t0: 6.8, t1: 10.0, text: 'ماكو فوليوم = رخيص؟', size: 66, color: COLORS.grey},
  {t0: 10.0, t1: 13.2, text: 'الفوليوم الخفيف = سرعة نزول', size: 62, color: COLORS.cyan},
  {t0: 13.2, t1: 14.8, text: 'الفراغ ياخذ فلوسك', size: 96, color: COLORS.white, stamp: true},
  {t0: 14.8, t1: 18.6, text: 'بعت من الحافة  ←  POC  ·  +4.5R', size: 60, color: COLORS.teal},
  {t0: 18.6, t1: 19.8, text: 'الستوب فوق الفوليوم الثقيل', size: 60, color: COLORS.white},
  {t0: 19.8, t1: 22.0, text: 'اكتب «بروفايل» بالتعليقات', size: 70, color: COLORS.gold},
];

export const Captions: React.FC<{t: number}> = ({t}) => {
  const active = CAPS.find((c) => t >= c.t0 && t < c.t1);
  if (!active) return null;
  const lt = t - active.t0;
  const rem = active.t1 - t;

  let transform = '';
  let opacity = 1;
  let clip = 'none';
  if (active.stamp) {
    const sc = interpolate(lt, [0, 0.09], [1.14, 1.0], {extrapolateRight: 'clamp', easing: Easing.out(Easing.ease)});
    transform = `scale(${sc})`;
    opacity = interpolate(lt, [0, 0.06], [0, 1], {extrapolateRight: 'clamp'});
  } else {
    const y = interpolate(lt, [0, 0.27], [22, 0], {extrapolateRight: 'clamp', easing: Easing.out(Easing.ease)});
    transform = `translateY(${y}px)`;
    opacity = interpolate(lt, [0, 0.22], [0, 1], {extrapolateRight: 'clamp'});
    // mask-wipe R→L reveal
    const rev = interpolate(lt, [0.02, 0.34], [100, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
    clip = `inset(0 0 0 ${rev}%)`;
  }
  // fade out last 0.18s
  opacity *= interpolate(rem, [0, 0.18], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <div style={{position: 'absolute', left: 40, right: 40, top: 1430, display: 'flex', justifyContent: 'center'}}>
      <div style={{
        direction: 'rtl', fontFamily: 'Tajawal', fontWeight: 700, fontSize: active.size,
        lineHeight: 1.25, color: active.color, textAlign: 'center', transform, opacity,
        clipPath: clip as any, WebkitClipPath: clip as any,
        textShadow: '0 3px 22px rgba(0,0,0,0.85)', maxWidth: 980,
      }}>
        {active.text}
      </div>
    </div>
  );
};
