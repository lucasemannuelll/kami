from __future__ import annotations

import sys

import typer

from kami.chapters import ChapterSpecError, parse_chapter_spec
from kami.config import resolve_db_path
from kami.db import connect
from kami.formatting import console, render_unlog_result, resolve_or_exit
from kami.repo import chapter_exists, unlog_chapters

_CONFIRM_THRESHOLD = 10


def _parse_spec(chapter_spec: str) -> list[str]:
    try:
        return parse_chapter_spec(chapter_spec)
    except ChapterSpecError as e:
        raise typer.BadParameter(str(e), param_hint="SPEC") from e


def _filter_existing(conn, series_id: int, chapters: list[str]) -> list[str]:
    return [ch for ch in chapters if chapter_exists(conn, series_id, ch)[0]]


def _report_dry_run(
    chapters: list[str],
    delete: bool,
    json_mode: bool,
) -> None:
    if json_mode:
        import json

        print(
            json.dumps(
                {
                    "dry_run": True,
                    "chapters": chapters,
                    "delete": delete,
                }
            )
        )
        return

    action_description: str = "delete" if delete else "clear read date on"
    console.print(
        f"Would {action_description} {len(chapters)} chapter(s): {', '.join(chapters)}"
    )


def _confirm_or_exit(chapter_count: int) -> None:
    if not sys.stdin.isatty():
        console.print(
            f"[red]error:[/] refusing to delete {chapter_count} "
            "chapters without --yes in non-interactive context"
        )
        raise typer.Exit(code=10)

    confirmed = typer.confirm(
        f"Delete {chapter_count} chapter rows? This cannot be undone",
        default=False,
    )

    if not confirmed:
        raise typer.Exit(code=10)


def register(app: typer.Typer) -> None:
    @app.command("unlog", help="Clear read dates or delete chapter rows.")
    def unlog_cmd(
        ctx: typer.Context,
        query: str = typer.Argument(
            ...,
            help="Series title (or unique prefix)",
        ),
        spec: str = typer.Argument(..., help="Chapter spec"),
        delete: bool = typer.Option(
            False,
            "--delete",
            help="Delete rows entirely (default: clear read date)",
        ),
        yes: bool = typer.Option(
            False,
            "--yes",
            "-y",
            help="Skip confirmation",
        ),
        dry_run: bool = typer.Option(
            False,
            "--dry-run",
            help="Show what would change",
        ),
    ) -> None:
        """Without --delete: set read_date=NULL. With --delete: remove rows (prompts at >=10)."""
        chapters = _parse_spec(spec)

        db_path = resolve_db_path(ctx.obj["db"])

        with connect(db_path) as conn:
            series_id = resolve_or_exit(
                conn,
                query,
                json_mode=ctx.obj["json"],
            )

            matched = _filter_existing(conn, series_id, chapters)
            if not matched:
                console.print("[dim]No matching chapters; nothing to do.[/]")
                return

            if dry_run:
                _report_dry_run(matched, delete, ctx.obj["json"])
                return

            if delete and len(matched) >= _CONFIRM_THRESHOLD and not yes:
                _confirm_or_exit(len(matched))

            unlog_chapters(conn, series_id, matched, delete=delete)

        render_unlog_result(
            title=query,
            chapters=matched,
            delete=delete,
            json_mode=ctx.obj["json"],
            dry_run=False,
        )
