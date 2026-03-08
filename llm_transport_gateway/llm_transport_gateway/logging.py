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

    # Only write to file if AI_GATEWAY_LOG_DIR is explicitly set
    if os.getenv("AI_GATEWAY_LOG_DIR"):
        try:
            (_log_dir() / "llm_transport_gateway.log.jsonl").open("a", encoding="utf-8").write(
                line + "\n"
            )
        except Exception:
            # Logging must never break the call path
            pass
