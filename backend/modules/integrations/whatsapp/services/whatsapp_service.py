"""WhatsApp Service - Servico de Integracao WhatsApp Business API.

Sprint 31 - Automacoes WhatsApp.
Responsavel por:
- Envio de mensagens via templates
- Gerenciamento de fila de mensagens
- Processamento de webhooks
- Relatorios de envio
"""

import enum
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.integrations.whatsapp.models.message_log import (
    ConversationType,
    MessageDirection,
    MessageLog,
)
from modules.integrations.whatsapp.models.message_queue import (
    MessagePriority,
    MessagePurpose,
    MessageQueue,
    MessageStatus,
    MessageType,
)
from modules.integrations.whatsapp.models.message_template import MessageTemplate
from modules.integrations.whatsapp.models.whatsapp_config import (
    WhatsAppConfig,
    WhatsAppStatus,
)


class SendResult(str, enum.Enum):
    """Resultado do envio."""

    SUCCESS = "SUCCESS"
    QUEUED = "QUEUED"
    FAILED = "FAILED"
    RATE_LIMITED = "RATE_LIMITED"
    INVALID_NUMBER = "INVALID_NUMBER"
    TEMPLATE_NOT_APPROVED = "TEMPLATE_NOT_APPROVED"
    CONFIG_NOT_CONNECTED = "CONFIG_NOT_CONNECTED"


@dataclass
class SendResponse:
    """Resposta de envio de mensagem."""

    result: SendResult
    message_id: Optional[UUID] = None
    external_id: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def is_success(self) -> bool:
        """Verifica se foi sucesso."""
        return self.result in (SendResult.SUCCESS, SendResult.QUEUED)


@dataclass
class QueueStats:
    """Estatisticas da fila."""

    total_queued: int = 0
    total_processing: int = 0
    total_sent: int = 0
    total_delivered: int = 0
    total_read: int = 0
    total_failed: int = 0
    total_cancelled: int = 0

    @property
    def total_pending(self) -> int:
        """Total pendente."""
        return self.total_queued + self.total_processing

    @property
    def total_completed(self) -> int:
        """Total completado."""
        return self.total_sent + self.total_delivered + self.total_read

    @property
    def success_rate(self) -> Decimal:
        """Taxa de sucesso."""
        total = self.total_completed + self.total_failed
        if total == 0:
            return Decimal("0")
        return (Decimal(str(self.total_completed)) / Decimal(str(total))) * 100


@dataclass
class DailyReport:
    """Relatorio diario de mensagens."""

    date: date
    tenant_id: UUID
    messages_sent: int = 0
    messages_delivered: int = 0
    messages_read: int = 0
    messages_failed: int = 0
    messages_received: int = 0
    unique_recipients: int = 0
    total_cost: Decimal = Decimal("0")

    templates_used: dict = field(default_factory=dict)
    purposes: dict = field(default_factory=dict)
    errors: dict = field(default_factory=dict)

    @property
    def delivery_rate(self) -> Decimal:
        """Taxa de entrega."""
        if self.messages_sent == 0:
            return Decimal("0")
        return (Decimal(str(self.messages_delivered)) / Decimal(str(self.messages_sent))) * 100

    @property
    def read_rate(self) -> Decimal:
        """Taxa de leitura."""
        if self.messages_delivered == 0:
            return Decimal("0")
        return (Decimal(str(self.messages_read)) / Decimal(str(self.messages_delivered))) * 100


class WhatsAppService:
    """Servico de integracao WhatsApp Business API."""

    # Constantes
    MAX_RETRIES = 3
    RETRY_DELAY_MINUTES = 5
    MESSAGE_WINDOW_HOURS = 24

    def __init__(self, session: AsyncSession):
        """Inicializa o servico.

        Args:
            session: Sessao assincrona do banco de dados.
        """
        self.session = session

    async def send_template_message(  # pylint: disable=too-many-locals,too-many-return-statements
        self,
        tenant_id: UUID,
        template_name: str,
        recipient_phone: str,
        variables: dict,
        recipient_name: Optional[str] = None,
        recipient_id: Optional[UUID] = None,
        purpose: MessagePurpose = MessagePurpose.NOTIFICATION,
        priority: MessagePriority = MessagePriority.NORMAL,
        context_type: Optional[str] = None,
        context_id: Optional[UUID] = None,
        schedule_at: Optional[datetime] = None,
    ) -> SendResponse:
        """Envia mensagem usando template.

        Args:
            tenant_id: ID do tenant.
            template_name: Nome do template.
            recipient_phone: Telefone do destinatario.
            variables: Variaveis do template.
            recipient_name: Nome do destinatario.
            recipient_id: ID do destinatario.
            purpose: Proposito da mensagem.
            priority: Prioridade.
            context_type: Tipo de contexto.
            context_id: ID do contexto.
            schedule_at: Data/hora para agendamento.

        Returns:
            SendResponse com resultado.
        """
        # Busca configuracao ativa
        config = await self._get_active_config(tenant_id)
        if not config:
            return SendResponse(
                result=SendResult.CONFIG_NOT_CONNECTED,
                error_message="Nenhuma configuracao WhatsApp ativa",
            )

        # Busca template
        template = await self._get_template_by_name(tenant_id, template_name)
        if not template:
            return SendResponse(
                result=SendResult.TEMPLATE_NOT_APPROVED,
                error_message=f"Template '{template_name}' nao encontrado",
            )

        if not template.is_approved:
            return SendResponse(
                result=SendResult.TEMPLATE_NOT_APPROVED,
                error_message=f"Template '{template_name}' nao aprovado",
            )

        # Valida telefone
        normalized_phone = self._normalize_phone(recipient_phone)
        if not normalized_phone:
            return SendResponse(
                result=SendResult.INVALID_NUMBER,
                error_message="Numero de telefone invalido",
            )

        # Verifica rate limiting
        if not config.can_send_messages:
            return SendResponse(
                result=SendResult.RATE_LIMITED,
                error_message="Limite diario de mensagens atingido",
            )

        # Renderiza conteudo
        content = template.render(variables)

        # Cria mensagem na fila
        message = MessageQueue(
            tenant_id=tenant_id,
            config_id=config.id,
            template_id=template.id,
            recipient_phone=normalized_phone,
            recipient_name=recipient_name,
            recipient_id=recipient_id,
            message_type=MessageType.TEMPLATE,
            purpose=purpose,
            content=content,
            template_variables=variables,
            priority=priority,
            context_type=context_type,
            context_id=context_id,
            scheduled_at=schedule_at,
            status=MessageStatus.QUEUED,
        )

        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)

        # Incrementa uso do template
        template.increment_use()

        # Se nao for agendada, tenta enviar imediatamente
        if not schedule_at or schedule_at <= datetime.utcnow():
            return await self._send_message_now(message, config)

        return SendResponse(
            result=SendResult.QUEUED,
            message_id=message.id,
        )

    async def send_billing_reminder(
        self,
        tenant_id: UUID,
        recipient_phone: str,
        recipient_name: str,
        amount: Decimal,
        due_date: date,
        boleto_url: Optional[str] = None,
        recipient_id: Optional[UUID] = None,
        context_id: Optional[UUID] = None,
    ) -> SendResponse:
        """Envia lembrete de cobranca.

        Args:
            tenant_id: ID do tenant.
            recipient_phone: Telefone.
            recipient_name: Nome.
            amount: Valor.
            due_date: Data de vencimento.
            boleto_url: URL do boleto.
            recipient_id: ID do cliente.
            context_id: ID do boleto/fatura.

        Returns:
            SendResponse.
        """
        variables = {
            "1": recipient_name,
            "2": f"R$ {amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "3": due_date.strftime("%d/%m/%Y"),
        }

        if boleto_url:
            variables["4"] = boleto_url

        return await self.send_template_message(
            tenant_id=tenant_id,
            template_name="billing_reminder",
            recipient_phone=recipient_phone,
            variables=variables,
            recipient_name=recipient_name,
            recipient_id=recipient_id,
            purpose=MessagePurpose.BILLING,
            priority=MessagePriority.HIGH,
            context_type="boleto",
            context_id=context_id,
        )

    async def process_queue(
        self,
        tenant_id: UUID,
        limit: int = 100,
    ) -> dict:
        """Processa fila de mensagens pendentes.

        Args:
            tenant_id: ID do tenant.
            limit: Limite de mensagens a processar.

        Returns:
            Dict com estatisticas de processamento.
        """
        now = datetime.utcnow()
        stats = {"processed": 0, "sent": 0, "failed": 0, "skipped": 0}

        # Busca mensagens pendentes
        query = (
            select(MessageQueue)
            .where(
                and_(
                    MessageQueue.tenant_id == tenant_id,
                    MessageQueue.status == MessageStatus.QUEUED,
                    (MessageQueue.scheduled_at.is_(None)) | (MessageQueue.scheduled_at <= now),
                    (MessageQueue.expires_at.is_(None)) | (MessageQueue.expires_at > now),
                )
            )
            .order_by(MessageQueue.priority.desc(), MessageQueue.created_at)
            .limit(limit)
        )

        result = await self.session.execute(query)
        messages = list(result.scalars().all())

        config = await self._get_active_config(tenant_id)
        if not config:
            return stats

        for message in messages:
            stats["processed"] += 1

            # Verifica se pode enviar
            if not config.can_send_messages:
                stats["skipped"] += 1
                continue

            # Tenta enviar
            response = await self._send_message_now(message, config)

            if response.is_success:
                stats["sent"] += 1
            else:
                stats["failed"] += 1

        return stats

    async def get_queue_stats(self, tenant_id: UUID) -> QueueStats:
        """Obtem estatisticas da fila.

        Args:
            tenant_id: ID do tenant.

        Returns:
            QueueStats.
        """
        stats = QueueStats()

        for status in MessageStatus:
            query = select(func.count(MessageQueue.id)).where(
                and_(
                    MessageQueue.tenant_id == tenant_id,
                    MessageQueue.status == status,
                )
            )
            result = await self.session.execute(query)
            count = result.scalar() or 0

            if status == MessageStatus.QUEUED:
                stats.total_queued = count
            elif status == MessageStatus.PROCESSING:
                stats.total_processing = count
            elif status == MessageStatus.SENT:
                stats.total_sent = count
            elif status == MessageStatus.DELIVERED:
                stats.total_delivered = count
            elif status == MessageStatus.READ:
                stats.total_read = count
            elif status == MessageStatus.FAILED:
                stats.total_failed = count
            elif status == MessageStatus.CANCELLED:
                stats.total_cancelled = count

        return stats

    async def get_daily_report(
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
        report = DailyReport(date=report_date, tenant_id=tenant_id)

        start = datetime.combine(report_date, datetime.min.time())
        end = datetime.combine(report_date + timedelta(days=1), datetime.min.time())

        # Mensagens enviadas
        query = select(MessageLog).where(
            and_(
                MessageLog.tenant_id == tenant_id,
                MessageLog.direction == MessageDirection.OUTBOUND,
                MessageLog.created_at >= start,
                MessageLog.created_at < end,
            )
        )
        result = await self.session.execute(query)
        outbound_messages = list(result.scalars().all())

        for msg in outbound_messages:
            report.messages_sent += 1
            if msg.is_delivered:
                report.messages_delivered += 1
            if msg.is_read:
                report.messages_read += 1
            if msg.has_error:
                report.messages_failed += 1
                error_key = msg.error_code or "unknown"
                report.errors[error_key] = report.errors.get(error_key, 0) + 1

            report.total_cost += msg.cost

            if msg.template_name:
                report.templates_used[msg.template_name] = (
                    report.templates_used.get(msg.template_name, 0) + 1
                )

        # Mensagens recebidas
        query_in = select(func.count(MessageLog.id)).where(
            and_(
                MessageLog.tenant_id == tenant_id,
                MessageLog.direction == MessageDirection.INBOUND,
                MessageLog.created_at >= start,
                MessageLog.created_at < end,
            )
        )
        result = await self.session.execute(query_in)
        report.messages_received = result.scalar() or 0

        # Destinatarios unicos
        query_recipients = select(func.count(func.distinct(MessageLog.to_phone))).where(
            and_(
                MessageLog.tenant_id == tenant_id,
                MessageLog.direction == MessageDirection.OUTBOUND,
                MessageLog.created_at >= start,
                MessageLog.created_at < end,
            )
        )
        result = await self.session.execute(query_recipients)
        report.unique_recipients = result.scalar() or 0

        return report

    async def handle_webhook(
        self,
        tenant_id: UUID,
        webhook_data: dict,
    ) -> bool:
        """Processa webhook do WhatsApp.

        Args:
            tenant_id: ID do tenant.
            webhook_data: Dados do webhook.

        Returns:
            True se processado com sucesso.
        """
        # Extrai dados do webhook (formato Meta Cloud API)
        entry = webhook_data.get("entry", [])
        if not entry:
            return False

        for ent in entry:
            changes = ent.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                await self._process_webhook_value(tenant_id, value)

        return True

    async def cancel_scheduled_messages(
        self,
        tenant_id: UUID,
        context_type: str,
        context_id: UUID,
    ) -> int:
        """Cancela mensagens agendadas por contexto.

        Args:
            tenant_id: ID do tenant.
            context_type: Tipo de contexto.
            context_id: ID do contexto.

        Returns:
            Quantidade cancelada.
        """
        query = (
            select(MessageQueue)
            .where(
                and_(
                    MessageQueue.tenant_id == tenant_id,
                    MessageQueue.context_type == context_type,
                    MessageQueue.context_id == context_id,
                    MessageQueue.status == MessageStatus.QUEUED,
                )
            )
        )
        result = await self.session.execute(query)
        messages = list(result.scalars().all())

        count = 0
        for message in messages:
            message.cancel()
            count += 1

        await self.session.commit()
        return count

    # --- Metodos privados ---

    async def _get_active_config(self, tenant_id: UUID) -> Optional[WhatsAppConfig]:
        """Busca configuracao ativa."""
        query = select(WhatsAppConfig).where(
            and_(
                WhatsAppConfig.tenant_id == tenant_id,
                WhatsAppConfig.status == WhatsAppStatus.CONNECTED,
                WhatsAppConfig.active.is_(True),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_template_by_name(
        self,
        tenant_id: UUID,
        name: str,
    ) -> Optional[MessageTemplate]:
        """Busca template por nome."""
        query = select(MessageTemplate).where(
            and_(
                MessageTemplate.tenant_id == tenant_id,
                MessageTemplate.name == name,
                MessageTemplate.active.is_(True),
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _send_message_now(  # pylint: disable=too-many-locals
        self,
        message: MessageQueue,
        config: WhatsAppConfig,
    ) -> SendResponse:
        """Envia mensagem imediatamente.

        Nota: Em producao, aqui seria a integracao real com a API do WhatsApp.
        """
        message.status = MessageStatus.PROCESSING
        await self.session.commit()

        try:
            # Simula envio para API (em producao, fazer chamada HTTP real)
            external_id = f"wamid.{message.id}"

            # Marca como enviada
            message.mark_sent(external_id)

            # Incrementa contador do config
            config.increment_message_count()

            # Cria log
            log = MessageLog.from_outbound(
                tenant_id=message.tenant_id,
                config_id=config.id,
                from_phone=config.phone_number,
                to_phone=message.recipient_phone,
                message_type=message.message_type.value.lower(),
                content=message.content,
                external_id=external_id,
                queue_id=message.id,
            )
            log.template_name = message.template.name if message.template else None
            log.template_data = message.template_variables
            log.conversation_type = ConversationType.BUSINESS_INITIATED

            self.session.add(log)
            await self.session.commit()

            return SendResponse(
                result=SendResult.SUCCESS,
                message_id=message.id,
                external_id=external_id,
            )

        except Exception as exc:  # pylint: disable=broad-except
            error_message = str(exc)
            message.mark_failed("SEND_ERROR", error_message)

            # Agenda retentativa se possivel
            if message.can_retry:
                next_retry = datetime.utcnow() + timedelta(minutes=self.RETRY_DELAY_MINUTES)
                message.schedule_retry(next_retry)

            await self.session.commit()

            return SendResponse(
                result=SendResult.FAILED,
                message_id=message.id,
                error_code="SEND_ERROR",
                error_message=error_message,
            )

    async def _process_webhook_value(
        self,
        tenant_id: UUID,
        value: dict,
    ) -> None:
        """Processa valor do webhook."""
        # Status updates
        statuses = value.get("statuses", [])
        for status in statuses:
            await self._update_message_status(tenant_id, status)

        # Incoming messages
        messages = value.get("messages", [])
        for msg in messages:
            await self._log_incoming_message(tenant_id, value, msg)

    async def _update_message_status(
        self,
        tenant_id: UUID,
        status_data: dict,
    ) -> None:
        """Atualiza status de mensagem via webhook."""
        external_id = status_data.get("id")
        status = status_data.get("status")

        if not external_id:
            return

        # Busca mensagem na fila
        query = select(MessageQueue).where(
            and_(
                MessageQueue.tenant_id == tenant_id,
                MessageQueue.external_id == external_id,
            )
        )
        result = await self.session.execute(query)
        message = result.scalar_one_or_none()

        if not message:
            return

        # Atualiza status
        if status == "delivered":
            message.mark_delivered()
        elif status == "read":
            message.mark_read()
        elif status == "failed":
            errors = status_data.get("errors", [{}])
            error = errors[0] if errors else {}
            message.mark_failed(
                error.get("code", "UNKNOWN"),
                error.get("message", "Unknown error"),
            )

        # Atualiza log
        query_log = select(MessageLog).where(
            and_(
                MessageLog.tenant_id == tenant_id,
                MessageLog.external_id == external_id,
            )
        )
        result = await self.session.execute(query_log)
        log = result.scalar_one_or_none()

        if log:
            log.status = status
            if status == "delivered":
                log.timestamp_delivered = datetime.utcnow()
            elif status == "read":
                log.timestamp_read = datetime.utcnow()

        await self.session.commit()

    async def _log_incoming_message(
        self,
        tenant_id: UUID,
        value: dict,
        msg_data: dict,
    ) -> None:
        """Registra mensagem recebida."""
        config = await self._get_active_config(tenant_id)
        if not config:
            return

        contacts = value.get("contacts", [{}])
        contact = contacts[0] if contacts else {}

        log = MessageLog.from_inbound(
            tenant_id=tenant_id,
            config_id=config.id,
            from_phone=msg_data.get("from", ""),
            to_phone=config.phone_number,
            message_type=msg_data.get("type", "text"),
            content=msg_data.get("text", {}).get("body", ""),
            external_id=msg_data.get("id", ""),
            contact_name=contact.get("profile", {}).get("name"),
            webhook_data=msg_data,
        )

        self.session.add(log)
        await self.session.commit()

    @staticmethod
    def _normalize_phone(phone: str) -> Optional[str]:
        """Normaliza numero de telefone para formato internacional."""
        if not phone:
            return None

        # Remove caracteres nao numericos
        digits = "".join(c for c in phone if c.isdigit())

        if len(digits) < 10:
            return None

        # Adiciona codigo do Brasil se necessario
        if len(digits) == 10 or len(digits) == 11:
            digits = "55" + digits

        return digits
