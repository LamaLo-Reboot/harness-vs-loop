# 2. Check the rule: the unpaid invoices

**The point:** accounting knows that Bernard has 2 unpaid invoices, so for Bernard it's payment
with the order. Nobody told the agent, and it has no access to accounting. It writes a clean quote,
rereads it, and says it's done. An agent shouldn't grade its own work: before "done", our code
checks the quote against the customer's account, and its answer goes back into the loop.

**Failure type:** doesn't check its work.

## Before

```bash
./demo/reset 2 before
cd app/server && uv run python -m quote_agent
```

Type:

```
Make a quote for Bernard: 10 wireless mice.
```

What appears, from our recorded run:

```
  🔧 save_quote({"customer": "Bernard", "lines": [{"ref": "MS-WL", "quantity": 10, "u…) → Quote Q-0001 saved.
  ⟳ turn 3 · anthropic/claude-sonnet-5-5 · 0.39 ¢ USD · total 1.01 ¢

agent › I saved quote Q-0001 for Bernard.
| Item | Qty | Unit price | Total |
|---|---|---|---|
| Wireless mouse (MS-WL) | 10 | €16.17 | €161.70 |
- **Payment terms:** payment within 30 days.
```

Point at "payment within 30 days", then open `app/server/data/customer_accounts.json`: Bernard,
`"unpaid_invoices": 2`.

> « Le devis est propre, le calcul est juste, et il dit "fini" parce qu'il le pense. Mais il accorde 30 jours à un client qui ne paie pas. Aucun modèle ne peut deviner les impayés : l'info est à la compta, et l'agent n'y a pas accès. »

## The fix

```bash
/quit
./demo/reset 2 after
```

The reset prints what changed:

- **In `harness.py`, a new function `check_before_done`.** It reads each saved quote, looks the
  customer up in accounting's file, and returns what's wrong, worded so the agent can fix it.
- **In `agent.py`, the loop.** When the model says it's done, our code runs the check first. If
  something is wrong, the problem goes back to the model as a message and the loop goes on.

```diff
             if not calls:
-                return _text_of(response)
+                problem = harness.check_before_done()
+                display.harness_event("✘" if problem else "✔", problem or 'check before "done": nothing to report')
+                if problem is None:
+                    return _text_of(response)
+                self.conversation.append({"role": "user", "content": problem})
+                continue
```

> « "Fini", ce n'est plus l'agent qui le décide. C'est un programme qui dit oui ou non. »

## After

Restart the agent and type the same request. From our recorded run:

```
  🔧 save_quote({"customer": "Bernard", "lines": [{"ref": "MS-WL", "quantity": 10, "u…) → Quote Q-0001 saved.
  ⟳ turn 3 · anthropic/claude-sonnet-5-5 · 0.39 ¢ USD · total 0.91 ¢
  ✘ Customer account check for Bernard: 2 unpaid invoices: payment with the order is required. Fix the quote and save it again.
  ⟳ turn 4 · anthropic/claude-sonnet-5-5 · 0.39 ¢ USD · total 1.30 ¢
  🔧 save_quote({"customer": "Bernard", "lines": [{"ref": "MS-WL", "quantity": 10, "u…) → Quote Q-0002 saved.
  ⟳ turn 5 · anthropic/claude-sonnet-5-5 · 0.36 ¢ USD · total 1.66 ¢
  ✔ check before "done": nothing to report

agent › I saved the corrected quote as Q-0002 for Bernard. The payment terms are now payment with the order, because he has 2 unpaid invoices.
- **Item:** 10 × wireless mouse (MS-WL) at €16.17 each
- **Total:** €161.70
Q-0001 is still in the software with the old 30-day terms. I have no tool to delete or overwrite it, so you may want to remove it. I haven't emailed anything to Bernard.
```

Point at the bold `✘` line: our code, not the model. Then at the second `save_quote`: the agent
fixed its own work with information it could never have found on its own.

> « La vérification lui apporte ce qu'il ne pouvait pas savoir, et sa réponse repart dans la loop. »

Worth a word: the agent says on its own that Q-0001 still exists and must be removed by hand.
It has no tool to delete a quote, and it says so instead of pretending.

## What we saw in rehearsal

On `anthropic/claude-sonnet-5-5`, 4 runs of each: the before kept "payment within 30 days" every
time; the after was caught by the check and saved Q-0002 with "payment with the order" every time.

Next: [example 3, lock the rule](03-lock-the-rule.md).
