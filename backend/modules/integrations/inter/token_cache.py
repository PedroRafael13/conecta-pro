"""D6 — Cache Redis para token OAuth2 Inter (TTL 50min)."""

import logging

logger = logging.getLogger(__name__)

REDIS_TOKEN_KEY = "inter:token"
REDIS_TOKEN_TTL = 50 * 60  # 50 min (token valid 1h, refresh before expiry)


async def get_cached_token() -> str | None:
    """Retorna token cacheado do Redis, ou None se ausente/expirado."""
    try:
        from core.cache.redis import get_redis

        redis = await get_redis()
        cached = await redis.get(REDIS_TOKEN_KEY)
        if cached:
            return cached.decode() if isinstance(cached, bytes) else cached
    except Exception as exc:
        logger.debug("Inter token_cache: Redis indisponível (%s)", exc)
    return None


async def set_cached_token(token: str) -> None:
    """Salva token no Redis com TTL de 50min."""
    try:
        from core.cache.redis import get_redis

        redis = await get_redis()
        await redis.set(REDIS_TOKEN_KEY, token, ex=REDIS_TOKEN_TTL)
        logger.debug("Inter token_cache: token gravado (TTL=%ds)", REDIS_TOKEN_TTL)
    except Exception as exc:
        logger.debug("Inter token_cache: falha ao gravar Redis (%s)", exc)


async def invalidate_token() -> None:
    """Remove token do cache (força reautenticação)."""
    try:
        from core.cache.redis import get_redis

        redis = await get_redis()
        await redis.delete(REDIS_TOKEN_KEY)
    except Exception as exc:
        logger.debug("Inter token_cache: falha ao invalidar (%s)", exc)
