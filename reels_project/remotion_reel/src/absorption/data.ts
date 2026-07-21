export const FPS = 30;
export const TEAL = '#4fd0e0';
export const RED = '#ff5b6a';
export const TRANS = 15;

export type KB = {s0: number; s1: number; x0: number; x1: number; y0: number; y1: number; ox?: string; oy?: string};
export type Beat = {a: number; b: number; c: number; d: number; text: string; size: number; emph?: boolean};

export type AScene = {
  page: number;
  img: string;
  dur: number;
  kb: KB;
  beats: Beat[];
  bar: boolean;   // show bottom caption bar
  kind?: 'wall' | 'chart' | 'signs' | 'shield' | 'hook';
};

export const SCENES: AScene[] = [
  {
    page: 1, img: 'absorption/s1.png', dur: 150, bar: true, kind: 'hook',
    kb: {s0: 1.15, s1: 1.30, x0: 0, x1: 0, y0: -58, y1: 78},
    beats: [{a: 14, b: 38, c: 146, d: 150, text: 'وفجأة وقف… مو لأن البيع خلص', size: 52, emph: true}],
  },
  {
    page: 2, img: 'absorption/s2.png', dur: 610, bar: true, kind: 'wall',
    kb: {s0: 1.15, s1: 1.42, x0: -20, x1: 24, y0: -34, y1: 40, oy: '55%'},
    beats: [
      {a: 10, b: 34, c: 150, d: 172, text: 'تخيّل واحد يدز جدار', size: 62, emph: true},
      {a: 172, b: 196, c: 312, d: 334, text: 'يدز ويدز… والجدار ما يتحرك', size: 54},
      {a: 334, b: 358, c: 470, d: 492, text: 'هذا هو الامتصاص', size: 72, emph: true},
      {a: 492, b: 516, c: 600, d: 610, text: 'مشتري كبير يستقبل كل البيع', size: 50},
    ],
  },
  {
    page: 3, img: 'absorption/s3.png', dur: 480, bar: true, kind: 'signs',
    kb: {s0: 1.22, s1: 1.26, x0: 0, x1: 0, y0: 150, y1: -190},
    beats: [
      {a: 10, b: 34, c: 122, d: 144, text: '3 علامات تكشف الامتصاص', size: 58, emph: true},
      {a: 144, b: 168, c: 250, d: 272, text: '1) حجم عالي عند المستوى', size: 52},
      {a: 272, b: 296, c: 372, d: 394, text: '2) دلتا سالبة… والشمعة ما تكسر', size: 46},
      {a: 394, b: 418, c: 470, d: 480, text: '3) ذيل واضح ورفض للنزول', size: 50},
    ],
  },
  {
    page: 4, img: 'absorption/s4.png', dur: 380, bar: true, kind: 'chart',
    kb: {s0: 1.16, s1: 1.36, x0: 10, x1: -54, y0: 48, y1: -26, oy: '58%'},
    beats: [
      {a: 10, b: 34, c: 150, d: 172, text: 'بيع 4 أضعاف الطبيعي', size: 56, emph: true},
      {a: 172, b: 196, c: 272, d: 294, text: 'والسعر ما نزل ولا نقطة', size: 54},
      {a: 294, b: 318, c: 372, d: 380, text: 'بعد 3 شموع… +40 نقطة', size: 60, emph: true},
    ],
  },
  {
    page: 5, img: 'absorption/s5.png', dur: 240, bar: false, kind: 'shield',
    kb: {s0: 1.26, s1: 1.14, x0: 0, x1: 0, y0: -10, y1: 14},
    beats: [],
  },
];

export const INTRO_DUR = 72;      // ~2s hook card
export const INTRO_TRANS = 12;    // fast fade into scene 1

export const totalAbsFrames =
  INTRO_DUR - INTRO_TRANS + SCENES.reduce((a, s) => a + s.dur, 0) - TRANS * (SCENES.length - 1);
