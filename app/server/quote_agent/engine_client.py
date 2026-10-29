"""The only place in the demo that calls a model.

It speaks the OpenAI Responses format on `POST /v1/responses`, which the engine, Ollama and
the fake engine all answer the same way. Tiers, when set, go in the engine's own `lamalo`
extension: they steer the engine's choice when the model is `auto`.
"""

import httpx


class EngineError(Exception):
    pass


class EngineClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        transport: httpx.AsyncBaseTransport | None = None,
        timeout_seconds: float = 120,
        tiers: dict[str, float] | None = None,
    ):
        self._tiers = tiers
        self._http = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            transport=transport,
            timeout=timeout_seconds,
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def create_response(self, body: dict) -> dict:
        if self._tiers:
            body = {**body, "lamalo": {"tiers": self._tiers}}
        try:
            response = await self._http.post("/v1/responses", json=body)
        except httpx.HTTPError as exc:
            raise EngineError(f"engine unreachable: {exc}") from exc
        if response.is_error:
            raise EngineError(f"engine answered {response.status_code}: {response.text}")
        return response.json()
