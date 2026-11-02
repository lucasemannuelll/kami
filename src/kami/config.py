from __future__ import annotations

import os
from pathlib import Path
from typing import Final

from platformdirs import user_data_dir

APP_NAME: Final[str] = "kami"
DB_FILENAME: Final[str] = "kami.db"
ENV_VAR: Final[str] = "KAMI_DB"


def default_db_path() -> Path:
    return Path(user_data_dir(APP_NAME, appauthor=False)) / DB_FILENAME


def resolve_db_path(cli_override: str | None) -> Path:
    if cli_override:
        return Path(cli_override).expanduser().resolve()

    env_value: str | None = os.environ.get(ENV_VAR)
    if env_value:
        return Path(env_value).expanduser().resolve()

    return default_db_path().expanduser().resolve()


def ensure_parent_dir(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
