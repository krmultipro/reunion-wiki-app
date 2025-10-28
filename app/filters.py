"""Custom Jinja filters."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from flask import Flask


def format_date(value: Any, fmt: str = "%d/%m/%Y") -> str:
    """Format SQLite dates stored as string or datetime."""
    if not value:
        return ""
    if isinstance(value, datetime):
        return value.strftime(fmt)

    if isinstance(value, str):
        for pattern in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                parsed = datetime.strptime(value, pattern)
                return parsed.strftime(fmt)
            except ValueError:
                continue
    return str(value)


def init_app(app: Flask) -> None:
    """Register custom filters."""
    app.jinja_env.filters["format_date"] = format_date
