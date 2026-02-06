"""
Token blacklist via Redis para revogação de JWT.

Armazena JTIs (JWT IDs) de tokens revogados no Redis com TTL
automático baseado no tempo de expiração do token.
"""

from datetime import UTC, datetime

from core.logging import logger


async def add_to_blacklist(jti: str, expires_at: datetime) -> bool:
    """
    Adiciona um token à blacklist.

    Args:
        jti: JWT ID do token a revogar
        expires_at: Datetime de expiração do token (para calcular TTL)

    Returns:
        True se adicionado com sucesso
    """
    from core.cache.redis import get_redis

    try:
        client = await get_redis()
        now = datetime.now(UTC)

        # TTL = tempo restante até expiração do token
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        ttl_seconds = int((expires_at - now).total_seconds())

        if ttl_seconds <= 0:
            return True  # Token já expirado, não precisa blacklist

        key = f"token:blacklist:{jti}"
        await client.setex(key, ttl_seconds, "1")
        logger.info("Token revogado: jti=%s, ttl=%ds", jti, ttl_seconds)
        return True

    except Exception as e:
        logger.error("Falha ao revogar token: %s", e)
        return False


async def is_blacklisted(jti: str) -> bool:
    """
    Verifica se um token foi revogado.

    Args:
        jti: JWT ID do token

    Returns:
        True se o token está na blacklist
    """
    from core.cache.redis import get_redis

    try:
        client = await get_redis()
        result = await client.get(f"token:blacklist:{jti}")
        return result is not None
    except Exception as e:
        logger.error("Falha ao verificar blacklist: %s", e)
        # Em caso de falha do Redis, negar acesso por segurança
        return True
