from __future__ import annotations

import typer

from kami.config import resolve_db_path
from kami.db import init_schema
from kami.formatting import emit


def register(app: typer.Typer) -> None:
    @app.command("init")
    def init_cmd(ctx: typer.Context) -> None:
        db_path: str = resolve_db_path(ctx.obj["db"])
        is_new_database: bool = init_schema(db_path)

        if is_new_database:
            status_message: str = f"Initialized db at {db_path}"
        else:
            status_message: str = f"Db already Initialized at {db_path}"

        emit(
            status_message,
            json_mode=ctx.obj["json"],
            log_result={"path": str(db_path), "fresh": is_new_database},
        )
