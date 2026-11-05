from __future__ import annotations

from datetime import date


class DateParseError(ValueError):
    """Raised when a date string cannot be parsed."""


def parse_date(date_str: str) -> date:
    if not date_str:
        raise DateParseError("date is empty")

    try:
        return date.fromisoformat(date_str)
    except ValueError as e:
        raise DateParseError(
            f"Invalid: {date_str!r}\nExpected: YYYY-MM-DD"
        ) from e


def today_iso() -> str:
    return date.today().isoformat()
