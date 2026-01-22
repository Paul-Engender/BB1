# Gateways â€“ Code (Upload-Safe Consolidation)

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/client.py

```
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from .config import GatewayConfig, load_config
from .errors import GatewayConfigError
from .logging import log_event, prompt_hash8
from .retry import RetryPolicy, run_with_retry
from .providers.gemini import call_gemini
from .providers.offline import call_offline

# openai provider can be added later without changing this contract.


@dataclass
class CallOptions:
    provider: Optional[str] = None
    model: Optional[str] = None
    timeout_s: Optional[float] = None
    temperature: Optional[float] = None  # accepted but provider may ignore
    max_tokens: Optional[int] = None     # accepted but provider may ignore


class AIGatewayClient:
    """
    AI Gateway public API.
    Contract: accepts prompt, returns raw model text unchanged.
    Handles only transport concerns (security, retries, stability, logging).
    """

    def __init__(self, cfg: Optional[GatewayConfig] = None):
        self.cfg = cfg or load_config()

    def call(self, prompt: str, *, options: Optional[CallOptions] = None) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt must be a non-empty string")

        opt = options or CallOptions()
        provider = (opt.provider or self.cfg.provider).strip().lower()
        model = (opt.model or self.cfg.model).strip()
        timeout_s = float(opt.timeout_s or self.cfg.timeout_s)

        ph = prompt_hash8(prompt)
        t0 = time.time()

        policy = RetryPolicy(
            max_retries=self.cfg.max_retries,
            backoff_base_s=self.cfg.backoff_base_s,
            backoff_max_s=self.cfg.backoff_max_s,
        )

        log_event(
            "ai_gateway.call.start",
            provider=provider,
            model=model,
            timeout_s=timeout_s,
            prompt_hash8=ph,
        )

        def _invoke() -> str:
            if provider == "offline":
                return call_offline(prompt=prompt, model=model, timeout_s=timeout_s)

            if provider == "gemini":
                if not self.cfg.gemini_api_key:
                    raise GatewayConfigError("Missing GEMINI_API_KEY (or AI_GATEWAY_GEMINI_API_KEY).")
                return call_gemini(
                    prompt=prompt,
                    model=model,
                    api_key=self.cfg.gemini_api_key,
                    timeout_s=timeout_s,
                )

            raise GatewayConfigError(f"Unknown provider: {provider}")

        try:
            out = run_with_retry(_invoke, policy)
            ms = int((time.time() - t0) * 1000)
            log_event(
                "ai_gateway.call.ok",
                provider=provider,
                model=model,
                latency_ms=ms,
                prompt_hash8=ph,
            )
            return out
        except Exception as e:
            ms = int((time.time() - t0) * 1000)
            log_event(
                "ai_gateway.call.fail",
                provider=provider,
                model=model,
                latency_ms=ms,
                prompt_hash8=ph,
                error_type=type(e).__name__,
            )
            raise

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/config.py

```
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class GatewayConfig:
    provider: str
    model: str
    timeout_s: float
    max_retries: int
    backoff_base_s: float
    backoff_max_s: float
    # Provider keys (kept here to avoid scattering env reads)
    gemini_api_key: str | None


def _get_float(name: str, default: float) -> float:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    try:
        return float(v)
    except ValueError:
        return default


def _get_int(name: str, default: int) -> int:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    try:
        return int(v)
    except ValueError:
        return default


def load_config() -> GatewayConfig:
    # Stable, boring env var surface
    provider = os.getenv("AI_GATEWAY_PROVIDER", "gemini").strip().lower()
    model = os.getenv("AI_GATEWAY_MODEL", "").strip()

    timeout_s = _get_float("AI_GATEWAY_TIMEOUT_S", 60.0)
    max_retries = _get_int("AI_GATEWAY_RETRIES", 3)
    backoff_base_s = _get_float("AI_GATEWAY_BACKOFF_BASE_S", 1.0)
    backoff_max_s = _get_float("AI_GATEWAY_BACKOFF_MAX_S", 20.0)

    # Provider-specific keys (still env-only)
    gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("AI_GATEWAY_GEMINI_API_KEY")

    # Provide sane default model if not set
    if not model:
        if provider == "gemini":
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        elif provider == "offline":
            model = "offline"
        else:
            model = "default"

    return GatewayConfig(
        provider=provider,
        model=model,
        timeout_s=timeout_s,
        max_retries=max_retries,
        backoff_base_s=backoff_base_s,
        backoff_max_s=backoff_max_s,
        gemini_api_key=gemini_api_key,
    )

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/errors.py

```
# Transport-level errors only. No semantics, no workflow logic.

from __future__ import annotations


class AIGatewayError(RuntimeError):
    """Base class for AI Gateway transport errors."""


class GatewayConfigError(AIGatewayError):
    """Misconfiguration (missing keys, invalid provider/model)."""


class GatewayTimeoutError(AIGatewayError):
    """Request exceeded timeout."""


class GatewayAuthError(AIGatewayError):
    """Authentication/authorization failure."""


class GatewayRateLimitError(AIGatewayError):
    """Supplier rate limited the request (HTTP 429)."""


class GatewayUpstreamError(AIGatewayError):
    """Supplier/service error (5xx or other upstream failure)."""


class GatewayClientError(AIGatewayError):
    """Non-retryable client error (4xx except 429)."""

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/__init__.py

```
from .client import AIGatewayClient, CallOptions
from .errors import (
    AIGatewayError,
    GatewayConfigError,
    GatewayTimeoutError,
    GatewayAuthError,
    GatewayRateLimitError,
    GatewayUpstreamError,
    GatewayClientError,
)

__all__ = [
    "AIGatewayClient",
    "CallOptions",
    "AIGatewayError",
    "GatewayConfigError",
    "GatewayTimeoutError",
    "GatewayAuthError",
    "GatewayRateLimitError",
    "GatewayUpstreamError",
    "GatewayClientError",
]

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/logging.py

```
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def prompt_hash8(prompt: str) -> str:
    return hashlib.sha256((prompt or "").encode("utf-8")).hexdigest()[:8]


def _log_dir() -> Path:
    # Keep logs local to gateway by default, configurable if needed
    base = os.getenv("AI_GATEWAY_LOG_DIR", "")
    if base:
        p = Path(base)
    else:
        p = Path(__file__).resolve().parent / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p


def log_event(event: str, **fields: Any) -> None:
    """
    Operational logging only. Never log prompt or output text.
    Emits JSONL for easy ingestion.
    """
    rec = {"ts": _utc_now(), "event": event, **fields}
    line = json.dumps(rec, ensure_ascii=False)
    print(line, flush=True)

    try:
        (_log_dir() / "ai_gateway.log.jsonl").open("a", encoding="utf-8").write(line + "\n")
    except Exception:
        # Logging must never break the call path
        pass

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/logs/ai_gateway.log.jsonl

```
{"ts": "2026-01-21T13:51:46Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T13:51:46Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 73, "prompt_hash8": "d3e9ca8a", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T13:52:09Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "offline", "timeout_s": 60.0, "prompt_hash8": "3514cf81"}
{"ts": "2026-01-21T13:52:09Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "offline", "latency_ms": 0, "prompt_hash8": "3514cf81"}
{"ts": "2026-01-21T13:53:38Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T13:53:38Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 65, "prompt_hash8": "d3e9ca8a", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:09:52Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T14:09:52Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 658, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T14:10:21Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T14:10:21Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 527, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 68, "prompt_hash8": "73d07d68", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 51, "prompt_hash8": "5857ac47", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 53, "prompt_hash8": "a936bf73", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 58, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:32:38Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 66, "prompt_hash8": "73d07d68", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 55, "prompt_hash8": "5857ac47", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 51, "prompt_hash8": "a936bf73", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 53, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 56, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:08Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:34:08Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 65, "prompt_hash8": "73d07d68", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:08Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:34:08Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 55, "prompt_hash8": "5857ac47", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 56, "prompt_hash8": "a936bf73", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 50, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 56, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "unknown", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.fail", "provider": "unknown", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayAuthError"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "unknown", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.fail", "provider": "unknown", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayAuthError"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.start", "provider": "unknown", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.fail", "provider": "unknown", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayAuthError"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "unknown", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.fail", "provider": "unknown", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayAuthError"}

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/providers/__init__.py

```
# Provider modules live here.

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/providers/offline.py

```
from __future__ import annotations

def call_offline(*, prompt: str, model: str, timeout_s: float) -> str:
    # Deterministic stub for tests and offline runs
    return ""

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/retry.py

```
from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, TypeVar

from .errors import (
    GatewayRateLimitError,
    GatewayTimeoutError,
    GatewayUpstreamError,
)

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = 3
    backoff_base_s: float = 1.0
    backoff_max_s: float = 20.0


_RETRYABLE = (GatewayTimeoutError, GatewayRateLimitError, GatewayUpstreamError)


def _sleep_s(policy: RetryPolicy, attempt: int) -> float:
    # exp backoff with jitter
    base = policy.backoff_base_s * (2 ** max(0, attempt))
    jitter = random.uniform(0.0, 0.25 * base)
    return min(policy.backoff_max_s, base + jitter)


def run_with_retry(fn: Callable[[], T], policy: RetryPolicy) -> T:
    last_exc: Exception | None = None
    for attempt in range(policy.max_retries + 1):
        try:
            return fn()
        except _RETRYABLE as e:
            last_exc = e
            if attempt >= policy.max_retries:
                raise
            time.sleep(_sleep_s(policy, attempt))
    # Should be unreachable
    assert last_exc is not None
    raise last_exc

```

## File: /home/user/AA1/gateways/ai_gateway/audit_gateways_code.md.part_000

```
# Audit Document for /home/user/AA1/gateways

## File: `/home/user/AA1/gateways/ai_gateway/.pytest_cache/v/cache/lastfailed`

```
{}
```

## File: `/home/user/AA1/gateways/ai_gateway/.pytest_cache/v/cache/stepwise`

```
[]
```

## File: `/home/user/AA1/gateways/ai_gateway/.pytest_cache/v/cache/nodeids`

```
[
  "tests/providers/test_gemini.py::test_call_gemini_auth_error",
  "tests/providers/test_gemini.py::test_call_gemini_client_error",
  "tests/providers/test_gemini.py::test_call_gemini_empty_response_content",
  "tests/providers/test_gemini.py::test_call_gemini_invalid_json_response",
  "tests/providers/test_gemini.py::test_call_gemini_network_error",
  "tests/providers/test_gemini.py::test_call_gemini_rate_limit_error",
  "tests/providers/test_gemini.py::test_call_gemini_success",
  "tests/providers/test_gemini.py::test_call_gemini_timeout_error",
  "tests/providers/test_gemini.py::test_call_gemini_upstream_error",
  "tests/providers/test_gemini.py::test_safe_err_with_empty_response",
  "tests/providers/test_gemini.py::test_safe_err_with_error_json",
  "tests/providers/test_gemini.py::test_safe_err_with_invalid_json",
  "tests/providers/test_gemini.py::test_safe_err_with_other_json",
  "tests/test_client.py::test_client_calls_gemini_provider_correctly",
  "tests/test_client.py::test_client_calls_offline_provider_correctly",
  "tests/test_client.py::test_client_does_not_modify_output",
  "tests/test_client.py::test_client_does_not_modify_prompt",
  "tests/test_client.py::test_client_handles_call_options_override",
  "tests/test_client.py::test_client_initializes_with_provided_config",
  "tests/test_client.py::test_client_loads_config_if_not_provided",
  "tests/test_client.py::test_client_logs_failure_on_exception",
  "tests/test_client.py::test_client_logs_prompt_hash_not_prompt_text",
  "tests/test_client.py::test_client_raises_gateway_config_error_for_missing_gemini_key",
  "tests/test_client.py::test_client_raises_gateway_config_error_for_unknown_provider",
  "tests/test_client.py::test_client_raises_value_error_for_empty_prompt",
  "tests/test_retry.py::test_run_with_retry_exceeds_max_retries",
  "tests/test_retry.py::test_run_with_retry_multiple_retryable_errors",
  "tests/test_retry.py::test_run_with_retry_non_retryable_error",
  "tests/test_retry.py::test_run_with_retry_other_exception_raised_immediately",
  "tests/test_retry.py::test_run_with_retry_success_after_retries",
  "tests/test_retry.py::test_run_with_retry_success_first_attempt",
  "tests/test_retry.py::test_sleep_s_calculation"
]
```

## File: `/home/user/AA1/gateways/ai_gateway/.pytest_cache/.gitignore`

```
# Created by pytest automatically.
*

```

## File: `/home/user/AA1/gateways/ai_gateway/.pytest_cache/CACHEDIR.TAG`

```
Signature: 8a477f597d28d172789f06886806bc55
# This file is a cache directory tag created by pytest.
# For information about cache directory tags, see:
#	https://bford.info/cachedir/spec.html

```

## File: `/home/user/AA1/gateways/ai_gateway/.pytest_cache/README.md`

```
# pytest cache directory #

This directory contains data from the pytest's cache plugin,
which provides the `--lf` and `--ff` options, as well as the `cache` fixture.

**Do not** commit this to version control.

See [the docs](https://docs.pytest.org/en/stable/how-to/cache.html) for more information.

```

## File: `/home/user/AA1/gateways/ai_gateway/pyproject.toml`

```
[tool.poetry]
name = "ai-gateway"
version = "0.1.0"
description = ""
authors = ["InstaPact <oss@instapact.com>"]
readme = "README.md"
packages = [{include = "ai_gateway", from = "."}]


[tool.poetry.dependencies]
python = "^3.11"
pydantic = "^2.5.3"
httpx = "^0.26.0"
backoff = "^2.2.1"


[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.1"
pytest-mock = "^3.12.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

```

## File: `/home/user/AA1/gateways/ai_gateway/tests/providers/test_gemini.py`

```
import pytest
from unittest.mock import Mock, patch
import httpx

from ai_gateway.providers.gemini import call_gemini, _safe_err
from ai_gateway.errors import GatewayAuthError, GatewayClientError, GatewayRateLimitError, GatewayTimeoutError, GatewayUpstreamError

# Mock configuration
MOCK_API_KEY = "test_api_key"
MOCK_MODEL = "gemini-test-model"
MOCK_PROMPT = "test prompt"
MOCK_TIMEOUT = 10.0

@pytest.fixture
def mock_httpx_client():
    with patch("httpx.Client") as mock_client_class:
        mock_client = mock_client_class.return_value
        # Critical line: what the `with` block binds to as `client`
        mock_client.__enter__.return_value = mock_client
        yield mock_client

# --- Test _safe_err function ---
def test_safe_err_with_error_json():
    resp = Mock(status_code=400) # Simple Mock for _safe_err
    resp.json.return_value = {"error": {"status": "INVALID_ARGUMENT", "code": 400, "message": "API key not valid."}}
    resp.text = "raw text"
    assert _safe_err(resp) == "INVALID_ARGUMENT 400: API key not valid."

def test_safe_err_with_other_json():
    resp = Mock(status_code=200) # Simple Mock for _safe_err
    resp.json.return_value = {"status": "OK"}
    resp.text = "raw text"
    assert _safe_err(resp) == '{"status": "OK"}'

def test_safe_err_with_invalid_json():
    resp = Mock(status_code=200) # Simple Mock for _safe_err
    resp.json.side_effect = ValueError("Not JSON")
    resp.text = "raw text"
    assert _safe_err(resp) == "raw text"

def test_safe_err_with_empty_response():
    resp = Mock(status_code=200) # Simple Mock for _safe_err
    resp.json.side_effect = ValueError("Not JSON")
    resp.text = None
    assert _safe_err(resp) == ""

# --- Test call_gemini function ---

def test_call_gemini_success(mock_httpx_client):
    mock_resp = Mock(status_code=200)
    mock_resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Expected Output"}]}}]
    }
    mock_httpx_client.post.return_value = mock_resp

    result = call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)
    assert result == "Expected Output"
    mock_httpx_client.post.assert_called_once()
    
def test_call_gemini_auth_error(mock_httpx_client):
    mock_resp = Mock(status_code=401)
    mock_resp.json.return_value = {"error": {"message": "Invalid API Key"}}
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayAuthError, match="Gemini auth error: HTTP 401"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_rate_limit_error(mock_httpx_client):
    mock_resp = Mock(status_code=429)
    mock_resp.json.return_value = {"error": {"message": "Rate limit exceeded"}}
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayRateLimitError, match="Gemini rate limited"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_client_error(mock_httpx_client):
    mock_resp = Mock(status_code=400)
    mock_resp.json.return_value = {"error": {"message": "Bad Request"}}
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayClientError, match="Gemini client error HTTP 400"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_upstream_error(mock_httpx_client):
    mock_resp = Mock(status_code=500)
    mock_resp.json.return_value = {"error": {"message": "Internal Server Error"}}
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayUpstreamError, match="Gemini upstream error HTTP 500"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_timeout_error(mock_httpx_client):
    mock_httpx_client.post.side_effect = httpx.ReadTimeout("Timeout")

    with pytest.raises(GatewayTimeoutError, match="Gemini timeout"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_network_error(mock_httpx_client):
    mock_httpx_client.post.side_effect = httpx.RequestError("Network error", request=httpx.Request("GET", "http://test.com"))

    with pytest.raises(GatewayUpstreamError, match="Gemini request error"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_invalid_json_response(mock_httpx_client):
    mock_resp = Mock(status_code=200)
    mock_resp.json.side_effect = ValueError("Not JSON")
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayUpstreamError, match="Gemini returned non-JSON response"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_empty_response_content(mock_httpx_client):
    mock_resp = Mock(status_code=200)
    # Simulate various empty/missing parts in the JSON response
    mock_resp.json.return_value = {
        "candidates": [
            {"content": {"parts": [{"text": None}]}},
            {"content": {"parts": [{}]}},
            {"content": {}},
            {},
        ]
    }
    mock_httpx_client.post.return_value = mock_resp

    result = call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)
    assert result == "" # Should return empty string if content is missing or None
```

## File: `/home/user/AA1/gateways/ai_gateway/tests/providers/__pycache__/test_gemini.cpython-312-pytest-7.4.4.pyc`

```
Ë
:çpi“ãóì—ddlZddlmcmZddlZddlmZm	Z	ddl
Z
ddlmZmZddlmZmZmZmZmZdZdZdZdZej0d	„«Zd
„Zd„Zd„Zd„Zd„Zd„Zd„Z d„Z!d„Z"d„Z#d„Z$d„Z%d„Z&y)éN)ÚMockÚpatch)Úcall_geminiÚ	_safe_err)ÚGatewayAuthErrorÚGatewayClientErrorÚGatewayRateLimitErrorÚGatewayTimeoutErrorÚGatewayUpstreamErrorÚtest_api_keyzgemini-test-modelztest promptg$@c#óK—td«5}|j}||j_|–—ddd«y#1swYyxYw­w)Nzhttpx.Client)rÚreturn_valueÚ	__enter__)Úmock_client_classÚmock_clients  úA/home/user/AA1/gateways/ai_gateway/tests/providers/test_gemini.pyÚmock_httpx_clientrsDèø€ä	ˆ~Ó	ğĞ"3Ø'×4Ñ4ˆà-8ˆ×ÑÔ*ØÒ÷	÷ñüs‚A"9°	A¹A¾Acóx—td¬«}dddddœi|j_d|_t	|«}d}||k(}|sötjd	|fd
||f«dtj«vstjt«rtjt«nddtj«vstj|«rtj|«ndtj|«tj|«dœz}dd|iz}ttj|««‚dx}x}}y)Né©Ústatus_codeÚerrorÚINVALID_ARGUMENTzAPI key not valid.)ÚstatusÚcodeÚmessageúraw textz(INVALID_ARGUMENT 400: API key not valid.©ú==©z0%(py3)s
{%(py3)s = %(py0)s(%(py1)s)
} == %(py6)srÚresp©Úpy0Úpy1Úpy3Úpy6úassert %(py8)sÚpy8©rÚjsonrÚtextrÚ
@pytest_arÚ_call_reprcompareÚ@py_builtinsÚlocalsÚ_should_repr_global_nameÚ	_safereprÚAssertionErrorÚ_format_explanation©r!Ú@py_assert2Ú@py_assert5Ú@py_assert4Ú@py_format7Ú@py_format9s      rÚtest_safe_err_with_error_jsonr:s–€Ü˜CÔ €DØ%Ğ2DÈcĞ^rÑ'sĞt€D‡IIÔØ€D„IßH×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×HĞHócóp—td¬«}ddi|j_d|_t	|«}d}||k(}|sötjd|fd||f«d	tj«vstjt«rtjt«nd	d
tj«vstj|«rtj|«nd
tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}}y)NéÈrrÚOKrz{"status": "OK"}rr rr!r"r'r(r)r4s      rÚtest_safe_err_with_other_jsonr?s€Ü˜CÔ €DØ&¨Ğ-€D‡IIÔØ€D„Iß0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0Ğ0r;có~—td¬«}td«|j_d|_t|«}d}||k(}|sötjd|fd||f«dtj«vstjt
«rtjt
«nddtj«vstj|«rtj|«ndtj|«tj|«d	œz}d
d|iz}ttj|««‚dx}x}}y)Nr=rúNot JSONrrr rr!r"r'r(©rÚ
ValueErrorr*Úside_effectr+rr,r-r.r/r0r1r2r3r4s      rÚtest_safe_err_with_invalid_jsonrE#s€Ü˜CÔ €DÜ& zÓ2€D‡IIÔØ€D„Iß(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(Ğ(r;có~—td¬«}td«|j_d|_t|«}d}||k(}|sötjd|fd||f«dtj«vstjt
«rtjt
«nddtj«vstj|«rtj|«ndtj|«tj|«d	œz}d
d|iz}ttj|««‚dx}x}}y)Nr=rrAÚrr rr!r"r'r(rBr4s      rÚ!test_safe_err_with_empty_responserH)s€Ü˜CÔ €DÜ& zÓ2€D‡IIÔØ€D„Iß × × × × × × × × × × × × × × × × × × × × × × × × × × × × × × × × × Ğ r;có2—td¬«}dddddigiigi|j_||j_t	t
ttt¬«}d}||k(}|s™tjd	|fd
||f«dtj«vstj|«rtj|«ndtj|«dœz}dd|iz}ttj |««‚dx}}|jj#«y)Nr=rÚ
candidatesÚcontentÚpartsr+zExpected Output©ÚpromptÚmodelÚapi_keyÚ	timeout_sr©z%(py0)s == %(py3)sÚresult©r#r%úassert %(py5)sÚpy5)rr*rÚpostrÚMOCK_PROMPTÚ
MOCK_MODELÚMOCK_API_KEYÚMOCK_TIMEOUTr,r-r.r/r0r1r2r3Úassert_called_once©rÚ	mock_resprSr5Ú@py_assert1Ú@py_format4Ú@py_format6s       rÚtest_call_gemini_successrb1s¨€Ü Ô%€Ià˜	 G¨vĞ7HĞ.IĞ-JĞ#KĞLĞMğ#€I‡NNÔğ+4Ğ×ÑÔ'ä¤´:Ä|Ô_kÔl€Fß&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&Õ&Ø×Ñ×-Ñ-Õ/r;có—td¬«}dddii|j_||j_t	j
td¬«5ttttt¬«ddd«y#1swYyxYw)	Ni‘rrrzInvalid API KeyzGemini auth error: HTTP 401©ÚmatchrM)rr*rrWÚpytestÚraisesrrrXrYrZr[©rr^s  rÚtest_call_gemini_auth_errorri<sj€Ü Ô%€IØ#*¨YĞ8IĞ,JĞ"K€I‡NNÔØ*3Ğ×ÑÔ'ä	‰Ô'Ğ/LÔ	MñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúóÁ A7Á7Bcó—td¬«}dddii|j_||j_t	j
td¬«5ttttt¬«ddd«y#1swYyxYw)	Ni­rrrzRate limit exceededzGemini rate limitedrdrM)rr*rrWrfrgr	rrXrYrZr[rhs  rÚ!test_call_gemini_rate_limit_errorrlDsj€Ü Ô%€IØ#*¨YĞ8MĞ,NĞ"O€I‡NNÔØ*3Ğ×ÑÔ'ä	‰Ô,Ğ4IÔ	JñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúrjcó—td¬«}dddii|j_||j_t	j
td¬«5ttttt¬«ddd«y#1swYyxYw)	NrrrrzBad RequestzGemini client error HTTP 400rdrM)rr*rrWrfrgrrrXrYrZr[rhs  rÚtest_call_gemini_client_errorrnLsi€Ü Ô%€IØ#*¨Y¸Ğ,FĞ"G€I‡NNÔØ*3Ğ×ÑÔ'ä	‰Ô)Ğ1OÔ	PñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúrjcó—td¬«}dddii|j_||j_t	j
td¬«5ttttt¬«ddd«y#1swYyxYw)	NiôrrrzInternal Server ErrorzGemini upstream error HTTP 500rdrM)rr*rrWrfrgrrrXrYrZr[rhs  rÚtest_call_gemini_upstream_errorrpTsj€Ü Ô%€IØ#*¨YĞ8OĞ,PĞ"Q€I‡NNÔØ*3Ğ×ÑÔ'ä	‰Ô+Ğ3SÔ	TñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúrjcóê—tjd«|j_t	j
td¬«5ttttt¬«ddd«y#1swYyxYw)NÚTimeoutzGemini timeoutrdrM)ÚhttpxÚReadTimeoutrWrDrfrgr
rrXrYrZr[©rs rÚtest_call_gemini_timeout_errorrv\sT€Ü).×):Ñ):¸9Ó)EĞ×ÑÔ&ä	‰Ô*Ğ2BÔ	CñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúsÁ A)Á)A2có—tjdtjdd«¬«|j_tjtd¬«5ttttt¬«ddd«y#1swYyxYw)NzNetwork errorÚGETzhttp://test.com)ÚrequestzGemini request errorrdrM)rsÚRequestErrorÚRequestrWrDrfrgrrrXrYrZr[rus rÚtest_call_gemini_network_errorr|bsf€Ü).×);Ñ);¸OÔUZ×UbÑUbĞchĞj{ÓU|Ô)}Ğ×ÑÔ&ä	‰Ô+Ğ3IÔ	JñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúsÁ A?Á?Bcó—td¬«}td«|j_||j_tjtd¬«5ttttt¬«ddd«y#1swYyxYw)Nr=rrAz!Gemini returned non-JSON responserdrM)rrCr*rDrWrrfrgrrrXrYrZr[rhs  rÚ&test_call_gemini_invalid_json_responser~hsd€Ü Ô%€IÜ!+¨JÓ!7€I‡NNÔØ*3Ğ×ÑÔ'ä	‰Ô+Ğ3VÔ	WñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúsÁ A<Á<Bcó—td¬«}dddddigiiddigiidiiigi|j_||j_t	t
ttt¬«}d}||k(}|s™tjd	|fd
||f«dtj«vstj|«rtj|«ndtj|«dœz}dd|iz}ttj |««‚dx}}y)Nr=rrJrKrLr+rMrGrrRrSrTrUrV)rr*rrWrrXrYrZr[r,r-r.r/r0r1r2r3r]s       rÚ'test_call_gemini_empty_response_contentr€ps±€Ü Ô%€Iğ	Ø˜ F¨D >Ğ"2Ğ3Ğ4Ø˜ 2 $˜Ğ(Ø˜ˆOØğ	
ğ#€I‡NNÔğ+4Ğ×ÑÔ'ä¤´:Ä|Ô_kÔl€Fß×××××××××××××××××××Ör;)'Úbuiltinsr.Ú_pytest.assertion.rewriteÚ	assertionÚrewriter,rfÚunittest.mockrrrsÚai_gateway.providers.geminirrÚai_gateway.errorsrrr	r
rrZrYrXr[Úfixturerr:r?rErHrbrirlrnrprvr|r~r€©r;rú<module>rŠs–ğß„ƒß%Ûç>÷EõEğ€Ø €
Ø€Ø€à‡ñóğòIò1ò)ò!ò	0òhòhòhòhòhòhòhór;
```

## File: `/home/user/AA1/gateways/ai_gateway/tests/test_client.py`

```
import pytest
from unittest.mock import Mock, patch, call
import os

from ai_gateway.client import AIGatewayClient, CallOptions
from ai_gateway.config import GatewayConfig
from ai_gateway.errors import GatewayConfigError, GatewayAuthError, AIGatewayError

# Fixtures for common objects
@pytest.fixture
def mock_config():
    return GatewayConfig(
        provider="gemini",
        model="gemini-test-model",
        timeout_s=10.0,
        max_retries=1,
        backoff_base_s=1.0,
        backoff_max_s=20.0,
        gemini_api_key="TEST_GEMINI_KEY",
        openai_api_key=None,
    )

@pytest.fixture
def client(mock_config):
    return AIGatewayClient(cfg=mock_config)

@pytest.fixture(autouse=True)
def mock_dependencies(mocker, mock_config): # Added mock_config here
    # Patch modules as they are imported within client.py
    log_event_mock = mocker.patch('ai_gateway.client.log_event')
    prompt_hash8_mock = mocker.patch('ai_gateway.client.prompt_hash8', return_value="TESTHASH")
    run_with_retry_mock = mocker.patch('ai_gateway.retry.run_with_retry', side_effect=lambda fn, policy: fn()) # Execute fn immediately

    # Patch modules as they are imported within client.py
    call_gemini_mock = mocker.patch('ai_gateway.client.call_gemini', return_value="MODEL_OUTPUT_OK")
    call_offline_mock = mocker.patch('ai_gateway.client.call_offline', return_value="")
    load_config_mock = mocker.patch('ai_gateway.client.load_config', return_value=mock_config) # Patch where client.py looks for it

    # Return a dict of mocks for easier access in tests
    return {
        "log_event": log_event_mock,
        "prompt_hash8": prompt_hash8_mock,
        "run_with_retry": run_with_retry_mock,
        "call_gemini": call_gemini_mock,
        "call_offline": call_offline_mock,
        "load_config": load_config_mock,
    }

# --- Tests for Data Integrity and Privacy ---

def test_client_does_not_modify_prompt(client, mock_dependencies):
    original_prompt = "Return exactly: This is my prompt."
    expected_output = "MODEL_OUTPUT_OK"
    
    client.call(original_prompt)
    
    # Verify that call_gemini received the original prompt
    mock_dependencies["call_gemini"].assert_called_once_with(
        prompt=original_prompt,
        model=mock_dependencies["load_config"].return_value.model, # Get model from mocked config
        api_key=mock_dependencies["load_config"].return_value.gemini_api_key, # Get API key from mocked config
        timeout_s=mock_dependencies["load_config"].return_value.timeout_s, # Get timeout from mocked config
    )

def test_client_does_not_modify_output(client, mock_dependencies):
    # The mock for call_gemini already ensures a fixed output.
    # The test here is to ensure AIGatewayClient returns it as-is.
    output = client.call("any prompt")
    assert output == "MODEL_OUTPUT_OK"
    
def test_client_logs_prompt_hash_not_prompt_text(client, mock_dependencies, mocker):
    prompt = "Sensitive prompt content"
    client.call(prompt)
    
    # Check log_event calls for 'prompt_hash8'
    mock_dependencies["log_event"].assert_any_call(
        "ai_gateway.call.start",
        provider="gemini",
        model="gemini-test-model",
        timeout_s=10.0,
        prompt_hash8="TESTHASH",
    )
    mock_dependencies["log_event"].assert_any_call(
        "ai_gateway.call.ok",
        provider="gemini",
        model="gemini-test-model",
        latency_ms=mocker.ANY, # Use mocker.ANY for dynamic values
        prompt_hash8="TESTHASH",
    )
    # Ensure no calls directly include the original prompt text
    for call_args in mock_dependencies["log_event"].call_args_list:
        args, kwargs = call_args
        # Check kwargs first, then args if needed, but for named args, kwargs is sufficient
        assert prompt not in kwargs.values()
        # For positional args if any might contain prompt
        # for arg in args:
        #     assert prompt not in str(arg)


# --- Tests for core client behavior ---

def test_client_initializes_with_provided_config():
    custom_config = GatewayConfig(
        provider="offline",
        model="test-offline",
        timeout_s=5.0,
        max_retries=0,
        backoff_base_s=0.0,
        backoff_max_s=0.0,
        gemini_api_key=None,
        openai_api_key=None,
    )
    client = AIGatewayClient(cfg=custom_config)
    assert client.cfg is custom_config

def test_client_loads_config_if_not_provided(mocker, mock_dependencies):
    # Ensure load_config is mocked out and returns a known config
    test_config = GatewayConfig(
        provider="default", model="default", timeout_s=1.0, max_retries=0,
        backoff_base_s=0.0, backoff_max_s=0.0, gemini_api_key=None, openai_api_key=None
    )
    mock_dependencies["load_config"].return_value = test_config # Set return value for the mock
    
    # Create client without passing config, so it calls load_config
    client = AIGatewayClient() 
    mock_dependencies["load_config"].assert_called_once()
    assert client.cfg.provider == "default"

def test_client_calls_gemini_provider_correctly(client, mock_dependencies):
    client.call("test prompt")
    mock_dependencies["call_gemini"].assert_called_once()

def test_client_calls_offline_provider_correctly(mock_config, mock_dependencies):
    # Create a new client with a config that explicitly sets the provider to offline
    offline_config = GatewayConfig(**{**mock_config.__dict__, "provider": "offline"})
    client = AIGatewayClient(cfg=offline_config)
    client.call("test prompt")
    mock_dependencies["call_offline"].assert_called_once()
    mock_dependencies["call_gemini"].assert_not_called()

def test_client_handles_call_options_override(mock_config, mock_dependencies):
    # Ensure base config is gemini so we can override it
    base_config = GatewayConfig(**{**mock_config.__dict__, "provider": "gemini"})
    client = AIGatewayClient(cfg=base_config)
    
    options = CallOptions(provider="offline", timeout_s=5.0)
    client.call("test prompt", options=options)
    
    # Ensure offline was called with overridden timeout
    mock_dependencies["call_offline"].assert_called_once_with(
        prompt="test prompt", model="gemini-test-model", timeout_s=5.0 # Model from config, not overridden
    )
    mock_dependencies["call_gemini"].assert_not_called()


def test_client_raises_value_error_for_empty_prompt(client):
    with pytest.raises(ValueError, match="prompt must be a non-empty string"):
        client.call("")
    with pytest.raises(ValueError, match="prompt must be a non-empty string"):
        client.call("   ")
    with pytest.raises(ValueError, match="prompt must be a non-empty string"):
        client.call(None) # type: ignore

def test_client_raises_gateway_config_error_for_missing_gemini_key(mocker, mock_dependencies, mock_config):
    # Create a new config with missing API key
    mock_config_no_key = GatewayConfig(**{**mock_config.__dict__, "gemini_api_key": None})
    mock_dependencies["load_config"].return_value = mock_config_no_key # Ensure this is the config loaded
    
    client = AIGatewayClient() # Client will load the mocked config
    
    with pytest.raises(GatewayConfigError, match="Missing GEMINI_API_KEY"):
        client.call("test prompt")

def test_client_raises_gateway_config_error_for_unknown_provider(mocker, mock_dependencies, mock_config):
    # Create a new config with an unknown provider and a valid gemini key to reach the "unknown provider" check
    mock_config_unknown_provider = GatewayConfig(**{
        **mock_config.__dict__,
        "provider": "unknown",
        "gemini_api_key": "VALID_KEY_FOR_TEST" # Ensure API key is present so it doesn't fail on missing key first
    })
    mock_dependencies["load_config"].return_value = mock_config_unknown_provider # Ensure this is the config loaded
    
    client = AIGatewayClient() # Client will load the mocked config
    
    with pytest.raises(GatewayConfigError, match="Unknown provider: unknown"):
        client.call("test prompt")

def test_client_logs_failure_on_exception(client, mock_dependencies, mocker):
    mock_dependencies["call_gemini"].side_effect = GatewayAuthError("auth fail")
    
    with pytest.raises(GatewayAuthError):
        client.call("test prompt")
    
    mock_dependencies["log_event"].assert_called_with(
        "ai_gateway.call.fail",
        provider="gemini",
        model="gemini-test-model",
        latency_ms=mocker.ANY,
        prompt_hash8="TESTHASH",
        error_type="GatewayAuthError",
    )

```

## File: `/home/user/AA1/gateways/ai_gateway/tests/test_retry.py`

```
import pytest
from unittest.mock import Mock, call
import time

from ai_gateway.retry import RetryPolicy, run_with_retry, _sleep_s # Import _sleep_s directly
from ai_gateway.errors import GatewayTimeoutError, GatewayRateLimitError, GatewayUpstreamError, GatewayClientError, GatewayAuthError

def test_run_with_retry_success_first_attempt():
    # Test that a successful function call returns immediately
    mock_fn = Mock(return_value="success")
    policy = RetryPolicy(max_retries=3)
    result = run_with_retry(mock_fn, policy)
    assert result == "success"
    mock_fn.assert_called_once()

def test_run_with_retry_success_after_retries(mocker): # Added mocker
    # Test that a function succeeds after a few retries
    mock_fn = Mock(side_effect=[GatewayTimeoutError("timeout"), GatewayUpstreamError("upstream"), "success"])
    policy = RetryPolicy(max_retries=3, backoff_base_s=0.01) # Short backoff for testing
    mocker.patch('time.sleep') # Mock sleep to avoid actual delays
    
    result = run_with_retry(mock_fn, policy)
    assert result == "success"
    assert mock_fn.call_count == 3
    assert time.sleep.called # Ensure sleep was called

def test_run_with_retry_exceeds_max_retries(mocker): # Added mocker
    # Test that a retryable error is re-raised after max_retries
    mock_fn = Mock(side_effect=GatewayTimeoutError("timeout"))
    policy = RetryPolicy(max_retries=2, backoff_base_s=0.01)
    mocker.patch('time.sleep')

    with pytest.raises(GatewayTimeoutError):
        run_with_retry(mock_fn, policy)
    assert mock_fn.call_count == 3 # Initial call + 2 retries

def test_run_with_retry_non_retryable_error():
    # Test that a non-retryable error is raised immediately
    mock_fn = Mock(side_effect=GatewayClientError("bad request"))
    policy = RetryPolicy(max_retries=3)
    
    with pytest.raises(GatewayClientError):
        run_with_retry(mock_fn, policy)
    mock_fn.assert_called_once() # Should not retry

def test_run_with_retry_other_exception_raised_immediately():
    # Test that an unexpected exception is raised immediately
    mock_fn = Mock(side_effect=ValueError("unexpected"))
    policy = RetryPolicy(max_retries=3)
    
    with pytest.raises(ValueError):
        run_with_retry(mock_fn, policy)
    mock_fn.assert_called_once()

def test_run_with_retry_multiple_retryable_errors(mocker): # Added mocker
    # Test with a mix of retryable errors
    mock_fn = Mock(side_effect=[GatewayRateLimitError("rate limited"), GatewayTimeoutError("timeout"), "finally success"])
    policy = RetryPolicy(max_retries=2, backoff_base_s=0.01)
    mocker.patch('time.sleep')
    
    result = run_with_retry(mock_fn, policy)
    assert result == "finally success"
    assert mock_fn.call_count == 3

def test_sleep_s_calculation(mocker): # Added mocker
    # Test that _sleep_s calculates a reasonable backoff (no exact values due to jitter)
    policy = RetryPolicy(backoff_base_s=1.0, backoff_max_s=10.0)
    mocker.patch('random.uniform', return_value=0) # Remove jitter for predictable results

    # Attempt 0: base * 2^0 = 1.0, jitter 0, min(10.0, 1.0) = 1.0
    assert _sleep_s(policy, 0) == 1.0 # Corrected access

    # Attempt 1: base * 2^1 = 2.0, jitter 0, min(10.0, 2.0) = 2.0
    assert _sleep_s(policy, 1) == 2.0 # Corrected access

    # Attempt 2: base * 2^2 = 4.0, jitter 0, min(10.0, 4.0) = 4.0
    assert _sleep_s(policy, 2) == 4.0 # Corrected access

    # Attempt 3: base * 2^3 = 8.0, jitter 0, min(10.0, 8.0) = 8.0
    assert _sleep_s(policy, 3) == 8.0 # Corrected access

    # Attempt 4: base * 2^4 = 16.0, jitter 0, min(10.0, 16.0) = 10.0 (capped by backoff_max_s)
    assert _sleep_s(policy, 4) == 10.0 # Corrected access
```

## File: `/home/user/AA1/gateways/ai_gateway/tests/__pycache__/test_retry.cpython-312-pytest-7.4.4.pyc`

```
Ë
eãpilãó˜—ddlZddlmcmZddlZddlmZm	Z	ddl
Z
ddlmZmZmZddlmZmZmZmZmZd„Zd„Zd„Zd„Zd	„Zd
„Zd„Zy)éN)ÚMockÚcall)ÚRetryPolicyÚrun_with_retryÚ_sleep_s)ÚGatewayTimeoutErrorÚGatewayRateLimitErrorÚGatewayUpstreamErrorÚGatewayClientErrorÚGatewayAuthErrorcó¸—td¬«}td¬«}t||«}d}||k(}|s™tjd|fd||f«dtj«vstj|«rtj|«ndtj|«dœz}d	d
|iz}ttj|««‚dx}}|j«y)NÚsuccess©Úreturn_valueé©Úmax_retries©ú==©z%(py0)s == %(py3)sÚresult©Úpy0Úpy3úassert %(py5)sÚpy5)rrrÚ
@pytest_arÚ_call_reprcompareÚ@py_builtinsÚlocalsÚ_should_repr_global_nameÚ	_safereprÚAssertionErrorÚ_format_explanationÚassert_called_once)Úmock_fnÚpolicyrÚ@py_assert2Ú@py_assert1Ú@py_format4Ú@py_format6s       ú6/home/user/AA1/gateways/ai_gateway/tests/test_retry.pyÚ)test_run_with_retry_success_first_attemptr-sm€ä 	Ô*€GÜ QÔ'€FÜ˜G VÓ,€Fß×××××××××××××××××××ÕØ×ÑÕ ócóä—ttd«td«dg¬«}tdd¬«}|j	d«t||«}d}||k(}|s™tjd	|fd
||f«dtj«vstj|«rtj|«ndtj|«dœz}dd|iz}ttj|««‚dx}}|j}d}||k(}	|	s­tjd	|	fd||f«dtj«vstj|«rtj|«ndtj|«tj|«dœz}dd|iz}
ttj|
««‚dx}x}	}tj }|j"}	|	s•ddtj«vstjt«rtjt«ndtj|«tj|	«dœz}ttj|««‚dx}}	y)NÚtimeoutÚupstreamr©Úside_effectrç{®Gáz„?©rÚbackoff_base_sú
time.sleeprrrrrr©z2%(py2)s
{%(py2)s = %(py0)s.call_count
} == %(py5)sr&©rÚpy2rúassert %(py7)sÚpy7zEassert %(py4)s
{%(py4)s = %(py2)s
{%(py2)s = %(py0)s.sleep
}.called
}Útime)rr:Úpy4)rrr
rÚpatchrrrrr r!r"r#r$Ú
call_countr=ÚsleepÚcalled)Úmockerr&r'rr(r)r*r+Ú@py_assert4Ú@py_assert3Ú@py_format8Ú@py_format5s            r,Ú)test_run_with_retry_success_after_retriesrHs€äÔ 3°IÓ >Ô@TĞU_Ó@`ĞbkĞlÔm€GÜ Q°tÔ<€FØ
‡LLÔä˜G VÓ,€Fß×××××××××××××××××××Õß"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"ß××××××××××××××××××××××r.cón—ttd«¬«}tdd¬«}|jd«t	j
t«5t||«ddd«|j}d}||k(}|s­tjd|fd	||f«d
tj«vstj|«rtj|«nd
tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}}y#1swYŒÒxYw)Nr0r2ér4r5r7rrr8r&r9r;r<)rrrr?ÚpytestÚraisesrr@rrrr r!r"r#r$)rCr&r'r)rDrEr+rFs        r,Ú'test_run_with_retry_exceeds_max_retriesrMs¤€äÔ2°9Ó=Ô>€GÜ Q°tÔ<€FØ
‡LLÔä	‰Ô*Ó	+ñ(Üw Ô'÷(ç"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"Ğ"÷(ğ(úsÁD+Ä+D4cóÚ—ttd«¬«}td¬«}tjt«5t||«ddd«|j«y#1swYŒxYw)Nzbad requestr2rr)rrrrKrLrr%©r&r's  r,Ú'test_run_with_retry_non_retryable_errorrP%sT€äÔ1°-Ó@ÔA€GÜ QÔ'€Fä	‰Ô)Ó	*ñ(Üw Ô'÷(à×ÑÕ ÷(ğ(úó»A!Á!A*cóÚ—ttd«¬«}td¬«}tjt«5t||«ddd«|j«y#1swYŒxYw)NÚ
unexpectedr2rr)rÚ
ValueErrorrrKrLrr%rOs  r,Ú6test_run_with_retry_other_exception_raised_immediatelyrU.sR€äœz¨,Ó7Ô8€GÜ QÔ'€Fä	‰”zÓ	"ñ(Üw Ô'÷(à×ÑÕ ÷(ğ(úrQcóv—ttd«td«dg¬«}tdd¬«}|j	d«t||«}d}||k(}|s™tjd	|fd
||f«dtj«vstj|«rtj|«ndtj|«dœz}dd|iz}ttj|««‚dx}}|j}d}||k(}	|	s­tjd	|	fd||f«dtj«vstj|«rtj|«ndtj|«tj|«dœz}dd|iz}
ttj|
««‚dx}x}	}y)Nzrate limitedr0zfinally successr2rJr4r5r7rrrrrrrr8r&r9r;r<)rr	rrr?rrrrr r!r"r#r$r@)rCr&r'rr(r)r*r+rDrErFs           r,Ú-test_run_with_retry_multiple_retryable_errorsrW7sÒ€äÔ 5°nÓ EÔGZĞ[dÓGeĞgxĞyÔz€GÜ Q°tÔ<€FØ
‡LLÔä˜G VÓ,€Fß&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&Õ&ß"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"Ğ"r.cóè—tdd¬«}|jdd¬«d}t||«}d}||k(}|s
tjd|fd||f«d	tj«vstjt«rtjt«nd	d
tj«vstj|«rtj|«nd
tj|«tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}x}}d}t||«}d}||k(}|s
tjd|fd||f«d	tj«vstjt«rtjt«nd	d
tj«vstj|«rtj|«nd
tj|«tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}x}}d}t||«}d}||k(}|s
tjd|fd||f«d	tj«vstjt«rtjt«nd	d
tj«vstj|«rtj|«nd
tj|«tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}x}}d}t||«}d}||k(}|s
tjd|fd||f«d	tj«vstjt«rtjt«nd	d
tj«vstj|«rtj|«nd
tj|«tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}x}}d}t||«}d}||k(}|s
tjd|fd||f«d	tj«vstjt«rtjt«nd	d
tj«vstj|«rtj|«nd
tj|«tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}x}}y)Ngğ?g$@)r6Úbackoff_max_szrandom.uniformrrr)z9%(py5)s
{%(py5)s = %(py0)s(%(py1)s, %(py3)s)
} == %(py8)srr')rÚpy1rrÚpy8zassert %(py10)sÚpy10ég@rJg@rg @é)rr?rrrrr r!r"r#r$)rCr'r(rDÚ@py_assert7Ú@py_assert6Ú@py_format9Ú@py_format11s        r,Útest_sleep_s_calculationrcAsc€ä¨¸4Ô@€FØ
‡LLĞ!°€LÔ2÷&×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%Ñ%÷&×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%Ñ%÷&×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%Ñ%÷&×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%Ñ%÷'×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&Ò&r.)ÚbuiltinsrÚ_pytest.assertion.rewriteÚ	assertionÚrewriterrKÚunittest.mockrrr=Úai_gateway.retryrrrÚai_gateway.errorsrr	r
rrr-rHrMrPrUrWrc©r.r,ú<module>rlsGğß„ƒß$ÛçBÑB÷EõEò!ò	ò#ò!ò!ò#ó'r.
```

## File: `/home/user/AA1/gateways/ai_gateway/tests/__pycache__/test_client.cpython-312-pytest-7.4.4.pyc`

```
Ë
æpiL!ãó4—ddlZddlmcmZddlZddlmZm	Z	m
Z
ddlZddlmZmZddlmZddlmZmZmZej*d„«Zej*d„«Zej*d¬	«d
„«Zd„Zd„Zd„Zd„Zd„Zd„Zd„Zd„Z d„Z!d„Z"d„Z#d„Z$y)éN)ÚMockÚpatchÚcall)ÚAIGatewayClientÚCallOptions©ÚGatewayConfig)ÚGatewayConfigErrorÚGatewayAuthErrorÚAIGatewayErrorc
ó(—tdddddddd¬«S)	NÚgeminiúgemini-test-modelç$@éçğ?g4@ÚTEST_GEMINI_KEY©ÚproviderÚmodelÚ	timeout_sÚmax_retriesÚbackoff_base_sÚbackoff_max_sÚgemini_api_keyÚopenai_api_keyr©óú7/home/user/AA1/gateways/ai_gateway/tests/test_client.pyÚmock_configr 
s'€äØØ!ØØØØØ(Øô	ğ	rcó—t|¬«S)N©Úcfg)r)r s rÚclientr$s€ä˜{Ô+Ğ+rT)Úautousecóö—|jd«}|jdd¬«}|jdd„¬«}|jdd	¬«}|jd
d¬«}|jd|¬«}||||||dœS)Nzai_gateway.client.log_eventzai_gateway.client.prompt_hash8ÚTESTHASH)Úreturn_valuezai_gateway.retry.run_with_retrycó—|«S)Nr)ÚfnÚpolicys  rú<lambda>z#mock_dependencies.<locals>.<lambda> s
€ÑikÓim€r)Úside_effectzai_gateway.client.call_geminiÚMODEL_OUTPUT_OKzai_gateway.client.call_offlineÚzai_gateway.client.load_config)Ú	log_eventÚprompt_hash8Úrun_with_retryÚcall_geminiÚcall_offlineÚload_config)r)Úmockerr Úlog_event_mockÚprompt_hash8_mockÚrun_with_retry_mockÚcall_gemini_mockÚcall_offline_mockÚload_config_mocks        rÚmock_dependenciesr=sœ€ğ—\‘\Ğ"?Ó@€NØŸ™Ğ%EĞT^˜Ó_ĞØ Ÿ,™,Ğ'HÑVm˜,ÓnĞğ—|‘|Ğ$CĞRc|ÓdĞØŸ™Ğ%EĞTV˜ÓWĞØ—|‘|Ğ$CĞR]|Ó^Ğğ$Ø)Ø-Ø'Ø)Ø'ñğrcóè—d}d}|j|«|dj||djj|djj|djj
¬«y)Nz"Return exactly: This is my prompt.r.r3r5)ÚpromptrÚapi_keyr)rÚassert_called_once_withr(rrr)r$r=Úoriginal_promptÚexpected_outputs    rÚ"test_client_does_not_modify_promptrD3sq€Ø:€OØ'€Oà
‡KKÔ ğmÑ$×<Ñ<ØØ Ñ.×;Ñ;×AÑAØ! -Ñ0×=Ñ=×LÑLØ# MÑ2×?Ñ?×IÑIğ	=õrcór—|jd«}d}||k(}|s™tjd|fd||f«dtj«vstj
|«rtj|«ndtj|«dœz}dd|iz}ttj|««‚dx}}y)	Nz
any promptr.©ú==)z%(py0)s == %(py3)sÚoutput)Úpy0Úpy3zassert %(py5)sÚpy5)	rÚ
@pytest_arÚ_call_reprcompareÚ@py_builtinsÚlocalsÚ_should_repr_global_nameÚ	_safereprÚAssertionErrorÚ_format_explanation)r$r=rHÚ@py_assert2Ú@py_assert1Ú@py_format4Ú@py_format6s       rÚ"test_client_does_not_modify_outputrXAsQ€ğ[‰[˜Ó&€Fß&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&Ö&rcóò—d}|j|«|djddddd¬«|djd	dd|jd¬
«|djD]}|\}}|j}|«}||v}	|	sîtjd|	fd||f«dtj«vstj|«rtj|«nddtj«vstj|«rtj|«ndtj|«tj|«dœz}
dd|
iz}ttj|««‚dx}	x}}Œy)NzSensitive prompt contentr0zai_gateway.call.startrrrr')rrrr1zai_gateway.call.ok)rrÚ
latency_msr1)únot in)zI%(py0)s not in %(py6)s
{%(py6)s = %(py4)s
{%(py4)s = %(py2)s.values
}()
}r?Úkwargs)rIÚpy2Úpy4Úpy6zassert %(py8)sÚpy8)rÚassert_any_callÚANYÚcall_args_listÚvaluesrLrMrNrOrPrQrRrS)r$r=r6r?Ú	call_argsÚargsr\Ú@py_assert3Ú@py_assert5rUÚ@py_format7Ú@py_format9s            rÚ,test_client_logs_prompt_hash_not_prompt_textrkGsô€Ø'€FØ
‡KKÔğkÑ"×2Ñ2ØØØ!ØØğ3ôğkÑ"×2Ñ2ØØØ!Ø—:‘:Øğ3ôğ' {Ñ3×BÑBó-ˆ	Ø ‰ˆˆfç,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,Ö,ñ-rc
ó"—tdddddddd¬«}t|¬«}|j}||u}|sÚtjd|fd	||f«d
tj«vstj|«rtj|«nd
tj|«dtj«vstj|«rtj|«nddœz}dd|iz}ttj|««‚dx}}y)NÚofflineztest-offlineç@rçrr")Úis)z+%(py2)s
{%(py2)s = %(py0)s.cfg
} is %(py4)sr$Úcustom_config)rIr]r^zassert %(py6)sr_)r	rr#rLrMrNrOrPrQrRrS)rqr$rUrgÚ@py_format5ris      rÚ,test_client_initializes_with_provided_configrsfs€Ü!ØØØØØØØØô	€Mô Ô/€Fß&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&Ğ&rc
óL—tdddddddd¬«}||d_t«}|dj«|j}|j
}d}||k(}|sÁtjd|fd||f«d	tj«vstj|«rtj|«nd	tj|«tj|«tj|«d
œz}dd|iz}	ttj|	««‚dx}x}x}}y)NÚdefaultrrrorr5rF)zI%(py4)s
{%(py4)s = %(py2)s
{%(py2)s = %(py0)s.cfg
}.provider
} == %(py7)sr$)rIr]r^Úpy7zassert %(py9)sÚpy9)r	r(rÚassert_called_oncer#rrLrMrNrOrPrQrRrS)
r6r=Útest_configr$rUrgÚ@py_assert6rhÚ@py_format8Ú@py_format10s
          rÚ(test_client_loads_config_if_not_providedr}ts¥€äØ )°sÈØ¨#¸dĞSWô€Kğ5@ĞmÑ$Ô1ôÓ€FØmÑ$×7Ñ7Ô9ß+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+Ò+rcóL—|jd«|dj«y)Nútest promptr3)rrx)r$r=s  rÚ+test_client_calls_gemini_provider_correctlyr€s€Ø
‡KKÔØmÑ$×7Ñ7Õ9rcóÀ—tdii|j¥ddi¥¤}t|¬«}|jd«|dj	«|dj«y)Nrrmr"rr4r3r)r	Ú__dict__rrrxÚassert_not_called)r r=Úoffline_configr$s    rÚ,test_client_calls_offline_provider_correctlyr……sZ€ä"ÑUĞ%T¨×(<Ñ(<Ğ%T¸jÈ)Ñ%TÑU€NÜ Ô0€FØ
‡KKÔØnÑ%×8Ñ8Ô:ØmÑ$×6Ñ6Õ8rcóæ—tdii|j¥ddi¥¤}t|¬«}tdd¬«}|j	d|¬«|d	jdd
d¬«|dj«y)Nrrr"rmrn)rrr)Úoptionsr4r)r?rrr3r)r	r‚rrrrArƒ)r r=Úbase_configr$r‡s     rÚ)test_client_handles_call_options_overrider‰s}€äÑQĞ"P [×%9Ñ%9Ğ"P¸:ÀxÑ"PÑQ€KÜ Ô-€Fä 9¸Ô<€GØ
‡KK w€KÔ/ğnÑ%×=Ñ=ØĞ$7À3ğ>ôğmÑ$×6Ñ6Õ8rcóŠ—tjtd¬«5|jd«ddd«tjtd¬«5|jd«ddd«tjtd¬«5|jd«ddd«y#1swYŒtxYw#1swYŒKxYw#1swYyxYw)Nz!prompt must be a non-empty string©Úmatchr/z   )ÚpytestÚraisesÚ
ValueErrorr)r$s rÚ/test_client_raises_value_error_for_empty_promptrœs–€Ü	‰”zĞ)LÔ	MñØ‰BŒ÷ä	‰”zĞ)LÔ	MñØ‰EÔ÷ä	‰”zĞ)LÔ	MñØ‰DÔ÷ğ÷	ğú÷ğú÷ğús#œB!ÁB-ÂB9Â!B*Â-B6Â9Ccóä—tdii|j¥ddi¥¤}||d_t«}t	j
td¬«5|jd«ddd«y#1swYyxYw)Nrr5zMissing GEMINI_API_KEYr‹rr©r	r‚r(rrrr
r)r6r=r Úmock_config_no_keyr$s     rÚ>test_client_raises_gateway_config_error_for_missing_gemini_keyr”¤sl€ä&ÑZĞ)Y¨K×,@Ñ,@Ğ)YĞBRĞTXÑ)YÑZĞØ4FĞmÑ$Ô1äÓ€Fä	‰Ô)Ğ1IÔ	Jñ#Ø‰MÔ"÷#÷#ñ#úsÁA&Á&A/cóæ—tdii|j¥dddœ¥¤}||d_t«}t	j
td¬«5|jd«ddd«y#1swYyxYw)	NÚunknownÚVALID_KEY_FOR_TEST)rrr5zUnknown provider: unknownr‹rrr’)r6r=r Úmock_config_unknown_providerr$s     rÚ<test_client_raises_gateway_config_error_for_unknown_providerr™®sz€ä#0ñ$ğ4Ø
×
Ñ
ğ4àØ.ò4ñ$Ğ ğ
5QĞmÑ$Ô1äÓ€Fä	‰Ô)Ğ1LÔ	Mñ#Ø‰MÔ"÷#÷#ñ#úsÁA'Á'A0cóğ—td«|d_tjt«5|j	d«ddd«|djddd|jdd	¬
«y#1swYŒ.xYw)Nz	auth failr3rr0zai_gateway.call.failrrr'r)rrrZr1Ú
error_type)rr-rrrÚassert_called_withrb)r$r=r6s   rÚ%test_client_logs_failure_on_exceptionr¼ss€Ü3CÀKÓ3PĞmÑ$Ô0ä	‰Ô'Ó	(ñ#Ø‰MÔ"÷#ğkÑ"×5Ñ5ØØØ!Ø—:‘:ØØ%ğ6õ÷#ğ#ús­A,Á,A5)%ÚbuiltinsrNÚ_pytest.assertion.rewriteÚ	assertionÚrewriterLrÚunittest.mockrrrÚosÚai_gateway.clientrrÚai_gateway.configr	Úai_gateway.errorsr
rrÚfixturer r$r=rDrXrkrsr}r€r…r‰rr”r™rrrrú<module>r¨s¬ğß„ƒß+Ñ+Û	ç:İ+ßRÑRğ‡ñ
óğ
ğ‡ñ,óğ,ğ€‡˜Ôñóğò.ò'ò-ò>'ò,ò:ò9ò9òò#ò#ór
```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/__init__.py`

```
from .client import AIGatewayClient, CallOptions
from .errors import (
    AIGatewayError,
    GatewayConfigError,
    GatewayTimeoutError,
    GatewayAuthError,
    GatewayRateLimitError,
    GatewayUpstreamError,
    GatewayClientError,
)

__all__ = [
    "AIGatewayClient",
    "CallOptions",
    "AIGatewayError",
    "GatewayConfigError",
    "GatewayTimeoutError",
    "GatewayAuthError",
    "GatewayRateLimitError",
    "GatewayUpstreamError",
    "GatewayClientError",
]

```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/config.py`

```
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class GatewayConfig:
    provider: str
    model: str
    timeout_s: float
    max_retries: int
    backoff_base_s: float
    backoff_max_s: float
    # Provider keys (kept here to avoid scattering env reads)
    gemini_api_key: str | None
    openai_api_key: str | None


def _get_float(name: str, default: float) -> float:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    try:
        return float(v)
    except ValueError:
        return default


def _get_int(name: str, default: int) -> int:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    try:
        return int(v)
    except ValueError:
        return default


def load_config() -> GatewayConfig:
    # Stable, boring env var surface
    provider = os.getenv("AI_GATEWAY_PROVIDER", "gemini").strip().lower()
    model = os.getenv("AI_GATEWAY_MODEL", "").strip()

    timeout_s = _get_float("AI_GATEWAY_TIMEOUT_S", 60.0)
    max_retries = _get_int("AI_GATEWAY_RETRIES", 3)
    backoff_base_s = _get_float("AI_GATEWAY_BACKOFF_BASE_S", 1.0)
    backoff_max_s = _get_float("AI_GATEWAY_BACKOFF_MAX_S", 20.0)

    # Provider-specific keys (still env-only)
    gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("AI_GATEWAY_GEMINI_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY") or os.getenv("AI_GATEWAY_OPENAI_API_KEY")

    # Provide sane default model if not set
    if not model:
        if provider == "gemini":
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        elif provider == "openai":
            model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
        elif provider == "offline":
            model = "offline"
        else:
            model = "default"

    return GatewayConfig(
        provider=provider,
        model=model,
        timeout_s=timeout_s,
        max_retries=max_retries,
        backoff_base_s=backoff_base_s,
        backoff_max_s=backoff_max_s,
        gemini_api_key=gemini_api_key,
        openai_api_key=openai_api_key,
    )

```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/providers/__init__.py`

```
# Provider modules live here.

```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/providers/offline.py`

```
from __future__ import annotations

def call_offline(*, prompt: str, model: str, timeout_s: float) -> str:
    # Deterministic stub for tests and offline runs
    return ""

```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/providers/openai.py`

```
# future

```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/providers/gemini.py`

```
from __future__ import annotations

import json
import time
import httpx

from ..errors import (
    GatewayAuthError,
    GatewayClientError,
    GatewayRateLimitError,
    GatewayTimeoutError,
    GatewayUpstreamError,
)

# NOTE: This is transport only: prompt -> text.
# No schema enforcement. No output interpretation.


def call_gemini(
    *,
    prompt: str,
    model: str,
    api_key: str,
    timeout_s: float,
) -> str:
    """
    Gemini generateContent (Generative Language API).
    Returns model text unchanged.
    """
    # Endpoint is configurable to survive API churn
    base = "https://generativelanguage.googleapis.com"
    version = "v1"
    endpoint = f"{base}/{version}/models/{model}:generateContent"

    headers = {
        "Content-Type": "application/json",
        # Prefer header auth; keep query-free by default
        "x-goog-api-key": api_key,
    }

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ]
    }

    t0 = time.time()
    try:
        with httpx.Client(timeout=timeout_s) as client:
            resp = client.post(endpoint, headers=headers, json=payload)
        # --- DEBUG PRINT ---
        print(f"DEBUG: Type of resp: {type(resp)}")
        print(f"DEBUG: Type of resp.status_code: {type(resp.status_code)}")
        print(f"DEBUG: Value of resp.status_code: {resp.status_code}")
        # --- END DEBUG PRINT ---
    except httpx.ReadTimeout as e:
        raise GatewayTimeoutError(f"Gemini timeout after {timeout_s}s") from e
    except httpx.RequestError as e:
        # Network/DNS/connectivity
        raise GatewayUpstreamError(f"Gemini request error: {type(e).__name__}") from e

    # Map errors
    if resp.status_code == 401 or resp.status_code == 403:
        raise GatewayAuthError(f"Gemini auth error: HTTP {resp.status_code}")
    if resp.status_code == 429:
        raise GatewayRateLimitError("Gemini rate limited (HTTP 429)")
    if 400 <= resp.status_code < 500:
        detail = _safe_err(resp)
        raise GatewayClientError(f"Gemini client error HTTP {resp.status_code}: {detail}")
    if resp.status_code >= 500:
        detail = _safe_err(resp)
        raise GatewayUpstreamError(f"Gemini upstream error HTTP {resp.status_code}: {detail}")

    # Parse response text (transport normalization only)
    try:
        data = resp.json()
    except Exception as e:
        raise GatewayUpstreamError("Gemini returned non-JSON response") from e

    text = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text")
    )
    # Return raw text as-is (contract), ensuring None becomes ""
    return text if text is not None else ""


def _safe_err(resp: httpx.Response) -> str:
    try:
        j = resp.json()
        if isinstance(j, dict) and "error" in j:
            e = j["error"]
            return f"{e.get('status','?')} {e.get('code','?')}: {e.get('message','')}"
        return json.dumps(j)[:300]
    except Exception:
        return (resp.text or "")[:300]
```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/providers/__pycache__/__init__.cpython-312.pyc`

```
Ë
¤×piãó—y)N©róúC/home/user/AA1/gateways/ai_gateway/ai_gateway/providers/__init__.pyú<module>rsñr
```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/providers/__pycache__/offline.cpython-312.pyc`

```
Ë
ˆ×pi­ãó—ddlmZdd„Zy)é)Úannotationscó—y)NÚ©)ÚpromptÚmodelÚ	timeout_ss   úB/home/user/AA1/gateways/ai_gateway/ai_gateway/providers/offline.pyÚcall_offliners€àóN)rÚstrrrr	ÚfloatÚreturnr)Ú
__future__rrrrr
ú<module>rsğİ"ôr
```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/providers/__pycache__/gemini.cpython-312.pyc`

```
Ë
Rçpióãóh—ddlmZddlZddlZddlZddlmZmZmZm	Z	m
Z
										dd„Zdd„Zy)	é)ÚannotationsNé)ÚGatewayAuthErrorÚGatewayClientErrorÚGatewayRateLimitErrorÚGatewayTimeoutErrorÚGatewayUpstreamErrorcóĞ—d}d}|›d|›d|›d}d|dœ}dd	d
|igdœgi}tj«}		tj|¬«5}
|
j|||¬«}ddd«t	dt«›«t	dt|j«›«t	d|j›«|jdk(s|jdk(rtd|j›«‚|jdk(rtd«‚d|jcxkrdkr)nn&t|«}td|j›d|›«‚|jdk\r&t|«}td|j›d|›«‚	|j!«}|j%d ig«d!j%d"i«j%d#ig«d!j%d
«}||Sd$S#1swYŒ}xYw#tj$r}td|›d«|‚d}~wtj$r'}tdt|«j›«|‚d}~wwxYw#t"$r}td«|‚d}~wwxYw)%z]
    Gemini generateContent (Generative Language API).
    Returns model text unchanged.
    z)https://generativelanguage.googleapis.comÚv1ú/z/models/z:generateContentzapplication/json)zContent-Typezx-goog-api-keyÚcontentsÚuserÚtext)ÚroleÚparts)Útimeout)ÚheadersÚjsonNzDEBUG: Type of resp: z!DEBUG: Type of resp.status_code: z"DEBUG: Value of resp.status_code: zGemini timeout after ÚszGemini request error: i‘i“zGemini auth error: HTTP i­zGemini rate limited (HTTP 429)iiôzGemini client error HTTP ú: zGemini upstream error HTTP z!Gemini returned non-JSON responseÚ
candidatesrÚcontentrÚ)ÚtimeÚhttpxÚClientÚpostÚprintÚtypeÚstatus_codeÚReadTimeoutrÚRequestErrorr	Ú__name__rrÚ	_safe_errrrÚ	ExceptionÚget)ÚpromptÚmodelÚapi_keyÚ	timeout_sÚbaseÚversionÚendpointrÚpayloadÚt0ÚclientÚrespÚeÚdetailÚdatars                úA/home/user/AA1/gateways/ai_gateway/ai_gateway/providers/gemini.pyÚcall_geminir6s¥€ğ7€DØ€GØq˜˜	 ¨%¨Ğ0@ĞA€Hğ+à!ñ€Gğ	Ø¨°Ğ'7Ğ&8Ñ9ğ
ğ€Gô
‰‹€BğWÜ\‰\ )Ô,ğ	H°Ø—;‘;˜x°¸w;ÓGˆD÷	Hô	Ğ%¤d¨4£j \Ğ2Ô3ÜĞ1´$°t×7GÑ7GÓ2HĞ1IĞJÔKÜĞ2°4×3CÑ3CĞ2DĞEÔFğ×Ñ˜3Ò $×"2Ñ"2°cÒ"9ÜĞ!9¸$×:JÑ:JĞ9KĞLÓMĞMØ×Ñ˜3ÒÜ#Ğ$DÓEĞEØ
ˆd×ÑÔ$ Õ$Ü˜4“ˆÜ Ğ#<¸T×=MÑ=MĞ<NÈbĞQWĞPXĞ!YÓZĞZØ×Ñ˜3ÒÜ˜4“ˆÜ"Ğ%@À×AQÑAQĞ@RĞRTĞU[ĞT\Ğ#]Ó^Ğ^ğOØy‰y‹{ˆğ
	‰ ˜tÓ$ QÑ'ß	‰ˆY˜Ó	ß	‰ˆWrdÓ	˜Añ	÷
‰ˆV‹ğ		ğĞ#ˆ4Ğ+¨Ğ+÷M	Hñ	Hûô×ÑòOÜ!Ğ$9¸)¸ÀAĞ"FÓGÈQĞNûÜ×ÑòWä"Ğ%;¼DÀ»G×<LÑ<LĞ;MĞ#NÓOĞUVĞVûğWûô&òOÜ"Ğ#FÓGÈQĞNûğOúsTµG(ÁGÁ AG(Å<IÇG%Ç G(Ç(IÇ;HÈIÈ!"IÉIÉ	I%ÉI É I%có>—	|j«}t|t«rCd|vr?|d}|jdd«›d|jdd«›d|jdd«›Stj|«dd	S#t
$r|jxsddd	cYSwxYw)
NÚerrorÚstatusú?ú ÚcoderÚmessageri,)rÚ
isinstanceÚdictr&Údumpsr%r)r1Újr2s   r5r$r$Zs €ğ'ØI‰I‹KˆÜaœÔ 7¨a¡<Ø'‘
ˆAØ—e‘e˜H SÓ)Ğ*¨!¨A¯E©E°&¸Ó,=Ğ+>¸bÀÇÁÀyĞQSÓATĞ@UĞVĞVÜz‰z˜!‹}˜T˜cĞ"Ğ"øÜò'Ø—	‘	’˜R  #Ğ&Ò&ğ'ús‚A"A=Á%A=Á=BÂB)
r'Ústrr(rBr)rBr*ÚfloatÚreturnrB)r1zhttpx.ResponserDrB)Ú
__future__rrrrÚerrorsrrrrr	r6r$©ór5ú<module>rIs\ğİ"ãÛÛ÷õğD,àğD,ğğD,ğğ	D,ğ
ğD,ğ	óD,ôN'rH
```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/logs/ai_gateway.log.jsonl`

```
{"ts": "2026-01-21T13:51:46Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T13:51:46Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 73, "prompt_hash8": "d3e9ca8a", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T13:52:09Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "offline", "timeout_s": 60.0, "prompt_hash8": "3514cf81"}
{"ts": "2026-01-21T13:52:09Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "offline", "latency_ms": 0, "prompt_hash8": "3514cf81"}
{"ts": "2026-01-21T13:53:38Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T13:53:38Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 65, "prompt_hash8": "d3e9ca8a", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:09:52Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T14:09:52Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 658, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T14:10:21Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T14:10:21Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 527, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 68, "prompt_hash8": "73d07d68", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 51, "prompt_hash8": "5857ac47", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 53, "prompt_hash8": "a936bf73", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 58, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:32:38Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 66, "prompt_hash8": "73d07d68", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 55, "prompt_hash8": "5857ac47", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 51, "prompt_hash8": "a936bf73", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 53, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 56, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:08Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:34:08Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 65, "prompt_hash8": "73d07d68", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:08Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:34:08Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 55, "prompt_hash8": "5857ac47", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 56, "prompt_hash8": "a936bf73", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 50, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 56, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "unknown", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.fail", "provider": "unknown", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayAuthError"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "unknown", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.fail", "provider": "unknown", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayAuthError"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.start", "provider": "unknown", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.fail", "provider": "unknown", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayAuthError"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "unknown", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.fail", "provider": "unknown", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayAuthError"}

```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/logging.py`

```
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def prompt_hash8(prompt: str) -> str:
    return hashlib.sha256((prompt or "").encode("utf-8")).hexdigest()[:8]


def _log_dir() -> Path:
    # Keep logs local to gateway by default, configurable if needed
    base = os.getenv("AI_GATEWAY_LOG_DIR", "")
    if base:
        p = Path(base)
    else:
        p = Path(__file__).resolve().parent / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p


def log_event(event: str, **fields: Any) -> None:
    """
    Operational logging only. Never log prompt or output text.
    Emits JSONL for easy ingestion.
    """
    rec = {"ts": _utc_now(), "event": event, **fields}
    line = json.dumps(rec, ensure_ascii=False)
    print(line, flush=True)

    try:
        (_log_dir() / "ai_gateway.log.jsonl").open("a", encoding="utf-8").write(line + "\n")
    except Exception:
        # Logging must never break the call path
        pass

```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/retry.py`

```
from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, TypeVar

from .errors import (
    GatewayRateLimitError,
    GatewayTimeoutError,
    GatewayUpstreamError,
)

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = 3
    backoff_base_s: float = 1.0
    backoff_max_s: float = 20.0


_RETRYABLE = (GatewayTimeoutError, GatewayRateLimitError, GatewayUpstreamError)


def _sleep_s(policy: RetryPolicy, attempt: int) -> float:
    # exp backoff with jitter
    base = policy.backoff_base_s * (2 ** max(0, attempt))
    jitter = random.uniform(0.0, 0.25 * base)
    return min(policy.backoff_max_s, base + jitter)


def run_with_retry(fn: Callable[[], T], policy: RetryPolicy) -> T:
    last_exc: Exception | None = None
    for attempt in range(policy.max_retries + 1):
        try:
            return fn()
        except _RETRYABLE as e:
            last_exc = e
            if attempt >= policy.max_retries:
                raise
            time.sleep(_sleep_s(policy, attempt))
    # Should be unreachable
    assert last_exc is not None
    raise last_exc

```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/client.py`

```
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from .config import GatewayConfig, load_config
from .errors import GatewayConfigError
from .logging import log_event, prompt_hash8
from .retry import RetryPolicy, run_with_retry
from .providers.gemini import call_gemini
from .providers.offline import call_offline

# openai provider can be added later without changing this contract.


@dataclass
class CallOptions:
    provider: Optional[str] = None
    model: Optional[str] = None
    timeout_s: Optional[float] = None
    temperature: Optional[float] = None  # accepted but provider may ignore
    max_tokens: Optional[int] = None     # accepted but provider may ignore


class AIGatewayClient:
    """
    AI Gateway public API.
    Contract: accepts prompt, returns raw model text unchanged.
    Handles only transport concerns (security, retries, stability, logging).
    """

    def __init__(self, cfg: Optional[GatewayConfig] = None):
        self.cfg = cfg or load_config()

    def call(self, prompt: str, *, options: Optional[CallOptions] = None) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt must be a non-empty string")

        opt = options or CallOptions()
        provider = (opt.provider or self.cfg.provider).strip().lower()
        model = (opt.model or self.cfg.model).strip()
        timeout_s = float(opt.timeout_s or self.cfg.timeout_s)

        ph = prompt_hash8(prompt)
        t0 = time.time()

        policy = RetryPolicy(
            max_retries=self.cfg.max_retries,
            backoff_base_s=self.cfg.backoff_base_s,
            backoff_max_s=self.cfg.backoff_max_s,
        )

        log_event(
            "ai_gateway.call.start",
            provider=provider,
            model=model,
            timeout_s=timeout_s,
            prompt_hash8=ph,
        )

        def _invoke() -> str:
            if provider == "offline":
                return call_offline(prompt=prompt, model=model, timeout_s=timeout_s)

            if provider == "gemini":
                if not self.cfg.gemini_api_key:
                    raise GatewayConfigError("Missing GEMINI_API_KEY (or AI_GATEWAY_GEMINI_API_KEY).")
                return call_gemini(
                    prompt=prompt,
                    model=model,
                    api_key=self.cfg.gemini_api_key,
                    timeout_s=timeout_s,
                )

            raise GatewayConfigError(f"Unknown provider: {provider}")

        try:
            out = run_with_retry(_invoke, policy)
            ms = int((time.time() - t0) * 1000)
            log_event(
                "ai_gateway.call.ok",
                provider=provider,
                model=model,
                latency_ms=ms,
                prompt_hash8=ph,
            )
            return out
        except Exception as e:
            ms = int((time.time() - t0) * 1000)
            log_event(
                "ai_gateway.call.fail",
                provider=provider,
                model=model,
                latency_ms=ms,
                prompt_hash8=ph,
                error_type=type(e).__name__,
            )
            raise

```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/errors.py`

```
# Transport-level errors only. No semantics, no workflow logic.

from __future__ import annotations


class AIGatewayError(RuntimeError):
    """Base class for AI Gateway transport errors."""


class GatewayConfigError(AIGatewayError):
    """Misconfiguration (missing keys, invalid provider/model)."""


class GatewayTimeoutError(AIGatewayError):
    """Request exceeded timeout."""


class GatewayAuthError(AIGatewayError):
    """Authentication/authorization failure."""


class GatewayRateLimitError(AIGatewayError):
    """Supplier rate limited the request (HTTP 429)."""


class GatewayUpstreamError(AIGatewayError):
    """Supplier/service error (5xx or other upstream failure)."""


class GatewayClientError(AIGatewayError):
    """Non-retryable client error (4xx except 429)."""

```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/__pycache__/retry.cpython-312.pyc`

```
Ë
S×piŒãó¦—ddlmZddlZddlZddlmZddlmZmZddl	m
Z
mZmZed«Zed¬	«Gd
„d««Zee
efZdd„Zdd„Zy)é)ÚannotationsN)Ú	dataclass)ÚCallableÚTypeVaré)ÚGatewayRateLimitErrorÚGatewayTimeoutErrorÚGatewayUpstreamErrorÚTT)Úfrozencó8—eZdZUdZded<dZded<dZded<y	)
ÚRetryPolicyéÚintÚmax_retriesgğ?ÚfloatÚbackoff_base_sg4@Úbackoff_max_sN)Ú__name__Ú
__module__Ú__qualname__rÚ__annotations__rr©óú6/home/user/AA1/gateways/ai_gateway/ai_gateway/retry.pyrrs …à€KÓØ€NEÓØ€M5Ôrrcó—|jdtd|«zz}tjdd|z«}t	|j
||z«S)NérggĞ?)rÚmaxÚrandomÚuniformÚminr)ÚpolicyÚattemptÚbaseÚjitters    rÚ_sleep_sr&sH€à× Ñ  A¬¨Q°«Ñ$8Ñ9€DÜ^‰^˜C ¨¡Ó-€FÜˆv×#Ñ# T¨F¡]Ó3Ğ3rcóì—d}t|jdz«D]}	|«cS|€J‚|‚#t$r;}|}||jk\r‚tjt||««Yd}~ŒSd}~wwxYw)Nr)ÚrangerÚ
_RETRYABLEÚtimeÚsleepr&)Úfnr"Úlast_excr#Úes     rÚrun_with_retryr/"sƒ€Ø!%€HÜ˜×+Ñ+¨aÑ/Ó0ò2ˆğ	2Ù“4ŠKğ2ğĞĞĞØ
€Nøôò	2ØˆHØ˜&×,Ñ,Ò,ØÜJ‰J”x ¨Ó0×1Ñ1ûğ		2úsŸ/¯	A3¸1A.Á.A3)r"rr#rÚreturnr)r,zCallable[[], T]r"rr0r)Ú
__future__rrr*ÚdataclassesrÚtypingrrÚerrorsrr	r
rrr)r&r/rrrú<module>r5sağİ"ãÛİ!ß$÷ññˆCƒL€ñ$Ô÷ ğ óğ ğ"Ğ#8Ğ:NĞO€
ó4ôr
```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/__pycache__/errors.cpython-312.pyc`

```
Ë
×piãóª—ddlmZGd„de«ZGd„de«ZGd„de«ZGd„d	e«ZGd
„de«ZGd„de«ZGd„de«Z	y)é)Úannotationscó—eZdZdZy)ÚAIGatewayErrorz+Base class for AI Gateway transport errors.N©Ú__name__Ú
__module__Ú__qualname__Ú__doc__©óú7/home/user/AA1/gateways/ai_gateway/ai_gateway/errors.pyrrs„Ú5rrcó—eZdZdZy)ÚGatewayConfigErrorz8Misconfiguration (missing keys, invalid provider/model).Nrrrrrr
s„ÚBrrcó—eZdZdZy)ÚGatewayTimeoutErrorzRequest exceeded timeout.Nrrrrrrs„Ú#rrcó—eZdZdZy)ÚGatewayAuthErrorz%Authentication/authorization failure.Nrrrrrrs„Ú/rrcó—eZdZdZy)ÚGatewayRateLimitErrorz-Supplier rate limited the request (HTTP 429).Nrrrrrrs„Ú7rrcó—eZdZdZy)ÚGatewayUpstreamErrorz7Supplier/service error (5xx or other upstream failure).Nrrrrrrs„ÚArrcó—eZdZdZy)ÚGatewayClientErrorz,Non-retryable client error (4xx except 429).Nrrrrrrs„Ú6rrN)
Ú
__future__rÚRuntimeErrorrrrrrrrrrrú<module>rsbğõ#ô6\ô6ôC˜ôCô$˜.ô$ô0~ô0ô8˜Nô8ôB˜>ôBô7˜õ7r
```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/__pycache__/__init__.cpython-312.pyc`

```
Ë
9Øpiàãó@—ddlmZmZddlmZmZmZmZmZm	Z	m
Z
gd¢Zy)é)ÚAIGatewayClientÚCallOptions)ÚAIGatewayErrorÚGatewayConfigErrorÚGatewayTimeoutErrorÚGatewayAuthErrorÚGatewayRateLimitErrorÚGatewayUpstreamErrorÚGatewayClientError)	rrrrrrr	r
rN)ÚclientrrÚerrorsrrrrr	r
rÚ__all__©óú9/home/user/AA1/gateways/ai_gateway/ai_gateway/__init__.pyú<module>rsğß0÷÷ñò
r
```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/__pycache__/client.cpython-312.pyc`

```
Ë
”×pi¡ãó¶—ddlmZddlZddlmZddlmZddlmZm	Z	ddl
mZddlmZmZdd	lmZmZdd
lmZddlmZeGd„d««ZGd„d«Zy)é)ÚannotationsN)Ú	dataclass)ÚOptionalé)ÚGatewayConfigÚload_config)ÚGatewayConfigError)Ú	log_eventÚprompt_hash8)ÚRetryPolicyÚrun_with_retry)Úcall_gemini)Úcall_offlinecóT—eZdZUdZded<dZded<dZded<dZded<dZded	<y)
ÚCallOptionsNzOptional[str]ÚproviderÚmodelzOptional[float]Ú	timeout_sÚtemperaturezOptional[int]Ú
max_tokens)	Ú__name__Ú
__module__Ú__qualname__rÚ__annotations__rrrr©óú7/home/user/AA1/gateways/ai_gateway/ai_gateway/client.pyrrs4…à"€HˆmÓ"Ø€Eˆ=ÓØ!%€IˆÓ%Ø#'€KÓ'Ø $€JÔ$rrcó(—eZdZdZddd„Zddœdd„Zy)	ÚAIGatewayClientz­
    AI Gateway public API.
    Contract: accepts prompt, returns raw model text unchanged.
    Handles only transport concerns (security, retries, stability, logging).
    Ncó*—|xs
t«|_y©N)rÚcfg)Úselfr"s  rÚ__init__zAIGatewayClient.__init__!s€ØÒ'œ+›-ˆr)Úoptionscóø‡‡‡‡‡—t‰t«r‰j«std«‚|xs
t	«}|j
xs‰jj
j«j«Š|jxs‰jjj«Št|jxs‰jj«Št‰«}tj«}t‰jj‰jj‰jj ¬«}t#d‰‰‰|¬«dˆˆˆˆˆfd„}	t%||«}t'tj«|z
dz«}	t#d‰‰|	|¬«|S#t($rM}
t'tj«|z
dz«}	t#d	‰‰|	|t+|
«j,¬
«‚d}
~
wwxYw)Nz!prompt must be a non-empty string)Úmax_retriesÚbackoff_base_sÚbackoff_max_szai_gateway.call.start)rrrrcóØ•—‰dk(rt‰‰‰¬«S‰dk(rD‰jjstd«‚t	‰‰‰jj‰¬«Std‰›«‚)NÚoffline)ÚpromptrrÚgeminiz6Missing GEMINI_API_KEY (or AI_GATEWAY_GEMINI_API_KEY).)r,rÚapi_keyrzUnknown provider: )rr"Úgemini_api_keyr	r)rr,rr#rs€€€€€rÚ_invokez%AIGatewayClient.call.<locals>._invoke>ssø€Ø˜9Ò$Ü#¨6¸È)ÔTĞTà˜8Ò#Ø—x‘x×.Ò.Ü,Ğ-eÓfĞfÜ"Ø!ØØ ŸH™H×3Ñ3Ø'ô	ğô%Ğ'9¸(¸Ğ%DÓEĞErièzai_gateway.call.ok)rrÚ
latency_msrzai_gateway.call.fail)rrr1rÚ
error_type)ÚreturnÚstr)Ú
isinstancer4ÚstripÚ
ValueErrorrrr"ÚlowerrÚfloatrrÚtimerr'r(r)r
rÚintÚ	ExceptionÚtyper)r#r,r%ÚoptÚphÚt0Úpolicyr0ÚoutÚmsÚerrrs``         @@@rÚcallzAIGatewayClient.call$sšü€Ü˜&¤#Ô&¨f¯l©l¬nÜĞ@ÓAĞAàÒ&œ›ˆØ—L‘LÒ5 D§H¡H×$5Ñ$5×<Ñ<Ó>×DÑDÓFˆØ—‘Ò,˜dŸh™hŸn™n×3Ñ3Ó5ˆÜ˜#Ÿ-™-Ò=¨4¯8©8×+=Ñ+=Ó>ˆ	ä˜&Ó!ˆÜY‰Y‹[ˆäØŸ™×,Ñ,ØŸ8™8×2Ñ2ØŸ(™(×0Ñ0ô
ˆô	Ø#ØØØØõ	
÷	Fñ	Fğ 	Ü  ¨&Ó1ˆCÜ”d—i‘i“k BÑ&¨$Ñ.Ó/ˆBÜØ$Ø!ØØØõğˆJøÜò
	Ü”d—i‘i“k BÑ&¨$Ñ.Ó/ˆBÜØ&Ø!ØØØÜ ›7×+Ñ+õğûğ
	úsÅ"AF#Æ#	G9Æ,AG4Ç4G9r!)r"zOptional[GatewayConfig])r,r4r%zOptional[CallOptions]r3r4)rrrÚ__doc__r$rErrrrrs„ñô(ğEIö?rr)Ú
__future__rr:ÚdataclassesrÚtypingrÚconfigrrÚerrorsr	Úloggingr
rÚretryrrÚproviders.geminirÚproviders.offlinerrrrrrú<module>rPsHğİ"ãİ!İç.İ&ß,ß.İ)İ+ğ
÷%ğ%óğ%÷IòIr
```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/__pycache__/logging.cpython-312.pyc`

```
Ë
A×pimãól—ddlmZddlZddlZddlZddlmZddlmZddlm	Z	d
d„Z
dd„Zdd„Zdd	„Zy)é)ÚannotationsN)Údatetime)ÚPath)ÚAnycóP—tj«jd¬«dzS)NÚseconds)ÚtimespecÚZ)rÚutcnowÚ	isoformat©óú8/home/user/AA1/gateways/ai_gateway/ai_gateway/logging.pyÚ_utc_nowrs"€Ü?‰?Ó×&Ñ&°	Ğ&Ó:¸SÑ@Ğ@rcót—tj|xsdjd««j«ddS)NÚúutf-8é)ÚhashlibÚsha256ÚencodeÚ	hexdigest)Úprompts rÚprompt_hash8rs0€Ü>‰>˜6š< R×/Ñ/°Ó8Ó9×CÑCÓEÀbÀqĞIĞIrcóÈ—tjdd«}|rt|«}n*tt«j	«j
dz}|jdd¬«|S)NÚAI_GATEWAY_LOG_DIRrÚlogsT)ÚparentsÚexist_ok)ÚosÚgetenvrÚ__file__ÚresolveÚparentÚmkdir)ÚbaseÚps  rÚ_log_dirr(sQ€ä9‰9Ğ)¨2Ó.€DÙÜ‹J‰ä”‹N×"Ñ"Ó$×+Ñ+¨fÑ4ˆØ‡GGD 4€GÔ(Ø€Hrcóê—t«|dœ|¥}tj|d¬«}t|d¬«	t	«dzjdd¬	«j|d
z«y#t$rYywxYw)zh
    Operational logging only. Never log prompt or output text.
    Emits JSONL for easy ingestion.
    )ÚtsÚeventF)Úensure_asciiT)Úflushzai_gateway.log.jsonlÚar)Úencodingú
N)rÚjsonÚdumpsÚprintr(ÚopenÚwriteÚ	Exception)r+ÚfieldsÚrecÚlines    rÚ	log_eventr:ss€ô
“ eÑ
6¨vĞ
6€CÜ:‰:c¨Ô.€DÜ	ˆ$dÕğÜ	‹Ğ,Ñ	,×2Ñ2°3ÀĞ2ÓI×OÑOĞPTĞW[ÑP[Õ\øÜòáğúsµ0A&Á&	A2Á1A2)ÚreturnÚstr)rr<r;r<)r;r)r+r<r7rr;ÚNone)Ú
__future__rrr1r rÚpathlibrÚtypingrrrr(r:rrrú<module>rAs0ğİ"ãÛÛ	İİİóAóJóôr
```

## File: `/home/user/AA1/gateways/ai_gateway/ai_gateway/__pycache__/config.cpython-312.pyc`

```
Ë
$×pinãóh—ddlmZddlZddlmZed¬«Gd„d««Zdd„Zdd	„Zdd
„Zy)é)ÚannotationsN)Ú	dataclassT)Úfrozencó^—eZdZUded<ded<ded<ded<ded<ded	<d
ed<d
ed<y)ÚGatewayConfigÚstrÚproviderÚmodelÚfloatÚ	timeout_sÚintÚmax_retriesÚbackoff_base_sÚbackoff_max_sz
str | NoneÚgemini_api_keyÚopenai_api_keyN)Ú__name__Ú
__module__Ú__qualname__Ú__annotations__©óú7/home/user/AA1/gateways/ai_gateway/ai_gateway/config.pyrrs0…àƒMØƒJØÓØÓØÓØÓàÓØÔrrcó”—tj|«}||j«dk(r|S	t|«S#t$r|cYSwxYw©NÚ)ÚosÚgetenvÚstriprÚ
ValueError©ÚnameÚdefaultÚvs   rÚ
_get_floatr%sG€Ü
	‰	$‹€AØ€yA—G‘G“I ’OØˆğÜQ‹xˆøÜòØŠğúó®
9¹AÁAcó”—tj|«}||j«dk(r|S	t|«S#t$r|cYSwxYwr)rrrrr r!s   rÚ_get_intr(sG€Ü
	‰	$‹€AØ€yA—G‘G“I ’OØˆğÜ1‹vˆøÜòØŠğúr&c
ó¤—tjdd«j«j«}tjdd«j«}t	dd«}tdd«}t	d	d
«}t	dd«}tjd«xstjd«}tjd«xstjd«}|s^|dk(r%tjdd«j«}n4|dk(r%tjdd«j«}n
|dk(rd}nd}t||||||||¬«S)NÚAI_GATEWAY_PROVIDERÚgeminiÚAI_GATEWAY_MODELrÚAI_GATEWAY_TIMEOUT_SgN@ÚAI_GATEWAY_RETRIESéÚAI_GATEWAY_BACKOFF_BASE_Sgğ?ÚAI_GATEWAY_BACKOFF_MAX_Sg4@ÚGEMINI_API_KEYÚAI_GATEWAY_GEMINI_API_KEYÚOPENAI_API_KEYÚAI_GATEWAY_OPENAI_API_KEYÚGEMINI_MODELzgemini-2.5-flashÚopenaiÚOPENAI_MODELzgpt-4.1-miniÚoffliner#©r	r
rrrrrr)rrrÚlowerr%r(rr:s        rÚload_configr<(s0€äy‰yĞ.°Ó9×?Ñ?ÓA×GÑGÓI€HÜI‰IĞ(¨"Ó-×3Ñ3Ó5€EäĞ1°4Ó8€IÜĞ/°Ó3€KÜĞ ;¸SÓA€NÜĞ9¸4Ó@€Mô—Y‘YĞ/Ó0ÒZ´B·I±IĞ>YÓ4Z€NÜ—Y‘YĞ/Ó0ÒZ´B·I±IĞ>YÓ4Z€NñØxÒÜ—I‘I˜nĞ.@ÓA×GÑGÓI‰EØ˜Ò!Ü—I‘I˜n¨nÓ=×CÑCÓE‰EØ˜Ò"Ø‰EàˆEäØØØØØ%Ø#Ø%Ø%ô	ğ	r)r"rr#rÚreturnr)r"rr#rr=r)r=r)	Ú
__future__rrÚdataclassesrrr%r(r<rrrú<module>r@s;ğİ"ã	İ!ñ$Ô÷	ğ	óğ	óóô"r
```

## File: `/home/user/AA1/gateways/ai_gateway/README.md`

```

```

## File: `/home/user/AA1/gateways/ai_gateway/gateways_full_dump.md`

```
# Gateways Repository Snapshot

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/client.py

```
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from .config import GatewayConfig, load_config
from .errors import GatewayConfigError
from .logging import log_event, prompt_hash8
from .retry import RetryPolicy, run_with_retry
from .providers.gemini import call_gemini
from .providers.offline import call_offline

# openai provider can be added later without changing this contract.


@dataclass
class CallOptions:
    provider: Optional[str] = None
    model: Optional[str] = None
    timeout_s: Optional[float] = None
    temperature: Optional[float] = None  # accepted but provider may ignore
    max_tokens: Optional[int] = None     # accepted but provider may ignore


class AIGatewayClient:
    """
    AI Gateway public API.
    Contract: accepts prompt, returns raw model text unchanged.
    Handles only transport concerns (security, retries, stability, logging).
    """

    def __init__(self, cfg: Optional[GatewayConfig] = None):
        self.cfg = cfg or load_config()

    def call(self, prompt: str, *, options: Optional[CallOptions] = None) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt must be a non-empty string")

        opt = options or CallOptions()
        provider = (opt.provider or self.cfg.provider).strip().lower()
        model = (opt.model or self.cfg.model).strip()
        timeout_s = float(opt.timeout_s or self.cfg.timeout_s)

        ph = prompt_hash8(prompt)
        t0 = time.time()

        policy = RetryPolicy(
            max_retries=self.cfg.max_retries,
            backoff_base_s=self.cfg.backoff_base_s,
            backoff_max_s=self.cfg.backoff_max_s,
        )

        log_event(
            "ai_gateway.call.start",
            provider=provider,
            model=model,
            timeout_s=timeout_s,
            prompt_hash8=ph,
        )

        def _invoke() -> str:
            if provider == "offline":
                return call_offline(prompt=prompt, model=model, timeout_s=timeout_s)

            if provider == "gemini":
                if not self.cfg.gemini_api_key:
                    raise GatewayConfigError("Missing GEMINI_API_KEY (or AI_GATEWAY_GEMINI_API_KEY).")
                return call_gemini(
                    prompt=prompt,
                    model=model,
                    api_key=self.cfg.gemini_api_key,
                    timeout_s=timeout_s,
                )

            raise GatewayConfigError(f"Unknown provider: {provider}")

        try:
            out = run_with_retry(_invoke, policy)
            ms = int((time.time() - t0) * 1000)
            log_event(
                "ai_gateway.call.ok",
                provider=provider,
                model=model,
                latency_ms=ms,
                prompt_hash8=ph,
            )
            return out
        except Exception as e:
            ms = int((time.time() - t0) * 1000)
            log_event(
                "ai_gateway.call.fail",
                provider=provider,
                model=model,
                latency_ms=ms,
                prompt_hash8=ph,
                error_type=type(e).__name__,
            )
            raise

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/config.py

```
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class GatewayConfig:
    provider: str
    model: str
    timeout_s: float
    max_retries: int
    backoff_base_s: float
    backoff_max_s: float
    # Provider keys (kept here to avoid scattering env reads)
    gemini_api_key: str | None
    openai_api_key: str | None


def _get_float(name: str, default: float) -> float:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    try:
        return float(v)
    except ValueError:
        return default


def _get_int(name: str, default: int) -> int:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    try:
        return int(v)
    except ValueError:
        return default


def load_config() -> GatewayConfig:
    # Stable, boring env var surface
    provider = os.getenv("AI_GATEWAY_PROVIDER", "gemini").strip().lower()
    model = os.getenv("AI_GATEWAY_MODEL", "").strip()

    timeout_s = _get_float("AI_GATEWAY_TIMEOUT_S", 60.0)
    max_retries = _get_int("AI_GATEWAY_RETRIES", 3)
    backoff_base_s = _get_float("AI_GATEWAY_BACKOFF_BASE_S", 1.0)
    backoff_max_s = _get_float("AI_GATEWAY_BACKOFF_MAX_S", 20.0)

    # Provider-specific keys (still env-only)
    gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("AI_GATEWAY_GEMINI_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY") or os.getenv("AI_GATEWAY_OPENAI_API_KEY")

    # Provide sane default model if not set
    if not model:
        if provider == "gemini":
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        elif provider == "openai":
            model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
        elif provider == "offline":
            model = "offline"
        else:
            model = "default"

    return GatewayConfig(
        provider=provider,
        model=model,
        timeout_s=timeout_s,
        max_retries=max_retries,
        backoff_base_s=backoff_base_s,
        backoff_max_s=backoff_max_s,
        gemini_api_key=gemini_api_key,
        openai_api_key=openai_api_key,
    )

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/errors.py

```
# Transport-level errors only. No semantics, no workflow logic.

from __future__ import annotations


class AIGatewayError(RuntimeError):
    """Base class for AI Gateway transport errors."""


class GatewayConfigError(AIGatewayError):
    """Misconfiguration (missing keys, invalid provider/model)."""


class GatewayTimeoutError(AIGatewayError):
    """Request exceeded timeout."""


class GatewayAuthError(AIGatewayError):
    """Authentication/authorization failure."""


class GatewayRateLimitError(AIGatewayError):
    """Supplier rate limited the request (HTTP 429)."""


class GatewayUpstreamError(AIGatewayError):
    """Supplier/service error (5xx or other upstream failure)."""


class GatewayClientError(AIGatewayError):
    """Non-retryable client error (4xx except 429)."""

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/__init__.py

```
from .client import AIGatewayClient, CallOptions
from .errors import (
    AIGatewayError,
    GatewayConfigError,
    GatewayTimeoutError,
    GatewayAuthError,
    GatewayRateLimitError,
    GatewayUpstreamError,
    GatewayClientError,
)

__all__ = [
    "AIGatewayClient",
    "CallOptions",
    "AIGatewayError",
    "GatewayConfigError",
    "GatewayTimeoutError",
    "GatewayAuthError",
    "GatewayRateLimitError",
    "GatewayUpstreamError",
    "GatewayClientError",
]

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/logging.py

```
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def prompt_hash8(prompt: str) -> str:
    return hashlib.sha256((prompt or "").encode("utf-8")).hexdigest()[:8]


def _log_dir() -> Path:
    # Keep logs local to gateway by default, configurable if needed
    base = os.getenv("AI_GATEWAY_LOG_DIR", "")
    if base:
        p = Path(base)
    else:
        p = Path(__file__).resolve().parent / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p


def log_event(event: str, **fields: Any) -> None:
    """
    Operational logging only. Never log prompt or output text.
    Emits JSONL for easy ingestion.
    """
    rec = {"ts": _utc_now(), "event": event, **fields}
    line = json.dumps(rec, ensure_ascii=False)
    print(line, flush=True)

    try:
        (_log_dir() / "ai_gateway.log.jsonl").open("a", encoding="utf-8").write(line + "\n")
    except Exception:
        # Logging must never break the call path
        pass

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/logs/ai_gateway.log.jsonl

```
{"ts": "2026-01-21T13:51:46Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T13:51:46Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 73, "prompt_hash8": "d3e9ca8a", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T13:52:09Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "offline", "timeout_s": 60.0, "prompt_hash8": "3514cf81"}
{"ts": "2026-01-21T13:52:09Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "offline", "latency_ms": 0, "prompt_hash8": "3514cf81"}
{"ts": "2026-01-21T13:53:38Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T13:53:38Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 65, "prompt_hash8": "d3e9ca8a", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:09:52Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T14:09:52Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 658, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T14:10:21Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T14:10:21Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 527, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 68, "prompt_hash8": "73d07d68", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 51, "prompt_hash8": "5857ac47", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 53, "prompt_hash8": "a936bf73", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 58, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:32:38Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 66, "prompt_hash8": "73d07d68", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 55, "prompt_hash8": "5857ac47", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 51, "prompt_hash8": "a936bf73", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 53, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 56, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:08Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:34:08Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 65, "prompt_hash8": "73d07d68", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:08Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:34:08Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 55, "prompt_hash8": "5857ac47", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 56, "prompt_hash8": "a936bf73", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 50, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 56, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "unknown", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.fail", "provider": "unknown", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayAuthError"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "unknown", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.fail", "provider": "unknown", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayAuthError"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.start", "provider": "unknown", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.fail", "provider": "unknown", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayAuthError"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "unknown", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.fail", "provider": "unknown", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayAuthError"}

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/providers/gemini.py

```
from __future__ import annotations

import json
import time
import httpx

from ..errors import (
    GatewayAuthError,
    GatewayClientError,
    GatewayRateLimitError,
    GatewayTimeoutError,
    GatewayUpstreamError,
)

# NOTE: This is transport only: prompt -> text.
# No schema enforcement. No output interpretation.


def call_gemini(
    *,
    prompt: str,
    model: str,
    api_key: str,
    timeout_s: float,
) -> str:
    """
    Gemini generateContent (Generative Language API).
    Returns model text unchanged.
    """
    # Endpoint is configurable to survive API churn
    base = "https://generativelanguage.googleapis.com"
    version = "v1"
    endpoint = f"{base}/{version}/models/{model}:generateContent"

    headers = {
        "Content-Type": "application/json",
        # Prefer header auth; keep query-free by default
        "x-goog-api-key": api_key,
    }

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ]
    }

    t0 = time.time()
    try:
        with httpx.Client(timeout=timeout_s) as client:
            resp = client.post(endpoint, headers=headers, json=payload)
        # --- DEBUG PRINT ---
        print(f"DEBUG: Type of resp: {type(resp)}")
        print(f"DEBUG: Type of resp.status_code: {type(resp.status_code)}")
        print(f"DEBUG: Value of resp.status_code: {resp.status_code}")
        # --- END DEBUG PRINT ---
    except httpx.ReadTimeout as e:
        raise GatewayTimeoutError(f"Gemini timeout after {timeout_s}s") from e
    except httpx.RequestError as e:
        # Network/DNS/connectivity
        raise GatewayUpstreamError(f"Gemini request error: {type(e).__name__}") from e

    # Map errors
    if resp.status_code == 401 or resp.status_code == 403:
        raise GatewayAuthError(f"Gemini auth error: HTTP {resp.status_code}")
    if resp.status_code == 429:
        raise GatewayRateLimitError("Gemini rate limited (HTTP 429)")
    if 400 <= resp.status_code < 500:
        detail = _safe_err(resp)
        raise GatewayClientError(f"Gemini client error HTTP {resp.status_code}: {detail}")
    if resp.status_code >= 500:
        detail = _safe_err(resp)
        raise GatewayUpstreamError(f"Gemini upstream error HTTP {resp.status_code}: {detail}")

    # Parse response text (transport normalization only)
    try:
        data = resp.json()
    except Exception as e:
        raise GatewayUpstreamError("Gemini returned non-JSON response") from e

    text = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text")
    )
    # Return raw text as-is (contract), ensuring None becomes ""
    return text if text is not None else ""


def _safe_err(resp: httpx.Response) -> str:
    try:
        j = resp.json()
        if isinstance(j, dict) and "error" in j:
            e = j["error"]
            return f"{e.get('status','?')} {e.get('code','?')}: {e.get('message','')}"
        return json.dumps(j)[:300]
    except Exception:
        return (resp.text or "")[:300]
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/providers/__init__.py

```
# Provider modules live here.

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/providers/offline.py

```
from __future__ import annotations

def call_offline(*, prompt: str, model: str, timeout_s: float) -> str:
    # Deterministic stub for tests and offline runs
    return ""

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/providers/openai.py

```
# future

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/providers/__pycache__/gemini.cpython-312.pyc

```
Ë
Rçpióãóh—ddlmZddlZddlZddlZddlmZmZmZm	Z	m
Z
										dd„Zdd„Zy)	é)ÚannotationsNé)ÚGatewayAuthErrorÚGatewayClientErrorÚGatewayRateLimitErrorÚGatewayTimeoutErrorÚGatewayUpstreamErrorcóĞ—d}d}|›d|›d|›d}d|dœ}dd	d
|igdœgi}tj«}		tj|¬«5}
|
j|||¬«}ddd«t	dt«›«t	dt|j«›«t	d|j›«|jdk(s|jdk(rtd|j›«‚|jdk(rtd«‚d|jcxkrdkr)nn&t|«}td|j›d|›«‚|jdk\r&t|«}td|j›d|›«‚	|j!«}|j%d ig«d!j%d"i«j%d#ig«d!j%d
«}||Sd$S#1swYŒ}xYw#tj$r}td|›d«|‚d}~wtj$r'}tdt|«j›«|‚d}~wwxYw#t"$r}td«|‚d}~wwxYw)%z]
    Gemini generateContent (Generative Language API).
    Returns model text unchanged.
    z)https://generativelanguage.googleapis.comÚv1ú/z/models/z:generateContentzapplication/json)zContent-Typezx-goog-api-keyÚcontentsÚuserÚtext)ÚroleÚparts)Útimeout)ÚheadersÚjsonNzDEBUG: Type of resp: z!DEBUG: Type of resp.status_code: z"DEBUG: Value of resp.status_code: zGemini timeout after ÚszGemini request error: i‘i“zGemini auth error: HTTP i­zGemini rate limited (HTTP 429)iiôzGemini client error HTTP ú: zGemini upstream error HTTP z!Gemini returned non-JSON responseÚ
candidatesrÚcontentrÚ)ÚtimeÚhttpxÚClientÚpostÚprintÚtypeÚstatus_codeÚReadTimeoutrÚRequestErrorr	Ú__name__rrÚ	_safe_errrrÚ	ExceptionÚget)ÚpromptÚmodelÚapi_keyÚ	timeout_sÚbaseÚversionÚendpointrÚpayloadÚt0ÚclientÚrespÚeÚdetailÚdatars                úA/home/user/AA1/gateways/ai_gateway/ai_gateway/providers/gemini.pyÚcall_geminir6s¥€ğ7€DØ€GØq˜˜	 ¨%¨Ğ0@ĞA€Hğ+à!ñ€Gğ	Ø¨°Ğ'7Ğ&8Ñ9ğ
ğ€Gô
‰‹€BğWÜ\‰\ )Ô,ğ	H°Ø—;‘;˜x°¸w;ÓGˆD÷	Hô	Ğ%¤d¨4£j \Ğ2Ô3ÜĞ1´$°t×7GÑ7GÓ2HĞ1IĞJÔKÜĞ2°4×3CÑ3CĞ2DĞEÔFğ×Ñ˜3Ò $×"2Ñ"2°cÒ"9ÜĞ!9¸$×:JÑ:JĞ9KĞLÓMĞMØ×Ñ˜3ÒÜ#Ğ$DÓEĞEØ
ˆd×ÑÔ$ Õ$Ü˜4“ˆÜ Ğ#<¸T×=MÑ=MĞ<NÈbĞQWĞPXĞ!YÓZĞZØ×Ñ˜3ÒÜ˜4“ˆÜ"Ğ%@À×AQÑAQĞ@RĞRTĞU[ĞT\Ğ#]Ó^Ğ^ğOØy‰y‹{ˆğ
	‰ ˜tÓ$ QÑ'ß	‰ˆY˜Ó	ß	‰ˆWrdÓ	˜Añ	÷
‰ˆV‹ğ		ğĞ#ˆ4Ğ+¨Ğ+÷M	Hñ	Hûô×ÑòOÜ!Ğ$9¸)¸ÀAĞ"FÓGÈQĞNûÜ×ÑòWä"Ğ%;¼DÀ»G×<LÑ<LĞ;MĞ#NÓOĞUVĞVûğWûô&òOÜ"Ğ#FÓGÈQĞNûğOúsTµG(ÁGÁ AG(Å<IÇG%Ç G(Ç(IÇ;HÈIÈ!"IÉIÉ	I%ÉI É I%có>—	|j«}t|t«rCd|vr?|d}|jdd«›d|jdd«›d|jdd«›Stj|«dd	S#t
$r|jxsddd	cYSwxYw)
NÚerrorÚstatusú?ú ÚcoderÚmessageri,)rÚ
isinstanceÚdictr&Údumpsr%r)r1Újr2s   r5r$r$Zs €ğ'ØI‰I‹KˆÜaœÔ 7¨a¡<Ø'‘
ˆAØ—e‘e˜H SÓ)Ğ*¨!¨A¯E©E°&¸Ó,=Ğ+>¸bÀÇÁÀyĞQSÓATĞ@UĞVĞVÜz‰z˜!‹}˜T˜cĞ"Ğ"øÜò'Ø—	‘	’˜R  #Ğ&Ò&ğ'ús‚A"A=Á%A=Á=BÂB)
r'Ústrr(rBr)rBr*ÚfloatÚreturnrB)r1zhttpx.ResponserDrB)Ú
__future__rrrrÚerrorsrrrrr	r6r$©ór5ú<module>rIs\ğİ"ãÛÛ÷õğD,àğD,ğğD,ğğ	D,ğ
ğD,ğ	óD,ôN'rH
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/providers/__pycache__/__init__.cpython-312.pyc

```
Ë
¤×piãó—y)N©róúC/home/user/AA1/gateways/ai_gateway/ai_gateway/providers/__init__.pyú<module>rsñr
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/providers/__pycache__/offline.cpython-312.pyc

```
Ë
ˆ×pi­ãó—ddlmZdd„Zy)é)Úannotationscó—y)NÚ©)ÚpromptÚmodelÚ	timeout_ss   úB/home/user/AA1/gateways/ai_gateway/ai_gateway/providers/offline.pyÚcall_offliners€àóN)rÚstrrrr	ÚfloatÚreturnr)Ú
__future__rrrrr
ú<module>rsğİ"ôr
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/__pycache__/client.cpython-312.pyc

```
Ë
”×pi¡ãó¶—ddlmZddlZddlmZddlmZddlmZm	Z	ddl
mZddlmZmZdd	lmZmZdd
lmZddlmZeGd„d««ZGd„d«Zy)é)ÚannotationsN)Ú	dataclass)ÚOptionalé)ÚGatewayConfigÚload_config)ÚGatewayConfigError)Ú	log_eventÚprompt_hash8)ÚRetryPolicyÚrun_with_retry)Úcall_gemini)Úcall_offlinecóT—eZdZUdZded<dZded<dZded<dZded<dZded	<y)
ÚCallOptionsNzOptional[str]ÚproviderÚmodelzOptional[float]Ú	timeout_sÚtemperaturezOptional[int]Ú
max_tokens)	Ú__name__Ú
__module__Ú__qualname__rÚ__annotations__rrrr©óú7/home/user/AA1/gateways/ai_gateway/ai_gateway/client.pyrrs4…à"€HˆmÓ"Ø€Eˆ=ÓØ!%€IˆÓ%Ø#'€KÓ'Ø $€JÔ$rrcó(—eZdZdZddd„Zddœdd„Zy)	ÚAIGatewayClientz­
    AI Gateway public API.
    Contract: accepts prompt, returns raw model text unchanged.
    Handles only transport concerns (security, retries, stability, logging).
    Ncó*—|xs
t«|_y©N)rÚcfg)Úselfr"s  rÚ__init__zAIGatewayClient.__init__!s€ØÒ'œ+›-ˆr)Úoptionscóø‡‡‡‡‡—t‰t«r‰j«std«‚|xs
t	«}|j
xs‰jj
j«j«Š|jxs‰jjj«Št|jxs‰jj«Št‰«}tj«}t‰jj‰jj‰jj ¬«}t#d‰‰‰|¬«dˆˆˆˆˆfd„}	t%||«}t'tj«|z
dz«}	t#d‰‰|	|¬«|S#t($rM}
t'tj«|z
dz«}	t#d	‰‰|	|t+|
«j,¬
«‚d}
~
wwxYw)Nz!prompt must be a non-empty string)Úmax_retriesÚbackoff_base_sÚbackoff_max_szai_gateway.call.start)rrrrcóØ•—‰dk(rt‰‰‰¬«S‰dk(rD‰jjstd«‚t	‰‰‰jj‰¬«Std‰›«‚)NÚoffline)ÚpromptrrÚgeminiz6Missing GEMINI_API_KEY (or AI_GATEWAY_GEMINI_API_KEY).)r,rÚapi_keyrzUnknown provider: )rr"Úgemini_api_keyr	r)rr,rr#rs€€€€€rÚ_invokez%AIGatewayClient.call.<locals>._invoke>ssø€Ø˜9Ò$Ü#¨6¸È)ÔTĞTà˜8Ò#Ø—x‘x×.Ò.Ü,Ğ-eÓfĞfÜ"Ø!ØØ ŸH™H×3Ñ3Ø'ô	ğô%Ğ'9¸(¸Ğ%DÓEĞErièzai_gateway.call.ok)rrÚ
latency_msrzai_gateway.call.fail)rrr1rÚ
error_type)ÚreturnÚstr)Ú
isinstancer4ÚstripÚ
ValueErrorrrr"ÚlowerrÚfloatrrÚtimerr'r(r)r
rÚintÚ	ExceptionÚtyper)r#r,r%ÚoptÚphÚt0Úpolicyr0ÚoutÚmsÚerrrs``         @@@rÚcallzAIGatewayClient.call$sšü€Ü˜&¤#Ô&¨f¯l©l¬nÜĞ@ÓAĞAàÒ&œ›ˆØ—L‘LÒ5 D§H¡H×$5Ñ$5×<Ñ<Ó>×DÑDÓFˆØ—‘Ò,˜dŸh™hŸn™n×3Ñ3Ó5ˆÜ˜#Ÿ-™-Ò=¨4¯8©8×+=Ñ+=Ó>ˆ	ä˜&Ó!ˆÜY‰Y‹[ˆäØŸ™×,Ñ,ØŸ8™8×2Ñ2ØŸ(™(×0Ñ0ô
ˆô	Ø#ØØØØõ	
÷	Fñ	Fğ 	Ü  ¨&Ó1ˆCÜ”d—i‘i“k BÑ&¨$Ñ.Ó/ˆBÜØ$Ø!ØØØõğˆJøÜò
	Ü”d—i‘i“k BÑ&¨$Ñ.Ó/ˆBÜØ&Ø!ØØØÜ ›7×+Ñ+õğûğ
	úsÅ"AF#Æ#	G9Æ,AG4Ç4G9r!)r"zOptional[GatewayConfig])r,r4r%zOptional[CallOptions]r3r4)rrrÚ__doc__r$rErrrrrs„ñô(ğEIö?rr)Ú
__future__rr:ÚdataclassesrÚtypingrÚconfigrrÚerrorsr	Úloggingr
rÚretryrrÚproviders.geminirÚproviders.offlinerrrrrrú<module>rPsHğİ"ãİ!İç.İ&ß,ß.İ)İ+ğ
÷%ğ%óğ%÷IòIr
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/__pycache__/config.cpython-312.pyc

```
Ë
$×pinãóh—ddlmZddlZddlmZed¬«Gd„d««Zdd„Zdd	„Zdd
„Zy)é)ÚannotationsN)Ú	dataclassT)Úfrozencó^—eZdZUded<ded<ded<ded<ded<ded	<d
ed<d
ed<y)ÚGatewayConfigÚstrÚproviderÚmodelÚfloatÚ	timeout_sÚintÚmax_retriesÚbackoff_base_sÚbackoff_max_sz
str | NoneÚgemini_api_keyÚopenai_api_keyN)Ú__name__Ú
__module__Ú__qualname__Ú__annotations__©óú7/home/user/AA1/gateways/ai_gateway/ai_gateway/config.pyrrs0…àƒMØƒJØÓØÓØÓØÓàÓØÔrrcó”—tj|«}||j«dk(r|S	t|«S#t$r|cYSwxYw©NÚ)ÚosÚgetenvÚstriprÚ
ValueError©ÚnameÚdefaultÚvs   rÚ
_get_floatr%sG€Ü
	‰	$‹€AØ€yA—G‘G“I ’OØˆğÜQ‹xˆøÜòØŠğúó®
9¹AÁAcó”—tj|«}||j«dk(r|S	t|«S#t$r|cYSwxYwr)rrrrr r!s   rÚ_get_intr(sG€Ü
	‰	$‹€AØ€yA—G‘G“I ’OØˆğÜ1‹vˆøÜòØŠğúr&c
ó¤—tjdd«j«j«}tjdd«j«}t	dd«}tdd«}t	d	d
«}t	dd«}tjd«xstjd«}tjd«xstjd«}|s^|dk(r%tjdd«j«}n4|dk(r%tjdd«j«}n
|dk(rd}nd}t||||||||¬«S)NÚAI_GATEWAY_PROVIDERÚgeminiÚAI_GATEWAY_MODELrÚAI_GATEWAY_TIMEOUT_SgN@ÚAI_GATEWAY_RETRIESéÚAI_GATEWAY_BACKOFF_BASE_Sgğ?ÚAI_GATEWAY_BACKOFF_MAX_Sg4@ÚGEMINI_API_KEYÚAI_GATEWAY_GEMINI_API_KEYÚOPENAI_API_KEYÚAI_GATEWAY_OPENAI_API_KEYÚGEMINI_MODELzgemini-2.5-flashÚopenaiÚOPENAI_MODELzgpt-4.1-miniÚoffliner#©r	r
rrrrrr)rrrÚlowerr%r(rr:s        rÚload_configr<(s0€äy‰yĞ.°Ó9×?Ñ?ÓA×GÑGÓI€HÜI‰IĞ(¨"Ó-×3Ñ3Ó5€EäĞ1°4Ó8€IÜĞ/°Ó3€KÜĞ ;¸SÓA€NÜĞ9¸4Ó@€Mô—Y‘YĞ/Ó0ÒZ´B·I±IĞ>YÓ4Z€NÜ—Y‘YĞ/Ó0ÒZ´B·I±IĞ>YÓ4Z€NñØxÒÜ—I‘I˜nĞ.@ÓA×GÑGÓI‰EØ˜Ò!Ü—I‘I˜n¨nÓ=×CÑCÓE‰EØ˜Ò"Ø‰EàˆEäØØØØØ%Ø#Ø%Ø%ô	ğ	r)r"rr#rÚreturnr)r"rr#rr=r)r=r)	Ú
__future__rrÚdataclassesrrr%r(r<rrrú<module>r@s;ğİ"ã	İ!ñ$Ô÷	ğ	óğ	óóô"r
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/__pycache__/errors.cpython-312.pyc

```
Ë
×piãóª—ddlmZGd„de«ZGd„de«ZGd„de«ZGd„d	e«ZGd
„de«ZGd„de«ZGd„de«Z	y)é)Úannotationscó—eZdZdZy)ÚAIGatewayErrorz+Base class for AI Gateway transport errors.N©Ú__name__Ú
__module__Ú__qualname__Ú__doc__©óú7/home/user/AA1/gateways/ai_gateway/ai_gateway/errors.pyrrs„Ú5rrcó—eZdZdZy)ÚGatewayConfigErrorz8Misconfiguration (missing keys, invalid provider/model).Nrrrrrr
s„ÚBrrcó—eZdZdZy)ÚGatewayTimeoutErrorzRequest exceeded timeout.Nrrrrrrs„Ú#rrcó—eZdZdZy)ÚGatewayAuthErrorz%Authentication/authorization failure.Nrrrrrrs„Ú/rrcó—eZdZdZy)ÚGatewayRateLimitErrorz-Supplier rate limited the request (HTTP 429).Nrrrrrrs„Ú7rrcó—eZdZdZy)ÚGatewayUpstreamErrorz7Supplier/service error (5xx or other upstream failure).Nrrrrrrs„ÚArrcó—eZdZdZy)ÚGatewayClientErrorz,Non-retryable client error (4xx except 429).Nrrrrrrs„Ú6rrN)
Ú
__future__rÚRuntimeErrorrrrrrrrrrrú<module>rsbğõ#ô6\ô6ôC˜ôCô$˜.ô$ô0~ô0ô8˜Nô8ôB˜>ôBô7˜õ7r
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/__pycache__/__init__.cpython-312.pyc

```
Ë
9Øpiàãó@—ddlmZmZddlmZmZmZmZmZm	Z	m
Z
gd¢Zy)é)ÚAIGatewayClientÚCallOptions)ÚAIGatewayErrorÚGatewayConfigErrorÚGatewayTimeoutErrorÚGatewayAuthErrorÚGatewayRateLimitErrorÚGatewayUpstreamErrorÚGatewayClientError)	rrrrrrr	r
rN)ÚclientrrÚerrorsrrrrr	r
rÚ__all__©óú9/home/user/AA1/gateways/ai_gateway/ai_gateway/__init__.pyú<module>rsğß0÷÷ñò
r
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/__pycache__/logging.cpython-312.pyc

```
Ë
A×pimãól—ddlmZddlZddlZddlZddlmZddlmZddlm	Z	d
d„Z
dd„Zdd„Zdd	„Zy)é)ÚannotationsN)Údatetime)ÚPath)ÚAnycóP—tj«jd¬«dzS)NÚseconds)ÚtimespecÚZ)rÚutcnowÚ	isoformat©óú8/home/user/AA1/gateways/ai_gateway/ai_gateway/logging.pyÚ_utc_nowrs"€Ü?‰?Ó×&Ñ&°	Ğ&Ó:¸SÑ@Ğ@rcót—tj|xsdjd««j«ddS)NÚúutf-8é)ÚhashlibÚsha256ÚencodeÚ	hexdigest)Úprompts rÚprompt_hash8rs0€Ü>‰>˜6š< R×/Ñ/°Ó8Ó9×CÑCÓEÀbÀqĞIĞIrcóÈ—tjdd«}|rt|«}n*tt«j	«j
dz}|jdd¬«|S)NÚAI_GATEWAY_LOG_DIRrÚlogsT)ÚparentsÚexist_ok)ÚosÚgetenvrÚ__file__ÚresolveÚparentÚmkdir)ÚbaseÚps  rÚ_log_dirr(sQ€ä9‰9Ğ)¨2Ó.€DÙÜ‹J‰ä”‹N×"Ñ"Ó$×+Ñ+¨fÑ4ˆØ‡GGD 4€GÔ(Ø€Hrcóê—t«|dœ|¥}tj|d¬«}t|d¬«	t	«dzjdd¬	«j|d
z«y#t$rYywxYw)zh
    Operational logging only. Never log prompt or output text.
    Emits JSONL for easy ingestion.
    )ÚtsÚeventF)Úensure_asciiT)Úflushzai_gateway.log.jsonlÚar)Úencodingú
N)rÚjsonÚdumpsÚprintr(ÚopenÚwriteÚ	Exception)r+ÚfieldsÚrecÚlines    rÚ	log_eventr:ss€ô
“ eÑ
6¨vĞ
6€CÜ:‰:c¨Ô.€DÜ	ˆ$dÕğÜ	‹Ğ,Ñ	,×2Ñ2°3ÀĞ2ÓI×OÑOĞPTĞW[ÑP[Õ\øÜòáğúsµ0A&Á&	A2Á1A2)ÚreturnÚstr)rr<r;r<)r;r)r+r<r7rr;ÚNone)Ú
__future__rrr1r rÚpathlibrÚtypingrrrr(r:rrrú<module>rAs0ğİ"ãÛÛ	İİİóAóJóôr
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/__pycache__/retry.cpython-312.pyc

```
Ë
S×piŒãó¦—ddlmZddlZddlZddlmZddlmZmZddl	m
Z
mZmZed«Zed¬	«Gd
„d««Zee
efZdd„Zdd„Zy)é)ÚannotationsN)Ú	dataclass)ÚCallableÚTypeVaré)ÚGatewayRateLimitErrorÚGatewayTimeoutErrorÚGatewayUpstreamErrorÚTT)Úfrozencó8—eZdZUdZded<dZded<dZded<y	)
ÚRetryPolicyéÚintÚmax_retriesgğ?ÚfloatÚbackoff_base_sg4@Úbackoff_max_sN)Ú__name__Ú
__module__Ú__qualname__rÚ__annotations__rr©óú6/home/user/AA1/gateways/ai_gateway/ai_gateway/retry.pyrrs …à€KÓØ€NEÓØ€M5Ôrrcó—|jdtd|«zz}tjdd|z«}t	|j
||z«S)NérggĞ?)rÚmaxÚrandomÚuniformÚminr)ÚpolicyÚattemptÚbaseÚjitters    rÚ_sleep_sr&sH€à× Ñ  A¬¨Q°«Ñ$8Ñ9€DÜ^‰^˜C ¨¡Ó-€FÜˆv×#Ñ# T¨F¡]Ó3Ğ3rcóì—d}t|jdz«D]}	|«cS|€J‚|‚#t$r;}|}||jk\r‚tjt||««Yd}~ŒSd}~wwxYw)Nr)ÚrangerÚ
_RETRYABLEÚtimeÚsleepr&)Úfnr"Úlast_excr#Úes     rÚrun_with_retryr/"sƒ€Ø!%€HÜ˜×+Ñ+¨aÑ/Ó0ò2ˆğ	2Ù“4ŠKğ2ğĞĞĞØ
€Nøôò	2ØˆHØ˜&×,Ñ,Ò,ØÜJ‰J”x ¨Ó0×1Ñ1ûğ		2úsŸ/¯	A3¸1A.Á.A3)r"rr#rÚreturnr)r,zCallable[[], T]r"rr0r)Ú
__future__rrr*ÚdataclassesrÚtypingrrÚerrorsrr	r
rrr)r&r/rrrú<module>r5sağİ"ãÛİ!ß$÷ññˆCƒL€ñ$Ô÷ ğ óğ ğ"Ğ#8Ğ:NĞO€
ó4ôr
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/retry.py

```
from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, TypeVar

from .errors import (
    GatewayRateLimitError,
    GatewayTimeoutError,
    GatewayUpstreamError,
)

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = 3
    backoff_base_s: float = 1.0
    backoff_max_s: float = 20.0


_RETRYABLE = (GatewayTimeoutError, GatewayRateLimitError, GatewayUpstreamError)


def _sleep_s(policy: RetryPolicy, attempt: int) -> float:
    # exp backoff with jitter
    base = policy.backoff_base_s * (2 ** max(0, attempt))
    jitter = random.uniform(0.0, 0.25 * base)
    return min(policy.backoff_max_s, base + jitter)


def run_with_retry(fn: Callable[[], T], policy: RetryPolicy) -> T:
    last_exc: Exception | None = None
    for attempt in range(policy.max_retries + 1):
        try:
            return fn()
        except _RETRYABLE as e:
            last_exc = e
            if attempt >= policy.max_retries:
                raise
            time.sleep(_sleep_s(policy, attempt))
    # Should be unreachable
    assert last_exc is not None
    raise last_exc

```

## File: /home/user/AA1/gateways/ai_gateway/gateways_full_dump.md

```

```

## File: /home/user/AA1/gateways/ai_gateway/poetry.lock

```
# This file is automatically @generated by Poetry 2.3.1 and should not be changed by hand.

[[package]]
name = "annotated-types"
version = "0.7.0"
description = "Reusable constraint types to use with typing.Annotated"
optional = false
python-versions = ">=3.8"
groups = ["main"]
files = [
    {file = "annotated_types-0.7.0-py3-none-any.whl", hash = "sha256:1f02e8b43a8fbbc3f3e0d4f0f4bfc8131bcb4eebe8849b8e5c773f3a1c582a53"},
    {file = "annotated_types-0.7.0.tar.gz", hash = "sha256:aff07c09a53a08bc8cfccb9c85b05f1aa9a2a6f23728d790723543408344ce89"},
]

[[package]]
name = "anyio"
version = "4.12.1"
description = "High-level concurrency and networking framework on top of asyncio or Trio"
optional = false
python-versions = ">=3.9"
groups = ["main"]
files = [
    {file = "anyio-4.12.1-py3-none-any.whl", hash = "sha256:d405828884fc140aa80a3c667b8beed277f1dfedec42ba031bd6ac3db606ab6c"},
    {file = "anyio-4.12.1.tar.gz", hash = "sha256:41cfcc3a4c85d3f05c932da7c26d0201ac36f72abd4435ba90d0464a3ffed703"},
]

[package.dependencies]
idna = ">=2.8"
typing_extensions = {version = ">=4.5", markers = "python_version < \"3.13\""}

[package.extras]
trio = ["trio (>=0.31.0) ; python_version < \"3.10\"", "trio (>=0.32.0) ; python_version >= \"3.10\""]

[[package]]
name = "backoff"
version = "2.2.1"
description = "Function decoration for backoff and retry"
optional = false
python-versions = ">=3.7,<4.0"
groups = ["main"]
files = [
    {file = "backoff-2.2.1-py3-none-any.whl", hash = "sha256:63579f9a0628e06278f7e47b7d7d5b6ce20dc65c5e96a6f3ca99a6adca0396e8"},
    {file = "backoff-2.2.1.tar.gz", hash = "sha256:03f829f5bb1923180821643f8753b0502c3b682293992485b0eef2807afa5cba"},
]

[[package]]
name = "certifi"
version = "2026.1.4"
description = "Python package for providing Mozilla's CA Bundle."
optional = false
python-versions = ">=3.7"
groups = ["main"]
files = [
    {file = "certifi-2026.1.4-py3-none-any.whl", hash = "sha256:9943707519e4add1115f44c2bc244f782c0249876bf51b6599fee1ffbedd685c"},
    {file = "certifi-2026.1.4.tar.gz", hash = "sha256:ac726dd470482006e014ad384921ed6438c457018f4b3d204aea4281258b2120"},
]

[[package]]
name = "colorama"
version = "0.4.6"
description = "Cross-platform colored terminal text."
optional = false
python-versions = "!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*,!=3.6.*,>=2.7"
groups = ["dev"]
markers = "sys_platform == \"win32\""
files = [
    {file = "colorama-0.4.6-py2.py3-none-any.whl", hash = "sha256:4f1d9991f5acc0ca119f9d443620b77f9d6b33703e51011c16baf57afb285fc6"},
    {file = "colorama-0.4.6.tar.gz", hash = "sha256:08695f5cb7ed6e0531a20572697297273c47b8cae5a63ffc6d6ed5c201be6e44"},
]

[[package]]
name = "h11"
version = "0.16.0"
description = "A pure-Python, bring-your-own-I/O implementation of HTTP/1.1"
optional = false
python-versions = ">=3.8"
groups = ["main"]
files = [
    {file = "h11-0.16.0-py3-none-any.whl", hash = "sha256:63cf8bbe7522de3bf65932fda1d9c2772064ffb3dae62d55932da54b31cb6c86"},
    {file = "h11-0.16.0.tar.gz", hash = "sha256:4e35b956cf45792e4caa5885e69fba00bdbc6ffafbfa020300e549b208ee5ff1"},
]

[[package]]
name = "httpcore"
version = "1.0.9"
description = "A minimal low-level HTTP client."
optional = false
python-versions = ">=3.8"
groups = ["main"]
files = [
    {file = "httpcore-1.0.9-py3-none-any.whl", hash = "sha256:2d400746a40668fc9dec9810239072b40b4484b640a8c38fd654a024c7a1bf55"},
    {file = "httpcore-1.0.9.tar.gz", hash = "sha256:6e34463af53fd2ab5d807f399a9b45ea31c3dfa2276f15a2c3f00afff6e176e8"},
]

[package.dependencies]
certifi = "*"
h11 = ">=0.16"

[package.extras]
asyncio = ["anyio (>=4.0,<5.0)"]
http2 = ["h2 (>=3,<5)"]
socks = ["socksio (==1.*)"]
trio = ["trio (>=0.22.0,<1.0)"]

[[package]]
name = "httpx"
version = "0.26.0"
description = "The next generation HTTP client."
optional = false
python-versions = ">=3.8"
groups = ["main"]
files = [
    {file = "httpx-0.26.0-py3-none-any.whl", hash = "sha256:8915f5a3627c4d47b73e8202457cb28f1266982d1159bd5779d86a80c0eab1cd"},
    {file = "httpx-0.26.0.tar.gz", hash = "sha256:451b55c30d5185ea6b23c2c793abf9bb237d2a7dfb901ced6ff69ad37ec1dfaf"},
]

[package.dependencies]
anyio = "*"
certifi = "*"
httpcore = "==1.*"
idna = "*"
sniffio = "*"

[package.extras]
brotli = ["brotli ; platform_python_implementation == \"CPython\"", "brotlicffi ; platform_python_implementation != \"CPython\""]
cli = ["click (==8.*)", "pygments (==2.*)", "rich (>=10,<14)"]
http2 = ["h2 (>=3,<5)"]
socks = ["socksio (==1.*)"]

[[package]]
name = "idna"
version = "3.11"
description = "Internationalized Domain Names in Applications (IDNA)"
optional = false
python-versions = ">=3.8"
groups = ["main"]
files = [
    {file = "idna-3.11-py3-none-any.whl", hash = "sha256:771a87f49d9defaf64091e6e6fe9c18d4833f140bd19464795bc32d966ca37ea"},
    {file = "idna-3.11.tar.gz", hash = "sha256:795dafcc9c04ed0c1fb032c2aa73654d8e8c5023a7df64a53f39190ada629902"},
]

[package.extras]
all = ["flake8 (>=7.1.1)", "mypy (>=1.11.2)", "pytest (>=8.3.2)", "ruff (>=0.6.2)"]

[[package]]
name = "iniconfig"
version = "2.3.0"
description = "brain-dead simple config-ini parsing"
optional = false
python-versions = ">=3.10"
groups = ["dev"]
files = [
    {file = "iniconfig-2.3.0-py3-none-any.whl", hash = "sha256:f631c04d2c48c52b84d0d0549c99ff3859c98df65b3101406327ecc7d53fbf12"},
    {file = "iniconfig-2.3.0.tar.gz", hash = "sha256:c76315c77db068650d49c5b56314774a7804df16fee4402c1f19d6d15d8c4730"},
]

[[package]]
name = "packaging"
version = "25.0"
description = "Core utilities for Python packages"
optional = false
python-versions = ">=3.8"
groups = ["dev"]
files = [
    {file = "packaging-25.0-py3-none-any.whl", hash = "sha256:29572ef2b1f17581046b3a2227d5c611fb25ec70ca1ba8554b24b0e69331a484"},
    {file = "packaging-25.0.tar.gz", hash = "sha256:d443872c98d677bf60f6a1f2f8c1cb748e8fe762d2bf9d3148b5599295b0fc4f"},
]

[[package]]
name = "pluggy"
version = "1.6.0"
description = "plugin and hook calling mechanisms for python"
optional = false
python-versions = ">=3.9"
groups = ["dev"]
files = [
    {file = "pluggy-1.6.0-py3-none-any.whl", hash = "sha256:e920276dd6813095e9377c0bc5566d94c932c33b27a3e3945d8389c374dd4746"},
    {file = "pluggy-1.6.0.tar.gz", hash = "sha256:7dcc130b76258d33b90f61b658791dede3486c3e6bfb003ee5c9bfb396dd22f3"},
]

[package.extras]
dev = ["pre-commit", "tox"]
testing = ["coverage", "pytest", "pytest-benchmark"]

[[package]]
name = "pydantic"
version = "2.12.5"
description = "Data validation using Python type hints"
optional = false
python-versions = ">=3.9"
groups = ["main"]
files = [
    {file = "pydantic-2.12.5-py3-none-any.whl", hash = "sha256:e561593fccf61e8a20fc46dfc2dfe075b8be7d0188df33f221ad1f0139180f9d"},
    {file = "pydantic-2.12.5.tar.gz", hash = "sha256:4d351024c75c0f085a9febbb665ce8c0c6ec5d30e903bdb6394b7ede26aebb49"},
]

[package.dependencies]
annotated-types = ">=0.6.0"
pydantic-core = "2.41.5"
typing-extensions = ">=4.14.1"
typing-inspection = ">=0.4.2"

[package.extras]
email = ["email-validator (>=2.0.0)"]
timezone = ["tzdata ; python_version >= \"3.9\" and platform_system == \"Windows\""]

[[package]]
name = "pydantic-core"
version = "2.41.5"
description = "Core functionality for Pydantic validation and serialization"
optional = false
python-versions = ">=3.9"
groups = ["main"]
files = [
    {file = "pydantic_core-2.41.5-cp310-cp310-macosx_10_12_x86_64.whl", hash = "sha256:77b63866ca88d804225eaa4af3e664c5faf3568cea95360d21f4725ab6e07146"},
    {file = "pydantic_core-2.41.5-cp310-cp310-macosx_11_0_arm64.whl", hash = "sha256:dfa8a0c812ac681395907e71e1274819dec685fec28273a28905df579ef137e2"},
    {file = "pydantic_core-2.41.5-cp310-cp310-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:5921a4d3ca3aee735d9fd163808f5e8dd6c6972101e4adbda9a4667908849b97"},
    {file = "pydantic_core-2.41.5-cp310-cp310-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:e25c479382d26a2a41b7ebea1043564a937db462816ea07afa8a44c0866d52f9"},
    {file = "pydantic_core-2.41.5-cp310-cp310-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:f547144f2966e1e16ae626d8ce72b4cfa0caedc7fa28052001c94fb2fcaa1c52"},
    {file = "pydantic_core-2.41.5-cp310-cp310-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:6f52298fbd394f9ed112d56f3d11aabd0d5bd27beb3084cc3d8ad069483b8941"},
    {file = "pydantic_core-2.41.5-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:100baa204bb412b74fe285fb0f3a385256dad1d1879f0a5cb1499ed2e83d132a"},
    {file = "pydantic_core-2.41.5-cp310-cp310-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:05a2c8852530ad2812cb7914dc61a1125dc4e06252ee98e5638a12da6cc6fb6c"},
    {file = "pydantic_core-2.41.5-cp310-cp310-musllinux_1_1_aarch64.whl", hash = "sha256:29452c56df2ed968d18d7e21f4ab0ac55e71dc59524872f6fc57dcf4a3249ed2"},
    {file = "pydantic_core-2.41.5-cp310-cp310-musllinux_1_1_armv7l.whl", hash = "sha256:d5160812ea7a8a2ffbe233d8da666880cad0cbaf5d4de74ae15c313213d62556"},
    {file = "pydantic_core-2.41.5-cp310-cp310-musllinux_1_1_x86_64.whl", hash = "sha256:df3959765b553b9440adfd3c795617c352154e497a4eaf3752555cfb5da8fc49"},
    {file = "pydantic_core-2.41.5-cp310-cp310-win32.whl", hash = "sha256:1f8d33a7f4d5a7889e60dc39856d76d09333d8a6ed0f5f1190635cbec70ec4ba"},
    {file = "pydantic_core-2.41.5-cp310-cp310-win_amd64.whl", hash = "sha256:62de39db01b8d593e45871af2af9e497295db8d73b085f6bfd0b18c83c70a8f9"},
    {file = "pydantic_core-2.41.5-cp311-cp311-macosx_10_12_x86_64.whl", hash = "sha256:a3a52f6156e73e7ccb0f8cced536adccb7042be67cb45f9562e12b319c119da6"},
    {file = "pydantic_core-2.41.5-cp311-cp311-macosx_11_0_arm64.whl", hash = "sha256:7f3bf998340c6d4b0c9a2f02d6a400e51f123b59565d74dc60d252ce888c260b"},
    {file = "pydantic_core-2.41.5-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:378bec5c66998815d224c9ca994f1e14c0c21cb95d2f52b6021cc0b2a58f2a5a"},
    {file = "pydantic_core-2.41.5-cp311-cp311-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:e7b576130c69225432866fe2f4a469a85a54ade141d96fd396dffcf607b558f8"},
    {file = "pydantic_core-2.41.5-cp311-cp311-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:6cb58b9c66f7e4179a2d5e0f849c48eff5c1fca560994d6eb6543abf955a149e"},
    {file = "pydantic_core-2.41.5-cp311-cp311-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:88942d3a3dff3afc8288c21e565e476fc278902ae4d6d134f1eeda118cc830b1"},
    {file = "pydantic_core-2.41.5-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:f31d95a179f8d64d90f6831d71fa93290893a33148d890ba15de25642c5d075b"},
    {file = "pydantic_core-2.41.5-cp311-cp311-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:c1df3d34aced70add6f867a8cf413e299177e0c22660cc767218373d0779487b"},
    {file = "pydantic_core-2.41.5-cp311-cp311-musllinux_1_1_aarch64.whl", hash = "sha256:4009935984bd36bd2c774e13f9a09563ce8de4abaa7226f5108262fa3e637284"},
    {file = "pydantic_core-2.41.5-cp311-cp311-musllinux_1_1_armv7l.whl", hash = "sha256:34a64bc3441dc1213096a20fe27e8e128bd3ff89921706e83c0b1ac971276594"},
    {file = "pydantic_core-2.41.5-cp311-cp311-musllinux_1_1_x86_64.whl", hash = "sha256:c9e19dd6e28fdcaa5a1de679aec4141f691023916427ef9bae8584f9c2fb3b0e"},
    {file = "pydantic_core-2.41.5-cp311-cp311-win32.whl", hash = "sha256:2c010c6ded393148374c0f6f0bf89d206bf3217f201faa0635dcd56bd1520f6b"},
    {file = "pydantic_core-2.41.5-cp311-cp311-win_amd64.whl", hash = "sha256:76ee27c6e9c7f16f47db7a94157112a2f3a00e958bc626e2f4ee8bec5c328fbe"},
    {file = "pydantic_core-2.41.5-cp311-cp311-win_arm64.whl", hash = "sha256:4bc36bbc0b7584de96561184ad7f012478987882ebf9f9c389b23f432ea3d90f"},
    {file = "pydantic_core-2.41.5-cp312-cp312-macosx_10_12_x86_64.whl", hash = "sha256:f41a7489d32336dbf2199c8c0a215390a751c5b014c2c1c5366e817202e9cdf7"},
    {file = "pydantic_core-2.41.5-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:070259a8818988b9a84a449a2a7337c7f430a22acc0859c6b110aa7212a6d9c0"},
    {file = "pydantic_core-2.41.5-cp312-cp312-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:e96cea19e34778f8d59fe40775a7a574d95816eb150850a85a7a4c8f4b94ac69"},
    {file = "pydantic_core-2.41.5-cp312-cp312-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:ed2e99c456e3fadd05c991f8f437ef902e00eedf34320ba2b0842bd1c3ca3a75"},
    {file = "pydantic_core-2.41.5-cp312-cp312-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:65840751b72fbfd82c3c640cff9284545342a4f1eb1586ad0636955b261b0b05"},
    {file = "pydantic_core-2.41.5-cp312-cp312-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:e536c98a7626a98feb2d3eaf75944ef6f3dbee447e1f841eae16f2f0a72d8ddc"},
    {file = "pydantic_core-2.41.5-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:eceb81a8d74f9267ef4081e246ffd6d129da5d87e37a77c9bde550cb04870c1c"},
    {file = "pydantic_core-2.41.5-cp312-cp312-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:d38548150c39b74aeeb0ce8ee1d8e82696f4a4e16ddc6de7b1d8823f7de4b9b5"},
    {file = "pydantic_core-2.41.5-cp312-cp312-musllinux_1_1_aarch64.whl", hash = "sha256:c23e27686783f60290e36827f9c626e63154b82b116d7fe9adba1fda36da706c"},
    {file = "pydantic_core-2.41.5-cp312-cp312-musllinux_1_1_armv7l.whl", hash = "sha256:482c982f814460eabe1d3bb0adfdc583387bd4691ef00b90575ca0d2b6fe2294"},
    {file = "pydantic_core-2.41.5-cp312-cp312-musllinux_1_1_x86_64.whl", hash = "sha256:bfea2a5f0b4d8d43adf9d7b8bf019fb46fdd10a2e5cde477fbcb9d1fa08c68e1"},
    {file = "pydantic_core-2.41.5-cp312-cp312-win32.whl", hash = "sha256:b74557b16e390ec12dca509bce9264c3bbd128f8a2c376eaa68003d7f327276d"},
    {file = "pydantic_core-2.41.5-cp312-cp312-win_amd64.whl", hash = "sha256:1962293292865bca8e54702b08a4f26da73adc83dd1fcf26fbc875b35d81c815"},
    {file = "pydantic_core-2.41.5-cp312-cp312-win_arm64.whl", hash = "sha256:1746d4a3d9a794cacae06a5eaaccb4b8643a131d45fbc9af23e353dc0a5ba5c3"},
    {file = "pydantic_core-2.41.5-cp313-cp313-macosx_10_12_x86_64.whl", hash = "sha256:941103c9be18ac8daf7b7adca8228f8ed6bb7a1849020f643b3a14d15b1924d9"},
    {file = "pydantic_core-2.41.5-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:112e305c3314f40c93998e567879e887a3160bb8689ef3d2c04b6cc62c33ac34"},
    {file = "pydantic_core-2.41.5-cp313-cp313-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:0cbaad15cb0c90aa221d43c00e77bb33c93e8d36e0bf74760cd00e732d10a6a0"},
    {file = "pydantic_core-2.41.5-cp313-cp313-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:03ca43e12fab6023fc79d28ca6b39b05f794ad08ec2feccc59a339b02f2b3d33"},
    {file = "pydantic_core-2.41.5-cp313-cp313-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:dc799088c08fa04e43144b164feb0c13f9a0bc40503f8df3e9fde58a3c0c101e"},
    {file = "pydantic_core-2.41.5-cp313-cp313-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:97aeba56665b4c3235a0e52b2c2f5ae9cd071b8a8310ad27bddb3f7fb30e9aa2"},
    {file = "pydantic_core-2.41.5-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:406bf18d345822d6c21366031003612b9c77b3e29ffdb0f612367352aab7d586"},
    {file = "pydantic_core-2.41.5-cp313-cp313-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:b93590ae81f7010dbe380cdeab6f515902ebcbefe0b9327cc4804d74e93ae69d"},
    {file = "pydantic_core-2.41.5-cp313-cp313-musllinux_1_1_aarch64.whl", hash = "sha256:01a3d0ab748ee531f4ea6c3e48ad9dac84ddba4b0d82291f87248f2f9de8d740"},
    {file = "pydantic_core-2.41.5-cp313-cp313-musllinux_1_1_armv7l.whl", hash = "sha256:6561e94ba9dacc9c61bce40e2d6bdc3bfaa0259d3ff36ace3b1e6901936d2e3e"},
    {file = "pydantic_core-2.41.5-cp313-cp313-musllinux_1_1_x86_64.whl", hash = "sha256:915c3d10f81bec3a74fbd4faebe8391013ba61e5a1a8d48c4455b923bdda7858"},
    {file = "pydantic_core-2.41.5-cp313-cp313-win32.whl", hash = "sha256:650ae77860b45cfa6e2cdafc42618ceafab3a2d9a3811fcfbd3bbf8ac3c40d36"},
    {file = "pydantic_core-2.41.5-cp313-cp313-win_amd64.whl", hash = "sha256:79ec52ec461e99e13791ec6508c722742ad745571f234ea6255bed38c6480f11"},
    {file = "pydantic_core-2.41.5-cp313-cp313-win_arm64.whl", hash = "sha256:3f84d5c1b4ab906093bdc1ff10484838aca54ef08de4afa9de0f5f14d69639cd"},
    {file = "pydantic_core-2.41.5-cp314-cp314-macosx_10_12_x86_64.whl", hash = "sha256:3f37a19d7ebcdd20b96485056ba9e8b304e27d9904d233d7b1015db320e51f0a"},
    {file = "pydantic_core-2.41.5-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:1d1d9764366c73f996edd17abb6d9d7649a7eb690006ab6adbda117717099b14"},
    {file = "pydantic_core-2.41.5-cp314-cp314-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:25e1c2af0fce638d5f1988b686f3b3ea8cd7de5f244ca147c777769e798a9cd1"},
    {file = "pydantic_core-2.41.5-cp314-cp314-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:506d766a8727beef16b7adaeb8ee6217c64fc813646b424d0804d67c16eddb66"},
    {file = "pydantic_core-2.41.5-cp314-cp314-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:4819fa52133c9aa3c387b3328f25c1facc356491e6135b459f1de698ff64d869"},
    {file = "pydantic_core-2.41.5-cp314-cp314-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:2b761d210c9ea91feda40d25b4efe82a1707da2ef62901466a42492c028553a2"},
    {file = "pydantic_core-2.41.5-cp314-cp314-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:22f0fb8c1c583a3b6f24df2470833b40207e907b90c928cc8d3594b76f874375"},
    {file = "pydantic_core-2.41.5-cp314-cp314-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:2782c870e99878c634505236d81e5443092fba820f0373997ff75f90f68cd553"},
    {file = "pydantic_core-2.41.5-cp314-cp314-musllinux_1_1_aarch64.whl", hash = "sha256:0177272f88ab8312479336e1d777f6b124537d47f2123f89cb37e0accea97f90"},
    {file = "pydantic_core-2.41.5-cp314-cp314-musllinux_1_1_armv7l.whl", hash = "sha256:63510af5e38f8955b8ee5687740d6ebf7c2a0886d15a6d65c32814613681bc07"},
    {file = "pydantic_core-2.41.5-cp314-cp314-musllinux_1_1_x86_64.whl", hash = "sha256:e56ba91f47764cc14f1daacd723e3e82d1a89d783f0f5afe9c364b8bb491ccdb"},
    {file = "pydantic_core-2.41.5-cp314-cp314-win32.whl", hash = "sha256:aec5cf2fd867b4ff45b9959f8b20ea3993fc93e63c7363fe6851424c8a7e7c23"},
    {file = "pydantic_core-2.41.5-cp314-cp314-win_amd64.whl", hash = "sha256:8e7c86f27c585ef37c35e56a96363ab8de4e549a95512445b85c96d3e2f7c1bf"},
    {file = "pydantic_core-2.41.5-cp314-cp314-win_arm64.whl", hash = "sha256:e672ba74fbc2dc8eea59fb6d4aed6845e6905fc2a8afe93175d94a83ba2a01a0"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-macosx_10_12_x86_64.whl", hash = "sha256:8566def80554c3faa0e65ac30ab0932b9e3a5cd7f8323764303d468e5c37595a"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:b80aa5095cd3109962a298ce14110ae16b8c1aece8b72f9dafe81cf597ad80b3"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:3006c3dd9ba34b0c094c544c6006cc79e87d8612999f1a5d43b769b89181f23c"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:72f6c8b11857a856bcfa48c86f5368439f74453563f951e473514579d44aa612"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:5cb1b2f9742240e4bb26b652a5aeb840aa4b417c7748b6f8387927bc6e45e40d"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:bd3d54f38609ff308209bd43acea66061494157703364ae40c951f83ba99a1a9"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:2ff4321e56e879ee8d2a879501c8e469414d948f4aba74a2d4593184eb326660"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:d0d2568a8c11bf8225044aa94409e21da0cb09dcdafe9ecd10250b2baad531a9"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-musllinux_1_1_aarch64.whl", hash = "sha256:a39455728aabd58ceabb03c90e12f71fd30fa69615760a075b9fec596456ccc3"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-musllinux_1_1_armv7l.whl", hash = "sha256:239edca560d05757817c13dc17c50766136d21f7cd0fac50295499ae24f90fdf"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-musllinux_1_1_x86_64.whl", hash = "sha256:2a5e06546e19f24c6a96a129142a75cee553cc018ffee48a460059b1185f4470"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-win32.whl", hash = "sha256:b4ececa40ac28afa90871c2cc2b9ffd2ff0bf749380fbdf57d165fd23da353aa"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-win_amd64.whl", hash = "sha256:80aa89cad80b32a912a65332f64a4450ed00966111b6615ca6816153d3585a8c"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-win_arm64.whl", hash = "sha256:35b44f37a3199f771c3eaa53051bc8a70cd7b54f333531c59e29fd4db5d15008"},
    {file = "pydantic_core-2.41.5-cp39-cp39-macosx_10_12_x86_64.whl", hash = "sha256:8bfeaf8735be79f225f3fefab7f941c712aaca36f1128c9d7e2352ee1aa87bdf"},
    {file = "pydantic_core-2.41.5-cp39-cp39-macosx_11_0_arm64.whl", hash = "sha256:346285d28e4c8017da95144c7f3acd42740d637ff41946af5ce6e5e420502dd5"},
    {file = "pydantic_core-2.41.5-cp39-cp39-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:a75dafbf87d6276ddc5b2bf6fae5254e3d0876b626eb24969a574fff9149ee5d"},
    {file = "pydantic_core-2.41.5-cp39-cp39-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:7b93a4d08587e2b7e7882de461e82b6ed76d9026ce91ca7915e740ecc7855f60"},
    {file = "pydantic_core-2.41.5-cp39-cp39-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:e8465ab91a4bd96d36dde3263f06caa6a8a6019e4113f24dc753d79a8b3a3f82"},
    {file = "pydantic_core-2.41.5-cp39-cp39-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:299e0a22e7ae2b85c1a57f104538b2656e8ab1873511fd718a1c1c6f149b77b5"},
    {file = "pydantic_core-2.41.5-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:707625ef0983fcfb461acfaf14de2067c5942c6bb0f3b4c99158bed6fedd3cf3"},
    {file = "pydantic_core-2.41.5-cp39-cp39-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:f41eb9797986d6ebac5e8edff36d5cef9de40def462311b3eb3eeded1431e425"},
    {file = "pydantic_core-2.41.5-cp39-cp39-musllinux_1_1_aarch64.whl", hash = "sha256:0384e2e1021894b1ff5a786dbf94771e2986ebe2869533874d7e43bc79c6f504"},
    {file = "pydantic_core-2.41.5-cp39-cp39-musllinux_1_1_armv7l.whl", hash = "sha256:f0cd744688278965817fd0839c4a4116add48d23890d468bc436f78beb28abf5"},
    {file = "pydantic_core-2.41.5-cp39-cp39-musllinux_1_1_x86_64.whl", hash = "sha256:753e230374206729bf0a807954bcc6c150d3743928a73faffee51ac6557a03c3"},
    {file = "pydantic_core-2.41.5-cp39-cp39-win32.whl", hash = "sha256:873e0d5b4fb9b89ef7c2d2a963ea7d02879d9da0da8d9d4933dee8ee86a8b460"},
    {file = "pydantic_core-2.41.5-cp39-cp39-win_amd64.whl", hash = "sha256:e4f4a984405e91527a0d62649ee21138f8e3d0ef103be488c1dc11a80d7f184b"},
    {file = "pydantic_core-2.41.5-graalpy311-graalpy242_311_native-macosx_10_12_x86_64.whl", hash = "sha256:b96d5f26b05d03cc60f11a7761a5ded1741da411e7fe0909e27a5e6a0cb7b034"},
    {file = "pydantic_core-2.41.5-graalpy311-graalpy242_311_native-macosx_11_0_arm64.whl", hash = "sha256:634e8609e89ceecea15e2d61bc9ac3718caaaa71963717bf3c8f38bfde64242c"},
    {file = "pydantic_core-2.41.5-graalpy311-graalpy242_311_native-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:93e8740d7503eb008aa2df04d3b9735f845d43ae845e6dcd2be0b55a2da43cd2"},
    {file = "pydantic_core-2.41.5-graalpy311-graalpy242_311_native-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:f15489ba13d61f670dcc96772e733aad1a6f9c429cc27574c6cdaed82d0146ad"},
    {file = "pydantic_core-2.41.5-graalpy312-graalpy250_312_native-macosx_10_12_x86_64.whl", hash = "sha256:7da7087d756b19037bc2c06edc6c170eeef3c3bafcb8f532ff17d64dc427adfd"},
    {file = "pydantic_core-2.41.5-graalpy312-graalpy250_312_native-macosx_11_0_arm64.whl", hash = "sha256:aabf5777b5c8ca26f7824cb4a120a740c9588ed58df9b2d196ce92fba42ff8dc"},
    {file = "pydantic_core-2.41.5-graalpy312-graalpy250_312_native-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:c007fe8a43d43b3969e8469004e9845944f1a80e6acd47c150856bb87f230c56"},
    {file = "pydantic_core-2.41.5-graalpy312-graalpy250_312_native-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:76d0819de158cd855d1cbb8fcafdf6f5cf1eb8e470abe056d5d161106e38062b"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-macosx_10_12_x86_64.whl", hash = "sha256:b5819cd790dbf0c5eb9f82c73c16b39a65dd6dd4d1439dcdea7816ec9adddab8"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-macosx_11_0_arm64.whl", hash = "sha256:5a4e67afbc95fa5c34cf27d9089bca7fcab4e51e57278d710320a70b956d1b9a"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:ece5c59f0ce7d001e017643d8d24da587ea1f74f6993467d85ae8a5ef9d4f42b"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:16f80f7abe3351f8ea6858914ddc8c77e02578544a0ebc15b4c2e1a0e813b0b2"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-musllinux_1_1_aarch64.whl", hash = "sha256:33cb885e759a705b426baada1fe68cbb0a2e68e34c5d0d0289a364cf01709093"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-musllinux_1_1_armv7l.whl", hash = "sha256:c8d8b4eb992936023be7dee581270af5c6e0697a8559895f527f5b7105ecd36a"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-musllinux_1_1_x86_64.whl", hash = "sha256:242a206cd0318f95cd21bdacff3fcc3aab23e79bba5cac3db5a841c9ef9c6963"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-win_amd64.whl", hash = "sha256:d3a978c4f57a597908b7e697229d996d77a6d3c94901e9edee593adada95ce1a"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-macosx_10_12_x86_64.whl", hash = "sha256:b2379fa7ed44ddecb5bfe4e48577d752db9fc10be00a6b7446e9663ba143de26"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-macosx_11_0_arm64.whl", hash = "sha256:266fb4cbf5e3cbd0b53669a6d1b039c45e3ce651fd5442eff4d07c2cc8d66808"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:58133647260ea01e4d0500089a8c4f07bd7aa6ce109682b1426394988d8aaacc"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:287dad91cfb551c363dc62899a80e9e14da1f0e2b6ebde82c806612ca2a13ef1"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-musllinux_1_1_aarch64.whl", hash = "sha256:03b77d184b9eb40240ae9fd676ca364ce1085f203e1b1256f8ab9984dca80a84"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-musllinux_1_1_armv7l.whl", hash = "sha256:a668ce24de96165bb239160b3d854943128f4334822900534f2fe947930e5770"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-musllinux_1_1_x86_64.whl", hash = "sha256:f14f8f046c14563f8eb3f45f499cc658ab8d10072961e07225e507adb700e93f"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-win_amd64.whl", hash = "sha256:56121965f7a4dc965bff783d70b907ddf3d57f6eba29b6d2e5dabfaf07799c51"},
    {file = "pydantic_core-2.41.5.tar.gz", hash = "sha256:08daa51ea16ad373ffd5e7606252cc32f07bc72b28284b6bc9c6df804816476e"},
]

[package.dependencies]
typing-extensions = ">=4.14.1"

[[package]]
name = "pytest"
version = "7.4.4"
description = "pytest: simple powerful testing with Python"
optional = false
python-versions = ">=3.7"
groups = ["dev"]
files = [
    {file = "pytest-7.4.4-py3-none-any.whl", hash = "sha256:b090cdf5ed60bf4c45261be03239c2c1c22df034fbffe691abe93cd80cea01d8"},
    {file = "pytest-7.4.4.tar.gz", hash = "sha256:2cf0005922c6ace4a3e2ec8b4080eb0d9753fdc93107415332f50ce9e7994280"},
]

[package.dependencies]
colorama = {version = "*", markers = "sys_platform == \"win32\""}
iniconfig = "*"
packaging = "*"
pluggy = ">=0.12,<2.0"

[package.extras]
testing = ["argcomplete", "attrs (>=19.2.0)", "hypothesis (>=3.56)", "mock", "nose", "pygments (>=2.7.2)", "requests", "setuptools", "xmlschema"]

[[package]]
name = "pytest-asyncio"
version = "0.21.2"
description = "Pytest support for asyncio"
optional = false
python-versions = ">=3.7"
groups = ["dev"]
files = [
    {file = "pytest_asyncio-0.21.2-py3-none-any.whl", hash = "sha256:ab664c88bb7998f711d8039cacd4884da6430886ae8bbd4eded552ed2004f16b"},
    {file = "pytest_asyncio-0.21.2.tar.gz", hash = "sha256:d67738fc232b94b326b9d060750beb16e0074210b98dd8b58a5239fa2a154f45"},
]

[package.dependencies]
pytest = ">=7.0.0"

[package.extras]
docs = ["sphinx (>=5.3)", "sphinx-rtd-theme (>=1.0)"]
testing = ["coverage (>=6.2)", "flaky (>=3.5.0)", "hypothesis (>=5.7.1)", "mypy (>=0.931)", "pytest-trio (>=0.7.0)"]

[[package]]
name = "pytest-mock"
version = "3.15.1"
description = "Thin-wrapper around the mock package for easier use with pytest"
optional = false
python-versions = ">=3.9"
groups = ["dev"]
files = [
    {file = "pytest_mock-3.15.1-py3-none-any.whl", hash = "sha256:0a25e2eb88fe5168d535041d09a4529a188176ae608a6d249ee65abc0949630d"},
    {file = "pytest_mock-3.15.1.tar.gz", hash = "sha256:1849a238f6f396da19762269de72cb1814ab44416fa73a8686deac10b0d87a0f"},
]

[package.dependencies]
pytest = ">=6.2.5"

[package.extras]
dev = ["pre-commit", "pytest-asyncio", "tox"]

[[package]]
name = "sniffio"
version = "1.3.1"
description = "Sniff out which async library your code is running under"
optional = false
python-versions = ">=3.7"
groups = ["main"]
files = [
    {file = "sniffio-1.3.1-py3-none-any.whl", hash = "sha256:2f6da418d1f1e0fddd844478f41680e794e6051915791a034ff65e5f100525a2"},
    {file = "sniffio-1.3.1.tar.gz", hash = "sha256:f4324edc670a0f49750a81b895f35c3adb843cca46f0530f79fc1babb23789dc"},
]

[[package]]
name = "typing-extensions"
version = "4.15.0"
description = "Backported and Experimental Type Hints for Python 3.9+"
optional = false
python-versions = ">=3.9"
groups = ["main"]
files = [
    {file = "typing_extensions-4.15.0-py3-none-any.whl", hash = "sha256:f0fa19c6845758ab08074a0cfa8b7aecb71c999ca73d62883bc25cc018c4e548"},
    {file = "typing_extensions-4.15.0.tar.gz", hash = "sha256:0cea48d173cc12fa28ecabc3b837ea3cf6f38c6d1136f85cbaaf598984861466"},
]

[[package]]
name = "typing-inspection"
version = "0.4.2"
description = "Runtime typing introspection tools"
optional = false
python-versions = ">=3.9"
groups = ["main"]
files = [
    {file = "typing_inspection-0.4.2-py3-none-any.whl", hash = "sha256:4ed1cacbdc298c220f1bd249ed5287caa16f34d44ef4e9c3d0cbad5b521545e7"},
    {file = "typing_inspection-0.4.2.tar.gz", hash = "sha256:ba561c48a67c5958007083d386c3295464928b01faa735ab8547c5692e87f464"},
]

[package.dependencies]
typing-extensions = ">=4.12.0"

[metadata]
lock-version = "2.1"
python-versions = "^3.11"
content-hash = "7625bff269edfa5d64c1de8d0b5eb2deab8b59559ca77c91e18a03c75406687c"

```

## File: /home/user/AA1/gateways/ai_gateway/pyproject.toml

```
[tool.poetry]
name = "ai-gateway"
version = "0.1.0"
description = ""
authors = ["InstaPact <oss@instapact.com>"]
readme = "README.md"
packages = [{include = "ai_gateway", from = "."}]


[tool.poetry.dependencies]
python = "^3.11"
pydantic = "^2.5.3"
httpx = "^0.26.0"
backoff = "^2.2.1"


[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.1"
pytest-mock = "^3.12.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

```

## File: /home/user/AA1/gateways/ai_gateway/.pytest_cache/CACHEDIR.TAG

```
Signature: 8a477f597d28d172789f06886806bc55
# This file is a cache directory tag created by pytest.
# For information about cache directory tags, see:
#	https://bford.info/cachedir/spec.html

```

## File: /home/user/AA1/gateways/ai_gateway/.pytest_cache/.gitignore

```
# Created by pytest automatically.
*

```

## File: /home/user/AA1/gateways/ai_gateway/.pytest_cache/README.md

```
# pytest cache directory #

This directory contains data from the pytest's cache plugin,
which provides the `--lf` and `--ff` options, as well as the `cache` fixture.

**Do not** commit this to version control.

See [the docs](https://docs.pytest.org/en/stable/how-to/cache.html) for more information.

```

## File: /home/user/AA1/gateways/ai_gateway/.pytest_cache/v/cache/lastfailed

```
{}
```

## File: /home/user/AA1/gateways/ai_gateway/.pytest_cache/v/cache/nodeids

```
[
  "tests/providers/test_gemini.py::test_call_gemini_auth_error",
  "tests/providers/test_gemini.py::test_call_gemini_client_error",
  "tests/providers/test_gemini.py::test_call_gemini_empty_response_content",
  "tests/providers/test_gemini.py::test_call_gemini_invalid_json_response",
  "tests/providers/test_gemini.py::test_call_gemini_network_error",
  "tests/providers/test_gemini.py::test_call_gemini_rate_limit_error",
  "tests/providers/test_gemini.py::test_call_gemini_success",
  "tests/providers/test_gemini.py::test_call_gemini_timeout_error",
  "tests/providers/test_gemini.py::test_call_gemini_upstream_error",
  "tests/providers/test_gemini.py::test_safe_err_with_empty_response",
  "tests/providers/test_gemini.py::test_safe_err_with_error_json",
  "tests/providers/test_gemini.py::test_safe_err_with_invalid_json",
  "tests/providers/test_gemini.py::test_safe_err_with_other_json",
  "tests/test_client.py::test_client_calls_gemini_provider_correctly",
  "tests/test_client.py::test_client_calls_offline_provider_correctly",
  "tests/test_client.py::test_client_does_not_modify_output",
  "tests/test_client.py::test_client_does_not_modify_prompt",
  "tests/test_client.py::test_client_handles_call_options_override",
  "tests/test_client.py::test_client_initializes_with_provided_config",
  "tests/test_client.py::test_client_loads_config_if_not_provided",
  "tests/test_client.py::test_client_logs_failure_on_exception",
  "tests/test_client.py::test_client_logs_prompt_hash_not_prompt_text",
  "tests/test_client.py::test_client_raises_gateway_config_error_for_missing_gemini_key",
  "tests/test_client.py::test_client_raises_gateway_config_error_for_unknown_provider",
  "tests/test_client.py::test_client_raises_value_error_for_empty_prompt",
  "tests/test_retry.py::test_run_with_retry_exceeds_max_retries",
  "tests/test_retry.py::test_run_with_retry_multiple_retryable_errors",
  "tests/test_retry.py::test_run_with_retry_non_retryable_error",
  "tests/test_retry.py::test_run_with_retry_other_exception_raised_immediately",
  "tests/test_retry.py::test_run_with_retry_success_after_retries",
  "tests/test_retry.py::test_run_with_retry_success_first_attempt",
  "tests/test_retry.py::test_sleep_s_calculation"
]
```

## File: /home/user/AA1/gateways/ai_gateway/.pytest_cache/v/cache/stepwise

```
[]
```

## File: /home/user/AA1/gateways/ai_gateway/README.md

```

```

## File: /home/user/AA1/gateways/ai_gateway/SERVICE_CONTRACT.md

```
# SERVICE_CONTRACT.md  
## AI Gateway â€” LLM Transport & Stability Layer

---

## 1. Purpose

The **AI Gateway** is an infrastructure service that provides **reliable, secure, and provider-agnostic access to Large Language Models (LLMs)**.

It is **plumbing**, not intelligence.

The service exists to:
- accept a fully-formed prompt
- invoke an LLM supplier
- return the modelâ€™s output **unchanged**
- manage operational, security, and supplier complexity

---

## 2. Explicit Non-Goals (Hard Boundary)

The AI Gateway **MUST NOT**:

- interpret prompts
- interpret outputs
- validate or enforce schemas (e.g. JSON)
- correct or â€œrepairâ€ model responses
- apply workflow logic
- encode domain knowledge
- make decisions
- understand ontology, governance, or semantics
- modify prompts or outputs in any way

All meaning, validation, and governance live **outside** this service.

---

## 3. Input Contract

### Required
- `prompt: str`  
  A fully-formed prompt supplied by the caller.

### Optional (transport-level only)
- `provider` (e.g. gemini, openai, offline)
- `model`
- `timeout_seconds`
- `temperature`
- `max_tokens`

The AI Gateway **does not inspect, parse, or alter** the prompt.

---

## 4. Output Contract

### Success
- Returns **exactly the text produced by the model**, unchanged.

### Failure
- Raises a transport-level error or returns an explicit failure.
- Failures are limited to operational concerns:
  - timeouts
  - authentication errors
  - rate limits
  - supplier availability
  - network failures

The service **never rewrites, truncates, or restructures** model output.

---

## 5. Operational Guarantees

### 5.1 Stability
- Enforced request timeouts
- Bounded retries
- Exponential backoff
- Retries only on transient failures:
  - timeouts
  - HTTP 429
  - HTTP 5xx

### 5.2 Determinism
- Low default temperature unless overridden
- No hidden prompt augmentation
- No stateful behavior across calls

---

## 6. Security Guarantees

- API keys loaded only from environment variables
- No prompt logging by default
- No output logging by default
- No secrets written to disk or stdout
- Debug logging must be explicitly enabled and opt-in

---

## 7. Logging & Observability (Operational Only)

The service MAY log:
- timestamp
- provider
- model
- latency
- retry count
- success / failure
- **prompt hash (never prompt text)**

The service MUST NOT log:
- prompt contents
- model outputs
- domain or customer data

---

## 8. Provider & Model Abstraction

The AI Gateway:
- abstracts supplier-specific APIs
- isolates model naming and version churn
- normalizes transport-level errors

Callers must not rely on supplier-specific behavior.

---

## 9. Change Control Rule (Non-Negotiable)

Any change that introduces:
- semantic interpretation
- output validation
- schema enforcement
- task logic
- workflow behavior
- domain awareness

**violates this contract and must be rejected.**

---

## 10. Design Principle (Canonical)

> **This service is dumb on purpose.**  
> **Intelligence lives in the prompt and the caller.**

---

## 11. Intended Longevity

This contract is designed to remain valid across:
- LLM provider changes
- model evolution
- prompt strategies
- ontology workflows
- governance processes

If this contract no longer fits, a **new service** must be created.

```

## File: /home/user/AA1/gateways/ai_gateway/tests/providers/__pycache__/test_gemini.cpython-312-pytest-7.4.4.pyc

```
Ë
:çpi“ãóì—ddlZddlmcmZddlZddlmZm	Z	ddl
Z
ddlmZmZddlmZmZmZmZmZdZdZdZdZej0d	„«Zd
„Zd„Zd„Zd„Zd„Zd„Zd„Z d„Z!d„Z"d„Z#d„Z$d„Z%d„Z&y)éN)ÚMockÚpatch)Úcall_geminiÚ	_safe_err)ÚGatewayAuthErrorÚGatewayClientErrorÚGatewayRateLimitErrorÚGatewayTimeoutErrorÚGatewayUpstreamErrorÚtest_api_keyzgemini-test-modelztest promptg$@c#óK—td«5}|j}||j_|–—ddd«y#1swYyxYw­w)Nzhttpx.Client)rÚreturn_valueÚ	__enter__)Úmock_client_classÚmock_clients  úA/home/user/AA1/gateways/ai_gateway/tests/providers/test_gemini.pyÚmock_httpx_clientrsDèø€ä	ˆ~Ó	ğĞ"3Ø'×4Ñ4ˆà-8ˆ×ÑÔ*ØÒ÷	÷ñüs‚A"9°	A¹A¾Acóx—td¬«}dddddœi|j_d|_t	|«}d}||k(}|sötjd	|fd
||f«dtj«vstjt«rtjt«nddtj«vstj|«rtj|«ndtj|«tj|«dœz}dd|iz}ttj|««‚dx}x}}y)Né©Ústatus_codeÚerrorÚINVALID_ARGUMENTzAPI key not valid.)ÚstatusÚcodeÚmessageúraw textz(INVALID_ARGUMENT 400: API key not valid.©ú==©z0%(py3)s
{%(py3)s = %(py0)s(%(py1)s)
} == %(py6)srÚresp©Úpy0Úpy1Úpy3Úpy6úassert %(py8)sÚpy8©rÚjsonrÚtextrÚ
@pytest_arÚ_call_reprcompareÚ@py_builtinsÚlocalsÚ_should_repr_global_nameÚ	_safereprÚAssertionErrorÚ_format_explanation©r!Ú@py_assert2Ú@py_assert5Ú@py_assert4Ú@py_format7Ú@py_format9s      rÚtest_safe_err_with_error_jsonr:s–€Ü˜CÔ €DØ%Ğ2DÈcĞ^rÑ'sĞt€D‡IIÔØ€D„IßH×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×HĞHócóp—td¬«}ddi|j_d|_t	|«}d}||k(}|sötjd|fd||f«d	tj«vstjt«rtjt«nd	d
tj«vstj|«rtj|«nd
tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}}y)NéÈrrÚOKrz{"status": "OK"}rr rr!r"r'r(r)r4s      rÚtest_safe_err_with_other_jsonr?s€Ü˜CÔ €DØ&¨Ğ-€D‡IIÔØ€D„Iß0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0Ğ0r;có~—td¬«}td«|j_d|_t|«}d}||k(}|sötjd|fd||f«dtj«vstjt
«rtjt
«nddtj«vstj|«rtj|«ndtj|«tj|«d	œz}d
d|iz}ttj|««‚dx}x}}y)Nr=rúNot JSONrrr rr!r"r'r(©rÚ
ValueErrorr*Úside_effectr+rr,r-r.r/r0r1r2r3r4s      rÚtest_safe_err_with_invalid_jsonrE#s€Ü˜CÔ €DÜ& zÓ2€D‡IIÔØ€D„Iß(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(Ğ(r;có~—td¬«}td«|j_d|_t|«}d}||k(}|sötjd|fd||f«dtj«vstjt
«rtjt
«nddtj«vstj|«rtj|«ndtj|«tj|«d	œz}d
d|iz}ttj|««‚dx}x}}y)Nr=rrAÚrr rr!r"r'r(rBr4s      rÚ!test_safe_err_with_empty_responserH)s€Ü˜CÔ €DÜ& zÓ2€D‡IIÔØ€D„Iß × × × × × × × × × × × × × × × × × × × × × × × × × × × × × × × × × Ğ r;có2—td¬«}dddddigiigi|j_||j_t	t
ttt¬«}d}||k(}|s™tjd	|fd
||f«dtj«vstj|«rtj|«ndtj|«dœz}dd|iz}ttj |««‚dx}}|jj#«y)Nr=rÚ
candidatesÚcontentÚpartsr+zExpected Output©ÚpromptÚmodelÚapi_keyÚ	timeout_sr©z%(py0)s == %(py3)sÚresult©r#r%úassert %(py5)sÚpy5)rr*rÚpostrÚMOCK_PROMPTÚ
MOCK_MODELÚMOCK_API_KEYÚMOCK_TIMEOUTr,r-r.r/r0r1r2r3Úassert_called_once©rÚ	mock_resprSr5Ú@py_assert1Ú@py_format4Ú@py_format6s       rÚtest_call_gemini_successrb1s¨€Ü Ô%€Ià˜	 G¨vĞ7HĞ.IĞ-JĞ#KĞLĞMğ#€I‡NNÔğ+4Ğ×ÑÔ'ä¤´:Ä|Ô_kÔl€Fß&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&Õ&Ø×Ñ×-Ñ-Õ/r;có—td¬«}dddii|j_||j_t	j
td¬«5ttttt¬«ddd«y#1swYyxYw)	Ni‘rrrzInvalid API KeyzGemini auth error: HTTP 401©ÚmatchrM)rr*rrWÚpytestÚraisesrrrXrYrZr[©rr^s  rÚtest_call_gemini_auth_errorri<sj€Ü Ô%€IØ#*¨YĞ8IĞ,JĞ"K€I‡NNÔØ*3Ğ×ÑÔ'ä	‰Ô'Ğ/LÔ	MñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúóÁ A7Á7Bcó—td¬«}dddii|j_||j_t	j
td¬«5ttttt¬«ddd«y#1swYyxYw)	Ni­rrrzRate limit exceededzGemini rate limitedrdrM)rr*rrWrfrgr	rrXrYrZr[rhs  rÚ!test_call_gemini_rate_limit_errorrlDsj€Ü Ô%€IØ#*¨YĞ8MĞ,NĞ"O€I‡NNÔØ*3Ğ×ÑÔ'ä	‰Ô,Ğ4IÔ	JñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúrjcó—td¬«}dddii|j_||j_t	j
td¬«5ttttt¬«ddd«y#1swYyxYw)	NrrrrzBad RequestzGemini client error HTTP 400rdrM)rr*rrWrfrgrrrXrYrZr[rhs  rÚtest_call_gemini_client_errorrnLsi€Ü Ô%€IØ#*¨Y¸Ğ,FĞ"G€I‡NNÔØ*3Ğ×ÑÔ'ä	‰Ô)Ğ1OÔ	PñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúrjcó—td¬«}dddii|j_||j_t	j
td¬«5ttttt¬«ddd«y#1swYyxYw)	NiôrrrzInternal Server ErrorzGemini upstream error HTTP 500rdrM)rr*rrWrfrgrrrXrYrZr[rhs  rÚtest_call_gemini_upstream_errorrpTsj€Ü Ô%€IØ#*¨YĞ8OĞ,PĞ"Q€I‡NNÔØ*3Ğ×ÑÔ'ä	‰Ô+Ğ3SÔ	TñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúrjcóê—tjd«|j_t	j
td¬«5ttttt¬«ddd«y#1swYyxYw)NÚTimeoutzGemini timeoutrdrM)ÚhttpxÚReadTimeoutrWrDrfrgr
rrXrYrZr[©rs rÚtest_call_gemini_timeout_errorrv\sT€Ü).×):Ñ):¸9Ó)EĞ×ÑÔ&ä	‰Ô*Ğ2BÔ	CñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúsÁ A)Á)A2có—tjdtjdd«¬«|j_tjtd¬«5ttttt¬«ddd«y#1swYyxYw)NzNetwork errorÚGETzhttp://test.com)ÚrequestzGemini request errorrdrM)rsÚRequestErrorÚRequestrWrDrfrgrrrXrYrZr[rus rÚtest_call_gemini_network_errorr|bsf€Ü).×);Ñ);¸OÔUZ×UbÑUbĞchĞj{ÓU|Ô)}Ğ×ÑÔ&ä	‰Ô+Ğ3IÔ	JñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúsÁ A?Á?Bcó—td¬«}td«|j_||j_tjtd¬«5ttttt¬«ddd«y#1swYyxYw)Nr=rrAz!Gemini returned non-JSON responserdrM)rrCr*rDrWrrfrgrrrXrYrZr[rhs  rÚ&test_call_gemini_invalid_json_responser~hsd€Ü Ô%€IÜ!+¨JÓ!7€I‡NNÔØ*3Ğ×ÑÔ'ä	‰Ô+Ğ3VÔ	WñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúsÁ A<Á<Bcó—td¬«}dddddigiiddigiidiiigi|j_||j_t	t
ttt¬«}d}||k(}|s™tjd	|fd
||f«dtj«vstj|«rtj|«ndtj|«dœz}dd|iz}ttj |««‚dx}}y)Nr=rrJrKrLr+rMrGrrRrSrTrUrV)rr*rrWrrXrYrZr[r,r-r.r/r0r1r2r3r]s       rÚ'test_call_gemini_empty_response_contentr€ps±€Ü Ô%€Iğ	Ø˜ F¨D >Ğ"2Ğ3Ğ4Ø˜ 2 $˜Ğ(Ø˜ˆOØğ	
ğ#€I‡NNÔğ+4Ğ×ÑÔ'ä¤´:Ä|Ô_kÔl€Fß×××××××××××××××××××Ör;)'Úbuiltinsr.Ú_pytest.assertion.rewriteÚ	assertionÚrewriter,rfÚunittest.mockrrrsÚai_gateway.providers.geminirrÚai_gateway.errorsrrr	r
rrZrYrXr[Úfixturerr:r?rErHrbrirlrnrprvr|r~r€©r;rú<module>rŠs–ğß„ƒß%Ûç>÷EõEğ€Ø €
Ø€Ø€à‡ñóğòIò1ò)ò!ò	0òhòhòhòhòhòhòhór;
```

## File: /home/user/AA1/gateways/ai_gateway/tests/providers/test_gemini.py

```
import pytest
from unittest.mock import Mock, patch
import httpx

from ai_gateway.providers.gemini import call_gemini, _safe_err
from ai_gateway.errors import GatewayAuthError, GatewayClientError, GatewayRateLimitError, GatewayTimeoutError, GatewayUpstreamError

# Mock configuration
MOCK_API_KEY = "test_api_key"
MOCK_MODEL = "gemini-test-model"
MOCK_PROMPT = "test prompt"
MOCK_TIMEOUT = 10.0

@pytest.fixture
def mock_httpx_client():
    with patch("httpx.Client") as mock_client_class:
        mock_client = mock_client_class.return_value
        # Critical line: what the `with` block binds to as `client`
        mock_client.__enter__.return_value = mock_client
        yield mock_client

# --- Test _safe_err function ---
def test_safe_err_with_error_json():
    resp = Mock(status_code=400) # Simple Mock for _safe_err
    resp.json.return_value = {"error": {"status": "INVALID_ARGUMENT", "code": 400, "message": "API key not valid."}}
    resp.text = "raw text"
    assert _safe_err(resp) == "INVALID_ARGUMENT 400: API key not valid."

def test_safe_err_with_other_json():
    resp = Mock(status_code=200) # Simple Mock for _safe_err
    resp.json.return_value = {"status": "OK"}
    resp.text = "raw text"
    assert _safe_err(resp) == '{"status": "OK"}'

def test_safe_err_with_invalid_json():
    resp = Mock(status_code=200) # Simple Mock for _safe_err
    resp.json.side_effect = ValueError("Not JSON")
    resp.text = "raw text"
    assert _safe_err(resp) == "raw text"

def test_safe_err_with_empty_response():
    resp = Mock(status_code=200) # Simple Mock for _safe_err
    resp.json.side_effect = ValueError("Not JSON")
    resp.text = None
    assert _safe_err(resp) == ""

# --- Test call_gemini function ---

def test_call_gemini_success(mock_httpx_client):
    mock_resp = Mock(status_code=200)
    mock_resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Expected Output"}]}}]
    }
    mock_httpx_client.post.return_value = mock_resp

    result = call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)
    assert result == "Expected Output"
    mock_httpx_client.post.assert_called_once()
    
def test_call_gemini_auth_error(mock_httpx_client):
    mock_resp = Mock(status_code=401)
    mock_resp.json.return_value = {"error": {"message": "Invalid API Key"}}
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayAuthError, match="Gemini auth error: HTTP 401"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_rate_limit_error(mock_httpx_client):
    mock_resp = Mock(status_code=429)
    mock_resp.json.return_value = {"error": {"message": "Rate limit exceeded"}}
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayRateLimitError, match="Gemini rate limited"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_client_error(mock_httpx_client):
    mock_resp = Mock(status_code=400)
    mock_resp.json.return_value = {"error": {"message": "Bad Request"}}
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayClientError, match="Gemini client error HTTP 400"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_upstream_error(mock_httpx_client):
    mock_resp = Mock(status_code=500)
    mock_resp.json.return_value = {"error": {"message": "Internal Server Error"}}
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayUpstreamError, match="Gemini upstream error HTTP 500"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_timeout_error(mock_httpx_client):
    mock_httpx_client.post.side_effect = httpx.ReadTimeout("Timeout")

    with pytest.raises(GatewayTimeoutError, match="Gemini timeout"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_network_error(mock_httpx_client):
    mock_httpx_client.post.side_effect = httpx.RequestError("Network error", request=httpx.Request("GET", "http://test.com"))

    with pytest.raises(GatewayUpstreamError, match="Gemini request error"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_invalid_json_response(mock_httpx_client):
    mock_resp = Mock(status_code=200)
    mock_resp.json.side_effect = ValueError("Not JSON")
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayUpstreamError, match="Gemini returned non-JSON response"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_empty_response_content(mock_httpx_client):
    mock_resp = Mock(status_code=200)
    # Simulate various empty/missing parts in the JSON response
    mock_resp.json.return_value = {
        "candidates": [
            {"content": {"parts": [{"text": None}]}},
            {"content": {"parts": [{}]}},
            {"content": {}},
            {},
        ]
    }
    mock_httpx_client.post.return_value = mock_resp

    result = call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)
    assert result == "" # Should return empty string if content is missing or None
```

## File: /home/user/AA1/gateways/ai_gateway/tests/__pycache__/test_client.cpython-312-pytest-7.4.4.pyc

```
Ë
æpiL!ãó4—ddlZddlmcmZddlZddlmZm	Z	m
Z
ddlZddlmZmZddlmZddlmZmZmZej*d„«Zej*d„«Zej*d¬	«d
„«Zd„Zd„Zd„Zd„Zd„Zd„Zd„Zd„Z d„Z!d„Z"d„Z#d„Z$y)éN)ÚMockÚpatchÚcall)ÚAIGatewayClientÚCallOptions©ÚGatewayConfig)ÚGatewayConfigErrorÚGatewayAuthErrorÚAIGatewayErrorc
ó(—tdddddddd¬«S)	NÚgeminiúgemini-test-modelç$@éçğ?g4@ÚTEST_GEMINI_KEY©ÚproviderÚmodelÚ	timeout_sÚmax_retriesÚbackoff_base_sÚbackoff_max_sÚgemini_api_keyÚopenai_api_keyr©óú7/home/user/AA1/gateways/ai_gateway/tests/test_client.pyÚmock_configr 
s'€äØØ!ØØØØØ(Øô	ğ	rcó—t|¬«S)N©Úcfg)r)r s rÚclientr$s€ä˜{Ô+Ğ+rT)Úautousecóö—|jd«}|jdd¬«}|jdd„¬«}|jdd	¬«}|jd
d¬«}|jd|¬«}||||||dœS)Nzai_gateway.client.log_eventzai_gateway.client.prompt_hash8ÚTESTHASH)Úreturn_valuezai_gateway.retry.run_with_retrycó—|«S)Nr)ÚfnÚpolicys  rú<lambda>z#mock_dependencies.<locals>.<lambda> s
€ÑikÓim€r)Úside_effectzai_gateway.client.call_geminiÚMODEL_OUTPUT_OKzai_gateway.client.call_offlineÚzai_gateway.client.load_config)Ú	log_eventÚprompt_hash8Úrun_with_retryÚcall_geminiÚcall_offlineÚload_config)r)Úmockerr Úlog_event_mockÚprompt_hash8_mockÚrun_with_retry_mockÚcall_gemini_mockÚcall_offline_mockÚload_config_mocks        rÚmock_dependenciesr=sœ€ğ—\‘\Ğ"?Ó@€NØŸ™Ğ%EĞT^˜Ó_ĞØ Ÿ,™,Ğ'HÑVm˜,ÓnĞğ—|‘|Ğ$CĞRc|ÓdĞØŸ™Ğ%EĞTV˜ÓWĞØ—|‘|Ğ$CĞR]|Ó^Ğğ$Ø)Ø-Ø'Ø)Ø'ñğrcóè—d}d}|j|«|dj||djj|djj|djj
¬«y)Nz"Return exactly: This is my prompt.r.r3r5)ÚpromptrÚapi_keyr)rÚassert_called_once_withr(rrr)r$r=Úoriginal_promptÚexpected_outputs    rÚ"test_client_does_not_modify_promptrD3sq€Ø:€OØ'€Oà
‡KKÔ ğmÑ$×<Ñ<ØØ Ñ.×;Ñ;×AÑAØ! -Ñ0×=Ñ=×LÑLØ# MÑ2×?Ñ?×IÑIğ	=õrcór—|jd«}d}||k(}|s™tjd|fd||f«dtj«vstj
|«rtj|«ndtj|«dœz}dd|iz}ttj|««‚dx}}y)	Nz
any promptr.©ú==)z%(py0)s == %(py3)sÚoutput)Úpy0Úpy3zassert %(py5)sÚpy5)	rÚ
@pytest_arÚ_call_reprcompareÚ@py_builtinsÚlocalsÚ_should_repr_global_nameÚ	_safereprÚAssertionErrorÚ_format_explanation)r$r=rHÚ@py_assert2Ú@py_assert1Ú@py_format4Ú@py_format6s       rÚ"test_client_does_not_modify_outputrXAsQ€ğ[‰[˜Ó&€Fß&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&Ö&rcóò—d}|j|«|djddddd¬«|djd	dd|jd¬
«|djD]}|\}}|j}|«}||v}	|	sîtjd|	fd||f«dtj«vstj|«rtj|«nddtj«vstj|«rtj|«ndtj|«tj|«dœz}
dd|
iz}ttj|««‚dx}	x}}Œy)NzSensitive prompt contentr0zai_gateway.call.startrrrr')rrrr1zai_gateway.call.ok)rrÚ
latency_msr1)únot in)zI%(py0)s not in %(py6)s
{%(py6)s = %(py4)s
{%(py4)s = %(py2)s.values
}()
}r?Úkwargs)rIÚpy2Úpy4Úpy6zassert %(py8)sÚpy8)rÚassert_any_callÚANYÚcall_args_listÚvaluesrLrMrNrOrPrQrRrS)r$r=r6r?Ú	call_argsÚargsr\Ú@py_assert3Ú@py_assert5rUÚ@py_format7Ú@py_format9s            rÚ,test_client_logs_prompt_hash_not_prompt_textrkGsô€Ø'€FØ
‡KKÔğkÑ"×2Ñ2ØØØ!ØØğ3ôğkÑ"×2Ñ2ØØØ!Ø—:‘:Øğ3ôğ' {Ñ3×BÑBó-ˆ	Ø ‰ˆˆfç,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,Ö,ñ-rc
ó"—tdddddddd¬«}t|¬«}|j}||u}|sÚtjd|fd	||f«d
tj«vstj|«rtj|«nd
tj|«dtj«vstj|«rtj|«nddœz}dd|iz}ttj|««‚dx}}y)NÚofflineztest-offlineç@rçrr")Úis)z+%(py2)s
{%(py2)s = %(py0)s.cfg
} is %(py4)sr$Úcustom_config)rIr]r^zassert %(py6)sr_)r	rr#rLrMrNrOrPrQrRrS)rqr$rUrgÚ@py_format5ris      rÚ,test_client_initializes_with_provided_configrsfs€Ü!ØØØØØØØØô	€Mô Ô/€Fß&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&Ğ&rc
óL—tdddddddd¬«}||d_t«}|dj«|j}|j
}d}||k(}|sÁtjd|fd||f«d	tj«vstj|«rtj|«nd	tj|«tj|«tj|«d
œz}dd|iz}	ttj|	««‚dx}x}x}}y)NÚdefaultrrrorr5rF)zI%(py4)s
{%(py4)s = %(py2)s
{%(py2)s = %(py0)s.cfg
}.provider
} == %(py7)sr$)rIr]r^Úpy7zassert %(py9)sÚpy9)r	r(rÚassert_called_oncer#rrLrMrNrOrPrQrRrS)
r6r=Útest_configr$rUrgÚ@py_assert6rhÚ@py_format8Ú@py_format10s
          rÚ(test_client_loads_config_if_not_providedr}ts¥€äØ )°sÈØ¨#¸dĞSWô€Kğ5@ĞmÑ$Ô1ôÓ€FØmÑ$×7Ñ7Ô9ß+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+Ò+rcóL—|jd«|dj«y)Nútest promptr3)rrx)r$r=s  rÚ+test_client_calls_gemini_provider_correctlyr€s€Ø
‡KKÔØmÑ$×7Ñ7Õ9rcóÀ—tdii|j¥ddi¥¤}t|¬«}|jd«|dj	«|dj«y)Nrrmr"rr4r3r)r	Ú__dict__rrrxÚassert_not_called)r r=Úoffline_configr$s    rÚ,test_client_calls_offline_provider_correctlyr……sZ€ä"ÑUĞ%T¨×(<Ñ(<Ğ%T¸jÈ)Ñ%TÑU€NÜ Ô0€FØ
‡KKÔØnÑ%×8Ñ8Ô:ØmÑ$×6Ñ6Õ8rcóæ—tdii|j¥ddi¥¤}t|¬«}tdd¬«}|j	d|¬«|d	jdd
d¬«|dj«y)Nrrr"rmrn)rrr)Úoptionsr4r)r?rrr3r)r	r‚rrrrArƒ)r r=Úbase_configr$r‡s     rÚ)test_client_handles_call_options_overrider‰s}€äÑQĞ"P [×%9Ñ%9Ğ"P¸:ÀxÑ"PÑQ€KÜ Ô-€Fä 9¸Ô<€GØ
‡KK w€KÔ/ğnÑ%×=Ñ=ØĞ$7À3ğ>ôğmÑ$×6Ñ6Õ8rcóŠ—tjtd¬«5|jd«ddd«tjtd¬«5|jd«ddd«tjtd¬«5|jd«ddd«y#1swYŒtxYw#1swYŒKxYw#1swYyxYw)Nz!prompt must be a non-empty string©Úmatchr/z   )ÚpytestÚraisesÚ
ValueErrorr)r$s rÚ/test_client_raises_value_error_for_empty_promptrœs–€Ü	‰”zĞ)LÔ	MñØ‰BŒ÷ä	‰”zĞ)LÔ	MñØ‰EÔ÷ä	‰”zĞ)LÔ	MñØ‰DÔ÷ğ÷	ğú÷ğú÷ğús#œB!ÁB-ÂB9Â!B*Â-B6Â9Ccóä—tdii|j¥ddi¥¤}||d_t«}t	j
td¬«5|jd«ddd«y#1swYyxYw)Nrr5zMissing GEMINI_API_KEYr‹rr©r	r‚r(rrrr
r)r6r=r Úmock_config_no_keyr$s     rÚ>test_client_raises_gateway_config_error_for_missing_gemini_keyr”¤sl€ä&ÑZĞ)Y¨K×,@Ñ,@Ğ)YĞBRĞTXÑ)YÑZĞØ4FĞmÑ$Ô1äÓ€Fä	‰Ô)Ğ1IÔ	Jñ#Ø‰MÔ"÷#÷#ñ#úsÁA&Á&A/cóæ—tdii|j¥dddœ¥¤}||d_t«}t	j
td¬«5|jd«ddd«y#1swYyxYw)	NÚunknownÚVALID_KEY_FOR_TEST)rrr5zUnknown provider: unknownr‹rrr’)r6r=r Úmock_config_unknown_providerr$s     rÚ<test_client_raises_gateway_config_error_for_unknown_providerr™®sz€ä#0ñ$ğ4Ø
×
Ñ
ğ4àØ.ò4ñ$Ğ ğ
5QĞmÑ$Ô1äÓ€Fä	‰Ô)Ğ1LÔ	Mñ#Ø‰MÔ"÷#÷#ñ#úsÁA'Á'A0cóğ—td«|d_tjt«5|j	d«ddd«|djddd|jdd	¬
«y#1swYŒ.xYw)Nz	auth failr3rr0zai_gateway.call.failrrr'r)rrrZr1Ú
error_type)rr-rrrÚassert_called_withrb)r$r=r6s   rÚ%test_client_logs_failure_on_exceptionr¼ss€Ü3CÀKÓ3PĞmÑ$Ô0ä	‰Ô'Ó	(ñ#Ø‰MÔ"÷#ğkÑ"×5Ñ5ØØØ!Ø—:‘:ØØ%ğ6õ÷#ğ#ús­A,Á,A5)%ÚbuiltinsrNÚ_pytest.assertion.rewriteÚ	assertionÚrewriterLrÚunittest.mockrrrÚosÚai_gateway.clientrrÚai_gateway.configr	Úai_gateway.errorsr
rrÚfixturer r$r=rDrXrkrsr}r€r…r‰rr”r™rrrrú<module>r¨s¬ğß„ƒß+Ñ+Û	ç:İ+ßRÑRğ‡ñ
óğ
ğ‡ñ,óğ,ğ€‡˜Ôñóğò.ò'ò-ò>'ò,ò:ò9ò9òò#ò#ór
```

## File: /home/user/AA1/gateways/ai_gateway/tests/__pycache__/test_retry.cpython-312-pytest-7.4.4.pyc

```
Ë
eãpilãó˜—ddlZddlmcmZddlZddlmZm	Z	ddl
Z
ddlmZmZmZddlmZmZmZmZmZd„Zd„Zd„Zd„Zd	„Zd
„Zd„Zy)éN)ÚMockÚcall)ÚRetryPolicyÚrun_with_retryÚ_sleep_s)ÚGatewayTimeoutErrorÚGatewayRateLimitErrorÚGatewayUpstreamErrorÚGatewayClientErrorÚGatewayAuthErrorcó¸—td¬«}td¬«}t||«}d}||k(}|s™tjd|fd||f«dtj«vstj|«rtj|«ndtj|«dœz}d	d
|iz}ttj|««‚dx}}|j«y)NÚsuccess©Úreturn_valueé©Úmax_retries©ú==©z%(py0)s == %(py3)sÚresult©Úpy0Úpy3úassert %(py5)sÚpy5)rrrÚ
@pytest_arÚ_call_reprcompareÚ@py_builtinsÚlocalsÚ_should_repr_global_nameÚ	_safereprÚAssertionErrorÚ_format_explanationÚassert_called_once)Úmock_fnÚpolicyrÚ@py_assert2Ú@py_assert1Ú@py_format4Ú@py_format6s       ú6/home/user/AA1/gateways/ai_gateway/tests/test_retry.pyÚ)test_run_with_retry_success_first_attemptr-sm€ä 	Ô*€GÜ QÔ'€FÜ˜G VÓ,€Fß×××××××××××××××××××ÕØ×ÑÕ ócóä—ttd«td«dg¬«}tdd¬«}|j	d«t||«}d}||k(}|s™tjd	|fd
||f«dtj«vstj|«rtj|«ndtj|«dœz}dd|iz}ttj|««‚dx}}|j}d}||k(}	|	s­tjd	|	fd||f«dtj«vstj|«rtj|«ndtj|«tj|«dœz}dd|iz}
ttj|
««‚dx}x}	}tj }|j"}	|	s•ddtj«vstjt«rtjt«ndtj|«tj|	«dœz}ttj|««‚dx}}	y)NÚtimeoutÚupstreamr©Úside_effectrç{®Gáz„?©rÚbackoff_base_sú
time.sleeprrrrrr©z2%(py2)s
{%(py2)s = %(py0)s.call_count
} == %(py5)sr&©rÚpy2rúassert %(py7)sÚpy7zEassert %(py4)s
{%(py4)s = %(py2)s
{%(py2)s = %(py0)s.sleep
}.called
}Útime)rr:Úpy4)rrr
rÚpatchrrrrr r!r"r#r$Ú
call_countr=ÚsleepÚcalled)Úmockerr&r'rr(r)r*r+Ú@py_assert4Ú@py_assert3Ú@py_format8Ú@py_format5s            r,Ú)test_run_with_retry_success_after_retriesrHs€äÔ 3°IÓ >Ô@TĞU_Ó@`ĞbkĞlÔm€GÜ Q°tÔ<€FØ
‡LLÔä˜G VÓ,€Fß×××××××××××××××××××Õß"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"ß××××××××××××××××××××××r.cón—ttd«¬«}tdd¬«}|jd«t	j
t«5t||«ddd«|j}d}||k(}|s­tjd|fd	||f«d
tj«vstj|«rtj|«nd
tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}}y#1swYŒÒxYw)Nr0r2ér4r5r7rrr8r&r9r;r<)rrrr?ÚpytestÚraisesrr@rrrr r!r"r#r$)rCr&r'r)rDrEr+rFs        r,Ú'test_run_with_retry_exceeds_max_retriesrMs¤€äÔ2°9Ó=Ô>€GÜ Q°tÔ<€FØ
‡LLÔä	‰Ô*Ó	+ñ(Üw Ô'÷(ç"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"Ğ"÷(ğ(úsÁD+Ä+D4cóÚ—ttd«¬«}td¬«}tjt«5t||«ddd«|j«y#1swYŒxYw)Nzbad requestr2rr)rrrrKrLrr%©r&r's  r,Ú'test_run_with_retry_non_retryable_errorrP%sT€äÔ1°-Ó@ÔA€GÜ QÔ'€Fä	‰Ô)Ó	*ñ(Üw Ô'÷(à×ÑÕ ÷(ğ(úó»A!Á!A*cóÚ—ttd«¬«}td¬«}tjt«5t||«ddd«|j«y#1swYŒxYw)NÚ
unexpectedr2rr)rÚ
ValueErrorrrKrLrr%rOs  r,Ú6test_run_with_retry_other_exception_raised_immediatelyrU.sR€äœz¨,Ó7Ô8€GÜ QÔ'€Fä	‰”zÓ	"ñ(Üw Ô'÷(à×ÑÕ ÷(ğ(úrQcóv—ttd«td«dg¬«}tdd¬«}|j	d«t||«}d}||k(}|s™tjd	|fd
||f«dtj«vstj|«rtj|«ndtj|«dœz}dd|iz}ttj|««‚dx}}|j}d}||k(}	|	s­tjd	|	fd||f«dtj«vstj|«rtj|«ndtj|«tj|«dœz}dd|iz}
ttj|
««‚dx}x}	}y)Nzrate limitedr0zfinally successr2rJr4r5r7rrrrrrrr8r&r9r;r<)rr	rrr?rrrrr r!r"r#r$r@)rCr&r'rr(r)r*r+rDrErFs           r,Ú-test_run_with_retry_multiple_retryable_errorsrW7sÒ€äÔ 5°nÓ EÔGZĞ[dÓGeĞgxĞyÔz€GÜ Q°tÔ<€FØ
‡LLÔä˜G VÓ,€Fß&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&Õ&ß"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"Ğ"r.cóè—tdd¬«}|jdd¬«d}t||«}d}||k(}|s
tjd|fd||f«d	tj«vstjt«rtjt«nd	d
tj«vstj|«rtj|«nd
tj|«tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}x}}d}t||«}d}||k(}|s
tjd|fd||f«d	tj«vstjt«rtjt«nd	d
tj«vstj|«rtj|«nd
tj|«tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}x}}d}t||«}d}||k(}|s
tjd|fd||f«d	tj«vstjt«rtjt«nd	d
tj«vstj|«rtj|«nd
tj|«tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}x}}d}t||«}d}||k(}|s
tjd|fd||f«d	tj«vstjt«rtjt«nd	d
tj«vstj|«rtj|«nd
tj|«tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}x}}d}t||«}d}||k(}|s
tjd|fd||f«d	tj«vstjt«rtjt«nd	d
tj«vstj|«rtj|«nd
tj|«tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}x}}y)Ngğ?g$@)r6Úbackoff_max_szrandom.uniformrrr)z9%(py5)s
{%(py5)s = %(py0)s(%(py1)s, %(py3)s)
} == %(py8)srr')rÚpy1rrÚpy8zassert %(py10)sÚpy10ég@rJg@rg @é)rr?rrrrr r!r"r#r$)rCr'r(rDÚ@py_assert7Ú@py_assert6Ú@py_format9Ú@py_format11s        r,Útest_sleep_s_calculationrcAsc€ä¨¸4Ô@€FØ
‡LLĞ!°€LÔ2÷&×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%Ñ%÷&×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%Ñ%÷&×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%Ñ%÷&×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%Ñ%÷'×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&Ò&r.)ÚbuiltinsrÚ_pytest.assertion.rewriteÚ	assertionÚrewriterrKÚunittest.mockrrr=Úai_gateway.retryrrrÚai_gateway.errorsrr	r
rrr-rHrMrPrUrWrc©r.r,ú<module>rlsGğß„ƒß$ÛçBÑB÷EõEò!ò	ò#ò!ò!ò#ó'r.
```

## File: /home/user/AA1/gateways/ai_gateway/tests/test_client.py

```
import pytest
from unittest.mock import Mock, patch, call
import os

from ai_gateway.client import AIGatewayClient, CallOptions
from ai_gateway.config import GatewayConfig
from ai_gateway.errors import GatewayConfigError, GatewayAuthError, AIGatewayError

# Fixtures for common objects
@pytest.fixture
def mock_config():
    return GatewayConfig(
        provider="gemini",
        model="gemini-test-model",
        timeout_s=10.0,
        max_retries=1,
        backoff_base_s=1.0,
        backoff_max_s=20.0,
        gemini_api_key="TEST_GEMINI_KEY",
        openai_api_key=None,
    )

@pytest.fixture
def client(mock_config):
    return AIGatewayClient(cfg=mock_config)

@pytest.fixture(autouse=True)
def mock_dependencies(mocker, mock_config): # Added mock_config here
    # Patch modules as they are imported within client.py
    log_event_mock = mocker.patch('ai_gateway.client.log_event')
    prompt_hash8_mock = mocker.patch('ai_gateway.client.prompt_hash8', return_value="TESTHASH")
    run_with_retry_mock = mocker.patch('ai_gateway.retry.run_with_retry', side_effect=lambda fn, policy: fn()) # Execute fn immediately

    # Patch modules as they are imported within client.py
    call_gemini_mock = mocker.patch('ai_gateway.client.call_gemini', return_value="MODEL_OUTPUT_OK")
    call_offline_mock = mocker.patch('ai_gateway.client.call_offline', return_value="")
    load_config_mock = mocker.patch('ai_gateway.client.load_config', return_value=mock_config) # Patch where client.py looks for it

    # Return a dict of mocks for easier access in tests
    return {
        "log_event": log_event_mock,
        "prompt_hash8": prompt_hash8_mock,
        "run_with_retry": run_with_retry_mock,
        "call_gemini": call_gemini_mock,
        "call_offline": call_offline_mock,
        "load_config": load_config_mock,
    }

# --- Tests for Data Integrity and Privacy ---

def test_client_does_not_modify_prompt(client, mock_dependencies):
    original_prompt = "Return exactly: This is my prompt."
    expected_output = "MODEL_OUTPUT_OK"
    
    client.call(original_prompt)
    
    # Verify that call_gemini received the original prompt
    mock_dependencies["call_gemini"].assert_called_once_with(
        prompt=original_prompt,
        model=mock_dependencies["load_config"].return_value.model, # Get model from mocked config
        api_key=mock_dependencies["load_config"].return_value.gemini_api_key, # Get API key from mocked config
        timeout_s=mock_dependencies["load_config"].return_value.timeout_s, # Get timeout from mocked config
    )

def test_client_does_not_modify_output(client, mock_dependencies):
    # The mock for call_gemini already ensures a fixed output.
    # The test here is to ensure AIGatewayClient returns it as-is.
    output = client.call("any prompt")
    assert output == "MODEL_OUTPUT_OK"
    
def test_client_logs_prompt_hash_not_prompt_text(client, mock_dependencies, mocker):
    prompt = "Sensitive prompt content"
    client.call(prompt)
    
    # Check log_event calls for 'prompt_hash8'
    mock_dependencies["log_event"].assert_any_call(
        "ai_gateway.call.start",
        provider="gemini",
        model="gemini-test-model",
        timeout_s=10.0,
        prompt_hash8="TESTHASH",
    )
    mock_dependencies["log_event"].assert_any_call(
        "ai_gateway.call.ok",
        provider="gemini",
        model="gemini-test-model",
        latency_ms=mocker.ANY, # Use mocker.ANY for dynamic values
        prompt_hash8="TESTHASH",
    )
    # Ensure no calls directly include the original prompt text
    for call_args in mock_dependencies["log_event"].call_args_list:
        args, kwargs = call_args
        # Check kwargs first, then args if needed, but for named args, kwargs is sufficient
        assert prompt not in kwargs.values()
        # For positional args if any might contain prompt
        # for arg in args:
        #     assert prompt not in str(arg)


# --- Tests for core client behavior ---

def test_client_initializes_with_provided_config():
    custom_config = GatewayConfig(
        provider="offline",
        model="test-offline",
        timeout_s=5.0,
        max_retries=0,
        backoff_base_s=0.0,
        backoff_max_s=0.0,
        gemini_api_key=None,
        openai_api_key=None,
    )
    client = AIGatewayClient(cfg=custom_config)
    assert client.cfg is custom_config

def test_client_loads_config_if_not_provided(mocker, mock_dependencies):
    # Ensure load_config is mocked out and returns a known config
    test_config = GatewayConfig(
        provider="default", model="default", timeout_s=1.0, max_retries=0,
        backoff_base_s=0.0, backoff_max_s=0.0, gemini_api_key=None, openai_api_key=None
    )
    mock_dependencies["load_config"].return_value = test_config # Set return value for the mock
    
    # Create client without passing config, so it calls load_config
    client = AIGatewayClient() 
    mock_dependencies["load_config"].assert_called_once()
    assert client.cfg.provider == "default"

def test_client_calls_gemini_provider_correctly(client, mock_dependencies):
    client.call("test prompt")
    mock_dependencies["call_gemini"].assert_called_once()

def test_client_calls_offline_provider_correctly(mock_config, mock_dependencies):
    # Create a new client with a config that explicitly sets the provider to offline
    offline_config = GatewayConfig(**{**mock_config.__dict__, "provider": "offline"})
    client = AIGatewayClient(cfg=offline_config)
    client.call("test prompt")
    mock_dependencies["call_offline"].assert_called_once()
    mock_dependencies["call_gemini"].assert_not_called()

def test_client_handles_call_options_override(mock_config, mock_dependencies):
    # Ensure base config is gemini so we can override it
    base_config = GatewayConfig(**{**mock_config.__dict__, "provider": "gemini"})
    client = AIGatewayClient(cfg=base_config)
    
    options = CallOptions(provider="offline", timeout_s=5.0)
    client.call("test prompt", options=options)
    
    # Ensure offline was called with overridden timeout
    mock_dependencies["call_offline"].assert_called_once_with(
        prompt="test prompt", model="gemini-test-model", timeout_s=5.0 # Model from config, not overridden
    )
    mock_dependencies["call_gemini"].assert_not_called()


def test_client_raises_value_error_for_empty_prompt(client):
    with pytest.raises(ValueError, match="prompt must be a non-empty string"):
        client.call("")
    with pytest.raises(ValueError, match="prompt must be a non-empty string"):
        client.call("   ")
    with pytest.raises(ValueError, match="prompt must be a non-empty string"):
        client.call(None) # type: ignore

def test_client_raises_gateway_config_error_for_missing_gemini_key(mocker, mock_dependencies, mock_config):
    # Create a new config with missing API key
    mock_config_no_key = GatewayConfig(**{**mock_config.__dict__, "gemini_api_key": None})
    mock_dependencies["load_config"].return_value = mock_config_no_key # Ensure this is the config loaded
    
    client = AIGatewayClient() # Client will load the mocked config
    
    with pytest.raises(GatewayConfigError, match="Missing GEMINI_API_KEY"):
        client.call("test prompt")

def test_client_raises_gateway_config_error_for_unknown_provider(mocker, mock_dependencies, mock_config):
    # Create a new config with an unknown provider and a valid gemini key to reach the "unknown provider" check
    mock_config_unknown_provider = GatewayConfig(**{
        **mock_config.__dict__,
        "provider": "unknown",
        "gemini_api_key": "VALID_KEY_FOR_TEST" # Ensure API key is present so it doesn't fail on missing key first
    })
    mock_dependencies["load_config"].return_value = mock_config_unknown_provider # Ensure this is the config loaded
    
    client = AIGatewayClient() # Client will load the mocked config
    
    with pytest.raises(GatewayConfigError, match="Unknown provider: unknown"):
        client.call("test prompt")

def test_client_logs_failure_on_exception(client, mock_dependencies, mocker):
    mock_dependencies["call_gemini"].side_effect = GatewayAuthError("auth fail")
    
    with pytest.raises(GatewayAuthError):
        client.call("test prompt")
    
    mock_dependencies["log_event"].assert_called_with(
        "ai_gateway.call.fail",
        provider="gemini",
        model="gemini-test-model",
        latency_ms=mocker.ANY,
        prompt_hash8="TESTHASH",
        error_type="GatewayAuthError",
    )

```

## File: /home/user/AA1/gateways/ai_gateway/tests/test_retry.py

```
import pytest
from unittest.mock import Mock, call
import time

from ai_gateway.retry import RetryPolicy, run_with_retry, _sleep_s # Import _sleep_s directly
from ai_gateway.errors import GatewayTimeoutError, GatewayRateLimitError, GatewayUpstreamError, GatewayClientError, GatewayAuthError

def test_run_with_retry_success_first_attempt():
    # Test that a successful function call returns immediately
    mock_fn = Mock(return_value="success")
    policy = RetryPolicy(max_retries=3)
    result = run_with_retry(mock_fn, policy)
    assert result == "success"
    mock_fn.assert_called_once()

def test_run_with_retry_success_after_retries(mocker): # Added mocker
    # Test that a function succeeds after a few retries
    mock_fn = Mock(side_effect=[GatewayTimeoutError("timeout"), GatewayUpstreamError("upstream"), "success"])
    policy = RetryPolicy(max_retries=3, backoff_base_s=0.01) # Short backoff for testing
    mocker.patch('time.sleep') # Mock sleep to avoid actual delays
    
    result = run_with_retry(mock_fn, policy)
    assert result == "success"
    assert mock_fn.call_count == 3
    assert time.sleep.called # Ensure sleep was called

def test_run_with_retry_exceeds_max_retries(mocker): # Added mocker
    # Test that a retryable error is re-raised after max_retries
    mock_fn = Mock(side_effect=GatewayTimeoutError("timeout"))
    policy = RetryPolicy(max_retries=2, backoff_base_s=0.01)
    mocker.patch('time.sleep')

    with pytest.raises(GatewayTimeoutError):
        run_with_retry(mock_fn, policy)
    assert mock_fn.call_count == 3 # Initial call + 2 retries

def test_run_with_retry_non_retryable_error():
    # Test that a non-retryable error is raised immediately
    mock_fn = Mock(side_effect=GatewayClientError("bad request"))
    policy = RetryPolicy(max_retries=3)
    
    with pytest.raises(GatewayClientError):
        run_with_retry(mock_fn, policy)
    mock_fn.assert_called_once() # Should not retry

def test_run_with_retry_other_exception_raised_immediately():
    # Test that an unexpected exception is raised immediately
    mock_fn = Mock(side_effect=ValueError("unexpected"))
    policy = RetryPolicy(max_retries=3)
    
    with pytest.raises(ValueError):
        run_with_retry(mock_fn, policy)
    mock_fn.assert_called_once()

def test_run_with_retry_multiple_retryable_errors(mocker): # Added mocker
    # Test with a mix of retryable errors
    mock_fn = Mock(side_effect=[GatewayRateLimitError("rate limited"), GatewayTimeoutError("timeout"), "finally success"])
    policy = RetryPolicy(max_retries=2, backoff_base_s=0.01)
    mocker.patch('time.sleep')
    
    result = run_with_retry(mock_fn, policy)
    assert result == "finally success"
    assert mock_fn.call_count == 3

def test_sleep_s_calculation(mocker): # Added mocker
    # Test that _sleep_s calculates a reasonable backoff (no exact values due to jitter)
    policy = RetryPolicy(backoff_base_s=1.0, backoff_max_s=10.0)
    mocker.patch('random.uniform', return_value=0) # Remove jitter for predictable results

    # Attempt 0: base * 2^0 = 1.0, jitter 0, min(10.0, 1.0) = 1.0
    assert _sleep_s(policy, 0) == 1.0 # Corrected access

    # Attempt 1: base * 2^1 = 2.0, jitter 0, min(10.0, 2.0) = 2.0
    assert _sleep_s(policy, 1) == 2.0 # Corrected access

    # Attempt 2: base * 2^2 = 4.0, jitter 0, min(10.0, 4.0) = 4.0
    assert _sleep_s(policy, 2) == 4.0 # Corrected access

    # Attempt 3: base * 2^3 = 8.0, jitter 0, min(10.0, 8.0) = 8.0
    assert _sleep_s(policy, 3) == 8.0 # Corrected access

    # Attempt 4: base * 2^4 = 16.0, jitter 0, min(10.0, 16.0) = 10.0 (capped by backoff_max_s)
    assert _sleep_s(policy, 4) == 10.0 # Corrected access
```


```

## File: `/home/user/AA1/gateways/ai_gateway/SERVICE_CONTRACT.md`

```
# SERVICE_CONTRACT.md  
## AI Gateway â€” LLM Transport & Stability Layer

---

## 1. Purpose

The **AI Gateway** is an infrastructure service that provides **reliable, secure, and provider-agnostic access to Large Language Models (LLMs)**.

It is **plumbing**, not intelligence.

The service exists to:
- accept a fully-formed prompt
- invoke an LLM supplier
- return the modelâ€™s output **unchanged**
- manage operational, security, and supplier complexity

---

## 2. Explicit Non-Goals (Hard Boundary)

The AI Gateway **MUST NOT**:

- interpret prompts
- interpret outputs
- validate or enforce schemas (e.g. JSON)
- correct or â€œrepairâ€ model responses
- apply workflow logic
- encode domain knowledge
- make decisions
- understand ontology, governance, or semantics
- modify prompts or outputs in any way

All meaning, validation, and governance live **outside** this service.

---

## 3. Input Contract

### Required
- `prompt: str`  
  A fully-formed prompt supplied by the caller.

### Optional (transport-level only)
- `provider` (e.g. gemini, openai, offline)
- `model`
- `timeout_seconds`
- `temperature`
- `max_tokens`

The AI Gateway **does not inspect, parse, or alter** the prompt.

---

## 4. Output Contract

### Success
- Returns **exactly the text produced by the model**, unchanged.

### Failure
- Raises a transport-level error or returns an explicit failure.
- Failures are limited to operational concerns:
  - timeouts
  - authentication errors
  - rate limits
  - supplier availability
  - network failures

The service **never rewrites, truncates, or restructures** model output.

---

## 5. Operational Guarantees

### 5.1 Stability
- Enforced request timeouts
- Bounded retries
- Exponential backoff
- Retries only on transient failures:
  - timeouts
  - HTTP 429
  - HTTP 5xx

### 5.2 Determinism
- Low default temperature unless overridden
- No hidden prompt augmentation
- No stateful behavior across calls

---

## 6. Security Guarantees

- API keys loaded only from environment variables
- No prompt logging by default
- No output logging by default
- No secrets written to disk or stdout
- Debug logging must be explicitly enabled and opt-in

---

## 7. Logging & Observability (Operational Only)

The service MAY log:
- timestamp
- provider
- model
- latency
- retry count
- success / failure
- **prompt hash (never prompt text)**

The service MUST NOT log:
- prompt contents
- model outputs
- domain or customer data

---

## 8. Provider & Model Abstraction

The AI Gateway:
- abstracts supplier-specific APIs
- isolates model naming and version churn
- normalizes transport-level errors

Callers must not rely on supplier-specific behavior.

---

## 9. Change Control Rule (Non-Negotiable)

Any change that introduces:
- semantic interpretation
- output validation
- schema enforcement
- task logic
- workflow behavior
- domain awareness

**violates this contract and must be rejected.**

---

## 10. Design Principle (Canonical)

> **This service is dumb on purpose.**  
> **Intelligence lives in the prompt and the caller.**

---

## 11. Intended Longevity

This contract is designed to remain valid across:
- LLM provider changes
- model evolution
- prompt strategies
- ontology workflows
- governance processes

If this contract no longer fits, a **new service** must be created.

```


```

## File: /home/user/AA1/gateways/ai_gateway/gateways_full_dump.md

```
# Gateways Repository Snapshot

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/client.py

```
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from .config import GatewayConfig, load_config
from .errors import GatewayConfigError
from .logging import log_event, prompt_hash8
from .retry import RetryPolicy, run_with_retry
from .providers.gemini import call_gemini
from .providers.offline import call_offline

# openai provider can be added later without changing this contract.


@dataclass
class CallOptions:
    provider: Optional[str] = None
    model: Optional[str] = None
    timeout_s: Optional[float] = None
    temperature: Optional[float] = None  # accepted but provider may ignore
    max_tokens: Optional[int] = None     # accepted but provider may ignore


class AIGatewayClient:
    """
    AI Gateway public API.
    Contract: accepts prompt, returns raw model text unchanged.
    Handles only transport concerns (security, retries, stability, logging).
    """

    def __init__(self, cfg: Optional[GatewayConfig] = None):
        self.cfg = cfg or load_config()

    def call(self, prompt: str, *, options: Optional[CallOptions] = None) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt must be a non-empty string")

        opt = options or CallOptions()
        provider = (opt.provider or self.cfg.provider).strip().lower()
        model = (opt.model or self.cfg.model).strip()
        timeout_s = float(opt.timeout_s or self.cfg.timeout_s)

        ph = prompt_hash8(prompt)
        t0 = time.time()

        policy = RetryPolicy(
            max_retries=self.cfg.max_retries,
            backoff_base_s=self.cfg.backoff_base_s,
            backoff_max_s=self.cfg.backoff_max_s,
        )

        log_event(
            "ai_gateway.call.start",
            provider=provider,
            model=model,
            timeout_s=timeout_s,
            prompt_hash8=ph,
        )

        def _invoke() -> str:
            if provider == "offline":
                return call_offline(prompt=prompt, model=model, timeout_s=timeout_s)

            if provider == "gemini":
                if not self.cfg.gemini_api_key:
                    raise GatewayConfigError("Missing GEMINI_API_KEY (or AI_GATEWAY_GEMINI_API_KEY).")
                return call_gemini(
                    prompt=prompt,
                    model=model,
                    api_key=self.cfg.gemini_api_key,
                    timeout_s=timeout_s,
                )

            raise GatewayConfigError(f"Unknown provider: {provider}")

        try:
            out = run_with_retry(_invoke, policy)
            ms = int((time.time() - t0) * 1000)
            log_event(
                "ai_gateway.call.ok",
                provider=provider,
                model=model,
                latency_ms=ms,
                prompt_hash8=ph,
            )
            return out
        except Exception as e:
            ms = int((time.time() - t0) * 1000)
            log_event(
                "ai_gateway.call.fail",
                provider=provider,
                model=model,
                latency_ms=ms,
                prompt_hash8=ph,
                error_type=type(e).__name__,
            )
            raise

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/config.py

```
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class GatewayConfig:
    provider: str
    model: str
    timeout_s: float
    max_retries: int
    backoff_base_s: float
    backoff_max_s: float
    # Provider keys (kept here to avoid scattering env reads)
    gemini_api_key: str | None
    openai_api_key: str | None


def _get_float(name: str, default: float) -> float:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    try:
        return float(v)
    except ValueError:
        return default


def _get_int(name: str, default: int) -> int:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    try:
        return int(v)
    except ValueError:
        return default


def load_config() -> GatewayConfig:
    # Stable, boring env var surface
    provider = os.getenv("AI_GATEWAY_PROVIDER", "gemini").strip().lower()
    model = os.getenv("AI_GATEWAY_MODEL", "").strip()

    timeout_s = _get_float("AI_GATEWAY_TIMEOUT_S", 60.0)
    max_retries = _get_int("AI_GATEWAY_RETRIES", 3)
    backoff_base_s = _get_float("AI_GATEWAY_BACKOFF_BASE_S", 1.0)
    backoff_max_s = _get_float("AI_GATEWAY_BACKOFF_MAX_S", 20.0)

    # Provider-specific keys (still env-only)
    gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("AI_GATEWAY_GEMINI_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY") or os.getenv("AI_GATEWAY_OPENAI_API_KEY")

    # Provide sane default model if not set
    if not model:
        if provider == "gemini":
            model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
        elif provider == "openai":
            model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
        elif provider == "offline":
            model = "offline"
        else:
            model = "default"

    return GatewayConfig(
        provider=provider,
        model=model,
        timeout_s=timeout_s,
        max_retries=max_retries,
        backoff_base_s=backoff_base_s,
        backoff_max_s=backoff_max_s,
        gemini_api_key=gemini_api_key,
        openai_api_key=openai_api_key,
    )

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/errors.py

```
# Transport-level errors only. No semantics, no workflow logic.

from __future__ import annotations


class AIGatewayError(RuntimeError):
    """Base class for AI Gateway transport errors."""


class GatewayConfigError(AIGatewayError):
    """Misconfiguration (missing keys, invalid provider/model)."""


class GatewayTimeoutError(AIGatewayError):
    """Request exceeded timeout."""


class GatewayAuthError(AIGatewayError):
    """Authentication/authorization failure."""


class GatewayRateLimitError(AIGatewayError):
    """Supplier rate limited the request (HTTP 429)."""


class GatewayUpstreamError(AIGatewayError):
    """Supplier/service error (5xx or other upstream failure)."""


class GatewayClientError(AIGatewayError):
    """Non-retryable client error (4xx except 429)."""

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/__init__.py

```
from .client import AIGatewayClient, CallOptions
from .errors import (
    AIGatewayError,
    GatewayConfigError,
    GatewayTimeoutError,
    GatewayAuthError,
    GatewayRateLimitError,
    GatewayUpstreamError,
    GatewayClientError,
)

__all__ = [
    "AIGatewayClient",
    "CallOptions",
    "AIGatewayError",
    "GatewayConfigError",
    "GatewayTimeoutError",
    "GatewayAuthError",
    "GatewayRateLimitError",
    "GatewayUpstreamError",
    "GatewayClientError",
]

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/logging.py

```
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def prompt_hash8(prompt: str) -> str:
    return hashlib.sha256((prompt or "").encode("utf-8")).hexdigest()[:8]


def _log_dir() -> Path:
    # Keep logs local to gateway by default, configurable if needed
    base = os.getenv("AI_GATEWAY_LOG_DIR", "")
    if base:
        p = Path(base)
    else:
        p = Path(__file__).resolve().parent / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p


def log_event(event: str, **fields: Any) -> None:
    """
    Operational logging only. Never log prompt or output text.
    Emits JSONL for easy ingestion.
    """
    rec = {"ts": _utc_now(), "event": event, **fields}
    line = json.dumps(rec, ensure_ascii=False)
    print(line, flush=True)

    try:
        (_log_dir() / "ai_gateway.log.jsonl").open("a", encoding="utf-8").write(line + "\n")
    except Exception:
        # Logging must never break the call path
        pass

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/logs/ai_gateway.log.jsonl

```
{"ts": "2026-01-21T13:51:46Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T13:51:46Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 73, "prompt_hash8": "d3e9ca8a", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T13:52:09Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "offline", "timeout_s": 60.0, "prompt_hash8": "3514cf81"}
{"ts": "2026-01-21T13:52:09Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "offline", "latency_ms": 0, "prompt_hash8": "3514cf81"}
{"ts": "2026-01-21T13:53:38Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T13:53:38Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 65, "prompt_hash8": "d3e9ca8a", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:09:52Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T14:09:52Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 658, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T14:10:21Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T14:10:21Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 527, "prompt_hash8": "d3e9ca8a"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 68, "prompt_hash8": "73d07d68", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 51, "prompt_hash8": "5857ac47", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 53, "prompt_hash8": "a936bf73", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 58, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:31:49Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:32:38Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 66, "prompt_hash8": "73d07d68", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 55, "prompt_hash8": "5857ac47", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 51, "prompt_hash8": "a936bf73", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 53, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:32:39Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 56, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:08Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:34:08Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 65, "prompt_hash8": "73d07d68", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:08Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:34:08Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 55, "prompt_hash8": "5857ac47", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 56, "prompt_hash8": "a936bf73", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 50, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-2.5-flash", "timeout_s": 60.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-2.5-flash", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:34:09Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 56, "prompt_hash8": "cb2fea28", "error_type": "GatewayClientError"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "unknown", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.fail", "provider": "unknown", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:38:20Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayAuthError"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "unknown", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.fail", "provider": "unknown", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:41:42Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayAuthError"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:30Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.start", "provider": "unknown", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.fail", "provider": "unknown", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:43:31Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayAuthError"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "73d07d68"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "5857ac47"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "a936bf73"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "offline", "model": "gemini-test-model", "timeout_s": 5.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.ok", "provider": "offline", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "unknown", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.fail", "provider": "unknown", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayConfigError"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.start", "provider": "gemini", "model": "gemini-test-model", "timeout_s": 10.0, "prompt_hash8": "cb2fea28"}
{"ts": "2026-01-21T14:44:18Z", "event": "ai_gateway.call.fail", "provider": "gemini", "model": "gemini-test-model", "latency_ms": 0, "prompt_hash8": "cb2fea28", "error_type": "GatewayAuthError"}

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/providers/gemini.py

```
from __future__ import annotations

import json
import time
import httpx

from ..errors import (
    GatewayAuthError,
    GatewayClientError,
    GatewayRateLimitError,
    GatewayTimeoutError,
    GatewayUpstreamError,
)

# NOTE: This is transport only: prompt -> text.
# No schema enforcement. No output interpretation.


def call_gemini(
    *,
    prompt: str,
    model: str,
    api_key: str,
    timeout_s: float,
) -> str:
    """
    Gemini generateContent (Generative Language API).
    Returns model text unchanged.
    """
    # Endpoint is configurable to survive API churn
    base = "https://generativelanguage.googleapis.com"
    version = "v1"
    endpoint = f"{base}/{version}/models/{model}:generateContent"

    headers = {
        "Content-Type": "application/json",
        # Prefer header auth; keep query-free by default
        "x-goog-api-key": api_key,
    }

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": prompt}]}
        ]
    }

    t0 = time.time()
    try:
        with httpx.Client(timeout=timeout_s) as client:
            resp = client.post(endpoint, headers=headers, json=payload)
        # --- DEBUG PRINT ---
        print(f"DEBUG: Type of resp: {type(resp)}")
        print(f"DEBUG: Type of resp.status_code: {type(resp.status_code)}")
        print(f"DEBUG: Value of resp.status_code: {resp.status_code}")
        # --- END DEBUG PRINT ---
    except httpx.ReadTimeout as e:
        raise GatewayTimeoutError(f"Gemini timeout after {timeout_s}s") from e
    except httpx.RequestError as e:
        # Network/DNS/connectivity
        raise GatewayUpstreamError(f"Gemini request error: {type(e).__name__}") from e

    # Map errors
    if resp.status_code == 401 or resp.status_code == 403:
        raise GatewayAuthError(f"Gemini auth error: HTTP {resp.status_code}")
    if resp.status_code == 429:
        raise GatewayRateLimitError("Gemini rate limited (HTTP 429)")
    if 400 <= resp.status_code < 500:
        detail = _safe_err(resp)
        raise GatewayClientError(f"Gemini client error HTTP {resp.status_code}: {detail}")
    if resp.status_code >= 500:
        detail = _safe_err(resp)
        raise GatewayUpstreamError(f"Gemini upstream error HTTP {resp.status_code}: {detail}")

    # Parse response text (transport normalization only)
    try:
        data = resp.json()
    except Exception as e:
        raise GatewayUpstreamError("Gemini returned non-JSON response") from e

    text = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text")
    )
    # Return raw text as-is (contract), ensuring None becomes ""
    return text if text is not None else ""


def _safe_err(resp: httpx.Response) -> str:
    try:
        j = resp.json()
        if isinstance(j, dict) and "error" in j:
            e = j["error"]
            return f"{e.get('status','?')} {e.get('code','?')}: {e.get('message','')}"
        return json.dumps(j)[:300]
    except Exception:
        return (resp.text or "")[:300]
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/providers/__init__.py

```
# Provider modules live here.

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/providers/offline.py

```
from __future__ import annotations

def call_offline(*, prompt: str, model: str, timeout_s: float) -> str:
    # Deterministic stub for tests and offline runs
    return ""

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/providers/openai.py

```
# future

```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/providers/__pycache__/gemini.cpython-312.pyc

```
Ë
Rçpióãóh—ddlmZddlZddlZddlZddlmZmZmZm	Z	m
Z
										dd„Zdd„Zy)	é)ÚannotationsNé)ÚGatewayAuthErrorÚGatewayClientErrorÚGatewayRateLimitErrorÚGatewayTimeoutErrorÚGatewayUpstreamErrorcóĞ—d}d}|›d|›d|›d}d|dœ}dd	d
|igdœgi}tj«}		tj|¬«5}
|
j|||¬«}ddd«t	dt«›«t	dt|j«›«t	d|j›«|jdk(s|jdk(rtd|j›«‚|jdk(rtd«‚d|jcxkrdkr)nn&t|«}td|j›d|›«‚|jdk\r&t|«}td|j›d|›«‚	|j!«}|j%d ig«d!j%d"i«j%d#ig«d!j%d
«}||Sd$S#1swYŒ}xYw#tj$r}td|›d«|‚d}~wtj$r'}tdt|«j›«|‚d}~wwxYw#t"$r}td«|‚d}~wwxYw)%z]
    Gemini generateContent (Generative Language API).
    Returns model text unchanged.
    z)https://generativelanguage.googleapis.comÚv1ú/z/models/z:generateContentzapplication/json)zContent-Typezx-goog-api-keyÚcontentsÚuserÚtext)ÚroleÚparts)Útimeout)ÚheadersÚjsonNzDEBUG: Type of resp: z!DEBUG: Type of resp.status_code: z"DEBUG: Value of resp.status_code: zGemini timeout after ÚszGemini request error: i‘i“zGemini auth error: HTTP i­zGemini rate limited (HTTP 429)iiôzGemini client error HTTP ú: zGemini upstream error HTTP z!Gemini returned non-JSON responseÚ
candidatesrÚcontentrÚ)ÚtimeÚhttpxÚClientÚpostÚprintÚtypeÚstatus_codeÚReadTimeoutrÚRequestErrorr	Ú__name__rrÚ	_safe_errrrÚ	ExceptionÚget)ÚpromptÚmodelÚapi_keyÚ	timeout_sÚbaseÚversionÚendpointrÚpayloadÚt0ÚclientÚrespÚeÚdetailÚdatars                úA/home/user/AA1/gateways/ai_gateway/ai_gateway/providers/gemini.pyÚcall_geminir6s¥€ğ7€DØ€GØq˜˜	 ¨%¨Ğ0@ĞA€Hğ+à!ñ€Gğ	Ø¨°Ğ'7Ğ&8Ñ9ğ
ğ€Gô
‰‹€BğWÜ\‰\ )Ô,ğ	H°Ø—;‘;˜x°¸w;ÓGˆD÷	Hô	Ğ%¤d¨4£j \Ğ2Ô3ÜĞ1´$°t×7GÑ7GÓ2HĞ1IĞJÔKÜĞ2°4×3CÑ3CĞ2DĞEÔFğ×Ñ˜3Ò $×"2Ñ"2°cÒ"9ÜĞ!9¸$×:JÑ:JĞ9KĞLÓMĞMØ×Ñ˜3ÒÜ#Ğ$DÓEĞEØ
ˆd×ÑÔ$ Õ$Ü˜4“ˆÜ Ğ#<¸T×=MÑ=MĞ<NÈbĞQWĞPXĞ!YÓZĞZØ×Ñ˜3ÒÜ˜4“ˆÜ"Ğ%@À×AQÑAQĞ@RĞRTĞU[ĞT\Ğ#]Ó^Ğ^ğOØy‰y‹{ˆğ
	‰ ˜tÓ$ QÑ'ß	‰ˆY˜Ó	ß	‰ˆWrdÓ	˜Añ	÷
‰ˆV‹ğ		ğĞ#ˆ4Ğ+¨Ğ+÷M	Hñ	Hûô×ÑòOÜ!Ğ$9¸)¸ÀAĞ"FÓGÈQĞNûÜ×ÑòWä"Ğ%;¼DÀ»G×<LÑ<LĞ;MĞ#NÓOĞUVĞVûğWûô&òOÜ"Ğ#FÓGÈQĞNûğOúsTµG(ÁGÁ AG(Å<IÇG%Ç G(Ç(IÇ;HÈIÈ!"IÉIÉ	I%ÉI É I%có>—	|j«}t|t«rCd|vr?|d}|jdd«›d|jdd«›d|jdd«›Stj|«dd	S#t
$r|jxsddd	cYSwxYw)
NÚerrorÚstatusú?ú ÚcoderÚmessageri,)rÚ
isinstanceÚdictr&Údumpsr%r)r1Újr2s   r5r$r$Zs €ğ'ØI‰I‹KˆÜaœÔ 7¨a¡<Ø'‘
ˆAØ—e‘e˜H SÓ)Ğ*¨!¨A¯E©E°&¸Ó,=Ğ+>¸bÀÇÁÀyĞQSÓATĞ@UĞVĞVÜz‰z˜!‹}˜T˜cĞ"Ğ"øÜò'Ø—	‘	’˜R  #Ğ&Ò&ğ'ús‚A"A=Á%A=Á=BÂB)
r'Ústrr(rBr)rBr*ÚfloatÚreturnrB)r1zhttpx.ResponserDrB)Ú
__future__rrrrÚerrorsrrrrr	r6r$©ór5ú<module>rIs\ğİ"ãÛÛ÷õğD,àğD,ğğD,ğğ	D,ğ
ğD,ğ	óD,ôN'rH
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/providers/__pycache__/__init__.cpython-312.pyc

```
Ë
¤×piãó—y)N©róúC/home/user/AA1/gateways/ai_gateway/ai_gateway/providers/__init__.pyú<module>rsñr
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/providers/__pycache__/offline.cpython-312.pyc

```
Ë
ˆ×pi­ãó—ddlmZdd„Zy)é)Úannotationscó—y)NÚ©)ÚpromptÚmodelÚ	timeout_ss   úB/home/user/AA1/gateways/ai_gateway/ai_gateway/providers/offline.pyÚcall_offliners€àóN)rÚstrrrr	ÚfloatÚreturnr)Ú
__future__rrrrr
ú<module>rsğİ"ôr
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/__pycache__/client.cpython-312.pyc

```
Ë
”×pi¡ãó¶—ddlmZddlZddlmZddlmZddlmZm	Z	ddl
mZddlmZmZdd	lmZmZdd
lmZddlmZeGd„d««ZGd„d«Zy)é)ÚannotationsN)Ú	dataclass)ÚOptionalé)ÚGatewayConfigÚload_config)ÚGatewayConfigError)Ú	log_eventÚprompt_hash8)ÚRetryPolicyÚrun_with_retry)Úcall_gemini)Úcall_offlinecóT—eZdZUdZded<dZded<dZded<dZded<dZded	<y)
ÚCallOptionsNzOptional[str]ÚproviderÚmodelzOptional[float]Ú	timeout_sÚtemperaturezOptional[int]Ú
max_tokens)	Ú__name__Ú
__module__Ú__qualname__rÚ__annotations__rrrr©óú7/home/user/AA1/gateways/ai_gateway/ai_gateway/client.pyrrs4…à"€HˆmÓ"Ø€Eˆ=ÓØ!%€IˆÓ%Ø#'€KÓ'Ø $€JÔ$rrcó(—eZdZdZddd„Zddœdd„Zy)	ÚAIGatewayClientz­
    AI Gateway public API.
    Contract: accepts prompt, returns raw model text unchanged.
    Handles only transport concerns (security, retries, stability, logging).
    Ncó*—|xs
t«|_y©N)rÚcfg)Úselfr"s  rÚ__init__zAIGatewayClient.__init__!s€ØÒ'œ+›-ˆr)Úoptionscóø‡‡‡‡‡—t‰t«r‰j«std«‚|xs
t	«}|j
xs‰jj
j«j«Š|jxs‰jjj«Št|jxs‰jj«Št‰«}tj«}t‰jj‰jj‰jj ¬«}t#d‰‰‰|¬«dˆˆˆˆˆfd„}	t%||«}t'tj«|z
dz«}	t#d‰‰|	|¬«|S#t($rM}
t'tj«|z
dz«}	t#d	‰‰|	|t+|
«j,¬
«‚d}
~
wwxYw)Nz!prompt must be a non-empty string)Úmax_retriesÚbackoff_base_sÚbackoff_max_szai_gateway.call.start)rrrrcóØ•—‰dk(rt‰‰‰¬«S‰dk(rD‰jjstd«‚t	‰‰‰jj‰¬«Std‰›«‚)NÚoffline)ÚpromptrrÚgeminiz6Missing GEMINI_API_KEY (or AI_GATEWAY_GEMINI_API_KEY).)r,rÚapi_keyrzUnknown provider: )rr"Úgemini_api_keyr	r)rr,rr#rs€€€€€rÚ_invokez%AIGatewayClient.call.<locals>._invoke>ssø€Ø˜9Ò$Ü#¨6¸È)ÔTĞTà˜8Ò#Ø—x‘x×.Ò.Ü,Ğ-eÓfĞfÜ"Ø!ØØ ŸH™H×3Ñ3Ø'ô	ğô%Ğ'9¸(¸Ğ%DÓEĞErièzai_gateway.call.ok)rrÚ
latency_msrzai_gateway.call.fail)rrr1rÚ
error_type)ÚreturnÚstr)Ú
isinstancer4ÚstripÚ
ValueErrorrrr"ÚlowerrÚfloatrrÚtimerr'r(r)r
rÚintÚ	ExceptionÚtyper)r#r,r%ÚoptÚphÚt0Úpolicyr0ÚoutÚmsÚerrrs``         @@@rÚcallzAIGatewayClient.call$sšü€Ü˜&¤#Ô&¨f¯l©l¬nÜĞ@ÓAĞAàÒ&œ›ˆØ—L‘LÒ5 D§H¡H×$5Ñ$5×<Ñ<Ó>×DÑDÓFˆØ—‘Ò,˜dŸh™hŸn™n×3Ñ3Ó5ˆÜ˜#Ÿ-™-Ò=¨4¯8©8×+=Ñ+=Ó>ˆ	ä˜&Ó!ˆÜY‰Y‹[ˆäØŸ™×,Ñ,ØŸ8™8×2Ñ2ØŸ(™(×0Ñ0ô
ˆô	Ø#ØØØØõ	
÷	Fñ	Fğ 	Ü  ¨&Ó1ˆCÜ”d—i‘i“k BÑ&¨$Ñ.Ó/ˆBÜØ$Ø!ØØØõğˆJøÜò
	Ü”d—i‘i“k BÑ&¨$Ñ.Ó/ˆBÜØ&Ø!ØØØÜ ›7×+Ñ+õğûğ
	úsÅ"AF#Æ#	G9Æ,AG4Ç4G9r!)r"zOptional[GatewayConfig])r,r4r%zOptional[CallOptions]r3r4)rrrÚ__doc__r$rErrrrrs„ñô(ğEIö?rr)Ú
__future__rr:ÚdataclassesrÚtypingrÚconfigrrÚerrorsr	Úloggingr
rÚretryrrÚproviders.geminirÚproviders.offlinerrrrrrú<module>rPsHğİ"ãİ!İç.İ&ß,ß.İ)İ+ğ
÷%ğ%óğ%÷IòIr
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/__pycache__/config.cpython-312.pyc

```
Ë
$×pinãóh—ddlmZddlZddlmZed¬«Gd„d««Zdd„Zdd	„Zdd
„Zy)é)ÚannotationsN)Ú	dataclassT)Úfrozencó^—eZdZUded<ded<ded<ded<ded<ded	<d
ed<d
ed<y)ÚGatewayConfigÚstrÚproviderÚmodelÚfloatÚ	timeout_sÚintÚmax_retriesÚbackoff_base_sÚbackoff_max_sz
str | NoneÚgemini_api_keyÚopenai_api_keyN)Ú__name__Ú
__module__Ú__qualname__Ú__annotations__©óú7/home/user/AA1/gateways/ai_gateway/ai_gateway/config.pyrrs0…àƒMØƒJØÓØÓØÓØÓàÓØÔrrcó”—tj|«}||j«dk(r|S	t|«S#t$r|cYSwxYw©NÚ)ÚosÚgetenvÚstriprÚ
ValueError©ÚnameÚdefaultÚvs   rÚ
_get_floatr%sG€Ü
	‰	$‹€AØ€yA—G‘G“I ’OØˆğÜQ‹xˆøÜòØŠğúó®
9¹AÁAcó”—tj|«}||j«dk(r|S	t|«S#t$r|cYSwxYwr)rrrrr r!s   rÚ_get_intr(sG€Ü
	‰	$‹€AØ€yA—G‘G“I ’OØˆğÜ1‹vˆøÜòØŠğúr&c
ó¤—tjdd«j«j«}tjdd«j«}t	dd«}tdd«}t	d	d
«}t	dd«}tjd«xstjd«}tjd«xstjd«}|s^|dk(r%tjdd«j«}n4|dk(r%tjdd«j«}n
|dk(rd}nd}t||||||||¬«S)NÚAI_GATEWAY_PROVIDERÚgeminiÚAI_GATEWAY_MODELrÚAI_GATEWAY_TIMEOUT_SgN@ÚAI_GATEWAY_RETRIESéÚAI_GATEWAY_BACKOFF_BASE_Sgğ?ÚAI_GATEWAY_BACKOFF_MAX_Sg4@ÚGEMINI_API_KEYÚAI_GATEWAY_GEMINI_API_KEYÚOPENAI_API_KEYÚAI_GATEWAY_OPENAI_API_KEYÚGEMINI_MODELzgemini-2.5-flashÚopenaiÚOPENAI_MODELzgpt-4.1-miniÚoffliner#©r	r
rrrrrr)rrrÚlowerr%r(rr:s        rÚload_configr<(s0€äy‰yĞ.°Ó9×?Ñ?ÓA×GÑGÓI€HÜI‰IĞ(¨"Ó-×3Ñ3Ó5€EäĞ1°4Ó8€IÜĞ/°Ó3€KÜĞ ;¸SÓA€NÜĞ9¸4Ó@€Mô—Y‘YĞ/Ó0ÒZ´B·I±IĞ>YÓ4Z€NÜ—Y‘YĞ/Ó0ÒZ´B·I±IĞ>YÓ4Z€NñØxÒÜ—I‘I˜nĞ.@ÓA×GÑGÓI‰EØ˜Ò!Ü—I‘I˜n¨nÓ=×CÑCÓE‰EØ˜Ò"Ø‰EàˆEäØØØØØ%Ø#Ø%Ø%ô	ğ	r)r"rr#rÚreturnr)r"rr#rr=r)r=r)	Ú
__future__rrÚdataclassesrrr%r(r<rrrú<module>r@s;ğİ"ã	İ!ñ$Ô÷	ğ	óğ	óóô"r
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/__pycache__/errors.cpython-312.pyc

```
Ë
×piãóª—ddlmZGd„de«ZGd„de«ZGd„de«ZGd„d	e«ZGd
„de«ZGd„de«ZGd„de«Z	y)é)Úannotationscó—eZdZdZy)ÚAIGatewayErrorz+Base class for AI Gateway transport errors.N©Ú__name__Ú
__module__Ú__qualname__Ú__doc__©óú7/home/user/AA1/gateways/ai_gateway/ai_gateway/errors.pyrrs„Ú5rrcó—eZdZdZy)ÚGatewayConfigErrorz8Misconfiguration (missing keys, invalid provider/model).Nrrrrrr
s„ÚBrrcó—eZdZdZy)ÚGatewayTimeoutErrorzRequest exceeded timeout.Nrrrrrrs„Ú#rrcó—eZdZdZy)ÚGatewayAuthErrorz%Authentication/authorization failure.Nrrrrrrs„Ú/rrcó—eZdZdZy)ÚGatewayRateLimitErrorz-Supplier rate limited the request (HTTP 429).Nrrrrrrs„Ú7rrcó—eZdZdZy)ÚGatewayUpstreamErrorz7Supplier/service error (5xx or other upstream failure).Nrrrrrrs„ÚArrcó—eZdZdZy)ÚGatewayClientErrorz,Non-retryable client error (4xx except 429).Nrrrrrrs„Ú6rrN)
Ú
__future__rÚRuntimeErrorrrrrrrrrrrú<module>rsbğõ#ô6\ô6ôC˜ôCô$˜.ô$ô0~ô0ô8˜Nô8ôB˜>ôBô7˜õ7r
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/__pycache__/__init__.cpython-312.pyc

```
Ë
9Øpiàãó@—ddlmZmZddlmZmZmZmZmZm	Z	m
Z
gd¢Zy)é)ÚAIGatewayClientÚCallOptions)ÚAIGatewayErrorÚGatewayConfigErrorÚGatewayTimeoutErrorÚGatewayAuthErrorÚGatewayRateLimitErrorÚGatewayUpstreamErrorÚGatewayClientError)	rrrrrrr	r
rN)ÚclientrrÚerrorsrrrrr	r
rÚ__all__©óú9/home/user/AA1/gateways/ai_gateway/ai_gateway/__init__.pyú<module>rsğß0÷÷ñò
r
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/__pycache__/logging.cpython-312.pyc

```
Ë
A×pimãól—ddlmZddlZddlZddlZddlmZddlmZddlm	Z	d
d„Z
dd„Zdd„Zdd	„Zy)é)ÚannotationsN)Údatetime)ÚPath)ÚAnycóP—tj«jd¬«dzS)NÚseconds)ÚtimespecÚZ)rÚutcnowÚ	isoformat©óú8/home/user/AA1/gateways/ai_gateway/ai_gateway/logging.pyÚ_utc_nowrs"€Ü?‰?Ó×&Ñ&°	Ğ&Ó:¸SÑ@Ğ@rcót—tj|xsdjd««j«ddS)NÚúutf-8é)ÚhashlibÚsha256ÚencodeÚ	hexdigest)Úprompts rÚprompt_hash8rs0€Ü>‰>˜6š< R×/Ñ/°Ó8Ó9×CÑCÓEÀbÀqĞIĞIrcóÈ—tjdd«}|rt|«}n*tt«j	«j
dz}|jdd¬«|S)NÚAI_GATEWAY_LOG_DIRrÚlogsT)ÚparentsÚexist_ok)ÚosÚgetenvrÚ__file__ÚresolveÚparentÚmkdir)ÚbaseÚps  rÚ_log_dirr(sQ€ä9‰9Ğ)¨2Ó.€DÙÜ‹J‰ä”‹N×"Ñ"Ó$×+Ñ+¨fÑ4ˆØ‡GGD 4€GÔ(Ø€Hrcóê—t«|dœ|¥}tj|d¬«}t|d¬«	t	«dzjdd¬	«j|d
z«y#t$rYywxYw)zh
    Operational logging only. Never log prompt or output text.
    Emits JSONL for easy ingestion.
    )ÚtsÚeventF)Úensure_asciiT)Úflushzai_gateway.log.jsonlÚar)Úencodingú
N)rÚjsonÚdumpsÚprintr(ÚopenÚwriteÚ	Exception)r+ÚfieldsÚrecÚlines    rÚ	log_eventr:ss€ô
“ eÑ
6¨vĞ
6€CÜ:‰:c¨Ô.€DÜ	ˆ$dÕğÜ	‹Ğ,Ñ	,×2Ñ2°3ÀĞ2ÓI×OÑOĞPTĞW[ÑP[Õ\øÜòáğúsµ0A&Á&	A2Á1A2)ÚreturnÚstr)rr<r;r<)r;r)r+r<r7rr;ÚNone)Ú
__future__rrr1r rÚpathlibrÚtypingrrrr(r:rrrú<module>rAs0ğİ"ãÛÛ	İİİóAóJóôr
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/__pycache__/retry.cpython-312.pyc

```
Ë
S×piŒãó¦—ddlmZddlZddlZddlmZddlmZmZddl	m
Z
mZmZed«Zed¬	«Gd
„d««Zee
efZdd„Zdd„Zy)é)ÚannotationsN)Ú	dataclass)ÚCallableÚTypeVaré)ÚGatewayRateLimitErrorÚGatewayTimeoutErrorÚGatewayUpstreamErrorÚTT)Úfrozencó8—eZdZUdZded<dZded<dZded<y	)
ÚRetryPolicyéÚintÚmax_retriesgğ?ÚfloatÚbackoff_base_sg4@Úbackoff_max_sN)Ú__name__Ú
__module__Ú__qualname__rÚ__annotations__rr©óú6/home/user/AA1/gateways/ai_gateway/ai_gateway/retry.pyrrs …à€KÓØ€NEÓØ€M5Ôrrcó—|jdtd|«zz}tjdd|z«}t	|j
||z«S)NérggĞ?)rÚmaxÚrandomÚuniformÚminr)ÚpolicyÚattemptÚbaseÚjitters    rÚ_sleep_sr&sH€à× Ñ  A¬¨Q°«Ñ$8Ñ9€DÜ^‰^˜C ¨¡Ó-€FÜˆv×#Ñ# T¨F¡]Ó3Ğ3rcóì—d}t|jdz«D]}	|«cS|€J‚|‚#t$r;}|}||jk\r‚tjt||««Yd}~ŒSd}~wwxYw)Nr)ÚrangerÚ
_RETRYABLEÚtimeÚsleepr&)Úfnr"Úlast_excr#Úes     rÚrun_with_retryr/"sƒ€Ø!%€HÜ˜×+Ñ+¨aÑ/Ó0ò2ˆğ	2Ù“4ŠKğ2ğĞĞĞØ
€Nøôò	2ØˆHØ˜&×,Ñ,Ò,ØÜJ‰J”x ¨Ó0×1Ñ1ûğ		2úsŸ/¯	A3¸1A.Á.A3)r"rr#rÚreturnr)r,zCallable[[], T]r"rr0r)Ú
__future__rrr*ÚdataclassesrÚtypingrrÚerrorsrr	r
rrr)r&r/rrrú<module>r5sağİ"ãÛİ!ß$÷ññˆCƒL€ñ$Ô÷ ğ óğ ğ"Ğ#8Ğ:NĞO€
ó4ôr
```

## File: /home/user/AA1/gateways/ai_gateway/ai_gateway/retry.py

```
from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, TypeVar

from .errors import (
    GatewayRateLimitError,
    GatewayTimeoutError,
    GatewayUpstreamError,
)

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    max_retries: int = 3
    backoff_base_s: float = 1.0
    backoff_max_s: float = 20.0


_RETRYABLE = (GatewayTimeoutError, GatewayRateLimitError, GatewayUpstreamError)


def _sleep_s(policy: RetryPolicy, attempt: int) -> float:
    # exp backoff with jitter
    base = policy.backoff_base_s * (2 ** max(0, attempt))
    jitter = random.uniform(0.0, 0.25 * base)
    return min(policy.backoff_max_s, base + jitter)


def run_with_retry(fn: Callable[[], T], policy: RetryPolicy) -> T:
    last_exc: Exception | None = None
    for attempt in range(policy.max_retries + 1):
        try:
            return fn()
        except _RETRYABLE as e:
            last_exc = e
            if attempt >= policy.max_retries:
                raise
            time.sleep(_sleep_s(policy, attempt))
    # Should be unreachable
    assert last_exc is not None
    raise last_exc

```

## File: /home/user/AA1/gateways/ai_gateway/gateways_full_dump.md

```

```

## File: /home/user/AA1/gateways/ai_gateway/poetry.lock

```
# This file is automatically @generated by Poetry 2.3.1 and should not be changed by hand.

[[package]]
name = "annotated-types"
version = "0.7.0"
description = "Reusable constraint types to use with typing.Annotated"
optional = false
python-versions = ">=3.8"
groups = ["main"]
files = [
    {file = "annotated_types-0.7.0-py3-none-any.whl", hash = "sha256:1f02e8b43a8fbbc3f3e0d4f0f4bfc8131bcb4eebe8849b8e5c773f3a1c582a53"},
    {file = "annotated_types-0.7.0.tar.gz", hash = "sha256:aff07c09a53a08bc8cfccb9c85b05f1aa9a2a6f23728d790723543408344ce89"},
]

[[package]]
name = "anyio"
version = "4.12.1"
description = "High-level concurrency and networking framework on top of asyncio or Trio"
optional = false
python-versions = ">=3.9"
groups = ["main"]
files = [
    {file = "anyio-4.12.1-py3-none-any.whl", hash = "sha256:d405828884fc140aa80a3c667b8beed277f1dfedec42ba031bd6ac3db606ab6c"},
    {file = "anyio-4.12.1.tar.gz", hash = "sha256:41cfcc3a4c85d3f05c932da7c26d0201ac36f72abd4435ba90d0464a3ffed703"},
]

[package.dependencies]
idna = ">=2.8"
typing_extensions = {version = ">=4.5", markers = "python_version < \"3.13\""}

[package.extras]
trio = ["trio (>=0.31.0) ; python_version < \"3.10\"", "trio (>=0.32.0) ; python_version >= \"3.10\""]

[[package]]
name = "backoff"
version = "2.2.1"
description = "Function decoration for backoff and retry"
optional = false
python-versions = ">=3.7,<4.0"
groups = ["main"]
files = [
    {file = "backoff-2.2.1-py3-none-any.whl", hash = "sha256:63579f9a0628e06278f7e47b7d7d5b6ce20dc65c5e96a6f3ca99a6adca0396e8"},
    {file = "backoff-2.2.1.tar.gz", hash = "sha256:03f829f5bb1923180821643f8753b0502c3b682293992485b0eef2807afa5cba"},
]

[[package]]
name = "certifi"
version = "2026.1.4"
description = "Python package for providing Mozilla's CA Bundle."
optional = false
python-versions = ">=3.7"
groups = ["main"]
files = [
    {file = "certifi-2026.1.4-py3-none-any.whl", hash = "sha256:9943707519e4add1115f44c2bc244f782c0249876bf51b6599fee1ffbedd685c"},
    {file = "certifi-2026.1.4.tar.gz", hash = "sha256:ac726dd470482006e014ad384921ed6438c457018f4b3d204aea4281258b2120"},
]

[[package]]
name = "colorama"
version = "0.4.6"
description = "Cross-platform colored terminal text."
optional = false
python-versions = "!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*,!=3.6.*,>=2.7"
groups = ["dev"]
markers = "sys_platform == \"win32\""
files = [
    {file = "colorama-0.4.6-py2.py3-none-any.whl", hash = "sha256:4f1d9991f5acc0ca119f9d443620b77f9d6b33703e51011c16baf57afb285fc6"},
    {file = "colorama-0.4.6.tar.gz", hash = "sha256:08695f5cb7ed6e0531a20572697297273c47b8cae5a63ffc6d6ed5c201be6e44"},
]

[[package]]
name = "h11"
version = "0.16.0"
description = "A pure-Python, bring-your-own-I/O implementation of HTTP/1.1"
optional = false
python-versions = ">=3.8"
groups = ["main"]
files = [
    {file = "h11-0.16.0-py3-none-any.whl", hash = "sha256:63cf8bbe7522de3bf65932fda1d9c2772064ffb3dae62d55932da54b31cb6c86"},
    {file = "h11-0.16.0.tar.gz", hash = "sha256:4e35b956cf45792e4caa5885e69fba00bdbc6ffafbfa020300e549b208ee5ff1"},
]

[[package]]
name = "httpcore"
version = "1.0.9"
description = "A minimal low-level HTTP client."
optional = false
python-versions = ">=3.8"
groups = ["main"]
files = [
    {file = "httpcore-1.0.9-py3-none-any.whl", hash = "sha256:2d400746a40668fc9dec9810239072b40b4484b640a8c38fd654a024c7a1bf55"},
    {file = "httpcore-1.0.9.tar.gz", hash = "sha256:6e34463af53fd2ab5d807f399a9b45ea31c3dfa2276f15a2c3f00afff6e176e8"},
]

[package.dependencies]
certifi = "*"
h11 = ">=0.16"

[package.extras]
asyncio = ["anyio (>=4.0,<5.0)"]
http2 = ["h2 (>=3,<5)"]
socks = ["socksio (==1.*)"]
trio = ["trio (>=0.22.0,<1.0)"]

[[package]]
name = "httpx"
version = "0.26.0"
description = "The next generation HTTP client."
optional = false
python-versions = ">=3.8"
groups = ["main"]
files = [
    {file = "httpx-0.26.0-py3-none-any.whl", hash = "sha256:8915f5a3627c4d47b73e8202457cb28f1266982d1159bd5779d86a80c0eab1cd"},
    {file = "httpx-0.26.0.tar.gz", hash = "sha256:451b55c30d5185ea6b23c2c793abf9bb237d2a7dfb901ced6ff69ad37ec1dfaf"},
]

[package.dependencies]
anyio = "*"
certifi = "*"
httpcore = "==1.*"
idna = "*"
sniffio = "*"

[package.extras]
brotli = ["brotli ; platform_python_implementation == \"CPython\"", "brotlicffi ; platform_python_implementation != \"CPython\""]
cli = ["click (==8.*)", "pygments (==2.*)", "rich (>=10,<14)"]
http2 = ["h2 (>=3,<5)"]
socks = ["socksio (==1.*)"]

[[package]]
name = "idna"
version = "3.11"
description = "Internationalized Domain Names in Applications (IDNA)"
optional = false
python-versions = ">=3.8"
groups = ["main"]
files = [
    {file = "idna-3.11-py3-none-any.whl", hash = "sha256:771a87f49d9defaf64091e6e6fe9c18d4833f140bd19464795bc32d966ca37ea"},
    {file = "idna-3.11.tar.gz", hash = "sha256:795dafcc9c04ed0c1fb032c2aa73654d8e8c5023a7df64a53f39190ada629902"},
]

[package.extras]
all = ["flake8 (>=7.1.1)", "mypy (>=1.11.2)", "pytest (>=8.3.2)", "ruff (>=0.6.2)"]

[[package]]
name = "iniconfig"
version = "2.3.0"
description = "brain-dead simple config-ini parsing"
optional = false
python-versions = ">=3.10"
groups = ["dev"]
files = [
    {file = "iniconfig-2.3.0-py3-none-any.whl", hash = "sha256:f631c04d2c48c52b84d0d0549c99ff3859c98df65b3101406327ecc7d53fbf12"},
    {file = "iniconfig-2.3.0.tar.gz", hash = "sha256:c76315c77db068650d49c5b56314774a7804df16fee4402c1f19d6d15d8c4730"},
]

[[package]]
name = "packaging"
version = "25.0"
description = "Core utilities for Python packages"
optional = false
python-versions = ">=3.8"
groups = ["dev"]
files = [
    {file = "packaging-25.0-py3-none-any.whl", hash = "sha256:29572ef2b1f17581046b3a2227d5c611fb25ec70ca1ba8554b24b0e69331a484"},
    {file = "packaging-25.0.tar.gz", hash = "sha256:d443872c98d677bf60f6a1f2f8c1cb748e8fe762d2bf9d3148b5599295b0fc4f"},
]

[[package]]
name = "pluggy"
version = "1.6.0"
description = "plugin and hook calling mechanisms for python"
optional = false
python-versions = ">=3.9"
groups = ["dev"]
files = [
    {file = "pluggy-1.6.0-py3-none-any.whl", hash = "sha256:e920276dd6813095e9377c0bc5566d94c932c33b27a3e3945d8389c374dd4746"},
    {file = "pluggy-1.6.0.tar.gz", hash = "sha256:7dcc130b76258d33b90f61b658791dede3486c3e6bfb003ee5c9bfb396dd22f3"},
]

[package.extras]
dev = ["pre-commit", "tox"]
testing = ["coverage", "pytest", "pytest-benchmark"]

[[package]]
name = "pydantic"
version = "2.12.5"
description = "Data validation using Python type hints"
optional = false
python-versions = ">=3.9"
groups = ["main"]
files = [
    {file = "pydantic-2.12.5-py3-none-any.whl", hash = "sha256:e561593fccf61e8a20fc46dfc2dfe075b8be7d0188df33f221ad1f0139180f9d"},
    {file = "pydantic-2.12.5.tar.gz", hash = "sha256:4d351024c75c0f085a9febbb665ce8c0c6ec5d30e903bdb6394b7ede26aebb49"},
]

[package.dependencies]
annotated-types = ">=0.6.0"
pydantic-core = "2.41.5"
typing-extensions = ">=4.14.1"
typing-inspection = ">=0.4.2"

[package.extras]
email = ["email-validator (>=2.0.0)"]
timezone = ["tzdata ; python_version >= \"3.9\" and platform_system == \"Windows\""]

[[package]]
name = "pydantic-core"
version = "2.41.5"
description = "Core functionality for Pydantic validation and serialization"
optional = false
python-versions = ">=3.9"
groups = ["main"]
files = [
    {file = "pydantic_core-2.41.5-cp310-cp310-macosx_10_12_x86_64.whl", hash = "sha256:77b63866ca88d804225eaa4af3e664c5faf3568cea95360d21f4725ab6e07146"},
    {file = "pydantic_core-2.41.5-cp310-cp310-macosx_11_0_arm64.whl", hash = "sha256:dfa8a0c812ac681395907e71e1274819dec685fec28273a28905df579ef137e2"},
    {file = "pydantic_core-2.41.5-cp310-cp310-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:5921a4d3ca3aee735d9fd163808f5e8dd6c6972101e4adbda9a4667908849b97"},
    {file = "pydantic_core-2.41.5-cp310-cp310-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:e25c479382d26a2a41b7ebea1043564a937db462816ea07afa8a44c0866d52f9"},
    {file = "pydantic_core-2.41.5-cp310-cp310-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:f547144f2966e1e16ae626d8ce72b4cfa0caedc7fa28052001c94fb2fcaa1c52"},
    {file = "pydantic_core-2.41.5-cp310-cp310-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:6f52298fbd394f9ed112d56f3d11aabd0d5bd27beb3084cc3d8ad069483b8941"},
    {file = "pydantic_core-2.41.5-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:100baa204bb412b74fe285fb0f3a385256dad1d1879f0a5cb1499ed2e83d132a"},
    {file = "pydantic_core-2.41.5-cp310-cp310-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:05a2c8852530ad2812cb7914dc61a1125dc4e06252ee98e5638a12da6cc6fb6c"},
    {file = "pydantic_core-2.41.5-cp310-cp310-musllinux_1_1_aarch64.whl", hash = "sha256:29452c56df2ed968d18d7e21f4ab0ac55e71dc59524872f6fc57dcf4a3249ed2"},
    {file = "pydantic_core-2.41.5-cp310-cp310-musllinux_1_1_armv7l.whl", hash = "sha256:d5160812ea7a8a2ffbe233d8da666880cad0cbaf5d4de74ae15c313213d62556"},
    {file = "pydantic_core-2.41.5-cp310-cp310-musllinux_1_1_x86_64.whl", hash = "sha256:df3959765b553b9440adfd3c795617c352154e497a4eaf3752555cfb5da8fc49"},
    {file = "pydantic_core-2.41.5-cp310-cp310-win32.whl", hash = "sha256:1f8d33a7f4d5a7889e60dc39856d76d09333d8a6ed0f5f1190635cbec70ec4ba"},
    {file = "pydantic_core-2.41.5-cp310-cp310-win_amd64.whl", hash = "sha256:62de39db01b8d593e45871af2af9e497295db8d73b085f6bfd0b18c83c70a8f9"},
    {file = "pydantic_core-2.41.5-cp311-cp311-macosx_10_12_x86_64.whl", hash = "sha256:a3a52f6156e73e7ccb0f8cced536adccb7042be67cb45f9562e12b319c119da6"},
    {file = "pydantic_core-2.41.5-cp311-cp311-macosx_11_0_arm64.whl", hash = "sha256:7f3bf998340c6d4b0c9a2f02d6a400e51f123b59565d74dc60d252ce888c260b"},
    {file = "pydantic_core-2.41.5-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:378bec5c66998815d224c9ca994f1e14c0c21cb95d2f52b6021cc0b2a58f2a5a"},
    {file = "pydantic_core-2.41.5-cp311-cp311-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:e7b576130c69225432866fe2f4a469a85a54ade141d96fd396dffcf607b558f8"},
    {file = "pydantic_core-2.41.5-cp311-cp311-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:6cb58b9c66f7e4179a2d5e0f849c48eff5c1fca560994d6eb6543abf955a149e"},
    {file = "pydantic_core-2.41.5-cp311-cp311-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:88942d3a3dff3afc8288c21e565e476fc278902ae4d6d134f1eeda118cc830b1"},
    {file = "pydantic_core-2.41.5-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:f31d95a179f8d64d90f6831d71fa93290893a33148d890ba15de25642c5d075b"},
    {file = "pydantic_core-2.41.5-cp311-cp311-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:c1df3d34aced70add6f867a8cf413e299177e0c22660cc767218373d0779487b"},
    {file = "pydantic_core-2.41.5-cp311-cp311-musllinux_1_1_aarch64.whl", hash = "sha256:4009935984bd36bd2c774e13f9a09563ce8de4abaa7226f5108262fa3e637284"},
    {file = "pydantic_core-2.41.5-cp311-cp311-musllinux_1_1_armv7l.whl", hash = "sha256:34a64bc3441dc1213096a20fe27e8e128bd3ff89921706e83c0b1ac971276594"},
    {file = "pydantic_core-2.41.5-cp311-cp311-musllinux_1_1_x86_64.whl", hash = "sha256:c9e19dd6e28fdcaa5a1de679aec4141f691023916427ef9bae8584f9c2fb3b0e"},
    {file = "pydantic_core-2.41.5-cp311-cp311-win32.whl", hash = "sha256:2c010c6ded393148374c0f6f0bf89d206bf3217f201faa0635dcd56bd1520f6b"},
    {file = "pydantic_core-2.41.5-cp311-cp311-win_amd64.whl", hash = "sha256:76ee27c6e9c7f16f47db7a94157112a2f3a00e958bc626e2f4ee8bec5c328fbe"},
    {file = "pydantic_core-2.41.5-cp311-cp311-win_arm64.whl", hash = "sha256:4bc36bbc0b7584de96561184ad7f012478987882ebf9f9c389b23f432ea3d90f"},
    {file = "pydantic_core-2.41.5-cp312-cp312-macosx_10_12_x86_64.whl", hash = "sha256:f41a7489d32336dbf2199c8c0a215390a751c5b014c2c1c5366e817202e9cdf7"},
    {file = "pydantic_core-2.41.5-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:070259a8818988b9a84a449a2a7337c7f430a22acc0859c6b110aa7212a6d9c0"},
    {file = "pydantic_core-2.41.5-cp312-cp312-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:e96cea19e34778f8d59fe40775a7a574d95816eb150850a85a7a4c8f4b94ac69"},
    {file = "pydantic_core-2.41.5-cp312-cp312-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:ed2e99c456e3fadd05c991f8f437ef902e00eedf34320ba2b0842bd1c3ca3a75"},
    {file = "pydantic_core-2.41.5-cp312-cp312-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:65840751b72fbfd82c3c640cff9284545342a4f1eb1586ad0636955b261b0b05"},
    {file = "pydantic_core-2.41.5-cp312-cp312-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:e536c98a7626a98feb2d3eaf75944ef6f3dbee447e1f841eae16f2f0a72d8ddc"},
    {file = "pydantic_core-2.41.5-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:eceb81a8d74f9267ef4081e246ffd6d129da5d87e37a77c9bde550cb04870c1c"},
    {file = "pydantic_core-2.41.5-cp312-cp312-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:d38548150c39b74aeeb0ce8ee1d8e82696f4a4e16ddc6de7b1d8823f7de4b9b5"},
    {file = "pydantic_core-2.41.5-cp312-cp312-musllinux_1_1_aarch64.whl", hash = "sha256:c23e27686783f60290e36827f9c626e63154b82b116d7fe9adba1fda36da706c"},
    {file = "pydantic_core-2.41.5-cp312-cp312-musllinux_1_1_armv7l.whl", hash = "sha256:482c982f814460eabe1d3bb0adfdc583387bd4691ef00b90575ca0d2b6fe2294"},
    {file = "pydantic_core-2.41.5-cp312-cp312-musllinux_1_1_x86_64.whl", hash = "sha256:bfea2a5f0b4d8d43adf9d7b8bf019fb46fdd10a2e5cde477fbcb9d1fa08c68e1"},
    {file = "pydantic_core-2.41.5-cp312-cp312-win32.whl", hash = "sha256:b74557b16e390ec12dca509bce9264c3bbd128f8a2c376eaa68003d7f327276d"},
    {file = "pydantic_core-2.41.5-cp312-cp312-win_amd64.whl", hash = "sha256:1962293292865bca8e54702b08a4f26da73adc83dd1fcf26fbc875b35d81c815"},
    {file = "pydantic_core-2.41.5-cp312-cp312-win_arm64.whl", hash = "sha256:1746d4a3d9a794cacae06a5eaaccb4b8643a131d45fbc9af23e353dc0a5ba5c3"},
    {file = "pydantic_core-2.41.5-cp313-cp313-macosx_10_12_x86_64.whl", hash = "sha256:941103c9be18ac8daf7b7adca8228f8ed6bb7a1849020f643b3a14d15b1924d9"},
    {file = "pydantic_core-2.41.5-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:112e305c3314f40c93998e567879e887a3160bb8689ef3d2c04b6cc62c33ac34"},
    {file = "pydantic_core-2.41.5-cp313-cp313-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:0cbaad15cb0c90aa221d43c00e77bb33c93e8d36e0bf74760cd00e732d10a6a0"},
    {file = "pydantic_core-2.41.5-cp313-cp313-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:03ca43e12fab6023fc79d28ca6b39b05f794ad08ec2feccc59a339b02f2b3d33"},
    {file = "pydantic_core-2.41.5-cp313-cp313-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:dc799088c08fa04e43144b164feb0c13f9a0bc40503f8df3e9fde58a3c0c101e"},
    {file = "pydantic_core-2.41.5-cp313-cp313-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:97aeba56665b4c3235a0e52b2c2f5ae9cd071b8a8310ad27bddb3f7fb30e9aa2"},
    {file = "pydantic_core-2.41.5-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:406bf18d345822d6c21366031003612b9c77b3e29ffdb0f612367352aab7d586"},
    {file = "pydantic_core-2.41.5-cp313-cp313-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:b93590ae81f7010dbe380cdeab6f515902ebcbefe0b9327cc4804d74e93ae69d"},
    {file = "pydantic_core-2.41.5-cp313-cp313-musllinux_1_1_aarch64.whl", hash = "sha256:01a3d0ab748ee531f4ea6c3e48ad9dac84ddba4b0d82291f87248f2f9de8d740"},
    {file = "pydantic_core-2.41.5-cp313-cp313-musllinux_1_1_armv7l.whl", hash = "sha256:6561e94ba9dacc9c61bce40e2d6bdc3bfaa0259d3ff36ace3b1e6901936d2e3e"},
    {file = "pydantic_core-2.41.5-cp313-cp313-musllinux_1_1_x86_64.whl", hash = "sha256:915c3d10f81bec3a74fbd4faebe8391013ba61e5a1a8d48c4455b923bdda7858"},
    {file = "pydantic_core-2.41.5-cp313-cp313-win32.whl", hash = "sha256:650ae77860b45cfa6e2cdafc42618ceafab3a2d9a3811fcfbd3bbf8ac3c40d36"},
    {file = "pydantic_core-2.41.5-cp313-cp313-win_amd64.whl", hash = "sha256:79ec52ec461e99e13791ec6508c722742ad745571f234ea6255bed38c6480f11"},
    {file = "pydantic_core-2.41.5-cp313-cp313-win_arm64.whl", hash = "sha256:3f84d5c1b4ab906093bdc1ff10484838aca54ef08de4afa9de0f5f14d69639cd"},
    {file = "pydantic_core-2.41.5-cp314-cp314-macosx_10_12_x86_64.whl", hash = "sha256:3f37a19d7ebcdd20b96485056ba9e8b304e27d9904d233d7b1015db320e51f0a"},
    {file = "pydantic_core-2.41.5-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:1d1d9764366c73f996edd17abb6d9d7649a7eb690006ab6adbda117717099b14"},
    {file = "pydantic_core-2.41.5-cp314-cp314-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:25e1c2af0fce638d5f1988b686f3b3ea8cd7de5f244ca147c777769e798a9cd1"},
    {file = "pydantic_core-2.41.5-cp314-cp314-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:506d766a8727beef16b7adaeb8ee6217c64fc813646b424d0804d67c16eddb66"},
    {file = "pydantic_core-2.41.5-cp314-cp314-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:4819fa52133c9aa3c387b3328f25c1facc356491e6135b459f1de698ff64d869"},
    {file = "pydantic_core-2.41.5-cp314-cp314-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:2b761d210c9ea91feda40d25b4efe82a1707da2ef62901466a42492c028553a2"},
    {file = "pydantic_core-2.41.5-cp314-cp314-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:22f0fb8c1c583a3b6f24df2470833b40207e907b90c928cc8d3594b76f874375"},
    {file = "pydantic_core-2.41.5-cp314-cp314-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:2782c870e99878c634505236d81e5443092fba820f0373997ff75f90f68cd553"},
    {file = "pydantic_core-2.41.5-cp314-cp314-musllinux_1_1_aarch64.whl", hash = "sha256:0177272f88ab8312479336e1d777f6b124537d47f2123f89cb37e0accea97f90"},
    {file = "pydantic_core-2.41.5-cp314-cp314-musllinux_1_1_armv7l.whl", hash = "sha256:63510af5e38f8955b8ee5687740d6ebf7c2a0886d15a6d65c32814613681bc07"},
    {file = "pydantic_core-2.41.5-cp314-cp314-musllinux_1_1_x86_64.whl", hash = "sha256:e56ba91f47764cc14f1daacd723e3e82d1a89d783f0f5afe9c364b8bb491ccdb"},
    {file = "pydantic_core-2.41.5-cp314-cp314-win32.whl", hash = "sha256:aec5cf2fd867b4ff45b9959f8b20ea3993fc93e63c7363fe6851424c8a7e7c23"},
    {file = "pydantic_core-2.41.5-cp314-cp314-win_amd64.whl", hash = "sha256:8e7c86f27c585ef37c35e56a96363ab8de4e549a95512445b85c96d3e2f7c1bf"},
    {file = "pydantic_core-2.41.5-cp314-cp314-win_arm64.whl", hash = "sha256:e672ba74fbc2dc8eea59fb6d4aed6845e6905fc2a8afe93175d94a83ba2a01a0"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-macosx_10_12_x86_64.whl", hash = "sha256:8566def80554c3faa0e65ac30ab0932b9e3a5cd7f8323764303d468e5c37595a"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:b80aa5095cd3109962a298ce14110ae16b8c1aece8b72f9dafe81cf597ad80b3"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:3006c3dd9ba34b0c094c544c6006cc79e87d8612999f1a5d43b769b89181f23c"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:72f6c8b11857a856bcfa48c86f5368439f74453563f951e473514579d44aa612"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:5cb1b2f9742240e4bb26b652a5aeb840aa4b417c7748b6f8387927bc6e45e40d"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:bd3d54f38609ff308209bd43acea66061494157703364ae40c951f83ba99a1a9"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:2ff4321e56e879ee8d2a879501c8e469414d948f4aba74a2d4593184eb326660"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:d0d2568a8c11bf8225044aa94409e21da0cb09dcdafe9ecd10250b2baad531a9"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-musllinux_1_1_aarch64.whl", hash = "sha256:a39455728aabd58ceabb03c90e12f71fd30fa69615760a075b9fec596456ccc3"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-musllinux_1_1_armv7l.whl", hash = "sha256:239edca560d05757817c13dc17c50766136d21f7cd0fac50295499ae24f90fdf"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-musllinux_1_1_x86_64.whl", hash = "sha256:2a5e06546e19f24c6a96a129142a75cee553cc018ffee48a460059b1185f4470"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-win32.whl", hash = "sha256:b4ececa40ac28afa90871c2cc2b9ffd2ff0bf749380fbdf57d165fd23da353aa"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-win_amd64.whl", hash = "sha256:80aa89cad80b32a912a65332f64a4450ed00966111b6615ca6816153d3585a8c"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-win_arm64.whl", hash = "sha256:35b44f37a3199f771c3eaa53051bc8a70cd7b54f333531c59e29fd4db5d15008"},
    {file = "pydantic_core-2.41.5-cp39-cp39-macosx_10_12_x86_64.whl", hash = "sha256:8bfeaf8735be79f225f3fefab7f941c712aaca36f1128c9d7e2352ee1aa87bdf"},
    {file = "pydantic_core-2.41.5-cp39-cp39-macosx_11_0_arm64.whl", hash = "sha256:346285d28e4c8017da95144c7f3acd42740d637ff41946af5ce6e5e420502dd5"},
    {file = "pydantic_core-2.41.5-cp39-cp39-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:a75dafbf87d6276ddc5b2bf6fae5254e3d0876b626eb24969a574fff9149ee5d"},
    {file = "pydantic_core-2.41.5-cp39-cp39-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:7b93a4d08587e2b7e7882de461e82b6ed76d9026ce91ca7915e740ecc7855f60"},
    {file = "pydantic_core-2.41.5-cp39-cp39-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:e8465ab91a4bd96d36dde3263f06caa6a8a6019e4113f24dc753d79a8b3a3f82"},
    {file = "pydantic_core-2.41.5-cp39-cp39-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:299e0a22e7ae2b85c1a57f104538b2656e8ab1873511fd718a1c1c6f149b77b5"},
    {file = "pydantic_core-2.41.5-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:707625ef0983fcfb461acfaf14de2067c5942c6bb0f3b4c99158bed6fedd3cf3"},
    {file = "pydantic_core-2.41.5-cp39-cp39-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:f41eb9797986d6ebac5e8edff36d5cef9de40def462311b3eb3eeded1431e425"},
    {file = "pydantic_core-2.41.5-cp39-cp39-musllinux_1_1_aarch64.whl", hash = "sha256:0384e2e1021894b1ff5a786dbf94771e2986ebe2869533874d7e43bc79c6f504"},
    {file = "pydantic_core-2.41.5-cp39-cp39-musllinux_1_1_armv7l.whl", hash = "sha256:f0cd744688278965817fd0839c4a4116add48d23890d468bc436f78beb28abf5"},
    {file = "pydantic_core-2.41.5-cp39-cp39-musllinux_1_1_x86_64.whl", hash = "sha256:753e230374206729bf0a807954bcc6c150d3743928a73faffee51ac6557a03c3"},
    {file = "pydantic_core-2.41.5-cp39-cp39-win32.whl", hash = "sha256:873e0d5b4fb9b89ef7c2d2a963ea7d02879d9da0da8d9d4933dee8ee86a8b460"},
    {file = "pydantic_core-2.41.5-cp39-cp39-win_amd64.whl", hash = "sha256:e4f4a984405e91527a0d62649ee21138f8e3d0ef103be488c1dc11a80d7f184b"},
    {file = "pydantic_core-2.41.5-graalpy311-graalpy242_311_native-macosx_10_12_x86_64.whl", hash = "sha256:b96d5f26b05d03cc60f11a7761a5ded1741da411e7fe0909e27a5e6a0cb7b034"},
    {file = "pydantic_core-2.41.5-graalpy311-graalpy242_311_native-macosx_11_0_arm64.whl", hash = "sha256:634e8609e89ceecea15e2d61bc9ac3718caaaa71963717bf3c8f38bfde64242c"},
    {file = "pydantic_core-2.41.5-graalpy311-graalpy242_311_native-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:93e8740d7503eb008aa2df04d3b9735f845d43ae845e6dcd2be0b55a2da43cd2"},
    {file = "pydantic_core-2.41.5-graalpy311-graalpy242_311_native-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:f15489ba13d61f670dcc96772e733aad1a6f9c429cc27574c6cdaed82d0146ad"},
    {file = "pydantic_core-2.41.5-graalpy312-graalpy250_312_native-macosx_10_12_x86_64.whl", hash = "sha256:7da7087d756b19037bc2c06edc6c170eeef3c3bafcb8f532ff17d64dc427adfd"},
    {file = "pydantic_core-2.41.5-graalpy312-graalpy250_312_native-macosx_11_0_arm64.whl", hash = "sha256:aabf5777b5c8ca26f7824cb4a120a740c9588ed58df9b2d196ce92fba42ff8dc"},
    {file = "pydantic_core-2.41.5-graalpy312-graalpy250_312_native-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:c007fe8a43d43b3969e8469004e9845944f1a80e6acd47c150856bb87f230c56"},
    {file = "pydantic_core-2.41.5-graalpy312-graalpy250_312_native-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:76d0819de158cd855d1cbb8fcafdf6f5cf1eb8e470abe056d5d161106e38062b"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-macosx_10_12_x86_64.whl", hash = "sha256:b5819cd790dbf0c5eb9f82c73c16b39a65dd6dd4d1439dcdea7816ec9adddab8"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-macosx_11_0_arm64.whl", hash = "sha256:5a4e67afbc95fa5c34cf27d9089bca7fcab4e51e57278d710320a70b956d1b9a"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:ece5c59f0ce7d001e017643d8d24da587ea1f74f6993467d85ae8a5ef9d4f42b"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:16f80f7abe3351f8ea6858914ddc8c77e02578544a0ebc15b4c2e1a0e813b0b2"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-musllinux_1_1_aarch64.whl", hash = "sha256:33cb885e759a705b426baada1fe68cbb0a2e68e34c5d0d0289a364cf01709093"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-musllinux_1_1_armv7l.whl", hash = "sha256:c8d8b4eb992936023be7dee581270af5c6e0697a8559895f527f5b7105ecd36a"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-musllinux_1_1_x86_64.whl", hash = "sha256:242a206cd0318f95cd21bdacff3fcc3aab23e79bba5cac3db5a841c9ef9c6963"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-win_amd64.whl", hash = "sha256:d3a978c4f57a597908b7e697229d996d77a6d3c94901e9edee593adada95ce1a"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-macosx_10_12_x86_64.whl", hash = "sha256:b2379fa7ed44ddecb5bfe4e48577d752db9fc10be00a6b7446e9663ba143de26"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-macosx_11_0_arm64.whl", hash = "sha256:266fb4cbf5e3cbd0b53669a6d1b039c45e3ce651fd5442eff4d07c2cc8d66808"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:58133647260ea01e4d0500089a8c4f07bd7aa6ce109682b1426394988d8aaacc"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:287dad91cfb551c363dc62899a80e9e14da1f0e2b6ebde82c806612ca2a13ef1"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-musllinux_1_1_aarch64.whl", hash = "sha256:03b77d184b9eb40240ae9fd676ca364ce1085f203e1b1256f8ab9984dca80a84"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-musllinux_1_1_armv7l.whl", hash = "sha256:a668ce24de96165bb239160b3d854943128f4334822900534f2fe947930e5770"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-musllinux_1_1_x86_64.whl", hash = "sha256:f14f8f046c14563f8eb3f45f499cc658ab8d10072961e07225e507adb700e93f"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-win_amd64.whl", hash = "sha256:56121965f7a4dc965bff783d70b907ddf3d57f6eba29b6d2e5dabfaf07799c51"},
    {file = "pydantic_core-2.41.5.tar.gz", hash = "sha256:08daa51ea16ad373ffd5e7606252cc32f07bc72b28284b6bc9c6df804816476e"},
]

[package.dependencies]
typing-extensions = ">=4.14.1"

[[package]]
name = "pytest"
version = "7.4.4"
description = "pytest: simple powerful testing with Python"
optional = false
python-versions = ">=3.7"
groups = ["dev"]
files = [
    {file = "pytest-7.4.4-py3-none-any.whl", hash = "sha256:b090cdf5ed60bf4c45261be03239c2c1c22df034fbffe691abe93cd80cea01d8"},
    {file = "pytest-7.4.4.tar.gz", hash = "sha256:2cf0005922c6ace4a3e2ec8b4080eb0d9753fdc93107415332f50ce9e7994280"},
]

[package.dependencies]
colorama = {version = "*", markers = "sys_platform == \"win32\""}
iniconfig = "*"
packaging = "*"
pluggy = ">=0.12,<2.0"

[package.extras]
testing = ["argcomplete", "attrs (>=19.2.0)", "hypothesis (>=3.56)", "mock", "nose", "pygments (>=2.7.2)", "requests", "setuptools", "xmlschema"]

[[package]]
name = "pytest-asyncio"
version = "0.21.2"
description = "Pytest support for asyncio"
optional = false
python-versions = ">=3.7"
groups = ["dev"]
files = [
    {file = "pytest_asyncio-0.21.2-py3-none-any.whl", hash = "sha256:ab664c88bb7998f711d8039cacd4884da6430886ae8bbd4eded552ed2004f16b"},
    {file = "pytest_asyncio-0.21.2.tar.gz", hash = "sha256:d67738fc232b94b326b9d060750beb16e0074210b98dd8b58a5239fa2a154f45"},
]

[package.dependencies]
pytest = ">=7.0.0"

[package.extras]
docs = ["sphinx (>=5.3)", "sphinx-rtd-theme (>=1.0)"]
testing = ["coverage (>=6.2)", "flaky (>=3.5.0)", "hypothesis (>=5.7.1)", "mypy (>=0.931)", "pytest-trio (>=0.7.0)"]

[[package]]
name = "pytest-mock"
version = "3.15.1"
description = "Thin-wrapper around the mock package for easier use with pytest"
optional = false
python-versions = ">=3.9"
groups = ["dev"]
files = [
    {file = "pytest_mock-3.15.1-py3-none-any.whl", hash = "sha256:0a25e2eb88fe5168d535041d09a4529a188176ae608a6d249ee65abc0949630d"},
    {file = "pytest_mock-3.15.1.tar.gz", hash = "sha256:1849a238f6f396da19762269de72cb1814ab44416fa73a8686deac10b0d87a0f"},
]

[package.dependencies]
pytest = ">=6.2.5"

[package.extras]
dev = ["pre-commit", "pytest-asyncio", "tox"]

[[package]]
name = "sniffio"
version = "1.3.1"
description = "Sniff out which async library your code is running under"
optional = false
python-versions = ">=3.7"
groups = ["main"]
files = [
    {file = "sniffio-1.3.1-py3-none-any.whl", hash = "sha256:2f6da418d1f1e0fddd844478f41680e794e6051915791a034ff65e5f100525a2"},
    {file = "sniffio-1.3.1.tar.gz", hash = "sha256:f4324edc670a0f49750a81b895f35c3adb843cca46f0530f79fc1babb23789dc"},
]

[[package]]
name = "typing-extensions"
version = "4.15.0"
description = "Backported and Experimental Type Hints for Python 3.9+"
optional = false
python-versions = ">=3.9"
groups = ["main"]
files = [
    {file = "typing_extensions-4.15.0-py3-none-any.whl", hash = "sha256:f0fa19c6845758ab08074a0cfa8b7aecb71c999ca73d62883bc25cc018c4e548"},
    {file = "typing_extensions-4.15.0.tar.gz", hash = "sha256:0cea48d173cc12fa28ecabc3b837ea3cf6f38c6d1136f85cbaaf598984861466"},
]

[[package]]
name = "typing-inspection"
version = "0.4.2"
description = "Runtime typing introspection tools"
optional = false
python-versions = ">=3.9"
groups = ["main"]
files = [
    {file = "typing_inspection-0.4.2-py3-none-any.whl", hash = "sha256:4ed1cacbdc298c220f1bd249ed5287caa16f34d44ef4e9c3d0cbad5b521545e7"},
    {file = "typing_inspection-0.4.2.tar.gz", hash = "sha256:ba561c48a67c5958007083d386c3295464928b01faa735ab8547c5692e87f464"},
]

[package.dependencies]
typing-extensions = ">=4.12.0"

[metadata]
lock-version = "2.1"
python-versions = "^3.11"
content-hash = "7625bff269edfa5d64c1de8d0b5eb2deab8b59559ca77c91e18a03c75406687c"

```

## File: /home/user/AA1/gateways/ai_gateway/pyproject.toml

```
[tool.poetry]
name = "ai-gateway"
version = "0.1.0"
description = ""
authors = ["InstaPact <oss@instapact.com>"]
readme = "README.md"
packages = [{include = "ai_gateway", from = "."}]


[tool.poetry.dependencies]
python = "^3.11"
pydantic = "^2.5.3"
httpx = "^0.26.0"
backoff = "^2.2.1"


[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.1"
pytest-mock = "^3.12.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

```

## File: /home/user/AA1/gateways/ai_gateway/.pytest_cache/CACHEDIR.TAG

```
Signature: 8a477f597d28d172789f06886806bc55
# This file is a cache directory tag created by pytest.
# For information about cache directory tags, see:
#	https://bford.info/cachedir/spec.html

```

## File: /home/user/AA1/gateways/ai_gateway/.pytest_cache/.gitignore

```
# Created by pytest automatically.
*

```

## File: /home/user/AA1/gateways/ai_gateway/.pytest_cache/README.md

```
# pytest cache directory #

This directory contains data from the pytest's cache plugin,
which provides the `--lf` and `--ff` options, as well as the `cache` fixture.

**Do not** commit this to version control.

See [the docs](https://docs.pytest.org/en/stable/how-to/cache.html) for more information.

```

## File: /home/user/AA1/gateways/ai_gateway/.pytest_cache/v/cache/lastfailed

```
{}
```

## File: /home/user/AA1/gateways/ai_gateway/.pytest_cache/v/cache/nodeids

```
[
  "tests/providers/test_gemini.py::test_call_gemini_auth_error",
  "tests/providers/test_gemini.py::test_call_gemini_client_error",
  "tests/providers/test_gemini.py::test_call_gemini_empty_response_content",
  "tests/providers/test_gemini.py::test_call_gemini_invalid_json_response",
  "tests/providers/test_gemini.py::test_call_gemini_network_error",
  "tests/providers/test_gemini.py::test_call_gemini_rate_limit_error",
  "tests/providers/test_gemini.py::test_call_gemini_success",
  "tests/providers/test_gemini.py::test_call_gemini_timeout_error",
  "tests/providers/test_gemini.py::test_call_gemini_upstream_error",
  "tests/providers/test_gemini.py::test_safe_err_with_empty_response",
  "tests/providers/test_gemini.py::test_safe_err_with_error_json",
  "tests/providers/test_gemini.py::test_safe_err_with_invalid_json",
  "tests/providers/test_gemini.py::test_safe_err_with_other_json",
  "tests/test_client.py::test_client_calls_gemini_provider_correctly",
  "tests/test_client.py::test_client_calls_offline_provider_correctly",
  "tests/test_client.py::test_client_does_not_modify_output",
  "tests/test_client.py::test_client_does_not_modify_prompt",
  "tests/test_client.py::test_client_handles_call_options_override",
  "tests/test_client.py::test_client_initializes_with_provided_config",
  "tests/test_client.py::test_client_loads_config_if_not_provided",
  "tests/test_client.py::test_client_logs_failure_on_exception",
  "tests/test_client.py::test_client_logs_prompt_hash_not_prompt_text",
  "tests/test_client.py::test_client_raises_gateway_config_error_for_missing_gemini_key",
  "tests/test_client.py::test_client_raises_gateway_config_error_for_unknown_provider",
  "tests/test_client.py::test_client_raises_value_error_for_empty_prompt",
  "tests/test_retry.py::test_run_with_retry_exceeds_max_retries",
  "tests/test_retry.py::test_run_with_retry_multiple_retryable_errors",
  "tests/test_retry.py::test_run_with_retry_non_retryable_error",
  "tests/test_retry.py::test_run_with_retry_other_exception_raised_immediately",
  "tests/test_retry.py::test_run_with_retry_success_after_retries",
  "tests/test_retry.py::test_run_with_retry_success_first_attempt",
  "tests/test_retry.py::test_sleep_s_calculation"
]
```

## File: /home/user/AA1/gateways/ai_gateway/.pytest_cache/v/cache/stepwise

```
[]
```

## File: /home/user/AA1/gateways/ai_gateway/README.md

```

```

## File: /home/user/AA1/gateways/ai_gateway/SERVICE_CONTRACT.md

```
# SERVICE_CONTRACT.md  
## AI Gateway â€” LLM Transport & Stability Layer

---

## 1. Purpose

The **AI Gateway** is an infrastructure service that provides **reliable, secure, and provider-agnostic access to Large Language Models (LLMs)**.

It is **plumbing**, not intelligence.

The service exists to:
- accept a fully-formed prompt
- invoke an LLM supplier
- return the modelâ€™s output **unchanged**
- manage operational, security, and supplier complexity

---

## 2. Explicit Non-Goals (Hard Boundary)

The AI Gateway **MUST NOT**:

- interpret prompts
- interpret outputs
- validate or enforce schemas (e.g. JSON)
- correct or â€œrepairâ€ model responses
- apply workflow logic
- encode domain knowledge
- make decisions
- understand ontology, governance, or semantics
- modify prompts or outputs in any way

All meaning, validation, and governance live **outside** this service.

---

## 3. Input Contract

### Required
- `prompt: str`  
  A fully-formed prompt supplied by the caller.

### Optional (transport-level only)
- `provider` (e.g. gemini, openai, offline)
- `model`
- `timeout_seconds`
- `temperature`
- `max_tokens`

The AI Gateway **does not inspect, parse, or alter** the prompt.

---

## 4. Output Contract

### Success
- Returns **exactly the text produced by the model**, unchanged.

### Failure
- Raises a transport-level error or returns an explicit failure.
- Failures are limited to operational concerns:
  - timeouts
  - authentication errors
  - rate limits
  - supplier availability
  - network failures

The service **never rewrites, truncates, or restructures** model output.

---

## 5. Operational Guarantees

### 5.1 Stability
- Enforced request timeouts
- Bounded retries
- Exponential backoff
- Retries only on transient failures:
  - timeouts
  - HTTP 429
  - HTTP 5xx

### 5.2 Determinism
- Low default temperature unless overridden
- No hidden prompt augmentation
- No stateful behavior across calls

---

## 6. Security Guarantees

- API keys loaded only from environment variables
- No prompt logging by default
- No output logging by default
- No secrets written to disk or stdout
- Debug logging must be explicitly enabled and opt-in

---

## 7. Logging & Observability (Operational Only)

The service MAY log:
- timestamp
- provider
- model
- latency
- retry count
- success / failure
- **prompt hash (never prompt text)**

The service MUST NOT log:
- prompt contents
- model outputs
- domain or customer data

---

## 8. Provider & Model Abstraction

The AI Gateway:
- abstracts supplier-specific APIs
- isolates model naming and version churn
- normalizes transport-level errors

Callers must not rely on supplier-specific behavior.

---

## 9. Change Control Rule (Non-Negotiable)

Any change that introduces:
- semantic interpretation
- output validation
- schema enforcement
- task logic
- workflow behavior
- domain awareness

**violates this contract and must be rejected.**

---

## 10. Design Principle (Canonical)

> **This service is dumb on purpose.**  
> **Intelligence lives in the prompt and the caller.**

---

## 11. Intended Longevity

This contract is designed to remain valid across:
- LLM provider changes
- model evolution
- prompt strategies
- ontology workflows
- governance processes

If this contract no longer fits, a **new service** must be created.

```

## File: /home/user/AA1/gateways/ai_gateway/tests/providers/__pycache__/test_gemini.cpython-312-pytest-7.4.4.pyc

```
Ë
:çpi“ãóì—ddlZddlmcmZddlZddlmZm	Z	ddl
Z
ddlmZmZddlmZmZmZmZmZdZdZdZdZej0d	„«Zd
„Zd„Zd„Zd„Zd„Zd„Zd„Z d„Z!d„Z"d„Z#d„Z$d„Z%d„Z&y)éN)ÚMockÚpatch)Úcall_geminiÚ	_safe_err)ÚGatewayAuthErrorÚGatewayClientErrorÚGatewayRateLimitErrorÚGatewayTimeoutErrorÚGatewayUpstreamErrorÚtest_api_keyzgemini-test-modelztest promptg$@c#óK—td«5}|j}||j_|–—ddd«y#1swYyxYw­w)Nzhttpx.Client)rÚreturn_valueÚ	__enter__)Úmock_client_classÚmock_clients  úA/home/user/AA1/gateways/ai_gateway/tests/providers/test_gemini.pyÚmock_httpx_clientrsDèø€ä	ˆ~Ó	ğĞ"3Ø'×4Ñ4ˆà-8ˆ×ÑÔ*ØÒ÷	÷ñüs‚A"9°	A¹A¾Acóx—td¬«}dddddœi|j_d|_t	|«}d}||k(}|sötjd	|fd
||f«dtj«vstjt«rtjt«nddtj«vstj|«rtj|«ndtj|«tj|«dœz}dd|iz}ttj|««‚dx}x}}y)Né©Ústatus_codeÚerrorÚINVALID_ARGUMENTzAPI key not valid.)ÚstatusÚcodeÚmessageúraw textz(INVALID_ARGUMENT 400: API key not valid.©ú==©z0%(py3)s
{%(py3)s = %(py0)s(%(py1)s)
} == %(py6)srÚresp©Úpy0Úpy1Úpy3Úpy6úassert %(py8)sÚpy8©rÚjsonrÚtextrÚ
@pytest_arÚ_call_reprcompareÚ@py_builtinsÚlocalsÚ_should_repr_global_nameÚ	_safereprÚAssertionErrorÚ_format_explanation©r!Ú@py_assert2Ú@py_assert5Ú@py_assert4Ú@py_format7Ú@py_format9s      rÚtest_safe_err_with_error_jsonr:s–€Ü˜CÔ €DØ%Ğ2DÈcĞ^rÑ'sĞt€D‡IIÔØ€D„IßH×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×H×HĞHócóp—td¬«}ddi|j_d|_t	|«}d}||k(}|sötjd|fd||f«d	tj«vstjt«rtjt«nd	d
tj«vstj|«rtj|«nd
tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}}y)NéÈrrÚOKrz{"status": "OK"}rr rr!r"r'r(r)r4s      rÚtest_safe_err_with_other_jsonr?s€Ü˜CÔ €DØ&¨Ğ-€D‡IIÔØ€D„Iß0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0×0Ğ0r;có~—td¬«}td«|j_d|_t|«}d}||k(}|sötjd|fd||f«dtj«vstjt
«rtjt
«nddtj«vstj|«rtj|«ndtj|«tj|«d	œz}d
d|iz}ttj|««‚dx}x}}y)Nr=rúNot JSONrrr rr!r"r'r(©rÚ
ValueErrorr*Úside_effectr+rr,r-r.r/r0r1r2r3r4s      rÚtest_safe_err_with_invalid_jsonrE#s€Ü˜CÔ €DÜ& zÓ2€D‡IIÔØ€D„Iß(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(×(Ğ(r;có~—td¬«}td«|j_d|_t|«}d}||k(}|sötjd|fd||f«dtj«vstjt
«rtjt
«nddtj«vstj|«rtj|«ndtj|«tj|«d	œz}d
d|iz}ttj|««‚dx}x}}y)Nr=rrAÚrr rr!r"r'r(rBr4s      rÚ!test_safe_err_with_empty_responserH)s€Ü˜CÔ €DÜ& zÓ2€D‡IIÔØ€D„Iß × × × × × × × × × × × × × × × × × × × × × × × × × × × × × × × × × Ğ r;có2—td¬«}dddddigiigi|j_||j_t	t
ttt¬«}d}||k(}|s™tjd	|fd
||f«dtj«vstj|«rtj|«ndtj|«dœz}dd|iz}ttj |««‚dx}}|jj#«y)Nr=rÚ
candidatesÚcontentÚpartsr+zExpected Output©ÚpromptÚmodelÚapi_keyÚ	timeout_sr©z%(py0)s == %(py3)sÚresult©r#r%úassert %(py5)sÚpy5)rr*rÚpostrÚMOCK_PROMPTÚ
MOCK_MODELÚMOCK_API_KEYÚMOCK_TIMEOUTr,r-r.r/r0r1r2r3Úassert_called_once©rÚ	mock_resprSr5Ú@py_assert1Ú@py_format4Ú@py_format6s       rÚtest_call_gemini_successrb1s¨€Ü Ô%€Ià˜	 G¨vĞ7HĞ.IĞ-JĞ#KĞLĞMğ#€I‡NNÔğ+4Ğ×ÑÔ'ä¤´:Ä|Ô_kÔl€Fß&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&Õ&Ø×Ñ×-Ñ-Õ/r;có—td¬«}dddii|j_||j_t	j
td¬«5ttttt¬«ddd«y#1swYyxYw)	Ni‘rrrzInvalid API KeyzGemini auth error: HTTP 401©ÚmatchrM)rr*rrWÚpytestÚraisesrrrXrYrZr[©rr^s  rÚtest_call_gemini_auth_errorri<sj€Ü Ô%€IØ#*¨YĞ8IĞ,JĞ"K€I‡NNÔØ*3Ğ×ÑÔ'ä	‰Ô'Ğ/LÔ	MñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúóÁ A7Á7Bcó—td¬«}dddii|j_||j_t	j
td¬«5ttttt¬«ddd«y#1swYyxYw)	Ni­rrrzRate limit exceededzGemini rate limitedrdrM)rr*rrWrfrgr	rrXrYrZr[rhs  rÚ!test_call_gemini_rate_limit_errorrlDsj€Ü Ô%€IØ#*¨YĞ8MĞ,NĞ"O€I‡NNÔØ*3Ğ×ÑÔ'ä	‰Ô,Ğ4IÔ	JñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúrjcó—td¬«}dddii|j_||j_t	j
td¬«5ttttt¬«ddd«y#1swYyxYw)	NrrrrzBad RequestzGemini client error HTTP 400rdrM)rr*rrWrfrgrrrXrYrZr[rhs  rÚtest_call_gemini_client_errorrnLsi€Ü Ô%€IØ#*¨Y¸Ğ,FĞ"G€I‡NNÔØ*3Ğ×ÑÔ'ä	‰Ô)Ğ1OÔ	PñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúrjcó—td¬«}dddii|j_||j_t	j
td¬«5ttttt¬«ddd«y#1swYyxYw)	NiôrrrzInternal Server ErrorzGemini upstream error HTTP 500rdrM)rr*rrWrfrgrrrXrYrZr[rhs  rÚtest_call_gemini_upstream_errorrpTsj€Ü Ô%€IØ#*¨YĞ8OĞ,PĞ"Q€I‡NNÔØ*3Ğ×ÑÔ'ä	‰Ô+Ğ3SÔ	TñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúrjcóê—tjd«|j_t	j
td¬«5ttttt¬«ddd«y#1swYyxYw)NÚTimeoutzGemini timeoutrdrM)ÚhttpxÚReadTimeoutrWrDrfrgr
rrXrYrZr[©rs rÚtest_call_gemini_timeout_errorrv\sT€Ü).×):Ñ):¸9Ó)EĞ×ÑÔ&ä	‰Ô*Ğ2BÔ	CñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúsÁ A)Á)A2có—tjdtjdd«¬«|j_tjtd¬«5ttttt¬«ddd«y#1swYyxYw)NzNetwork errorÚGETzhttp://test.com)ÚrequestzGemini request errorrdrM)rsÚRequestErrorÚRequestrWrDrfrgrrrXrYrZr[rus rÚtest_call_gemini_network_errorr|bsf€Ü).×);Ñ);¸OÔUZ×UbÑUbĞchĞj{ÓU|Ô)}Ğ×ÑÔ&ä	‰Ô+Ğ3IÔ	JñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúsÁ A?Á?Bcó—td¬«}td«|j_||j_tjtd¬«5ttttt¬«ddd«y#1swYyxYw)Nr=rrAz!Gemini returned non-JSON responserdrM)rrCr*rDrWrrfrgrrrXrYrZr[rhs  rÚ&test_call_gemini_invalid_json_responser~hsd€Ü Ô%€IÜ!+¨JÓ!7€I‡NNÔØ*3Ğ×ÑÔ'ä	‰Ô+Ğ3VÔ	WñhÜœ;¬jÄ,ÔZfÕg÷h÷hñhúsÁ A<Á<Bcó—td¬«}dddddigiiddigiidiiigi|j_||j_t	t
ttt¬«}d}||k(}|s™tjd	|fd
||f«dtj«vstj|«rtj|«ndtj|«dœz}dd|iz}ttj |««‚dx}}y)Nr=rrJrKrLr+rMrGrrRrSrTrUrV)rr*rrWrrXrYrZr[r,r-r.r/r0r1r2r3r]s       rÚ'test_call_gemini_empty_response_contentr€ps±€Ü Ô%€Iğ	Ø˜ F¨D >Ğ"2Ğ3Ğ4Ø˜ 2 $˜Ğ(Ø˜ˆOØğ	
ğ#€I‡NNÔğ+4Ğ×ÑÔ'ä¤´:Ä|Ô_kÔl€Fß×××××××××××××××××××Ör;)'Úbuiltinsr.Ú_pytest.assertion.rewriteÚ	assertionÚrewriter,rfÚunittest.mockrrrsÚai_gateway.providers.geminirrÚai_gateway.errorsrrr	r
rrZrYrXr[Úfixturerr:r?rErHrbrirlrnrprvr|r~r€©r;rú<module>rŠs–ğß„ƒß%Ûç>÷EõEğ€Ø €
Ø€Ø€à‡ñóğòIò1ò)ò!ò	0òhòhòhòhòhòhòhór;
```

## File: /home/user/AA1/gateways/ai_gateway/tests/providers/test_gemini.py

```
import pytest
from unittest.mock import Mock, patch
import httpx

from ai_gateway.providers.gemini import call_gemini, _safe_err
from ai_gateway.errors import GatewayAuthError, GatewayClientError, GatewayRateLimitError, GatewayTimeoutError, GatewayUpstreamError

# Mock configuration
MOCK_API_KEY = "test_api_key"
MOCK_MODEL = "gemini-test-model"
MOCK_PROMPT = "test prompt"
MOCK_TIMEOUT = 10.0

@pytest.fixture
def mock_httpx_client():
    with patch("httpx.Client") as mock_client_class:
        mock_client = mock_client_class.return_value
        # Critical line: what the `with` block binds to as `client`
        mock_client.__enter__.return_value = mock_client
        yield mock_client

# --- Test _safe_err function ---
def test_safe_err_with_error_json():
    resp = Mock(status_code=400) # Simple Mock for _safe_err
    resp.json.return_value = {"error": {"status": "INVALID_ARGUMENT", "code": 400, "message": "API key not valid."}}
    resp.text = "raw text"
    assert _safe_err(resp) == "INVALID_ARGUMENT 400: API key not valid."

def test_safe_err_with_other_json():
    resp = Mock(status_code=200) # Simple Mock for _safe_err
    resp.json.return_value = {"status": "OK"}
    resp.text = "raw text"
    assert _safe_err(resp) == '{"status": "OK"}'

def test_safe_err_with_invalid_json():
    resp = Mock(status_code=200) # Simple Mock for _safe_err
    resp.json.side_effect = ValueError("Not JSON")
    resp.text = "raw text"
    assert _safe_err(resp) == "raw text"

def test_safe_err_with_empty_response():
    resp = Mock(status_code=200) # Simple Mock for _safe_err
    resp.json.side_effect = ValueError("Not JSON")
    resp.text = None
    assert _safe_err(resp) == ""

# --- Test call_gemini function ---

def test_call_gemini_success(mock_httpx_client):
    mock_resp = Mock(status_code=200)
    mock_resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Expected Output"}]}}]
    }
    mock_httpx_client.post.return_value = mock_resp

    result = call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)
    assert result == "Expected Output"
    mock_httpx_client.post.assert_called_once()
    
def test_call_gemini_auth_error(mock_httpx_client):
    mock_resp = Mock(status_code=401)
    mock_resp.json.return_value = {"error": {"message": "Invalid API Key"}}
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayAuthError, match="Gemini auth error: HTTP 401"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_rate_limit_error(mock_httpx_client):
    mock_resp = Mock(status_code=429)
    mock_resp.json.return_value = {"error": {"message": "Rate limit exceeded"}}
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayRateLimitError, match="Gemini rate limited"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_client_error(mock_httpx_client):
    mock_resp = Mock(status_code=400)
    mock_resp.json.return_value = {"error": {"message": "Bad Request"}}
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayClientError, match="Gemini client error HTTP 400"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_upstream_error(mock_httpx_client):
    mock_resp = Mock(status_code=500)
    mock_resp.json.return_value = {"error": {"message": "Internal Server Error"}}
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayUpstreamError, match="Gemini upstream error HTTP 500"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_timeout_error(mock_httpx_client):
    mock_httpx_client.post.side_effect = httpx.ReadTimeout("Timeout")

    with pytest.raises(GatewayTimeoutError, match="Gemini timeout"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_network_error(mock_httpx_client):
    mock_httpx_client.post.side_effect = httpx.RequestError("Network error", request=httpx.Request("GET", "http://test.com"))

    with pytest.raises(GatewayUpstreamError, match="Gemini request error"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_invalid_json_response(mock_httpx_client):
    mock_resp = Mock(status_code=200)
    mock_resp.json.side_effect = ValueError("Not JSON")
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayUpstreamError, match="Gemini returned non-JSON response"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_empty_response_content(mock_httpx_client):
    mock_resp = Mock(status_code=200)
    # Simulate various empty/missing parts in the JSON response
    mock_resp.json.return_value = {
        "candidates": [
            {"content": {"parts": [{"text": None}]}},
            {"content": {"parts": [{}]}},
            {"content": {}},
            {},
        ]
    }
    mock_httpx_client.post.return_value = mock_resp

    result = call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)
    assert result == "" # Should return empty string if content is missing or None
```

## File: /home/user/AA1/gateways/ai_gateway/tests/__pycache__/test_client.cpython-312-pytest-7.4.4.pyc

```
Ë
æpiL!ãó4—ddlZddlmcmZddlZddlmZm	Z	m
Z
ddlZddlmZmZddlmZddlmZmZmZej*d„«Zej*d„«Zej*d¬	«d
„«Zd„Zd„Zd„Zd„Zd„Zd„Zd„Zd„Z d„Z!d„Z"d„Z#d„Z$y)éN)ÚMockÚpatchÚcall)ÚAIGatewayClientÚCallOptions©ÚGatewayConfig)ÚGatewayConfigErrorÚGatewayAuthErrorÚAIGatewayErrorc
ó(—tdddddddd¬«S)	NÚgeminiúgemini-test-modelç$@éçğ?g4@ÚTEST_GEMINI_KEY©ÚproviderÚmodelÚ	timeout_sÚmax_retriesÚbackoff_base_sÚbackoff_max_sÚgemini_api_keyÚopenai_api_keyr©óú7/home/user/AA1/gateways/ai_gateway/tests/test_client.pyÚmock_configr 
s'€äØØ!ØØØØØ(Øô	ğ	rcó—t|¬«S)N©Úcfg)r)r s rÚclientr$s€ä˜{Ô+Ğ+rT)Úautousecóö—|jd«}|jdd¬«}|jdd„¬«}|jdd	¬«}|jd
d¬«}|jd|¬«}||||||dœS)Nzai_gateway.client.log_eventzai_gateway.client.prompt_hash8ÚTESTHASH)Úreturn_valuezai_gateway.retry.run_with_retrycó—|«S)Nr)ÚfnÚpolicys  rú<lambda>z#mock_dependencies.<locals>.<lambda> s
€ÑikÓim€r)Úside_effectzai_gateway.client.call_geminiÚMODEL_OUTPUT_OKzai_gateway.client.call_offlineÚzai_gateway.client.load_config)Ú	log_eventÚprompt_hash8Úrun_with_retryÚcall_geminiÚcall_offlineÚload_config)r)Úmockerr Úlog_event_mockÚprompt_hash8_mockÚrun_with_retry_mockÚcall_gemini_mockÚcall_offline_mockÚload_config_mocks        rÚmock_dependenciesr=sœ€ğ—\‘\Ğ"?Ó@€NØŸ™Ğ%EĞT^˜Ó_ĞØ Ÿ,™,Ğ'HÑVm˜,ÓnĞğ—|‘|Ğ$CĞRc|ÓdĞØŸ™Ğ%EĞTV˜ÓWĞØ—|‘|Ğ$CĞR]|Ó^Ğğ$Ø)Ø-Ø'Ø)Ø'ñğrcóè—d}d}|j|«|dj||djj|djj|djj
¬«y)Nz"Return exactly: This is my prompt.r.r3r5)ÚpromptrÚapi_keyr)rÚassert_called_once_withr(rrr)r$r=Úoriginal_promptÚexpected_outputs    rÚ"test_client_does_not_modify_promptrD3sq€Ø:€OØ'€Oà
‡KKÔ ğmÑ$×<Ñ<ØØ Ñ.×;Ñ;×AÑAØ! -Ñ0×=Ñ=×LÑLØ# MÑ2×?Ñ?×IÑIğ	=õrcór—|jd«}d}||k(}|s™tjd|fd||f«dtj«vstj
|«rtj|«ndtj|«dœz}dd|iz}ttj|««‚dx}}y)	Nz
any promptr.©ú==)z%(py0)s == %(py3)sÚoutput)Úpy0Úpy3zassert %(py5)sÚpy5)	rÚ
@pytest_arÚ_call_reprcompareÚ@py_builtinsÚlocalsÚ_should_repr_global_nameÚ	_safereprÚAssertionErrorÚ_format_explanation)r$r=rHÚ@py_assert2Ú@py_assert1Ú@py_format4Ú@py_format6s       rÚ"test_client_does_not_modify_outputrXAsQ€ğ[‰[˜Ó&€Fß&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&Ö&rcóò—d}|j|«|djddddd¬«|djd	dd|jd¬
«|djD]}|\}}|j}|«}||v}	|	sîtjd|	fd||f«dtj«vstj|«rtj|«nddtj«vstj|«rtj|«ndtj|«tj|«dœz}
dd|
iz}ttj|««‚dx}	x}}Œy)NzSensitive prompt contentr0zai_gateway.call.startrrrr')rrrr1zai_gateway.call.ok)rrÚ
latency_msr1)únot in)zI%(py0)s not in %(py6)s
{%(py6)s = %(py4)s
{%(py4)s = %(py2)s.values
}()
}r?Úkwargs)rIÚpy2Úpy4Úpy6zassert %(py8)sÚpy8)rÚassert_any_callÚANYÚcall_args_listÚvaluesrLrMrNrOrPrQrRrS)r$r=r6r?Ú	call_argsÚargsr\Ú@py_assert3Ú@py_assert5rUÚ@py_format7Ú@py_format9s            rÚ,test_client_logs_prompt_hash_not_prompt_textrkGsô€Ø'€FØ
‡KKÔğkÑ"×2Ñ2ØØØ!ØØğ3ôğkÑ"×2Ñ2ØØØ!Ø—:‘:Øğ3ôğ' {Ñ3×BÑBó-ˆ	Ø ‰ˆˆfç,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,×,Ö,ñ-rc
ó"—tdddddddd¬«}t|¬«}|j}||u}|sÚtjd|fd	||f«d
tj«vstj|«rtj|«nd
tj|«dtj«vstj|«rtj|«nddœz}dd|iz}ttj|««‚dx}}y)NÚofflineztest-offlineç@rçrr")Úis)z+%(py2)s
{%(py2)s = %(py0)s.cfg
} is %(py4)sr$Úcustom_config)rIr]r^zassert %(py6)sr_)r	rr#rLrMrNrOrPrQrRrS)rqr$rUrgÚ@py_format5ris      rÚ,test_client_initializes_with_provided_configrsfs€Ü!ØØØØØØØØô	€Mô Ô/€Fß&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&Ğ&rc
óL—tdddddddd¬«}||d_t«}|dj«|j}|j
}d}||k(}|sÁtjd|fd||f«d	tj«vstj|«rtj|«nd	tj|«tj|«tj|«d
œz}dd|iz}	ttj|	««‚dx}x}x}}y)NÚdefaultrrrorr5rF)zI%(py4)s
{%(py4)s = %(py2)s
{%(py2)s = %(py0)s.cfg
}.provider
} == %(py7)sr$)rIr]r^Úpy7zassert %(py9)sÚpy9)r	r(rÚassert_called_oncer#rrLrMrNrOrPrQrRrS)
r6r=Útest_configr$rUrgÚ@py_assert6rhÚ@py_format8Ú@py_format10s
          rÚ(test_client_loads_config_if_not_providedr}ts¥€äØ )°sÈØ¨#¸dĞSWô€Kğ5@ĞmÑ$Ô1ôÓ€FØmÑ$×7Ñ7Ô9ß+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+×+Ò+rcóL—|jd«|dj«y)Nútest promptr3)rrx)r$r=s  rÚ+test_client_calls_gemini_provider_correctlyr€s€Ø
‡KKÔØmÑ$×7Ñ7Õ9rcóÀ—tdii|j¥ddi¥¤}t|¬«}|jd«|dj	«|dj«y)Nrrmr"rr4r3r)r	Ú__dict__rrrxÚassert_not_called)r r=Úoffline_configr$s    rÚ,test_client_calls_offline_provider_correctlyr……sZ€ä"ÑUĞ%T¨×(<Ñ(<Ğ%T¸jÈ)Ñ%TÑU€NÜ Ô0€FØ
‡KKÔØnÑ%×8Ñ8Ô:ØmÑ$×6Ñ6Õ8rcóæ—tdii|j¥ddi¥¤}t|¬«}tdd¬«}|j	d|¬«|d	jdd
d¬«|dj«y)Nrrr"rmrn)rrr)Úoptionsr4r)r?rrr3r)r	r‚rrrrArƒ)r r=Úbase_configr$r‡s     rÚ)test_client_handles_call_options_overrider‰s}€äÑQĞ"P [×%9Ñ%9Ğ"P¸:ÀxÑ"PÑQ€KÜ Ô-€Fä 9¸Ô<€GØ
‡KK w€KÔ/ğnÑ%×=Ñ=ØĞ$7À3ğ>ôğmÑ$×6Ñ6Õ8rcóŠ—tjtd¬«5|jd«ddd«tjtd¬«5|jd«ddd«tjtd¬«5|jd«ddd«y#1swYŒtxYw#1swYŒKxYw#1swYyxYw)Nz!prompt must be a non-empty string©Úmatchr/z   )ÚpytestÚraisesÚ
ValueErrorr)r$s rÚ/test_client_raises_value_error_for_empty_promptrœs–€Ü	‰”zĞ)LÔ	MñØ‰BŒ÷ä	‰”zĞ)LÔ	MñØ‰EÔ÷ä	‰”zĞ)LÔ	MñØ‰DÔ÷ğ÷	ğú÷ğú÷ğús#œB!ÁB-ÂB9Â!B*Â-B6Â9Ccóä—tdii|j¥ddi¥¤}||d_t«}t	j
td¬«5|jd«ddd«y#1swYyxYw)Nrr5zMissing GEMINI_API_KEYr‹rr©r	r‚r(rrrr
r)r6r=r Úmock_config_no_keyr$s     rÚ>test_client_raises_gateway_config_error_for_missing_gemini_keyr”¤sl€ä&ÑZĞ)Y¨K×,@Ñ,@Ğ)YĞBRĞTXÑ)YÑZĞØ4FĞmÑ$Ô1äÓ€Fä	‰Ô)Ğ1IÔ	Jñ#Ø‰MÔ"÷#÷#ñ#úsÁA&Á&A/cóæ—tdii|j¥dddœ¥¤}||d_t«}t	j
td¬«5|jd«ddd«y#1swYyxYw)	NÚunknownÚVALID_KEY_FOR_TEST)rrr5zUnknown provider: unknownr‹rrr’)r6r=r Úmock_config_unknown_providerr$s     rÚ<test_client_raises_gateway_config_error_for_unknown_providerr™®sz€ä#0ñ$ğ4Ø
×
Ñ
ğ4àØ.ò4ñ$Ğ ğ
5QĞmÑ$Ô1äÓ€Fä	‰Ô)Ğ1LÔ	Mñ#Ø‰MÔ"÷#÷#ñ#úsÁA'Á'A0cóğ—td«|d_tjt«5|j	d«ddd«|djddd|jdd	¬
«y#1swYŒ.xYw)Nz	auth failr3rr0zai_gateway.call.failrrr'r)rrrZr1Ú
error_type)rr-rrrÚassert_called_withrb)r$r=r6s   rÚ%test_client_logs_failure_on_exceptionr¼ss€Ü3CÀKÓ3PĞmÑ$Ô0ä	‰Ô'Ó	(ñ#Ø‰MÔ"÷#ğkÑ"×5Ñ5ØØØ!Ø—:‘:ØØ%ğ6õ÷#ğ#ús­A,Á,A5)%ÚbuiltinsrNÚ_pytest.assertion.rewriteÚ	assertionÚrewriterLrÚunittest.mockrrrÚosÚai_gateway.clientrrÚai_gateway.configr	Úai_gateway.errorsr
rrÚfixturer r$r=rDrXrkrsr}r€r…r‰rr”r™rrrrú<module>r¨s¬ğß„ƒß+Ñ+Û	ç:İ+ßRÑRğ‡ñ
óğ
ğ‡ñ,óğ,ğ€‡˜Ôñóğò.ò'ò-ò>'ò,ò:ò9ò9òò#ò#ór
```

## File: /home/user/AA1/gateways/ai_gateway/tests/__pycache__/test_retry.cpython-312-pytest-7.4.4.pyc

```
Ë
eãpilãó˜—ddlZddlmcmZddlZddlmZm	Z	ddl
Z
ddlmZmZmZddlmZmZmZmZmZd„Zd„Zd„Zd„Zd	„Zd
„Zd„Zy)éN)ÚMockÚcall)ÚRetryPolicyÚrun_with_retryÚ_sleep_s)ÚGatewayTimeoutErrorÚGatewayRateLimitErrorÚGatewayUpstreamErrorÚGatewayClientErrorÚGatewayAuthErrorcó¸—td¬«}td¬«}t||«}d}||k(}|s™tjd|fd||f«dtj«vstj|«rtj|«ndtj|«dœz}d	d
|iz}ttj|««‚dx}}|j«y)NÚsuccess©Úreturn_valueé©Úmax_retries©ú==©z%(py0)s == %(py3)sÚresult©Úpy0Úpy3úassert %(py5)sÚpy5)rrrÚ
@pytest_arÚ_call_reprcompareÚ@py_builtinsÚlocalsÚ_should_repr_global_nameÚ	_safereprÚAssertionErrorÚ_format_explanationÚassert_called_once)Úmock_fnÚpolicyrÚ@py_assert2Ú@py_assert1Ú@py_format4Ú@py_format6s       ú6/home/user/AA1/gateways/ai_gateway/tests/test_retry.pyÚ)test_run_with_retry_success_first_attemptr-sm€ä 	Ô*€GÜ QÔ'€FÜ˜G VÓ,€Fß×××××××××××××××××××ÕØ×ÑÕ ócóä—ttd«td«dg¬«}tdd¬«}|j	d«t||«}d}||k(}|s™tjd	|fd
||f«dtj«vstj|«rtj|«ndtj|«dœz}dd|iz}ttj|««‚dx}}|j}d}||k(}	|	s­tjd	|	fd||f«dtj«vstj|«rtj|«ndtj|«tj|«dœz}dd|iz}
ttj|
««‚dx}x}	}tj }|j"}	|	s•ddtj«vstjt«rtjt«ndtj|«tj|	«dœz}ttj|««‚dx}}	y)NÚtimeoutÚupstreamr©Úside_effectrç{®Gáz„?©rÚbackoff_base_sú
time.sleeprrrrrr©z2%(py2)s
{%(py2)s = %(py0)s.call_count
} == %(py5)sr&©rÚpy2rúassert %(py7)sÚpy7zEassert %(py4)s
{%(py4)s = %(py2)s
{%(py2)s = %(py0)s.sleep
}.called
}Útime)rr:Úpy4)rrr
rÚpatchrrrrr r!r"r#r$Ú
call_countr=ÚsleepÚcalled)Úmockerr&r'rr(r)r*r+Ú@py_assert4Ú@py_assert3Ú@py_format8Ú@py_format5s            r,Ú)test_run_with_retry_success_after_retriesrHs€äÔ 3°IÓ >Ô@TĞU_Ó@`ĞbkĞlÔm€GÜ Q°tÔ<€FØ
‡LLÔä˜G VÓ,€Fß×××××××××××××××××××Õß"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"ß××××××××××××××××××××××r.cón—ttd«¬«}tdd¬«}|jd«t	j
t«5t||«ddd«|j}d}||k(}|s­tjd|fd	||f«d
tj«vstj|«rtj|«nd
tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}}y#1swYŒÒxYw)Nr0r2ér4r5r7rrr8r&r9r;r<)rrrr?ÚpytestÚraisesrr@rrrr r!r"r#r$)rCr&r'r)rDrEr+rFs        r,Ú'test_run_with_retry_exceeds_max_retriesrMs¤€äÔ2°9Ó=Ô>€GÜ Q°tÔ<€FØ
‡LLÔä	‰Ô*Ó	+ñ(Üw Ô'÷(ç"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"Ğ"÷(ğ(úsÁD+Ä+D4cóÚ—ttd«¬«}td¬«}tjt«5t||«ddd«|j«y#1swYŒxYw)Nzbad requestr2rr)rrrrKrLrr%©r&r's  r,Ú'test_run_with_retry_non_retryable_errorrP%sT€äÔ1°-Ó@ÔA€GÜ QÔ'€Fä	‰Ô)Ó	*ñ(Üw Ô'÷(à×ÑÕ ÷(ğ(úó»A!Á!A*cóÚ—ttd«¬«}td¬«}tjt«5t||«ddd«|j«y#1swYŒxYw)NÚ
unexpectedr2rr)rÚ
ValueErrorrrKrLrr%rOs  r,Ú6test_run_with_retry_other_exception_raised_immediatelyrU.sR€äœz¨,Ó7Ô8€GÜ QÔ'€Fä	‰”zÓ	"ñ(Üw Ô'÷(à×ÑÕ ÷(ğ(úrQcóv—ttd«td«dg¬«}tdd¬«}|j	d«t||«}d}||k(}|s™tjd	|fd
||f«dtj«vstj|«rtj|«ndtj|«dœz}dd|iz}ttj|««‚dx}}|j}d}||k(}	|	s­tjd	|	fd||f«dtj«vstj|«rtj|«ndtj|«tj|«dœz}dd|iz}
ttj|
««‚dx}x}	}y)Nzrate limitedr0zfinally successr2rJr4r5r7rrrrrrrr8r&r9r;r<)rr	rrr?rrrrr r!r"r#r$r@)rCr&r'rr(r)r*r+rDrErFs           r,Ú-test_run_with_retry_multiple_retryable_errorsrW7sÒ€äÔ 5°nÓ EÔGZĞ[dÓGeĞgxĞyÔz€GÜ Q°tÔ<€FØ
‡LLÔä˜G VÓ,€Fß&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&Õ&ß"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"×"Ğ"r.cóè—tdd¬«}|jdd¬«d}t||«}d}||k(}|s
tjd|fd||f«d	tj«vstjt«rtjt«nd	d
tj«vstj|«rtj|«nd
tj|«tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}x}}d}t||«}d}||k(}|s
tjd|fd||f«d	tj«vstjt«rtjt«nd	d
tj«vstj|«rtj|«nd
tj|«tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}x}}d}t||«}d}||k(}|s
tjd|fd||f«d	tj«vstjt«rtjt«nd	d
tj«vstj|«rtj|«nd
tj|«tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}x}}d}t||«}d}||k(}|s
tjd|fd||f«d	tj«vstjt«rtjt«nd	d
tj«vstj|«rtj|«nd
tj|«tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}x}}d}t||«}d}||k(}|s
tjd|fd||f«d	tj«vstjt«rtjt«nd	d
tj«vstj|«rtj|«nd
tj|«tj|«tj|«dœz}dd|iz}ttj|««‚dx}x}x}}y)Ngğ?g$@)r6Úbackoff_max_szrandom.uniformrrr)z9%(py5)s
{%(py5)s = %(py0)s(%(py1)s, %(py3)s)
} == %(py8)srr')rÚpy1rrÚpy8zassert %(py10)sÚpy10ég@rJg@rg @é)rr?rrrrr r!r"r#r$)rCr'r(rDÚ@py_assert7Ú@py_assert6Ú@py_format9Ú@py_format11s        r,Útest_sleep_s_calculationrcAsc€ä¨¸4Ô@€FØ
‡LLĞ!°€LÔ2÷&×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%Ñ%÷&×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%Ñ%÷&×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%Ñ%÷&×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%×%Ñ%÷'×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&×&Ò&r.)ÚbuiltinsrÚ_pytest.assertion.rewriteÚ	assertionÚrewriterrKÚunittest.mockrrr=Úai_gateway.retryrrrÚai_gateway.errorsrr	r
rrr-rHrMrPrUrWrc©r.r,ú<module>rlsGğß„ƒß$ÛçBÑB÷EõEò!ò	ò#ò!ò!ò#ó'r.
```

## File: /home/user/AA1/gateways/ai_gateway/tests/test_client.py

```
import pytest
from unittest.mock import Mock, patch, call
import os

from ai_gateway.client import AIGatewayClient, CallOptions
from ai_gateway.config import GatewayConfig
from ai_gateway.errors import GatewayConfigError, GatewayAuthError, AIGatewayError

# Fixtures for common objects
@pytest.fixture
def mock_config():
    return GatewayConfig(
        provider="gemini",
        model="gemini-test-model",
        timeout_s=10.0,
        max_retries=1,
        backoff_base_s=1.0,
        backoff_max_s=20.0,
        gemini_api_key="TEST_GEMINI_KEY",
        openai_api_key=None,
    )

@pytest.fixture
def client(mock_config):
    return AIGatewayClient(cfg=mock_config)

@pytest.fixture(autouse=True)
def mock_dependencies(mocker, mock_config): # Added mock_config here
    # Patch modules as they are imported within client.py
    log_event_mock = mocker.patch('ai_gateway.client.log_event')
    prompt_hash8_mock = mocker.patch('ai_gateway.client.prompt_hash8', return_value="TESTHASH")
    run_with_retry_mock = mocker.patch('ai_gateway.retry.run_with_retry', side_effect=lambda fn, policy: fn()) # Execute fn immediately

    # Patch modules as they are imported within client.py
    call_gemini_mock = mocker.patch('ai_gateway.client.call_gemini', return_value="MODEL_OUTPUT_OK")
    call_offline_mock = mocker.patch('ai_gateway.client.call_offline', return_value="")
    load_config_mock = mocker.patch('ai_gateway.client.load_config', return_value=mock_config) # Patch where client.py looks for it

    # Return a dict of mocks for easier access in tests
    return {
        "log_event": log_event_mock,
        "prompt_hash8": prompt_hash8_mock,
        "run_with_retry": run_with_retry_mock,
        "call_gemini": call_gemini_mock,
        "call_offline": call_offline_mock,
        "load_config": load_config_mock,
    }

# --- Tests for Data Integrity and Privacy ---

def test_client_does_not_modify_prompt(client, mock_dependencies):
    original_prompt = "Return exactly: This is my prompt."
    expected_output = "MODEL_OUTPUT_OK"
    
    client.call(original_prompt)
    
    # Verify that call_gemini received the original prompt
    mock_dependencies["call_gemini"].assert_called_once_with(
        prompt=original_prompt,
        model=mock_dependencies["load_config"].return_value.model, # Get model from mocked config
        api_key=mock_dependencies["load_config"].return_value.gemini_api_key, # Get API key from mocked config
        timeout_s=mock_dependencies["load_config"].return_value.timeout_s, # Get timeout from mocked config
    )

def test_client_does_not_modify_output(client, mock_dependencies):
    # The mock for call_gemini already ensures a fixed output.
    # The test here is to ensure AIGatewayClient returns it as-is.
    output = client.call("any prompt")
    assert output == "MODEL_OUTPUT_OK"
    
def test_client_logs_prompt_hash_not_prompt_text(client, mock_dependencies, mocker):
    prompt = "Sensitive prompt content"
    client.call(prompt)
    
    # Check log_event calls for 'prompt_hash8'
    mock_dependencies["log_event"].assert_any_call(
        "ai_gateway.call.start",
        provider="gemini",
        model="gemini-test-model",
        timeout_s=10.0,
        prompt_hash8="TESTHASH",
    )
    mock_dependencies["log_event"].assert_any_call(
        "ai_gateway.call.ok",
        provider="gemini",
        model="gemini-test-model",
        latency_ms=mocker.ANY, # Use mocker.ANY for dynamic values
        prompt_hash8="TESTHASH",
    )
    # Ensure no calls directly include the original prompt text
    for call_args in mock_dependencies["log_event"].call_args_list:
        args, kwargs = call_args
        # Check kwargs first, then args if needed, but for named args, kwargs is sufficient
        assert prompt not in kwargs.values()
        # For positional args if any might contain prompt
        # for arg in args:
        #     assert prompt not in str(arg)


# --- Tests for core client behavior ---

def test_client_initializes_with_provided_config():
    custom_config = GatewayConfig(
        provider="offline",
        model="test-offline",
        timeout_s=5.0,
        max_retries=0,
        backoff_base_s=0.0,
        backoff_max_s=0.0,
        gemini_api_key=None,
        openai_api_key=None,
    )
    client = AIGatewayClient(cfg=custom_config)
    assert client.cfg is custom_config

def test_client_loads_config_if_not_provided(mocker, mock_dependencies):
    # Ensure load_config is mocked out and returns a known config
    test_config = GatewayConfig(
        provider="default", model="default", timeout_s=1.0, max_retries=0,
        backoff_base_s=0.0, backoff_max_s=0.0, gemini_api_key=None, openai_api_key=None
    )
    mock_dependencies["load_config"].return_value = test_config # Set return value for the mock
    
    # Create client without passing config, so it calls load_config
    client = AIGatewayClient() 
    mock_dependencies["load_config"].assert_called_once()
    assert client.cfg.provider == "default"

def test_client_calls_gemini_provider_correctly(client, mock_dependencies):
    client.call("test prompt")
    mock_dependencies["call_gemini"].assert_called_once()

def test_client_calls_offline_provider_correctly(mock_config, mock_dependencies):
    # Create a new client with a config that explicitly sets the provider to offline
    offline_config = GatewayConfig(**{**mock_config.__dict__, "provider": "offline"})
    client = AIGatewayClient(cfg=offline_config)
    client.call("test prompt")
    mock_dependencies["call_offline"].assert_called_once()
    mock_dependencies["call_gemini"].assert_not_called()

def test_client_handles_call_options_override(mock_config, mock_dependencies):
    # Ensure base config is gemini so we can override it
    base_config = GatewayConfig(**{**mock_config.__dict__, "provider": "gemini"})
    client = AIGatewayClient(cfg=base_config)
    
    options = CallOptions(provider="offline", timeout_s=5.0)
    client.call("test prompt", options=options)
    
    # Ensure offline was called with overridden timeout
    mock_dependencies["call_offline"].assert_called_once_with(
        prompt="test prompt", model="gemini-test-model", timeout_s=5.0 # Model from config, not overridden
    )
    mock_dependencies["call_gemini"].assert_not_called()


def test_client_raises_value_error_for_empty_prompt(client):
    with pytest.raises(ValueError, match="prompt must be a non-empty string"):
        client.call("")
    with pytest.raises(ValueError, match="prompt must be a non-empty string"):
        client.call("   ")
    with pytest.raises(ValueError, match="prompt must be a non-empty string"):
        client.call(None) # type: ignore

def test_client_raises_gateway_config_error_for_missing_gemini_key(mocker, mock_dependencies, mock_config):
    # Create a new config with missing API key
    mock_config_no_key = GatewayConfig(**{**mock_config.__dict__, "gemini_api_key": None})
    mock_dependencies["load_config"].return_value = mock_config_no_key # Ensure this is the config loaded
    
    client = AIGatewayClient() # Client will load the mocked config
    
    with pytest.raises(GatewayConfigError, match="Missing GEMINI_API_KEY"):
        client.call("test prompt")

def test_client_raises_gateway_config_error_for_unknown_provider(mocker, mock_dependencies, mock_config):
    # Create a new config with an unknown provider and a valid gemini key to reach the "unknown provider" check
    mock_config_unknown_provider = GatewayConfig(**{
        **mock_config.__dict__,
        "provider": "unknown",
        "gemini_api_key": "VALID_KEY_FOR_TEST" # Ensure API key is present so it doesn't fail on missing key first
    })
    mock_dependencies["load_config"].return_value = mock_config_unknown_provider # Ensure this is the config loaded
    
    client = AIGatewayClient() # Client will load the mocked config
    
    with pytest.raises(GatewayConfigError, match="Unknown provider: unknown"):
        client.call("test prompt")

def test_client_logs_failure_on_exception(client, mock_dependencies, mocker):
    mock_dependencies["call_gemini"].side_effect = GatewayAuthError("auth fail")
    
    with pytest.raises(GatewayAuthError):
        client.call("test prompt")
    
    mock_dependencies["log_event"].assert_called_with(
        "ai_gateway.call.fail",
        provider="gemini",
        model="gemini-test-model",
        latency_ms=mocker.ANY,
        prompt_hash8="TESTHASH",
        error_type="GatewayAuthError",
    )

```

## File: /home/user/AA1/gateways/ai_gateway/tests/test_retry.py

```
import pytest
from unittest.mock import Mock, call
import time

from ai_gateway.retry import RetryPolicy, run_with_retry, _sleep_s # Import _sleep_s directly
from ai_gateway.errors import GatewayTimeoutError, GatewayRateLimitError, GatewayUpstreamError, GatewayClientError, GatewayAuthError

def test_run_with_retry_success_first_attempt():
    # Test that a successful function call returns immediately
    mock_fn = Mock(return_value="success")
    policy = RetryPolicy(max_retries=3)
    result = run_with_retry(mock_fn, policy)
    assert result == "success"
    mock_fn.assert_called_once()

def test_run_with_retry_success_after_retries(mocker): # Added mocker
    # Test that a function succeeds after a few retries
    mock_fn = Mock(side_effect=[GatewayTimeoutError("timeout"), GatewayUpstreamError("upstream"), "success"])
    policy = RetryPolicy(max_retries=3, backoff_base_s=0.01) # Short backoff for testing
    mocker.patch('time.sleep') # Mock sleep to avoid actual delays
    
    result = run_with_retry(mock_fn, policy)
    assert result == "success"
    assert mock_fn.call_count == 3
    assert time.sleep.called # Ensure sleep was called

def test_run_with_retry_exceeds_max_retries(mocker): # Added mocker
    # Test that a retryable error is re-raised after max_retries
    mock_fn = Mock(side_effect=GatewayTimeoutError("timeout"))
    policy = RetryPolicy(max_retries=2, backoff_base_s=0.01)
    mocker.patch('time.sleep')

    with pytest.raises(GatewayTimeoutError):
        run_with_retry(mock_fn, policy)
    assert mock_fn.call_count == 3 # Initial call + 2 retries

def test_run_with_retry_non_retryable_error():
    # Test that a non-retryable error is raised immediately
    mock_fn = Mock(side_effect=GatewayClientError("bad request"))
    policy = RetryPolicy(max_retries=3)
    
    with pytest.raises(GatewayClientError):
        run_with_retry(mock_fn, policy)
    mock_fn.assert_called_once() # Should not retry

def test_run_with_retry_other_exception_raised_immediately():
    # Test that an unexpected exception is raised immediately
    mock_fn = Mock(side_effect=ValueError("unexpected"))
    policy = RetryPolicy(max_retries=3)
    
    with pytest.raises(ValueError):
        run_with_retry(mock_fn, policy)
    mock_fn.assert_called_once()

def test_run_with_retry_multiple_retryable_errors(mocker): # Added mocker
    # Test with a mix of retryable errors
    mock_fn = Mock(side_effect=[GatewayRateLimitError("rate limited"), GatewayTimeoutError("timeout"), "finally success"])
    policy = RetryPolicy(max_retries=2, backoff_base_s=0.01)
    mocker.patch('time.sleep')
    
    result = run_with_retry(mock_fn, policy)
    assert result == "finally success"
    assert mock_fn.call_count == 3

def test_sleep_s_calculation(mocker): # Added mocker
    # Test that _sleep_s calculates a reasonable backoff (no exact values due to jitter)
    policy = RetryPolicy(backoff_base_s=1.0, backoff_max_s=10.0)
    mocker.patch('random.uniform', return_value=0) # Remove jitter for predictable results

    # Attempt 0: base * 2^0 = 1.0, jitter 0, min(10.0, 1.0) = 1.0
    assert _sleep_s(policy, 0) == 1.0 # Corrected access

    # Attempt 1: base * 2^1 = 2.0, jitter 0, min(10.0, 2.0) = 2.0
    assert _sleep_s(policy, 1) == 2.0 # Corrected access

    # Attempt 2: base * 2^2 = 4.0, jitter 0, min(10.0, 4.0) = 4.0
    assert _sleep_s(policy, 2) == 4.0 # Corrected access

    # Attempt 3: base * 2^3 = 8.0, jitter 0, min(10.0, 8.0) = 8.0
    assert _sleep_s(policy, 3) == 8.0 # Corrected access

    # Attempt 4: base * 2^4 = 16.0, jitter 0, min(10.0, 16.0) = 10.0 (capped by backoff_max_s)
    assert _sleep_s(policy, 4) == 10.0 # Corrected access
```


```

## File: /home/user/AA1/gateways/ai_gateway/poetry.lock

```
# This file is automatically @generated by Poetry 2.3.1 and should not be changed by hand.

[[package]]
name = "annotated-types"
version = "0.7.0"
description = "Reusable constraint types to use with typing.Annotated"
optional = false
python-versions = ">=3.8"
groups = ["main"]
files = [
    {file = "annotated_types-0.7.0-py3-none-any.whl", hash = "sha256:1f02e8b43a8fbbc3f3e0d4f0f4bfc8131bcb4eebe8849b8e5c773f3a1c582a53"},
    {file = "annotated_types-0.7.0.tar.gz", hash = "sha256:aff07c09a53a08bc8cfccb9c85b05f1aa9a2a6f23728d790723543408344ce89"},
]

[[package]]
name = "anyio"
version = "4.12.1"
description = "High-level concurrency and networking framework on top of asyncio or Trio"
optional = false
python-versions = ">=3.9"
groups = ["main"]
files = [
    {file = "anyio-4.12.1-py3-none-any.whl", hash = "sha256:d405828884fc140aa80a3c667b8beed277f1dfedec42ba031bd6ac3db606ab6c"},
    {file = "anyio-4.12.1.tar.gz", hash = "sha256:41cfcc3a4c85d3f05c932da7c26d0201ac36f72abd4435ba90d0464a3ffed703"},
]

[package.dependencies]
idna = ">=2.8"
typing_extensions = {version = ">=4.5", markers = "python_version < \"3.13\""}

[package.extras]
trio = ["trio (>=0.31.0) ; python_version < \"3.10\"", "trio (>=0.32.0) ; python_version >= \"3.10\""]

[[package]]
name = "backoff"
version = "2.2.1"
description = "Function decoration for backoff and retry"
optional = false
python-versions = ">=3.7,<4.0"
groups = ["main"]
files = [
    {file = "backoff-2.2.1-py3-none-any.whl", hash = "sha256:63579f9a0628e06278f7e47b7d7d5b6ce20dc65c5e96a6f3ca99a6adca0396e8"},
    {file = "backoff-2.2.1.tar.gz", hash = "sha256:03f829f5bb1923180821643f8753b0502c3b682293992485b0eef2807afa5cba"},
]

[[package]]
name = "certifi"
version = "2026.1.4"
description = "Python package for providing Mozilla's CA Bundle."
optional = false
python-versions = ">=3.7"
groups = ["main"]
files = [
    {file = "certifi-2026.1.4-py3-none-any.whl", hash = "sha256:9943707519e4add1115f44c2bc244f782c0249876bf51b6599fee1ffbedd685c"},
    {file = "certifi-2026.1.4.tar.gz", hash = "sha256:ac726dd470482006e014ad384921ed6438c457018f4b3d204aea4281258b2120"},
]

[[package]]
name = "colorama"
version = "0.4.6"
description = "Cross-platform colored terminal text."
optional = false
python-versions = "!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*,!=3.6.*,>=2.7"
groups = ["dev"]
markers = "sys_platform == \"win32\""
files = [
    {file = "colorama-0.4.6-py2.py3-none-any.whl", hash = "sha256:4f1d9991f5acc0ca119f9d443620b77f9d6b33703e51011c16baf57afb285fc6"},
    {file = "colorama-0.4.6.tar.gz", hash = "sha256:08695f5cb7ed6e0531a20572697297273c47b8cae5a63ffc6d6ed5c201be6e44"},
]

[[package]]
name = "h11"
version = "0.16.0"
description = "A pure-Python, bring-your-own-I/O implementation of HTTP/1.1"
optional = false
python-versions = ">=3.8"
groups = ["main"]
files = [
    {file = "h11-0.16.0-py3-none-any.whl", hash = "sha256:63cf8bbe7522de3bf65932fda1d9c2772064ffb3dae62d55932da54b31cb6c86"},
    {file = "h11-0.16.0.tar.gz", hash = "sha256:4e35b956cf45792e4caa5885e69fba00bdbc6ffafbfa020300e549b208ee5ff1"},
]

[[package]]
name = "httpcore"
version = "1.0.9"
description = "A minimal low-level HTTP client."
optional = false
python-versions = ">=3.8"
groups = ["main"]
files = [
    {file = "httpcore-1.0.9-py3-none-any.whl", hash = "sha256:2d400746a40668fc9dec9810239072b40b4484b640a8c38fd654a024c7a1bf55"},
    {file = "httpcore-1.0.9.tar.gz", hash = "sha256:6e34463af53fd2ab5d807f399a9b45ea31c3dfa2276f15a2c3f00afff6e176e8"},
]

[package.dependencies]
certifi = "*"
h11 = ">=0.16"

[package.extras]
asyncio = ["anyio (>=4.0,<5.0)"]
http2 = ["h2 (>=3,<5)"]
socks = ["socksio (==1.*)"]
trio = ["trio (>=0.22.0,<1.0)"]

[[package]]
name = "httpx"
version = "0.26.0"
description = "The next generation HTTP client."
optional = false
python-versions = ">=3.8"
groups = ["main"]
files = [
    {file = "httpx-0.26.0-py3-none-any.whl", hash = "sha256:8915f5a3627c4d47b73e8202457cb28f1266982d1159bd5779d86a80c0eab1cd"},
    {file = "httpx-0.26.0.tar.gz", hash = "sha256:451b55c30d5185ea6b23c2c793abf9bb237d2a7dfb901ced6ff69ad37ec1dfaf"},
]

[package.dependencies]
anyio = "*"
certifi = "*"
httpcore = "==1.*"
idna = "*"
sniffio = "*"

[package.extras]
brotli = ["brotli ; platform_python_implementation == \"CPython\"", "brotlicffi ; platform_python_implementation != \"CPython\""]
cli = ["click (==8.*)", "pygments (==2.*)", "rich (>=10,<14)"]
http2 = ["h2 (>=3,<5)"]
socks = ["socksio (==1.*)"]

[[package]]
name = "idna"
version = "3.11"
description = "Internationalized Domain Names in Applications (IDNA)"
optional = false
python-versions = ">=3.8"
groups = ["main"]
files = [
    {file = "idna-3.11-py3-none-any.whl", hash = "sha256:771a87f49d9defaf64091e6e6fe9c18d4833f140bd19464795bc32d966ca37ea"},
    {file = "idna-3.11.tar.gz", hash = "sha256:795dafcc9c04ed0c1fb032c2aa73654d8e8c5023a7df64a53f39190ada629902"},
]

[package.extras]
all = ["flake8 (>=7.1.1)", "mypy (>=1.11.2)", "pytest (>=8.3.2)", "ruff (>=0.6.2)"]

[[package]]
name = "iniconfig"
version = "2.3.0"
description = "brain-dead simple config-ini parsing"
optional = false
python-versions = ">=3.10"
groups = ["dev"]
files = [
    {file = "iniconfig-2.3.0-py3-none-any.whl", hash = "sha256:f631c04d2c48c52b84d0d0549c99ff3859c98df65b3101406327ecc7d53fbf12"},
    {file = "iniconfig-2.3.0.tar.gz", hash = "sha256:c76315c77db068650d49c5b56314774a7804df16fee4402c1f19d6d15d8c4730"},
]

[[package]]
name = "packaging"
version = "25.0"
description = "Core utilities for Python packages"
optional = false
python-versions = ">=3.8"
groups = ["dev"]
files = [
    {file = "packaging-25.0-py3-none-any.whl", hash = "sha256:29572ef2b1f17581046b3a2227d5c611fb25ec70ca1ba8554b24b0e69331a484"},
    {file = "packaging-25.0.tar.gz", hash = "sha256:d443872c98d677bf60f6a1f2f8c1cb748e8fe762d2bf9d3148b5599295b0fc4f"},
]

[[package]]
name = "pluggy"
version = "1.6.0"
description = "plugin and hook calling mechanisms for python"
optional = false
python-versions = ">=3.9"
groups = ["dev"]
files = [
    {file = "pluggy-1.6.0-py3-none-any.whl", hash = "sha256:e920276dd6813095e9377c0bc5566d94c932c33b27a3e3945d8389c374dd4746"},
    {file = "pluggy-1.6.0.tar.gz", hash = "sha256:7dcc130b76258d33b90f61b658791dede3486c3e6bfb003ee5c9bfb396dd22f3"},
]

[package.extras]
dev = ["pre-commit", "tox"]
testing = ["coverage", "pytest", "pytest-benchmark"]

[[package]]
name = "pydantic"
version = "2.12.5"
description = "Data validation using Python type hints"
optional = false
python-versions = ">=3.9"
groups = ["main"]
files = [
    {file = "pydantic-2.12.5-py3-none-any.whl", hash = "sha256:e561593fccf61e8a20fc46dfc2dfe075b8be7d0188df33f221ad1f0139180f9d"},
    {file = "pydantic-2.12.5.tar.gz", hash = "sha256:4d351024c75c0f085a9febbb665ce8c0c6ec5d30e903bdb6394b7ede26aebb49"},
]

[package.dependencies]
annotated-types = ">=0.6.0"
pydantic-core = "2.41.5"
typing-extensions = ">=4.14.1"
typing-inspection = ">=0.4.2"

[package.extras]
email = ["email-validator (>=2.0.0)"]
timezone = ["tzdata ; python_version >= \"3.9\" and platform_system == \"Windows\""]

[[package]]
name = "pydantic-core"
version = "2.41.5"
description = "Core functionality for Pydantic validation and serialization"
optional = false
python-versions = ">=3.9"
groups = ["main"]
files = [
    {file = "pydantic_core-2.41.5-cp310-cp310-macosx_10_12_x86_64.whl", hash = "sha256:77b63866ca88d804225eaa4af3e664c5faf3568cea95360d21f4725ab6e07146"},
    {file = "pydantic_core-2.41.5-cp310-cp310-macosx_11_0_arm64.whl", hash = "sha256:dfa8a0c812ac681395907e71e1274819dec685fec28273a28905df579ef137e2"},
    {file = "pydantic_core-2.41.5-cp310-cp310-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:5921a4d3ca3aee735d9fd163808f5e8dd6c6972101e4adbda9a4667908849b97"},
    {file = "pydantic_core-2.41.5-cp310-cp310-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:e25c479382d26a2a41b7ebea1043564a937db462816ea07afa8a44c0866d52f9"},
    {file = "pydantic_core-2.41.5-cp310-cp310-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:f547144f2966e1e16ae626d8ce72b4cfa0caedc7fa28052001c94fb2fcaa1c52"},
    {file = "pydantic_core-2.41.5-cp310-cp310-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:6f52298fbd394f9ed112d56f3d11aabd0d5bd27beb3084cc3d8ad069483b8941"},
    {file = "pydantic_core-2.41.5-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:100baa204bb412b74fe285fb0f3a385256dad1d1879f0a5cb1499ed2e83d132a"},
    {file = "pydantic_core-2.41.5-cp310-cp310-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:05a2c8852530ad2812cb7914dc61a1125dc4e06252ee98e5638a12da6cc6fb6c"},
    {file = "pydantic_core-2.41.5-cp310-cp310-musllinux_1_1_aarch64.whl", hash = "sha256:29452c56df2ed968d18d7e21f4ab0ac55e71dc59524872f6fc57dcf4a3249ed2"},
    {file = "pydantic_core-2.41.5-cp310-cp310-musllinux_1_1_armv7l.whl", hash = "sha256:d5160812ea7a8a2ffbe233d8da666880cad0cbaf5d4de74ae15c313213d62556"},
    {file = "pydantic_core-2.41.5-cp310-cp310-musllinux_1_1_x86_64.whl", hash = "sha256:df3959765b553b9440adfd3c795617c352154e497a4eaf3752555cfb5da8fc49"},
    {file = "pydantic_core-2.41.5-cp310-cp310-win32.whl", hash = "sha256:1f8d33a7f4d5a7889e60dc39856d76d09333d8a6ed0f5f1190635cbec70ec4ba"},
    {file = "pydantic_core-2.41.5-cp310-cp310-win_amd64.whl", hash = "sha256:62de39db01b8d593e45871af2af9e497295db8d73b085f6bfd0b18c83c70a8f9"},
    {file = "pydantic_core-2.41.5-cp311-cp311-macosx_10_12_x86_64.whl", hash = "sha256:a3a52f6156e73e7ccb0f8cced536adccb7042be67cb45f9562e12b319c119da6"},
    {file = "pydantic_core-2.41.5-cp311-cp311-macosx_11_0_arm64.whl", hash = "sha256:7f3bf998340c6d4b0c9a2f02d6a400e51f123b59565d74dc60d252ce888c260b"},
    {file = "pydantic_core-2.41.5-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:378bec5c66998815d224c9ca994f1e14c0c21cb95d2f52b6021cc0b2a58f2a5a"},
    {file = "pydantic_core-2.41.5-cp311-cp311-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:e7b576130c69225432866fe2f4a469a85a54ade141d96fd396dffcf607b558f8"},
    {file = "pydantic_core-2.41.5-cp311-cp311-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:6cb58b9c66f7e4179a2d5e0f849c48eff5c1fca560994d6eb6543abf955a149e"},
    {file = "pydantic_core-2.41.5-cp311-cp311-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:88942d3a3dff3afc8288c21e565e476fc278902ae4d6d134f1eeda118cc830b1"},
    {file = "pydantic_core-2.41.5-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:f31d95a179f8d64d90f6831d71fa93290893a33148d890ba15de25642c5d075b"},
    {file = "pydantic_core-2.41.5-cp311-cp311-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:c1df3d34aced70add6f867a8cf413e299177e0c22660cc767218373d0779487b"},
    {file = "pydantic_core-2.41.5-cp311-cp311-musllinux_1_1_aarch64.whl", hash = "sha256:4009935984bd36bd2c774e13f9a09563ce8de4abaa7226f5108262fa3e637284"},
    {file = "pydantic_core-2.41.5-cp311-cp311-musllinux_1_1_armv7l.whl", hash = "sha256:34a64bc3441dc1213096a20fe27e8e128bd3ff89921706e83c0b1ac971276594"},
    {file = "pydantic_core-2.41.5-cp311-cp311-musllinux_1_1_x86_64.whl", hash = "sha256:c9e19dd6e28fdcaa5a1de679aec4141f691023916427ef9bae8584f9c2fb3b0e"},
    {file = "pydantic_core-2.41.5-cp311-cp311-win32.whl", hash = "sha256:2c010c6ded393148374c0f6f0bf89d206bf3217f201faa0635dcd56bd1520f6b"},
    {file = "pydantic_core-2.41.5-cp311-cp311-win_amd64.whl", hash = "sha256:76ee27c6e9c7f16f47db7a94157112a2f3a00e958bc626e2f4ee8bec5c328fbe"},
    {file = "pydantic_core-2.41.5-cp311-cp311-win_arm64.whl", hash = "sha256:4bc36bbc0b7584de96561184ad7f012478987882ebf9f9c389b23f432ea3d90f"},
    {file = "pydantic_core-2.41.5-cp312-cp312-macosx_10_12_x86_64.whl", hash = "sha256:f41a7489d32336dbf2199c8c0a215390a751c5b014c2c1c5366e817202e9cdf7"},
    {file = "pydantic_core-2.41.5-cp312-cp312-macosx_11_0_arm64.whl", hash = "sha256:070259a8818988b9a84a449a2a7337c7f430a22acc0859c6b110aa7212a6d9c0"},
    {file = "pydantic_core-2.41.5-cp312-cp312-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:e96cea19e34778f8d59fe40775a7a574d95816eb150850a85a7a4c8f4b94ac69"},
    {file = "pydantic_core-2.41.5-cp312-cp312-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:ed2e99c456e3fadd05c991f8f437ef902e00eedf34320ba2b0842bd1c3ca3a75"},
    {file = "pydantic_core-2.41.5-cp312-cp312-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:65840751b72fbfd82c3c640cff9284545342a4f1eb1586ad0636955b261b0b05"},
    {file = "pydantic_core-2.41.5-cp312-cp312-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:e536c98a7626a98feb2d3eaf75944ef6f3dbee447e1f841eae16f2f0a72d8ddc"},
    {file = "pydantic_core-2.41.5-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:eceb81a8d74f9267ef4081e246ffd6d129da5d87e37a77c9bde550cb04870c1c"},
    {file = "pydantic_core-2.41.5-cp312-cp312-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:d38548150c39b74aeeb0ce8ee1d8e82696f4a4e16ddc6de7b1d8823f7de4b9b5"},
    {file = "pydantic_core-2.41.5-cp312-cp312-musllinux_1_1_aarch64.whl", hash = "sha256:c23e27686783f60290e36827f9c626e63154b82b116d7fe9adba1fda36da706c"},
    {file = "pydantic_core-2.41.5-cp312-cp312-musllinux_1_1_armv7l.whl", hash = "sha256:482c982f814460eabe1d3bb0adfdc583387bd4691ef00b90575ca0d2b6fe2294"},
    {file = "pydantic_core-2.41.5-cp312-cp312-musllinux_1_1_x86_64.whl", hash = "sha256:bfea2a5f0b4d8d43adf9d7b8bf019fb46fdd10a2e5cde477fbcb9d1fa08c68e1"},
    {file = "pydantic_core-2.41.5-cp312-cp312-win32.whl", hash = "sha256:b74557b16e390ec12dca509bce9264c3bbd128f8a2c376eaa68003d7f327276d"},
    {file = "pydantic_core-2.41.5-cp312-cp312-win_amd64.whl", hash = "sha256:1962293292865bca8e54702b08a4f26da73adc83dd1fcf26fbc875b35d81c815"},
    {file = "pydantic_core-2.41.5-cp312-cp312-win_arm64.whl", hash = "sha256:1746d4a3d9a794cacae06a5eaaccb4b8643a131d45fbc9af23e353dc0a5ba5c3"},
    {file = "pydantic_core-2.41.5-cp313-cp313-macosx_10_12_x86_64.whl", hash = "sha256:941103c9be18ac8daf7b7adca8228f8ed6bb7a1849020f643b3a14d15b1924d9"},
    {file = "pydantic_core-2.41.5-cp313-cp313-macosx_11_0_arm64.whl", hash = "sha256:112e305c3314f40c93998e567879e887a3160bb8689ef3d2c04b6cc62c33ac34"},
    {file = "pydantic_core-2.41.5-cp313-cp313-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:0cbaad15cb0c90aa221d43c00e77bb33c93e8d36e0bf74760cd00e732d10a6a0"},
    {file = "pydantic_core-2.41.5-cp313-cp313-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:03ca43e12fab6023fc79d28ca6b39b05f794ad08ec2feccc59a339b02f2b3d33"},
    {file = "pydantic_core-2.41.5-cp313-cp313-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:dc799088c08fa04e43144b164feb0c13f9a0bc40503f8df3e9fde58a3c0c101e"},
    {file = "pydantic_core-2.41.5-cp313-cp313-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:97aeba56665b4c3235a0e52b2c2f5ae9cd071b8a8310ad27bddb3f7fb30e9aa2"},
    {file = "pydantic_core-2.41.5-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:406bf18d345822d6c21366031003612b9c77b3e29ffdb0f612367352aab7d586"},
    {file = "pydantic_core-2.41.5-cp313-cp313-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:b93590ae81f7010dbe380cdeab6f515902ebcbefe0b9327cc4804d74e93ae69d"},
    {file = "pydantic_core-2.41.5-cp313-cp313-musllinux_1_1_aarch64.whl", hash = "sha256:01a3d0ab748ee531f4ea6c3e48ad9dac84ddba4b0d82291f87248f2f9de8d740"},
    {file = "pydantic_core-2.41.5-cp313-cp313-musllinux_1_1_armv7l.whl", hash = "sha256:6561e94ba9dacc9c61bce40e2d6bdc3bfaa0259d3ff36ace3b1e6901936d2e3e"},
    {file = "pydantic_core-2.41.5-cp313-cp313-musllinux_1_1_x86_64.whl", hash = "sha256:915c3d10f81bec3a74fbd4faebe8391013ba61e5a1a8d48c4455b923bdda7858"},
    {file = "pydantic_core-2.41.5-cp313-cp313-win32.whl", hash = "sha256:650ae77860b45cfa6e2cdafc42618ceafab3a2d9a3811fcfbd3bbf8ac3c40d36"},
    {file = "pydantic_core-2.41.5-cp313-cp313-win_amd64.whl", hash = "sha256:79ec52ec461e99e13791ec6508c722742ad745571f234ea6255bed38c6480f11"},
    {file = "pydantic_core-2.41.5-cp313-cp313-win_arm64.whl", hash = "sha256:3f84d5c1b4ab906093bdc1ff10484838aca54ef08de4afa9de0f5f14d69639cd"},
    {file = "pydantic_core-2.41.5-cp314-cp314-macosx_10_12_x86_64.whl", hash = "sha256:3f37a19d7ebcdd20b96485056ba9e8b304e27d9904d233d7b1015db320e51f0a"},
    {file = "pydantic_core-2.41.5-cp314-cp314-macosx_11_0_arm64.whl", hash = "sha256:1d1d9764366c73f996edd17abb6d9d7649a7eb690006ab6adbda117717099b14"},
    {file = "pydantic_core-2.41.5-cp314-cp314-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:25e1c2af0fce638d5f1988b686f3b3ea8cd7de5f244ca147c777769e798a9cd1"},
    {file = "pydantic_core-2.41.5-cp314-cp314-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:506d766a8727beef16b7adaeb8ee6217c64fc813646b424d0804d67c16eddb66"},
    {file = "pydantic_core-2.41.5-cp314-cp314-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:4819fa52133c9aa3c387b3328f25c1facc356491e6135b459f1de698ff64d869"},
    {file = "pydantic_core-2.41.5-cp314-cp314-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:2b761d210c9ea91feda40d25b4efe82a1707da2ef62901466a42492c028553a2"},
    {file = "pydantic_core-2.41.5-cp314-cp314-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:22f0fb8c1c583a3b6f24df2470833b40207e907b90c928cc8d3594b76f874375"},
    {file = "pydantic_core-2.41.5-cp314-cp314-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:2782c870e99878c634505236d81e5443092fba820f0373997ff75f90f68cd553"},
    {file = "pydantic_core-2.41.5-cp314-cp314-musllinux_1_1_aarch64.whl", hash = "sha256:0177272f88ab8312479336e1d777f6b124537d47f2123f89cb37e0accea97f90"},
    {file = "pydantic_core-2.41.5-cp314-cp314-musllinux_1_1_armv7l.whl", hash = "sha256:63510af5e38f8955b8ee5687740d6ebf7c2a0886d15a6d65c32814613681bc07"},
    {file = "pydantic_core-2.41.5-cp314-cp314-musllinux_1_1_x86_64.whl", hash = "sha256:e56ba91f47764cc14f1daacd723e3e82d1a89d783f0f5afe9c364b8bb491ccdb"},
    {file = "pydantic_core-2.41.5-cp314-cp314-win32.whl", hash = "sha256:aec5cf2fd867b4ff45b9959f8b20ea3993fc93e63c7363fe6851424c8a7e7c23"},
    {file = "pydantic_core-2.41.5-cp314-cp314-win_amd64.whl", hash = "sha256:8e7c86f27c585ef37c35e56a96363ab8de4e549a95512445b85c96d3e2f7c1bf"},
    {file = "pydantic_core-2.41.5-cp314-cp314-win_arm64.whl", hash = "sha256:e672ba74fbc2dc8eea59fb6d4aed6845e6905fc2a8afe93175d94a83ba2a01a0"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-macosx_10_12_x86_64.whl", hash = "sha256:8566def80554c3faa0e65ac30ab0932b9e3a5cd7f8323764303d468e5c37595a"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-macosx_11_0_arm64.whl", hash = "sha256:b80aa5095cd3109962a298ce14110ae16b8c1aece8b72f9dafe81cf597ad80b3"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:3006c3dd9ba34b0c094c544c6006cc79e87d8612999f1a5d43b769b89181f23c"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:72f6c8b11857a856bcfa48c86f5368439f74453563f951e473514579d44aa612"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:5cb1b2f9742240e4bb26b652a5aeb840aa4b417c7748b6f8387927bc6e45e40d"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:bd3d54f38609ff308209bd43acea66061494157703364ae40c951f83ba99a1a9"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:2ff4321e56e879ee8d2a879501c8e469414d948f4aba74a2d4593184eb326660"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:d0d2568a8c11bf8225044aa94409e21da0cb09dcdafe9ecd10250b2baad531a9"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-musllinux_1_1_aarch64.whl", hash = "sha256:a39455728aabd58ceabb03c90e12f71fd30fa69615760a075b9fec596456ccc3"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-musllinux_1_1_armv7l.whl", hash = "sha256:239edca560d05757817c13dc17c50766136d21f7cd0fac50295499ae24f90fdf"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-musllinux_1_1_x86_64.whl", hash = "sha256:2a5e06546e19f24c6a96a129142a75cee553cc018ffee48a460059b1185f4470"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-win32.whl", hash = "sha256:b4ececa40ac28afa90871c2cc2b9ffd2ff0bf749380fbdf57d165fd23da353aa"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-win_amd64.whl", hash = "sha256:80aa89cad80b32a912a65332f64a4450ed00966111b6615ca6816153d3585a8c"},
    {file = "pydantic_core-2.41.5-cp314-cp314t-win_arm64.whl", hash = "sha256:35b44f37a3199f771c3eaa53051bc8a70cd7b54f333531c59e29fd4db5d15008"},
    {file = "pydantic_core-2.41.5-cp39-cp39-macosx_10_12_x86_64.whl", hash = "sha256:8bfeaf8735be79f225f3fefab7f941c712aaca36f1128c9d7e2352ee1aa87bdf"},
    {file = "pydantic_core-2.41.5-cp39-cp39-macosx_11_0_arm64.whl", hash = "sha256:346285d28e4c8017da95144c7f3acd42740d637ff41946af5ce6e5e420502dd5"},
    {file = "pydantic_core-2.41.5-cp39-cp39-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:a75dafbf87d6276ddc5b2bf6fae5254e3d0876b626eb24969a574fff9149ee5d"},
    {file = "pydantic_core-2.41.5-cp39-cp39-manylinux_2_17_armv7l.manylinux2014_armv7l.whl", hash = "sha256:7b93a4d08587e2b7e7882de461e82b6ed76d9026ce91ca7915e740ecc7855f60"},
    {file = "pydantic_core-2.41.5-cp39-cp39-manylinux_2_17_ppc64le.manylinux2014_ppc64le.whl", hash = "sha256:e8465ab91a4bd96d36dde3263f06caa6a8a6019e4113f24dc753d79a8b3a3f82"},
    {file = "pydantic_core-2.41.5-cp39-cp39-manylinux_2_17_s390x.manylinux2014_s390x.whl", hash = "sha256:299e0a22e7ae2b85c1a57f104538b2656e8ab1873511fd718a1c1c6f149b77b5"},
    {file = "pydantic_core-2.41.5-cp39-cp39-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:707625ef0983fcfb461acfaf14de2067c5942c6bb0f3b4c99158bed6fedd3cf3"},
    {file = "pydantic_core-2.41.5-cp39-cp39-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:f41eb9797986d6ebac5e8edff36d5cef9de40def462311b3eb3eeded1431e425"},
    {file = "pydantic_core-2.41.5-cp39-cp39-musllinux_1_1_aarch64.whl", hash = "sha256:0384e2e1021894b1ff5a786dbf94771e2986ebe2869533874d7e43bc79c6f504"},
    {file = "pydantic_core-2.41.5-cp39-cp39-musllinux_1_1_armv7l.whl", hash = "sha256:f0cd744688278965817fd0839c4a4116add48d23890d468bc436f78beb28abf5"},
    {file = "pydantic_core-2.41.5-cp39-cp39-musllinux_1_1_x86_64.whl", hash = "sha256:753e230374206729bf0a807954bcc6c150d3743928a73faffee51ac6557a03c3"},
    {file = "pydantic_core-2.41.5-cp39-cp39-win32.whl", hash = "sha256:873e0d5b4fb9b89ef7c2d2a963ea7d02879d9da0da8d9d4933dee8ee86a8b460"},
    {file = "pydantic_core-2.41.5-cp39-cp39-win_amd64.whl", hash = "sha256:e4f4a984405e91527a0d62649ee21138f8e3d0ef103be488c1dc11a80d7f184b"},
    {file = "pydantic_core-2.41.5-graalpy311-graalpy242_311_native-macosx_10_12_x86_64.whl", hash = "sha256:b96d5f26b05d03cc60f11a7761a5ded1741da411e7fe0909e27a5e6a0cb7b034"},
    {file = "pydantic_core-2.41.5-graalpy311-graalpy242_311_native-macosx_11_0_arm64.whl", hash = "sha256:634e8609e89ceecea15e2d61bc9ac3718caaaa71963717bf3c8f38bfde64242c"},
    {file = "pydantic_core-2.41.5-graalpy311-graalpy242_311_native-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:93e8740d7503eb008aa2df04d3b9735f845d43ae845e6dcd2be0b55a2da43cd2"},
    {file = "pydantic_core-2.41.5-graalpy311-graalpy242_311_native-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:f15489ba13d61f670dcc96772e733aad1a6f9c429cc27574c6cdaed82d0146ad"},
    {file = "pydantic_core-2.41.5-graalpy312-graalpy250_312_native-macosx_10_12_x86_64.whl", hash = "sha256:7da7087d756b19037bc2c06edc6c170eeef3c3bafcb8f532ff17d64dc427adfd"},
    {file = "pydantic_core-2.41.5-graalpy312-graalpy250_312_native-macosx_11_0_arm64.whl", hash = "sha256:aabf5777b5c8ca26f7824cb4a120a740c9588ed58df9b2d196ce92fba42ff8dc"},
    {file = "pydantic_core-2.41.5-graalpy312-graalpy250_312_native-manylinux_2_17_aarch64.manylinux2014_aarch64.whl", hash = "sha256:c007fe8a43d43b3969e8469004e9845944f1a80e6acd47c150856bb87f230c56"},
    {file = "pydantic_core-2.41.5-graalpy312-graalpy250_312_native-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:76d0819de158cd855d1cbb8fcafdf6f5cf1eb8e470abe056d5d161106e38062b"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-macosx_10_12_x86_64.whl", hash = "sha256:b5819cd790dbf0c5eb9f82c73c16b39a65dd6dd4d1439dcdea7816ec9adddab8"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-macosx_11_0_arm64.whl", hash = "sha256:5a4e67afbc95fa5c34cf27d9089bca7fcab4e51e57278d710320a70b956d1b9a"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:ece5c59f0ce7d001e017643d8d24da587ea1f74f6993467d85ae8a5ef9d4f42b"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:16f80f7abe3351f8ea6858914ddc8c77e02578544a0ebc15b4c2e1a0e813b0b2"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-musllinux_1_1_aarch64.whl", hash = "sha256:33cb885e759a705b426baada1fe68cbb0a2e68e34c5d0d0289a364cf01709093"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-musllinux_1_1_armv7l.whl", hash = "sha256:c8d8b4eb992936023be7dee581270af5c6e0697a8559895f527f5b7105ecd36a"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-musllinux_1_1_x86_64.whl", hash = "sha256:242a206cd0318f95cd21bdacff3fcc3aab23e79bba5cac3db5a841c9ef9c6963"},
    {file = "pydantic_core-2.41.5-pp310-pypy310_pp73-win_amd64.whl", hash = "sha256:d3a978c4f57a597908b7e697229d996d77a6d3c94901e9edee593adada95ce1a"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-macosx_10_12_x86_64.whl", hash = "sha256:b2379fa7ed44ddecb5bfe4e48577d752db9fc10be00a6b7446e9663ba143de26"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-macosx_11_0_arm64.whl", hash = "sha256:266fb4cbf5e3cbd0b53669a6d1b039c45e3ce651fd5442eff4d07c2cc8d66808"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-manylinux_2_17_x86_64.manylinux2014_x86_64.whl", hash = "sha256:58133647260ea01e4d0500089a8c4f07bd7aa6ce109682b1426394988d8aaacc"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-manylinux_2_5_i686.manylinux1_i686.whl", hash = "sha256:287dad91cfb551c363dc62899a80e9e14da1f0e2b6ebde82c806612ca2a13ef1"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-musllinux_1_1_aarch64.whl", hash = "sha256:03b77d184b9eb40240ae9fd676ca364ce1085f203e1b1256f8ab9984dca80a84"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-musllinux_1_1_armv7l.whl", hash = "sha256:a668ce24de96165bb239160b3d854943128f4334822900534f2fe947930e5770"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-musllinux_1_1_x86_64.whl", hash = "sha256:f14f8f046c14563f8eb3f45f499cc658ab8d10072961e07225e507adb700e93f"},
    {file = "pydantic_core-2.41.5-pp311-pypy311_pp73-win_amd64.whl", hash = "sha256:56121965f7a4dc965bff783d70b907ddf3d57f6eba29b6d2e5dabfaf07799c51"},
    {file = "pydantic_core-2.41.5.tar.gz", hash = "sha256:08daa51ea16ad373ffd5e7606252cc32f07bc72b28284b6bc9c6df804816476e"},
]

[package.dependencies]
typing-extensions = ">=4.14.1"

[[package]]
name = "pytest"
version = "7.4.4"
description = "pytest: simple powerful testing with Python"
optional = false
python-versions = ">=3.7"
groups = ["dev"]
files = [
    {file = "pytest-7.4.4-py3-none-any.whl", hash = "sha256:b090cdf5ed60bf4c45261be03239c2c1c22df034fbffe691abe93cd80cea01d8"},
    {file = "pytest-7.4.4.tar.gz", hash = "sha256:2cf0005922c6ace4a3e2ec8b4080eb0d9753fdc93107415332f50ce9e7994280"},
]

[package.dependencies]
colorama = {version = "*", markers = "sys_platform == \"win32\""}
iniconfig = "*"
packaging = "*"
pluggy = ">=0.12,<2.0"

[package.extras]
testing = ["argcomplete", "attrs (>=19.2.0)", "hypothesis (>=3.56)", "mock", "nose", "pygments (>=2.7.2)", "requests", "setuptools", "xmlschema"]

[[package]]
name = "pytest-asyncio"
version = "0.21.2"
description = "Pytest support for asyncio"
optional = false
python-versions = ">=3.7"
groups = ["dev"]
files = [
    {file = "pytest_asyncio-0.21.2-py3-none-any.whl", hash = "sha256:ab664c88bb7998f711d8039cacd4884da6430886ae8bbd4eded552ed2004f16b"},
    {file = "pytest_asyncio-0.21.2.tar.gz", hash = "sha256:d67738fc232b94b326b9d060750beb16e0074210b98dd8b58a5239fa2a154f45"},
]

[package.dependencies]
pytest = ">=7.0.0"

[package.extras]
docs = ["sphinx (>=5.3)", "sphinx-rtd-theme (>=1.0)"]
testing = ["coverage (>=6.2)", "flaky (>=3.5.0)", "hypothesis (>=5.7.1)", "mypy (>=0.931)", "pytest-trio (>=0.7.0)"]

[[package]]
name = "pytest-mock"
version = "3.15.1"
description = "Thin-wrapper around the mock package for easier use with pytest"
optional = false
python-versions = ">=3.9"
groups = ["dev"]
files = [
    {file = "pytest_mock-3.15.1-py3-none-any.whl", hash = "sha256:0a25e2eb88fe5168d535041d09a4529a188176ae608a6d249ee65abc0949630d"},
    {file = "pytest_mock-3.15.1.tar.gz", hash = "sha256:1849a238f6f396da19762269de72cb1814ab44416fa73a8686deac10b0d87a0f"},
]

[package.dependencies]
pytest = ">=6.2.5"

[package.extras]
dev = ["pre-commit", "pytest-asyncio", "tox"]

[[package]]
name = "sniffio"
version = "1.3.1"
description = "Sniff out which async library your code is running under"
optional = false
python-versions = ">=3.7"
groups = ["main"]
files = [
    {file = "sniffio-1.3.1-py3-none-any.whl", hash = "sha256:2f6da418d1f1e0fddd844478f41680e794e6051915791a034ff65e5f100525a2"},
    {file = "sniffio-1.3.1.tar.gz", hash = "sha256:f4324edc670a0f49750a81b895f35c3adb843cca46f0530f79fc1babb23789dc"},
]

[[package]]
name = "typing-extensions"
version = "4.15.0"
description = "Backported and Experimental Type Hints for Python 3.9+"
optional = false
python-versions = ">=3.9"
groups = ["main"]
files = [
    {file = "typing_extensions-4.15.0-py3-none-any.whl", hash = "sha256:f0fa19c6845758ab08074a0cfa8b7aecb71c999ca73d62883bc25cc018c4e548"},
    {file = "typing_extensions-4.15.0.tar.gz", hash = "sha256:0cea48d173cc12fa28ecabc3b837ea3cf6f38c6d1136f85cbaaf598984861466"},
]

[[package]]
name = "typing-inspection"
version = "0.4.2"
description = "Runtime typing introspection tools"
optional = false
python-versions = ">=3.9"
groups = ["main"]
files = [
    {file = "typing_inspection-0.4.2-py3-none-any.whl", hash = "sha256:4ed1cacbdc298c220f1bd249ed5287caa16f34d44ef4e9c3d0cbad5b521545e7"},
    {file = "typing_inspection-0.4.2.tar.gz", hash = "sha256:ba561c48a67c5958007083d386c3295464928b01faa735ab8547c5692e87f464"},
]

[package.dependencies]
typing-extensions = ">=4.12.0"

[metadata]
lock-version = "2.1"
python-versions = "^3.11"
content-hash = "7625bff269edfa5d64c1de8d0b5eb2deab8b59559ca77c91e18a03c75406687c"

```

## File: /home/user/AA1/gateways/ai_gateway/pyproject.toml

```
[tool.poetry]
name = "ai-gateway"
version = "0.1.0"
description = ""
authors = ["InstaPact <oss@instapact.com>"]
readme = "README.md"
packages = [{include = "ai_gateway", from = "."}]


[tool.poetry.dependencies]
python = "^3.11"
pydantic = "^2.5.3"
httpx = "^0.26.0"
backoff = "^2.2.1"


[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.1"
pytest-mock = "^3.12.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

```

## File: /home/user/AA1/gateways/ai_gateway/README.md

```

```

## File: /home/user/AA1/gateways/ai_gateway/SERVICE_CONTRACT.md

```
# SERVICE_CONTRACT.md  
## AI Gateway â€” LLM Transport & Stability Layer

---

## 1. Purpose

The **AI Gateway** is an infrastructure service that provides **reliable, secure, and provider-agnostic access to Large Language Models (LLMs)**.

It is **plumbing**, not intelligence.

The service exists to:
- accept a fully-formed prompt
- invoke an LLM supplier
- return the modelâ€™s output **unchanged**
- manage operational, security, and supplier complexity

---

## 2. Explicit Non-Goals (Hard Boundary)

The AI Gateway **MUST NOT**:

- interpret prompts
- interpret outputs
- validate or enforce schemas (e.g. JSON)
- correct or â€œrepairâ€ model responses
- apply workflow logic
- encode domain knowledge
- make decisions
- understand ontology, governance, or semantics
- modify prompts or outputs in any way

All meaning, validation, and governance live **outside** this service.

---

## 3. Input Contract

### Required
- `prompt: str`  
  A fully-formed prompt supplied by the caller.

### Optional (transport-level only)
- `provider` (e.g. gemini, openai, offline)
- `model`
- `timeout_seconds`
- `temperature`
- `max_tokens`

The AI Gateway **does not inspect, parse, or alter** the prompt.

---

## 4. Output Contract

### Success
- Returns **exactly the text produced by the model**, unchanged.

### Failure
- Raises a transport-level error or returns an explicit failure.
- Failures are limited to operational concerns:
  - timeouts
  - authentication errors
  - rate limits
  - supplier availability
  - network failures

The service **never rewrites, truncates, or restructures** model output.

---

## 5. Operational Guarantees

### 5.1 Stability
- Enforced request timeouts
- Bounded retries
- Exponential backoff
- Retries only on transient failures:
  - timeouts
  - HTTP 429
  - HTTP 5xx

### 5.2 Determinism
- Low default temperature unless overridden
- No hidden prompt augmentation
- No stateful behavior across calls

---

## 6. Security Guarantees

- API keys loaded only from environment variables
- No prompt logging by default
- No output logging by default
- No secrets written to disk or stdout
- Debug logging must be explicitly enabled and opt-in

---

## 7. Logging & Observability (Operational Only)

The service MAY log:
- timestamp
- provider
- model
- latency
- retry count
- success / failure
- **prompt hash (never prompt text)**

The service MUST NOT log:
- prompt contents
- model outputs
- domain or customer data

---

## 8. Provider & Model Abstraction

The AI Gateway:
- abstracts supplier-specific APIs
- isolates model naming and version churn
- normalizes transport-level errors

Callers must not rely on supplier-specific behavior.

---

## 9. Change Control Rule (Non-Negotiable)

Any change that introduces:
- semantic interpretation
- output validation
- schema enforcement
- task logic
- workflow behavior
- domain awareness

**violates this contract and must be rejected.**

---

## 10. Design Principle (Canonical)

> **This service is dumb on purpose.**  
> **Intelligence lives in the prompt and the caller.**

---

## 11. Intended Longevity

This contract is designed to remain valid across:
- LLM provider changes
- model evolution
- prompt strategies
- ontology workflows
- governance processes

If this contract no longer fits, a **new service** must be created.

```

## File: /home/user/AA1/gateways/ai_gateway/tests/providers/test_gemini.py

```
import pytest
from unittest.mock import Mock, patch
import httpx

from ai_gateway.providers.gemini import call_gemini, _safe_err
from ai_gateway.errors import GatewayAuthError, GatewayClientError, GatewayRateLimitError, GatewayTimeoutError, GatewayUpstreamError

# Mock configuration
MOCK_API_KEY = "test_api_key"
MOCK_MODEL = "gemini-test-model"
MOCK_PROMPT = "test prompt"
MOCK_TIMEOUT = 10.0

@pytest.fixture
def mock_httpx_client():
    with patch("httpx.Client") as mock_client_class:
        mock_client = mock_client_class.return_value
        # Critical line: what the `with` block binds to as `client`
        mock_client.__enter__.return_value = mock_client
        yield mock_client

# --- Test _safe_err function ---
def test_safe_err_with_error_json():
    resp = Mock(status_code=400) # Simple Mock for _safe_err
    resp.json.return_value = {"error": {"status": "INVALID_ARGUMENT", "code": 400, "message": "API key not valid."}}
    resp.text = "raw text"
    assert _safe_err(resp) == "Upstream error: Status=INVALID_ARGUMENT, Code=400, Message='API key not valid....'"

def test_safe_err_with_other_json():
    resp = Mock(status_code=200) # Simple Mock for _safe_err
    resp.json.return_value = {"status": "OK"}
    resp.text = "raw text"
    assert _safe_err(resp) == "Upstream error: HTTP 200 - Generic error, details redacted."

def test_safe_err_with_invalid_json():
    resp = Mock(status_code=200) # Simple Mock for _safe_err
    resp.json.side_effect = ValueError("Not JSON")
    resp.text = "raw text"
    assert _safe_err(resp) == "Upstream error: HTTP 200 - Generic error, details redacted."

def test_safe_err_with_empty_response():
    resp = Mock(status_code=200) # Simple Mock for _safe_err
    resp.json.side_effect = ValueError("Not JSON")
    resp.text = None
    assert _safe_err(resp) == "Upstream error: HTTP 200 - Generic error, details redacted."

# --- Test call_gemini function ---

def test_call_gemini_success(mock_httpx_client):
    mock_resp = Mock(status_code=200)
    mock_resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": "Expected Output"}]}}]
    }
    mock_httpx_client.post.return_value = mock_resp

    result = call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)
    assert result == "Expected Output"
    mock_httpx_client.post.assert_called_once()
    
def test_call_gemini_auth_error(mock_httpx_client):
    mock_resp = Mock(status_code=401)
    mock_resp.json.return_value = {"error": {"message": "Invalid API Key"}}
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayAuthError, match="Gemini auth error: HTTP 401"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_rate_limit_error(mock_httpx_client):
    mock_resp = Mock(status_code=429)
    mock_resp.json.return_value = {"error": {"message": "Rate limit exceeded"}}
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayRateLimitError, match="Gemini rate limited"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_client_error(mock_httpx_client):
    mock_resp = Mock(status_code=400)
    mock_resp.json.return_value = {"error": {"message": "Bad Request"}}
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayClientError, match="Gemini client error HTTP 400"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_upstream_error(mock_httpx_client):
    mock_resp = Mock(status_code=500)
    mock_resp.json.return_value = {"error": {"message": "Internal Server Error"}}
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayUpstreamError, match="Gemini upstream error HTTP 500"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_timeout_error(mock_httpx_client):
    mock_httpx_client.post.side_effect = httpx.ReadTimeout("Timeout")

    with pytest.raises(GatewayTimeoutError, match="Gemini timeout"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_network_error(mock_httpx_client):
    mock_httpx_client.post.side_effect = httpx.RequestError("Network error", request=httpx.Request("GET", "http://test.com"))

    with pytest.raises(GatewayUpstreamError, match="Gemini request error"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_invalid_json_response(mock_httpx_client):
    mock_resp = Mock(status_code=200)
    mock_resp.json.side_effect = ValueError("Not JSON")
    mock_httpx_client.post.return_value = mock_resp

    with pytest.raises(GatewayUpstreamError, match="Gemini returned non-JSON response"):
        call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)

def test_call_gemini_empty_response_content(mock_httpx_client):
    mock_resp = Mock(status_code=200)
    # Simulate various empty/missing parts in the JSON response
    mock_resp.json.return_value = {
        "candidates": [
            {"content": {"parts": [{"text": None}]}},
            {"content": {"parts": [{}]}},
            {"content": {}},
            {},
        ]
    }
    mock_httpx_client.post.return_value = mock_resp

    result = call_gemini(prompt=MOCK_PROMPT, model=MOCK_MODEL, api_key=MOCK_API_KEY, timeout_s=MOCK_TIMEOUT)
    assert result == "" # Should return empty string if content is missing or None
```

## File: /home/user/AA1/gateways/ai_gateway/tests/test_client.py

```
import pytest
from unittest.mock import Mock, patch, call
import os

from ai_gateway.client import AIGatewayClient, CallOptions
from ai_gateway.config import GatewayConfig
from ai_gateway.errors import GatewayConfigError, GatewayAuthError, AIGatewayError

# Fixtures for common objects
@pytest.fixture
def mock_config():
    return GatewayConfig(
        provider="gemini",
        model="gemini-test-model",
        timeout_s=10.0,
        max_retries=1,
        backoff_base_s=1.0,
        backoff_max_s=20.0,
        gemini_api_key="TEST_GEMINI_KEY",
    )

@pytest.fixture
def client(mock_config):
    return AIGatewayClient(cfg=mock_config)

@pytest.fixture(autouse=True)
def mock_dependencies(mocker, mock_config): # Added mock_config here
    # Patch modules as they are imported within client.py
    log_event_mock = mocker.patch('ai_gateway.client.log_event')
    prompt_hash8_mock = mocker.patch('ai_gateway.client.prompt_hash8', return_value="TESTHASH")
    run_with_retry_mock = mocker.patch('ai_gateway.retry.run_with_retry', side_effect=lambda fn, policy: fn()) # Execute fn immediately

    # Patch modules as they are imported within client.py
    call_gemini_mock = mocker.patch('ai_gateway.client.call_gemini', return_value="MODEL_OUTPUT_OK")
    call_offline_mock = mocker.patch('ai_gateway.client.call_offline', return_value="")
    load_config_mock = mocker.patch('ai_gateway.client.load_config', return_value=mock_config) # Patch where client.py looks for it

    # Return a dict of mocks for easier access in tests
    return {
        "log_event": log_event_mock,
        "prompt_hash8": prompt_hash8_mock,
        "run_with_retry": run_with_retry_mock,
        "call_gemini": call_gemini_mock,
        "call_offline": call_offline_mock,
        "load_config": load_config_mock,
    }

# --- Tests for Data Integrity and Privacy ---

def test_client_does_not_modify_prompt(client, mock_dependencies):
    original_prompt = "Return exactly: This is my prompt."
    expected_output = "MODEL_OUTPUT_OK"
    
    client.call(original_prompt)
    
    # Verify that call_gemini received the original prompt
    mock_dependencies["call_gemini"].assert_called_once_with(
        prompt=original_prompt,
        model=mock_dependencies["load_config"].return_value.model, # Get model from mocked config
        api_key=mock_dependencies["load_config"].return_value.gemini_api_key, # Get API key from mocked config
        timeout_s=mock_dependencies["load_config"].return_value.timeout_s, # Get timeout from mocked config
    )

def test_client_does_not_modify_output(client, mock_dependencies):
    # The mock for call_gemini already ensures a fixed output.
    # The test here is to ensure AIGatewayClient returns it as-is.
    output = client.call("any prompt")
    assert output == "MODEL_OUTPUT_OK"
    
def test_client_logs_prompt_hash_not_prompt_text(client, mock_dependencies, mocker):
    prompt = "Sensitive prompt content"
    output_text = "Sensitive output content from model"
    api_key = "SECRET_API_KEY_VALUE"

    # Temporarily override the return value of call_gemini mock for this test
    mock_dependencies["call_gemini"].return_value = output_text

    # Temporarily override the gemini_api_key in the client's config for this test
    # Since config is frozen, we create a new client with a modified config
    original_config = client.cfg
    modified_config = GatewayConfig(**{
        **original_config.__dict__,
        "gemini_api_key": api_key
    })
    client.cfg = modified_config # Reassign cfg to the new modified config

    client.call(prompt)
    
    # Check log_event calls for 'prompt_hash8'
    mock_dependencies["log_event"].assert_any_call(
        "ai_gateway.call.start",
        provider="gemini",
        model="gemini-test-model",
        timeout_s=10.0,
        prompt_hash8="TESTHASH",
    )
    mock_dependencies["log_event"].assert_any_call(
        "ai_gateway.call.ok",
        provider="gemini",
        model="gemini-test-model",
        latency_ms=mocker.ANY, # Use mocker.ANY for dynamic values
        prompt_hash8="TESTHASH",
    )
    # Ensure no calls directly include the original prompt text, output text, or API key
    for call_args in mock_dependencies["log_event"].call_args_list:
        _args, kwargs = call_args
        # Check kwargs for sensitive data
        for k, v in kwargs.items():
            assert prompt not in str(v)
            assert output_text not in str(v)
            assert api_key not in str(v)
        # In this logging setup, sensitive data would primarily be in kwargs.
        # If any positional arguments could contain sensitive data, they would need checking too.


# --- Tests for core client behavior ---

def test_client_initializes_with_provided_config():
    custom_config = GatewayConfig(
        provider="offline",
        model="test-offline",
        timeout_s=5.0,
        max_retries=0,
        backoff_base_s=0.0,
        backoff_max_s=0.0,
        gemini_api_key=None,
    )
    client = AIGatewayClient(cfg=custom_config)
    assert client.cfg is custom_config

def test_client_loads_config_if_not_provided(mocker, mock_dependencies):
    # Ensure load_config is mocked out and returns a known config
    test_config = GatewayConfig(
        provider="default", model="default", timeout_s=1.0, max_retries=0,
                    backoff_base_s=0.0, backoff_max_s=0.0, gemini_api_key=None    )
    mock_dependencies["load_config"].return_value = test_config # Set return value for the mock
    
    # Create client without passing config, so it calls load_config
    client = AIGatewayClient() 
    mock_dependencies["load_config"].assert_called_once()
    assert client.cfg.provider == "default"

def test_client_calls_gemini_provider_correctly(client, mock_dependencies):
    client.call("test prompt")
    mock_dependencies["call_gemini"].assert_called_once()

def test_client_calls_offline_provider_correctly(mock_config, mock_dependencies):
    # Create a new client with a config that explicitly sets the provider to offline
    offline_config = GatewayConfig(**{**mock_config.__dict__, "provider": "offline"})
    client = AIGatewayClient(cfg=offline_config)
    client.call("test prompt")
    mock_dependencies["call_offline"].assert_called_once()
    mock_dependencies["call_gemini"].assert_not_called()

def test_client_handles_call_options_override(mock_config, mock_dependencies):
    # Ensure base config is gemini so we can override it
    base_config = GatewayConfig(**{**mock_config.__dict__, "provider": "gemini"})
    client = AIGatewayClient(cfg=base_config)
    
    options = CallOptions(provider="offline", timeout_s=5.0)
    client.call("test prompt", options=options)
    
    # Ensure offline was called with overridden timeout
    mock_dependencies["call_offline"].assert_called_once_with(
        prompt="test prompt", model="gemini-test-model", timeout_s=5.0 # Model from config, not overridden
    )
    mock_dependencies["call_gemini"].assert_not_called()


def test_client_raises_value_error_for_empty_prompt(client):
    with pytest.raises(ValueError, match="prompt must be a non-empty string"):
        client.call("")
    with pytest.raises(ValueError, match="prompt must be a non-empty string"):
        client.call("   ")
    with pytest.raises(ValueError, match="prompt must be a non-empty string"):
        client.call(None) # type: ignore

def test_client_raises_gateway_config_error_for_missing_gemini_key(mocker, mock_dependencies, mock_config):
    # Create a new config with missing API key
    mock_config_no_key = GatewayConfig(**{**mock_config.__dict__, "gemini_api_key": None})
    mock_dependencies["load_config"].return_value = mock_config_no_key # Ensure this is the config loaded
    
    client = AIGatewayClient() # Client will load the mocked config
    
    with pytest.raises(GatewayConfigError, match="Missing GEMINI_API_KEY"):
        client.call("test prompt")

def test_client_raises_gateway_config_error_for_unknown_provider(mocker, mock_dependencies, mock_config):
    # Create a new config with an unknown provider and a valid gemini key to reach the "unknown provider" check
    mock_config_unknown_provider = GatewayConfig(**{
        **mock_config.__dict__,
        "provider": "unknown",
        "gemini_api_key": "VALID_KEY_FOR_TEST" # Ensure API key is present so it doesn't fail on missing key first
    })
    mock_dependencies["load_config"].return_value = mock_config_unknown_provider # Ensure this is the config loaded
    
    client = AIGatewayClient() # Client will load the mocked config
    
    with pytest.raises(GatewayConfigError, match="Unknown provider: unknown"):
        client.call("test prompt")

def test_client_logs_failure_on_exception(client, mock_dependencies, mocker):
    mock_dependencies["call_gemini"].side_effect = GatewayAuthError("auth fail")
    
    with pytest.raises(GatewayAuthError):
        client.call("test prompt")
    
    mock_dependencies["log_event"].assert_called_with(
        "ai_gateway.call.fail",
        provider="gemini",
        model="gemini-test-model",
        latency_ms=mocker.ANY,
        prompt_hash8="TESTHASH",
        error_type="GatewayAuthError",
    )

```

## File: /home/user/AA1/gateways/ai_gateway/tests/test_retry.py

```
import pytest
from unittest.mock import Mock, call
import time

from ai_gateway.retry import RetryPolicy, run_with_retry, _sleep_s # Import _sleep_s directly
from ai_gateway.errors import GatewayTimeoutError, GatewayRateLimitError, GatewayUpstreamError, GatewayClientError, GatewayAuthError

def test_run_with_retry_success_first_attempt():
    # Test that a successful function call returns immediately
    mock_fn = Mock(return_value="success")
    policy = RetryPolicy(max_retries=3)
    result = run_with_retry(mock_fn, policy)
    assert result == "success"
    mock_fn.assert_called_once()

def test_run_with_retry_success_after_retries(mocker): # Added mocker
    # Test that a function succeeds after a few retries
    mock_fn = Mock(side_effect=[GatewayTimeoutError("timeout"), GatewayUpstreamError("upstream"), "success"])
    policy = RetryPolicy(max_retries=3, backoff_base_s=0.01) # Short backoff for testing
    mocker.patch('time.sleep') # Mock sleep to avoid actual delays
    
    result = run_with_retry(mock_fn, policy)
    assert result == "success"
    assert mock_fn.call_count == 3
    assert time.sleep.called # Ensure sleep was called

def test_run_with_retry_exceeds_max_retries(mocker): # Added mocker
    # Test that a retryable error is re-raised after max_retries
    mock_fn = Mock(side_effect=GatewayTimeoutError("timeout"))
    policy = RetryPolicy(max_retries=2, backoff_base_s=0.01)
    mocker.patch('time.sleep')

    with pytest.raises(GatewayTimeoutError):
        run_with_retry(mock_fn, policy)
    assert mock_fn.call_count == 3 # Initial call + 2 retries

def test_run_with_retry_non_retryable_error():
    # Test that a non-retryable error is raised immediately
    mock_fn = Mock(side_effect=GatewayClientError("bad request"))
    policy = RetryPolicy(max_retries=3)
    
    with pytest.raises(GatewayClientError):
        run_with_retry(mock_fn, policy)
    mock_fn.assert_called_once() # Should not retry

def test_run_with_retry_other_exception_raised_immediately():
    # Test that an unexpected exception is raised immediately
    mock_fn = Mock(side_effect=ValueError("unexpected"))
    policy = RetryPolicy(max_retries=3)
    
    with pytest.raises(ValueError):
        run_with_retry(mock_fn, policy)
    mock_fn.assert_called_once()

def test_run_with_retry_multiple_retryable_errors(mocker): # Added mocker
    # Test with a mix of retryable errors
    mock_fn = Mock(side_effect=[GatewayRateLimitError("rate limited"), GatewayTimeoutError("timeout"), "finally success"])
    policy = RetryPolicy(max_retries=2, backoff_base_s=0.01)
    mocker.patch('time.sleep')
    
    result = run_with_retry(mock_fn, policy)
    assert result == "finally success"
    assert mock_fn.call_count == 3

def test_sleep_s_calculation(mocker): # Added mocker
    # Test that _sleep_s calculates a reasonable backoff (no exact values due to jitter)
    policy = RetryPolicy(backoff_base_s=1.0, backoff_max_s=10.0)
    mocker.patch('random.uniform', return_value=0) # Remove jitter for predictable results

    # Attempt 0: base * 2^0 = 1.0, jitter 0, min(10.0, 1.0) = 1.0
    assert _sleep_s(policy, 0) == 1.0 # Corrected access

    # Attempt 1: base * 2^1 = 2.0, jitter 0, min(10.0, 2.0) = 2.0
    assert _sleep_s(policy, 1) == 2.0 # Corrected access

    # Attempt 2: base * 2^2 = 4.0, jitter 0, min(10.0, 4.0) = 4.0
    assert _sleep_s(policy, 2) == 4.0 # Corrected access

    # Attempt 3: base * 2^3 = 8.0, jitter 0, min(10.0, 8.0) = 8.0
    assert _sleep_s(policy, 3) == 8.0 # Corrected access

    # Attempt 4: base * 2^4 = 16.0, jitter 0, min(10.0, 16.0) = 10.0 (capped by backoff_max_s)
    assert _sleep_s(policy, 4) == 10.0 # Corrected access
```

