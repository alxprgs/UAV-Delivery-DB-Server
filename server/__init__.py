import os
import shutil
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from b2sdk.v1 import B2Api, InMemoryAccountInfo

from server.core.config import settings
from server.core.init.init_ceo_worker import init_ceo_worker
from server.core.init.init_root_user import init_root_user
from server.core.logger_module import logger
from server.core.paths import USERS_DIR, WORKERS_DIR

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

async def beckup_event(bucket):
    if settings.BACKBLAZE_APPLICATION_KEY_ID and settings.BACKBLAZE_APPLICATION_KEY: 
        try:
            with tempfile.TemporaryDirectory(prefix="backup_zip_tmp_") as tmpdir:
                today = date.today().isoformat()
                archive_name = f"{today}_DB_backup"
                base_name = os.path.join(tmpdir, archive_name)
                shutil.make_archive(
                    base_name=base_name,
                    format="zip",
                    root_dir = str(Path("server") / "core" / "db_files")
                )
                zip_path = f"{base_name}.zip"
                try:
                    bucket.upload_local_file(
                        local_file=zip_path,
                        file_name=f"backups/{today}/{archive_name}.zip"
                    )
                except Exception as e:
                    logger.error("Ошибка закгрузки бекапа: %s "+ f"({datetime.now().isoformat()})", e, exc_info=True)
                    return False
            logger.info("Успешный бекап баз данных")
            return True
        except Exception as e:
            logger.error("Ошибка бекапа: %s "+ f"({datetime.now().isoformat()})", e, exc_info=True)
            return False
    else:
        return False
    
async def check_file(file_path: Path):
    file_path.parent.mkdir(parents=True, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    info = InMemoryAccountInfo()
    b2 = B2Api(info)
    (Path("server") / "logs").mkdir(parents=True, exist_ok=True)
    (Path("server") / "core" / "db_files").mkdir(parents=True, exist_ok=True)
    paths = [
        USERS_DIR,
        WORKERS_DIR,
    ]
    for path in paths:
        await check_file(file_path=path)
    b2.authorize_account("production", settings.BACKBLAZE_APPLICATION_KEY_ID, settings.BACKBLAZE_APPLICATION_KEY)
    if settings.BACKBLAZE_APPLICATION_KEY_ID and settings.BACKBLAZE_APPLICATION_KEY: 
        try:
            bucket = b2.get_bucket_by_name("UAV-DB-backups")
        except Exception:
            from b2sdk.v1 import BucketType
            bucket = b2.create_bucket("UAV-DB-backups", BucketType.ALL_PRIVATE)
        app.state.bucket = bucket
    await init_root_user()
    await init_ceo_worker()

    from server.routes.tools import ping
    from server.routes.db import auth, delete, find, insert, update
    from server.routes.specialized_db.rfid import auth_card

    if settings.BACKBLAZE_APPLICATION_KEY_ID and settings.BACKBLAZE_APPLICATION_KEY: 
        scheduler.add_job(beckup_event, trigger="interval", hours=1, minutes=0, args=[bucket], id="daily_backup", replace_existing=True)
        scheduler.start()

    blocked: dict[str, datetime] = {}
    app.state.blocked = blocked

    yield
    if settings.BACKBLAZE_APPLICATION_KEY_ID and settings.BACKBLAZE_APPLICATION_KEY: 
        scheduler.shutdown()

docs_config = {
    "openapi_url": "/openapi.json",
    "redoc_url": "/redoc",
    "docs_url": "/",
} if settings.DEV else {}

app = FastAPI(
    debug=settings.DEV,
    title="База данных специально для UAV-Delivery",
    version=f"{'dev' if settings.DEV else 'stable'} 0.0.4 {date.today().isoformat()}",
    lifespan=lifespan,
    **docs_config,
)
