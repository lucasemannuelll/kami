from __future__ import annotations

import sys
from pathlib import Path

import typer

from kami.config import resolve_db_path
from kami.db import connect
from kami.formatting import console, emit, resolve_or_exit
from kami.repo import remove_series, get_series_detail


def _confirm_or_exit(detail: object, *, json_mode: bool) -> None:
    from kami.models import SeriesDetail

    assert isinstance(detail, SeriesDetail)

    chapter_count: int = detail.chapters_read
    chapter_word: str = "chapter" if chapter_count == 1 else "chapters"

    if not sys.stdin.isatty():
        console.print(
            f"[red]error:[/] refusing to delete {detail.series.title!r} "
            f"({chapter_count} {chapter_word}) "
            "without --yes in non-interactive context"
        )
        raise typer.Exit(code=10)
    console.print(
        f"Delete [bold]{detail.series.title}[/bold] and "
        f"{chapter_count} logged {chapter_word}? This cannot be undone."
    )

    confirmed: bool = typer.confirm("Continue?", default=False)
    if not confirmed:
        raise typer.Exit(code=10)


def register(app: typer.Typer) -> None:
    @app.command("rm", help="Delete a series and its chapters.")
    def rm_cmd(
        ctx: typer.Context,
        query: str = typer.Argument(
            ..., help="Series title (or unique prefix)"
        ),
        yes: bool = typer.Option(
            False, "--yes", "-y", help="Skip confirmation"
        ),
    ) -> None:
        """Remove a series (and cascade its chapters/tags links). Prompts unless --yes."""
        db_path: Path = resolve_db_path(ctx.obj["db"])
        with connect(db_path) as conn:
            series_id: int | None = resolve_or_exit(
                conn, query, json_mode=ctx.obj["json"]
            )
            detail = get_series_detail(conn, series_id)

            assert detail is not None

            if not yes:
                _confirm_or_exit(detail, json_mode=ctx.obj["json"])

            remove_series(conn, series_id)

        emit(
            f"Deleted {detail.series.title!r} "
            f"({detail.chapters_read} "
            f"chapter{'s' if detail.chapters_read != 1 else ''}).",
            json_mode=ctx.obj["json"],
            log_result={
                "id": series_id,
                "title": detail.series.title,
                "chapters_deleted": detail.chapters_read,
            },
        )
