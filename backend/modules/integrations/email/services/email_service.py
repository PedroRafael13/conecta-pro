"""Email Service - Servico de Email.

Sprint 32 - Automacoes Email.
Responsavel por:
- Envio de emails
- Processamento de fila
- Tracking de eventos
- Webhooks de providers
"""

import enum
import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.integrations.email.models.email_config import EmailConfig
from modules.integrations.email.models.email_queue import (
    BounceType,
    EmailPriority,
    EmailQueue,
    EmailStatus,
)
from modules.integrations.email.models.email_subscription import EmailSubscription
from modules.integrations.email.models.email_template import EmailTemplate
from modules.integrations.email.models.email_tracking import EmailTracking, TrackingEventType


class SendResult(str, enum.Enum):
    """Resultado do envio."""

    SUCCESS = "SUCCESS"  # Enviado com sucesso
    QUEUED = "QUEUED"  # Adicionado a fila
    RATE_LIMITED = "RATE_LIMITED"  # Rate limit atingido
    INVALID_CONFIG = "INVALID_CONFIG"  # Configuracao invalida
    INVALID_RECIPIENT = "INVALID_RECIPIENT"  # Destinatario invalido
    UNSUBSCRIBED = "UNSUBSCRIBED"  # Destinatario descadastrado
    TEMPLATE_ERROR = "TEMPLATE_ERROR"  # Erro no template
    PROVIDER_ERROR = "PROVIDER_ERROR"  # Erro no provedor
    FAILED = "FAILED"  # Falha generica


@dataclass
class SendResponse:
    """Resposta de envio de email."""

    result: SendResult
    queue_id: Optional[UUID] = None
    message_id: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def success(self) -> bool:
        """Verifica se foi sucesso."""
        return self.result in (SendResult.SUCCESS, SendResult.QUEUED)


@dataclass
class QueueStats:
    """Estatisticas da fila."""

    queued: int = 0
    processing: int = 0
    sent: int = 0
    delivered: int = 0
    opened: int = 0
    clicked: int = 0
    bounced: int = 0
    failed: int = 0

    @property
    def total_pending(self) -> int:
        """Total pendente."""
        return self.queued + self.processing

    @property
    def total_completed(self) -> int:
        """Total completado."""
        return self.sent + self.delivered + self.opened + self.clicked

    @property
    def success_rate(self) -> float:
        """Taxa de sucesso."""
        total = self.total_completed + self.bounced + self.failed
        if total == 0:
            return 0.0
        return (self.total_completed / total) * 100


@dataclass
class DailyReport:
    """Relatorio diario de emails."""

    report_date: date
    total_sent: int = 0
    total_delivered: int = 0
    total_opened: int = 0
    total_clicked: int = 0
    total_bounced: int = 0
    total_unsubscribed: int = 0
    unique_opens: int = 0
    unique_clicks: int = 0

    @property
    def delivery_rate(self) -> float:
        """Taxa de entrega."""
        if not self.total_sent:
            return 0.0
        return (self.total_delivered / self.total_sent) * 100

    @property
    def open_rate(self) -> float:
        """Taxa de abertura."""
        if not self.total_delivered:
            return 0.0
        return (self.unique_opens / self.total_delivered) * 100

    @property
    def click_rate(self) -> float:
        """Taxa de clique."""
        if not self.total_delivered:
            return 0.0
        return (self.unique_clicks / self.total_delivered) * 100


@dataclass
class TrackingPixel:
    """Dados do pixel de tracking."""

    queue_id: UUID
    tenant_id: UUID
    campaign_id: Optional[UUID] = None


class EmailService:
    """Servico de Email."""

    # Regex para validacao de email
    EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )

    def __init__(self, session: AsyncSession):
        """Inicializa o servico.

        Args:
            session: Sessao assincrona do banco de dados.
        """
        self.session = session

    async def send_email(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        tenant_id: UUID,
        config_id: UUID,
        to_email: str,
        subject: str,
        html_content: str,
        to_name: Optional[str] = None,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
        template_id: Optional[UUID] = None,
        campaign_id: Optional[UUID] = None,
        variables: Optional[dict] = None,
        priority: EmailPriority = EmailPriority.NORMAL,
        scheduled_at: Optional[datetime] = None,
    ) -> SendResponse:
        """Envia ou enfileira um email.

        Args:
            tenant_id: ID do tenant.
            config_id: ID da configuracao.
            to_email: Email do destinatario.
            subject: Assunto.
            html_content: Conteudo HTML.
            to_name: Nome do destinatario.
            text_content: Conteudo texto.
            from_email: Email do remetente (override).
            from_name: Nome do remetente (override).
            reply_to: Reply-to.
            template_id: ID do template.
            campaign_id: ID da campanha.
            variables: Variaveis usadas.
            priority: Prioridade.
            scheduled_at: Agendamento.

        Returns:
            SendResponse.
        """
        # Valida email
        if not self.validate_email(to_email):
            return SendResponse(
                result=SendResult.INVALID_RECIPIENT,
                error_message="Email invalido",
            )

        # Busca config
        config = await self._get_config(config_id)
        if not config or not config.is_verified:
            return SendResponse(
                result=SendResult.INVALID_CONFIG,
                error_message="Configuracao invalida ou nao verificada",
            )

        # Verifica rate limit
        if not config.can_send:
            return SendResponse(
                result=SendResult.RATE_LIMITED,
                error_message="Rate limit atingido",
            )

        # Verifica inscricao
        subscription = await self._get_subscription(tenant_id, to_email)
        if subscription and not subscription.can_receive_email:
            return SendResponse(
                result=SendResult.UNSUBSCRIBED,
                error_message="Destinatario descadastrado",
            )

        # Cria entrada na fila
        queue_entry = EmailQueue(
            tenant_id=tenant_id,
            config_id=config_id,
            template_id=template_id,
            campaign_id=campaign_id,
            to_email=to_email,
            to_name=to_name,
            from_email=from_email or config.from_email,
            from_name=from_name or config.from_name,
            reply_to=reply_to or config.reply_to,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            variables=variables,
            priority=priority,
            scheduled_at=scheduled_at,
            status=EmailStatus.QUEUED,
        )

        self.session.add(queue_entry)
        await self.session.flush()

        # Se nao e agendado e tem alta prioridade, tenta enviar imediatamente
        if not scheduled_at and priority in (EmailPriority.HIGH, EmailPriority.URGENT):
            send_result = await self._send_immediate(queue_entry, config)
            if send_result.success:
                return send_result

        return SendResponse(
            result=SendResult.QUEUED,
            queue_id=queue_entry.id,
        )

    async def send_template(
        self,
        tenant_id: UUID,
        config_id: UUID,
        template_id: UUID,
        to_email: str,
        variables: dict,
        to_name: Optional[str] = None,
        campaign_id: Optional[UUID] = None,
        priority: EmailPriority = EmailPriority.NORMAL,
        scheduled_at: Optional[datetime] = None,
    ) -> SendResponse:
        """Envia email usando template.

        Args:
            tenant_id: ID do tenant.
            config_id: ID da configuracao.
            template_id: ID do template.
            to_email: Email do destinatario.
            variables: Variaveis para o template.
            to_name: Nome do destinatario.
            campaign_id: ID da campanha.
            priority: Prioridade.
            scheduled_at: Agendamento.

        Returns:
            SendResponse.
        """
        # Busca template
        template = await self._get_template(template_id)
        if not template or not template.is_active:
            return SendResponse(
                result=SendResult.TEMPLATE_ERROR,
                error_message="Template invalido ou inativo",
            )

        # Renderiza
        subject, html, text = template.render(variables)

        return await self.send_email(
            tenant_id=tenant_id,
            config_id=config_id,
            to_email=to_email,
            subject=subject,
            html_content=html,
            to_name=to_name,
            text_content=text,
            template_id=template_id,
            campaign_id=campaign_id,
            variables=variables,
            priority=priority,
            scheduled_at=scheduled_at,
        )

    async def process_queue(
        self,
        config_id: UUID,
        batch_size: int = 50,
    ) -> int:
        """Processa fila de emails.

        Args:
            config_id: ID da configuracao.
            batch_size: Tamanho do lote.

        Returns:
            Quantidade processada.
        """
        # Busca emails pendentes
        query = (
            select(EmailQueue)
            .where(
                and_(
                    EmailQueue.config_id == config_id,
                    EmailQueue.status == EmailStatus.QUEUED,
                    (EmailQueue.scheduled_at.is_(None))
                    | (EmailQueue.scheduled_at <= datetime.utcnow()),
                )
            )
            .order_by(EmailQueue.priority.desc(), EmailQueue.created_at.asc())
            .limit(batch_size)
        )

        result = await self.session.execute(query)
        emails = list(result.scalars().all())

        if not emails:
            return 0

        # Busca config
        config = await self._get_config(config_id)
        if not config or not config.is_verified:
            return 0

        processed = 0
        for email in emails:
            if not config.can_send:
                break  # Rate limit atingido

            email.mark_processing()
            await self._send_immediate(email, config)
            processed += 1

        return processed

    async def get_queue_stats(self, tenant_id: UUID) -> QueueStats:
        """Obtem estatisticas da fila.

        Args:
            tenant_id: ID do tenant.

        Returns:
            QueueStats.
        """
        query = (
            select(EmailQueue.status, func.count(EmailQueue.id))
            .where(EmailQueue.tenant_id == tenant_id)
            .group_by(EmailQueue.status)
        )

        result = await self.session.execute(query)
        counts = {row[0]: row[1] for row in result.all()}

        return QueueStats(
            queued=counts.get(EmailStatus.QUEUED, 0),
            processing=counts.get(EmailStatus.PROCESSING, 0),
            sent=counts.get(EmailStatus.SENT, 0),
            delivered=counts.get(EmailStatus.DELIVERED, 0),
            opened=counts.get(EmailStatus.OPENED, 0),
            clicked=counts.get(EmailStatus.CLICKED, 0),
            bounced=counts.get(EmailStatus.BOUNCED, 0),
            failed=counts.get(EmailStatus.FAILED, 0),
        )

    async def get_daily_report(  # pylint: disable=too-many-locals
        self,
        tenant_id: UUID,
        report_date: date,
    ) -> DailyReport:
        """Gera relatorio diario.

        Args:
            tenant_id: ID do tenant.
            report_date: Data do relatorio.

        Returns:
            DailyReport.
        """
        start_dt = datetime.combine(report_date, datetime.min.time())
        end_dt = datetime.combine(report_date, datetime.max.time())

        # Query para contagens de fila
        queue_query = (
            select(EmailQueue.status, func.count(EmailQueue.id))
            .where(
                and_(
                    EmailQueue.tenant_id == tenant_id,
                    EmailQueue.sent_at >= start_dt,
                    EmailQueue.sent_at <= end_dt,
                )
            )
            .group_by(EmailQueue.status)
        )

        queue_result = await self.session.execute(queue_query)
        queue_counts = {row[0]: row[1] for row in queue_result.all()}

        # Query para tracking
        tracking_query = (
            select(EmailTracking.event_type, func.count(EmailTracking.id))
            .where(
                and_(
                    EmailTracking.tenant_id == tenant_id,
                    EmailTracking.event_timestamp >= start_dt,
                    EmailTracking.event_timestamp <= end_dt,
                )
            )
            .group_by(EmailTracking.event_type)
        )

        tracking_result = await self.session.execute(tracking_query)
        tracking_counts = {row[0]: row[1] for row in tracking_result.all()}

        # Unique opens e clicks
        unique_opens_query = (
            select(func.count(func.distinct(EmailTracking.queue_id)))
            .where(
                and_(
                    EmailTracking.tenant_id == tenant_id,
                    EmailTracking.event_type == TrackingEventType.OPENED,
                    EmailTracking.event_timestamp >= start_dt,
                    EmailTracking.event_timestamp <= end_dt,
                )
            )
        )
        unique_opens_result = await self.session.execute(unique_opens_query)
        unique_opens = unique_opens_result.scalar() or 0

        unique_clicks_query = (
            select(func.count(func.distinct(EmailTracking.queue_id)))
            .where(
                and_(
                    EmailTracking.tenant_id == tenant_id,
                    EmailTracking.event_type == TrackingEventType.CLICKED,
                    EmailTracking.event_timestamp >= start_dt,
                    EmailTracking.event_timestamp <= end_dt,
                )
            )
        )
        unique_clicks_result = await self.session.execute(unique_clicks_query)
        unique_clicks = unique_clicks_result.scalar() or 0

        total_sent = sum(queue_counts.values())

        return DailyReport(
            report_date=report_date,
            total_sent=total_sent,
            total_delivered=queue_counts.get(EmailStatus.DELIVERED, 0),
            total_opened=tracking_counts.get(TrackingEventType.OPENED, 0),
            total_clicked=tracking_counts.get(TrackingEventType.CLICKED, 0),
            total_bounced=queue_counts.get(EmailStatus.BOUNCED, 0),
            total_unsubscribed=tracking_counts.get(TrackingEventType.UNSUBSCRIBED, 0),
            unique_opens=unique_opens,
            unique_clicks=unique_clicks,
        )

    async def track_open(
        self,
        queue_id: UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> bool:
        """Registra abertura de email.

        Args:
            queue_id: ID do email na fila.
            ip_address: IP do cliente.
            user_agent: User agent.

        Returns:
            True se registrado.
        """
        email = await self._get_queue_entry(queue_id)
        if not email:
            return False

        # Atualiza status
        email.mark_opened()

        # Cria evento de tracking
        tracking = EmailTracking.from_open(
            tenant_id=email.tenant_id,
            queue_id=queue_id,
            recipient_email=email.to_email,
            ip_address=ip_address,
            user_agent=user_agent,
            campaign_id=email.campaign_id,
        )
        tracking.parse_user_agent()

        self.session.add(tracking)
        return True

    async def track_click(
        self,
        queue_id: UUID,
        clicked_url: str,
        link_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> bool:
        """Registra clique em link.

        Args:
            queue_id: ID do email na fila.
            clicked_url: URL clicada.
            link_id: ID do link.
            ip_address: IP do cliente.
            user_agent: User agent.

        Returns:
            True se registrado.
        """
        email = await self._get_queue_entry(queue_id)
        if not email:
            return False

        # Atualiza status
        email.mark_clicked()

        # Cria evento de tracking
        tracking = EmailTracking.from_click(
            tenant_id=email.tenant_id,
            queue_id=queue_id,
            recipient_email=email.to_email,
            clicked_url=clicked_url,
            link_id=link_id,
            ip_address=ip_address,
            user_agent=user_agent,
            campaign_id=email.campaign_id,
        )
        tracking.parse_user_agent()

        self.session.add(tracking)
        return True

    async def handle_webhook(
        self,
        provider: str,
        payload: dict,
    ) -> bool:
        """Processa webhook de provedor.

        Args:
            provider: Nome do provedor.
            payload: Dados do webhook.

        Returns:
            True se processado.
        """
        # Extrai message_id do payload baseado no provedor
        message_id = self._extract_message_id(provider, payload)
        if not message_id:
            return False

        # Busca email pelo message_id
        email = await self._get_by_message_id(message_id)
        if not email:
            return False

        # Extrai evento
        event_type = self._extract_event_type(provider, payload)
        if not event_type:
            return False

        # Processa evento
        if event_type == "delivered":
            email.mark_delivered()
        elif event_type == "opened":
            await self.track_open(email.id)
        elif event_type == "clicked":
            url = payload.get("url", "")
            await self.track_click(email.id, url)
        elif event_type == "bounced":
            bounce_type = BounceType.HARD if payload.get("hard") else BounceType.SOFT
            email.mark_bounced(bounce_type, payload.get("reason"))
        elif event_type == "complained":
            email.mark_bounced(BounceType.COMPLAINT, "Marcado como spam")
        elif event_type == "unsubscribed":
            await self._unsubscribe_recipient(email.tenant_id, email.to_email)

        return True

    async def unsubscribe(
        self,
        tenant_id: UUID,
        email: str,
        token: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> bool:
        """Descadastra email.

        Args:
            tenant_id: ID do tenant.
            email: Email a descadastrar.
            token: Token de descadastro.
            reason: Motivo.

        Returns:
            True se descadastrado.
        """
        subscription = await self._get_subscription(tenant_id, email)
        if not subscription:
            return False

        # Verifica token se fornecido
        if token and subscription.unsubscribe_token != token:
            return False

        subscription.unsubscribe(reason)
        return True

    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de email.

        Args:
            email: Email a validar.

        Returns:
            True se valido.
        """
        if not email:
            return False
        return bool(EmailService.EMAIL_REGEX.match(email))

    # --- Metodos privados ---

    async def _get_config(self, config_id: UUID) -> Optional[EmailConfig]:
        """Busca configuracao."""
        query = select(EmailConfig).where(EmailConfig.id == config_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_template(self, template_id: UUID) -> Optional[EmailTemplate]:
        """Busca template."""
        query = select(EmailTemplate).where(EmailTemplate.id == template_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_queue_entry(self, queue_id: UUID) -> Optional[EmailQueue]:
        """Busca entrada na fila."""
        query = select(EmailQueue).where(EmailQueue.id == queue_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_by_message_id(self, message_id: str) -> Optional[EmailQueue]:
        """Busca por message_id do provedor."""
        query = select(EmailQueue).where(EmailQueue.provider_message_id == message_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_subscription(
        self,
        tenant_id: UUID,
        email: str,
    ) -> Optional[EmailSubscription]:
        """Busca inscricao."""
        email_hash = EmailSubscription.hash_email(email)
        query = select(EmailSubscription).where(
            and_(
                EmailSubscription.tenant_id == tenant_id,
                EmailSubscription.email_hash == email_hash,
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _send_immediate(
        self,
        email: EmailQueue,
        config: EmailConfig,
    ) -> SendResponse:
        """Envia email imediatamente (placeholder).

        Args:
            email: Email a enviar.
            config: Configuracao.

        Returns:
            SendResponse.
        """
        # Integracao real com providers sera implementada por provider
        # Por enquanto, simula envio
        message_id = f"sim_{email.id}"
        email.mark_sent(message_id)
        config.increment_sent()

        return SendResponse(
            result=SendResult.SUCCESS,
            queue_id=email.id,
            message_id=message_id,
        )

    async def _unsubscribe_recipient(self, tenant_id: UUID, email: str) -> None:
        """Descadastra destinatario internamente."""
        subscription = await self._get_subscription(tenant_id, email)
        if subscription:
            subscription.unsubscribe("Via webhook")

    @staticmethod
    def _extract_message_id(provider: str, payload: dict) -> Optional[str]:
        """Extrai message_id do payload de webhook."""
        if provider == "sendgrid":
            return payload.get("sg_message_id")
        if provider == "mailgun":
            return payload.get("message-id")
        if provider == "aws_ses":
            return payload.get("mail", {}).get("messageId")
        return payload.get("message_id")

    @staticmethod
    def _extract_event_type(provider: str, payload: dict) -> Optional[str]:
        """Extrai tipo de evento do payload de webhook."""
        event_map = {
            "delivered": "delivered",
            "delivery": "delivered",
            "open": "opened",
            "opened": "opened",
            "click": "clicked",
            "clicked": "clicked",
            "bounce": "bounced",
            "bounced": "bounced",
            "complaint": "complained",
            "spamreport": "complained",
            "unsubscribe": "unsubscribed",
            "unsubscribed": "unsubscribed",
        }

        if provider == "sendgrid":
            event = payload.get("event", "").lower()
        elif provider == "mailgun":
            event = payload.get("event", "").lower()
        elif provider == "aws_ses":
            event = payload.get("eventType", "").lower()
        else:
            event = payload.get("event", "").lower()

        return event_map.get(event)
