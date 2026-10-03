# The agent loop — Tool Runner, manual loop, output

The agent loop is: model emits tool calls → you execute them → results go back →
repeat until the model stops calling tools. **Use the SDK Tool Runner** to drive
this; only hand-roll the loop when you genuinely need control it doesn't expose.

## Tool Runner (default)

Define tools as decorated functions; the runner calls the API, runs your
functions, feeds results back, and stops when the model is done.

```python
from anthropic import Anthropic, beta_tool

client = Anthropic()

@beta_tool
def read_ohlc(symbol: str, timeframe: str) -> str:
    """Read the latest OHLC for a symbol at a timeframe.

    Call this when you need current price data before judging a setup.
    Args:
        symbol: e.g. "OANDA:XAUUSD".
        timeframe: e.g. "240" (4H), "1D".
    """
    data = fetch_ohlc(symbol, timeframe)   # your implementation
    return json.dumps(data)

runner = client.beta.messages.tool_runner(
    model="claude-opus-4-8",
    max_tokens=16000,
    thinking={"type": "adaptive"},
    tools=[read_ohlc],
    messages=[{"role": "user", "content": "Assess the XAUUSD 4H alert: ..."}],
)

for message in runner:            # each iteration yields the assistant message
    log_turn(message)             # log/inspect before the next tools run
final = message                   # last yielded message is the final answer
```

Why the runner over a manual loop: it removes the boilerplate **and still gives
you per-turn hooks** — you can inspect each yielded assistant message (for
logging or an approval gate) *before* its tools execute, mutate a tool result
before it returns, cap iterations, and stream. "I need to gate a risky tool" is
**not** a reason to drop to a manual loop — gate inside the tool function (return
a "denied" result) or inspect the pending `tool_use` block in the loop body.

## When to use a manual loop

Only when you must own the entire loop: a custom transport, request shapes the
SDK can't build, avoiding the beta dependency, or control flow the per-turn hooks
don't fit. The shape:

```python
messages = [{"role": "user", "content": user_input}]
while True:
    resp = client.messages.create(model="claude-opus-4-8", max_tokens=16000,
                                  tools=tools, messages=messages)
    if resp.stop_reason == "end_turn":
        break
    if resp.stop_reason == "pause_turn":               # server-tool loop paused
        messages = [{"role": "user", "content": user_input},
                    {"role": "assistant", "content": resp.content}]
        continue
    messages.append({"role": "assistant", "content": resp.content})
    results = []
    for b in resp.content:
        if b.type == "tool_use":
            out = execute_tool(b.name, b.input)         # your dispatch
            results.append({"type": "tool_result", "tool_use_id": b.id,
                            "content": out})
    messages.append({"role": "user", "content": results})   # all results, one message
```

Rules that bite if ignored: append the **full** `resp.content` (keep `tool_use`
blocks), return **all** tool results in a **single** user message, each
`tool_result` carries the matching `tool_use_id`, and a failed tool returns a
result with `is_error: True` rather than being dropped. Cap the loop
(`max_continuations`) so a misbehaving agent can't spin forever.

## `pause_turn` (server-side tools)

If the agent uses **server tools** (web search, code execution) the turn can stop
with `stop_reason: "pause_turn"` when the server-side sampling loop hits its
limit — re-send the assistant turn to resume (manual loop above). **The Python
Tool Runner does not auto-resume `pause_turn`** — a paused turn ends the loop and
is returned as the (truncated) final message. If you use server tools with the
runner, mirror the conversation as you iterate and restart the runner with the
paused turn appended, or handle it in a manual loop. For a **custom-tool-only**
agent (the common case here) this never fires.

## Getting a structured decision out

An automation needs a machine-readable verdict, not prose. Two ways:

- **A decision tool the agent must call to finish** — e.g. `submit_decision(action,
  confidence, reason)` with `action` an enum (`long`/`short`/`no_trade`/`alert_human`).
  The runner surfaces the call; you act on its typed input. This doubles as the
  gate for what happens next.
- **Structured outputs** on a final non-tool turn — `output_config={"format":
  {"type": "json_schema", "schema": {...}}}` — when you just need a JSON object
  and no further tool use. Note: incompatible with citations; on a forced
  `tool_choice` use the decision-tool approach instead.

Prefer the decision tool for pipelines: it keeps intake → reason → **decide** →
act in one loop and gives you a single place to enforce policy.

## Model choice & migrating the bridge

- **Default `claude-opus-4-8` + `thinking={"type":"adaptive"}`** for the deciding
  agent. Use `output_config={"effort": "high"}` for hard judgment; `low` for
  cheap mechanical sub-steps.
- The repo's `tv_claude_bridge.py` pins `model="claude-sonnet-4-20250514"`
  (deprecated, retires 2026-06-15). Migrate the string to `claude-opus-4-8` (or
  `claude-sonnet-5` for a cheaper high-volume path). No other code change is
  required for that call; if you later add thinking, use adaptive, not
  `budget_tokens` (which 400s on current models).
- For long/large outputs, **stream** (`client.messages.stream(...)` →
  `.get_final_message()`) so you don't hit HTTP timeouts.
