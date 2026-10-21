"""Client for the endpoint behind veiculos.fipe.org.br (undocumented, not an official API).

Every call is a form-encoded POST that returns JSON. The client spaces calls out (rate limit), retries
transient failures with backoff and never runs requests in parallel (CLAUDE.md, "Coleta na API da FIPE").
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

BASE_URL = "https://veiculos.fipe.org.br/api/veiculos/"
USER_AGENT = "fipe-collector/2 (+https://github.com/stuaninauts/fipe)"
CAR = 1  # codigoTipoVeiculo: 1 = cars (2 = motorcycles, 3 = trucks)

# Status codes worth another try: rate limiting and server-side hiccups.
RETRYABLE = frozenset({429, 500, 502, 503, 504})


class ApiError(Exception):
    """A call that still failed after every retry, or that answered with an error payload."""


@dataclass(frozen=True)
class Response:
    status: int
    body: str


# A transport takes (endpoint, form params) and returns the raw response. Tests swap in a fake one.
Transport = Callable[[str, Mapping[str, str]], Response]


def http_transport(endpoint: str, params: Mapping[str, str], timeout: float = 30.0) -> Response:
    data = urllib.parse.urlencode(params).encode()
    request = urllib.request.Request(
        BASE_URL + endpoint,
        data=data,
        method="POST",
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://veiculos.fipe.org.br/",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            return Response(resp.status, resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        return Response(err.code, err.read().decode("utf-8", errors="replace"))


@dataclass
class Client:
    transport: Transport = http_transport
    min_interval: float = 1.0  # seconds between the start of two calls
    max_attempts: int = 5
    backoff: float = 5.0  # first wait after a failure; doubles on each retry
    clock: Callable[[], float] = time.monotonic
    sleep: Callable[[float], None] = time.sleep
    calls: int = field(default=0, init=False)
    _last_call: float | None = field(default=None, init=False)

    def _wait_turn(self) -> None:
        if self._last_call is not None:
            remaining = self.min_interval - (self.clock() - self._last_call)
            if remaining > 0:
                self.sleep(remaining)
        self._last_call = self.clock()

    def post(self, endpoint: str, params: Mapping[str, str]) -> str:
        """Return the JSON body of a successful call, as text. Raises ApiError when it gives up."""
        last = ""
        for attempt in range(1, self.max_attempts + 1):
            self._wait_turn()
            self.calls += 1
            try:
                resp = self.transport(endpoint, params)
            except (urllib.error.URLError, TimeoutError, ConnectionError) as err:
                last = f"network error: {err}"
            else:
                if resp.status == 200:
                    _raise_on_error_payload(endpoint, params, resp.body)
                    return resp.body
                last = f"HTTP {resp.status}"
                if resp.status not in RETRYABLE:
                    break
            if attempt < self.max_attempts:
                self.sleep(self.backoff * 2 ** (attempt - 1))
        raise ApiError(f"{endpoint} {dict(params)}: {last}")


def _raise_on_error_payload(endpoint: str, params: Mapping[str, str], body: str) -> None:
    # The endpoint answers 200 with {"codigo": "...", "erro": "..."} when a combination does not exist.
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as err:
        raise ApiError(f"{endpoint} {dict(params)}: invalid JSON") from err
    if isinstance(payload, dict) and "erro" in payload:
        raise ApiError(f"{endpoint} {dict(params)}: {payload['erro']}")
