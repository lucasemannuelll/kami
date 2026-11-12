from __future__ import annotations

import os
from pathlib import Path

from platformdirs import user_data_dir

APP_NAME = "kami"
DB_FILENAME = "kami.db"
ENV_VAR = "KAMI_DB"


def default_db_path() -> Path:
    return Path(user_data_dir(APP_NAME, appauthor=False)) / DB_FILENAME


def resolve_db_path(cli_override) -> Path:
    if cli_override:
        return Path(cli_override).expanduser().resolve()

    env_value = os.environ.get(ENV_VAR)
    if env_value:
        return Path(env_value).expanduser().resolve()

    return default_db_path().expanduser().resolve()


def ensure_parent_dir(db_path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
