"""Text helpers (slugification, etc.)."""

from __future__ import annotations

import re
import unicodedata


def slugify(value: str) -> str:
    """Return a filesystem/URL friendly slug for category names."""
    value = (value or "").replace("&", "et")
    value = "".join(ch for ch in value if ch.isalnum() or ch.isspace() or ch in "-_")
    value = (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    value = value.lower().strip()
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"[^a-z0-9-]", "", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value
