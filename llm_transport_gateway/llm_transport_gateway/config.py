from __future__ import annotations

import os
from dataclasses import dataclass
from .errors import GatewayConfigError


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
    except ValueError as e:
        raise GatewayConfigError(f"Invalid float value for {name}: {v}") from e


def _get_int(name: str, default: int) -> int:
    v = os.getenv(name)
    if v is None or v.strip() == "":
        return default
    try:
        return int(v)
    except ValueError as e:
        raise GatewayConfigError(f"Invalid int value for {name}: {v}") from e


def load_config() -> GatewayConfig:
    # Stable, boring env var surface
    provider = os.getenv("AI_GATEWAY_PROVIDER", "gemini").strip().lower()
    model = os.getenv("AI_GATEWAY_MODEL", "").strip()

    timeout_s = _get_float("AI_GATEWAY_TIMEOUT_S", 60.0)
    max_retries = _get_int("AI_GATEWAY_RETRIES", 3)
    backoff_base_s = _get_float("AI_GATEWAY_BACKOFF_BASE_S", 1.0)
    backoff_max_s = _get_float("AI_GATEWAY_BACKOFF_MAX_S", 20.0)

    # Provider-specific keys (still env-only)
    gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv(
        "AI_GATEWAY_GEMINI_API_KEY"
    )

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
