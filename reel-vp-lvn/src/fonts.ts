import {continueRender, delayRender} from 'remotion';
import {TAJAWAL_BOLD, TAJAWAL_MEDIUM, TAJAWAL_REGULAR} from './fontData';

let injected = false;
export function useTajawal() {
  if (typeof document === 'undefined') return;
  if (!injected) {
    injected = true;
    const css = `
      @font-face{font-family:'Tajawal';font-weight:700;font-style:normal;src:url(${TAJAWAL_BOLD}) format('woff');font-display:block;}
      @font-face{font-family:'Tajawal';font-weight:500;font-style:normal;src:url(${TAJAWAL_MEDIUM}) format('woff');font-display:block;}
      @font-face{font-family:'Tajawal';font-weight:400;font-style:normal;src:url(${TAJAWAL_REGULAR}) format('woff');font-display:block;}
    `;
    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
  }
  const handle = delayRender('tajawal');
  Promise.all([
    (document as any).fonts.load('700 100px Tajawal'),
    (document as any).fonts.load('500 100px Tajawal'),
    (document as any).fonts.load('400 100px Tajawal'),
  ])
    .then(() => (document as any).fonts.ready)
    .then(() => continueRender(handle))
    .catch(() => continueRender(handle));
}
