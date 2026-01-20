"""
Service para Comunicados Operacionais.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.communication.models.announcement import (
    Announcement,
    AnnouncementStatus,
)
from modules.operacional.communication.models.announcement_read import AnnouncementRead
from modules.operacional.communication.repositories.communication_repository import (
    AnnouncementRepository,
)
from modules.operacional.communication.schemas.communication_schemas import (
    AnnouncementCreate,
    AnnouncementFilter,
    AnnouncementUpdate,
    AnnouncementReadStats,
)

logger = logging.getLogger(__name__)


class AnnouncementServiceError(Exception):
    """Excecao base para erros do AnnouncementService."""

    pass


class AnnouncementNotFoundError(AnnouncementServiceError):
    """Comunicado nao encontrado."""

    pass


class AnnouncementPublishError(AnnouncementServiceError):
    """Erro ao publicar comunicado."""

    pass


class AnnouncementService:
    """
    Service para gerenciamento de Comunicados.

    Fornece logica de negocio para criar, publicar, agendar e gerenciar
    comunicados, incluindo controle de leituras e confirmacoes.

    Attributes:
        db: Sessao assincrona do banco de dados
        repository: Repository de comunicados

    Example:
        >>> service = AnnouncementService(db)
        >>> announcement = await service.create(data, tenant_id, user_id)
        >>> await service.publish(announcement.id, tenant_id, user_id)
    """

    def __init__(self, db: AsyncSession) -> None:
        """
        Inicializa o service.

        Args:
            db: Sessao assincrona do banco de dados
        """
        self.db = db
        self.repository = AnnouncementRepository(db)

    async def create(
        self,
        data: AnnouncementCreate,
        tenant_id: str,
        created_by: str,
    ) -> Announcement:
        """
        Cria um novo comunicado.

        Args:
            data: Dados do comunicado
            tenant_id: ID do tenant
            created_by: ID do usuario criador

        Returns:
            Comunicado criado

        Raises:
            AnnouncementServiceError: Se ocorrer erro na criacao
        """
        try:
            announcement = await self.repository.create(data, tenant_id, created_by)
            logger.info(
                f"Comunicado criado: {announcement.id} por {created_by}"
            )
            return announcement
        except Exception as e:
            logger.error(f"Erro ao criar comunicado: {e}")
            raise AnnouncementServiceError(f"Erro ao criar comunicado: {e}") from e

    async def get_by_id(
        self,
        announcement_id: str,
        tenant_id: str,
    ) -> Announcement:
        """
        Busca comunicado por ID.

        Args:
            announcement_id: ID do comunicado
            tenant_id: ID do tenant

        Returns:
            Comunicado encontrado

        Raises:
            AnnouncementNotFoundError: Se nao encontrado
        """
        announcement = await self.repository.get_by_id(announcement_id, tenant_id)
        if not announcement:
            raise AnnouncementNotFoundError(
                f"Comunicado nao encontrado: {announcement_id}"
            )
        return announcement

    async def list(
        self,
        tenant_id: str,
        filters: Optional[AnnouncementFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Announcement], int]:
        """
        Lista comunicados com filtros e paginacao.

        Args:
            tenant_id: ID do tenant
            filters: Filtros de busca
            page: Pagina atual
            page_size: Itens por pagina

        Returns:
            Tupla (comunicados, total)
        """
        return await self.repository.list(tenant_id, filters, page, page_size)

    async def update(
        self,
        announcement_id: str,
        data: AnnouncementUpdate,
        tenant_id: str,
    ) -> Announcement:
        """
        Atualiza um comunicado.

        Args:
            announcement_id: ID do comunicado
            data: Dados para atualizacao
            tenant_id: ID do tenant

        Returns:
            Comunicado atualizado

        Raises:
            AnnouncementNotFoundError: Se nao encontrado
            AnnouncementServiceError: Se nao puder ser editado
        """
        announcement = await self.repository.update(announcement_id, data, tenant_id)
        if not announcement:
            raise AnnouncementNotFoundError(
                f"Comunicado nao encontrado ou nao pode ser editado: {announcement_id}"
            )
        return announcement

    async def delete(
        self,
        announcement_id: str,
        tenant_id: str,
    ) -> bool:
        """
        Remove um comunicado (soft delete).

        Args:
            announcement_id: ID do comunicado
            tenant_id: ID do tenant

        Returns:
            True se removido

        Raises:
            AnnouncementNotFoundError: Se nao encontrado
        """
        deleted = await self.repository.delete(announcement_id, tenant_id)
        if not deleted:
            raise AnnouncementNotFoundError(
                f"Comunicado nao encontrado: {announcement_id}"
            )
        return True

    async def publish(
        self,
        announcement_id: str,
        tenant_id: str,
        published_by: str,
        schedule_at: Optional[datetime] = None,
    ) -> Announcement:
        """
        Publica ou agenda um comunicado.

        Args:
            announcement_id: ID do comunicado
            tenant_id: ID do tenant
            published_by: ID do usuario que publica
            schedule_at: Data/hora para agendamento (None = publicar agora)

        Returns:
            Comunicado publicado/agendado

        Raises:
            AnnouncementNotFoundError: Se nao encontrado
            AnnouncementPublishError: Se nao puder ser publicado
        """
        announcement = await self.repository.publish(
            announcement_id, tenant_id, published_by, schedule_at
        )
        if not announcement:
            raise AnnouncementPublishError(
                f"Comunicado nao pode ser publicado: {announcement_id}"
            )

        # Notificar usuarios se publicado imediatamente
        if not schedule_at:
            await self._notify_recipients(announcement)

        return announcement

    async def _notify_recipients(self, announcement: Announcement) -> None:
        """
        Envia notificacoes para destinatarios do comunicado.

        Args:
            announcement: Comunicado publicado
        """
        try:
            from .notification_service import NotificationService
            from modules.operacional.communication.models.notification import (
                NotificationType,
                NotificationChannel,
            )
            from modules.operacional.communication.schemas.communication_schemas import (
                NotificationCreate,
            )

            notification_service = NotificationService(self.db)

            # Determina canais baseado na prioridade
            channels = [NotificationChannel.IN_APP]
            if announcement.priority in ("importante", "urgente"):
                channels.append(NotificationChannel.PUSH)

            # TODO: Buscar usuarios destinatarios baseado em target_type/target_ids
            # Por enquanto, apenas log
            logger.info(
                f"Notificando destinatarios do comunicado {announcement.id}"
            )

        except Exception as e:
            logger.error(f"Erro ao notificar destinatarios: {e}")

    async def get_for_user(
        self,
        tenant_id: str,
        user_id: str,
        user_roles: List[str],
        department_id: Optional[str] = None,
        post_id: Optional[str] = None,
        only_unread: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Announcement], int]:
        """
        Busca comunicados relevantes para um usuario.

        Args:
            tenant_id: ID do tenant
            user_id: ID do usuario
            user_roles: Roles do usuario
            department_id: ID do departamento
            post_id: ID do posto
            only_unread: Apenas nao lidos
            page: Pagina atual
            page_size: Itens por pagina

        Returns:
            Tupla (comunicados, total)
        """
        return await self.repository.get_for_user(
            tenant_id=tenant_id,
            user_id=user_id,
            user_roles=user_roles,
            department_id=department_id,
            post_id=post_id,
            only_unread=only_unread,
            page=page,
            page_size=page_size,
        )

    async def mark_as_read(
        self,
        announcement_id: str,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[AnnouncementRead]:
        """
        Marca comunicado como lido por um usuario.

        Args:
            announcement_id: ID do comunicado
            user_id: ID do usuario
            ip_address: Endereco IP
            user_agent: User-Agent

        Returns:
            Registro de leitura ou None se ja lido
        """
        return await self.repository.mark_as_read(
            announcement_id, user_id, ip_address, user_agent
        )

    async def acknowledge(
        self,
        announcement_id: str,
        user_id: str,
        tenant_id: str,
    ) -> AnnouncementRead:
        """
        Confirma leitura de comunicado.

        Args:
            announcement_id: ID do comunicado
            user_id: ID do usuario
            tenant_id: ID do tenant

        Returns:
            Registro de leitura

        Raises:
            AnnouncementNotFoundError: Se comunicado ou leitura nao encontrados
        """
        # Verifica se o comunicado existe
        await self.get_by_id(announcement_id, tenant_id)

        # Primeiro marca como lido se ainda nao foi
        await self.repository.mark_as_read(announcement_id, user_id)

        # Depois confirma
        read = await self.repository.acknowledge(announcement_id, user_id)
        if not read:
            raise AnnouncementNotFoundError(
                f"Registro de leitura nao encontrado: {announcement_id}"
            )

        return read

    async def get_read_stats(
        self,
        announcement_id: str,
        tenant_id: str,
    ) -> AnnouncementReadStats:
        """
        Obtem estatisticas de leitura de um comunicado.

        Args:
            announcement_id: ID do comunicado
            tenant_id: ID do tenant

        Returns:
            Estatisticas de leitura

        Raises:
            AnnouncementNotFoundError: Se nao encontrado
        """
        # Verifica se existe
        await self.get_by_id(announcement_id, tenant_id)

        stats = await self.repository.get_read_stats(announcement_id, tenant_id)
        if not stats:
            raise AnnouncementNotFoundError(
                f"Comunicado nao encontrado: {announcement_id}"
            )

        from modules.operacional.communication.schemas.communication_schemas import (
            AnnouncementReadResponse,
        )

        return AnnouncementReadStats(
            total_recipients=stats["total_recipients"],
            total_reads=stats["total_reads"],
            total_acknowledgments=stats["total_acknowledgments"],
            read_percentage=stats["read_percentage"],
            acknowledgment_percentage=stats["acknowledgment_percentage"],
            reads=[
                AnnouncementReadResponse.model_validate(r) for r in stats["reads"]
            ],
        )

    async def process_scheduled(self) -> int:
        """
        Processa comunicados agendados.

        Returns:
            Quantidade de comunicados publicados
        """
        count = await self.repository.process_scheduled()
        if count > 0:
            logger.info(f"Comunicados agendados publicados: {count}")
        return count

    async def process_expired(self) -> int:
        """
        Processa comunicados expirados.

        Returns:
            Quantidade de comunicados expirados
        """
        count = await self.repository.process_expired()
        if count > 0:
            logger.info(f"Comunicados expirados: {count}")
        return count

    async def get_unread_for_user(
        self,
        tenant_id: str,
        user_id: str,
        user_roles: List[str],
    ) -> List[Announcement]:
        """
        Busca comunicados nao lidos para um usuario.

        Args:
            tenant_id: ID do tenant
            user_id: ID do usuario
            user_roles: Roles do usuario

        Returns:
            Lista de comunicados nao lidos
        """
        announcements, _ = await self.get_for_user(
            tenant_id=tenant_id,
            user_id=user_id,
            user_roles=user_roles,
            only_unread=True,
            page=1,
            page_size=100,  # Limite para nao lidos
        )
        return announcements

    async def count_unread_for_user(
        self,
        tenant_id: str,
        user_id: str,
        user_roles: List[str],
    ) -> int:
        """
        Conta comunicados nao lidos para um usuario.

        Args:
            tenant_id: ID do tenant
            user_id: ID do usuario
            user_roles: Roles do usuario

        Returns:
            Quantidade de comunicados nao lidos
        """
        _, total = await self.get_for_user(
            tenant_id=tenant_id,
            user_id=user_id,
            user_roles=user_roles,
            only_unread=True,
            page=1,
            page_size=1,
        )
        return total
