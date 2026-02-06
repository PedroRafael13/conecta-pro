"""
Utilitários de cache - Invalidação e gestão avançada.
"""

from core.cache import cache_clear_pattern
from core.logging import logger


class CacheManager:
    """
    Gerenciador de cache com suporte a tags e invalidação inteligente.

    Permite organizar cache em grupos lógicos para invalidação eficiente.
    """

    @staticmethod
    async def invalidate_entity(entity_type: str, entity_id: str | None = None) -> int:
        """
        Invalida cache de uma entidade específica ou todas de um tipo.

        Args:
            entity_type: Tipo da entidade (ex: "post", "scale", "allocation")
            entity_id: ID específico (opcional - se None, invalida todas)

        Returns:
            Número de chaves removidas

        Examples:
            # Invalidar um post específico
            await CacheManager.invalidate_entity("post", "abc123")

            # Invalidar todos os posts
            await CacheManager.invalidate_entity("post")
        """
        if entity_id:
            pattern = f"*:{entity_type}:{entity_id}:*"
        else:
            pattern = f"*:{entity_type}:*"

        count = await cache_clear_pattern(pattern)

        logger.info(
            "Cache invalidado",
            action="invalidate_cache",
            entity_type=entity_type,
            entity_id=entity_id,
            keys_removed=count,
        )

        return count

    @staticmethod
    async def invalidate_list(entity_type: str) -> int:
        """
        Invalida cache de listagens de uma entidade.

        Args:
            entity_type: Tipo da entidade

        Returns:
            Número de chaves removidas

        Example:
            # Invalidar listagens de escalas
            await CacheManager.invalidate_list("scale")
        """
        patterns = [
            f"api:list_{entity_type}s:*",  # list_posts, list_scales, etc
            f"api:get_{entity_type}s_*",  # get_posts_by_*, etc
        ]

        total = 0
        for pattern in patterns:
            count = await cache_clear_pattern(pattern)
            total += count

        logger.info(
            "Cache de listagens invalidado",
            action="invalidate_list_cache",
            entity_type=entity_type,
            keys_removed=total,
        )

        return total

    @staticmethod
    async def invalidate_stats(entity_type: str | None = None) -> int:
        """
        Invalida cache de estatísticas.

        Args:
            entity_type: Tipo específico (opcional)

        Returns:
            Número de chaves removidas
        """
        if entity_type:
            pattern = f"api:*{entity_type}*stats*"
        else:
            pattern = "api:*stats*"

        count = await cache_clear_pattern(pattern)

        logger.info(
            "Cache de stats invalidado",
            action="invalidate_stats_cache",
            entity_type=entity_type,
            keys_removed=count,
        )

        return count

    @staticmethod
    async def invalidate_related(entity_type: str, related_ids: list[str]) -> int:
        """
        Invalida cache de entidades relacionadas.

        Args:
            entity_type: Tipo da entidade
            related_ids: Lista de IDs relacionados

        Returns:
            Número total de chaves removidas

        Example:
            # Quando uma escala é criada, invalidar cache do posto
            await CacheManager.invalidate_related("post", [post_id])
        """
        total = 0
        for related_id in related_ids:
            count = await CacheManager.invalidate_entity(entity_type, related_id)
            total += count

        return total

    @staticmethod
    async def invalidate_by_user(user_id: str) -> int:
        """
        Invalida cache específico de um usuário.

        Args:
            user_id: ID do usuário

        Returns:
            Número de chaves removidas
        """
        pattern = f"*:user:{user_id}:*"
        count = await cache_clear_pattern(pattern)

        logger.info(
            "Cache de usuário invalidado",
            action="invalidate_user_cache",
            user_id=user_id,
            keys_removed=count,
        )

        return count


# Helpers de invalidação por operação


async def invalidate_on_create(entity_type: str, related_entities: list[tuple] | None = None):
    """
    Invalida cache após criação de entidade.

    Args:
        entity_type: Tipo da entidade criada
        related_entities: Lista de (tipo, id) relacionados

    Example:
        # Criar uma alocação invalida listagens + post relacionado
        await invalidate_on_create("allocation", [("post", post_id)])
    """
    # Invalidar listagens
    await CacheManager.invalidate_list(entity_type)

    # Invalidar stats
    await CacheManager.invalidate_stats(entity_type)

    # Invalidar relacionados
    if related_entities:
        for rel_type, rel_id in related_entities:
            await CacheManager.invalidate_entity(rel_type, rel_id)


async def invalidate_on_update(entity_type: str, entity_id: str, related_entities: list[tuple] | None = None):
    """
    Invalida cache após atualização de entidade.

    Args:
        entity_type: Tipo da entidade
        entity_id: ID da entidade atualizada
        related_entities: Lista de (tipo, id) relacionados
    """
    # Invalidar entidade específica
    await CacheManager.invalidate_entity(entity_type, entity_id)

    # Invalidar listagens
    await CacheManager.invalidate_list(entity_type)

    # Invalidar stats
    await CacheManager.invalidate_stats(entity_type)

    # Invalidar relacionados
    if related_entities:
        for rel_type, rel_id in related_entities:
            await CacheManager.invalidate_entity(rel_type, rel_id)


async def invalidate_on_delete(entity_type: str, entity_id: str, related_entities: list[tuple] | None = None):
    """
    Invalida cache após deleção de entidade.

    Args:
        entity_type: Tipo da entidade
        entity_id: ID da entidade deletada
        related_entities: Lista de (tipo, id) relacionados
    """
    # Invalidar entidade específica
    await CacheManager.invalidate_entity(entity_type, entity_id)

    # Invalidar listagens
    await CacheManager.invalidate_list(entity_type)

    # Invalidar stats
    await CacheManager.invalidate_stats(entity_type)

    # Invalidar relacionados
    if related_entities:
        for rel_type, rel_id in related_entities:
            await CacheManager.invalidate_entity(rel_type, rel_id)
