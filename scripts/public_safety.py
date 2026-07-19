#!/usr/bin/env python3
"""Shared fail-closed checks for data projected onto public surfaces."""
from __future__ import annotations

import re
from collections.abc import Iterator


FORBIDDEN_VALUE_MARKERS = (
    ".private/",
    "private/",
    "payload_path",
    "raw-research",
    "raw_capture",
    "authorization: bearer",
    "-----begin private key-----",
)

FORBIDDEN_FIELD_NAMES = {
    "authorization",
    "client_material",
    "client_payload",
    "cookie",
    "payload_bytes",
    "payload_path",
    "raw_capture",
    "raw_conversation",
    "raw_conversations",
    "request_body",
    "response_body",
    "secret",
}

# Match path values at the beginning of a string or after ordinary prose/JSON
# boundaries. URL schemes do not match because their drive-like `s:/` fragment
# is preceded by another word character rather than one of these boundaries.
ABSOLUTE_MACHINE_PATH = re.compile(
    r"(?:^|[\s\"'(=\[])(?:[A-Za-z]:[\\/]|\\\\[^\\/\s]+[\\/][^\s]+|/[A-Za-z0-9._-]+(?:[\\/][^\s]*)?)"
)


def _walk(value: object, location: str = "$") -> Iterator[tuple[str, str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            child_location = f"{location}.{key_text}"
            yield child_location, "field", key_text
            yield from _walk(child, child_location)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _walk(child, f"{location}[{index}]")
    elif isinstance(value, str):
        yield location, "value", value


def public_content_violations(payload: object) -> list[str]:
    """Return stable, non-payload-bearing descriptions of public-data violations."""
    violations: set[str] = set()
    for location, kind, text in _walk(payload):
        lowered = text.casefold()
        normalized = lowered.replace("\\", "/")
        if kind == "field":
            if lowered in FORBIDDEN_FIELD_NAMES:
                violations.add(f"forbidden field at {location}")
            continue
        for marker in FORBIDDEN_VALUE_MARKERS:
            if marker in normalized:
                violations.add(f"forbidden marker {marker!r} at {location}")
        if ABSOLUTE_MACHINE_PATH.search(text):
            violations.add(f"absolute machine path at {location}")
        if normalized.startswith("file://"):
            violations.add(f"file URI at {location}")
    return sorted(violations)
