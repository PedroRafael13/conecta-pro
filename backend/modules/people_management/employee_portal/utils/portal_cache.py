"""
Cache Redis para o Portal do Funcionario.

Fornece funcoes de get/set/invalidate com chaves padronizadas
e um decorador @portal_cached para uso nos services do portal.
"""

import hashlib
import json
import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

from core.cache.redis import cache_clear_pattern, cache_get, cache_set

logger = logging.getLogger(__name__)

# TTLs padronizados por tipo de recurso (em segundos)
CACHE_TTLS: dict[str, int] = {
    "perfil": 300,  # 5 minutos
    "contrato": 300,  # 5 minutos
    "beneficios": 3600,  # 1 hora
    "banco_horas": 60,  # 1 minuto (muda frequentemente)
    "escalas": 300,  # 5 minutos
    "feriados": 86400,  # 24 horas
    "dashboard": 60,  # 1 minuto
    "ponto": 30,  # 30 segundos (dados em tempo real)
    "notificacoes": 15,  # 15 segundos (quase real-time)
}


def make_portal_key(employee_id: str, resource: str, **kwargs: Any) -> str:
    """Gera chave de cache padronizada para o portal.

    Formato: ``portal:{employee_id}:{resource}:{params_hash}``

    Args:
        employee_id: ID do funcionario.
        resource: Nome do recurso (ex: 'perfil', 'banco_horas').
        **kwargs: Parametros adicionais que diferenciam a chave
                  (ex: mes=3, ano=2026).

    Returns:
        Chave formatada para uso no Redis.

    Example::

        make_portal_key("abc-123", "banco_horas", mes=3, ano=2026)
        # => "portal:abc-123:banco_horas:a1b2c3d4"
    """
    if kwargs:
        params_str = json.dumps(kwargs, sort_keys=True, default=str)
        params_hash = hashlib.md5(params_str.encode(), usedforsecurity=False).hexdigest()[:8]
        return f"portal:{employee_id}:{resource}:{params_hash}"
    return f"portal:{employee_id}:{resource}"


async def portal_cache_get(employee_id: str, resource: str, **kwargs: Any) -> Any | None:
    """Busca no cache do portal.

    Args:
        employee_id: ID do funcionario.
        resource: Nome do recurso.
        **kwargs: Parametros adicionais da chave.

    Returns:
        Valor cacheado ou None se nao encontrado.
    """
    key = make_portal_key(employee_id, resource, **kwargs)
    try:
        value = await cache_get(key)
        if value is not None:
            logger.debug("Cache HIT: %s", key)
        else:
            logger.debug("Cache MISS: %s", key)
        return value
    except Exception as exc:
        logger.warning("Erro ao buscar cache portal (key=%s): %s", key, exc)
        return None


async def portal_cache_set(
    employee_id: str,
    resource: str,
    value: Any,
    ttl: int | None = None,
    **kwargs: Any,
) -> None:
    """Salva no cache do portal.

    Args:
        employee_id: ID do funcionario.
        resource: Nome do recurso.
        value: Valor a armazenar (dict ou list — sera serializado em JSON).
        ttl: TTL em segundos; se None usa o padrao de CACHE_TTLS para o resource.
        **kwargs: Parametros adicionais da chave.
    """
    key = make_portal_key(employee_id, resource, **kwargs)
    effective_ttl = ttl if ttl is not None else CACHE_TTLS.get(resource, 300)
    try:
        await cache_set(key, value, effective_ttl)
        logger.debug("Cache SET: %s (ttl=%ds)", key, effective_ttl)
    except Exception as exc:
        logger.warning("Erro ao salvar cache portal (key=%s): %s", key, exc)


async def portal_cache_invalidate(employee_id: str, resource: str | None = None) -> int:
    """Remove entradas do cache do portal.

    Args:
        employee_id: ID do funcionario.
        resource: Se informado, invalida apenas esse recurso;
                  caso contrario invalida todos os recursos do funcionario
                  (pattern ``portal:{employee_id}:*``).

    Returns:
        Numero de chaves removidas.
    """
    if resource:
        pattern = f"portal:{employee_id}:{resource}*"
    else:
        pattern = f"portal:{employee_id}:*"

    try:
        removed = await cache_clear_pattern(pattern)
        logger.debug("Cache INVALIDATE: pattern=%s removidas=%d", pattern, removed)
        return removed
    except Exception as exc:
        logger.warning("Erro ao invalidar cache portal (pattern=%s): %s", pattern, exc)
        return 0


def portal_cached(resource: str, ttl: int | None = None) -> Callable:
    """Decorador para cachear metodos de service do portal.

    Assume que o primeiro argumento apos ``self`` e ``db`` seja ``employee_id``
    (posicional ou keyword). Os demais kwargs sao usados na chave de cache.

    Args:
        resource: Nome do recurso (chave em CACHE_TTLS).
        ttl: TTL customizado; se None usa CACHE_TTLS[resource].

    Usage::

        class PortalService:
            @portal_cached("perfil")
            async def get_perfil(self, db, employee_id: str) -> dict:
                ...

            @portal_cached("banco_horas", ttl=60)
            async def get_banco_horas(self, db, employee_id: str, mes: int, ano: int) -> dict:
                ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self: Any, db: Any, employee_id: str, *args: Any, **kwargs: Any) -> Any:
            # Monta kwargs extras para diferenciar a chave (ex: mes, ano)
            extra: dict[str, Any] = {}
            # Pega nomes dos parametros posicionais restantes a partir da assinatura
            import inspect

            sig = inspect.signature(func)
            param_names = [
                p
                for p in list(sig.parameters.keys())[2:]  # pula self, db
                if p != "employee_id"
            ]
            for i, val in enumerate(args):
                if i < len(param_names):
                    extra[param_names[i]] = val
            extra.update(kwargs)

            eid = str(employee_id)

            # Tentar buscar do cache
            cached = await portal_cache_get(eid, resource, **extra)
            if cached is not None:
                return cached

            # Executar funcao original
            result = await func(self, db, employee_id, *args, **kwargs)

            # Salvar no cache
            if result is not None:
                await portal_cache_set(eid, resource, result, ttl=ttl, **extra)

            return result

        return wrapper

    return decorator
