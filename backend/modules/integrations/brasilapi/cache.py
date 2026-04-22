"""Redis cache layer for BrasilAPI responses."""

import json
import os
from typing import Any

import redis.asyncio as aioredis


class RedisCache:
    """Simple async Redis cache with JSON serialization."""

    def __init__(self, redis_url: str | None = None, prefix: str = "brasilapi"):
        self._url = redis_url or os.environ.get("REDIS_URL", "redis://redis:6379/1")
        self._prefix = prefix
        self._client: aioredis.Redis | None = None

    async def _get_client(self) -> aioredis.Redis:
        if self._client is None:
            self._client = aioredis.from_url(self._url, decode_responses=True)
        return self._client

    def _key(self, name: str) -> str:
        return f"{self._prefix}:{name}"

    async def get(self, name: str) -> Any | None:
        try:
            client = await self._get_client()
            raw = await client.get(self._key(name))
            return json.loads(raw) if raw else None
        except Exception:
            return None

    async def set(self, name: str, value: Any, ttl_seconds: int) -> None:
        try:
            client = await self._get_client()
            await client.set(self._key(name), json.dumps(value), ex=ttl_seconds)
        except Exception:
            pass

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()
            self._client = None
