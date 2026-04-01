"""
Cliente Redis para cache.
"""

import hashlib
import json
from collections.abc import Callable
from functools import wraps
from typing import Any

import redis.asyncio as redis

from core.config import settings
from core.logging import logger

# Namespace para evitar global statement
_state: dict[str, Any] = {"client": None}


async def get_redis() -> redis.Redis:
    """
    Retorna cliente Redis.

    Returns:
        Cliente Redis conectado
    """
    if _state["client"] is None:
        _state["client"] = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            retry_on_timeout=True,
            max_connections=50,
        )

    return _state["client"]


async def close_redis() -> None:
    """Fecha conexão Redis."""
    if _state["client"]:
        await _state["client"].close()
        _state["client"] = None


async def cache_get(key: str) -> Any | None:
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
    ttl: int | None = None,
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


def cache_response(ttl: int = 300, prefix: str = "api"):
    """
    Decorator para cachear respostas de endpoints.

    Args:
        ttl: Tempo de vida do cache em segundos (default: 5 min)
        prefix: Prefixo da chave de cache

    Usage:
        @router.get("/leads")
        @cache_response(ttl=60)
        async def get_leads():
            return await lead_service.get_all()
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Gerar chave unica baseada em funcao + parametros
            params_str = json.dumps(kwargs, sort_keys=True, default=str)
            params_hash = hashlib.md5(params_str.encode(), usedforsecurity=False).hexdigest()
            cache_key = f"{prefix}:{func.__name__}:{params_hash}"

            try:
                # Tentar buscar do cache
                cached = await cache_get(cache_key)
                if cached is not None:
                    logger.debug(f"Cache HIT: {cache_key}")
                    return cached

                logger.debug(f"Cache MISS: {cache_key}")
            except Exception as e:
                logger.warning(f"Erro ao buscar cache: {e}")

            # Executar funcao
            result = await func(*args, **kwargs)

            # Salvar no cache
            try:
                await cache_set(cache_key, result, ttl)
            except Exception as e:
                logger.warning(f"Erro ao salvar cache: {e}")

            return result

        return wrapper

    return decorator
