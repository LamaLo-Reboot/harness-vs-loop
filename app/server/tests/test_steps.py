"""Each step of the demo, as `./demo/reset` builds it, with a scripted model.

These check our harness, not the model: the model's answers are written in advance, and each
test checks what our code does with them.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest

SERVER_DIR = Path(__file__).resolve().parent.parent
RESET = SERVER_DIR.parent.parent / "demo" / "reset"
STEPS = ["0-start"] + [f"{example}-{moment}" for example in range(1, 6) for moment in ("before", "after")]


@pytest.fixture
def load_step(tmp_path, monkeypatch):
    """Builds a step in a copy of the agent and imports that copy instead of the live one."""
    live_modules = {name: module for name, module in sys.modules.items() if name.startswith("quote_agent")}

    def load(step: str) -> SimpleNamespace:
        server = tmp_path / step
        shutil.copytree(SERVER_DIR / "quote_agent", server / "quote_agent", ignore=shutil.ignore_patterns("__pycache__"))
        arguments = ["0"] if step == "0-start" else step.split("-")
        subprocess.run([sys.executable, RESET, *arguments], env={**os.environ, "SERVER_DIR": str(server)}, check=True, capture_output=True)
        for name in [name for name in sys.modules if name.startswith("quote_agent")]:
            sys.modules.pop(name)
        monkeypatch.syspath_prepend(str(server))
        from quote_agent import agent, backends, engine_client, harness, tools

        assert Path(harness.__file__).is_relative_to(server)
        return SimpleNamespace(agent=agent, backends=backends, engine_client=engine_client, harness=harness, tools=tools, server=server)

    yield load
    for name in [name for name in sys.modules if name.startswith("quote_agent")]:
        sys.modules.pop(name)
    sys.modules.update(live_modules)


def _answer(*items: dict) -> dict:
    return {"output": list(items), "usage": {"output_tokens": 1_000}, "lamalo": {"pricing": [{"pricing_unit_type": "per-1m-output-tokens", "cost_per_unit": 10.0, "currency": "USD"}]}}


def _call(name: str, arguments: dict, call_id: str = "c1") -> dict:
    return {"type": "function_call", "call_id": call_id, "name": name, "arguments": json.dumps(arguments)}


def _text(text: str) -> dict:
    return {"type": "message", "content": [{"type": "output_text", "text": text}]}


def _agent(step: SimpleNamespace, answers: list[dict], requests: list[dict]):
    """An agent whose model answers in order, repeating the last answer when the list runs out."""

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(json.loads(request.content))
        return httpx.Response(200, json=answers[min(len(requests), len(answers)) - 1])

    agent = step.agent.Agent(step.backends.Backend("test", "http://model", "test/model", "key"))
    agent.client = step.engine_client.EngineClient("http://model", "key", transport=httpx.MockTransport(handle))
    return agent


def _save(customer: str, ref: str, terms: str = "payment within 30 days", call_id: str = "c1") -> dict:
    return _call("save_quote", {"customer": customer, "lines": [{"ref": ref, "quantity": 2, "unit_price_eur": 50.0}], "payment_terms": terms}, call_id)


@pytest.mark.parametrize("step_name", STEPS)
async def test_every_step_runs_a_plain_answer(load_step, step_name):
    step = load_step(step_name)
    assert await _agent(step, [_answer(_text("Hello."))], []).ask("Hello") == "Hello."


async def test_example_1_after_writes_the_carton_rule_down(load_step):
    assert "box of 10" not in load_step("1-before").harness.INSTRUCTIONS
    assert "box of 10" in load_step("1-after").harness.INSTRUCTIONS


async def test_example_2_before_says_done_with_the_unpaid_customer_on_30_days(load_step):
    step = load_step("2-before")
    requests = []
    answer = await _agent(step, [_answer(_save("Bernard", "MS-WL")), _answer(_text("Done."))], requests).ask("Quote Bernard")
    assert answer == "Done."
    assert len(requests) == 2


async def test_example_2_after_checks_the_account_before_done_and_feeds_the_problem_back(load_step):
    step = load_step("2-after")
    requests = []
    answers = [
        _answer(_save("Bernard Ltd", "MS-WL")),
        _answer(_text("Done.")),
        _answer(_save("Bernard Ltd", "MS-WL", "payment with the order", "c2")),
        _answer(_text("Fixed.")),
    ]
    answer = await _agent(step, answers, requests).ask("Quote Bernard")
    assert answer == "Fixed."
    fed_back = requests[2]["input"][-1]
    assert fed_back["role"] == "user"
    assert "2 unpaid invoices: payment with the order is required" in fed_back["content"]


async def test_example_3_before_loses_what_was_said_when_memory_is_compressed(load_step):
    step = load_step("3-before")
    requests = []
    agent = _agent(step, [_answer(_save("Durand", "SCR-24")), _answer(_text("Saved."))], requests)
    await agent.ask("Quote Durand. Never send it without my approval.")
    agent.client = _agent(step, [_answer(_text("Saved."))], requests).client
    await agent.ask("Quote Petit")
    agent.client = _agent(step, [_answer(_text("Sent."))], requests).client
    await agent.ask("Send today's quotes.")
    summary = requests[-1]["input"][0]["content"]
    assert "Q-0001 for Durand" in summary
    assert "approval" not in summary


async def test_example_3_after_sends_only_with_a_yes_typed_by_a_human(load_step, monkeypatch):
    step = load_step("3-after")
    monkeypatch.setattr("builtins.input", lambda prompt: "n")
    requests = []
    answers = [_answer(_call("send_quote", {"customer": "Durand", "text": "Quote"})), _answer(_text("Not sent."))]
    await _agent(step, answers, requests).ask("Send today's quotes.")
    assert requests[1]["input"][-1]["output"] == step.harness.REFUSED
    assert step.tools.sent_to() == []


async def test_example_4_before_the_bank_answers_in_progress_forever(load_step):
    step = load_step("4-before")
    answers = [step.tools.get_exchange_rate("USD") for _ in range(12)]
    assert all(answer.startswith("Calculation in progress") for answer in answers)


async def test_example_4_after_stops_after_5_attempts_and_alerts_a_human(load_step):
    step = load_step("4-after")
    requests = []
    answer = await _agent(step, [_answer(_call("get_exchange_rate", {"currency": "USD"}))], requests).ask("Quote Moreau")
    assert answer.startswith("Stopped: 5 attempts at get_exchange_rate")
    assert len(requests) == 6
    assert "stopped" in (step.server / "out" / "alerts.txt").read_text(encoding="utf-8")


async def test_example_5_before_the_old_software_only_says_err_4012(load_step):
    step = load_step("5-before")
    requests = []
    await _agent(step, [_answer(_save("Garnier", "HDMI-2M")), _answer(_text("Error."))], requests).ask("Quote Garnier")
    assert requests[1]["input"][-1]["output"] == "ERR 4012"


async def test_example_5_after_the_refusal_says_what_to_do_instead(load_step):
    step = load_step("5-after")
    requests = []
    await _agent(step, [_answer(_save("Garnier", "HDMI-2M")), _answer(_text("Fixed."))], requests).ask("Quote Garnier")
    assert "Reference HDMI-2M was replaced by HDMI-2M-V2" in requests[1]["input"][-1]["output"]
