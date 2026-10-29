"""Where the model runs. All three answer `POST /v1/responses` with the same body, so switching
only changes the address, the model name and the key.

- engine: the cloud models, through the engine (needs a key).
- ollama: a small model on this laptop, no network.
- fake: the fake engine in `fake_engine/`, for people who clone the repo without a key.

On the engine, the model can also be `auto`: the engine picks it, steered by `tiers`
(`budget`, `latency`, `performance`, each 0 to 1).

With `RECORD=1`, every call to the model is also written to the current demo step's recording,
for the fake engine to replay.
"""

import os
from dataclasses import dataclass, replace

from fake_engine.recordings import Recorder
from quote_agent import demo_state
from quote_agent.engine_client import EngineClient

NAMES = ("engine", "ollama", "fake")
TIERS = ("budget", "latency", "performance")
TIER_LEVEL = 0.9


@dataclass(frozen=True)
class Backend:
    name: str
    url: str
    model: str
    key: str
    tiers: dict[str, float] | None = None

    def client(self) -> EngineClient:
        if os.environ.get("RECORD") == "1":
            return RecordingClient(self.url, self.key, tiers=self.tiers)
        return EngineClient(self.url, self.key, tiers=self.tiers)

    @property
    def label(self) -> str:
        if self.tiers:
            return f"{self.model} ({', '.join(self.tiers)})"
        return self.model


class RecordingClient(EngineClient):
    async def create_response(self, body: dict) -> dict:
        answer = await super().create_response(body)
        Recorder(demo_state.current()).write(body, answer)
        return answer


def load(name: str) -> Backend:
    if name == "engine":
        return Backend(
            "engine",
            os.environ.get("ENGINE_URL", "http://localhost:8088"),
            os.environ.get("ENGINE_DEFAULT_MODEL", "anthropic/claude-sonnet-5-5"),
            os.environ.get("ENGINE_KEY", ""),
        )
    if name == "ollama":
        return Backend(
            "ollama",
            os.environ.get("OLLAMA_URL", "http://localhost:11434"),
            os.environ.get("OLLAMA_MODEL", "qwen3.5:4b"),
            "ollama",
        )
    if name == "fake":
        return Backend("fake", os.environ.get("FAKE_ENGINE_URL", "http://localhost:8089"), "fake/model", "fake")
    raise ValueError(f"unknown backend {name!r}, expected one of {', '.join(NAMES)}")


def with_model(backend: Backend, model: str, tier: str | None = None) -> Backend:
    """The same backend with another model; a tier only steers `auto`."""
    return replace(backend, model=model, tiers={tier: TIER_LEVEL} if tier else None)
