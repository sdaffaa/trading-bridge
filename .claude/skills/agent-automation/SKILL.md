---
name: agent-automation
description: >-
  Build and run autonomous, scheduled, reliable Claude agents that automate a
  pipeline end-to-end — intake an event, reason over it with tools, decide, and
  act (notify / execute / escalate) without a human in the loop for each step.
  Use whenever the task is to design, wire, schedule, or harden an AI agent or a
  multi-agent pipeline: turn a webhook or alert into an automated agent, give an
  agent tools it can call, run an agent on a cron/trigger, make an agent retry
  and stay idempotent, gate its risky actions, log and observe its runs, or
  orchestrate several agents. In this repo that means the trading-bridge flow
  (TradingView alert → analysis agent → decision → Telegram/execution). Also in
  Arabic (أتمتة الايجنتس، وكيل مستقل، شغّل الوكيل تلقائياً، جدولة الوكيل، وكيل
  يحلل ويقرر، خط أنابيب وكلاء، اربط الويبهوك بوكيل، بوابات أمان للوكيل). Owns the
  agent runtime, tooling, scheduling, and reliability; it does NOT do market
  analysis or TradingView UI control (hand those to the methodology and
  tradingview-browse-select skills, which this skill calls as tools).
---

# Agent Automation — autonomous, scheduled, reliable Claude agents

## What this skill is for

Turning a one-shot LLM call into a **standing automation**: an agent that wakes
on an event (webhook, alert, schedule), gathers what it needs through **tools**,
**decides**, and **acts** — repeatably, safely, and observably, without a human
approving every step. In this repo the concrete backbone is `tv_claude_bridge.py`:
a TradingView alert arrives, an agent analyzes it, and the result goes to
Telegram. This skill is how you make that (and pipelines like it) autonomous and
production-worthy instead of a single blocking `messages.create`.

The mental model has four moving parts. Get these right and everything else is
detail:

1. **Trigger** — what starts a run (HTTP webhook, cron, queue message, manual).
2. **Agent loop** — the model calls tools and reads results until it's done. Use
   the SDK **Tool Runner**; don't hand-roll the loop unless you must.
3. **Tools** — the *only* way the agent touches the world. Their shape is your
   security boundary: risky/irreversible actions become gated tools.
4. **Reliability envelope** — retries, idempotency, timeouts, structured logs,
   and a kill switch wrapped around the whole run.

## Prerequisites

```bash
pip install anthropic          # already in requirements.txt for this repo
```

Auth resolves from `ANTHROPIC_API_KEY` (or an `ant auth login` profile) — never
hard-code a key. The runnable runtime is `scripts/agent_runtime.py`; prefer it
over rewriting the loop, and read it before extending — it already encodes the
Tool Runner loop, dry-run gating, retries, and JSON logging described here.

## Model & thinking defaults (this repo)

Default to **`claude-opus-4-8`** with **adaptive thinking** for anything that
reasons or decides. The current bridge pins `claude-sonnet-4-20250514`, which is
**deprecated** — migrate it (see `reference/agent-loop.md` → Model choice). Use
`claude-sonnet-5` or `claude-haiku-4-5` only for cheap, high-volume, low-stakes
steps (e.g. pre-classifying an alert), and say so when you do.

## The build loop (do these in order)

1. **Name the trigger and the terminal action.** "TradingView alert in → a
   graded decision out to Telegram, and nothing sent when the alert is
   malformed." Everything else serves that contract.
2. **List the tools the agent needs** — one per capability, typed inputs, a
   clear "call this when…" description. Separate **read** tools (safe, auto-run)
   from **act** tools (side effects → gated). → `reference/tools-and-guardrails.md`.
3. **Run it with the Tool Runner**, not a manual `while stop_reason` loop. Let
   the SDK drive tool calls; you keep per-turn hooks for approval and logging.
   → `reference/agent-loop.md`.
4. **Wrap the run in the reliability envelope** — idempotency key per event,
   retry with backoff on transient failures, a hard timeout, and one structured
   log line per tool call and per decision. → `reference/scheduling-and-reliability.md`.
5. **Schedule or trigger it** — keep the Flask webhook for push events; add cron
   for polling/heartbeat work. Never `sleep`-poll inside a request.
6. **Ship it in dry-run first.** Every act-tool no-ops and just logs what it
   *would* do until you've watched a few real runs. Flip to live deliberately.

## The non-negotiable: tools are the safety boundary

The agent can only affect the world through the tools you give it, so the tool
surface *is* the policy. Two rules make an autonomous agent safe to leave
running:

- **Split read from act.** Read/analysis tools (fetch a chart, read OHLC,
  compute a level) run automatically. Act tools (send Telegram, place/modify an
  order, delete data) are **irreversible or outward-facing** — gate them: honor
  a global dry-run flag, require a confirmation/allow decision, and make them
  **idempotent** (same event → same effect once, never twice).
- **The model's output is untrusted for side effects.** An alert body, a fetched
  page, or a tool result can try to redirect the agent. Validate at the boundary
  (schema-check the trigger, bound tool arguments) and never let free text alone
  authorize a trade or a broadcast. Detail and patterns:
  `reference/tools-and-guardrails.md`.

## Calling other skills as tools

This skill orchestrates; it doesn't re-implement. Expose the repo's other
capabilities as tools the agent can call:

- **`tradingview-browse-select`** — a tool like `read_chart(symbol, timeframe)`
  drives that skill's `tv_agent.py` to open the chart and read exact OHLC/levels,
  returning structured data to the agent.
- **Methodology skills** (ICT / SMC / volume-profile / footprint) — invoke as a
  sub-analysis step (a subagent or a tool) when the agent needs a graded read of
  a setup. Keep this skill on wiring and reliability; keep *meaning* over there.

## Reference files (read on demand)

- `reference/agent-loop.md` — Tool Runner vs manual loop, `pause_turn`, streaming,
  structured/decision output, model choice, and migrating the bridge's model.
- `reference/tools-and-guardrails.md` — designing tools, read/act split, gating
  irreversible actions, dry-run, idempotency, prompt-injection defense, trading
  safety (position caps, kill switch).
- `reference/scheduling-and-reliability.md` — triggers (webhook/cron/queue),
  retries + backoff, timeouts, idempotency keys, observability, and the
  webhook-doesn't-block rule.

## Guardrails

- **Autonomy is earned.** Start in dry-run, watch real runs, then enable live
  acting one tool at a time. Keep a kill switch (an env flag the runtime checks
  before every act-tool).
- **This is not financial advice and not an auto-trader by default.** Anything
  that places or modifies real orders must be explicitly enabled, capped, and
  idempotent — and is the user's decision to turn on, not this skill's.
- **Never commit secrets.** API keys, Telegram tokens, broker creds → env vars.
- Keep analysis in the analysis skills; this skill owns the machinery.
