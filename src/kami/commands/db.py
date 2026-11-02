from __future__ import annotations

import shutil
import subprocess
import sys

import typer

from kami.config import resolve_db_path


def register(app: typer.Typer) -> None:
    db_app = typer.Typer(
        help="Database maintenance and introspection.", no_args_is_help=True
    )

    app.add_typer(db_app, name="db")

    @db_app.command("path", help="Print the resolved database path.")
    def db_path_cmd(ctx: typer.Context) -> None:
        """Show the resolved DB path (CLI --db → $KAMI_DB → platformdirs)."""
        db_path = resolve_db_path(ctx.obj["db"])
        exists = db_path.exists()

        if ctx.obj["json"]:
            import json
            print(json.dumps({
                "path": str(db_path),
                "exists": exists,
                "size": db_path.stat().st_size if exists else None,
            }))
        else:
            print(str(db_path))

    @db_app.command("shell", help="Open an interactive sqlite3 shell on the DB.")
    def db_shell_cmd(ctx: typer.Context) -> None:
        """Run sqlite3 with .headers on / .mode box; extra args go before the DB path."""
        db_path = resolve_db_path(ctx.obj["db"])

        if not db_path.exists():
            print(f"error: database not found at {db_path}", file=sys.stderr)
            print("run 'kami init' to create it", file=sys.stderr)
            raise typer.Exit(code=5)
        sqlite_bin = shutil.which("sqlite3")

        if sqlite_bin is None:
            print(
                "error: sqlite3 binary not found on PATH. "
                "Install sqlite3 or use 'kami db path' "
                "and open the file yourself.",
                file=sys.stderr,
            )
            raise typer.Exit(code=5)

        extra_args = ctx.args
        cmd = [
            sqlite_bin,
            "-cmd",
            ".headers on",
            "-cmd",
            ".mode box",
            *extra_args,
            str(db_path),
        ]

        if ctx.obj["verbose"]:
            print("exec:", " ".join(repr(a) for a in cmd), file=sys.stderr)

        try:
            sys.exit(subprocess.call(cmd))
        except KeyboardInterrupt:
            raise typer.Exit(code=0) from None
