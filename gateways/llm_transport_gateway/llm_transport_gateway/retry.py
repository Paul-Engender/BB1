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
from .logging import log_event

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


def run_with_retry(fn: Callable[[], T], policy: RetryPolicy, request_id: str) -> T:
    last_exc: Exception | None = None
    for attempt in range(policy.max_retries + 1):
        try:
            return fn()
        except _RETRYABLE as e:
            last_exc = e
            log_event(
                "llm_transport_gateway.call.retry",
                request_id=request_id,
                attempt=attempt + 1,  # current attempt number
                max_retries=policy.max_retries,
                error_type=type(e).__name__,
            )
            if attempt >= policy.max_retries:
                raise
            time.sleep(_sleep_s(policy, attempt))
    # Should be unreachable
    assert last_exc is not None
    raise last_exc
