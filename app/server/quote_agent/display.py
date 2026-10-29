"""What the audience sees of each loop turn: one line per model call, one line per tool call,
and one line for each thing the harness does on its own (a check, a limit, a compressed memory).
"""

import json

from quote_agent.costs import Cost

DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"
ARGUMENTS_WIDTH = 70
RESULT_WIDTH = 70


def model_call(turn: int, model: str, cost: Cost | None, spent_cents: float) -> None:
    price = f"{cost.cents:.2f} ¢ {cost.currency} · total {spent_cents:.2f} ¢" if cost else "no price (local model)"
    print(f"{DIM}  ⟳ turn {turn} · {model} · {price}{RESET}")


def tool_call(name: str, arguments: str, result: str) -> None:
    shown_arguments = _short(json.dumps(json.loads(arguments or "{}"), ensure_ascii=False), ARGUMENTS_WIDTH)
    if shown_arguments == "{}":
        shown_arguments = ""
    lines = result.strip().splitlines() or [""]
    shown_result = _short(lines[0], RESULT_WIDTH) + (" …" if len(lines) > 1 and len(lines[0]) <= RESULT_WIDTH else "")
    print(f"  🔧 {BOLD}{name}{RESET}({shown_arguments}) → {shown_result}")


def harness_event(icon: str, text: str) -> None:
    """Something our harness did, not the model: shown in bold so it stands out from the loop."""
    print(f"  {icon} {BOLD}{text}{RESET}")


def quoted(text: str) -> None:
    for line in text.splitlines():
        print(f"{DIM}     │ {line}{RESET}")


def _short(text: str, width: int) -> str:
    return text if len(text) <= width else text[: width - 1] + "…"
