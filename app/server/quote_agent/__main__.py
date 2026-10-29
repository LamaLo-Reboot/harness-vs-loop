"""The terminal where we talk to the agent. Run it with `uv run python -m quote_agent`.

Commands: `/backend engine|ollama|fake` switches where the model runs, even mid-conversation;
`/model auto [budget|latency|performance]` lets the engine pick the model, `/model <id>` names
one, and `/model` alone goes back to the one in `.env` (engine only); `/quit` leaves. Ctrl+C stops the agent's current turn and forgets it, without leaving.
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from quote_agent import backends, demo_state
from quote_agent.agent import Agent
from quote_agent.engine_client import EngineError

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _banner(agent: Agent) -> str:
    return (
        f"Quote agent · {agent.backend.label} via {agent.backend.name} · {demo_state.label(demo_state.current())}"
        " · /backend engine|ollama|fake · /model · /quit"
    )


def main() -> None:
    loop = asyncio.new_event_loop()
    agent = Agent(backends.load(os.environ.get("BACKEND", "fake")))
    print(_banner(agent))
    while True:
        try:
            request = input("\nyou › ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not request:
            continue
        if request == "/quit":
            break
        if request.startswith("/backend"):
            name = request.removeprefix("/backend").strip()
            if name not in backends.NAMES:
                print(f"  choices: {', '.join(backends.NAMES)}")
                continue
            agent.switch_to(backends.load(name))
            print(_banner(agent))
            continue
        if request.startswith("/model"):
            words = request.removeprefix("/model").split()
            if agent.backend.name != "engine" or len(words) > 2:
                print(f"  on the engine: /model auto [{'|'.join(backends.TIERS)}], /model <provider/model> or /model")
                continue
            if len(words) == 2 and (words[0] != "auto" or words[1] not in backends.TIERS):
                print(f"  a tier goes only with auto: {', '.join(backends.TIERS)}")
                continue
            model = words[0] if words else backends.load("engine").model
            agent.switch_to(backends.with_model(agent.backend, model, words[1] if len(words) == 2 else None))
            print(_banner(agent))
            continue

        remembered = len(agent.conversation)
        turn = loop.create_task(agent.ask(request))
        try:
            answer = loop.run_until_complete(turn)
        except KeyboardInterrupt:
            turn.cancel()
            loop.run_until_complete(asyncio.gather(turn, return_exceptions=True))
            del agent.conversation[remembered:]
            print("\n  ⏹ interrupted: this turn is forgotten")
            continue
        except EngineError as error:
            del agent.conversation[remembered:]
            print(f"  ⚠ {error}")
            continue
        print(f"\nagent › {answer}")
    loop.close()


if __name__ == "__main__":
    main()
