from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_DIR = PROJECT_ROOT / "server" / "core" / "db_files"

USERS_DIR = DB_DIR / "users"
WORKERS_DIR = DB_DIR / "workers"