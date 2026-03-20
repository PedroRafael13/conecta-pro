"""PushController - API REST para Push Notifications.

Sprint 37 - Push Notifications Mobile.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.notifications.push.models import (
    CampaignStatus,
    MetricPeriod,
    PushCampaign,
    PushDevice,
    PushNotification,
    PushSegment,
)
from modules.notifications.push.schemas import (
    CampaignAnalyticsResponse,
    CampaignCreateRequest,
    CampaignListResponse,
    CampaignResponse,
    CampaignUpdateRequest,
    DeviceListResponse,
    DeviceRegisterRequest,
    DeviceResponse,
    DeviceUpdateRequest,
    MetricsSummaryResponse,
    NotificationResponse,
    SegmentCreateRequest,
    SegmentResponse,
    SendPushRequest,
    SendPushResponse,
    TopicResponse,
    TopicSubscribeRequest,
    TopicUnsubscribeRequest,
)
from modules.notifications.push.services.push_service import PushService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/push", tags=["Push Notifications"])


def get_push_service(db: Session = Depends(get_db)) -> PushService:
    """Dependency para PushService."""
    return PushService(db)


# ============================================================================
# Device Endpoints
# ============================================================================


@router.post(
    "/devices/register",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar dispositivo",
    description="Registra um novo dispositivo para receber push notifications.",
)
async def register_device(
    request: DeviceRegisterRequest,
    current_user: CurrentActiveUser,
    push_service: PushService = Depends(get_push_service),
) -> DeviceResponse:
    """Registra dispositivo para push notifications."""
    try:
        device = push_service.register_device(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            device_id=request.device_id,
            device_token=request.device_token,
            platform=request.platform.value,
            app_id=request.app_id,
            app_version=request.app_version,
            platform_version=request.platform_version,
            device_model=request.device_model,
            device_manufacturer=request.device_manufacturer,
            device_name=request.device_name,
            device_language=request.device_language,
            device_timezone=request.device_timezone,
            supports_rich_notifications=request.supports_rich_notifications,
            supports_actions=request.supports_actions,
            supports_images=request.supports_images,
            notifications_enabled=request.notifications_enabled,
            sound_enabled=request.sound_enabled,
            badge_enabled=request.badge_enabled,
            subscribed_topics=request.subscribed_topics,
            tags=request.tags,
            latitude=request.latitude,
            longitude=request.longitude,
            country=request.country,
            city=request.city,
        )

        logger.info(
            "Device registered: %s for user %s",
            device.id,
            current_user.id,
        )

        return DeviceResponse.model_validate(device)

    except Exception as e:
        logger.error("Error registering device: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao registrar dispositivo",
        ) from e


@router.get(
    "/devices",
    response_model=DeviceListResponse,
    summary="Listar dispositivos",
    description="Lista todos os dispositivos do usuário.",
)
async def list_devices(
    current_user: CurrentActiveUser,
    platform: str | None = Query(None, description="Filtrar por plataforma"),
    active_only: bool = Query(True, description="Apenas dispositivos ativos"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    push_service: PushService = Depends(get_push_service),
) -> DeviceListResponse:
    """Lista dispositivos do usuário."""
    try:
        devices = push_service.get_user_devices(
            user_id=current_user.id,
            active_only=active_only,
        )

        # Filtrar por plataforma se especificado
        if platform:
            devices = [d for d in devices if d.platform.value == platform]

        # Paginação
        total = len(devices)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = devices[start:end]

        return DeviceListResponse(
            items=[DeviceResponse.model_validate(d) for d in paginated],
            total=total,
            page=page,
            page_size=page_size,
        )

    except Exception as e:
        logger.error("Error listing devices: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar dispositivos",
        ) from e


@router.get(
    "/devices/{device_id}",
    response_model=DeviceResponse,
    summary="Obter dispositivo",
    description="Obtém detalhes de um dispositivo específico.",
)
async def get_device(
    device_id: UUID,
    current_user: CurrentActiveUser,
    push_service: PushService = Depends(get_push_service),
) -> DeviceResponse:
    """Obtém detalhes do dispositivo."""
    device = (
        push_service.db.query(PushDevice)
        .filter(
            PushDevice.id == device_id,
            PushDevice.user_id == current_user.id,
        )
        .first()
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado",
        )

    return DeviceResponse.model_validate(device)


@router.patch(
    "/devices/{device_id}",
    response_model=DeviceResponse,
    summary="Atualizar dispositivo",
    description="Atualiza configurações do dispositivo.",
)
async def update_device(
    device_id: UUID,
    request: DeviceUpdateRequest,
    current_user: CurrentActiveUser,
    push_service: PushService = Depends(get_push_service),
) -> DeviceResponse:
    """Atualiza dispositivo."""
    device = (
        push_service.db.query(PushDevice)
        .filter(
            PushDevice.id == device_id,
            PushDevice.user_id == current_user.id,
        )
        .first()
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado",
        )

    try:
        # Atualizar campos fornecidos
        update_data = request.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(device, field):
                setattr(device, field, value)

        device.updated_at = datetime.utcnow()
        push_service.db.commit()
        push_service.db.refresh(device)

        logger.info("Device updated: %s", device_id)
        return DeviceResponse.model_validate(device)

    except Exception as e:
        push_service.db.rollback()
        logger.error("Error updating device: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar dispositivo",
        ) from e


@router.delete(
    "/devices/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover dispositivo",
    description="Remove registro do dispositivo.",
)
async def unregister_device(
    device_id: UUID,
    current_user: CurrentActiveUser,
    push_service: PushService = Depends(get_push_service),
) -> None:
    """Remove registro do dispositivo."""
    device = (
        push_service.db.query(PushDevice)
        .filter(
            PushDevice.id == device_id,
            PushDevice.user_id == current_user.id,
        )
        .first()
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo não encontrado",
        )

    try:
        push_service.unregister_device(device_id=device_id)
        logger.info("Device unregistered: %s", device_id)

    except Exception as e:
        logger.error("Error unregistering device: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao remover dispositivo",
        ) from e


# ============================================================================
# Topic Endpoints
# ============================================================================


@router.post(
    "/topics/subscribe",
    response_model=TopicResponse,
    summary="Inscrever em tópico",
    description="Inscreve dispositivos em um tópico de notificações.",
)
async def subscribe_to_topic(
    request: TopicSubscribeRequest,
    current_user: CurrentActiveUser,
    push_service: PushService = Depends(get_push_service),
) -> TopicResponse:
    """Inscreve em tópico."""
    try:
        # Se user_ids fornecido, usa eles
        # Senão, usa device_ids
        # Senão, usa todos os dispositivos do usuário atual
        device_ids = request.device_ids

        if request.user_ids:
            # Buscar dispositivos dos usuários
            devices = (
                push_service.db.query(PushDevice)
                .filter(
                    PushDevice.user_id.in_(request.user_ids),
                    PushDevice.active == True,  # noqa: E712
                )
                .all()
            )
            device_ids = [d.id for d in devices]
        elif not device_ids:
            # Usar dispositivos do usuário atual
            devices = push_service.get_user_devices(
                user_id=current_user.id,
                active_only=True,
            )
            device_ids = [d.id for d in devices]

        result = push_service.subscribe_to_topic(
            topic=request.topic,
            device_ids=device_ids,
        )

        # Contar inscritos no tópico
        count = (
            push_service.db.query(PushDevice)
            .filter(
                PushDevice.subscribed_topics.contains([request.topic]),
                PushDevice.active == True,  # noqa: E712
            )
            .count()
        )

        logger.info(
            "Subscribed %d devices to topic '%s'",
            result["success_count"],
            request.topic,
        )

        return TopicResponse(
            topic=request.topic,
            subscriber_count=count,
        )

    except Exception as e:
        logger.error("Error subscribing to topic: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao inscrever em tópico",
        ) from e


@router.post(
    "/topics/unsubscribe",
    response_model=TopicResponse,
    summary="Desinscrever de tópico",
    description="Remove dispositivos de um tópico de notificações.",
)
async def unsubscribe_from_topic(
    request: TopicUnsubscribeRequest,
    current_user: CurrentActiveUser,
    push_service: PushService = Depends(get_push_service),
) -> TopicResponse:
    """Remove inscrição de tópico."""
    try:
        device_ids = request.device_ids

        if request.user_ids:
            devices = (
                push_service.db.query(PushDevice)
                .filter(
                    PushDevice.user_id.in_(request.user_ids),
                )
                .all()
            )
            device_ids = [d.id for d in devices]
        elif not device_ids:
            devices = push_service.get_user_devices(
                user_id=current_user.id,
                active_only=True,
            )
            device_ids = [d.id for d in devices]

        result = push_service.unsubscribe_from_topic(
            topic=request.topic,
            device_ids=device_ids,
        )

        count = (
            push_service.db.query(PushDevice)
            .filter(
                PushDevice.subscribed_topics.contains([request.topic]),
                PushDevice.active == True,  # noqa: E712
            )
            .count()
        )

        logger.info(
            "Unsubscribed %d devices from topic '%s'",
            result["success_count"],
            request.topic,
        )

        return TopicResponse(
            topic=request.topic,
            subscriber_count=count,
        )

    except Exception as e:
        logger.error("Error unsubscribing from topic: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao desinscrever de tópico",
        ) from e


@router.get(
    "/topics",
    response_model=list[TopicResponse],
    summary="Listar tópicos",
    description="Lista tópicos disponíveis e contagem de inscritos.",
)
async def list_topics(
    current_user: CurrentActiveUser,
    push_service: PushService = Depends(get_push_service),
) -> list[TopicResponse]:
    """Lista tópicos com contagem."""
    try:
        # Buscar todos os tópicos únicos do tenant
        devices = (
            push_service.db.query(PushDevice)
            .filter(
                PushDevice.tenant_id == current_user.tenant_id,
                PushDevice.active == True,  # noqa: E712
            )
            .all()
        )

        # Agregar tópicos
        topic_counts: dict[str, int] = {}
        for device in devices:
            for topic in device.subscribed_topics or []:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1

        return [TopicResponse(topic=topic, subscriber_count=count) for topic, count in sorted(topic_counts.items())]

    except Exception as e:
        logger.error("Error listing topics: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar tópicos",
        ) from e


# ============================================================================
# Notification Endpoints
# ============================================================================


@router.post(
    "/send",
    response_model=SendPushResponse,
    summary="Enviar notificação",
    description="Envia push notification para usuários, dispositivos ou tópicos.",
)
async def send_notification(
    request: SendPushRequest,
    current_user: CurrentActiveUser,
    push_service: PushService = Depends(get_push_service),
) -> SendPushResponse:
    """Envia push notification."""
    try:
        results = {
            "total_targeted": 0,
            "total_queued": 0,
            "total_failed": 0,
            "notification_ids": [],
            "failed_devices": [],
        }

        # Enviar para tópicos
        if request.topics:
            for topic in request.topics:
                result = push_service.send_to_topic(
                    tenant_id=current_user.tenant_id,
                    topic=topic,
                    title=request.title,
                    body=request.body,
                    image_url=request.image_url,
                    data=request.data_payload,
                    priority=request.priority.value,
                )
                if result.get("success"):
                    results["total_queued"] += 1
                    results["notification_ids"].append(result.get("notification_id"))
                else:
                    results["total_failed"] += 1

        # Enviar para usuários
        if request.user_ids:
            for user_id in request.user_ids:
                result = push_service.send_to_user(
                    tenant_id=current_user.tenant_id,
                    user_id=user_id,
                    title=request.title,
                    body=request.body,
                    image_url=request.image_url,
                    click_action=request.click_action,
                    data=request.data_payload,
                    priority=request.priority.value,
                    collapse_key=request.collapse_key,
                )
                results["total_targeted"] += result.get("total_devices", 0)
                results["total_queued"] += result.get("success_count", 0)
                results["total_failed"] += result.get("failure_count", 0)
                results["notification_ids"].extend(result.get("notification_ids", []))

        # Enviar para dispositivos específicos
        if request.device_ids:
            result = push_service.send_to_devices(
                tenant_id=current_user.tenant_id,
                device_ids=request.device_ids,
                title=request.title,
                body=request.body,
                image_url=request.image_url,
                click_action=request.click_action,
                data=request.data_payload,
                priority=request.priority.value,
            )
            results["total_targeted"] += len(request.device_ids)
            results["total_queued"] += result.get("success_count", 0)
            results["total_failed"] += result.get("failure_count", 0)
            results["notification_ids"].extend(result.get("notification_ids", []))

        logger.info(
            "Push sent: %d queued, %d failed",
            results["total_queued"],
            results["total_failed"],
        )

        return SendPushResponse(
            success=results["total_queued"] > 0,
            message=(
                f"Enviado para {results['total_queued']} dispositivos"
                if results["total_queued"] > 0
                else "Nenhum dispositivo recebeu a notificação"
            ),
            notification_ids=results["notification_ids"],
            total_targeted=results["total_targeted"],
            total_queued=results["total_queued"],
            total_failed=results["total_failed"],
            failed_devices=results["failed_devices"],
        )

    except Exception as e:
        logger.error("Error sending notification: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao enviar notificação",
        ) from e


@router.get(
    "/notifications",
    response_model=list[NotificationResponse],
    summary="Listar notificações",
    description="Lista notificações enviadas.",
)
async def list_notifications(
    current_user: CurrentActiveUser,
    user_id: UUID | None = Query(None, description="Filtrar por usuário"),
    device_id: UUID | None = Query(None, description="Filtrar por dispositivo"),
    status_filter: str | None = Query(None, description="Filtrar por status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    push_service: PushService = Depends(get_push_service),
) -> list[NotificationResponse]:
    """Lista notificações."""
    try:
        query = push_service.db.query(PushNotification).filter(
            PushNotification.tenant_id == current_user.tenant_id,
        )

        if user_id:
            query = query.filter(PushNotification.user_id == user_id)
        if device_id:
            query = query.filter(PushNotification.device_id == device_id)
        if status_filter:
            query = query.filter(PushNotification.status == status_filter)

        query = query.order_by(PushNotification.created_at.desc())

        # Paginação
        offset = (page - 1) * page_size
        notifications = query.offset(offset).limit(page_size).all()

        return [NotificationResponse.model_validate(n) for n in notifications]

    except Exception as e:
        logger.error("Error listing notifications: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar notificações",
        ) from e


@router.post(
    "/notifications/{notification_id}/opened",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Marcar como aberta",
    description="Registra que a notificação foi aberta pelo usuário.",
)
async def mark_notification_opened(
    notification_id: str,
    current_user: CurrentActiveUser,
    push_service: PushService = Depends(get_push_service),
) -> None:
    """Marca notificação como aberta."""
    try:
        push_service.record_notification_opened(notification_id=notification_id)
        logger.debug("Notification opened: %s", notification_id)
    except Exception as e:
        logger.error("Error marking notification opened: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao registrar abertura",
        ) from e


@router.post(
    "/notifications/{notification_id}/clicked",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Marcar como clicada",
    description="Registra que o usuário interagiu com a notificação.",
)
async def mark_notification_clicked(
    notification_id: str,
    current_user: CurrentActiveUser,  # pylint: disable=unused-argument
    action_id: str | None = Query(None, description="ID da ação clicada"),
    push_service: PushService = Depends(get_push_service),
) -> None:
    """Marca notificação como clicada."""
    try:
        push_service.record_notification_clicked(
            notification_id=notification_id,
            action_id=action_id,
        )
        logger.debug("Notification clicked: %s (action: %s)", notification_id, action_id)
    except Exception as e:
        logger.error("Error marking notification clicked: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao registrar clique",
        ) from e


# ============================================================================
# Campaign Endpoints
# ============================================================================


@router.post(
    "/campaigns",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar campanha",
    description="Cria uma nova campanha de push notifications.",
)
async def create_campaign(
    request: CampaignCreateRequest,
    current_user: CurrentActiveUser,
    push_service: PushService = Depends(get_push_service),
) -> CampaignResponse:
    """Cria campanha de push."""
    try:
        campaign = push_service.create_campaign(
            tenant_id=current_user.tenant_id,
            created_by=current_user.id,
            name=request.name,
            description=request.description,
            campaign_type=request.campaign_type.value,
            title=request.title,
            body=request.body,
            image_url=request.image_url,
            icon_url=request.icon_url,
            ios_subtitle=request.ios_subtitle,
            ios_sound=request.ios_sound,
            ios_badge=request.ios_badge,
            android_channel_id=request.android_channel_id,
            android_color=request.android_color,
            android_priority=request.android_priority,
            click_action=request.click_action,
            action_buttons=[b.model_dump() for b in request.action_buttons],
            data_payload=request.data_payload,
            target_type=request.target_type.value,
            target_segment_id=request.target_segment_id,
            target_users=request.target_users,
            target_topics=request.target_topics,
            target_tags=request.target_tags,
            target_platforms=request.target_platforms,
            scheduled_at=request.scheduled_at,
            timezone=request.timezone,
            optimal_time=request.optimal_time,
            ttl_seconds=request.ttl_seconds,
            rate_limit_per_second=request.rate_limit_per_second,
            category=request.category,
            tags=request.tags,
        )

        logger.info("Campaign created: %s", campaign.id)
        return CampaignResponse.model_validate(campaign)

    except Exception as e:
        logger.error("Error creating campaign: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar campanha",
        ) from e


@router.get(
    "/campaigns",
    response_model=CampaignListResponse,
    summary="Listar campanhas",
    description="Lista campanhas de push notifications.",
)
async def list_campaigns(
    current_user: CurrentActiveUser,
    status_filter: str | None = Query(None, description="Filtrar por status"),
    campaign_type: str | None = Query(None, description="Filtrar por tipo"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    push_service: PushService = Depends(get_push_service),
) -> CampaignListResponse:
    """Lista campanhas."""
    try:
        query = push_service.db.query(PushCampaign).filter(
            PushCampaign.tenant_id == current_user.tenant_id,
        )

        if status_filter:
            query = query.filter(PushCampaign.status == status_filter)
        if campaign_type:
            query = query.filter(PushCampaign.campaign_type == campaign_type)

        total = query.count()
        query = query.order_by(PushCampaign.created_at.desc())

        offset = (page - 1) * page_size
        campaigns = query.offset(offset).limit(page_size).all()

        return CampaignListResponse(
            items=[CampaignResponse.model_validate(c) for c in campaigns],
            total=total,
            page=page,
            page_size=page_size,
        )

    except Exception as e:
        logger.error("Error listing campaigns: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar campanhas",
        ) from e


@router.get(
    "/campaigns/{campaign_id}",
    response_model=CampaignResponse,
    summary="Obter campanha",
    description="Obtém detalhes de uma campanha.",
)
async def get_campaign(
    campaign_id: UUID,
    current_user: CurrentActiveUser,
    push_service: PushService = Depends(get_push_service),
) -> CampaignResponse:
    """Obtém campanha."""
    campaign = (
        push_service.db.query(PushCampaign)
        .filter(
            PushCampaign.id == campaign_id,
            PushCampaign.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha não encontrada",
        )

    return CampaignResponse.model_validate(campaign)


@router.patch(
    "/campaigns/{campaign_id}",
    response_model=CampaignResponse,
    summary="Atualizar campanha",
    description="Atualiza uma campanha (apenas se não iniciada).",
)
async def update_campaign(
    campaign_id: UUID,
    request: CampaignUpdateRequest,
    current_user: CurrentActiveUser,
    push_service: PushService = Depends(get_push_service),
) -> CampaignResponse:
    """Atualiza campanha."""
    campaign = (
        push_service.db.query(PushCampaign)
        .filter(
            PushCampaign.id == campaign_id,
            PushCampaign.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha não encontrada",
        )

    if campaign.status not in [CampaignStatus.DRAFT, CampaignStatus.SCHEDULED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campanha já iniciada não pode ser alterada",
        )

    try:
        update_data = request.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(campaign, field):
                setattr(campaign, field, value)

        campaign.updated_at = datetime.utcnow()
        push_service.db.commit()
        push_service.db.refresh(campaign)

        logger.info("Campaign updated: %s", campaign_id)
        return CampaignResponse.model_validate(campaign)

    except Exception as e:
        push_service.db.rollback()
        logger.error("Error updating campaign: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao atualizar campanha",
        ) from e


@router.post(
    "/campaigns/{campaign_id}/send",
    response_model=SendPushResponse,
    summary="Enviar campanha",
    description="Inicia o envio de uma campanha.",
)
async def send_campaign(
    campaign_id: UUID,
    current_user: CurrentActiveUser,
    push_service: PushService = Depends(get_push_service),
) -> SendPushResponse:
    """Envia campanha."""
    campaign = (
        push_service.db.query(PushCampaign)
        .filter(
            PushCampaign.id == campaign_id,
            PushCampaign.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha não encontrada",
        )

    if campaign.status not in [CampaignStatus.DRAFT, CampaignStatus.SCHEDULED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Campanha com status '{campaign.status.value}' não pode ser enviada",
        )

    try:
        result = push_service.send_campaign(campaign_id=campaign_id)

        logger.info(
            "Campaign %s sent: %d targeted, %d success",
            campaign_id,
            result.get("total_targeted", 0),
            result.get("success_count", 0),
        )

        return SendPushResponse(
            success=result.get("success_count", 0) > 0,
            message=f"Campanha enviada: {result.get('success_count', 0)} de {result.get('total_targeted', 0)}",
            notification_ids=[],
            total_targeted=result.get("total_targeted", 0),
            total_queued=result.get("success_count", 0),
            total_failed=result.get("failure_count", 0),
        )

    except Exception as e:
        logger.error("Error sending campaign: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao enviar campanha",
        ) from e


@router.delete(
    "/campaigns/{campaign_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir campanha",
    description="Exclui uma campanha (soft delete).",
)
async def delete_campaign(
    campaign_id: UUID,
    current_user: CurrentActiveUser,
    push_service: PushService = Depends(get_push_service),
) -> None:
    """Exclui campanha."""
    campaign = (
        push_service.db.query(PushCampaign)
        .filter(
            PushCampaign.id == campaign_id,
            PushCampaign.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha não encontrada",
        )

    try:
        campaign.active = False
        campaign.updated_at = datetime.utcnow()
        push_service.db.commit()

        logger.info("Campaign deleted: %s", campaign_id)

    except Exception as e:
        push_service.db.rollback()
        logger.error("Error deleting campaign: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao excluir campanha",
        ) from e


@router.get(
    "/campaigns/{campaign_id}/analytics",
    response_model=CampaignAnalyticsResponse,
    summary="Analytics da campanha",
    description="Obtém métricas detalhadas de uma campanha.",
)
async def get_campaign_analytics(
    campaign_id: UUID,
    current_user: CurrentActiveUser,
    push_service: PushService = Depends(get_push_service),
) -> CampaignAnalyticsResponse:
    """Obtém analytics da campanha."""
    campaign = (
        push_service.db.query(PushCampaign)
        .filter(
            PushCampaign.id == campaign_id,
            PushCampaign.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campanha não encontrada",
        )

    # Calcular taxas
    delivery_rate = (campaign.total_delivered / campaign.total_sent * 100) if campaign.total_sent > 0 else 0.0
    open_rate = (campaign.total_opened / campaign.total_delivered * 100) if campaign.total_delivered > 0 else 0.0
    click_rate = (campaign.total_clicked / campaign.total_opened * 100) if campaign.total_opened > 0 else 0.0

    return CampaignAnalyticsResponse(
        campaign_id=campaign.id,
        campaign_name=campaign.name,
        total_targeted=campaign.total_targeted,
        total_sent=campaign.total_sent,
        total_delivered=campaign.total_delivered,
        total_opened=campaign.total_opened,
        total_clicked=campaign.total_clicked,
        total_converted=0,
        delivery_rate=delivery_rate,
        open_rate=open_rate,
        click_rate=click_rate,
        conversion_rate=0.0,
    )


# ============================================================================
# Segment Endpoints
# ============================================================================


@router.post(
    "/segments",
    response_model=SegmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar segmento",
    description="Cria um novo segmento de dispositivos.",
)
async def create_segment(
    request: SegmentCreateRequest,
    current_user: CurrentActiveUser,
    push_service: PushService = Depends(get_push_service),
) -> SegmentResponse:
    """Cria segmento."""
    try:
        segment = PushSegment(
            tenant_id=current_user.tenant_id,
            created_by=current_user.id,
            name=request.name,
            description=request.description,
            rules=[r.model_dump() for r in request.rules],
            rules_logic=request.rules_logic,
            is_dynamic=request.is_dynamic,
        )

        push_service.db.add(segment)
        push_service.db.commit()
        push_service.db.refresh(segment)

        logger.info("Segment created: %s", segment.id)
        return SegmentResponse.model_validate(segment)

    except Exception as e:
        push_service.db.rollback()
        logger.error("Error creating segment: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao criar segmento",
        ) from e


@router.get(
    "/segments",
    response_model=list[SegmentResponse],
    summary="Listar segmentos",
    description="Lista segmentos de dispositivos.",
)
async def list_segments(
    current_user: CurrentActiveUser,
    push_service: PushService = Depends(get_push_service),
) -> list[SegmentResponse]:
    """Lista segmentos."""
    try:
        segments = (
            push_service.db.query(PushSegment)
            .filter(
                PushSegment.tenant_id == current_user.tenant_id,
                PushSegment.active == True,  # noqa: E712
            )
            .order_by(PushSegment.name)
            .all()
        )

        return [SegmentResponse.model_validate(s) for s in segments]

    except Exception as e:
        logger.error("Error listing segments: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao listar segmentos",
        ) from e


# ============================================================================
# Analytics Endpoints
# ============================================================================


@router.get(
    "/analytics/summary",
    response_model=MetricsSummaryResponse,
    summary="Resumo de métricas",
    description="Obtém resumo de métricas de push notifications.",
)
async def get_metrics_summary(
    current_user: CurrentActiveUser,
    period: MetricPeriod = Query(MetricPeriod.DAILY),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    platform: str | None = Query(None),
    push_service: PushService = Depends(get_push_service),
) -> MetricsSummaryResponse:
    """Obtém resumo de métricas."""
    try:
        # Definir período padrão (últimos 30 dias)
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            from datetime import timedelta

            start_date = end_date - timedelta(days=30)

        summary = push_service.get_metrics_summary(
            tenant_id=current_user.tenant_id,
            period=period.value,
            start_date=start_date,
            end_date=end_date,
            platform=platform,
        )

        return MetricsSummaryResponse(
            period=period,
            start_date=start_date,
            end_date=end_date,
            total_sent=summary.get("total_sent", 0),
            total_delivered=summary.get("total_delivered", 0),
            total_opened=summary.get("total_opened", 0),
            total_clicked=summary.get("total_clicked", 0),
            delivery_rate=summary.get("delivery_rate", 0.0),
            open_rate=summary.get("open_rate", 0.0),
            click_rate=summary.get("click_rate", 0.0),
            total_devices_active=summary.get("total_devices", 0),
            new_devices=summary.get("new_devices", 0),
            platform_breakdown=summary.get("platform_breakdown", {}),
        )

    except Exception as e:
        logger.error("Error getting metrics summary: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter métricas",
        ) from e


@router.get(
    "/analytics/devices",
    summary="Estatísticas de dispositivos",
    description="Obtém estatísticas de dispositivos registrados.",
)
async def get_device_stats(
    current_user: CurrentActiveUser,
    push_service: PushService = Depends(get_push_service),
) -> dict[str, Any]:
    """Obtém estatísticas de dispositivos."""
    try:
        # Total por plataforma
        devices = (
            push_service.db.query(PushDevice)
            .filter(
                PushDevice.tenant_id == current_user.tenant_id,
            )
            .all()
        )

        stats = {
            "total": len(devices),
            "active": len([d for d in devices if d.active]),
            "inactive": len([d for d in devices if not d.active]),
            "notifications_enabled": len([d for d in devices if d.notifications_enabled]),
            "by_platform": {},
            "by_status": {},
        }

        for device in devices:
            platform = device.platform.value
            status_val = device.status.value

            stats["by_platform"][platform] = stats["by_platform"].get(platform, 0) + 1
            stats["by_status"][status_val] = stats["by_status"].get(status_val, 0) + 1

        return stats

    except Exception as e:
        logger.error("Error getting device stats: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter estatísticas",
        ) from e
