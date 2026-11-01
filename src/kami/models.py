from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Chapter:
    chapter: str
    read_date: str | None

@dataclass(frozen=True)
class Series:
    id: int
    title: str
    series_type: str
    author: str | None
    status: str
    started: str | None
    tags: tuple[str, ...] = field(default_factory=tuple)

@dataclass(frozen=True)
class SeriesSummary:
    id: int
    title: str
    series_type: str
    status: str
    author: str | None
    tags: tuple[str, ...]
    chapters_read: int
    last_read: str | None

@dataclass(frozen=True)
class SeriesDetail:
    series: Series
    chapters_read: int
    last_chapters: tuple[Chapter, ...]
