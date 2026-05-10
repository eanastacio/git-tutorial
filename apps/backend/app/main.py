from __future__ import annotations

from contextlib import asynccontextmanager
from collections import defaultdict
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.router import api_router
from app.core.cache import cache_client
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
limiter = Limiter(key_func=get_remote_address)
request_windows: dict[str, tuple[int, int]] = defaultdict(lambda: (0, int(time.time() // 60)))


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    await cache_client.connect()
    yield
    await cache_client.disconnect()


app = FastAPI(
    title=settings.app_name,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def enforce_basic_rate_limit(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    current_minute = int(time.time() // 60)
    count, minute_bucket = request_windows[client_ip]
    if minute_bucket != current_minute:
        count = 0
        minute_bucket = current_minute
    count += 1
    request_windows[client_ip] = (count, minute_bucket)
    if count > settings.requests_per_minute:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
    return await call_next(request)


@app.get("/health")
@limiter.limit(f"{settings.requests_per_minute}/minute")
async def health(_: Request) -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router, prefix=settings.api_prefix)
