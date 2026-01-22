from __future__ import annotations

import httpx
import json
from llm_transport_gateway.errors import (
    GatewayAuthError,
    GatewayClientError,
    GatewayRateLimitError,
    GatewayTimeoutError,
    GatewayUpstreamError,
    AIGatewayError,
)


def call_gemini(prompt: str, model: str, api_key: str, timeout_s: float) -> str:
    """
    Calls the Gemini API using raw HTTP and returns the text response.
    """
    if not api_key:
        raise GatewayAuthError("Missing Gemini API key.")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        with httpx.Client() as client:
            response = client.post(
                url,
                headers=headers,
                params=params,
                json=payload,
                timeout=timeout_s,
            )
        response.raise_for_status()

        try:
            response_data = response.json()
        except (json.JSONDecodeError, ValueError) as exc:
            raise GatewayUpstreamError("Gemini returned non-JSON response") from exc

        candidates = response_data.get("candidates", [])
        if not candidates:
            raise GatewayUpstreamError("Gemini returned no candidates.")
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            raise GatewayUpstreamError(
                "Gemini returned no parts in the first candidate."
            )
        text = parts[0].get("text")
        if not text:
            raise GatewayUpstreamError("Gemini returned no text in the first part.")
        return text

    except httpx.TimeoutException as exc:
        raise GatewayTimeoutError("Gemini timeout") from exc
    except httpx.RequestError as exc:
        raise GatewayUpstreamError("Gemini request error") from exc
    except httpx.HTTPStatusError as exc:
        raise _safe_err(exc) from exc


def _safe_err(exc: httpx.HTTPStatusError) -> AIGatewayError:
    """
    Maps HTTP errors to gateway-specific, safe-to-log exceptions.
    This avoids echoing potentially sensitive payload data in logs.
    """
    response = exc.response
    status_code = response.status_code

    # Always generate a generic message to avoid leaking upstream details
    message = f"Gemini API error: HTTP {status_code}"

    if status_code in (401, 403):
        return GatewayAuthError(message)
    if status_code == 429:
        return GatewayRateLimitError(message)
    if 400 <= status_code < 500:
        return GatewayClientError(message)
    if 500 <= status_code < 600:
        return GatewayUpstreamError(message)

    return GatewayUpstreamError(message)
