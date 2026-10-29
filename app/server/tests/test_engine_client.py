import httpx
import pytest

from fake_engine import main as fake_engine
from fake_engine import recordings
from quote_agent.costs import compute_cost
from quote_agent.engine_client import EngineClient, EngineError

REQUEST = {"instructions": "You are the quote assistant.", "input": [{"role": "user", "content": "A quote for 50 HDMI cables"}]}


@pytest.fixture
def fake_step(tmp_path, monkeypatch):
    monkeypatch.setattr(recordings, "RECORDINGS_DIR", tmp_path)
    monkeypatch.setattr(fake_engine.demo_state, "current", lambda: "1-before")
    return tmp_path


def _client() -> EngineClient:
    transport = httpx.ASGITransport(app=fake_engine.create_app())
    return EngineClient("http://fake-engine", "test-key", transport=transport)


async def test_a_request_never_recorded_gets_the_contact_line_and_a_cost(fake_step):
    body = await _client().create_response(REQUEST)
    text = body["output"][0]["content"][0]["text"]
    assert fake_engine.NOT_RECORDED in text
    assert fake_engine.CONTACT in text
    assert compute_cost(body["usage"], body["lamalo"]["pricing"]).cents == pytest.approx(0.28)


async def test_a_recorded_request_is_replayed_with_the_contact_line_on_text_only_and_made_up_prices(fake_step):
    real_answer = {
        "id": "resp_1",
        "model": "anthropic/claude-sonnet-5-5",
        "output": [
            {"type": "reasoning", "id": "rs_1", "summary": []},
            {"type": "message", "id": "msg_1", "content": [{"type": "output_text", "text": "Here is the quote."}]},
            {"type": "function_call", "id": "fc_1", "call_id": "c1", "name": "get_supplier_prices", "arguments": "{}"},
        ],
        "usage": {"input_tokens": 1_000, "output_tokens": 100},
        "lamalo": {"pricing": [{"pricing_unit_type": "per-1m-input-tokens", "cost_per_unit": 3.0, "currency": "USD", "internal": "x"}]},
    }
    recordings.Recorder("1-before").write(REQUEST, real_answer)

    body = await _client().create_response(REQUEST)

    assert body["model"] == "anthropic/claude-sonnet-5-5 (replayed)"
    assert [item["type"] for item in body["output"]] == ["message", "function_call"]
    assert body["output"][0]["content"][0]["text"] == f"Here is the quote.\n\n({fake_engine.CONTACT})"
    assert body["output"][1]["arguments"] == "{}"
    assert body["lamalo"]["pricing"] == fake_engine.PRICING
    assert "lamalo" not in (recordings.RECORDINGS_DIR / "1-before.jsonl").read_text()


def test_the_replay_key_ignores_tool_results_but_not_what_the_user_typed():
    def body(rate: str, request: str = "Quote Martin") -> dict:
        return {
            "instructions": "x",
            "input": [
                {"role": "user", "content": request},
                {"type": "function_call", "call_id": "c1", "name": "get_exchange_rate", "arguments": '{"currency": "USD"}'},
                {"type": "function_call_output", "call_id": "c1", "output": rate},
            ],
        }

    assert recordings.key(body("1 EUR = 1.1133 USD")) == recordings.key(body("1 EUR = 1.0950 USD"))
    assert recordings.key(body("1 EUR = 1.1133 USD")) != recordings.key(body("1 EUR = 1.1133 USD", "Quote Durand"))


async def test_engine_errors_are_raised(fake_step):
    with pytest.raises(EngineError, match="422"):
        await _client().create_response({"no_input": True})


async def test_tiers_ride_in_the_lamalo_extension_only_when_set():
    sent = []

    def answer(request: httpx.Request) -> httpx.Response:
        sent.append(request.read())
        return httpx.Response(200, json={"output": []})

    transport = httpx.MockTransport(answer)
    await EngineClient("http://engine", "key", transport=transport).create_response({"model": "x"})
    await EngineClient("http://engine", "key", transport=transport, tiers={"budget": 0.9}).create_response({"model": "auto"})
    assert b"lamalo" not in sent[0]
    assert b'"lamalo":{"tiers":{"budget":0.9}}' in sent[1].replace(b" ", b"")
