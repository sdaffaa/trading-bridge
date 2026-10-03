# Scheduling & reliability — triggers and the envelope

An automation is only as good as the envelope around the agent loop: how it's
triggered, how it survives failure, and whether you can see what it did.

## Triggers — pick by how the event arrives

| Trigger | Use for | In this repo |
|---|---|---|
| **HTTP webhook** (push) | Events another system emits: TradingView alerts, broker fills | The Flask `/webhook` in `tv_claude_bridge.py` |
| **Cron / schedule** (poll) | Heartbeats, periodic scans, end-of-session summaries | Add a scheduler (systemd timer, cron, or an in-process scheduler) that calls the runtime |
| **Queue message** | Decoupling bursts, retries, back-pressure | Enqueue alerts, workers run the agent |
| **Manual** | Backfills, testing a single event | Run `agent_runtime.py` on one payload |

**The webhook must not block or `sleep`-poll.** Validate, enqueue or spawn the
run, and return `200` fast. A long agent loop inside the request times out the
caller and drops retries on the floor. If you keep it inline for simplicity,
still bound it with a hard timeout and return promptly.

## Validate the trigger at the door

Before the agent sees anything, schema-check the payload and reject
out-of-policy events — this is your first and cheapest guardrail:

```python
def validate_alert(data: dict) -> dict:
    sym = data.get("symbol")
    if sym not in ALLOWED_SYMBOLS:
        raise Reject(f"symbol not allowed: {sym}")
    if data.get("action") not in {"buy", "sell", "info"}:
        raise Reject("bad action")
    return {"symbol": sym, "action": data["action"], "price": float(data["price"]),
            "id": data.get("id") or hashlib.sha256(
                json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]}
```

The derived `id` is your **idempotency key** for the whole run.

## The reliability envelope

Wrap every run with:

- **Idempotency key per event** — dedupe replays end-to-end (a store of processed
  keys), and pass the key into act tools so they no-op on repeat.
- **Retry with backoff on *transient* failures only** — network errors, 429, 5xx.
  The Anthropic SDK already retries these (`max_retries`, default 2); add your own
  around the *whole run* if a step past the model call can fail. Do **not** retry
  4xx (bad request) or a completed act — retrying a placed order is a double
  trade. Backoff: `2s, 4s, 8s, 16s`, capped.
- **Hard timeout** on the run so a stuck agent can't hang a worker; also cap loop
  iterations (see `agent-loop.md`).
- **Kill switch check** before every act tool (see `tools-and-guardrails.md`).

## Observability — one structured line per step

You cannot operate what you cannot see. Emit **structured (JSON) logs**, not bare
prints:

- one line per **tool call** (name, args summary, ok/error, duration),
- one line per **decision** (action, confidence, reason, event id),
- one line per **act** (what was done, or "dry-run: would have …", idempotency key).

Include the event id and a run id on every line so you can reconstruct a single
run. The bridge currently `print()`s; upgrade to JSON logs keyed by event id so
runs are traceable and alert-able. Consider mirroring decisions to Telegram so a
human sees what the agent concluded even when acting is disabled.

## Putting it together (per event)

```
receive → validate (reject bad) → dedupe on id (skip if seen)
        → run agent loop (Tool Runner, timeout, iteration cap)
        → agent calls read tools freely, act tools gated
        → submit_decision → gated act (dry-run/kill-switch/caps/idempotent)
        → log decision + act (JSON, keyed by id) → mark id processed → return 200
```

Ship it with `AGENT_DRY_RUN=1`, watch several real events flow through the logs,
confirm the decisions and the *would-have* acts look right, then enable live
acting one tool at a time.
