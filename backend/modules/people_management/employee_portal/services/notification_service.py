"""
Notification Service — Gerenciamento de notificacoes do portal.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.people_management.employee_portal.models.notification import (
    PortalNotification,
    PortalNotificationType,
)

logger = logging.getLogger(__name__)


class PortalNotificationService:
    """Servico de notificacoes do portal do funcionario.

    Gerencia envio, listagem e marcacao de leitura de notificacoes.

    Attributes:
        db: Sessao async do banco de dados.
    """

    def __init__(self, db: AsyncSession) -> None:
        """Inicializa o servico com sessao de banco.

        Args:
            db: Sessao async do SQLAlchemy.
        """
        self.db = db

    async def get_notifications(
        self,
        employee_id: UUID,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Lista notificacoes do funcionario.

        Args:
            employee_id: UUID do funcionario.
            unread_only: Se True, retorna apenas nao lidas.
            limit: Quantidade maxima de resultados.
            offset: Paginacao — registros a pular.

        Returns:
            Lista de dicts com dados das notificacoes.
        """
        query = select(PortalNotification).where(PortalNotification.employee_id == employee_id)

        if unread_only:
            query = query.where(PortalNotification.is_read.is_(False))

        query = query.order_by(PortalNotification.created_at.desc())
        query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        notifications = result.scalars().all()

        return [
            {
                "id": n.id,
                "type": n.notification_type.value if n.notification_type else "general",
                "title": n.title,
                "message": n.message,
                "is_read": n.is_read,
                "read_at": n.read_at.isoformat() if n.read_at else None,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notifications
        ]

    async def mark_read(
        self,
        notification_id: int,
        employee_id: UUID,
    ) -> bool:
        """Marca uma notificacao como lida.

        Args:
            notification_id: ID da notificacao.
            employee_id: UUID do funcionario (para validacao de propriedade).

        Returns:
            True se marcada com sucesso, False se nao encontrada.
        """
        query = select(PortalNotification).where(
            PortalNotification.id == notification_id,
            PortalNotification.employee_id == employee_id,
        )
        result = await self.db.execute(query)
        notification = result.scalar_one_or_none()

        if not notification:
            return False

        notification.is_read = True
        notification.read_at = datetime.utcnow()

        try:
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error("Erro ao marcar notificacao como lida: %s", e)
            return False

    async def send_notification(
        self,
        employee_id: UUID,
        title: str,
        message: str | None = None,
        notification_type: str = "general",
    ) -> int | None:
        """Envia uma notificacao para o funcionario.

        Args:
            employee_id: UUID do funcionario destinatario.
            title: Titulo da notificacao.
            message: Corpo da mensagem (opcional).
            notification_type: Tipo da notificacao.

        Returns:
            ID da notificacao criada, ou None em caso de erro.
        """
        try:
            notif_type = PortalNotificationType(notification_type)
        except ValueError:
            notif_type = PortalNotificationType.GENERAL

        notification = PortalNotification(
            employee_id=employee_id,
            notification_type=notif_type,
            title=title,
            message=message,
            is_read=False,
            created_at=datetime.utcnow(),
        )

        try:
            self.db.add(notification)
            await self.db.commit()
            await self.db.refresh(notification)

            logger.info(
                "Notificacao enviada: employee_id=%s title=%s",
                employee_id,
                title,
            )
            return notification.id

        except Exception as e:
            await self.db.rollback()
            logger.error("Erro ao enviar notificacao: %s", e, exc_info=True)
            return None
