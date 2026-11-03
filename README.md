# kami

A minimal reading ledger for manga, manhwa, manhua, web novels, comics, and more — a small, fast CLI backed by SQLite.

`kami` tracks what you're reading, what you've read, and when. It's designed to stay out of your way: one database file, a handful of commands, and `--json` output for scripting.

---

## Features

- **Series tracking** — title, medium, author, status, start date, and tags
- **Chapter logging** — log single chapters, ranges, and decimal chapters (`12.1,12.2,13`)
- **Read dates** — record when you read, or backfill with `--date`
- **Fuzzy resolution** — refer to a series by any unique prefix; ambiguity is reported clearly
- **Tag filtering** — repeatable `--tag` with AND semantics
- **Machine-readable** — every command supports `--json`
- **Dry runs** — see what would change before committing
- **Inspectable** — open the DB in a preconfigured `sqlite3` shell

---

## Installation

Requires **Python ≥ 3.10**.

With [`uv`](https://github.com/astral-sh/uv):

```bash
uv sync
uv run kami --help
```

Or install the package directly:

```bash
pip install .
kami --help
```

---

## Quick start

```bash
# Create the database and schema
kami init

# Add a series
kami add "Frieren" --type Manga --author "Kanehito Yamada" --tag fantasy --tag adventure

# Log chapters 1 through 10
kami log Frieren 1-10

# Log a specific date
kami log Frieren 11 --date 2026-11-02

# See everything
kami list

# Show details for one series
kami show Frieren
```

---

## Global options

These apply to every command:

| Option            | Description                                        |
| ----------------- | -------------------------------------------------- |
| `--db PATH`       | Path to the SQLite database (overrides `$KAMI_DB`) |
| `--json`          | Output machine-readable JSON                       |
| `--verbose`, `-v` | Print debug info (SQL, exec commands)              |

---

## Commands

### `kami init`

Create the database and schema (creates parent directories as needed).

```bash
kami init
kami init --json
```

---

### `kami add`

Add a series to the ledger.

```bash
kami add TITLE --type TYPE [--author AUTHOR] [--status STATUS] [--tag TAG]... [--started DATE]
```

- `--type`, `-t` — one of `Manga`, `Manhwa`, `Manhua`, `Novel`, `Webtoon`, `Comic`
- `--status`, `-s` — one of `Reading`, `Completed`, `On Hold`, `Dropped` (default: `Reading`)
- `--author`, `-a` — optional author
- `--tag` — repeatable
- `--started` — `YYYY-MM-DD` or `pre-catalog`

```bash
kami add "Vinland Saga" -t Manga -a "Makoto Yukimura" --tag historical --started 2005-04-01
```

---

### `kami list`

List series, optionally filtered.

```bash
kami list [--status STATUS] [--type TYPE] [--tag TAG]...
```

Filters are combined with AND. Repeating `--tag` requires *all* listed tags.

```bash
kami list --status Reading
kami list --type Manhwa --tag romance --tag drama
kami list --json
```

---

### `kami show`

Print a series' metadata and its 3 most recent chapters.

```bash
kami show QUERY
```

`QUERY` may be the full title or any unique prefix.

---

### `kami edit`

Rename, change status/author, or add/remove tags.

```bash
kami edit QUERY [--title NEW_TITLE] [--status STATUS] [--author AUTHOR] \
                [--add-tags TAG]... [--remove-tags TAG]...
```

```bash
kami edit Frieren --status Completed
kami edit Frieren --add-tags magic --remove-tags adventure
```

---

### `kami rm`

Remove a series and cascade its chapters/tag links. Prompts unless `--yes`.

```bash
kami rm QUERY [--yes]
```

In non-interactive contexts (e.g. scripts, pipes), `--yes` is required.

---

### `kami log`

Record chapters as read.

```bash
kami log QUERY SPEC [--date YYYY-MM-DD] [--dry-run]
```

`SPEC` supports comma-separated items, ranges, and decimals:

```bash
kami log Frieren 12
kami log Frieren 13-20
kami log Frieren 21.1,21.2,22
kami log Frieren 1-5 --date 2026-10-01
kami log Frieren 1-5 --dry-run
```

A `--dry-run` reports which chapters would be newly added versus updated, without writing.

---

### `kami unlog`

The inverse of `log`. By default, clears the read date (`read_date = NULL`); with `--delete`, removes chapter rows entirely.

```bash
kami unlog QUERY SPEC [--delete] [--yes] [--dry-run]
```

- `--delete` — delete rows entirely
- `--yes`, `-y` — skip confirmation
- `--dry-run` — show what would happen

Deleting 10 or more chapters requires confirmation, and in non-interactive contexts requires `--yes`.

---

### `kami db`

Database maintenance and introspection.

#### `kami db path`

Print the resolved database path. With `--json`, also reports `exists` and `size`.

```bash
kami db path
kami db path --json
```

#### `kami db shell`

Open an interactive `sqlite3` shell on the database, preconfigured with `.headers on` and `.mode box`. Extra arguments are passed before the DB path.

```bash
kami db shell
```

---

## Chapter specs

The `SPEC` argument accepted by `log` and `unlog` supports:

| Syntax          | Meaning                            |
| --------------- | ---------------------------------- |
| `12`            | Chapter 12                         |
| `12.1`          | Chapter 12.1 (decimals)            |
| `12-20`         | Chapters 12 through 20 (inclusive) |
| `12.1-12.5`     | Decimal range, step `0.1`          |
| `1-3,5,7.1,7.2` | Comma-separated combination        |

Duplicates are removed. Ranges must be ascending and numeric.

---

## Statuses and types

**Types:** `Manga`, `Manhwa`, `Manhua`, `Novel`, `Webtoon`, `Comic`

**Statuses:** `Reading`, `Completed`, `On Hold`, `Dropped`

---

## JSON output

Pass `--json` to any command to get structured output instead of human-readable text.

```bash
kami list --json
```

```json
[
  {
    "id": 1,
    "title": "Frieren",
    "type": "Manga",
    "status": "Reading",
    "author": "Kanehito Yamada",
    "tags": ["adventure", "fantasy"],
    "chapters_read": 10,
    "last_read": "2026-11-02"
  }
]
```

Errors are also structured in JSON mode:

```json
{ "error": "not_found", "query": "Frieren" }
```

```json
{
  "error": "ambiguous",
  "query": "F",
  "candidates": [
    { "id": 1, "title": "Frieren", "series_type": "Manga" },
    { "id": 2, "title": "Fullmetal Alchemist", "series_type": "Manga" }
  ]
}
```

---

## Exit codes

| Code | Meaning                                                       |
| ---- | ------------------------------------------------------------- |
| `0`  | Success                                                       |
| `1`  | General error (e.g. duplicate series, invalid rename)         |
| `2`  | Ambiguous query — multiple series matched                     |
| `3`  | Series not found                                              |
| `5`  | Database error (missing DB, `sqlite3` binary not found, etc.) |
| `10` | User declined a destructive confirmation                      |

---

## Database schema

`kami` stores everything in a single SQLite file with four tables:

- **`series`** — id, title, type, author, status, started_at, `UNIQUE(title, series_type)`
- **`tags`** — id, name (`COLLATE NOCASE`)
- **`series_tags`** — many-to-many join, cascading deletes
- **`chapters`** — id, series_id, chapter, read_date, `UNIQUE(series_id, chapter)`

Inspect it directly with:

```bash
kami db shell
```
