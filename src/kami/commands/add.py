from __future__ import annotations

import sqlite3
from typing import Annotated

import typer

from kami.config import resolve_db_path
from kami.dates import DateParseError, parse_date
from kami.db import connect
from kami.formatting import console, emit
from kami.repo import add_series

TYPE_CHOICES = [
    "Manga",
    "Manhwa",
    "Manhua",
    "Novel",
    "Comic",
]
STATUS_CHOICES = [
    "Reading",
    "Completed",
    "On Hold",
    "Dropped",
]


def _validate_choice(
    value,
    choices,
    flag,
) -> None:
    if value not in choices:
        raise typer.BadParameter(
            f"invalid value {value!r}; choose from {', '.join(choices)}",
            param_hint=flag,
        )


def register(app: typer.Typer) -> None:
    @app.command("add", help="Add a series to the ledger.")
    def add_cmd(
        ctx: typer.Context,
        title: str = typer.Argument(..., help="Series title"),
        series_type: str = typer.Option(
            ...,
            "--type",
            "-t",
            help="Medium: Manga, Manhwa, Manhua, Novel",
        ),
        author: str | None = typer.Option(None, "--author", "-a"),
        status: str = typer.Option("Reading", "--status", "-s"),
        tags: Annotated[list[str], typer.Option("--tag", help="Repeatable")] = [],
        started_at: str | None = typer.Option(
            None, "--started", help="YYYY-MM-DD, or 'pre-catalog'"
        ),
    ) -> None:
        """
        Register a new series.
        Available types: Manga, Manhwa, Manhua, Novel, Comic.
        """
        _validate_choice(series_type, TYPE_CHOICES, "--type")
        _validate_choice(status, STATUS_CHOICES, "--status")

        if started_at is not None and started_at != "pre-catalog":
            try:
                parse_date(started_at)
            except DateParseError as e:
                raise typer.BadParameter(
                    str(e), param_hint="--started"
                ) from e

        db_path = resolve_db_path(ctx.obj["db"])

        with connect(db_path) as conn:
            try:
                new_id = add_series(
                    conn,
                    title=title,
                    series_type=series_type,
                    author=author,
                    status=status,
                    started_at=started_at,
                    tags=tags,
                )
            except sqlite3.IntegrityError:
                console.print(
                    f"[red]error:[/] series {title!r} - "
                    f"[{series_type}] already exists"
                )
                raise typer.Exit(code=1) from None

        emit(
            f"Added {title!r} [{series_type}] as {status}",
            json_mode=ctx.obj["json"],
            log_result={
                "id": new_id,
                "series_type": series_type,
                "status": status,
                "author": author,
                "tags": tags,
                "started_at": started_at,
            },
        )
