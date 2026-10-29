"""The harness: everything around the model that we write ourselves.

At the starting point it is only the instructions. Each example of the demo adds one piece:
`./demo/reset <example> after` shows exactly which.
"""

import json
from datetime import datetime

from quote_agent import display, tools

INSTRUCTIONS = """\
You are the quote assistant of a small company that resells computer equipment.
Our suppliers bill in dollars, our customers pay in euros.

For each quote request:
1. get the supplier's prices;
2. get today's exchange rate;
3. compute our selling prices in euros: the supplier's price converted, plus a 20% margin;
4. write the quote and save it in our software;
5. once the quote is saved, send it to the customer.

The supplier's price for the HDMI cable (HDMI-2M) is for a box of 10 cables.
Never a quote without today's rate.
Usual payment terms: payment within 30 days.
Answer in English, briefly.
"""


# Check the rule (example 2). Before the agent may say "done", our code checks each saved quote
# against the customer's account. The agent has no access to accounting: the check brings it
# what it can't know, and its answer goes back into the loop.


def check_before_done() -> str | None:
    """None when the work passes; otherwise what is wrong, worded so the agent can fix it."""
    accounts = json.loads((tools.DATA_DIR / "customer_accounts.json").read_text(encoding="utf-8"))
    for quote in tools.latest_saved_quotes():
        for name, account in accounts.items():
            if name.lower() in quote["customer"].lower() and isinstance(account, dict):
                unpaid = account["unpaid_invoices"]
                if unpaid and "order" not in quote["payment_terms"].lower():
                    return (
                        f"Customer account check for {name}: {unpaid} unpaid invoices: "
                        "payment with the order is required. Fix the quote and save it again."
                    )
    return None


# Memory (set up for example 3). The agent's memory holds a few requests; when it is full, the
# whole conversation is replaced by a summary. The limit is set very low for the demo. A real agent asks
# the model to write the summary; here our code writes it, so what gets lost is the same every
# time: the quotes survive, what you said doesn't.
MEMORY_LIMIT = 2  # requests


def memory_is_full(conversation: list[dict]) -> bool:
    return sum(1 for item in conversation if item.get("role") == "user") >= MEMORY_LIMIT


def compress(conversation: list[dict]) -> list[dict]:
    quotes = [
        f"- {quote['number']} for {quote['customer']}: "
        + ", ".join(f"{line['quantity']} × {line['ref']} at {line['unit_price_eur']} €" for line in quote["lines"])
        + f"; {quote['payment_terms']}"
        for quote in tools.latest_saved_quotes()
    ]
    sent = ", ".join(tools.sent_to()) or "none"
    summary = "Summary of our conversation so far. Saved quotes:\n" + "\n".join(quotes) + f"\nSent quotes: {sent}."
    display.harness_event("🗜", f"memory full: {len(conversation)} items replaced by this summary")
    display.quoted(summary)
    return [{"role": "user", "content": summary}]


# Lock the rule (example 3). Sending needs a yes typed by a human, whatever the agent remembers.
# The agent can't answer this question itself: it isn't a tool, it's our code waiting for you.
NEEDS_APPROVAL = {"send_quote"}
REFUSED = "Sending refused: the person in charge did not approve."


def approved(tool_name: str, arguments: dict) -> bool:
    answer = input(f"  ✋ {tool_name} → {arguments.get('customer')} · Send? (y/n) ")
    return answer.strip().lower().startswith("y")


# Lock: a stop limit (example 4). Set before starting; the loop we wrote has no limit of its own.
MAX_ATTEMPTS = 5  # calls to the same tool, per request
MAX_SPEND_CENTS = 200  # per request, in the engine's billing currency


def over_limit(tool_name: str, attempts: int, spent_cents: float) -> str | None:
    if attempts > MAX_ATTEMPTS:
        return f"{MAX_ATTEMPTS} attempts at {tool_name} with no result"
    if spent_cents > MAX_SPEND_CENTS:
        return f"budget of {MAX_SPEND_CENTS} ¢ exceeded"
    return None


def alert_human(reason: str) -> None:
    tools.OUT_DIR.mkdir(parents=True, exist_ok=True)
    with (tools.OUT_DIR / "alerts.txt").open("a", encoding="utf-8") as file:
        file.write(f"{datetime.now():%Y-%m-%d %H:%M} · quote agent stopped: {reason}\n")
    display.harness_event("🛑", f"stopped: {reason} · a human has been notified (out/alerts.txt)")


# Lock: a refusal that explains (example 5). We can't change the old software, but we control the
# code between it and the agent: it turns the bare error into what to do instead.


def explain(tool_name: str, arguments: dict, result: str) -> str:
    if tool_name != "save_quote" or result != "ERR 4012":
        return result
    replaced = tools.replaced_references()
    for line in arguments["lines"]:
        if line["ref"] in replaced:
            old, new = line["ref"], replaced[line["ref"]]
            return f"Quote not saved. Reference {old} was replaced by {new}: same product, same price. Save the line with {new}."
    return result
