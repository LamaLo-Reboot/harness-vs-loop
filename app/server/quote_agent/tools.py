"""The four tools the agent can call, and what our code does when it calls them.

The model never runs anything itself: it asks for a tool by name, with arguments, and
`run` does the work and hands back a text result.

Two systems behind the tools can be scripted from `data/`, for the examples that need them:
`bank_stuck.txt` makes the bank answer "in progress" forever (example 4), and
`software_references.json` makes the old software refuse references it no longer knows
(example 5). Without those files, the bank is the real ECB feed and the software accepts
every reference.
"""

import itertools
import json
import re
from datetime import datetime
from pathlib import Path

import httpx

SERVER_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = SERVER_DIR / "data"
OUT_DIR = SERVER_DIR / "out"

ECB_DAILY_RATES = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"

DEFINITIONS = [
    {
        "type": "function",
        "name": "get_supplier_prices",
        "description": "Our supplier's price list, in US dollars.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "type": "function",
        "name": "get_exchange_rate",
        "description": "The bank's exchange rate for today: what 1 euro is worth in a currency.",
        "parameters": {
            "type": "object",
            "properties": {"currency": {"type": "string", "description": "The currency code, for example USD."}},
            "required": ["currency"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "send_quote",
        "description": "Emails the quote to the customer.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer": {"type": "string", "description": "The customer's name."},
                "text": {"type": "string", "description": "The whole quote, as the customer will read it."},
            },
            "required": ["customer", "text"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "save_quote",
        "description": "Saves the quote in our business software.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer": {"type": "string", "description": "The customer's name."},
                "lines": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "ref": {"type": "string", "description": "The product reference."},
                            "quantity": {"type": "integer"},
                            "unit_price_eur": {"type": "number"},
                        },
                        "required": ["ref", "quantity", "unit_price_eur"],
                        "additionalProperties": False,
                    },
                },
                "payment_terms": {"type": "string", "description": "The payment terms."},
            },
            "required": ["customer", "lines", "payment_terms"],
            "additionalProperties": False,
        },
    },
]


def get_supplier_prices() -> str:
    return (DATA_DIR / "supplier_prices.txt").read_text(encoding="utf-8")


def parse_ecb_rate(xml: str, currency: str) -> str:
    day = re.search(r"time='(\d{4}-\d{2}-\d{2})'", xml)
    rate = re.search(rf"currency='{re.escape(currency.upper())}' rate='([\d.]+)'", xml)
    if not day or not rate:
        return f"No rate for the currency {currency}."
    return f"1 EUR = {rate.group(1)} {currency.upper()} (ECB reference rate of {day.group(1)})"


_bank_polls = itertools.count()


def get_exchange_rate(currency: str) -> str:
    stuck = DATA_DIR / "bank_stuck.txt"
    if stuck.exists():
        positions = [line for line in stuck.read_text(encoding="utf-8").split() if line.isdigit()]
        position = positions[next(_bank_polls) % len(positions)]
        return f"Calculation in progress, try again in a few seconds. Position in the queue: {position}."
    return parse_ecb_rate(httpx.get(ECB_DAILY_RATES, timeout=10).text, currency)


def send_quote(customer: str, text: str) -> str:
    sent_dir = OUT_DIR / "sent"
    sent_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    (sent_dir / f"{stamp}-{customer}.txt").write_text(text, encoding="utf-8")
    return f"Quote sent to {customer}."


def save_quote(customer: str, lines: list[dict], payment_terms: str) -> str:
    known = _software_references()
    if known is not None and any(line["ref"] not in known["active"] for line in lines):
        return "ERR 4012"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    saved = OUT_DIR / "saved_quotes.jsonl"
    number = len(saved.read_text(encoding="utf-8").splitlines()) + 1 if saved.exists() else 1
    record = {"number": f"Q-{number:04d}", "customer": customer, "lines": lines, "payment_terms": payment_terms}
    with saved.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")
    return f"Quote {record['number']} saved."


def _software_references() -> dict | None:
    path = DATA_DIR / "software_references.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def replaced_references() -> dict[str, str]:
    """Old reference → new one, as the old software knows them. The agent has no tool to read this."""
    return (_software_references() or {}).get("replaced", {})


def latest_saved_quotes() -> list[dict]:
    """The last quote saved for each customer."""
    saved = OUT_DIR / "saved_quotes.jsonl"
    if not saved.exists():
        return []
    latest = {}
    for line in saved.read_text(encoding="utf-8").splitlines():
        quote = json.loads(line)
        latest[quote["customer"]] = quote
    return list(latest.values())


def sent_to() -> list[str]:
    """The customers a quote was sent to."""
    sent_dir = OUT_DIR / "sent"
    return [path.stem.split("-", 2)[2] for path in sorted(sent_dir.glob("*.txt"))] if sent_dir.exists() else []


FUNCTIONS = {
    "get_supplier_prices": get_supplier_prices,
    "get_exchange_rate": get_exchange_rate,
    "send_quote": send_quote,
    "save_quote": save_quote,
}


def run(name: str, arguments: dict) -> str:
    if name not in FUNCTIONS:
        return f"Unknown tool: {name}."
    return FUNCTIONS[name](**arguments)
