import time

from fastapi import APIRouter, Request

from app.config import APP_VERSION

router = APIRouter()


@router.get("/health")
async def health(request: Request) -> dict:
    start_time = getattr(request.app.state, "start_time", time.time())
    uptime_seconds = round(time.time() - start_time, 3)
    return {
        "status": "ok",
        "uptime": uptime_seconds,
        "version": APP_VERSION,
    }
