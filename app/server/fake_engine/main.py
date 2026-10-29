"""A fake engine for people who clone the repo.

It answers `POST /v1/responses` in the real engine's format by replaying what the real engine
answered during our rehearsals (see `recordings.py`), for the demo step `./demo/reset` last set.
A request that was never recorded gets a short message instead. Run it with:

    uv run uvicorn fake_engine.main:app --port 8089
"""

import time
import uuid

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

from fake_engine import recordings
from quote_agent import demo_state

CONTACT = "Answer from the fake engine. To use the real engine: contact lamalo.ai."
NOT_RECORDED = (
    "The fake engine only knows the requests recorded for the demo, and this one isn't one of them. "
    "Type the request written in the demo notes, or switch to Ollama with /backend ollama."
)
MODEL = "fake/model"
# Made-up prices, so cloners still see a cost per call. They are not any real model's prices.
PRICING = [
    {"pricing_unit_type": "per-1m-input-tokens", "cost_per_unit": 1.0, "currency": "USD"},
    {"pricing_unit_type": "per-1m-output-tokens", "cost_per_unit": 4.0, "currency": "USD"},
]


class ResponseRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    input: str | list[dict]


def _usage(input_tokens: int, output_tokens: int) -> dict:
    return {
        "input_tokens": input_tokens,
        "input_tokens_details": {"cached_tokens": 0},
        "output_tokens": output_tokens,
        "output_tokens_details": {"reasoning_tokens": 0},
        "total_tokens": input_tokens + output_tokens,
    }


def _message(text: str) -> dict:
    return {
        "type": "message",
        "role": "assistant",
        "status": "completed",
        "content": [{"type": "output_text", "text": text, "annotations": []}],
    }


def _with_contact(output: list[dict]) -> list[dict]:
    """The contact line rides at the end of every text answer, never inside a tool call."""
    signed = []
    for item in output:
        if item["type"] == "message":
            content = [
                {**part, "text": f"{part['text']}\n\n({CONTACT})"} if part["type"] == "output_text" else part
                for part in item["content"]
            ]
            item = {**item, "content": content}
        signed.append(item)
    return signed


def create_app() -> FastAPI:
    app = FastAPI(title="Fake engine")

    @app.post("/v1/responses")
    def create_response(request: ResponseRequest) -> dict:
        body = request.model_dump()
        recorded = recordings.load(demo_state.current()).get(recordings.key(body))
        if recorded:
            output, usage, model = recorded["output"], recorded["usage"], f"{recorded['model']} (replayed)"
        else:
            output, usage, model = [_message(NOT_RECORDED)], _usage(1_200, 400), MODEL
        return {
            "id": f"resp_{uuid.uuid4().hex}",
            "object": "response",
            "created_at": int(time.time()),
            "status": "completed",
            "model": model,
            "output": _with_contact(output),
            "usage": usage,
            "error": None,
            "lamalo": {"pricing": PRICING},
        }

    return app


app = create_app()
