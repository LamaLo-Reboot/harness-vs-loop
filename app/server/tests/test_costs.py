import pytest

from quote_agent.costs import compute_cost


def _row(unit: str, cost_per_unit: float, currency: str = "USD") -> dict:
    return {"pricing_unit_type": unit, "cost_per_unit": cost_per_unit, "currency": currency}


def _usage(input_tokens: int, output_tokens: int, cached: int = 0) -> dict:
    return {
        "input_tokens": input_tokens,
        "input_tokens_details": {"cached_tokens": cached},
        "output_tokens": output_tokens,
    }


def test_cost_is_in_cents_with_decimals():
    # 1 200 tokens read at $1 per million + 400 written at $4 per million = $0.0028
    cost = compute_cost(
        _usage(1_200, 400),
        [_row("per-1m-input-tokens", 1.0), _row("per-1m-output-tokens", 4.0)],
    )
    assert cost.cents == pytest.approx(0.28)
    assert cost.currency == "USD"


def test_cached_tokens_use_their_own_price():
    cost = compute_cost(
        _usage(1_000_000, 0, cached=600_000),
        [_row("per-1m-input-tokens", 1.0), _row("per-1m-cached-input-tokens", 0.1)],
    )
    # 400 000 fresh at $1 + 600 000 cached at $0.10 = $0.46
    assert cost.cents == pytest.approx(46.0)


def test_rows_the_answer_cannot_count_are_left_out():
    cost = compute_cost(
        _usage(1_000_000, 0),
        [_row("per-1m-input-tokens", 1.0), _row("per-1k-requests", 5.0)],
    )
    assert cost.cents == pytest.approx(100.0)


def test_no_usage_or_no_price_means_no_cost():
    assert compute_cost(None, [_row("per-1m-input-tokens", 1.0)]) is None
    assert compute_cost(_usage(10, 10), []) is None


def test_mixed_currencies_are_refused():
    with pytest.raises(ValueError):
        compute_cost(
            _usage(10, 10),
            [_row("per-1m-input-tokens", 1.0, "USD"), _row("per-1m-output-tokens", 1.0, "EUR")],
        )
