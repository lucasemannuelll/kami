from __future__ import annotations


import typer

from kami.config import resolve_db_path
from kami.db import connect
from kami.formatting import render_show, resolve_or_exit
from kami.repo import get_series_detail


def register(app: typer.Typer) -> None:
    @app.command("show", help="Show details for one series.")
    def show_cmd(
        ctx: typer.Context,
        query: str = typer.Argument(
            ..., help="Series title (or unique prefix)"
        ),
    ) -> None:
        """Print a series' metadata and its 3 most recent chapters."""
        db_path = resolve_db_path(ctx.obj["db"])
        with connect(db_path) as conn:
            series_id = resolve_or_exit(
                conn, query, json_mode=ctx.obj["json"]
            )
            
            detail = get_series_detail(conn, series_id)

            assert detail is not None
        render_show(detail, json_mode=ctx.obj["json"])
