from __future__ import annotations

import sqlite3

from kami.models import Chapter, Series, SeriesDetail, SeriesSummary


def _set_tags(
    conn: sqlite3.Connection, series_id: int, tags: list[str]
) -> None:
    for tag in tags:
        add_tag_to_series(conn, series_id, tag)


def _ensure_tag(conn: sqlite3.Connection, name: str) -> int:
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (name,))
    tag_record = cursor.execute(
        "SELECT id FROM tags WHERE name = ? COLLATE NOCASE", (name,)
    ).fetchone()

    assert tag_record is not None
    return int(tag_record["id"])


def _tags_for(conn: sqlite3.Connection, series_id: int) -> tuple[str, ...]:
    cursor = conn.cursor()
    tag_records = cursor.execute(
        "SELECT t.name FROM tags t "
        "JOIN series_tags st ON st.tag_id = t.id "
        "WHERE st.series_id = ? "
        "ORDER BY t.name COLLATE NOCASE",
        (series_id,),
    ).fetchall()

    return tuple(tag_record["name"] for tag_record in tag_records)


def add_series(
    conn: sqlite3.Connection,
    *,
    title: str,
    series_type: str,
    author: str | None,
    status: str,
    started_at: str | None,
    tags: list[str],
) -> int:
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO series (title, series_type, author, status, started_at)"
        "VALUES (?, ?, ?, ?, ?)",
        (title, series_type, author, status, started_at),
    )

    series_id = cursor.lastrowid

    assert series_id is not None
    _set_tags(conn, series_id, tags)

    return series_id


def update_series(
    conn: sqlite3.Connection,
    series_id: int,
    *,
    title: str | None,
    author: str | None,
    status: str | None,
) -> None:
    set_clauses: list[str] = []
    query_params: list[object] = []

    if title is not None:
        set_clauses.append("title = ?")
        query_params.append(title)
    if status is not None:
        set_clauses.append("status = ?")
        query_params.append(status)
    if author is not None:
        set_clauses.append("author = ?")
        query_params.append(author)
    if not set_clauses:
        return

    query_params.append(series_id)
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE series SET {', '.join(set_clauses)} WHERE id = ?",
        query_params,
    )


def add_tag_to_series(
    conn: sqlite3.Connection, series_id: int, tag: str
) -> bool:
    tag_id: int = _ensure_tag(conn, tag)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO series_tags (series_id, tag_id) VALUES (?, ?)",
        (series_id, tag_id),
    )

    return cursor.rowcount > 0


def remove_tag_from_series(
    conn: sqlite3.Connection, series_id: int, tag: str
) -> bool:
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM series_tags "
        "WHERE series_id = ? AND tag_id = "
        "(SELECT id FROM tags WHERE name = ? COLLATE NOCASE)",
        (series_id, tag),
    )

    return cursor.rowcount > 0


def remove_series(conn: sqlite3.Connection, series_id: int) -> None:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM series WHERE id = ?", (series_id,))


def log_chapters(
    conn: sqlite3.Connection,
    series_id: int,
    chapters: list[str],
    read_date: str | None,
) -> int:
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO chapters (series_id, chapter, read_date) "
        "VALUES (?, ?, ?) "
        "ON CONFLICT(series_id, chapter) "
        "DO UPDATE SET read_date = excluded.read_date",
        [(series_id, chapter, read_date) for chapter in chapters],
    )
    return len(chapters)


def unlog_chapters(
    conn: sqlite3.Connection,
    series_id: int,
    chapters: list[str],
) -> int:
    cursor = conn.cursor()

    cursor.executemany(
        "DELETE FROM chapters WHERE series_id = ? AND chapter = ?",
        [(series_id, chapter) for chapter in chapters],
    )
    return cursor.rowcount


def get_series(conn: sqlite3.Connection, series_id: int) -> Series | None:
    cursor = conn.cursor()

    series_record = cursor.execute(
        "SELECT id, title, series_type, author, status, started_at "
        "FROM series "
        "WHERE id = ?",
        (series_id,),
    ).fetchone()

    if series_record is None:
        return None

    return Series(
        id=series_record["id"],
        title=series_record["title"],
        series_type=series_record["series_type"],
        author=series_record["author"],
        status=series_record["status"],
        started_at=series_record["started_at"],
        tags=_tags_for(conn, series_id),
    )


def list_series(
    conn: sqlite3.Connection,
    *,
    status: str | None = None,
    series_type: str | None = None,
    tags: list[str] | None = None,
) -> list[SeriesSummary]:
    filters: list[str] = []
    query_params: list[object] = []

    if status is not None:
        filters.append("s.status = ?")
        query_params.append(status)
    if series_type is not None:
        filters.append("s.series_type = ?")
        query_params.append(series_type)

    if tags:
        placeholders = ",".join("?" for _ in tags)
        filters.append(
            "s.id IN ( "
            "    SELECT st.series_id FROM series_tags st "
            "    JOIN tags t ON t.id = st.tag_id "
            f"    WHERE t.name COLLATE NOCASE IN ({placeholders}) "
            "    GROUP BY st.series_id "
            "    HAVING COUNT(DISTINCT t.name COLLATE NOCASE) = ?)"
        )
        query_params.extend(tags)
        query_params.append(len(tags))

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""

    sql_query = (
        "SELECT "
        "s.id, s.title, s.series_type, s.status, s.author, "
        "(SELECT COUNT(*) FROM chapters c "
        "WHERE c.series_id = s.id) AS chapters_read, "
        "(SELECT MAX(c.read_date) FROM chapters c "
        "WHERE c.series_id = s.id) AS last_read "
        "FROM series s "
        f"{where_clause} "
        "ORDER BY s.title COLLATE NOCASE"
    )

    cursor = conn.cursor()
    series_records = cursor.execute(sql_query, query_params).fetchall()

    return [
        SeriesSummary(
            id=series_row["id"],
            title=series_row["title"],
            series_type=series_row["series_type"],
            status=series_row["status"],
            author=series_row["author"],
            tags=_tags_for(conn, series_row["id"]),
            chapters_read=series_row["chapters_read"],
            last_read=series_row["last_read"],
        )
        for series_row in series_records
    ]


def get_series_detail(
    conn: sqlite3.Connection, series_id: int
) -> SeriesDetail | None:

    series = get_series(conn, series_id)
    if series is None:
        return None

    cursor = conn.cursor()

    chapter_count_record = cursor.execute(
        "SELECT COUNT(*) AS n FROM chapters WHERE series_id = ?", (series_id,)
    ).fetchone()
    chapters_read = int(chapter_count_record["n"])

    chapter_records = cursor.execute(
        "SELECT chapter, read_date FROM chapters "
        "WHERE series_id = ? "
        "ORDER BY "
        "  CASE WHEN read_date IS NULL THEN 1 ELSE 0 END, "
        "  read_date DESC, "
        "  CASE WHEN chapter GLOB '[0-9]*' THEN 0 ELSE 1 END, "
        "  CAST(chapter AS REAL) DESC, "
        "  chapter DESC "
        "LIMIT 3",
        (series_id,),
    ).fetchall()

    last_chapters = tuple(
        Chapter(
            chapter=chapter_record["chapter"],
            read_date=chapter_record["read_date"],
        )
        for chapter_record in chapter_records
    )

    return SeriesDetail(
        series=series, chapters_read=chapters_read, last_chapters=last_chapters
    )


def chapter_exists(
    conn: sqlite3.Connection, series_id: int, chapter: str
) -> tuple[bool, str | None]:
    cursor = conn.cursor()

    chapter_record = cursor.execute(
        "SELECT read_date FROM chapters WHERE series_id = ? AND chapter = ?",
        (
            series_id,
            chapter,
        ),
    ).fetchone()
    if chapter_record is None:
        return (False, None)
    return (True, chapter_record["read_date"])
