from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from server.core.config import settings
from pathlib import Path
from server.core.init_root_user import init_root_user
from b2sdk.v1 import InMemoryAccountInfo, B2Api
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, date
import shutil
import tempfile
import os

scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

async def beckup_event(bucket):
    try:
        with tempfile.TemporaryDirectory(prefix="backup_zip_tmp_") as tmpdir:
            today = date.today().isoformat()
            archive_name = f"{today}_DB_backup"
            base_name = os.path.join(tmpdir, archive_name)
            shutil.make_archive(
                base_name=base_name,
                format="zip",
                root_dir = str(Path("server") / "core" / "db")
            )
            zip_path = f"{base_name}.zip"
            try:
                bucket.upload_local_file(
                    local_file=zip_path,
                    file_name=f"backups/{today}/{archive_name}.zip"
                )
            except Exception as e:
                print(f"Ошибка загрузки бекапа: {e} ({datetime.now().isoformat()})")
                return False
        return True
    except Exception as e:
        print(f"Ошибка бекапа: {e} ({datetime.now().isoformat()})")
        return False


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    info = InMemoryAccountInfo()
    b2 = B2Api(info)
    (Path("server") / "logs").mkdir(parents=True, exist_ok=True)
    (Path("server") / "core" / "db").mkdir(parents=True, exist_ok=True)
    b2.authorize_account("production", settings.BACKBLAZE_APPLICATION_KEY_ID, settings.BACKBLAZE_APPLICATION_KEY)
    try:
        bucket = b2.get_bucket_by_name("UAV-DB-backups")
    except Exception:
        from b2sdk.v1 import BucketType
        bucket = b2.create_bucket("UAV-DB-backups", BucketType.ALL_PRIVATE)
    app.state.bucket = bucket
    await init_root_user()
    from server.routes.tools import ping
    scheduler.add_job(beckup_event, trigger="interval", hour=1, minute=0, args=[bucket], id="daily_backup", replace_existing=True)
    scheduler.start()

    yield

    scheduler.shutdown()

docs_config = {
    "openapi_url": "/openapi.json",
    "redoc_url": "/redoc",
    "docs_url": "/",
} if settings.DEV else {}

app = FastAPI(
    debug=settings.DEV,
    title="База данных специально для UAV-Delivery",
    version=f"{'dev' if settings.DEV else 'stable'} 0.0.1 {date.today().isoformat()}",
    lifespan=lifespan,
    **docs_config,
)