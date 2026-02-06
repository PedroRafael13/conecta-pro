"""
Service para Comunicados Operacionais.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.operacional.communication.models.announcement import (
    Announcement,
)
from modules.operacional.communication.models.announcement_read import AnnouncementRead
from modules.operacional.communication.repositories.communication_repository import (
    AnnouncementRepository,
)
from modules.operacional.communication.schemas.communication_schemas import (
    AnnouncementCreate,
    AnnouncementFilter,
    AnnouncementReadStats,
    AnnouncementUpdate,
)
from modules.operacional.models.employee import Employee

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
            logger.info(f"Comunicado criado: {announcement.id} por {created_by}")
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
            raise AnnouncementNotFoundError(f"Comunicado nao encontrado: {announcement_id}")
        return announcement

    async def list(
        self,
        tenant_id: str,
        filters: AnnouncementFilter | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Announcement], int]:
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
            raise AnnouncementNotFoundError(f"Comunicado nao encontrado ou nao pode ser editado: {announcement_id}")
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
            raise AnnouncementNotFoundError(f"Comunicado nao encontrado: {announcement_id}")
        return True

    async def publish(
        self,
        announcement_id: str,
        tenant_id: str,
        published_by: str,
        schedule_at: datetime | None = None,
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
        announcement = await self.repository.publish(announcement_id, tenant_id, published_by, schedule_at)
        if not announcement:
            raise AnnouncementPublishError(f"Comunicado nao pode ser publicado: {announcement_id}")

        # Notificar usuarios se publicado imediatamente
        if not schedule_at:
            await self._notify_recipients(announcement)

        return announcement

    async def _get_recipient_user_ids(self, announcement: Announcement) -> list[str]:
        """
        Busca IDs dos usuarios destinatarios baseado no tipo de destinatario.

        Args:
            announcement: Comunicado com configuracao de destinatarios

        Returns:
            Lista de IDs de funcionarios destinatarios
        """
        destinatarios_tipo = announcement.destinatarios_tipo or "todos"

        # Query base: funcionarios ativos do tenant
        query = select(Employee.id).where(
            Employee.is_active == True,  # noqa: E712
        )

        if destinatarios_tipo == "todos" or destinatarios_tipo == "all":
            # Todos os funcionarios ativos
            pass

        elif destinatarios_tipo == "post" or destinatarios_tipo == "posto":
            # Funcionarios alocados nos postos especificados
            if announcement.destinatarios_postos:
                query = query.where(Employee.posto_atual_id.in_(announcement.destinatarios_postos))
            else:
                logger.warning(f"Comunicado {announcement.id} com tipo 'post' mas sem postos definidos")
                return []

        elif destinatarios_tipo == "employee" or destinatarios_tipo == "funcionario":
            # Funcionarios especificos
            if announcement.destinatarios_funcionarios:
                query = query.where(Employee.id.in_(announcement.destinatarios_funcionarios))
            else:
                logger.warning(f"Comunicado {announcement.id} com tipo 'employee' mas sem funcionarios definidos")
                return []

        elif destinatarios_tipo == "department" or destinatarios_tipo == "departamento":
            # Funcionarios do departamento (usar extra_data para departamento_ids)
            department_ids = (announcement.extra_data or {}).get("departamento_ids", [])
            if department_ids:
                query = query.where(Employee.departamento_id.in_(department_ids))
            else:
                logger.warning(f"Comunicado {announcement.id} com tipo 'department' mas sem departamentos definidos")
                return []

        elif destinatarios_tipo == "client" or destinatarios_tipo == "cliente":
            # Funcionarios alocados em clientes especificos
            client_ids = (announcement.extra_data or {}).get("cliente_ids", [])
            if client_ids:
                query = query.where(Employee.cliente_id.in_(client_ids))
            else:
                logger.warning(f"Comunicado {announcement.id} com tipo 'client' mas sem clientes definidos")
                return []

        elif destinatarios_tipo == "role" or destinatarios_tipo == "cargo":
            # Funcionarios com cargo especifico
            role_ids = (announcement.extra_data or {}).get("cargo_ids", [])
            if role_ids:
                query = query.where(Employee.cargo_id.in_(role_ids))
            else:
                logger.warning(f"Comunicado {announcement.id} com tipo 'role' mas sem cargos definidos")
                return []

        else:
            logger.warning(f"Tipo de destinatario desconhecido: {destinatarios_tipo}, usando 'todos'")

        result = await self.db.execute(query)
        employee_ids = [str(row[0]) for row in result.fetchall()]

        logger.info(
            f"Comunicado {announcement.id}: {len(employee_ids)} destinatarios encontrados (tipo: {destinatarios_tipo})"
        )
        return employee_ids

    async def _notify_recipients(self, announcement: Announcement) -> None:
        """
        Envia notificacoes para destinatarios do comunicado.

        Args:
            announcement: Comunicado publicado
        """
        try:
            from modules.operacional.communication.models.notification import (
                NotificationChannel,
                NotificationType,
            )
            from modules.operacional.communication.schemas.communication_schemas import (
                NotificationCreate,
            )

            from .notification_service import NotificationService

            notification_service = NotificationService(self.db)

            # Determina canais baseado na prioridade
            channels = [NotificationChannel.IN_APP]
            if announcement.prioridade in ("alta", "urgente"):
                channels.append(NotificationChannel.PUSH)
            if announcement.enviar_email:
                channels.append(NotificationChannel.EMAIL)

            # Busca usuarios destinatarios baseado em destinatarios_tipo
            recipient_ids = await self._get_recipient_user_ids(announcement)

            if not recipient_ids:
                logger.warning(f"Comunicado {announcement.id}: nenhum destinatario encontrado")
                return

            # Cria notificacoes para cada destinatario
            notifications = [
                NotificationCreate(
                    user_id=user_id,
                    title=announcement.titulo,
                    body=announcement.resumo or announcement.conteudo[:200],
                    type=NotificationType.COMUNICADO,
                    channels=channels,
                    reference_type="announcement",
                    reference_id=str(announcement.id),
                    action_url=f"/comunicados/{announcement.id}",
                    extra_data={
                        "announcement_id": str(announcement.id),
                        "prioridade": announcement.prioridade,
                        "requer_confirmacao": announcement.requer_confirmacao,
                    },
                )
                for user_id in recipient_ids
            ]

            # Envia em lote
            await notification_service.send_bulk(
                notifications=notifications,
                tenant_id=str(announcement.tenant_id),
            )

            # Atualiza contador de destinatarios
            announcement.total_destinatarios = len(recipient_ids)
            await self.db.commit()

            logger.info(f"Comunicado {announcement.id}: {len(notifications)} notificacoes enviadas")

        except Exception as e:
            logger.error(f"Erro ao notificar destinatarios: {e}")

    async def get_for_user(
        self,
        tenant_id: str,
        user_id: str,
        user_roles: list[str],
        department_id: str | None = None,
        post_id: str | None = None,
        only_unread: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Announcement], int]:
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
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AnnouncementRead | None:
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
        return await self.repository.mark_as_read(announcement_id, user_id, ip_address, user_agent)

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
            raise AnnouncementNotFoundError(f"Registro de leitura nao encontrado: {announcement_id}")

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
            raise AnnouncementNotFoundError(f"Comunicado nao encontrado: {announcement_id}")

        from modules.operacional.communication.schemas.communication_schemas import (
            AnnouncementReadResponse,
        )

        return AnnouncementReadStats(
            total_recipients=stats["total_recipients"],
            total_reads=stats["total_reads"],
            total_acknowledgments=stats["total_acknowledgments"],
            read_percentage=stats["read_percentage"],
            acknowledgment_percentage=stats["acknowledgment_percentage"],
            reads=[AnnouncementReadResponse.model_validate(r) for r in stats["reads"]],
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
        user_roles: list[str],
    ) -> list[Announcement]:
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
        user_roles: list[str],
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
