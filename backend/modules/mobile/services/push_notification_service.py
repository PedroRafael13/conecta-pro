"""Serviço de notificações push."""

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from modules.mobile.models.device_token import DeviceToken
from modules.mobile.models.push_notification import (
    PushNotification,
    NotificationStatus,
    NotificationType,
    NotificationPriority,
)
from modules.mobile.schemas.notification_schemas import (
    PushNotificationCreate,
    NotificationPreferences,
    NotificationStats,
    BroadcastNotificationRequest,
    BroadcastNotificationResponse,
)

logger = logging.getLogger(__name__)


class PushNotificationService:
    """
    Serviço de notificações push.

    Suporta:
    - FCM (Firebase Cloud Messaging) para Android
    - APNs (Apple Push Notification service) para iOS
    - Agendamento de notificações
    - Notificações em broadcast
    - Tracking de entrega e leitura
    """

    def __init__(
        self,
        fcm_credentials: Optional[dict] = None,
        apns_credentials: Optional[dict] = None,
        default_ttl: int = 86400,  # 24h
    ) -> None:
        """
        Inicializa o serviço.

        Args:
            fcm_credentials: Credenciais do Firebase
            apns_credentials: Credenciais do APNs
            default_ttl: TTL padrão em segundos
        """
        self.fcm_credentials = fcm_credentials
        self.apns_credentials = apns_credentials
        self.default_ttl = default_ttl

        # Clients serão inicializados sob demanda
        self._fcm_client = None
        self._apns_client = None

    async def send_notification(
        self,
        db: AsyncSession,
        notification_data: PushNotificationCreate,
    ) -> PushNotification:
        """
        Envia notificação push para um usuário.

        Args:
            db: Sessão do banco
            notification_data: Dados da notificação

        Returns:
            PushNotification criada
        """
        # Buscar tokens do usuário
        tokens_query = select(DeviceToken).where(
            DeviceToken.user_id == notification_data.user_id,
            DeviceToken.is_active == True,
            DeviceToken.push_enabled == True,
        )
        result = await db.execute(tokens_query)
        tokens = result.scalars().all()

        if not tokens:
            logger.warning(f"No active tokens for user {notification_data.user_id}")
            # Criar notificação com status failed
            notification = PushNotification(
                user_id=notification_data.user_id,
                title=notification_data.title,
                body=notification_data.body,
                notification_type=NotificationType(notification_data.notification_type),
                priority=NotificationPriority(notification_data.priority),
                data_payload=notification_data.data_payload,
                image_url=notification_data.image_url,
                action_url=notification_data.action_url,
                category=notification_data.category,
                thread_id=notification_data.thread_id,
                collapse_key=notification_data.collapse_key,
                ttl_seconds=notification_data.ttl_seconds,
                status=NotificationStatus.FAILED,
                error_message="No active device tokens",
            )
            db.add(notification)
            await db.commit()
            return notification

        # Criar notificação no banco
        notification = PushNotification(
            user_id=notification_data.user_id,
            title=notification_data.title,
            body=notification_data.body,
            notification_type=NotificationType(notification_data.notification_type),
            priority=NotificationPriority(notification_data.priority),
            data_payload=notification_data.data_payload,
            image_url=notification_data.image_url,
            action_url=notification_data.action_url,
            category=notification_data.category,
            thread_id=notification_data.thread_id,
            collapse_key=notification_data.collapse_key,
            ttl_seconds=notification_data.ttl_seconds,
            scheduled_for=notification_data.scheduled_for,
        )
        db.add(notification)
        await db.flush()

        # Verificar se é agendada
        if notification_data.scheduled_for and notification_data.scheduled_for > datetime.utcnow():
            notification.status = NotificationStatus.PENDING
            await db.commit()
            logger.info(f"Notification {notification.id} scheduled for {notification_data.scheduled_for}")
            return notification

        # Enviar para cada token
        send_results = []
        for token in tokens:
            if token.platform in notification_data.platforms:
                success = await self._send_to_device(token, notification)
                send_results.append(success)
                token.update_last_used()

        # Atualizar status
        if any(send_results):
            notification.mark_as_sent()
        else:
            notification.mark_as_failed("All delivery attempts failed")

        await db.commit()
        return notification

    async def _send_to_device(
        self,
        token: DeviceToken,
        notification: PushNotification,
    ) -> bool:
        """
        Envia notificação para um dispositivo específico.

        Args:
            token: Token do dispositivo
            notification: Notificação a enviar

        Returns:
            True se enviou com sucesso
        """
        try:
            if token.platform == "android":
                return await self._send_fcm(token, notification)
            elif token.platform == "ios":
                return await self._send_apns(token, notification)
            else:
                logger.warning(f"Unknown platform: {token.platform}")
                return False
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False

    async def _send_fcm(
        self,
        token: DeviceToken,
        notification: PushNotification,
    ) -> bool:
        """Envia via Firebase Cloud Messaging."""
        if not self.fcm_credentials:
            logger.warning("FCM credentials not configured")
            # Simular envio em desenvolvimento
            notification.external_id = f"fcm_sim_{uuid.uuid4().hex[:8]}"
            return True

        try:
            # Construir payload FCM
            payload = {
                "token": token.token,
                "notification": {
                    "title": notification.title,
                    "body": notification.body,
                },
                "data": notification.data_payload or {},
                "android": {
                    "priority": "high" if notification.priority.value in ["high", "critical"] else "normal",
                    "ttl": f"{notification.ttl_seconds}s",
                },
            }

            if notification.image_url:
                payload["notification"]["image"] = notification.image_url

            if notification.collapse_key:
                payload["android"]["collapse_key"] = notification.collapse_key

            # TODO: Implementar envio real via Firebase Admin SDK
            # response = messaging.send(message)
            # notification.external_id = response

            # Simulação
            notification.external_id = f"fcm_{uuid.uuid4().hex[:12]}"
            logger.info(f"FCM notification sent: {notification.external_id}")
            return True

        except Exception as e:
            logger.error(f"FCM send error: {e}")
            return False

    async def _send_apns(
        self,
        token: DeviceToken,
        notification: PushNotification,
    ) -> bool:
        """Envia via Apple Push Notification service."""
        if not self.apns_credentials:
            logger.warning("APNs credentials not configured")
            # Simular envio em desenvolvimento
            notification.external_id = f"apns_sim_{uuid.uuid4().hex[:8]}"
            return True

        try:
            # Construir payload APNs
            payload = {
                "aps": {
                    "alert": {
                        "title": notification.title,
                        "body": notification.body,
                    },
                    "sound": "default",
                    "badge": 1,
                },
            }

            if notification.data_payload:
                payload.update(notification.data_payload)

            if notification.category:
                payload["aps"]["category"] = notification.category

            if notification.thread_id:
                payload["aps"]["thread-id"] = notification.thread_id

            if notification.image_url:
                payload["aps"]["mutable-content"] = 1

            # TODO: Implementar envio real via aioapns ou similar
            # response = await apns_client.send_notification(...)
            # notification.external_id = response.notification_id

            # Simulação
            notification.external_id = f"apns_{uuid.uuid4().hex[:12]}"
            logger.info(f"APNs notification sent: {notification.external_id}")
            return True

        except Exception as e:
            logger.error(f"APNs send error: {e}")
            return False

    async def send_broadcast(
        self,
        db: AsyncSession,
        request: BroadcastNotificationRequest,
    ) -> BroadcastNotificationResponse:
        """
        Envia notificação em broadcast.

        Args:
            db: Sessão do banco
            request: Dados do broadcast

        Returns:
            Response com estatísticas
        """
        broadcast_id = f"broadcast_{uuid.uuid4().hex[:12]}"

        # Construir query de tokens
        query = select(DeviceToken).where(
            DeviceToken.is_active == True,
            DeviceToken.push_enabled == True,
            DeviceToken.platform.in_(request.target_platforms),
        )

        # Filtrar por usuários específicos
        if request.target_users:
            query = query.where(DeviceToken.user_id.in_(request.target_users))

        result = await db.execute(query)
        tokens = result.scalars().all()

        # Agrupar por usuário (evitar duplicatas)
        user_tokens: dict[int, list[DeviceToken]] = {}
        for token in tokens:
            if token.user_id not in user_tokens:
                user_tokens[token.user_id] = []
            user_tokens[token.user_id].append(token)

        total_recipients = len(user_tokens)
        sent_count = 0
        failed_count = 0

        # Enviar para cada usuário
        for user_id, user_token_list in user_tokens.items():
            notification_data = PushNotificationCreate(
                user_id=user_id,
                title=request.title,
                body=request.body,
                notification_type=request.notification_type,
                priority=request.priority,
                data_payload={
                    **request.data_payload,
                    "broadcast_id": broadcast_id,
                },
                scheduled_for=request.scheduled_for,
                platforms=request.target_platforms,
            )

            try:
                notification = await self.send_notification(db, notification_data)
                if notification.status != NotificationStatus.FAILED:
                    sent_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logger.error(f"Broadcast send error for user {user_id}: {e}")
                failed_count += 1

        return BroadcastNotificationResponse(
            broadcast_id=broadcast_id,
            title=request.title,
            body=request.body,
            total_recipients=total_recipients,
            sent_count=sent_count,
            failed_count=failed_count,
            scheduled_for=request.scheduled_for,
            status="sent" if sent_count > 0 else "failed",
            created_at=datetime.utcnow(),
        )

    async def mark_as_delivered(
        self,
        db: AsyncSession,
        notification_id: uuid.UUID,
    ) -> bool:
        """Marca notificação como entregue."""
        query = (
            update(PushNotification)
            .where(PushNotification.id == notification_id)
            .values(
                status=NotificationStatus.DELIVERED,
                delivered_at=datetime.utcnow(),
            )
        )
        result = await db.execute(query)
        await db.commit()
        return result.rowcount > 0

    async def mark_as_read(
        self,
        db: AsyncSession,
        notification_id: uuid.UUID,
    ) -> bool:
        """Marca notificação como lida."""
        query = (
            update(PushNotification)
            .where(PushNotification.id == notification_id)
            .values(
                status=NotificationStatus.READ,
                read_at=datetime.utcnow(),
            )
        )
        result = await db.execute(query)
        await db.commit()
        return result.rowcount > 0

    async def get_user_notifications(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        unread_only: bool = False,
    ) -> tuple[list[PushNotification], int, int]:
        """
        Obtém notificações do usuário.

        Returns:
            Tupla (notificações, total, não lidas)
        """
        # Query base
        base_query = select(PushNotification).where(
            PushNotification.user_id == user_id,
            PushNotification.status != NotificationStatus.FAILED,
        )

        if unread_only:
            base_query = base_query.where(
                PushNotification.status != NotificationStatus.READ
            )

        # Total
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Não lidas
        unread_query = select(func.count()).where(
            PushNotification.user_id == user_id,
            PushNotification.status.in_([
                NotificationStatus.SENT,
                NotificationStatus.DELIVERED,
            ]),
        )
        unread_result = await db.execute(unread_query)
        unread_count = unread_result.scalar() or 0

        # Notificações
        query = base_query.order_by(
            PushNotification.created_at.desc()
        ).offset(offset).limit(limit)

        result = await db.execute(query)
        notifications = result.scalars().all()

        return list(notifications), total, unread_count

    async def get_stats(
        self,
        db: AsyncSession,
        user_id: Optional[int] = None,
        days: int = 30,
    ) -> NotificationStats:
        """Obtém estatísticas de notificações."""
        since = datetime.utcnow() - timedelta(days=days)

        base_query = select(PushNotification).where(
            PushNotification.created_at >= since
        )

        if user_id:
            base_query = base_query.where(PushNotification.user_id == user_id)

        # Contar por status
        result = await db.execute(base_query)
        notifications = result.scalars().all()

        total_sent = sum(1 for n in notifications if n.status != NotificationStatus.PENDING)
        total_delivered = sum(1 for n in notifications if n.status in [
            NotificationStatus.DELIVERED,
            NotificationStatus.READ,
        ])
        total_read = sum(1 for n in notifications if n.status == NotificationStatus.READ)
        total_failed = sum(1 for n in notifications if n.status == NotificationStatus.FAILED)

        # Calcular taxas
        delivery_rate = (total_delivered / total_sent * 100) if total_sent > 0 else 0
        read_rate = (total_read / total_delivered * 100) if total_delivered > 0 else 0

        # Tempo médio de entrega
        delivery_times = []
        for n in notifications:
            if n.sent_at and n.delivered_at:
                diff = (n.delivered_at - n.sent_at).total_seconds() * 1000
                delivery_times.append(diff)

        avg_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else 0

        return NotificationStats(
            total_sent=total_sent,
            total_delivered=total_delivered,
            total_read=total_read,
            total_failed=total_failed,
            delivery_rate=round(delivery_rate, 2),
            read_rate=round(read_rate, 2),
            avg_delivery_time_ms=round(avg_delivery_time, 2),
        )

    async def cleanup_old_notifications(
        self,
        db: AsyncSession,
        days: int = 90,
    ) -> int:
        """Remove notificações antigas."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Deletar notificações antigas que foram lidas ou falharam
        from sqlalchemy import delete
        query = delete(PushNotification).where(
            PushNotification.created_at < cutoff,
            PushNotification.status.in_([
                NotificationStatus.READ,
                NotificationStatus.FAILED,
            ]),
        )

        result = await db.execute(query)
        await db.commit()

        deleted = result.rowcount
        logger.info(f"Cleaned up {deleted} old notifications")
        return deleted

    async def register_device_token(
        self,
        db: AsyncSession,
        user_id: int,
        token: str,
        platform: str,
        device_id: str,
        device_info: Optional[dict] = None,
    ) -> DeviceToken:
        """
        Registra token de dispositivo.

        Args:
            db: Sessão do banco
            user_id: ID do usuário
            token: Token FCM/APNs
            platform: android ou ios
            device_id: ID único do dispositivo
            device_info: Informações extras do dispositivo

        Returns:
            DeviceToken criado ou atualizado
        """
        # Verificar se token já existe
        query = select(DeviceToken).where(
            DeviceToken.token == token,
            DeviceToken.platform == platform,
        )
        result = await db.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            # Atualizar token existente
            existing.user_id = user_id
            existing.device_id = device_id
            existing.is_active = True
            existing.update_last_used()

            if device_info:
                existing.device_name = device_info.get("device_name")
                existing.device_model = device_info.get("device_model")
                existing.os_version = device_info.get("os_version")
                existing.app_version = device_info.get("app_version")
                existing.locale = device_info.get("locale")
                existing.timezone = device_info.get("timezone")

            await db.commit()
            return existing

        # Criar novo token
        device_token = DeviceToken(
            user_id=user_id,
            token=token,
            platform=platform,
            device_id=device_id,
            device_name=device_info.get("device_name") if device_info else None,
            device_model=device_info.get("device_model") if device_info else None,
            os_version=device_info.get("os_version") if device_info else None,
            app_version=device_info.get("app_version") if device_info else None,
            locale=device_info.get("locale") if device_info else None,
            timezone=device_info.get("timezone") if device_info else None,
        )

        # Desativar outros tokens do mesmo device_id para este usuário
        deactivate_query = (
            update(DeviceToken)
            .where(
                DeviceToken.user_id == user_id,
                DeviceToken.device_id == device_id,
                DeviceToken.id != device_token.id,
            )
            .values(is_active=False)
        )
        await db.execute(deactivate_query)

        db.add(device_token)
        await db.commit()
        await db.refresh(device_token)

        return device_token

    async def unregister_device_token(
        self,
        db: AsyncSession,
        token: str,
    ) -> bool:
        """Remove registro de token."""
        query = (
            update(DeviceToken)
            .where(DeviceToken.token == token)
            .values(is_active=False)
        )
        result = await db.execute(query)
        await db.commit()
        return result.rowcount > 0
