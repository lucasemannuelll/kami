from __future__ import annotations

import sqlite3
import sys

import typer

from kami.db import KamiError
from kami.formatting import ResolveExit, error_console

app = typer.Typer(
    name="kami",
    help="A minimal reading ledger for manga, manhwa, manhua, and web novels.",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def root(
    ctx: typer.Context,
    db: str | None = typer.Option(
        None,
        "--db",
        help="Path to the SQLite database (overrides $KAMI_DB)",
    ),
    json_mode: bool = typer.Option(
        False,
        "--json",
        help="Output machine-readable JSON.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Print debug info (SQL, exec commands)",
    ),
) -> None:
    ctx.obj = {
        "db": db,
        "json": json_mode,
        "verbose": verbose,
    }


def _register_commands() -> None:
    from kami.commands import add, db, edit, init, log, rm, show, unlog
    from kami.commands import list as list_mod

    init.register(app)
    add.register(app)
    list_mod.register(app)
    show.register(app)
    edit.register(app)
    rm.register(app)
    log.register(app)
    unlog.register(app)
    db.register(app)


_register_commands()


def main() -> None:
    try:
        app()
    except ResolveExit as e:
        sys.exit(e.code)
    except KamiError as e:
        error_console.print(f"[red]error:[/] {e}")
        sys.exit(1)
    except sqlite3.Error as e:
        error_console.print(f"[red]error:[/] database error: {e}")
        sys.exit(5)


if __name__ == "__main__":
    main()
