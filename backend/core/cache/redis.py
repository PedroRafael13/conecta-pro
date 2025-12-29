"""
Cliente Redis para cache.
"""

import json
from typing import Any, Optional

import redis.asyncio as redis

from core.config import settings

# Cliente Redis
redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """
    Retorna cliente Redis.

    Returns:
        Cliente Redis conectado
    """
    global redis_client

    if redis_client is None:
        redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    return redis_client


async def close_redis() -> None:
    """Fecha conexão Redis."""
    global redis_client

    if redis_client:
        await redis_client.close()
        redis_client = None


async def cache_get(key: str) -> Optional[Any]:
    """
    Obtém valor do cache.

    Args:
        key: Chave do cache

    Returns:
        Valor ou None se não existir
    """
    client = await get_redis()
    value = await client.get(key)

    if value:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    return None


async def cache_set(
    key: str,
    value: Any,
    ttl: Optional[int] = None,
) -> bool:
    """
    Define valor no cache.

    Args:
        key: Chave do cache
        value: Valor a armazenar
        ttl: Tempo de expiração em segundos (default: settings.redis_ttl)

    Returns:
        True se sucesso
    """
    client = await get_redis()
    ttl = ttl or settings.redis_ttl

    if isinstance(value, (dict, list)):
        value = json.dumps(value)

    await client.setex(key, ttl, value)
    return True


async def cache_delete(key: str) -> bool:
    """
    Remove valor do cache.

    Args:
        key: Chave do cache

    Returns:
        True se removido
    """
    client = await get_redis()
    result = await client.delete(key)
    return result > 0


async def cache_clear_pattern(pattern: str) -> int:
    """
    Remove todas as chaves que correspondem ao padrão.

    Args:
        pattern: Padrão de chave (ex: "user:*")

    Returns:
        Número de chaves removidas
    """
    client = await get_redis()
    keys = []

    async for key in client.scan_iter(match=pattern):
        keys.append(key)

    if keys:
        return await client.delete(*keys)

    return 0
