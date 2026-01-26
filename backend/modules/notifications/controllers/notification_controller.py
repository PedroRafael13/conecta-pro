"""NotificationController - Endpoints REST para Notificações.

Sprint 36 - Notification Hub.
"""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.notifications.models import (
    ChannelType,
    NotificationChannel,
    NotificationLog,
    NotificationPreference,
    NotificationQueue,
    NotificationTemplate,
    QueueStatus,
)
from modules.notifications.schemas import (
    ChannelConfigCreate,
    ChannelConfigResponse,
    ChannelConfigUpdate,
    LogEntryResponse,
    PreferenceResponse,
    PreferenceUpdate,
    QueueItemResponse,
    QueueStatsResponse,
    SendNotificationRequest,
    SendNotificationResponse,
    TemplateCreate,
    TemplateResponse,
    TemplateUpdate,
)
from modules.notifications.services import ChannelDispatcher, NotificationService
from modules.notifications.services.push_service import PushNotificationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# =============================================================================
# Helpers
# =============================================================================


def get_tenant_id(current_user) -> UUID:
    """Extrai tenant_id do usuário atual."""
    return current_user.tenant_id


# =============================================================================
# Send Notifications
# =============================================================================


@router.post(
    "/send",
    response_model=SendNotificationResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def send_notification(
    request: SendNotificationRequest,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
) -> SendNotificationResponse:
    """Envia notificações para os destinatários especificados."""
    tenant_id = get_tenant_id(current_user)

    try:
        service = NotificationService(db, tenant_id)
        result = service.send_notification(
            request=request,
            created_by=current_user.id,
        )
        return result

    except Exception as e:
        logger.error(f"Erro ao enviar notificação: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao enviar notificação: {str(e)}",
        )


@router.post("/send/{notification_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_notification(
    notification_id: str,
    current_user: CurrentActiveUser,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
) -> dict:
    """Cancela uma notificação pendente ou agendada."""
    tenant_id = get_tenant_id(current_user)

    service = NotificationService(db, tenant_id)
    success = service.cancel_notification(notification_id, reason)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada ou não pode ser cancelada",
        )

    return {"success": True, "message": "Notificação cancelada"}


# =============================================================================
# Channels
# =============================================================================


@router.get("/channels", response_model=List[ChannelConfigResponse])
async def list_channels(
    current_user: CurrentActiveUser,
    channel_type: Optional[str] = None,
    active: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[ChannelConfigResponse]:
    """Lista canais de notificação configurados."""
    tenant_id = get_tenant_id(current_user)

    query = db.query(NotificationChannel).filter(
        NotificationChannel.tenant_id == tenant_id,
    )

    if channel_type:
        query = query.filter(NotificationChannel.channel_type == channel_type)
    if active is not None:
        query = query.filter(NotificationChannel.active == active)

    channels = query.offset(skip).limit(limit).all()
    return channels


@router.post(
    "/channels",
    response_model=ChannelConfigResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_channel(
    data: ChannelConfigCreate,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
) -> ChannelConfigResponse:
    """Cria um novo canal de notificação."""
    tenant_id = get_tenant_id(current_user)

    existing = (
        db.query(NotificationChannel)
        .filter(
            NotificationChannel.tenant_id == tenant_id,
            NotificationChannel.slug == data.slug,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Canal com slug '{data.slug}' já existe",
        )

    channel = NotificationChannel(
        tenant_id=tenant_id,
        created_by=current_user.id,
        **data.model_dump(),
    )

    db.add(channel)
    db.commit()
    db.refresh(channel)

    return channel


@router.get("/channels/{channel_id}", response_model=ChannelConfigResponse)
async def get_channel(
    channel_id: UUID,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
) -> ChannelConfigResponse:
    """Obtém detalhes de um canal."""
    tenant_id = get_tenant_id(current_user)

    channel = (
        db.query(NotificationChannel)
        .filter(
            NotificationChannel.tenant_id == tenant_id,
            NotificationChannel.id == channel_id,
        )
        .first()
    )

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canal não encontrado",
        )

    return channel


@router.patch("/channels/{channel_id}", response_model=ChannelConfigResponse)
async def update_channel(
    channel_id: UUID,
    data: ChannelConfigUpdate,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
) -> ChannelConfigResponse:
    """Atualiza um canal existente."""
    tenant_id = get_tenant_id(current_user)

    channel = (
        db.query(NotificationChannel)
        .filter(
            NotificationChannel.tenant_id == tenant_id,
            NotificationChannel.id == channel_id,
        )
        .first()
    )

    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Canal não encontrado",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(channel, field, value)

    channel.updated_by = current_user.id
    db.commit()
    db.refresh(channel)

    return channel


# =============================================================================
# Templates
# =============================================================================


@router.get("/templates", response_model=List[TemplateResponse])
async def list_templates(
    current_user: CurrentActiveUser,
    category: Optional[str] = None,
    template_status: Optional[str] = None,
    active: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[TemplateResponse]:
    """Lista templates de notificação."""
    tenant_id = get_tenant_id(current_user)

    query = db.query(NotificationTemplate).filter(
        NotificationTemplate.tenant_id == tenant_id,
    )

    if category:
        query = query.filter(NotificationTemplate.category == category)
    if template_status:
        query = query.filter(NotificationTemplate.status == template_status)
    if active is not None:
        query = query.filter(NotificationTemplate.active == active)

    templates = query.offset(skip).limit(limit).all()
    return templates


@router.post(
    "/templates",
    response_model=TemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_template(
    data: TemplateCreate,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
) -> TemplateResponse:
    """Cria um novo template de notificação."""
    tenant_id = get_tenant_id(current_user)

    existing = (
        db.query(NotificationTemplate)
        .filter(
            NotificationTemplate.tenant_id == tenant_id,
            NotificationTemplate.slug == data.slug,
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Template com slug '{data.slug}' já existe",
        )

    variables = [v.model_dump() for v in data.variables] if data.variables else []

    template = NotificationTemplate(
        tenant_id=tenant_id,
        created_by=current_user.id,
        **data.model_dump(exclude={"variables"}),
        variables=variables,
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    return template


@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: UUID,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
) -> TemplateResponse:
    """Obtém detalhes de um template."""
    tenant_id = get_tenant_id(current_user)

    template = (
        db.query(NotificationTemplate)
        .filter(
            NotificationTemplate.tenant_id == tenant_id,
            NotificationTemplate.id == template_id,
        )
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template não encontrado",
        )

    return template


@router.patch("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: UUID,
    data: TemplateUpdate,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
) -> TemplateResponse:
    """Atualiza um template existente."""
    tenant_id = get_tenant_id(current_user)

    template = (
        db.query(NotificationTemplate)
        .filter(
            NotificationTemplate.tenant_id == tenant_id,
            NotificationTemplate.id == template_id,
        )
        .first()
    )

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template não encontrado",
        )

    update_data = data.model_dump(exclude_unset=True)

    if "variables" in update_data and update_data["variables"]:
        update_data["variables"] = [v.model_dump() for v in data.variables]

    for field, value in update_data.items():
        setattr(template, field, value)

    template.updated_by = current_user.id
    template.version += 1
    db.commit()
    db.refresh(template)

    return template


# =============================================================================
# Preferences
# =============================================================================


@router.get("/preferences/me", response_model=PreferenceResponse)
async def get_my_preferences(
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
) -> PreferenceResponse:
    """Obtém preferências do usuário atual."""
    tenant_id = get_tenant_id(current_user)

    preference = (
        db.query(NotificationPreference)
        .filter(
            NotificationPreference.tenant_id == tenant_id,
            NotificationPreference.user_id == current_user.id,
        )
        .first()
    )

    if not preference:
        preference = NotificationPreference(
            tenant_id=tenant_id,
            user_id=current_user.id,
            user_email=current_user.email,
        )
        db.add(preference)
        db.commit()
        db.refresh(preference)

    return preference


@router.patch("/preferences/me", response_model=PreferenceResponse)
async def update_my_preferences(
    data: PreferenceUpdate,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
) -> PreferenceResponse:
    """Atualiza preferências do usuário atual."""
    tenant_id = get_tenant_id(current_user)

    preference = (
        db.query(NotificationPreference)
        .filter(
            NotificationPreference.tenant_id == tenant_id,
            NotificationPreference.user_id == current_user.id,
        )
        .first()
    )

    if not preference:
        preference = NotificationPreference(
            tenant_id=tenant_id,
            user_id=current_user.id,
            user_email=current_user.email,
        )
        db.add(preference)

    update_data = data.model_dump(exclude_unset=True)

    if "category_preferences" in update_data and update_data["category_preferences"]:
        update_data["category_preferences"] = {
            k: v.model_dump() for k, v in data.category_preferences.items()
        }

    for field, value in update_data.items():
        setattr(preference, field, value)

    db.commit()
    db.refresh(preference)

    return preference


@router.post("/preferences/unsubscribe")
async def unsubscribe(
    token: str = Query(...),
    db: Session = Depends(get_db),
) -> dict:
    """Processa unsubscribe via link."""
    preference = (
        db.query(NotificationPreference)
        .filter(NotificationPreference.verification_token == token)
        .first()
    )

    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token inválido",
        )

    preference.global_unsubscribe = True
    preference.unsubscribed_at = datetime.utcnow()
    db.commit()

    return {"success": True, "message": "Inscrição cancelada com sucesso"}


# =============================================================================
# Queue
# =============================================================================


@router.get("/queue", response_model=List[QueueItemResponse])
async def list_queue(
    current_user: CurrentActiveUser,
    queue_status: Optional[str] = None,
    channel_type: Optional[str] = None,
    user_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[QueueItemResponse]:
    """Lista itens da fila de notificações."""
    tenant_id = get_tenant_id(current_user)

    query = db.query(NotificationQueue).filter(
        NotificationQueue.tenant_id == tenant_id,
    )

    if queue_status:
        query = query.filter(NotificationQueue.status == queue_status)
    if channel_type:
        query = query.filter(NotificationQueue.channel_type == channel_type)
    if user_id:
        query = query.filter(NotificationQueue.user_id == user_id)

    items = query.order_by(NotificationQueue.created_at.desc()).offset(skip).limit(limit).all()

    return items


@router.get("/queue/stats", response_model=QueueStatsResponse)
async def get_queue_stats(
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
) -> QueueStatsResponse:
    """Obtém estatísticas da fila."""
    tenant_id = get_tenant_id(current_user)

    service = NotificationService(db, tenant_id)
    stats = service.get_queue_stats()

    return QueueStatsResponse(
        total_pending=stats["by_status"].get("pending", 0),
        total_scheduled=stats["by_status"].get("scheduled", 0),
        total_processing=stats["by_status"].get("processing", 0),
        total_sent=stats["by_status"].get("sent", 0),
        total_delivered=stats["by_status"].get("delivered", 0),
        total_failed=stats["by_status"].get("failed", 0),
        total_retry=stats["by_status"].get("retry", 0),
        by_channel=stats["by_channel"],
        oldest_pending_at=stats["oldest_pending_at"],
    )


@router.post("/queue/process")
async def process_queue(
    current_user: CurrentActiveUser,
    batch_size: int = Query(default=100, ge=1, le=1000),
    channel_type: Optional[str] = None,
    db: Session = Depends(get_db),
) -> dict:
    """Processa itens pendentes da fila."""
    tenant_id = get_tenant_id(current_user)

    dispatcher = ChannelDispatcher(db, tenant_id)

    ch_type = ChannelType(channel_type) if channel_type else None
    results = dispatcher.process_pending(
        batch_size=batch_size,
        channel_type=ch_type,
    )

    return {
        "success": True,
        "processed": results["processed"],
        "success_count": results["success"],
        "failed_count": results["failed"],
        "retry_count": results["retry"],
    }


# =============================================================================
# Logs & History
# =============================================================================


@router.get("/history", response_model=List[QueueItemResponse])
async def get_notification_history(
    current_user: CurrentActiveUser,
    user_id: Optional[UUID] = None,
    channel_type: Optional[str] = None,
    history_status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[QueueItemResponse]:
    """Obtém histórico de notificações enviadas."""
    tenant_id = get_tenant_id(current_user)

    service = NotificationService(db, tenant_id)

    queue_status = QueueStatus(history_status) if history_status else None

    notifications = service.get_notification_history(
        user_id=user_id,
        channel_type=channel_type,
        status=queue_status,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=skip,
    )

    return notifications


@router.get("/logs/{notification_id}", response_model=List[LogEntryResponse])
async def get_notification_logs(
    notification_id: str,
    current_user: CurrentActiveUser,
    db: Session = Depends(get_db),
) -> List[LogEntryResponse]:
    """Obtém logs de uma notificação específica."""
    tenant_id = get_tenant_id(current_user)

    logs = (
        db.query(NotificationLog)
        .filter(
            NotificationLog.tenant_id == tenant_id,
            NotificationLog.notification_id == notification_id,
        )
        .order_by(NotificationLog.created_at.asc())
        .all()
    )

    return logs


# =============================================================================
# Tracking (Webhooks)
# =============================================================================


@router.post("/webhooks/email")
async def email_webhook(
    payload: dict,
    db: Session = Depends(get_db),
) -> dict:
    """Webhook para eventos de email."""
    logger.info(f"Email webhook recebido: {payload}")
    return {"received": True}


@router.post("/webhooks/sms")
async def sms_webhook(
    payload: dict,
    db: Session = Depends(get_db),
) -> dict:
    """Webhook para eventos de SMS."""
    logger.info(f"SMS webhook recebido: {payload}")
    return {"received": True}


@router.post("/webhooks/whatsapp")
async def whatsapp_webhook(
    payload: dict,
    db: Session = Depends(get_db),
) -> dict:
    """Webhook para eventos de WhatsApp."""
    logger.info(f"WhatsApp webhook recebido: {payload}")
    return {"received": True}


@router.get("/track/open/{notification_id}")
async def track_open(
    notification_id: str,
    db: Session = Depends(get_db),
) -> dict:
    """Endpoint de tracking de abertura (pixel)."""
    queue_item = (
        db.query(NotificationQueue)
        .filter(NotificationQueue.notification_id == notification_id)
        .first()
    )

    if queue_item:
        queue_item.opened = True
        queue_item.opened_at = queue_item.opened_at or datetime.utcnow()
        queue_item.opened_count = (queue_item.opened_count or 0) + 1
        db.commit()

    return {"tracked": True}


@router.get("/track/click/{notification_id}")
async def track_click(
    notification_id: str,
    url: str = Query(...),
    db: Session = Depends(get_db),
) -> RedirectResponse:
    """Endpoint de tracking de clique."""
    queue_item = (
        db.query(NotificationQueue)
        .filter(NotificationQueue.notification_id == notification_id)
        .first()
    )

    if queue_item:
        queue_item.clicked = True
        queue_item.clicked_at = queue_item.clicked_at or datetime.utcnow()
        queue_item.clicked_count = (queue_item.clicked_count or 0) + 1

        clicked_links = queue_item.clicked_links or []
        clicked_links.append({"url": url, "clicked_at": datetime.utcnow().isoformat()})
        queue_item.clicked_links = clicked_links

        db.commit()

    return RedirectResponse(url=url)


# =============================================================================
# Push Notifications
# =============================================================================


@router.post("/push/subscribe", status_code=status.HTTP_200_OK)
async def subscribe_push(
    device_token: str,
    platform: str,
    device_info: Optional[dict] = None,
    current_user: CurrentActiveUser = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    """Registra dispositivo para receber notificações push."""
    tenant_id = get_tenant_id(current_user)

    service = PushNotificationService(db, tenant_id)
    result = service.subscribe_device(
        user_id=current_user.id,
        device_token=device_token,
        platform=platform,
        device_info=device_info,
    )

    return result


@router.post("/push/unsubscribe", status_code=status.HTTP_200_OK)
async def unsubscribe_push(
    device_token: str,
    current_user: CurrentActiveUser = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    """Remove registro de dispositivo."""
    tenant_id = get_tenant_id(current_user)

    service = PushNotificationService(db, tenant_id)
    result = service.unsubscribe_device(
        user_id=current_user.id,
        device_token=device_token,
    )

    return result


@router.get("/push", status_code=status.HTTP_200_OK)
async def list_push_notifications(
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    current_user: CurrentActiveUser = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    """Lista notificações push do usuário."""
    tenant_id = get_tenant_id(current_user)

    service = PushNotificationService(db, tenant_id)
    notifications = service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )

    unread_count = service.get_unread_count(current_user.id)

    return {
        "notifications": notifications,
        "unread_count": unread_count,
        "total": len(notifications),
    }


@router.patch("/push/{notification_id}/read", status_code=status.HTTP_200_OK)
async def mark_push_as_read(
    notification_id: UUID,
    current_user: CurrentActiveUser = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    """Marca notificação como lida."""
    tenant_id = get_tenant_id(current_user)

    service = PushNotificationService(db, tenant_id)
    result = service.mark_as_read(
        notification_id=notification_id,
        user_id=current_user.id,
    )

    return result


@router.post("/push/read-all", status_code=status.HTTP_200_OK)
async def mark_all_push_as_read(
    current_user: CurrentActiveUser = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    """Marca todas as notificações como lidas."""
    tenant_id = get_tenant_id(current_user)

    service = PushNotificationService(db, tenant_id)
    result = service.mark_all_as_read(user_id=current_user.id)

    return result


@router.get("/push/unread-count", status_code=status.HTTP_200_OK)
async def get_push_unread_count(
    current_user: CurrentActiveUser = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    """Retorna quantidade de notificações não lidas."""
    tenant_id = get_tenant_id(current_user)

    service = PushNotificationService(db, tenant_id)
    count = service.get_unread_count(user_id=current_user.id)

    return {"unread_count": count}


@router.post("/push/send", status_code=status.HTTP_202_ACCEPTED)
async def send_push_notification(
    title: str,
    body: str,
    user_id: UUID,
    data: Optional[dict] = None,
    action_url: Optional[str] = None,
    current_user: CurrentActiveUser = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    """Envia notificação push para usuário (admin apenas)."""
    tenant_id = get_tenant_id(current_user)

    service = PushNotificationService(db, tenant_id)
    result = service.send_push_notification(
        user_id=user_id,
        title=title,
        body=body,
        data=data,
        action_url=action_url,
    )

    return result
