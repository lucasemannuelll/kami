from __future__ import annotations
import typer
from kami.config import resolve_db_path
from kami.db import connect
from kami.formatting import render_list
from kami.repo import list_series
from kami.commands.add import STATUS_CHOICES, TYPE_CHOICES
from pathlib import Path

def register(app: typer.Typer) -> None:
    @app.command("list")
    def list_cmd(ctx: typer.Context,
                 status: str | None = typer.Option(None, "--status", "-s"),
                 series_type: str | None = typer.Option(None, "--type", "-t"),
                 tags: list[str] = typer.Option([], "--tag", help="repeatable; AND semantics"),
                 ) -> None:
        if status is not None and status not in STATUS_CHOICES:
            raise typer.BadParameter(f"invalid status {status!r}; choose from {', '.join(STATUS_CHOICES)}",
                                     param_hint="--status",
                                )
        if series_type is not None and series_type not in TYPE_CHOICES:
            raise typer.BadParameter(f"invalid type {type!r}; choose from {', '.join(TYPE_CHOICES)}",
                                     param_hint="--type",
        )

        db_path: Path = resolve_db_path(ctx.obj["db"])
        with connect(db_path) as conn:
            summaries = list_series(conn, status=status, series_type=series_type, tags=tags)
        render_list(summaries, json_mode=ctx.obj["json"])

