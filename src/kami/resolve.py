from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class SeriesRow:
    id: int
    title: str
    series_type: str


@dataclass(frozen=True)
class Resolved:
    series: SeriesRow


@dataclass(frozen=True)
class Ambiguous:
    query: str
    candidates: list[SeriesRow]


@dataclass(frozen=True)
class NotFound:
    query: str


Resolution = Resolved | Ambiguous | NotFound


def _fetch(conn: sqlite3.Connection, sql_query: str, params: tuple) -> list[SeriesRow]:
    series_records = conn.execute(sql_query, params).fetchall()

    return [
        SeriesRow(
            id=series_record["id"],
            title=series_record["title"],
            series_type=series_record["series_type"],
        )
        for series_record in series_records
    ]


def _escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def resolve_series(conn: sqlite3.Connection, search_query: str) -> Resolution:
    if not search_query or not search_query.strip():
        return NotFound(query="")

    cleaned_query: str = search_query.strip()

    exact_matches: list[SeriesRow] = _fetch(
        conn,
        "SELECT id, title, series_type FROM series WHERE title = ? COLLATE NOCASE",
        (cleaned_query,),
    )

    if len(exact_matches) > 1:
        return Ambiguous(query=cleaned_query, candidates=exact_matches)

    prefix_matches = _fetch(
        conn,
        "SELECT id, title, series_type FROM series "
        "WHERE title LIKE ? ESCAPE '\\' "
        "ORDER BY title",
        (_escape_like(cleaned_query) + "%",),
    )

    if len(prefix_matches) == 1:
        return Resolved(series=prefix_matches[0])
    if len(prefix_matches) > 1:
        return Ambiguous(query=cleaned_query, candidates=prefix_matches)

    return NotFound(query=cleaned_query)
