from server import app
from fastapi import status, Request
from fastapi.responses import JSONResponse
from server.core.functions.log_functions import write_log
from server.events.viewing_event import viewing_event
from time import perf_counter
import psutil

@app.get(path="/tools/ping/v1", status_code=status.HTTP_200_OK, tags=["tools"])
async def pingv1(request: Request) -> JSONResponse:
    await viewing_event(request)
    statuswrite = await write_log(endpoint="Ping_V1", request=request)
    if statuswrite == False:
        try:
            await write_log(endpoint="Ping_V2", request=request, status="Internal Server Error")
        except Exception:
            pass
        return JSONResponse(
            content={"status": False, "detail": "Log write error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    return JSONResponse(content={"status": True}, status_code=status.HTTP_200_OK)

@app.get(path="/tools/ping/v2", status_code=status.HTTP_200_OK, tags=["tools"])
async def pingv2(request: Request) -> JSONResponse:
    await viewing_event(request)
    start = perf_counter()
    statuswrite = await write_log(endpoint="Ping_V2", request=request)
    if statuswrite == False:
        try:
            await write_log(endpoint="Ping_V2", request=request, status="Internal Server Error")
        except Exception:
            pass
        return JSONResponse(
            content={"status": False, "detail": "Log write error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    vm = psutil.virtual_memory()
    du = psutil.disk_usage("/")
    elapsed_ms = (perf_counter() - start) * 1000
    return JSONResponse(content={
                        "status": True,
                        "ram": {
                            "total": vm.total,
                            "used": vm.used,
                            "free": vm.available,
                            "percent": vm.percent,
                        },
                        "disk": {
                            "total": du.total,
                            "used": du.used,
                            "free": du.free,
                            "percent": du.percent,
                        },
                        "processing_ms": round(elapsed_ms, 2)
                        },
                        status_code=status.HTTP_200_OK)
