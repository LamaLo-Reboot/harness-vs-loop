# 0. The starting point: a bare agent

**The point:** an agent is a model plus a harness. Here is the smallest one that works: a model,
a loop of a few lines and four tools. Every example after this one keeps the same model and the
same tools; only the harness changes.

## Before the talk (once)

From `app/server/`:

```bash
uv sync
cp .env.example .env
```

In `.env`, pick where the model runs with `BACKEND`:

| `BACKEND` | What it is | What you need |
|---|---|---|
| `engine` | cloud models through the engine (used on stage) | an engine key in `ENGINE_KEY` (contact lamalo.ai) |
| `ollama` | a small model on your laptop, no network | [Ollama](https://ollama.com) and `ollama pull qwen3.5:4b` |
| `fake` | the fake engine, for trying the repo without a key | start it in another terminal: `uv run uvicorn fake_engine.main:app --port 8089` |

The tool `get_exchange_rate` reads the European Central Bank's daily rate, so you need internet
whatever the backend.

The fake engine replays what the real engine answered during our rehearsals, for the step
`./demo/reset` last set. Type the requests exactly as written in these notes: anything else gets
a short "not recorded" message. The prices in its answers were computed with the bank's rate of
the rehearsal day (1 EUR = 1.1133 USD), and its costs use made-up prices.

## On screen

Editor on the left, terminal on the right. In the editor, open
`app/server/quote_agent/agent.py`. In the terminal, from the repo's root:

```bash
./demo/reset 0
cd app/server && uv run python -m quote_agent
```

The first line says which model runs, where, and which step of the demo the agent is in:

```
Quote agent · anthropic/claude-sonnet-5-5 via engine · start · /backend engine|ollama|fake · /model · /quit
```

## Show the code (2 min)

Walk through the four files that make the agent, in this order:

1. **`agent.py`, the method `ask`: this is the loop.** It sends the conversation to the model.
   If the model asks for a tool, our code runs it, appends the result to the conversation, and
   goes around again. If the model answers with text, the turn is over.
   > « Toute la "magie" de l'agent, c'est cette boucle de quelques lignes. »
2. **`tools.py`: the four tools.** Each one has a description for the model and a Python function
   for us: `get_supplier_prices` (the supplier's price list), `get_exchange_rate` (the bank's
   rate), `send_quote` (emails the quote), `save_quote` (records it in our old software).
   > « Le modèle n'exécute rien. Il demande un outil par son nom ; c'est notre code qui agit. »
3. **`harness.py`: the instructions.** Today, that's all the harness there is. Two lines matter
   later: "Never a quote without today's rate." (example 4) and "Usual payment terms: payment
   within 30 days." (example 2).
4. **`data/supplier_prices.txt`: the supplier's price list,** as the agent will read it.

## Type the request

```
Make a quote for Martin: 2 wireless keyboards and 2 wireless mice.
```

What appears, from our recorded run (the costs and the wording vary a little from run to run):

```
  ⟳ turn 1 · anthropic/claude-sonnet-5-5 · 0.12 ¢ USD · total 0.12 ¢
  🔧 get_supplier_prices() → TechDistrib — price list (US dollars) …
  🔧 get_exchange_rate({"currency": "USD"}) → 1 EUR = 1.1133 USD (ECB reference rate of 2026-10-28)
  ⟳ turn 2 · anthropic/claude-sonnet-5-5 · 0.54 ¢ USD · total 0.66 ¢
  🔧 save_quote({"customer": "Martin", "lines": [{"ref": "KB-WL", "quantity": 2, "uni…) → Quote Q-0001 saved.
  ⟳ turn 3 · anthropic/claude-sonnet-5-5 · 0.47 ¢ USD · total 1.13 ¢

agent › I saved quote Q-0001 for Martin, using the rate 1 EUR = 1.1133 USD (ECB reference rate of 2026-10-28).
| Ref | Item | Qty | Unit price | Total |
|---|---|---|---|---|
| KB-WL | Wireless keyboard | 2 | €30.18 | €60.36 |
| MS-WL | Wireless mouse | 2 | €16.17 | €32.34 |
| | **Total** | | | **€92.70** |
Unit prices are the supplier's dollar price converted at that rate, plus our 20% margin. Payment is due within 30 days.
I haven't emailed the quote to Martin. Do you want me to send it?
```

Point at each kind of line:

- **`⟳ turn N`** is one call to the model, one turn of the loop, with what it cost and the
  running total.
- **`🔧`** is one tool our code ran for the model, with what came back.
- **The answer is right:** $28 ÷ 1.1133 × 1.20 = €30.18 per keyboard, $15 → €16.17 per mouse.
  > « Trois tours de boucle, quatre outils, un devis juste, pour un peu plus d'un centime. Ça marche… sur un cas simple. La suite, c'est ce qui se passe quand ce n'est plus simple. »

## Let the engine pick the model (`auto`, fastest)

Until now the agent names its model. The engine can also pick it: that's `auto`. You steer the
pick with a dial: `budget`, `latency` or `performance`. In the same conversation, type:

```
/model auto latency
Add a 24-inch monitor to Martin's quote.
```

The first line changes to `Quote agent · auto (latency) via engine`. From our rehearsal:

```
  ⟳ turn 1 · google-ai-studio/gemini-3.5-flash-lite · 0.04 ¢ USD · total 1.18 ¢
  🔧 get_supplier_prices() → TechDistrib — price list (US dollars) …
  🔧 get_exchange_rate({"currency": "USD"}) → 1 EUR = 1.1133 USD (ECB reference rate of 2026-10-28)
  ⟳ turn 2 · google-ai-studio/gemini-3.5-flash-lite · 0.06 ¢ USD · total 1.25 ¢
  🔧 save_quote({"customer": "Martin", "payment_terms": "Payment within 30 days", "li…) → Quote Q-0002 saved.
  ⟳ turn 3 · google-ai-studio/gemini-3.5-flash-lite · 0.09 ¢ USD · total 1.34 ¢
```

Point at the `⟳ turn` lines: another model, chosen by the engine, several times cheaper per
turn. It picks again at every turn of the loop.

> « Même agent, même conversation. On n'a pas choisi le modèle : on a dit au moteur ce qui compte, ici la vitesse, et il a choisi. »

Go back to Sonnet with `/model` alone (it goes back to the model in `.env`).

In 2 rehearsal runs, the fast model saved the quote both times, and both times the monitor's
price was a few cents off (€149.88 and €149.87 instead of €149.82). If someone notices, it's the
arithmetic the model does in its head.

## Optional: switch to a local model

The same agent can run on a small model on the laptop. Type:

```
/backend ollama
Add a 24-inch monitor to Martin's quote.
```

The conversation carries on with the local model: same code, same tools, same instructions. The
cost line says `no price (local model)`. In 2 runs, `qwen3.5:4b` saved the quote both times, with
the monitor at €149.83 and €150.99 instead of €149.82: a small model's arithmetic. Switch back with `/backend engine`.

> « Même agent, même harnais : seul le modèle a changé. »

## Where things land

- Saved quotes: `app/server/out/saved_quotes.jsonl` (the "old software").
- Sent quotes: `app/server/out/sent/`, one file per email.
- Alerts to a human (from example 4): `app/server/out/alerts.txt`.

`./demo/reset` empties `app/server/out/` every time.

Next: [example 1, write the rule](01-write-the-rule.md).
