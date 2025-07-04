from pathlib import Path
from typing import AsyncGenerator
from datetime import date, datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from server.core.paths import mkdir_all
from server.core.config import settings
from server.core.logger_module import logger
from server.events.beckup_event import backup_event
from server.core.inits.init_ceo_worker import init_ceo_worker
from server.core.inits.init_root_user import init_root_user
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    mkdir_all(verbose=True)

    await init_root_user()
    await init_ceo_worker()

    from server.routes.tools import ping
    from server.routes.db import auth, delete, find, insert, update
    from server.routes.specialized_db.rfid import auth_card

    if settings.BACKBLAZE_APPLICATION_KEY_ID and settings.BACKBLAZE_APPLICATION_KEY:
        scheduler.add_job(backup_event, trigger="interval", hours=1, minutes=0, id="daily_backup", replace_existing=True)
    scheduler.start()

    blocked: dict[str, datetime] = {}
    app.state.blocked = blocked

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
    version=f"{'dev' if settings.DEV else 'stable'} 0.1.0 {date.today().isoformat()}",
    lifespan=lifespan,
    **docs_config,
)
