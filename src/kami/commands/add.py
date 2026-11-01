from __future__ import annotations
import typer 
import sqlite3
from kami.config import resolve_db_path
from kami.db import connect
from kami.dates import DateParseError, parse_date
from kami.formatting import console, emit
from kami.repo import add_series

TYPE_CHOICES: list[str] = ["Manga", "Manhwa", "Manhua", "Novel", "Webtoon", "Comic"]
STATUS_CHOICES: list[str] = ["Reading", "Completed", "On Hold", "Dropped"]

def register(app: typer.Typer) -> None:
    @app.command("add")
    def add_cmd(
            ctx: typer.Context,
            title: str = typer.Argument(..., help="Series title"),
            type: str = typer.Option(
                ..., "--type", "-t",
                help="Medium: Manga, Manhwa, Manhua, Novel, Webtoon",
            ),
            author: str | None = typer.Option(None, "--author", "-a"),
            status: str = typer.Option("Reading", "--status", "-s"),
            tags: list[str] = typer.Option([], "--tag", help="Repeatable"),
            started: str | None = typer.Option(
                None, "--started",
                help="YYYY-MM-DD, or 'pre-catalog'",
            ),
        ) -> None:
        raise NotImplemented("Tired as fuck, will implement later")
