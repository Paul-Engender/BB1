# Transport-level errors only. No semantics, no workflow logic.

from __future__ import annotations


class AIGatewayError(RuntimeError):
    """Base class for LLM Transport Gateway transport errors."""


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
