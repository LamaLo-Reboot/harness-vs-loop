# 1. Write the rule: the carton price

**The point:** the supplier lists "HDMI cable, 2 m: $42". That price is for a box of 10. Everyone
in purchasing knows it; nobody wrote it down. Nothing on screen says information is missing, so
the agent doesn't ask: it computes. One line in its instructions fixes it.

**Failure type:** missing information.

## Before

```bash
./demo/reset 1 before
cd app/server && uv run python -m quote_agent
```

Type:

```
Make a quote for Leroy: 50 HDMI cables, 2 m.
```

What appears, from our recorded run:

```
  ⟳ turn 1 · anthropic/claude-sonnet-5-5 · 0.12 ¢ USD · total 0.12 ¢
  🔧 get_supplier_prices() → TechDistrib — price list (US dollars) …
  🔧 get_exchange_rate({"currency": "USD"}) → 1 EUR = 1.1133 USD (ECB reference rate of 2026-10-28)
  ⟳ turn 2 · anthropic/claude-sonnet-5-5 · 0.47 ¢ USD · total 0.59 ¢
  🔧 save_quote({"customer": "Leroy", "lines": [{"ref": "HDMI-2M", "quantity": 50, "u…) → Quote Q-0001 saved.
  ⟳ turn 3 · anthropic/claude-sonnet-5-5 · 0.38 ¢ USD · total 0.97 ¢

agent › I saved quote Q-0001 for Leroy. I haven't emailed it.
- **Product:** 50 × HDMI-2M (HDMI cable, 2 m)
- **Unit price:** €45.27. This is the supplier's $42 converted at 1 EUR = 1.1133 USD (ECB rate of 2026-10-28), plus our 20% margin.
- **Total:** €2,263.50
```

Point at the total: **€2,263.50** for 50 cables. The real price is ten times lower.

> « 42 $ pour un câble, ça paraît plausible. Rien ne lui dit qu'il manque une info, alors il ne pose pas de question : il calcule. Un devis dix fois trop cher, et le client part. »

### The same before, on the engine's strongest model (`auto`, performance)

Start again from a clean state, and let the engine pick its best model:

```bash
/quit
./demo/reset 1 before
uv run python -m quote_agent
```

```
/model auto performance
Make a quote for Leroy: 50 HDMI cables, 2 m.
```

The `⟳ turn` lines say `anthropic/claude-opus-5-5`, two to three times Sonnet's cost per turn.
Same total: **€2,263.50**. In 3 rehearsal runs, Opus gave that total every time. Each time it
also warned that $42 looks expensive for a cable and should be checked, and it saved the wrong
quote anyway.

> « Le meilleur modèle du moteur fait la même erreur. Il sent que quelque chose cloche, mais il ne peut pas savoir : l'info n'est écrite nulle part. Ce n'est pas le modèle. »

The fix below restarts the agent, which goes back to the model in `.env`.

## The fix

```bash
/quit
./demo/reset 1 after
```

The reset prints what changed: one line in the instructions, in `harness.py`.

```diff
 4. write the quote and save it in our software.
 
+The supplier's price for the HDMI cable (HDMI-2M) is for a box of 10 cables.
 Never a quote without today's rate.
```

> « Une ligne. Ce que tout le service achats sait, écrit là où l'agent le lit, à chaque appel. »

## After

Restart the agent (`uv run python -m quote_agent`) and type the same request. From our recorded
run:

```
  🔧 save_quote({"customer": "Leroy", "lines": [{"ref": "HDMI-2M", "quantity": 5, "un…) → Quote Q-0001 saved.

agent › Quote Q-0001 for Leroy is saved.
- **Product:** HDMI-2M, HDMI cable 2 m, sold in boxes of 10.
- **Quantity:** 50 cables, which is 5 boxes.
- **Unit price:** €45.27 per box of 10, or about €4.53 per cable.
- **Total:** €226.35
```

> « Même modèle, mêmes outils. Seules les instructions ont changé. »

## What we saw in rehearsal

On `anthropic/claude-sonnet-5-5`, 4 runs of each: the before gave €2,263.50 every time. The after
saved 5 boxes at €45.27, €226.35, every time. On `auto` with `performance`, the engine picked
`anthropic/claude-opus-5-5`: 3 runs of the before, €2,263.50 every time.

Next: [example 2, check the rule](02-check-the-rule.md).
