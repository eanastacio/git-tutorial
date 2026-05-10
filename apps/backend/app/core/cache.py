from __future__ import annotations

import json
import logging
from typing import Any

from redis.asyncio import Redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class CacheClient:
    def __init__(self) -> None:
        self._client: Redis | None = None
        self._settings = get_settings()

    async def connect(self) -> None:
        if not self._settings.enable_cache or not self._settings.redis_url:
            return
        try:
            self._client = Redis.from_url(self._settings.redis_url, decode_responses=True)
            await self._client.ping()
            logger.info("Connected to Redis cache")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Cache disabled: %s", exc)
            self._client = None

    async def disconnect(self) -> None:
        if self._client:
            await self._client.close()

    async def get_json(self, key: str) -> Any | None:
        if not self._client:
            return None
        raw = await self._client.get(key)
        if not raw:
            return None
        return json.loads(raw)

    async def set_json(self, key: str, value: Any, ttl: int | None = None) -> None:
        if not self._client:
            return
        ttl = ttl or self._settings.cache_ttl_seconds
        await self._client.set(key, json.dumps(value), ex=ttl)


cache_client = CacheClient()
