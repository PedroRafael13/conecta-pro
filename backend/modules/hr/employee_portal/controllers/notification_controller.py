"""Controller para notificações do portal."""

import logging
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user, require_roles
from core.database import get_async_session
from modules.hr.employee_portal.models import NotificationType
from modules.hr.employee_portal.schemas import (
    NotificationCreate,
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
)
from modules.hr.employee_portal.services import PortalNotificationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Portal - Notificações"])


@router.get(
    "/",
    response_model=NotificationListResponse,
    summary="Listar notificações",
)
async def list_notifications(
    is_read: bool | None = Query(None, description="Filtrar por lidas/não lidas"),
    notification_type: NotificationType | None = Query(None, alias="type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Lista notificações do funcionário."""
    service = PortalNotificationService(db)
    employee_id = UUID(current_user["employee_id"])

    notifications, total = await service.list_notifications(
        employee_id,
        page=page,
        page_size=page_size,
        is_read=is_read,
        notification_type=notification_type,
    )

    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in notifications],
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get(
    "/unread-count",
    response_model=UnreadCountResponse,
    summary="Contagem de não lidas",
)
async def get_unread_count(
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Retorna contagem de notificações não lidas."""
    service = PortalNotificationService(db)
    employee_id = UUID(current_user["employee_id"])

    return await service.get_unread_count(employee_id)


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    summary="Visualizar notificação",
)
async def get_notification(
    notification_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Visualiza notificação específica."""
    service = PortalNotificationService(db)
    employee_id = UUID(current_user["employee_id"])

    notification = await service.repo.get_by_id(notification_id)
    if not notification or notification.employee_id != employee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada",
        )

    return NotificationResponse.model_validate(notification)


@router.post(
    "/{notification_id}/read", response_model=NotificationResponse, summary="Marcar como lida", status_code=201
)
async def mark_as_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Marca notificação como lida."""
    service = PortalNotificationService(db)
    employee_id = UUID(current_user["employee_id"])

    notification = await service.mark_as_read(notification_id, employee_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada",
        )

    return NotificationResponse.model_validate(notification)


@router.post("/mark-multiple-read", summary="Marcar múltiplas como lidas", status_code=201)
async def mark_multiple_as_read(
    notification_ids: list[UUID] = Body(..., min_length=1, max_length=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Marca múltiplas notificações como lidas."""
    service = PortalNotificationService(db)
    employee_id = UUID(current_user["employee_id"])

    count = await service.mark_multiple_as_read(notification_ids, employee_id)

    return {
        "message": f"Marcadas {count} notificações como lidas",
        "count": count,
    }


@router.post("/mark-all-read", summary="Marcar todas como lidas", status_code=201)
async def mark_all_as_read(
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Marca todas as notificações como lidas."""
    service = PortalNotificationService(db)
    employee_id = UUID(current_user["employee_id"])

    count = await service.mark_all_as_read(employee_id)

    return {
        "message": f"Marcadas {count} notificações como lidas",
        "count": count,
    }


@router.post(
    "/{notification_id}/dismiss", response_model=NotificationResponse, summary="Descartar notificação", status_code=201
)
async def dismiss_notification(
    notification_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Descarta notificação (não será mais exibida)."""
    service = PortalNotificationService(db)
    employee_id = UUID(current_user["employee_id"])

    notification = await service.dismiss_notification(notification_id, employee_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada",
        )

    return NotificationResponse.model_validate(notification)


# --- Endpoints administrativos ---


@router.post(
    "/",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar notificação",
    dependencies=[Depends(require_roles(["admin", "hr"]))],
)
async def send_notification(
    data: NotificationCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Envia notificação para funcionário."""
    service = PortalNotificationService(db)
    condominio_id = UUID(current_user["condominio_id"])

    notification = await service.send_notification(
        employee_id=data.employee_id,
        notification_type=data.notification_type,
        title=data.title,
        message=data.message,
        condominio_id=condominio_id,
        reference_type=data.reference_type,
        reference_id=data.reference_id,
        action_url=data.action_url,
        action_label=data.action_label,
        extra_data=data.extra_data,
        created_by=UUID(current_user["sub"]),
    )

    return NotificationResponse.model_validate(notification)


@router.post(
    "/bulk",
    summary="Enviar notificação em lote",
    dependencies=[Depends(require_roles(["admin", "hr"], status_code=201))],
)
async def send_bulk_notification(
    employee_ids: list[UUID] = Body(..., min_length=1, max_length=1000),
    notification_type: NotificationType = Body(...),
    title: str = Body(..., min_length=1, max_length=200),
    message: str = Body(..., min_length=1, max_length=2000),
    db: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    """Envia notificação para múltiplos funcionários."""
    service = PortalNotificationService(db)
    condominio_id = UUID(current_user["condominio_id"])

    notifications = await service.send_bulk_notification(
        employee_ids=employee_ids,
        notification_type=notification_type,
        title=title,
        message=message,
        condominio_id=condominio_id,
        created_by=UUID(current_user["sub"]),
    )

    return {
        "message": f"Enviadas {len(notifications)} notificações",
        "count": len(notifications),
    }
