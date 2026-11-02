from __future__ import annotations

import sqlite3
from pathlib import Path

import typer

from kami.commands.add import STATUS_CHOICES
from kami.config import resolve_db_path
from kami.db import connect
from kami.formatting import console, emit, resolve_or_exit
from kami.repo import add_tag_to_series, remove_tag_from_series, update_series


def _summarize(updated_fields: dict[str, object]) -> str:
    summary_parts: list[str] = []

    for field_name in ("title", "status", "author"):
        if field_name in updated_fields:
            summary_parts.append(f"{field_name}={updated_fields[field_name]}")
    if "tags_added" in updated_fields:
        summary_parts.append(f"+{','.join(updated_fields['tags_added'])}")
    if "tags_removed" in updated_fields:
        summary_parts.append(f"-{','.join(updated_fields['tags_removed'])}")

    return " ".join(summary_parts)


def register(app: typer.Typer) -> None:
    @app.command("edit", help="Edit a series' metadata or tags.")
    def edit_cmd(
        ctx: typer.Context,
        query: str = typer.Argument(..., help="Series title (or unique prefix)"),
        new_title: str | None = typer.Option(None, "--title"),
        status: str | None = typer.Option(None, "--status", "-s"),
        author: str | None = typer.Option(None, "--author", "-a"),
        add_tags: list[str] = typer.Option([], "--add-tags"),
        remove_tags: list[str] = typer.Option([], "--remove-tags"),
    ) -> None:
        """Rename, change status/author, or add/remove tags on a resolved series."""
        if status is not None and status not in STATUS_CHOICES:
            raise typer.BadParameter(
                f"invalid status {status!r}; choose from {', '.join(STATUS_CHOICES)}",
                param_hint="--status",
            )

        db_path: Path = resolve_db_path(ctx.obj["db"])
        updated_fields: dict[str, object] = {}

        with connect(db_path) as conn:
            series_id = resolve_or_exit(
                conn,
                query,
                json_mode=ctx.obj["json"],
            )

            try:
                update_series(
                    conn,
                    series_id,
                    title=new_title,
                    status=status,
                    author=author,
                )
            except sqlite3.IntegrityError:
                console.print(
                    f"[red]error:[/red] cannot rename to {new_title!r}: "
                    "a series with that title and type already exists"
                )
                raise typer.Exit(code=1) from None

            if new_title is not None:
                updated_fields["title"] = new_title
            if status is not None:
                updated_fields["status"] = status
            if author is not None:
                updated_fields["author"] = author

            added_tags: list[str] = []
            removed_tags: list[str] = []

            for tag in add_tags:
                if add_tag_to_series(conn, series_id, tag):
                    added_tags.append(tag)
            for tag in remove_tags:
                if remove_tag_from_series(conn, series_id, tag):
                    removed_tags.append(tag)

        if added_tags:
            updated_fields["tags_added"] = added_tags
        if removed_tags:
            updated_fields["tags_removed"] = removed_tags

        if not updated_fields:
            console.print("[dim]No changes[/]")

        change_summary = _summarize(updated_fields)
        emit(
            f"Updated {query!r}: {change_summary}",
            json_mode=ctx.obj["json"],
            log_result={"id": series_id, **updated_fields},
        )
