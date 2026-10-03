---
name: liquidity-state-brand
description: >-
  The single source of truth for the Liquidity State brand identity — colors, typography, logo usage, voice & tone, visual system, and audience profile. ALWAYS consult this skill before designing ANY content for the Liquidity State Instagram account (posts, carousels, reels, stories, ads, thumbnails, PDFs, lead magnets) or writing any copy in its voice — even if the user doesn't mention the brand by name. Triggers include: Liquidity State, ليكويدتي ستيت, حساب الانستغرام, تصميم بوست, هوية البراند, البراند, brand colors, أي محتوى للحساب.
---

# Liquidity State — Brand Identity Core

This skill is the **root dependency** of the content system. Every other content skill
(content-writing-engine, carousel-design-pro, reels-design-pipeline, meta-ads-campaigns)
must apply these rules. Never invent new colors, fonts, or tones — everything derives from here.

## 1. Brand Essence

- **Account:** @liquidity.state — Instagram, trading education (faceless charts + voiceover; personal photo only as profile picture)
- **Positioning:** "أرى السوق من منظورات فكرية أخرى" — institutional-grade market reading (Footprint, Order Flow, Liquidity Theory) made simple for Arabic-speaking traders
- **Promise:** "هدفي أخلي التداول سهل للناس 📊"
- **Persona:** Fahad — Kuwaiti trader, calm authority, teacher not hype-seller. Documented trades for education (صفقات موثقة لغرض تعليمي), never signals-selling energy.
- **Business model:** Audience-building → lead magnets (ManyChat) → high-ticket private cohort course ($950–1,500/student; previous sales ~30,000 KWD over 2 years)

## 2. Visual Identity

### Colors (exact system)
| Role | Value | Usage |
|---|---|---|
| Background primary | Dark teal / blue-grey `#0E1E24` → `#12262E` gradient range | All backgrounds |
| Surface / cards | Muted teal `#1B3A45` (accent boxes) | Content boxes, highlight panels |
| Text primary | White `#FFFFFF` | Headlines, body |
| Text secondary | Cool grey `#9FB4BC` | Sub-labels, captions |
| Accent bullish | Teal-green `#2ECC9A` | Buy zones, positive stats, arrows up |
| Accent bearish | Soft red `#E15A5A` | Sell zones, SL, arrows down |
| Metallic accent | Silver/steel gradient | Gem logo, highlight covers, dividers |

Rules: never pure black backgrounds; never neon; charts always brand-styled (dark teal canvas, teal-green/soft-red candles). Geometric/constellation line accents allowed as background texture at low opacity.

### Logo
White faceted icosahedron/gem on the dark-teal background. Placement: bottom-center or bottom-corner watermark on posts/reels; small, never dominating. Highlight covers: darker metallic gem style.

### Typography
- Arabic: **Tajawal** (Bold for headlines, Regular for body). Must render with correct shaping/RTL — apply the `arabic-video-text` skill for any rasterized/video text.
- Numbers & tickers: Latin numerals, Tajawal or a clean geometric sans.
- Hierarchy: one big hook line per screen; max 2 font sizes per slide besides labels.

## 3. Voice & Tone

- **Language:** Kuwaiti/Gulf Arabic for hooks, captions, and voiceover; Modern Standard acceptable for educational definitions; English only for technical terms (Footprint, FVG, Order Flow, POC…).
- **Tone:** confident, direct, zero-hype. Teaches the "why", not just the "what". Uses the confrontational-but-caring hook style (see hook bank in content-writing-engine).
- **Never:** promises of profit, "اربح X% مضمون", lambo culture, signal-group vibes. Always: "لغرض تعليمي".
- **Voiceover:** ElevenLabs brand voice (Brian brand voice, native Kuwaiti-Arabic delivery, 1.1x speed), mastered to **-14 LUFS** for Instagram. Use `arabic-voiceover` + `elevenlabs` skills.
- **Dialect lexicon (نقول / ما نقول)** — always use the left form in on-screen text, captions, and voiceover:
  - إهي ✅ / هي ❌ (the pronoun she/it — do NOT change substrings inside other words like «الجبهية»)
  - تعورك ✅ / توجعك ❌ (to hurt you)
  - صكّر ✅ / اقفل ❌ (close, e.g. صكّر المنصة)

  This list is extensible — when Fahad corrects a word ("احنا نقول X مو Y"), add the pair here.

## 4. Content Pillars (fixed rotation)

1. **تعليم Order Flow / Footprint** — the differentiation pillar (highest saves)
2. **صفقات موثقة** — documented XAUUSD trades (best follow-conversion: 14 follows from one reel)
3. **سيكولوجيا وإدارة رأس المال** — psychology & money management
4. **نماذج الدخول** — entry models (RBR/RDR, sweeps, structure)
5. **Lead magnets** — comment-keyword → ManyChat DM PDF (follow-gated)

## 5. Format DNA (what performs, from real account data)

- **Carousels** = save machines (18 saves / 333 reached) but follower-only reach → use for depth + saves.
- **Reels** = reach machines → must pass the 5-second hook test (account skip rate baseline 66.9%; beat it).
- **Documented-trade reels** = best follow converter → at least 1/week.
- **Comment-keyword CTAs** work strongly (تأمين reel: 11 comments on 61 views) → every educational post gets a keyword.
- Music-only reels without voiceover underperform → default to brand voiceover.

## 6. Standing Reel/Post Structure (adopted method)

1. **0–5s:** counter-expectation hook (الهوك وعد مش خدعة)
2. **5–30s:** tangible visual analogy
3. **30–48s:** rule + numbered framework ("3 نقاط / 3 طرق")
4. **48–64s:** applied live chart examples per point
5. **64–80s:** quotable philosophical reframe
6. **Last seconds:** Save + Share CTA (+ keyword CTA if lead magnet)

Hook types rotation: thought-provoking question / shocking stat / eye-catching chart motion.

## 7. Audience

- Core: Arabic-speaking retail traders (Gulf, Iraq, Maghreb — Iraq/Maghreb are the proven ad-growth geos)
- Level: beginner→intermediate wanting "institutional" edge
- Time zone anchor: Kuwait time for all session/schedule content
