# Liquidity State — Reels (1080×1920)

Professional vertical reel built from 10 designed slides: Ken Burns motion,
crossfade transitions, animated Arabic captions (RTL-correct), progress counter,
and an offline-synthesized cinematic ambient music bed.

## Pipeline
1. `make_captions.py`  — renders per-slide caption overlays (PIL + libraqm, raw RTL text).
2. `build_segments.py` — Ken Burns zoom per slide + static caption overlay → `segments/`.
3. `make_music.py`     — offline cinematic ambient bed (ffmpeg synthesis).
4. `assemble.py`       — xfade-concat segments + mux music → `output/`.

## Rebuild
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install arabic-reshaper python-bidi Pillow
python3 make_captions.py && python3 build_segments.py
python3 make_music.py 40.9 && python3 assemble.py
```

## Notes
- Source slides: `final/p01.png … p10.png` (page order 1–10).
- No neural voiceover: all cloud TTS hosts are blocked by the session network
  policy, so the reel is caption-driven. Provide an audio file to add a synced VO.

Final output: `output/reels_LiquidityState.mp4` — 1080×1920 · 30fps · ~41s · AAC 48k stereo.
