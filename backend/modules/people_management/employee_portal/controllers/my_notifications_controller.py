"""
My Notifications Controller — Notificacoes do funcionario no portal.

Endpoints:
- GET /portal/my-notifications
- PATCH /portal/my-notifications/{notification_id}/read
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from modules.people_management.employee_portal.auth import CurrentEmployeeId

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Portal - Notificacoes"])


class NotificationResponse(BaseModel):
    """Notificacao do portal do funcionario."""

    id: int | None = None
    title: str | None = None
    message: str | None = None
    is_read: bool = False
    notification_type: str | None = None
    created_at: str | None = None

    model_config = ConfigDict(from_attributes=True)


class NotificationReadResponse(BaseModel):
    """Resposta ao marcar notificacao como lida."""

    id: int
    is_read: bool = True
    read_at: str | None = None

    model_config = ConfigDict(from_attributes=True)


@router.get(
    "/my-notifications",
    response_model=list[NotificationResponse],
    summary="Minhas notificacoes",
    description="Retorna lista de notificacoes do funcionario logado.",
)
async def get_my_notifications(
    employee_id: CurrentEmployeeId,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna notificacoes do funcionario autenticado."""
    try:
        from sqlalchemy import select

        from modules.people_management.employee_portal.models.notification import (
            PortalNotification,
        )

        result = await db.execute(
            select(PortalNotification)
            .where(PortalNotification.employee_id == str(employee_id))
            .order_by(PortalNotification.created_at.desc())
        )
        notifications = result.scalars().all()

        return [
            NotificationResponse(
                id=n.id,
                title=n.title,
                message=n.message,
                is_read=n.is_read,
                notification_type=str(n.notification_type.value) if n.notification_type else None,
                created_at=str(n.created_at) if n.created_at else None,
            )
            for n in notifications
        ]

    except (ImportError, Exception) as e:
        logger.warning(f"Erro ao buscar notificacoes do funcionario {employee_id}: {e}")

    return []


@router.patch(
    "/my-notifications/{notification_id}/read",
    response_model=NotificationReadResponse,
    summary="Marcar notificacao como lida",
    description="Marca uma notificacao especifica como lida.",
)
async def mark_notification_as_read(
    notification_id: int,
    employee_id: CurrentEmployeeId,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Marca uma notificacao como lida para o funcionario autenticado."""
    try:
        from sqlalchemy import select

        from modules.people_management.employee_portal.models.notification import (
            PortalNotification,
        )

        result = await db.execute(
            select(PortalNotification).where(
                PortalNotification.id == notification_id,
                PortalNotification.employee_id == str(employee_id),
            )
        )
        notification = result.scalar_one_or_none()

        if not notification:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Notificacao {notification_id} nao encontrada.",
            )

        notification.is_read = True
        notification.read_at = datetime.utcnow()
        await db.commit()
        await db.refresh(notification)

        logger.info(f"Notificacao {notification_id} marcada como lida pelo funcionario {employee_id}")

        return NotificationReadResponse(
            id=notification.id,
            is_read=True,
            read_at=str(notification.read_at),
        )

    except HTTPException:
        raise
    except (ImportError, Exception) as e:
        logger.warning(f"Erro ao marcar notificacao {notification_id} como lida: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar notificacao.",
        )
