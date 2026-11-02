from __future__ import annotations

import typer

from kami.chapters import ChapterSpecError, parse_chapter_spec
from kami.config import resolve_db_path
from kami.dates import DateParseError, parse_date, today_iso
from kami.db import connect
from kami.formatting import console, render_log_result, resolve_or_exit
from kami.repo import chapter_exists, log_chapters


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
            series_id = resolve_or_exit(conn, query, json_mode=ctx.obj["json"])

            

