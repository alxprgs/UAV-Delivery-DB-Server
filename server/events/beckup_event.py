import os, shutil, tempfile
from typing import Optional, TYPE_CHECKING
from datetime import date, datetime
from pathlib import Path
from b2sdk.v1 import B2Api, InMemoryAccountInfo
import asyncio
import logging

if TYPE_CHECKING: 
    from server.core.config import Settings

async def backup_event(
    settings: Optional["Settings"] = None,
    logger: logging.Logger | None = None,
    db_dir: Path | None = None,
) -> bool:
    if settings is None:
        try:
            from server import settings as srv_settings
            settings = srv_settings
        except ImportError:
            return False

    if logger is None:
        try:
            from server.core.logger_module import logger as srv_logger
            logger = srv_logger
        except ImportError:
            logger = None

    if db_dir is None:
        try:
            from server.core.paths import DB_DIR as default_db_dir
            db_dir = default_db_dir
        except ImportError:
            return False
        
    bucket = None
    info = InMemoryAccountInfo()
    b2 = B2Api(info)

    if not (bucket and settings.BACKBLAZE_APPLICATION_KEY_ID and settings.BACKBLAZE_APPLICATION_KEY):
        if logger:
            logger.warning("Backup skipped: bucket or Backblaze credentials missing")
        return False

    try:
        b2.authorize_account("production", settings.BACKBLAZE_APPLICATION_KEY_ID, settings.BACKBLAZE_APPLICATION_KEY)
        try:
            bucket = b2.get_bucket_by_name("UAV-DB-backups")
        except Exception:
            from b2sdk.v1 import BucketType
            bucket = b2.create_bucket("UAV-DB-backups", BucketType.ALL_PRIVATE)
    except Exception:
        pass

    try:
        today = date.today().isoformat()
        archive_name = f"{today}_DB_backup"

        def _create_zip(tmpdir: str) -> Path:
            base_name = os.path.join(tmpdir, archive_name)
            shutil.make_archive(base_name=base_name, format="zip", root_dir=str(db_dir))
            return Path(f"{base_name}.zip")

        with tempfile.TemporaryDirectory(prefix="backup_zip_tmp_") as tmpdir:
            loop = asyncio.get_running_loop()
            zip_path = await loop.run_in_executor(None, _create_zip, tmpdir)
            await loop.run_in_executor(
                None,
                bucket.upload_local_file,
                str(zip_path),
                f"backups/{today}/{archive_name}.zip",
            )

        if logger:
            logger.info("Успешный бэкап баз данных")
        return True

    except Exception as e:
        msg = f"Ошибка бэкапа: {e} ({datetime.now().isoformat()})"
        if logger:
            logger.error(msg, exc_info=True)
        else:
            print(msg)
        return False
