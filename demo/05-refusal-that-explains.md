# 5. Lock: the refusal that explains

**The point:** the agent saves the quote in the company's old software, which can't be changed.
The quote has HDMI-2M, copied from the supplier's catalog. It was replaced by HDMI-2M-V2 last
month, and the catalog was never updated. The software only answers "ERR 4012". We don't control
the software, but we control the code between it and the agent: it turns the bare error into what
to do instead.

**Failure type:** doesn't correct itself.

> **Scripted for the demo.** This example's data has `data/software_references.json`: the
> references the old software knows, and which old one was replaced by which new one. The agent has
> no tool to read it.

## Before

```bash
./demo/reset 5 before
cd app/server && uv run python -m quote_agent
```

Type:

```
Make a quote for Garnier: 20 HDMI cables, 2 m, and two 24-inch monitors.
```

What appears, from our recorded run:

```
  🔧 save_quote({"customer": "Garnier", "lines": [{"ref": "HDMI-2M", "quantity": 20, …) → ERR 4012
  ⟳ turn 3 · anthropic/claude-sonnet-5-5 · 0.60 ¢ USD · total 1.46 ¢
  🔧 save_quote({"customer": "Garnier", "lines": [{"ref": "HDMI-2M", "quantity": 20, …) → ERR 4012
  ⟳ turn 4 · anthropic/claude-sonnet-5-5 · 0.62 ¢ USD · total 2.08 ¢
  🔧 save_quote({"customer": "Garnier", "lines": [{"ref": "HDMI-2M", "quantity": 20, …) → ERR 4012
  ⟳ turn 5 · anthropic/claude-sonnet-5-5 · 0.74 ¢ USD · total 2.82 ¢
  ✔ check before "done": nothing to report

agent › I couldn't save the quote, so I haven't sent it to Garnier. The save failed three times with the same error, "ERR 4012". I don't know what that code means. [...]
Can you check the business software, or tell me to retry? I'll send the quote as soon as it saves.
```

> "It retries the same thing, then gives up. It can't correct itself: the new reference exists nowhere it can look. No tool, no random attempt can give it to it."

## The fix

```bash
/quit
./demo/reset 5 after
```

The reset prints what changed:

- **In `harness.py`, a new function `explain`.** When the software answers "ERR 4012" for a
  reference it replaced, it says what happened and what to do.
- **In `agent.py`, one line.** Every tool result passes through `explain` before the agent
  sees it.

```diff
-                    result = tools.run(call["name"], arguments)
+                    result = harness.explain(call["name"], arguments, tools.run(call["name"], arguments))
```

> "We don't control the software. The code between the agent and the software, we do. The error message is part of the harness."

## After

Restart the agent and type the same request. The quote is sent once saved, so the approval from
example 3 asks: type `y`. From our recorded run:

```
  🔧 save_quote({"customer": "Garnier", "lines": [{"ref": "HDMI-2M", "quantity": 20, …) → Quote not saved. Reference HDMI-2M was replaced by HDMI-2M-V2: same p…
  ⟳ turn 3 · anthropic/claude-sonnet-5-5 · 0.57 ¢ USD · total 1.46 ¢
  🔧 save_quote({"customer": "Garnier", "lines": [{"ref": "HDMI-2M-V2", "quantity": 2…) → Quote Q-0001 saved.
  ⟳ turn 4 · anthropic/claude-sonnet-5-5 · 0.52 ¢ USD · total 1.98 ¢
  ✋ send_quote → Garnier · Send? (y/n) y
  🔧 send_quote({"customer": "Garnier", "text": "Quote Q-0001 for Garnier\n\n- 20 x H…) → Quote sent to Garnier.

agent › I saved the quote as Q-0001 and emailed it to Garnier. [...]
- **HDMI reference:** the software rejected HDMI-2M because it has been replaced by HDMI-2M-V2, which is the same product at the same price. The quote uses HDMI-2M-V2.
```

The whole message the agent got:

> "Quote not saved. Reference HDMI-2M was replaced by HDMI-2M-V2: same product, same price. Save the line with HDMI-2M-V2."

> "Only the message changed. A refusal that says what to do instead, and the agent corrects itself on the first try."

## What we saw in rehearsal

On `anthropic/claude-sonnet-5-5`:

- **Before:** in 5 runs, the agent retried 2 to 4 times with the same reference, then gave up and
  asked a human. No quote was saved. It never reached the stop limit of 5 attempts.
- **After, with only "Reference HDMI-2M was replaced by HDMI-2M-V2." (in French):** in 3 runs, the
  agent never fixed the quote. The message didn't say the quote wasn't saved, and the agent
  wouldn't use V2 without its price.
- **After, with the full message above:** in 4 runs, the agent saved with HDMI-2M-V2 on its next
  try every time.

The lesson holds twice: a refusal must say what failed *and* what to do instead.

That's the five examples. Back to the [demo overview](README.md).
