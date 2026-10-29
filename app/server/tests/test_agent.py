import json

import httpx
import pytest

from quote_agent import tools
from quote_agent.agent import Agent
from quote_agent.backends import Backend
from quote_agent.engine_client import EngineClient

PRICING = [{"pricing_unit_type": "per-1m-output-tokens", "cost_per_unit": 10.0, "currency": "USD"}]


def _answer(output: list[dict]) -> dict:
    return {"status": "completed", "output": output, "usage": {"output_tokens": 1_000}, "lamalo": {"pricing": PRICING}}


def _scripted_model(answers: list[dict], requests: list[dict]) -> httpx.MockTransport:
    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(json.loads(request.content))
        return httpx.Response(200, json=answers[len(requests) - 1])

    return httpx.MockTransport(handle)


@pytest.fixture
def isolated_data(tmp_path, monkeypatch):
    data = tmp_path / "data"
    data.mkdir()
    (data / "supplier_prices.txt").write_text("KB-WL  Clavier sans fil  28 $\n", encoding="utf-8")
    monkeypatch.setattr(tools, "DATA_DIR", data)
    monkeypatch.setattr(tools, "OUT_DIR", tmp_path / "out")
    return tmp_path


def _agent(transport: httpx.MockTransport) -> Agent:
    agent = Agent(Backend("test", "http://model", "test/model", "key"))
    agent.client = EngineClient("http://model", "key", transport=transport)
    return agent


async def test_the_loop_runs_the_tool_the_model_asks_for_and_hands_back_the_result(isolated_data):
    requests: list[dict] = []
    agent = _agent(
        _scripted_model(
            [
                _answer([{"type": "function_call", "call_id": "c1", "name": "get_supplier_prices", "arguments": "{}"}]),
                _answer([{"type": "message", "content": [{"type": "output_text", "text": "Keyboard: $28."}]}]),
            ],
            requests,
        )
    )

    answer = await agent.ask("How much is the keyboard?")

    assert answer == "Keyboard: $28."
    assert len(requests) == 2
    handed_back = requests[1]["input"][-1]
    assert handed_back["type"] == "function_call_output"
    assert handed_back["call_id"] == "c1"
    assert "28 $" in handed_back["output"]
    assert agent.spent_cents == pytest.approx(2.0)  # 2 calls × 1 000 tokens at $10 per million


async def test_every_request_carries_the_instructions_and_the_four_tools(isolated_data):
    requests: list[dict] = []
    agent = _agent(_scripted_model([_answer([{"type": "message", "content": []}])], requests))

    await agent.ask("Bonjour")

    assert requests[0]["instructions"]
    assert [tool["name"] for tool in requests[0]["tools"]] == [
        "get_supplier_prices",
        "get_exchange_rate",
        "send_quote",
        "save_quote",
    ]


def test_saved_quotes_get_a_number(isolated_data):
    line = [{"ref": "KB-WL", "quantity": 2, "unit_price_eur": 30.2}]
    assert tools.run("save_quote", {"customer": "Martin", "lines": line, "payment_terms": "30 days"}) == "Quote Q-0001 saved."
    assert tools.run("save_quote", {"customer": "Martin", "lines": line, "payment_terms": "30 days"}) == "Quote Q-0002 saved."


def test_sent_quotes_land_in_the_outbox(isolated_data):
    assert tools.run("send_quote", {"customer": "Martin", "text": "Quote"}) == "Quote sent to Martin."
    assert len(list((isolated_data / "out" / "sent").iterdir())) == 1


def test_the_bank_rate_is_read_from_the_ecb_feed():
    xml = "<Cube time='2026-10-28'><Cube currency='USD' rate='1.1133'/><Cube currency='JPY' rate='170.2'/></Cube>"
    assert tools.parse_ecb_rate(xml, "usd") == "1 EUR = 1.1133 USD (ECB reference rate of 2026-10-28)"
    assert tools.parse_ecb_rate(xml, "XXX") == "No rate for the currency XXX."
