"""Real engine answers, recorded during rehearsals and replayed by the fake engine.

Each step of the demo has its own file, `recordings/<step>.jsonl`, one line per model call: the
key of the request and the answer the real engine gave. To record a step, run the agent on the
engine with `RECORD=1` in `app/server/.env`; it replaces that step's recording.

The key is what the model was shown: the instructions, what the user typed, which tools it called
with which arguments. The text of the tool results is left out on purpose: the bank's rate changes
every day, and the replay should still find its way.
"""

import hashlib
import json
from pathlib import Path

RECORDINGS_DIR = Path(__file__).resolve().parent / "recordings"


def key(body: dict) -> str:
    shown = []
    for item in body["input"] if isinstance(body["input"], list) else [{"role": "user", "content": body["input"]}]:
        if item.get("role") == "user":
            shown.append(["user", item["content"]])
        elif item.get("type") == "function_call":
            shown.append(["call", item["name"], item["arguments"]])
        elif item.get("type") == "function_call_output":
            shown.append(["result"])
        elif item.get("type") == "message":
            shown.append(["answer"])
    raw = json.dumps([body.get("instructions", ""), shown], ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def load(step: str) -> dict[str, dict]:
    path = RECORDINGS_DIR / f"{step}.jsonl"
    if not path.exists():
        return {}
    answers = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        entry = json.loads(line)
        answers.setdefault(entry["key"], entry["answer"])
    return answers


def keep(answer: dict) -> dict:
    """Only what the replay needs: what the model said and how many tokens it used. The engine's
    price list stays out of the public repo; the fake engine bills with its own."""
    return {
        "model": answer.get("model"),
        "output": [_without_id(item) for item in answer["output"] if item["type"] in ("message", "function_call")],
        "usage": answer.get("usage"),
    }


def _without_id(item: dict) -> dict:
    return {name: value for name, value in item.items() if name != "id"}


class Recorder:
    """Writes each call of one step to its recording, starting the file afresh."""

    _started: set[Path] = set()

    def __init__(self, step: str):
        self.path = RECORDINGS_DIR / f"{step}.jsonl"
        if self.path not in Recorder._started:
            RECORDINGS_DIR.mkdir(exist_ok=True)
            self.path.write_text("", encoding="utf-8")
            Recorder._started.add(self.path)

    def write(self, body: dict, answer: dict) -> None:
        entry = {"key": key(body), "answer": keep(answer)}
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(entry, ensure_ascii=False) + "\n")
