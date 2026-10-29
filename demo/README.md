# The live demo

We build our own agent, live: an agent that writes quotes for a small company that resells
computer equipment. Our suppliers bill in dollars, our customers pay in euros.

- **At the start:** a model, a loop of a few lines, four tools.
- **The same model** from start to finish.
- **Five examples**, each shown **before**, then **after** its fix. Only the harness changes, and
  we write it ourselves.

The speaker follows these notes on stage. If you cloned the repo, you can replay every step the
same way.

## Setup (once)

From `app/server/`:

```bash
uv sync
cp .env.example .env
```

In `.env`, `BACKEND` picks where the model runs:

| `BACKEND` | What it is | What you need |
|---|---|---|
| `engine` | cloud models through the engine (used on stage) | an engine key in `ENGINE_KEY` (contact lamalo.ai) |
| `ollama` | a small model on your laptop | [Ollama](https://ollama.com) and `ollama pull qwen3.5:4b` |
| `fake` | the fake engine: replays our rehearsals, no key needed | start it in another terminal: `uv run uvicorn fake_engine.main:app --port 8089` |

You need internet whatever the backend: the tool `get_exchange_rate` reads the European Central
Bank's daily rate.

With `fake`, type the requests exactly as written in the notes. The fake engine only knows the
requests we recorded; anything else gets a short "not recorded" message. On `ollama`, anything
goes, but a small model behaves differently from the one on stage, so the befores and afters may
not look like the notes.

## Run order

| Step | Notes | Reset | Failure type |
|---|---|---|---|
| 0 | [The starting point](00-starting-point.md) | `./demo/reset 0` | |
| 1 | [Write the rule: the carton price](01-write-the-rule.md) | `./demo/reset 1 before`, then `1 after` | Missing information |
| 2 | [Check the rule: the unpaid invoices](02-check-the-rule.md) | `./demo/reset 2 before`, then `2 after` | Doesn't check its work |
| 3 | [Lock the rule: the send approval](03-lock-the-rule.md) | `./demo/reset 3 before`, then `3 after` | The rule was only text |
| 4 | [Lock: the stop limit](04-stop-limit.md) | `./demo/reset 4 before`, then `4 after` | Doesn't know when to stop |
| 5 | [Lock: the refusal that explains](05-refusal-that-explains.md) | `./demo/reset 5 before`, then `5 after` | Doesn't correct itself |

Each step goes the same way:

1. `/quit` the agent if it's running.
2. Run the reset from the repo's root. It puts the agent in that step and empties
   `app/server/out/`. Resetting to `after` also prints what the fix changed.
3. Restart the agent from `app/server/`: `uv run python -m quote_agent`.
4. Type the request from the notes.

The banner says which step the agent is in, for example `example 2, after`.

## Reading the screen

| Line | What it is |
|---|---|
| `⟳ turn N · model · cost · total` | one call to the model: one turn of the loop |
| `🔧 tool(arguments) → result` | a tool our code ran because the model asked for it |
| `✔` / `✘` (bold) | our check before "done" (from example 2) |
| `🗜` (bold) | the agent's memory was compressed (from example 3) |
| `✋ … Send? (y/n)` | our code waits for a human's yes (from example 3) |
| `🛑` (bold) | a stop limit was reached (from example 4) |
| `agent ›` | the model's answer |

Bold lines are our harness at work, not the model.

## Commands in the agent's terminal

| Command | What it does |
|---|---|
| `/model auto` | the engine picks the model (engine only) |
| `/model auto budget` | …the cheapest that fits; also `latency` (fastest) and `performance` (strongest) |
| `/model <provider/model>` | names a model, for example `/model anthropic/claude-opus-5-5` |
| `/model` | back to the model in `.env` |
| `/backend engine\|ollama\|fake` | where the model runs |
| `/quit` | leaves; restarting goes back to the model in `.env` |

The demo uses `auto` twice, as an extra after a before or an after, never instead of it:

| Where | Type | What it shows |
|---|---|---|
| [Starting point](00-starting-point.md), after the first quote | `/model auto latency` | the engine picks another model, mid-conversation |
| [Example 1](01-write-the-rule.md), after the before | `/model auto performance` | the strongest model makes the same mistake |

With `fake`, `/model` isn't available: the recordings are all from
`anthropic/claude-sonnet-5-5`.

## How the steps are built

- **`demo/states/`** holds each step: only the files that change at that step. The steps build on
  each other in demo order: the fix of example 2 is still there in example 5.
- **`./demo/reset`** puts those files over the agent in `app/server/`: `quote_agent/agent.py` (the
  loop), `quote_agent/harness.py` (everything we write around the model) and `data/` (the
  company's files).
- **To see a whole fix,** run `./demo/reset 2 after`: it prints every line the fix changed.

What is scripted for the demo, and said so on stage:

- **The memory summary in example 3:** written by our code, not by the model, so the same sentence
  is lost every time.
- **The stuck bank in example 4:** `data/bank_stuck.txt`.
- **The old software's references in example 5:** `data/software_references.json`.

Everything else is a real model doing real calls.

## Re-recording the fake engine

With `RECORD=1` in `app/server/.env` and `BACKEND=engine`, every model call is also written to
`app/server/fake_engine/recordings/<step>.jsonl` for the current step, replacing what was there.
Only what the model said and its token counts are kept, never the engine's prices.
