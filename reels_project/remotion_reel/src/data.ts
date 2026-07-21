export type Slide = {
  page: number;
  img: string;
  caption: string;
  dur: number; // frames
  zoomIn: boolean;
  // approx crystal center (in 1080x1920 space) for glow/ring anchoring
  cx: number;
  cyGlow: number;
  cyRing: number;
};

// Ken Burns alternates; glow/ring anchored near each slide's crystal.
export const SLIDES: Slide[] = [
  {page: 1,  img: 'slides/p01.png', caption: 'متى يجب أن تبتعد عن الجارت؟',   dur: 150, zoomIn: true,  cx: 540, cyGlow: 1430, cyRing: 1560},
  {page: 2,  img: 'slides/p02.png', caption: 'بعد 3 خسائر متتالية… ابتعد',    dur: 135, zoomIn: false, cx: 540, cyGlow: 1180, cyRing: 1300},
  {page: 3,  img: 'slides/p03.png', caption: 'لا تتداول انتقامًا من الخسارة', dur: 135, zoomIn: true,  cx: 540, cyGlow: 1330, cyRing: 1450},
  {page: 4,  img: 'slides/p04.png', caption: 'ما في Setup واضح؟ لا تدخل',      dur: 135, zoomIn: false, cx: 540, cyGlow: 1300, cyRing: 1420},
  {page: 5,  img: 'slides/p05.png', caption: 'الملل يصنع صفقات عشوائية',       dur: 135, zoomIn: true,  cx: 540, cyGlow: 1250, cyRing: 1380},
  {page: 6,  img: 'slides/p06.png', caption: 'متعب أو مشتت؟ ابتعد',           dur: 135, zoomIn: false, cx: 540, cyGlow: 1330, cyRing: 1450},
  {page: 7,  img: 'slides/p07.png', caption: 'قبل الأخبار القوية… راقب فقط',  dur: 135, zoomIn: true,  cx: 540, cyGlow: 1230, cyRing: 1360},
  {page: 8,  img: 'slides/p08.png', caption: 'كسرت خطتك؟ اخرج فورًا',          dur: 135, zoomIn: false, cx: 540, cyGlow: 1300, cyRing: 1420},
  {page: 9,  img: 'slides/p09.png', caption: 'بعد ربح كبير… خذ استراحة',       dur: 135, zoomIn: true,  cx: 540, cyGlow: 1260, cyRing: 1390},
  {page: 10, img: 'slides/p10.png', caption: 'الجودة قبل عدد الصفقات',         dur: 160, zoomIn: false, cx: 540, cyGlow: 1300, cyRing: 1420},
];

export const TRANSITION = 18; // frames overlap
export const FPS = 30;
export const TEAL = '#4fd0e0';

export const totalFrames =
  SLIDES.reduce((s, x) => s + x.dur, 0) - TRANSITION * (SLIDES.length - 1);
