import {loadFont} from '@remotion/fonts';
import {staticFile, delayRender, continueRender} from 'remotion';

const handle = delayRender('load-fonts');

Promise.all([
  loadFont({family: 'Tajawal', url: staticFile('fonts/Tajawal-Medium.ttf'), weight: '500'}),
  loadFont({family: 'Tajawal', url: staticFile('fonts/Tajawal-Bold.ttf'), weight: '700'}),
  loadFont({family: 'Tajawal', url: staticFile('fonts/Tajawal-ExtraBold.ttf'), weight: '800'}),
  loadFont({family: 'Tajawal', url: staticFile('fonts/Tajawal-Black.ttf'), weight: '900'}),
  // IBM Plex Sans Arabic — supports چ (Gulf spelling of "chart")
  loadFont({family: 'PlexAr', url: staticFile('fonts/IBMPlexSansArabic-SemiBold.ttf'), weight: '600'}),
  loadFont({family: 'PlexAr', url: staticFile('fonts/IBMPlexSansArabic-Bold.ttf'), weight: '700'}),
])
  .then(() => continueRender(handle))
  .catch(() => continueRender(handle));

export const FONT = 'Tajawal';
export const FONT_PLEX = 'PlexAr';
