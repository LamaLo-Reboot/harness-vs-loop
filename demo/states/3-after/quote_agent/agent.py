"""The agent: a model, a loop of a few lines, four tools.

The loop asks the model what to do next. When it asks for a tool, our code runs it and hands
back the result; when it answers with text, the turn is over.
"""

import json

from quote_agent import display, harness, tools
from quote_agent.backends import Backend
from quote_agent.costs import compute_cost


class Agent:
    def __init__(self, backend: Backend):
        self.conversation: list[dict] = []
        self.spent_cents = 0.0
        self.turn = 0
        self.switch_to(backend)

    def switch_to(self, backend: Backend) -> None:
        self.backend = backend
        self.client = backend.client()

    async def ask(self, request: str) -> str:
        if harness.memory_is_full(self.conversation):
            self.conversation = harness.compress(self.conversation)
        self.conversation.append({"role": "user", "content": request})
        self.turn = 0
        while True:
            response = await self._call_model()
            calls = [item for item in response["output"] if item["type"] == "function_call"]
            if not calls:
                problem = harness.check_before_done()
                display.harness_event("✘" if problem else "✔", problem or 'check before "done": nothing to report')
                if problem is None:
                    return _text_of(response)
                self.conversation.append({"role": "user", "content": problem})
                continue
            for call in calls:
                arguments = json.loads(call["arguments"] or "{}")
                if call["name"] in harness.NEEDS_APPROVAL and not harness.approved(call["name"], arguments):
                    result = harness.REFUSED
                else:
                    result = tools.run(call["name"], arguments)
                display.tool_call(call["name"], call["arguments"], result)
                self._hand_back(call, result)

    async def _call_model(self) -> dict:
        self.turn += 1
        response = await self.client.create_response(
            {
                "model": self.backend.model,
                "instructions": harness.INSTRUCTIONS,
                "input": self.conversation,
                "tools": tools.DEFINITIONS,
            }
        )
        self.conversation += response["output"]
        cost = compute_cost(response.get("usage"), (response.get("lamalo") or {}).get("pricing", []))
        if cost:
            self.spent_cents += cost.cents
        display.model_call(self.turn, response.get("model") or self.backend.model, cost, self.spent_cents)
        return response

    def _hand_back(self, call: dict, result: str) -> None:
        self.conversation.append({"type": "function_call_output", "call_id": call["call_id"], "output": result})


def _text_of(response: dict) -> str:
    return "\n".join(
        part["text"]
        for item in response["output"]
        if item["type"] == "message"
        for part in item["content"]
        if part["type"] == "output_text"
    )
