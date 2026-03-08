from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional
import uuid

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
    max_tokens: Optional[int] = None  # accepted but provider may ignore


class AIGatewayClient:
    """
    LLM Transport Gateway public API.
    Contract: accepts prompt, returns raw model text unchanged.
    Handles only transport concerns (security, retries, stability, logging).
    """

    def __init__(self, cfg: Optional[GatewayConfig] = None):
        self.cfg = cfg or load_config()

    def call(self, prompt: str, *, options: Optional[CallOptions] = None) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt must be a non-empty string")

        # GUARDRAIL: If API evolves to accept structured payloads (e.g., JSON bodies),
        # implement an explicit blocklist here for fields like 'hasAuthorityBearer',
        # 'exercisedUnderMandate', 'decision', 'approved', 'eligible' to prevent
        # accidental "authority smuggling" into the transport layer.
        # This service is transport-only and must not interpret or enforce authority semantics.

        request_id = str(uuid.uuid4())  # Generate a unique request_id

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
            "llm_transport_gateway.call.start",
            request_id=request_id,  # Add request_id
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
                    raise GatewayConfigError(
                        "Missing GEMINI_API_KEY (or AI_GATEWAY_GEMINI_API_KEY)."
                    )
                return call_gemini(
                    prompt=prompt,
                    model=model,
                    api_key=self.cfg.gemini_api_key,
                    timeout_s=timeout_s,
                )

            raise GatewayConfigError(f"Unknown provider: {provider}")

        try:
            out = run_with_retry(_invoke, policy, request_id)
            ms = int((time.time() - t0) * 1000)
            log_event(
                "llm_transport_gateway.call.ok",
                request_id=request_id,  # Add request_id
                provider=provider,
                model=model,
                latency_ms=ms,
                prompt_hash8=ph,
            )
            return out
        except Exception as e:
            ms = int((time.time() - t0) * 1000)
            log_event(
                "llm_transport_gateway.call.fail",
                request_id=request_id,
                provider=provider,
                model=model,
                latency_ms=ms,
                prompt_hash8=ph,
                error_type=type(e).__name__,
            )
            raise
