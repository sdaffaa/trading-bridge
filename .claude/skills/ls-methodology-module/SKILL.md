---
name: ls-methodology-module
description: >-
  Decide WHICH trading methodologies a single Liquidity State piece should use, and how to layer them, so a reel
  or carousel proves one idea with the fewest tools instead of cramming indicators. Use this WHENEVER you're
  planning the analytical content of a piece and choosing between ICT, SMC, Footprint/Order Flow, Volume Profile,
  Volume, or VWAP — e.g. "أي مدرسة أستخدم / ادمج الأدوات / حلل الشارت / نموذج دخول / اختار الهوك / أي أداة تأكيد".
  It sets a primary topic + optional one structure, one context, and one confirmation layer (max three), rejects
  incoherent combos, and supplies the approved hook and keyword-CTA per school. Pair with verified-market-charts
  (real data) and ls-reel-engine (render).
---

# Multi-Methodology Module

Core principle: **a piece doesn't show off how many tools we know — it uses the fewest tools needed to prove one
idea clearly.** Every added tool must answer a *different* question or it gets cut.

## Layer selection
```
PRIMARY_TOPIC      = SMC | ICT | FOOTPRINT | VOLUME_PROFILE | VOLUME | VWAP   (exactly one)
STRUCTURE_METHOD   = NONE | SMC | ICT
CONTEXT_LAYER      = NONE | VOLUME_PROFILE | VWAP
CONFIRMATION_LAYER = NONE | FOOTPRINT | VOLUME
```
One primary + at most one of each other layer → **max three analytical layers** in a piece. Never all six.

## The three questions each layer answers
- **SMC / ICT** → "Where is liquidity, and what is structure/bias?"
- **Volume Profile / VWAP** → "Where is value, and is price accepted or stretched away from it?"
- **Footprint / Volume** → "Did buyers/sellers actually participate?"
If a tool doesn't add a new answer, remove it.

## Valid combos (examples)
- ICT primary + Volume Profile context + Footprint confirmation → sweep → back into value → absorption → entry.
- SMC primary + VWAP context + Volume confirmation → CHoCH → reclaim VWAP → volume expansion on displacement → entry.
- Volume Profile primary + ICT structure → break above VAH → failed acceptance → back into value → POC then VAL.
  (this is the shipped `ls-reel-engine` template.)

## Forbidden
- BOS+CHoCH+FVG+OTE+OrderBlock+VWAP+POC+Delta all in one scene. Footprint "decoration" without real Bid×Ask/Delta.
- Volume Profile without a stated range; VWAP without a session/anchor; Volume without a named source.
- Confirmation tools that conflict, then hiding the conflict.

Full per-school function lists: `references/per-school.md`. Approved hooks + keyword CTAs: `references/hooks-ctas.md`.
Data-accuracy rules for each tool live in the `verified-market-charts` skill (`references/school-data-rules.md`).
