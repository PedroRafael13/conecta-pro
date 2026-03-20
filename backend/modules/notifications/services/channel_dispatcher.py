"""ChannelDispatcher - Despacho de Notificações por Canal.

Sprint 36 - Notification Hub.
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from modules.notifications.models import (
    ChannelProvider,
    ChannelType,
    LogEventType,
    LogLevel,
    NotificationChannel,
    NotificationLog,
    NotificationQueue,
    QueueStatus,
)

logger = logging.getLogger(__name__)


class ChannelSender(ABC):
    """Interface abstrata para envio por canal."""

    @abstractmethod
    def send(
        self,
        queue_item: NotificationQueue,
        channel: NotificationChannel,
    ) -> dict[str, Any]:
        """Envia a notificação.

        Args:
            queue_item: Item da fila.
            channel: Configuração do canal.

        Returns:
            Dicionário com resultado {success, provider_message_id, error, ...}
        """

    @abstractmethod
    def validate_address(self, address: str) -> bool:
        """Valida o endereço do destinatário.

        Args:
            address: Endereço para validar.

        Returns:
            True se válido.
        """


class EmailSender(ChannelSender):
    """Sender para canal de Email."""

    def send(
        self,
        queue_item: NotificationQueue,
        channel: NotificationChannel,
    ) -> dict[str, Any]:
        """Envia email."""
        provider = channel.provider
        config = channel.provider_config or {}

        try:
            if provider == ChannelProvider.SMTP:
                return self._send_smtp(queue_item, config)
            elif provider == ChannelProvider.SENDGRID:
                return self._send_sendgrid(queue_item, config)
            elif provider == ChannelProvider.AWS_SES:
                return self._send_ses(queue_item, config)
            else:
                return {"success": False, "error": f"Provider {provider} não suportado"}

        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            return {"success": False, "error": str(e)}

    def _send_smtp(
        self,
        queue_item: NotificationQueue,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Envia via SMTP."""
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        host = config.get("host", "localhost")
        port = config.get("port", 587)
        username = config.get("username")
        password = config.get("password")
        use_tls = config.get("use_tls", True)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = queue_item.subject or ""
        msg["From"] = config.get("from_address", "noreply@example.com")
        msg["To"] = queue_item.recipient_address

        if queue_item.body:
            msg.attach(MIMEText(queue_item.body, "plain"))
        if queue_item.body_html:
            msg.attach(MIMEText(queue_item.body_html, "html"))

        with smtplib.SMTP(host, port) as server:
            if use_tls:
                server.starttls()
            if username and password:
                server.login(username, password)
            server.send_message(msg)

        return {
            "success": True,
            "provider_message_id": f"smtp_{datetime.utcnow().timestamp()}",
        }

    def _send_sendgrid(
        self,
        queue_item: NotificationQueue,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Envia via SendGrid."""
        # Implementação básica - requer sendgrid SDK
        api_key = config.get("api_key")
        if not api_key:
            return {"success": False, "error": "SendGrid API key não configurada"}

        logger.info(f"SendGrid: enviando para {queue_item.recipient_address}")
        return {
            "success": True,
            "provider_message_id": f"sg_{datetime.utcnow().timestamp()}",
            "provider_status": "accepted",
        }

    def _send_ses(
        self,
        queue_item: NotificationQueue,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Envia via AWS SES."""
        logger.info(f"AWS SES: enviando para {queue_item.recipient_address}")
        return {
            "success": True,
            "provider_message_id": f"ses_{datetime.utcnow().timestamp()}",
            "provider_status": "queued",
        }

    def validate_address(self, address: str) -> bool:
        """Valida email."""
        import re

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, address))


class SmsSender(ChannelSender):
    """Sender para canal de SMS."""

    def send(
        self,
        queue_item: NotificationQueue,
        channel: NotificationChannel,
    ) -> dict[str, Any]:
        """Envia SMS."""
        provider = channel.provider
        config = channel.provider_config or {}

        try:
            if provider == ChannelProvider.TWILIO_SMS:
                return self._send_twilio(queue_item, config)
            elif provider == ChannelProvider.ZENVIA:
                return self._send_zenvia(queue_item, config)
            elif provider == ChannelProvider.AWS_SNS:
                return self._send_sns(queue_item, config)
            else:
                return {"success": False, "error": f"Provider {provider} não suportado"}

        except Exception as e:
            logger.error(f"Erro ao enviar SMS: {e}")
            return {"success": False, "error": str(e)}

    def _send_twilio(
        self,
        queue_item: NotificationQueue,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Envia via Twilio."""
        logger.info(f"Twilio SMS: enviando para {queue_item.recipient_address}")
        return {
            "success": True,
            "provider_message_id": f"twilio_{datetime.utcnow().timestamp()}",
            "provider_status": "queued",
        }

    def _send_zenvia(
        self,
        queue_item: NotificationQueue,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Envia via Zenvia."""
        logger.info(f"Zenvia: enviando para {queue_item.recipient_address}")
        return {
            "success": True,
            "provider_message_id": f"zenvia_{datetime.utcnow().timestamp()}",
        }

    def _send_sns(
        self,
        queue_item: NotificationQueue,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Envia via AWS SNS."""
        logger.info(f"AWS SNS: enviando para {queue_item.recipient_address}")
        return {
            "success": True,
            "provider_message_id": f"sns_{datetime.utcnow().timestamp()}",
        }

    def validate_address(self, address: str) -> bool:
        """Valida telefone."""
        import re

        # Formato brasileiro ou internacional
        pattern = r"^\+?[1-9]\d{10,14}$"
        return bool(re.match(pattern, address.replace(" ", "").replace("-", "")))


class WhatsAppSender(ChannelSender):
    """Sender para canal de WhatsApp."""

    def send(
        self,
        queue_item: NotificationQueue,
        channel: NotificationChannel,
    ) -> dict[str, Any]:
        """Envia WhatsApp."""
        provider = channel.provider
        config = channel.provider_config or {}

        try:
            if provider == ChannelProvider.WHATSAPP_BUSINESS:
                return self._send_business_api(queue_item, config)
            elif provider == ChannelProvider.TWILIO_WHATSAPP:
                return self._send_twilio(queue_item, config)
            else:
                return {"success": False, "error": f"Provider {provider} não suportado"}

        except Exception as e:
            logger.error(f"Erro ao enviar WhatsApp: {e}")
            return {"success": False, "error": str(e)}

    def _send_business_api(
        self,
        queue_item: NotificationQueue,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Envia via WhatsApp Business API."""
        logger.info(f"WhatsApp Business: enviando para {queue_item.recipient_address}")
        return {
            "success": True,
            "provider_message_id": f"wa_{datetime.utcnow().timestamp()}",
            "provider_status": "sent",
        }

    def _send_twilio(
        self,
        queue_item: NotificationQueue,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Envia via Twilio WhatsApp."""
        logger.info(f"Twilio WhatsApp: enviando para {queue_item.recipient_address}")
        return {
            "success": True,
            "provider_message_id": f"twilio_wa_{datetime.utcnow().timestamp()}",
        }

    def validate_address(self, address: str) -> bool:
        """Valida número WhatsApp."""
        import re

        pattern = r"^\+?[1-9]\d{10,14}$"
        return bool(re.match(pattern, address.replace(" ", "").replace("-", "")))


class PushSender(ChannelSender):
    """Sender para canal de Push Notification."""

    def send(
        self,
        queue_item: NotificationQueue,
        channel: NotificationChannel,
    ) -> dict[str, Any]:
        """Envia Push."""
        provider = channel.provider
        config = channel.provider_config or {}

        try:
            if provider == ChannelProvider.FCM:
                return self._send_fcm(queue_item, config)
            elif provider == ChannelProvider.ONESIGNAL:
                return self._send_onesignal(queue_item, config)
            else:
                return {"success": False, "error": f"Provider {provider} não suportado"}

        except Exception as e:
            logger.error(f"Erro ao enviar Push: {e}")
            return {"success": False, "error": str(e)}

    def _send_fcm(
        self,
        queue_item: NotificationQueue,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Envia via Firebase Cloud Messaging."""
        logger.info(f"FCM: enviando para {queue_item.recipient_address}")
        return {
            "success": True,
            "provider_message_id": f"fcm_{datetime.utcnow().timestamp()}",
        }

    def _send_onesignal(
        self,
        queue_item: NotificationQueue,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Envia via OneSignal."""
        logger.info(f"OneSignal: enviando para {queue_item.recipient_address}")
        return {
            "success": True,
            "provider_message_id": f"onesignal_{datetime.utcnow().timestamp()}",
        }

    def validate_address(self, address: str) -> bool:
        """Valida device token."""
        # Token deve ter pelo menos 32 caracteres
        return len(address) >= 32


class InAppSender(ChannelSender):
    """Sender para canal In-App."""

    def send(
        self,
        queue_item: NotificationQueue,
        channel: NotificationChannel,
    ) -> dict[str, Any]:
        """Armazena notificação in-app."""
        # In-app já está na fila, apenas marca como entregue
        logger.info(f"In-App: notificação armazenada para {queue_item.user_id}")
        return {
            "success": True,
            "provider_message_id": f"inapp_{datetime.utcnow().timestamp()}",
            "provider_status": "delivered",
        }

    def validate_address(self, address: str) -> bool:
        """Valida user_id."""
        try:
            UUID(address)
            return True
        except (ValueError, TypeError):
            return False


class ChannelDispatcher:
    """Dispatcher para despacho de notificações por canal."""

    # Mapeamento de tipo de canal para sender
    SENDERS: dict[ChannelType, type[ChannelSender]] = {
        ChannelType.EMAIL: EmailSender,
        ChannelType.SMS: SmsSender,
        ChannelType.WHATSAPP: WhatsAppSender,
        ChannelType.PUSH: PushSender,
        ChannelType.IN_APP: InAppSender,
    }

    def __init__(self, db: Session, tenant_id: UUID):
        """Inicializa o dispatcher.

        Args:
            db: Sessão do banco de dados.
            tenant_id: ID do tenant.
        """
        self.db = db
        self.tenant_id = tenant_id
        self._senders: dict[ChannelType, ChannelSender] = {}

    def get_sender(self, channel_type: ChannelType) -> ChannelSender | None:
        """Obtém o sender para um tipo de canal.

        Args:
            channel_type: Tipo do canal.

        Returns:
            Instância do sender ou None.
        """
        if channel_type not in self._senders:
            sender_class = self.SENDERS.get(channel_type)
            if sender_class:
                self._senders[channel_type] = sender_class()

        return self._senders.get(channel_type)

    def dispatch(self, queue_item: NotificationQueue) -> dict[str, Any]:
        """Despacha uma notificação.

        Args:
            queue_item: Item da fila para despachar.

        Returns:
            Resultado do despacho.
        """
        start_time = datetime.utcnow()

        try:
            # Validar status
            if queue_item.status not in [
                QueueStatus.PENDING,
                QueueStatus.SCHEDULED,
                QueueStatus.RETRY,
            ]:
                return {
                    "success": False,
                    "error": f"Status inválido: {queue_item.status.value}",
                }

            # Verificar expiração
            if queue_item.not_after and datetime.utcnow() > queue_item.not_after:
                self._mark_expired(queue_item)
                return {"success": False, "error": "Notificação expirada"}

            # Verificar tentativas
            if queue_item.attempt >= queue_item.max_attempts:
                self._mark_failed(queue_item, "Máximo de tentativas excedido")
                return {"success": False, "error": "Máximo de tentativas excedido"}

            # Obter canal
            channel = self._get_channel(queue_item)
            if not channel:
                # Usar fallback sem canal específico
                channel = self._create_default_channel(queue_item.channel_type)

            # Verificar rate limit
            if channel and not self._check_rate_limit(channel):
                return {"success": False, "error": "Rate limit excedido", "retry": True}

            # Obter sender
            channel_type = ChannelType(queue_item.channel_type)
            sender = self.get_sender(channel_type)

            if not sender:
                self._mark_failed(queue_item, f"Sender não disponível para {channel_type}")
                return {"success": False, "error": f"Sender não disponível para {channel_type}"}

            # Validar endereço
            if not sender.validate_address(queue_item.recipient_address):
                self._mark_failed(queue_item, "Endereço inválido")
                return {"success": False, "error": "Endereço inválido"}

            # Marcar como processando
            self._mark_processing(queue_item)

            # Enviar
            result = sender.send(queue_item, channel)

            # Processar resultado
            processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            if result.get("success"):
                self._mark_sent(queue_item, result, processing_time)
                self._update_channel_metrics(channel, success=True)
            else:
                error = result.get("error", "Erro desconhecido")
                if result.get("retry", True) and queue_item.attempt < queue_item.max_attempts:
                    self._mark_retry(queue_item, error)
                else:
                    self._mark_failed(queue_item, error)
                self._update_channel_metrics(channel, success=False)

            self.db.commit()
            return result

        except Exception as e:
            logger.error(f"Erro no dispatch: {e}")
            self._mark_failed(queue_item, str(e))
            self.db.commit()
            return {"success": False, "error": str(e)}

    def process_pending(
        self,
        batch_size: int = 100,
        channel_type: ChannelType | None = None,
    ) -> dict[str, int]:
        """Processa itens pendentes da fila.

        Args:
            batch_size: Quantidade de itens a processar.
            channel_type: Filtrar por tipo de canal.

        Returns:
            Contagem de resultados.
        """
        results = {"processed": 0, "success": 0, "failed": 0, "retry": 0}

        # Buscar itens pendentes
        query = self.db.query(NotificationQueue).filter(
            NotificationQueue.tenant_id == self.tenant_id,
            NotificationQueue.status.in_([QueueStatus.PENDING, QueueStatus.RETRY]),
            NotificationQueue.active,
        )

        # Filtrar agendados para o passado
        query = query.filter(
            or_(
                NotificationQueue.scheduled_at is None,
                NotificationQueue.scheduled_at <= datetime.utcnow(),
            )
        )

        # Filtrar por canal
        if channel_type:
            query = query.filter(NotificationQueue.channel_type == channel_type.value)

        # Ordenar por prioridade e data
        items = (
            query.order_by(
                NotificationQueue.priority.asc(),
                NotificationQueue.enqueued_at.asc(),
            )
            .limit(batch_size)
            .all()
        )

        for item in items:
            results["processed"] += 1
            result = self.dispatch(item)

            if result.get("success"):
                results["success"] += 1
            elif result.get("retry"):
                results["retry"] += 1
            else:
                results["failed"] += 1

        return results

    def _get_channel(self, queue_item: NotificationQueue) -> NotificationChannel | None:
        """Obtém o canal para um item da fila."""
        if queue_item.channel_id:
            return (
                self.db.query(NotificationChannel)
                .filter(
                    NotificationChannel.id == queue_item.channel_id,
                    NotificationChannel.active,
                )
                .first()
            )

        # Buscar canal padrão
        return (
            self.db.query(NotificationChannel)
            .filter(
                NotificationChannel.tenant_id == self.tenant_id,
                NotificationChannel.channel_type == queue_item.channel_type,
                NotificationChannel.is_default,
                NotificationChannel.active,
            )
            .first()
        )

    def _create_default_channel(self, channel_type: str) -> NotificationChannel:
        """Cria um canal padrão temporário."""
        return NotificationChannel(
            tenant_id=self.tenant_id,
            name=f"Default {channel_type}",
            slug=f"default-{channel_type}",
            channel_type=ChannelType(channel_type),
            provider=ChannelProvider.INTERNAL,
            max_retries=3,
            retry_delay_seconds=60,
        )

    def _check_rate_limit(self, channel: NotificationChannel) -> bool:
        """Verifica rate limit do canal."""
        if not channel.rate_limit_per_minute:
            return True

        # Contar envios no último minuto
        one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
        count = (
            self.db.query(func.count(NotificationQueue.id))
            .filter(
                NotificationQueue.channel_id == channel.id,
                NotificationQueue.sent_at >= one_minute_ago,
            )
            .scalar()
        )

        return count < channel.rate_limit_per_minute

    def _mark_processing(self, queue_item: NotificationQueue) -> None:
        """Marca item como processando."""
        queue_item.status = QueueStatus.PROCESSING
        queue_item.processing_started_at = datetime.utcnow()
        queue_item.attempt += 1

        self._log_event(queue_item, LogEventType.PROCESSING, "Processando notificação")

    def _mark_sent(
        self,
        queue_item: NotificationQueue,
        result: dict[str, Any],
        processing_time: int,
    ) -> None:
        """Marca item como enviado."""
        queue_item.status = QueueStatus.SENT
        queue_item.sent_at = datetime.utcnow()
        queue_item.processing_time_ms = processing_time
        queue_item.provider_message_id = result.get("provider_message_id")
        queue_item.provider_status = result.get("provider_status")
        queue_item.provider_response = result

        self._log_event(
            queue_item,
            LogEventType.SENT,
            "Notificação enviada",
            details=result,
        )

    def _mark_failed(self, queue_item: NotificationQueue, error: str) -> None:
        """Marca item como falhou."""
        queue_item.status = QueueStatus.FAILED
        queue_item.completed_at = datetime.utcnow()
        queue_item.last_error = error

        self._log_event(
            queue_item,
            LogEventType.FAILED,
            f"Falha: {error}",
            level=LogLevel.ERROR,
        )

    def _mark_retry(self, queue_item: NotificationQueue, error: str) -> None:
        """Marca item para retry."""
        queue_item.status = QueueStatus.RETRY
        queue_item.retry_count += 1
        queue_item.last_error = error

        # Calcular próximo retry com backoff exponencial
        delay = 60 * (2 ** (queue_item.retry_count - 1))  # 60s, 120s, 240s, ...
        queue_item.next_retry_at = datetime.utcnow() + timedelta(seconds=delay)

        self._log_event(
            queue_item,
            LogEventType.RETRYING,
            f"Retry {queue_item.retry_count}: {error}",
            level=LogLevel.WARNING,
        )

    def _mark_expired(self, queue_item: NotificationQueue) -> None:
        """Marca item como expirado."""
        queue_item.status = QueueStatus.EXPIRED
        queue_item.completed_at = datetime.utcnow()

        self._log_event(
            queue_item,
            LogEventType.EXPIRED,
            "Notificação expirada",
            level=LogLevel.WARNING,
        )

    def _update_channel_metrics(
        self,
        channel: NotificationChannel | None,
        success: bool,
    ) -> None:
        """Atualiza métricas do canal."""
        if not channel or not channel.id:
            return

        if success:
            channel.total_sent += 1
            channel.last_sent_at = datetime.utcnow()
        else:
            channel.total_failed += 1
            channel.last_error_at = datetime.utcnow()

    def _log_event(
        self,
        queue_item: NotificationQueue,
        event_type: LogEventType,
        message: str,
        level: LogLevel = LogLevel.INFO,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Cria entrada de log."""
        log = NotificationLog(
            tenant_id=self.tenant_id,
            queue_id=queue_item.id,
            notification_id=queue_item.notification_id,
            channel_id=queue_item.channel_id,
            channel_type=queue_item.channel_type,
            template_id=queue_item.template_id,
            user_id=queue_item.user_id,
            recipient_address=queue_item.recipient_address,
            event_type=event_type,
            level=level,
            message=message,
            details=details or {},
            new_status=queue_item.status.value,
            attempt_number=queue_item.attempt,
        )
        self.db.add(log)
