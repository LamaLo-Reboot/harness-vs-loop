"""Which step of the demo the agent is in, as `./demo/reset` last left it.

The reset script writes the step to `app/server/.demo-state`. The banner shows it, and the fake
engine uses it to pick which recording to replay.
"""

from pathlib import Path

STATE_FILE = Path(__file__).resolve().parent.parent / ".demo-state"
START = "0-start"


def current() -> str:
    return STATE_FILE.read_text(encoding="utf-8").strip() if STATE_FILE.exists() else START


def label(state: str) -> str:
    if state == START:
        return "start"
    example, moment = state.split("-")
    return f"example {example}, {moment}"
