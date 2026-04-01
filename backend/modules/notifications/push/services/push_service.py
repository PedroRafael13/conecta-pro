"""PushService - Serviço de Orquestração de Push Notifications.

Sprint 37 - Push Notifications Mobile.
"""

import hashlib
import logging
import uuid as uuid_module
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from modules.notifications.push.models import (
    CampaignStatus,
    DevicePlatform,
    DeviceStatus,
    NotificationPriority,
    NotificationStatus,
    PushCampaign,
    PushDevice,
    PushNotification,
    PushNotificationAction,
    TargetType,
)
from modules.notifications.push.services.apns_service import APNsService
from modules.notifications.push.services.fcm_service import FCMMessage, FCMService

logger = logging.getLogger(__name__)


class PushService:
    """Serviço principal de Push Notifications."""

    def __init__(self, db: Session, tenant_id: UUID):
        """Inicializa o serviço.

        Args:
            db: Sessão do banco de dados.
            tenant_id: ID do tenant.
        """
        self.db = db
        self.tenant_id = tenant_id
        self._fcm_service: FCMService | None = None
        self._apns_service: APNsService | None = None

    # ========================================================================
    # Device Management
    # ========================================================================

    def register_device(
        self,
        user_id: UUID,
        device_id: str,
        device_token: str,
        platform: DevicePlatform,
        app_id: str,
        **kwargs: Any,
    ) -> PushDevice:
        """Registra ou atualiza um dispositivo.

        Args:
            user_id: ID do usuário.
            device_id: ID único do dispositivo.
            device_token: Token FCM/APNs.
            platform: Plataforma (ios, android, web).
            app_id: Bundle ID / Package name.
            **kwargs: Campos adicionais.

        Returns:
            PushDevice registrado.
        """
        # Busca dispositivo existente
        device = (
            self.db.query(PushDevice)
            .filter(
                PushDevice.tenant_id == self.tenant_id,
                PushDevice.device_id == device_id,
            )
            .first()
        )

        token_hash = hashlib.sha256(device_token.encode()).hexdigest()

        if device:
            # Atualiza dispositivo existente
            device.device_token = device_token
            device.device_token_hash = token_hash
            device.user_id = user_id
            device.platform = platform
            device.app_id = app_id
            device.token_updated_at = datetime.utcnow()
            device.last_active_at = datetime.utcnow()
            device.status = DeviceStatus.ACTIVE
            device.consecutive_failures = 0

            # Atualiza campos adicionais
            for key, value in kwargs.items():
                if hasattr(device, key) and value is not None:
                    setattr(device, key, value)

            logger.info("Device updated: %s", device_id[:20])
        else:
            # Cria novo dispositivo
            device = PushDevice(
                tenant_id=self.tenant_id,
                user_id=user_id,
                device_id=device_id,
                device_token=device_token,
                device_token_hash=token_hash,
                platform=platform,
                app_id=app_id,
                token_registered_at=datetime.utcnow(),
                last_active_at=datetime.utcnow(),
                **kwargs,
            )
            self.db.add(device)
            logger.info("Device registered: %s", device_id[:20])

        self.db.commit()
        self.db.refresh(device)
        return device

    def unregister_device(self, device_id: str) -> bool:
        """Remove registro de dispositivo.

        Args:
            device_id: ID do dispositivo.

        Returns:
            True se removido com sucesso.
        """
        device = (
            self.db.query(PushDevice)
            .filter(
                PushDevice.tenant_id == self.tenant_id,
                PushDevice.device_id == device_id,
            )
            .first()
        )

        if device:
            device.status = DeviceStatus.UNREGISTERED
            device.active = False
            self.db.commit()
            logger.info("Device unregistered: %s", device_id[:20])
            return True

        return False

    def get_user_devices(
        self,
        user_id: UUID,
        active_only: bool = True,
    ) -> list[PushDevice]:
        """Obtém dispositivos de um usuário.

        Args:
            user_id: ID do usuário.
            active_only: Apenas dispositivos ativos.

        Returns:
            Lista de dispositivos.
        """
        query = self.db.query(PushDevice).filter(
            PushDevice.tenant_id == self.tenant_id,
            PushDevice.user_id == user_id,
        )

        if active_only:
            query = query.filter(
                PushDevice.active == True,  # noqa: E712
                PushDevice.status == DeviceStatus.ACTIVE,
            )

        return query.all()

    def update_device_activity(self, device_id: str) -> None:
        """Atualiza última atividade do dispositivo."""
        self.db.query(PushDevice).filter(
            PushDevice.tenant_id == self.tenant_id,
            PushDevice.device_id == device_id,
        ).update({"last_active_at": datetime.utcnow()})
        self.db.commit()

    # ========================================================================
    # Topic Management
    # ========================================================================

    def subscribe_to_topic(
        self,
        topic: str,
        device_ids: list[UUID] | None = None,
        user_ids: list[UUID] | None = None,
    ) -> dict[str, Any]:
        """Inscreve dispositivos em um tópico.

        Args:
            topic: Nome do tópico.
            device_ids: IDs dos dispositivos.
            user_ids: IDs dos usuários.

        Returns:
            Resultado da operação.
        """
        devices = self._get_devices_by_ids_or_users(device_ids, user_ids)

        if not devices:
            return {"success_count": 0, "failure_count": 0}

        # Agrupa por plataforma
        android_tokens = []
        ios_devices = []

        for device in devices:
            if topic not in (device.subscribed_topics or []):
                if device.subscribed_topics is None:
                    device.subscribed_topics = []
                device.subscribed_topics.append(topic)

            if device.platform in [DevicePlatform.ANDROID, DevicePlatform.WEB]:
                android_tokens.append(device.device_token)
            elif device.platform == DevicePlatform.IOS:
                ios_devices.append(device)

        self.db.commit()

        results = {"success_count": len(devices), "failure_count": 0}

        # FCM subscribe
        if android_tokens and self._fcm_service:
            fcm_result = self._fcm_service.subscribe_to_topic(android_tokens, topic)
            results["fcm"] = fcm_result

        logger.info("Subscribed %d devices to topic '%s'", len(devices), topic)
        return results

    def unsubscribe_from_topic(
        self,
        topic: str,
        device_ids: list[UUID] | None = None,
        user_ids: list[UUID] | None = None,
    ) -> dict[str, Any]:
        """Remove dispositivos de um tópico.

        Args:
            topic: Nome do tópico.
            device_ids: IDs dos dispositivos.
            user_ids: IDs dos usuários.

        Returns:
            Resultado da operação.
        """
        devices = self._get_devices_by_ids_or_users(device_ids, user_ids)

        if not devices:
            return {"success_count": 0, "failure_count": 0}

        android_tokens = []

        for device in devices:
            if device.subscribed_topics and topic in device.subscribed_topics:
                device.subscribed_topics.remove(topic)

            if device.platform in [DevicePlatform.ANDROID, DevicePlatform.WEB]:
                android_tokens.append(device.device_token)

        self.db.commit()

        results = {"success_count": len(devices), "failure_count": 0}

        # FCM unsubscribe
        if android_tokens and self._fcm_service:
            fcm_result = self._fcm_service.unsubscribe_from_topic(android_tokens, topic)
            results["fcm"] = fcm_result

        logger.info("Unsubscribed %d devices from topic '%s'", len(devices), topic)
        return results

    # ========================================================================
    # Send Notifications
    # ========================================================================

    def send_to_user(
        self,
        user_id: UUID,
        title: str,
        body: str,
        **kwargs: Any,
    ) -> list[PushNotification]:
        """Envia notificação para todos os dispositivos de um usuário.

        Args:
            user_id: ID do usuário.
            title: Título da notificação.
            body: Corpo da notificação.
            **kwargs: Campos adicionais.

        Returns:
            Lista de notificações criadas.
        """
        devices = self.get_user_devices(user_id, active_only=True)

        if not devices:
            logger.warning("No active devices for user %s", user_id)
            return []

        return self._send_to_devices(devices, title, body, **kwargs)

    def send_to_devices(
        self,
        device_ids: list[UUID],
        title: str,
        body: str,
        **kwargs: Any,
    ) -> list[PushNotification]:
        """Envia notificação para dispositivos específicos.

        Args:
            device_ids: IDs dos dispositivos.
            title: Título da notificação.
            body: Corpo da notificação.
            **kwargs: Campos adicionais.

        Returns:
            Lista de notificações criadas.
        """
        devices = (
            self.db.query(PushDevice)
            .filter(
                PushDevice.tenant_id == self.tenant_id,
                PushDevice.id.in_(device_ids),
                PushDevice.active == True,  # noqa: E712
                PushDevice.status == DeviceStatus.ACTIVE,
            )
            .all()
        )

        return self._send_to_devices(devices, title, body, **kwargs)

    def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Envia notificação para um tópico.

        Args:
            topic: Nome do tópico.
            title: Título da notificação.
            body: Corpo da notificação.
            **kwargs: Campos adicionais.

        Returns:
            Resultado do envio.
        """
        results = {
            "success": False,
            "topic": topic,
            "fcm_result": None,
        }

        # FCM topic send
        if self._fcm_service:
            fcm_response = self._fcm_service.send_to_topic(
                topic=topic,
                title=title,
                body=body,
                image=kwargs.get("image_url"),
                data=kwargs.get("data_payload"),
            )
            results["fcm_result"] = {
                "success": fcm_response.success,
                "message_id": fcm_response.message_id,
                "error": fcm_response.error_message,
            }
            results["success"] = fcm_response.success

        logger.info("Sent notification to topic '%s': success=%s", topic, results["success"])
        return results

    def _send_to_devices(
        self,
        devices: list[PushDevice],
        title: str,
        body: str,
        **kwargs: Any,
    ) -> list[PushNotification]:
        """Envia notificação para lista de dispositivos.

        Args:
            devices: Lista de dispositivos.
            title: Título.
            body: Corpo.
            **kwargs: Campos adicionais.

        Returns:
            Lista de notificações criadas.
        """
        notifications = []

        for device in devices:
            # Cria registro da notificação
            notification = PushNotification(
                tenant_id=self.tenant_id,
                notification_id=f"push_{uuid_module.uuid4().hex[:16]}",
                device_id=device.id,
                user_id=device.user_id,
                device_token=device.device_token,
                platform=device.platform.value,
                app_id=device.app_id,
                title=title,
                body=body,
                subtitle=kwargs.get("subtitle"),
                image_url=kwargs.get("image_url"),
                click_action=kwargs.get("click_action"),
                action_buttons=kwargs.get("action_buttons", []),
                data_payload=kwargs.get("data_payload", {}),
                priority=kwargs.get("priority", NotificationPriority.HIGH),
                ttl_seconds=kwargs.get("ttl_seconds", 86400),
                collapse_key=kwargs.get("collapse_key"),
                mutable_content=kwargs.get("mutable_content", False),
                content_available=kwargs.get("content_available", False),
                category=kwargs.get("category"),
                source_type=kwargs.get("source_type"),
                source_id=kwargs.get("source_id"),
                campaign_id=kwargs.get("campaign_id"),
                provider="fcm" if device.platform != DevicePlatform.IOS else "apns",
                status=NotificationStatus.PENDING,
            )

            self.db.add(notification)
            notifications.append(notification)

        self.db.commit()

        # Envia as notificações
        for notification in notifications:
            self._dispatch_notification(notification)

        return notifications

    def _dispatch_notification(self, notification: PushNotification) -> None:
        """Despacha notificação para o provedor apropriado.

        Args:
            notification: Notificação a enviar.
        """
        try:
            notification.update_status(NotificationStatus.SENDING)
            self.db.commit()

            if notification.platform in ["android", "web"]:
                success = self._send_via_fcm(notification)
            elif notification.platform == "ios":
                success = self._send_via_apns(notification)
            else:
                success = self._send_via_fcm(notification)  # Default to FCM

            if success:
                notification.update_status(NotificationStatus.SENT)
                self._update_device_stats(notification.device_id, success=True)
            else:
                if notification.is_retryable:
                    notification.update_status(NotificationStatus.PENDING)
                    notification.next_retry_at = datetime.utcnow() + timedelta(minutes=5)
                else:
                    notification.update_status(NotificationStatus.FAILED)
                    self._update_device_stats(notification.device_id, success=False)

            self.db.commit()

        except Exception as e:
            logger.error("Failed to dispatch notification: %s", e)
            notification.update_status(
                NotificationStatus.FAILED,
                details={"error": str(e)},
            )
            notification.error_message = str(e)
            self.db.commit()

    def _send_via_fcm(self, notification: PushNotification) -> bool:
        """Envia via Firebase Cloud Messaging."""
        if not self._fcm_service:
            # Simulação se não configurado
            logger.info("FCM: Simulating send to %s", notification.device_token[:20])
            notification.provider_message_id = f"fcm_sim_{datetime.utcnow().timestamp()}"
            return True

        message = FCMMessage(
            token=notification.device_token,
            title=notification.title,
            body=notification.body,
            image=notification.image_url,
            data=notification.data_payload,
            android=self._fcm_service.build_android_config(
                click_action=notification.click_action,
                ttl=notification.ttl_seconds,
                collapse_key=notification.collapse_key,
            ),
        )

        response = self._fcm_service.send(message)

        notification.provider_message_id = response.message_id
        notification.provider_status = "success" if response.success else "failed"
        notification.error_code = response.error_code
        notification.error_message = response.error_message
        notification.attempt += 1

        # Verifica token inválido
        if response.error_code and self._fcm_service.is_invalid_token_error(response.error_code):
            self._invalidate_device_token(notification.device_id, response.error_code)

        return response.success

    def _send_via_apns(self, notification: PushNotification) -> bool:
        """Envia via Apple Push Notification Service."""
        if not self._apns_service:
            # Simulação se não configurado
            logger.info("APNs: Simulating send to %s", notification.device_token[:20])
            notification.provider_message_id = f"apns_sim_{datetime.utcnow().timestamp()}"
            return True

        payload = self._apns_service.build_payload(
            title=notification.title,
            body=notification.body,
            subtitle=notification.subtitle,
            sound="default",
            mutable_content=notification.mutable_content,
            custom_data=notification.data_payload,
        )

        response = self._apns_service.send(
            device_token=notification.device_token,
            payload=payload,
            priority=10 if notification.priority == NotificationPriority.HIGH else 5,
        )

        notification.provider_message_id = response.apns_id
        notification.provider_status = "success" if response.success else "failed"
        notification.error_code = response.reason
        notification.attempt += 1

        # Verifica token inválido
        if response.reason and self._apns_service.is_invalid_token_error(response.reason):
            self._invalidate_device_token(notification.device_id, response.reason)

        return response.success

    def _update_device_stats(self, device_id: UUID, success: bool) -> None:
        """Atualiza estatísticas do dispositivo."""
        device = self.db.query(PushDevice).filter(PushDevice.id == device_id).first()
        if device:
            device.total_notifications_sent += 1
            device.last_notification_at = datetime.utcnow()
            if success:
                device.reset_failures()
            else:
                device.increment_failures()

    def _invalidate_device_token(self, device_id: UUID, reason: str) -> None:
        """Invalida token de dispositivo."""
        device = self.db.query(PushDevice).filter(PushDevice.id == device_id).first()
        if device:
            device.invalidate_token(reason)
            logger.warning("Device token invalidated: %s - %s", device_id, reason)

    def _get_devices_by_ids_or_users(
        self,
        device_ids: list[UUID] | None,
        user_ids: list[UUID] | None,
    ) -> list[PushDevice]:
        """Obtém dispositivos por IDs ou usuários."""
        query = self.db.query(PushDevice).filter(
            PushDevice.tenant_id == self.tenant_id,
            PushDevice.active == True,  # noqa: E712
            PushDevice.status == DeviceStatus.ACTIVE,
        )

        conditions = []
        if device_ids:
            conditions.append(PushDevice.id.in_(device_ids))
        if user_ids:
            conditions.append(PushDevice.user_id.in_(user_ids))

        if conditions:
            query = query.filter(or_(*conditions))

        return query.all()

    # ========================================================================
    # Campaign Management
    # ========================================================================

    def create_campaign(
        self,
        name: str,
        title: str,
        body: str,
        **kwargs: Any,
    ) -> PushCampaign:
        """Cria uma campanha de push.

        Args:
            name: Nome da campanha.
            title: Título da notificação.
            body: Corpo da notificação.
            **kwargs: Campos adicionais.

        Returns:
            Campanha criada.
        """
        campaign = PushCampaign(
            tenant_id=self.tenant_id,
            name=name,
            title=title,
            body=body,
            status=CampaignStatus.DRAFT,
            **kwargs,
        )

        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)

        logger.info("Campaign created: %s", campaign.name)
        return campaign

    def send_campaign(self, campaign_id: UUID) -> dict[str, Any]:
        """Executa envio de campanha.

        Args:
            campaign_id: ID da campanha.

        Returns:
            Resultado do envio.
        """
        campaign = (
            self.db.query(PushCampaign)
            .filter(
                PushCampaign.tenant_id == self.tenant_id,
                PushCampaign.id == campaign_id,
            )
            .first()
        )

        if not campaign:
            raise ValueError(f"Campaign not found: {campaign_id}")

        if not campaign.can_send():
            raise ValueError(f"Campaign cannot be sent: {campaign.status.value}")

        # Atualiza status
        campaign.status = CampaignStatus.SENDING
        campaign.started_at = datetime.utcnow()
        self.db.commit()

        try:
            # Obtém dispositivos alvo
            devices = self._get_campaign_targets(campaign)
            campaign.total_targeted = len(devices)

            # Envia para cada dispositivo
            notifications = self._send_to_devices(
                devices=devices,
                title=campaign.title,
                body=campaign.body,
                image_url=campaign.image_url,
                click_action=campaign.click_action,
                action_buttons=campaign.action_buttons,
                data_payload=campaign.data_payload,
                category=campaign.category,
                campaign_id=campaign.id,
            )

            campaign.total_sent = len(notifications)
            campaign.status = CampaignStatus.SENT
            campaign.completed_at = datetime.utcnow()

            if campaign.started_at:
                processing_ms = (campaign.completed_at - campaign.started_at).total_seconds() * 1000
                campaign.processing_time_ms = int(processing_ms)

            self.db.commit()

            logger.info(
                "Campaign sent: %s - %d notifications",
                campaign.name,
                len(notifications),
            )

            return {
                "success": True,
                "campaign_id": str(campaign.id),
                "total_targeted": campaign.total_targeted,
                "total_sent": campaign.total_sent,
            }

        except Exception as e:
            logger.error("Campaign send failed: %s", e)
            campaign.status = CampaignStatus.FAILED
            campaign.last_error = str(e)
            campaign.error_count += 1
            self.db.commit()
            raise

    def _get_campaign_targets(self, campaign: PushCampaign) -> list[PushDevice]:
        """Obtém dispositivos alvo da campanha."""
        query = self.db.query(PushDevice).filter(
            PushDevice.tenant_id == self.tenant_id,
            PushDevice.active == True,  # noqa: E712
            PushDevice.status == DeviceStatus.ACTIVE,
            PushDevice.notifications_enabled == True,  # noqa: E712
        )

        # Filtro de plataforma
        if campaign.target_platforms:
            platforms = [DevicePlatform(p) for p in campaign.target_platforms]
            query = query.filter(PushDevice.platform.in_(platforms))

        # Filtro por tipo de target
        if campaign.target_type == TargetType.USERS and campaign.target_users:
            query = query.filter(PushDevice.user_id.in_(campaign.target_users))
        elif campaign.target_type == TargetType.DEVICES and campaign.target_devices:
            query = query.filter(PushDevice.id.in_(campaign.target_devices))
        elif campaign.target_type == TargetType.TOPIC and campaign.target_topics:
            for topic in campaign.target_topics:
                query = query.filter(PushDevice.subscribed_topics.contains([topic]))

        # Limite
        if campaign.max_recipients:
            query = query.limit(campaign.max_recipients)

        return query.all()

    # ========================================================================
    # Analytics
    # ========================================================================

    def get_metrics_summary(
        self,
        start_date: datetime,
        end_date: datetime,
        platform: str | None = None,
    ) -> dict[str, Any]:
        """Obtém resumo de métricas.

        Args:
            start_date: Data inicial.
            end_date: Data final.
            platform: Plataforma (opcional).

        Returns:
            Resumo de métricas.
        """
        query = self.db.query(
            func.count(PushNotification.id).label("total_sent"),
            func.sum(func.cast(PushNotification.status == NotificationStatus.DELIVERED, Integer)).label(
                "total_delivered"
            ),
            func.sum(
                func.cast(PushNotification.opened == True, Integer)  # noqa: E712
            ).label("total_opened"),
            func.sum(
                func.cast(PushNotification.clicked == True, Integer)  # noqa: E712
            ).label("total_clicked"),
        ).filter(
            PushNotification.tenant_id == self.tenant_id,
            PushNotification.created_at >= start_date,
            PushNotification.created_at <= end_date,
        )

        if platform:
            query = query.filter(PushNotification.platform == platform)

        result = query.first()

        total_sent = result.total_sent or 0
        total_delivered = result.total_delivered or 0
        total_opened = result.total_opened or 0
        total_clicked = result.total_clicked or 0

        return {
            "total_sent": total_sent,
            "total_delivered": total_delivered,
            "total_opened": total_opened,
            "total_clicked": total_clicked,
            "delivery_rate": (total_delivered / total_sent * 100) if total_sent else 0,
            "open_rate": (total_opened / total_delivered * 100) if total_delivered else 0,
            "click_rate": (total_clicked / total_delivered * 100) if total_delivered else 0,
        }

    def record_notification_opened(
        self,
        notification_id: str,
        platform: str | None = None,
        source: str | None = None,
    ) -> bool:
        """Registra abertura de notificação.

        Args:
            notification_id: ID da notificação.
            platform: Plataforma de abertura.
            source: Fonte (notification_center, direct, etc).

        Returns:
            True se registrado.
        """
        notification = (
            self.db.query(PushNotification)
            .filter(
                PushNotification.tenant_id == self.tenant_id,
                PushNotification.notification_id == notification_id,
            )
            .first()
        )

        if notification:
            notification.update_status(NotificationStatus.OPENED)
            notification.opened_platform = platform
            notification.opened_source = source
            self.db.commit()

            # Atualiza estatísticas do dispositivo
            device = self.db.query(PushDevice).filter(PushDevice.id == notification.device_id).first()
            if device:
                device.total_notifications_opened += 1
                device.last_opened_at = datetime.utcnow()
                self.db.commit()

            # Registra ação
            action = PushNotificationAction(
                tenant_id=self.tenant_id,
                notification_id=notification.id,
                device_id=notification.device_id,
                user_id=notification.user_id,
                action_type="open",
                platform=platform,
                source=source,
            )
            self.db.add(action)
            self.db.commit()

            return True

        return False

    def record_notification_clicked(
        self,
        notification_id: str,
        action_id: str | None = None,
        url: str | None = None,
    ) -> bool:
        """Registra clique em notificação.

        Args:
            notification_id: ID da notificação.
            action_id: ID do botão clicado.
            url: URL clicada.

        Returns:
            True se registrado.
        """
        notification = (
            self.db.query(PushNotification)
            .filter(
                PushNotification.tenant_id == self.tenant_id,
                PushNotification.notification_id == notification_id,
            )
            .first()
        )

        if notification:
            notification.update_status(NotificationStatus.CLICKED)
            notification.clicked_action = action_id
            notification.clicked_url = url
            self.db.commit()

            # Atualiza estatísticas do dispositivo
            device = self.db.query(PushDevice).filter(PushDevice.id == notification.device_id).first()
            if device:
                device.total_notifications_clicked += 1
                self.db.commit()

            # Registra ação
            action = PushNotificationAction(
                tenant_id=self.tenant_id,
                notification_id=notification.id,
                device_id=notification.device_id,
                user_id=notification.user_id,
                action_type="click",
                action_id=action_id,
                action_value=url,
            )
            self.db.add(action)
            self.db.commit()

            return True

        return False


# Importação Integer para query
from sqlalchemy import Integer  # noqa: E402
