"""
Cache para dados de referência (estados, cidades, categorias, etc.)

Dados de referência são aqueles que mudam muito raramente
(ex: lista de estados brasileiros, tipos de contrato, cargos).

Estes dados são ideais para cache com TTL longo (24h ou mais).
"""

from core.cache.redis import cache_delete, cache_get, cache_set
from core.logging import logger


class ReferenceDataCache:
    """
    Cache especializado para dados de referência.

    Estes dados mudam muito raramente e podem ser cacheados
    por longos períodos (24h ou mais).
    """

    # TTLs recomendados por tipo de dado
    TTL_ESTADOS = 86400 * 7  # 7 dias - estados quase nunca mudam
    TTL_MUNICIPIOS = 86400 * 7  # 7 dias
    TTL_CARGOS = 86400  # 1 dia
    TTL_TIPOS_CONTRATO = 86400  # 1 dia
    TTL_TIPOS_DOCUMENTO = 86400  # 1 dia
    TTL_CATEGORIAS = 3600  # 1 hora
    TTL_UNIDADES_MEDIDA = 86400 * 30  # 30 dias
    TTL_BANCOS = 86400 * 30  # 30 dias

    @staticmethod
    async def get_estados(repository) -> list[dict]:
        """
        Retorna lista de estados brasileiros.
        Cache: 7 dias

        Args:
            repository: Repositório para buscar dados se não estiverem em cache

        Returns:
            Lista de estados
        """
        cache_key = "ref:estados"

        # Tentar cache
        cached = await cache_get(cache_key)
        if cached is not None:
            logger.debug("Cache HIT: estados")
            return cached

        # Buscar do banco
        estados = await repository.get_all_estados()
        estados_list = [e.to_dict() if hasattr(e, "to_dict") else e for e in estados]

        # Salvar no cache
        await cache_set(cache_key, estados_list, ttl=ReferenceDataCache.TTL_ESTADOS)
        logger.debug("Cache MISS: estados - carregado do banco")

        return estados_list

    @staticmethod
    async def get_municipios_por_uf(uf: str, repository) -> list[dict]:
        """
        Retorna municípios de uma UF.
        Cache: 7 dias

        Args:
            uf: Sigla da UF (ex: 'SP', 'RJ')
            repository: Repositório para buscar dados

        Returns:
            Lista de municípios
        """
        cache_key = f"ref:municipios:{uf.upper()}"

        cached = await cache_get(cache_key)
        if cached is not None:
            logger.debug(f"Cache HIT: municipios/{uf}")
            return cached

        municipios = await repository.get_municipios_by_uf(uf)
        municipios_list = [m.to_dict() if hasattr(m, "to_dict") else m for m in municipios]

        await cache_set(cache_key, municipios_list, ttl=ReferenceDataCache.TTL_MUNICIPIOS)
        logger.debug(f"Cache MISS: municipios/{uf} - carregado do banco")

        return municipios_list

    @staticmethod
    async def get_cargos(repository) -> list[dict]:
        """
        Retorna lista de cargos.
        Cache: 1 dia

        Args:
            repository: Repositório de cargos

        Returns:
            Lista de cargos
        """
        cache_key = "ref:cargos"

        cached = await cache_get(cache_key)
        if cached is not None:
            return cached

        cargos = await repository.get_all_cargos()
        cargos_list = [c.to_dict() if hasattr(c, "to_dict") else c for c in cargos]

        await cache_set(cache_key, cargos_list, ttl=ReferenceDataCache.TTL_CARGOS)

        return cargos_list

    @staticmethod
    async def get_tipos_contrato(repository) -> list[dict]:
        """
        Retorna tipos de contrato.
        Cache: 1 dia
        """
        cache_key = "ref:tipos_contrato"

        cached = await cache_get(cache_key)
        if cached is not None:
            return cached

        tipos = await repository.get_all_tipos_contrato()
        tipos_list = [t.to_dict() if hasattr(t, "to_dict") else t for t in tipos]

        await cache_set(cache_key, tipos_list, ttl=ReferenceDataCache.TTL_TIPOS_CONTRATO)

        return tipos_list

    @staticmethod
    async def get_bancos(repository) -> list[dict]:
        """
        Retorna lista de bancos (código, nome).
        Cache: 30 dias
        """
        cache_key = "ref:bancos"

        cached = await cache_get(cache_key)
        if cached is not None:
            return cached

        bancos = await repository.get_all_bancos()
        bancos_list = [b.to_dict() if hasattr(b, "to_dict") else b for b in bancos]

        await cache_set(cache_key, bancos_list, ttl=ReferenceDataCache.TTL_BANCOS)

        return bancos_list

    @staticmethod
    async def invalidate_estados():
        """Invalida cache de estados (raramente necessário)."""
        await cache_delete("ref:estados")
        logger.info("Cache invalidado: estados")

    @staticmethod
    async def invalidate_municipios(uf: str | None = None):
        """
        Invalida cache de municípios.

        Args:
            uf: Se especificado, invalida apenas essa UF
        """
        if uf:
            await cache_delete(f"ref:municipios:{uf.upper()}")
            logger.info(f"Cache invalidado: municipios/{uf}")
        else:
            # Invalida todos (usar com cuidado)
            from core.cache.redis import cache_clear_pattern

            await cache_clear_pattern("ref:municipios:*")
            logger.info("Cache invalidado: todos os municipios")

    @staticmethod
    async def invalidate_all():
        """Invalida todo o cache de dados de referência."""
        from core.cache.redis import cache_clear_pattern

        await cache_clear_pattern("ref:*")
        logger.info("Cache invalidado: todos os dados de referencia")


# Instância global para uso conveniente
reference_cache = ReferenceDataCache()
