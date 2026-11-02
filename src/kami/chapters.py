from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Final

_RANGE_RE: Final[re.Pattern[str]] = re.compile(
    r"^\s*(\d[\w.]*)\s*[-–]\s*(\d[\w.]*)\s*$"
)
_INT_OR_DEC_RE: Final[re.Pattern[str]] = re.compile(r"^\d+(?:\.\d+)?$")


class ChapterSpecError(ValueError):
    """Raised when a chapter spec cannot be parsed."""


def parse_chapter_spec(chapter_spec: str) -> list[str]:
    if not chapter_spec or not chapter_spec.strip():
        raise ChapterSpecError("empty chapter spec")

    unique_chapters: list[str] = []
    seen_chapters: set[str] = set()

    for raw_item in chapter_spec.split(","):
        item_spec: str = raw_item.strip()
        if not item_spec:
            raise ChapterSpecError(f"empty item in spec: {chapter_spec!r}")

        for chapter in _expand_item(item_spec):
            if chapter not in seen_chapters:
                seen_chapters.add(chapter)
                unique_chapters.append(chapter)

    return unique_chapters


def _expand_item(item_spec: str) -> list[str]:
    range_match: re.Match[str] | None = _RANGE_RE.match(item_spec)
    if not range_match:
        return [item_spec]

    start_str: str = range_match.group(1)
    end_str: str = range_match.group(2)

    if not (_INT_OR_DEC_RE.match(start_str) and _INT_OR_DEC_RE.match(end_str)):
        raise ChapterSpecError(f"must be numeric: {item_spec!r}")

    return _expand_range(start_str, end_str)


def _expand_range(start_str: str, end_str: str) -> list[str]:
    try:
        range_start: Decimal = Decimal(start_str)
        range_end: Decimal = Decimal(end_str)
    except InvalidOperation as e:
        raise ChapterSpecError(f"invalid: {start_str!r}-{end_str!r}") from e

    if range_start > range_end:
        raise ChapterSpecError(f"start higher than end: {start_str}-{end_str}")

    both_are_integer: bool = (
        range_start == range_start.to_integral_value()
        and range_end == range_end.to_integral_value()
    )
    step_size: Decimal = Decimal(1) if both_are_integer else Decimal("0.1")

    expanded_range: list[str] = []
    current_value: Decimal = range_start

    while current_value <= range_end:
        expanded_range.append(_format_decimal(current_value))
        current_value += step_size

    return expanded_range


def _format_decimal(decimal_value: Decimal) -> str:
    if decimal_value == decimal_value.to_integral_value():
        return str(int(decimal_value))

    return format(decimal_value.normalize(), "f")


def sort_key(chapter: str) -> tuple[int, float, str]:
    if _INT_OR_DEC_RE.match(chapter):
        return (0, float(chapter), chapter)

    return (1, 0.0, chapter)
