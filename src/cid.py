"""
CID library based on UUIDv7-shaped identifiers and SHA-256 content binding.

A CID has the canonical form:
    cid:<uuidv7>-<sha256_hex>
"""

from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import threading
import time
import uuid
from typing import Optional

CID_PREFIX = "cid:"
_SHA256_HEX_LEN = 64
_CID_RE = re.compile(
    r"^cid:([0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})-([0-9a-f]{64})$"
)

_STATE_LOCK = threading.Lock()
_LAST_TS_MS = -1
_RAND_A_COUNTER = secrets.randbits(12)


def _to_bytes(content: bytes | bytearray | memoryview) -> bytes:
    if isinstance(content, bytes):
        return content
    if isinstance(content, (bytearray, memoryview)):
        return bytes(content)
    raise TypeError("content must be bytes-like")


def generate_uuidv7() -> uuid.UUID:
    """
    Generate a UUIDv7-compatible UUID.

    This implementation includes a monotonic counter in rand_a to preserve
    ordering for rapid calls within the same millisecond and tolerate small
    clock regressions.
    """
    global _LAST_TS_MS, _RAND_A_COUNTER

    now_ms = int(time.time_ns() // 1_000_000)
    if now_ms >= 1 << 48:
        raise ValueError("timestamp is too large for UUIDv7")

    with _STATE_LOCK:
        ts_ms = now_ms
        if ts_ms < _LAST_TS_MS:
            ts_ms = _LAST_TS_MS

        if ts_ms == _LAST_TS_MS:
            _RAND_A_COUNTER = (_RAND_A_COUNTER + 1) & 0xFFF
            if _RAND_A_COUNTER == 0:
                ts_ms = _LAST_TS_MS + 1
        else:
            _RAND_A_COUNTER = secrets.randbits(12)

        _LAST_TS_MS = ts_ms
        rand_a = _RAND_A_COUNTER

    rand_b = secrets.randbits(62)

    uuid_int = (ts_ms << 80) | (0x7 << 76) | (rand_a << 64) | (0x2 << 62) | rand_b
    return uuid.UUID(int=uuid_int)


def mint_cid(content: bytes | bytearray | memoryview) -> str:
    """
    Mint a CID for the given content.

    Identical content can receive different CIDs because the UUIDv7 component
    is freshly generated on each call.
    """
    content_bytes = _to_bytes(content)
    generated_uuid = generate_uuidv7()
    sha256_hash = hashlib.sha256(content_bytes).hexdigest()
    return f"{CID_PREFIX}{generated_uuid}-{sha256_hash}"


def validate_cid(cid: str, content: bytes | bytearray | memoryview) -> bool:
    """
    Validate a CID against corresponding content bytes.

    Returns False for any invalid inputs or mismatches.
    """
    try:
        content_bytes = _to_bytes(content)
    except TypeError:
        return False

    parsed = _parse_cid(cid)
    if parsed is None:
        return False

    _, hash_from_cid = parsed
    content_hash = hashlib.sha256(content_bytes).hexdigest()
    return hmac.compare_digest(content_hash, hash_from_cid)


def get_hash_from_cid(cid: str) -> Optional[str]:
    """Extract the SHA-256 hex digest from a valid CID string."""
    parsed = _parse_cid(cid)
    if parsed is None:
        return None
    _, hash_from_cid = parsed
    return hash_from_cid


def _parse_cid(cid: str) -> Optional[tuple[uuid.UUID, str]]:
    if not isinstance(cid, str):
        return None

    match = _CID_RE.fullmatch(cid)
    if match is None:
        return None

    uuid_str, hash_from_cid = match.groups()
    try:
        parsed_uuid = uuid.UUID(uuid_str)
    except ValueError:
        return None

    if parsed_uuid.version != 7:
        return None
    if parsed_uuid.variant != uuid.RFC_4122:
        return None

    if len(hash_from_cid) != _SHA256_HEX_LEN:
        return None

    return parsed_uuid, hash_from_cid


__all__ = [
    "CID_PREFIX",
    "generate_uuidv7",
    "mint_cid",
    "validate_cid",
    "get_hash_from_cid",
]
