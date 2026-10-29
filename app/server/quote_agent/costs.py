"""Turns what the engine reports into a cost.

The engine never computes a cost: each answer carries the price list that applied
(`lamalo.pricing`) and how much was used (`usage`). This module multiplies one by the other.

All costs in this demo are in cents, with decimals (0.31 means 0.31 cents), in the price
list's currency.
"""

from dataclasses import dataclass

TOKENS_PER_PRICED_UNIT = 1_000_000
CENTS_PER_UNIT_OF_CURRENCY = 100


@dataclass(frozen=True)
class Cost:
    cents: float
    currency: str


def _token_counts(usage: dict) -> dict[str, int]:
    """How many tokens each price row applies to. The engine's `input_tokens` includes the
    cached ones, which have their own, cheaper row."""
    input_tokens = usage.get("input_tokens", 0)
    cached = (usage.get("input_tokens_details") or {}).get("cached_tokens", 0)
    return {
        "per-1m-input-tokens": input_tokens - cached,
        "per-1m-cached-input-tokens": cached,
        "per-1m-output-tokens": usage.get("output_tokens", 0),
    }


def compute_cost(usage: dict | None, pricing: list[dict]) -> Cost | None:
    """The cost of one engine call, or None when the engine reported no usage or no price.

    Only the token rows are counted: they are the quantities an answer reports. Other fees
    (per search, for example) are only in the engine's usage ledger, so this is the cost of
    the tokens read and written.
    """
    if not usage or not pricing:
        return None
    counts = _token_counts(usage)
    currencies = {row["currency"] for row in pricing}
    if len(currencies) != 1:
        raise ValueError(f"price list mixes currencies: {sorted(currencies)}")
    amount = 0.0
    for row in pricing:
        quantity = counts.get(row["pricing_unit_type"])
        if quantity:
            amount += quantity / TOKENS_PER_PRICED_UNIT * float(row["cost_per_unit"])
    return Cost(cents=amount * CENTS_PER_UNIT_OF_CURRENCY, currency=currencies.pop())
