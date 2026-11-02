from __future__ import annotations

import json
from typing import Any

from rich.console import Console
from rich.table import Table

from kami.models import SeriesDetail, SeriesSummary
from kami.resolve import Ambiguous, NotFound

console = Console(stderr=False)
error_console = Console(stderr=True)


class ResolveExit(Exception):
    def __init__(self, code: int) -> None:
        super().__init__(f"resolve failed (exit {code})")
        self.code = code


def emit(text: str, *, json_mode: bool, log_result: dict[str, Any]) -> None:
    if json_mode:
        typer_echo(json.dumps(log_result))
    else:
        console.print(text)


def typer_echo(text: str) -> None:
    print(text)


def human_date(read_date: str | None) -> str:
    return read_date if read_date is not None else "unknown"


def human_tags(tags: tuple[str, ...]) -> str:
    return ", ".join(tags) if tags else "-"


def render_list(summaries: list[SeriesSummary], *, json_mode: bool) -> None:
    if json_mode:
        print(json.dumps([_summary_to_dict(summary) for summary in summaries]))
        return

    if not summaries:
        console.print("[dim]No series match[/]")
        return

    table = Table(show_header=True, header_style="bold")
    table.add_column("Title")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Read", justify="right")
    table.add_column("Tags")

    for summary in summaries:
        table.add_row(
            summary.title,
            summary.series_type,
            summary.status,
            str(summary.chapters_read),
            human_tags(summary.tags),
        )

    console.print(table)


def _summary_to_dict(summary: SeriesSummary) -> dict[str, Any]:
    return {
        "id": summary.id,
        "title": summary.title,
        "type": summary.series_type,
        "status": summary.status,
        "author": summary.author,
        "tags": list(summary.tags),
        "chapters_read": summary.chapters_read,
        "last_read": summary.last_read,
    }


def render_show(detail: SeriesDetail, *, json_mode: bool) -> None:
    if json_mode:
        print(json.dumps(_detail_to_dict(detail)))
        return

    series = detail.series
    console.print(f"[bold]{series.title}[/] [dim]{series.series_type}[/]")
    console.print(f"    Status: {series.status}")

    if series.author:
        console.print(f"    Author: {series.author}")
    if series.started_at:
        console.print(f"    Started at: {series.started_at}")

    console.print(f"    Tags: {human_tags(series.tags)}")
    console.print(f"    Chapters read: {detail.chapters_read}")

    if not detail.last_chapters:
        console.print("    [dim]No chapters logged yet[/]")
        return

    console.print("    Last chapters:")
    for chapter in detail.last_chapters:
        console.print(
            f"    • {chapter.chapter} - {human_date(chapter.read_date)}"
        )


def _detail_to_dict(detail: SeriesDetail) -> dict[str, Any]:
    series = detail.series

    return {
        "id": series.id,
        "title": series.title,
        "type": series.series_type,
        "status": series.status,
        "author": series.author,
        "started_at": series.started_at,
        "tags": list(series.tags),
        "chapters_read": detail.chapters_read,
        "last_chapters": [
            {"chapter": chapter.chapter, "read_date": chapter.read_date}
            for chapter in detail.last_chapters
        ],
    }


def render_log_results(
    *,
    title: str,
    chapters: list[str],
    read_date: str,
    json_mode: bool,
    dry_run: bool,
) -> None:
    log_result = {
        "series": title,
        "chapters": chapters,
        "read_date": read_date,
        "dry_run": dry_run,
    }
    if json_mode:
        print(json.dumps(log_result))
        return

    action_prefix = "Would log " if dry_run else "Logged"
    chapter_word = "chapter" if len(chapters) == 1 else "chapters"
    console.print(
        f"{action_prefix} {len(chapters)} {chapter_word} "
        f"for [bold]{title}[/]".strip()
    )


def render_ambiguous(
    query: str, candidates: list[Any], *, json_mode: bool
) -> None:
    if json_mode:
        print(
            json.dumps(
                {
                    "error": "ambiguous",
                    "query": query,
                    "candidates": [
                        {
                            "id": candidate.id,
                            "title": candidate.title,
                            "series_type": candidate.series_type,
                        }
                        for candidate in candidates
                    ],
                }
            )
        )
        return
    error_console.print(f"[red]error:[/] {query!r} matches multiple series: ")
    for candidate in candidates:
        error_console.print(
            f"    • {candidate.title} [{candidate.series_type}]"
        )
    error_console.print("Use a longer query, or the full title")


def render_not_found(query: str, *, json_mode: bool) -> None:
    if json_mode:
        print(json.dumps({"error": "not_found", "query": query}))
        return

    error_console.print(f"[red]error:[/] no series matching {query!r}")


def resolve_or_exit(conn: Any, query: str, *, json_mode: bool) -> int | None:
    from kami.resolve import resolve_series

    resolution_result = resolve_series(conn, query)

    if isinstance(resolution_result, Ambiguous):
        render_ambiguous(
            resolution_result.query,
            resolution_result.candidates,
            json_mode=json_mode,
        )
        return ResolveExit(2)
    if isinstance(resolution_result, NotFound):
        render_not_found(
            resolution_result.query,
            resolution_result.candidates,
            json_mode=json_mode,
        )
        return ResolveExit(3)

    return resolution_result.series.id
