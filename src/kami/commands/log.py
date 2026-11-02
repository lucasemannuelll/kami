from __future__ import annotations

import typer

from kami.chapters import ChapterSpecError, parse_chapter_spec
from kami.config import resolve_db_path
from kami.dates import DateParseError, parse_date, today_iso
from kami.db import connect
from kami.formatting import console, render_log_results, resolve_or_exit
from kami.repo import chapter_exists, log_chapters


def _report_dry_run(
    conn,
    series_id: int,
    chapters: list[str],
    read_date: str,
    json_mode: bool
) -> None:
    new: list[str] = []
    update: list[str] = []

    for ch in chapters:
        exists, _prev = chapter_exists(conn, series_id, ch)
        (update if exists else new).append(ch)

    if json_mode:
        import json

        print(json.dumps({
            "dry_run": True,
            "new": new,
            "update": update,
            "read_date": read_date,
        }))
        return

    if new:
        console.print(f"New:    {', '.join(new)}")
    if update:
        console.print(f"Update: {', '.join(update)}")
    if not new and not update:
        console.print("[dim]Nothing to do[/]")
    else:
        console.print(f"[dim]Would log {len(chapters)} "
                      f"chapter(s) on {read_date}.[/]")


def _resolve_date(date_input: str | None) -> str:
    if date_input is None:
        return today_iso()
    try:
        return parse_date(date_input).isoformat()
    except DateParseError as e:
        raise typer.BadParameter(str(e), param_hint="--date") from e


def _parse_spec(chapter_spec: str) -> list[str]:
    try:
        return parse_chapter_spec(chapter_spec)
    except ChapterSpecError as e:
        raise typer.BadParameter(str(e), param_hint="SPEC") from e


def register(app: typer.Typer) -> None:
    @app.command("log")
    def log_cmd(
        ctx: typer.Context,
        query: str = typer.Argument(
            ..., help="Series title (or unique prefix)"
        ),
        spec: str = typer.Argument(
            ..., help="Chapter spec: '213', '218-225', '12.1,12.2,13'",
        ),
        date: str | None = typer.Option(
            None, "--date", "-d",
            help="YYYY-MM-DD (default: today)",
        ),
        dry_run: bool = typer.Option(
            False, "--dry-run", help="Show what would change"
        ),
    ) -> None:
        read_date = _resolve_date(date)
        chapters = _parse_spec(spec)

        db_path = resolve_db_path(ctx.obj["db"])

        with connect(db_path) as conn:
            series_id = resolve_or_exit(
                            conn,
                            query,
                            json_mode=ctx.obj["json"]
                        )

            if dry_run:
                _report_dry_run(
                    conn,
                    series_id,
                    chapters,
                    read_date, ctx.obj["json"]
                )
                return
            log_chapters(
                conn,
                series_id,
                chapters,
                read_date,
            )

        render_log_results(
            title=query,
            chapters=chapters,
            read_date=read_date,
            json_mode=ctx.obj["json"],
            dry_run=False,
        )
