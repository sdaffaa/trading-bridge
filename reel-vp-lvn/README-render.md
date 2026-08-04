# reel-vp-lvn — كيف تطلّع نسخة بالفويس أوفر

الريل الحالي (out/reel-vp-lvn.mp4) فيه المؤثرات (SFX) + الكابشن + الشارت المتحرك، بدون تعليق صوتي.
الفويس أوفر تولّد بحساب Higgsfield (مدته 26.56s) — نزّله من المعرض.

## باكها الفويس (على جهازك، يحتاج ffmpeg):
1. حمّل الفويس أوفر → خزنه public/audio/vo.mp3
2. نسخة الفيديو بالفويس:  `npx remotion render src/index.ts VPReelVO out/reel-vo.mp4 --crf=18`
3. لأن الفويس 26.56s والريل 22s: إمّا
   - نمدّد الريل (أقولك أعدّل التوقيتات لـ 27s)، أو
   - نسرّع الفويس ليصير 22s:  `ffmpeg -i vo.mp3 -filter:a "atempo=1.207" -ar 48000 public/audio/vo.mp3`
   - ثم ماستر لـ -14 LUFS:  `ffmpeg -i public/audio/vo.mp3 -af "loudnorm=I=-14:TP=-1.2:LRA=9" public/audio/vo_master.wav`
