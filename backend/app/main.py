import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import Gauge
from prometheus_fastapi_instrumentator import Instrumentator

from app.middleware.cors import add_cors
from app.middleware.logging import StructuredLoggingMiddleware, configure_logging
from app.middleware.timing import TimingMiddleware
from app.routes import health, metrics, projects

app_uptime_seconds = Gauge(
    "app_uptime_seconds",
    "Seconds since the application started.",
)


async def _uptime_updater(start_time: float) -> None:
    while True:
        app_uptime_seconds.set(time.time() - start_time)
        await asyncio.sleep(15)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    start_time = time.time()
    app.state.start_time = start_time
    app_uptime_seconds.set(0)
    task = asyncio.create_task(_uptime_updater(start_time))
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


def create_app() -> FastAPI:
    app = FastAPI(
        title="Portfolio API",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Middleware: register in reverse execution order (last added runs first).
    # Desired order on the request path: CORS -> Timing -> Logging -> handler.
    app.add_middleware(StructuredLoggingMiddleware)
    app.add_middleware(TimingMiddleware)
    add_cors(app)

    app.include_router(health.router)
    app.include_router(projects.router)
    app.include_router(metrics.router)

    Instrumentator(
        should_group_status_codes=False,
        excluded_handlers=["/metrics"],
    ).instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)

    return app


app = create_app()
