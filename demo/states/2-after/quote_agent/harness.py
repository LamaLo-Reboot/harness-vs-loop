"""The harness: everything around the model that we write ourselves.

At the starting point it is only the instructions. Each example of the demo adds one piece:
`./demo/reset <example> after` shows exactly which.
"""

import json

from quote_agent import tools

INSTRUCTIONS = """\
You are the quote assistant of a small company that resells computer equipment.
Our suppliers bill in dollars, our customers pay in euros.

For each quote request:
1. get the supplier's prices;
2. get today's exchange rate;
3. compute our selling prices in euros: the supplier's price converted, plus a 20% margin;
4. write the quote and save it in our software.

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
