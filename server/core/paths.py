from pathlib import Path
import logging
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve()
for _ in range(2):
    PROJECT_ROOT = PROJECT_ROOT.parent

DB_DIR   = PROJECT_ROOT / "core" / "db_files"
LOG_DIR  = PROJECT_ROOT / "logs"
USERS_DIR   = DB_DIR / "users"
WORKERS_DIR = DB_DIR / "workers"

def mkdir_all(
    logger: logging.Logger | None = None,
    verbose: bool = False
) -> bool:
    paths: Iterable[Path] = (DB_DIR, LOG_DIR, USERS_DIR, WORKERS_DIR)
    ok = True

    for path in paths:
        try:
            path.mkdir(parents=True, exist_ok=True)
            if verbose:
                msg = f"Создан (или уже есть) каталог: {path}"
                (logger or print)(msg) if not logger else logger.info(msg)
        except Exception as e:
            ok = False
            if verbose:
                msg = f"Ошибка создания каталога {path}: {e}"
                (logger or print)(msg) if not logger else logger.error(msg, exc_info=True)

    return ok
