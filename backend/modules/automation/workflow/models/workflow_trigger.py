"""Workflow Trigger Model - Gatilhos de Workflow.

Sprint 33 - Workflow Engine (Unificado).
"""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class TriggerType(StrEnum):
    """Tipo de trigger."""

    # Tipos genericos
    EVENT = "EVENT"  # Evento do sistema
    SCHEDULE = "SCHEDULE"  # Agendamento (cron)
    WEBHOOK = "WEBHOOK"  # Chamada externa
    MANUAL = "MANUAL"  # Execucao manual
    DATA_CHANGE = "DATA_CHANGE"  # Mudanca em dados
    CONDITION = "CONDITION"  # Condicao satisfeita
    API = "API"  # Chamada via API

    # Eventos de entidade
    ENTITY_CREATED = "ENTITY_CREATED"  # Registro criado
    ENTITY_UPDATED = "ENTITY_UPDATED"  # Registro atualizado
    ENTITY_DELETED = "ENTITY_DELETED"  # Registro deletado
    ENTITY_STATUS_CHANGED = "ENTITY_STATUS_CHANGED"  # Status alterado

    # Eventos de tempo
    DATE_FIELD = "DATE_FIELD"  # Campo de data
    DELAY_AFTER = "DELAY_AFTER"  # Apos X tempo de evento

    # Eventos de usuario
    USER_ACTION = "USER_ACTION"  # Acao de usuario
    FORM_SUBMIT = "FORM_SUBMIT"  # Submissao de formulario

    # Eventos de integracao
    WEBHOOK_RECEIVED = "WEBHOOK_RECEIVED"  # Webhook recebido
    API_CALL = "API_CALL"  # Chamada de API

    # Eventos especificos
    LEAD_SCORED = "LEAD_SCORED"  # Lead pontuado
    PAYMENT_RECEIVED = "PAYMENT_RECEIVED"  # Pagamento recebido
    CONTRACT_SIGNED = "CONTRACT_SIGNED"  # Contrato assinado
    INVOICE_OVERDUE = "INVOICE_OVERDUE"  # Fatura vencida


class TriggerEvent(StrEnum):
    """Eventos do sistema."""

    # Documentos
    DOCUMENT_UPLOADED = "document.uploaded"
    DOCUMENT_PROCESSED = "document.processed"
    DOCUMENT_APPROVED = "document.approved"
    DOCUMENT_REJECTED = "document.rejected"

    # Financeiro
    PAYMENT_RECEIVED = "payment.received"
    PAYMENT_OVERDUE = "payment.overdue"
    INVOICE_CREATED = "invoice.created"
    INVOICE_SENT = "invoice.sent"

    # Comunicacao
    MESSAGE_RECEIVED = "message.received"
    EMAIL_RECEIVED = "email.received"
    NOTIFICATION_SENT = "notification.sent"

    # Usuarios
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_LOGIN = "user.login"

    # CRM
    LEAD_CREATED = "lead.created"
    LEAD_UPDATED = "lead.updated"
    LEAD_CONVERTED = "lead.converted"
    OPPORTUNITY_CREATED = "opportunity.created"
    OPPORTUNITY_WON = "opportunity.won"
    OPPORTUNITY_LOST = "opportunity.lost"

    # Manutencao
    TICKET_CREATED = "ticket.created"
    TICKET_UPDATED = "ticket.updated"
    TICKET_RESOLVED = "ticket.resolved"

    # Alertas
    ALERT_TRIGGERED = "alert.triggered"
    ANOMALY_DETECTED = "anomaly.detected"
    THRESHOLD_EXCEEDED = "threshold.exceeded"

    # Sistema
    SYSTEM_ERROR = "system.error"
    BACKUP_COMPLETED = "backup.completed"
    INTEGRATION_SYNC = "integration.sync"

    # Custom
    CUSTOM = "custom"


class TriggerStatus(StrEnum):
    """Status do trigger."""

    ACTIVE = "ACTIVE"  # Ativo
    INACTIVE = "INACTIVE"  # Inativo
    PAUSED = "PAUSED"  # Pausado
    ERROR = "ERROR"  # Em erro


class WorkflowTrigger(Base):
    """Gatilho que inicia um workflow."""

    __tablename__ = "workflow_triggers"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Relacionamento com Workflow
    workflow_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Identificacao
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Tipo e Status
    trigger_type = Column(
        Enum(TriggerType, name="triggertype_wf", create_type=True),
        nullable=False,
    )
    status = Column(
        Enum(TriggerStatus, name="triggerstatus", create_type=True),
        nullable=False,
        default=TriggerStatus.ACTIVE,
    )

    # Evento (para tipo EVENT)
    event = Column(
        Enum(TriggerEvent, name="triggerevent", create_type=True),
        nullable=True,
    )
    custom_event = Column(String(100), nullable=True)  # Para eventos customizados

    # Configuracao do trigger
    # Ex para ENTITY_CREATED: {"entity": "Lead", "filters": {"source": "WEBSITE"}}
    # Ex para SCHEDULE: {"cron": "0 9 * * 1", "timezone": "America/Sao_Paulo"}
    # Ex para DATE_FIELD: {"entity": "Contract", "field": "end_date", "days_before": 30}
    config = Column(JSONB, nullable=False, default=dict)

    # Configuracoes especificas por tipo
    # Ex: {"frequency": "daily", "time_of_day": "09:00", "timezone": "America/Sao_Paulo"}
    schedule_config = Column(JSONB, nullable=True)
    # Ex: {"secret_key": "...", "allowed_ips": [...], "validate_signature": true}
    webhook_config = Column(JSONB, nullable=True)
    # Ex: {"entity_type": "Lead", "fields": ["status"], "operations": ["update"]}
    data_change_config = Column(JSONB, nullable=True)

    # Filtros adicionais
    # Ex: {"field": "value", "operator": ">=", "value": 1000}
    filters = Column(JSONB, nullable=True)
    filter_expression = Column(Text, nullable=True)  # Expressao de filtro

    # Input
    input_schema = Column(JSONB, nullable=True)
    input_mapping = Column(JSONB, nullable=True)

    # Limite de execucoes
    max_executions = Column(Integer, nullable=True)  # None = ilimitado
    current_executions = Column(Integer, default=0, nullable=False)
    trigger_count = Column(Integer, default=0, nullable=False)  # Alias para current_executions

    # Cooldown entre execucoes (para evitar spam)
    cooldown_seconds = Column(Integer, default=0, nullable=True)

    # Concorrencia
    max_concurrent = Column(Integer, default=1, nullable=False)

    # Prioridade (para triggers concorrentes)
    priority = Column(Integer, default=0, nullable=False)

    # Flags
    active = Column(Boolean, default=True, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    once_per_entity = Column(Boolean, default=False, nullable=False)

    # Metadados
    extra_metadata = Column("metadata", JSONB, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    next_scheduled_at = Column(DateTime(timezone=True), nullable=True)

    # Error tracking
    last_error = Column(Text, nullable=True)
    error_count = Column(Integer, default=0, nullable=False)

    # Relationships
    workflow = relationship("Workflow", back_populates="triggers")

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<WorkflowTrigger {self.name} ({self.trigger_type.value})>"

    @property
    def is_active(self) -> bool:
        """Verifica se esta ativo."""
        return self.status == TriggerStatus.ACTIVE and self.active and self.is_enabled

    @property
    def can_trigger(self) -> bool:
        """Verifica se pode disparar."""
        if not self.is_active:
            return False

        if self.cooldown_seconds and self.cooldown_seconds > 0 and self.last_triggered_at:
            elapsed = (datetime.utcnow() - self.last_triggered_at).total_seconds()
            if elapsed < self.cooldown_seconds:
                return False

        if self.has_reached_limit:
            return False

        return True

    @property
    def webhook_url(self) -> str:
        """URL para webhook."""
        if self.trigger_type in (TriggerType.WEBHOOK, TriggerType.WEBHOOK_RECEIVED):
            return f"/api/v1/workflows/webhook/{self.id}"
        return ""

    @property
    def is_scheduled(self) -> bool:
        """Verifica se e agendado."""
        return self.trigger_type in (
            TriggerType.SCHEDULE,
            TriggerType.DATE_FIELD,
            TriggerType.DELAY_AFTER,
        )

    @property
    def is_event_based(self) -> bool:
        """Verifica se e baseado em evento."""
        return self.trigger_type.value.startswith("ENTITY_")

    @property
    def has_reached_limit(self) -> bool:
        """Verifica se atingiu limite de execucoes."""
        if self.max_executions is None:
            return False
        return self.current_executions >= self.max_executions

    @property
    def entity_type(self) -> str | None:
        """Retorna tipo de entidade do trigger."""
        if self.config:
            return self.config.get("entity")
        return None

    @property
    def cron_expression(self) -> str | None:
        """Retorna expressao cron."""
        if self.config and self.trigger_type == TriggerType.SCHEDULE:
            return self.config.get("cron")
        return None

    def activate(self) -> None:
        """Ativa o trigger."""
        self.status = TriggerStatus.ACTIVE
        self.active = True

    def deactivate(self) -> None:
        """Desativa o trigger."""
        self.status = TriggerStatus.INACTIVE
        self.active = False

    def pause(self) -> None:
        """Pausa o trigger."""
        self.status = TriggerStatus.PAUSED

    def resume(self) -> None:
        """Retoma o trigger."""
        if self.status == TriggerStatus.PAUSED:
            self.status = TriggerStatus.ACTIVE

    def record_triggered(self) -> None:
        """Registra que foi disparado."""
        self.current_executions = (self.current_executions or 0) + 1
        self.trigger_count = self.current_executions
        self.last_triggered_at = datetime.utcnow()
        self.error_count = 0
        self.last_error = None

    def matches_event(self, event_name: str, event_data: dict | None = None) -> bool:
        """Verifica se evento corresponde ao trigger.

        Args:
            event_name: Nome do evento.
            event_data: Dados do evento.

        Returns:
            True se corresponde.
        """
        if self.trigger_type not in (
            TriggerType.EVENT,
            TriggerType.ENTITY_CREATED,
            TriggerType.ENTITY_UPDATED,
            TriggerType.ENTITY_DELETED,
        ):
            return False

        # Verifica nome do evento
        if self.event:
            if event_name != self.event.value:
                return False
        elif self.custom_event:
            if event_name != self.custom_event:
                return False
        else:
            return False

        # Verifica filtros
        if event_data and self.filters:
            for key, value in self.filters.items() if isinstance(self.filters, dict) else []:
                if event_data.get(key) != value:
                    return False

        return True

    def validate_webhook(self, headers: dict, remote_ip: str = "") -> bool:
        """Valida requisicao de webhook.

        Args:
            headers: Headers da requisicao.
            remote_ip: IP remoto.

        Returns:
            True se valido.
        """
        if not self.webhook_config:
            return True

        config = self.webhook_config

        # Verifica IP
        allowed_ips = config.get("allowed_ips", [])
        if allowed_ips and remote_ip:
            if remote_ip not in allowed_ips:
                return False

        # Verifica headers obrigatorios
        required_headers = config.get("required_headers", {})
        for key, value in required_headers.items():
            if headers.get(key) != value:
                return False

        return True

    def record_error(self, error_message: str) -> None:
        """Registra erro.

        Args:
            error_message: Mensagem de erro.
        """
        self.error_count = (self.error_count or 0) + 1
        self.last_error = error_message

        # Desativa apos muitos erros
        if self.error_count >= 5:
            self.status = TriggerStatus.ERROR

    def matches_entity(self, entity_type: str, entity_data: dict) -> bool:
        """Verifica se entidade corresponde ao trigger.

        Args:
            entity_type: Tipo da entidade.
            entity_data: Dados da entidade.

        Returns:
            True se corresponde.
        """
        # Verifica tipo de entidade
        if self.entity_type and self.entity_type != entity_type:
            return False

        # Verifica filtros
        if self.filters:
            for filter_config in self.filters if isinstance(self.filters, list) else [self.filters]:
                field = filter_config.get("field")
                operator = filter_config.get("operator", "==")
                value = filter_config.get("value")

                if field and field in entity_data:
                    entity_value = entity_data[field]

                    if not self._evaluate_condition(entity_value, operator, value):
                        return False

        return True

    def _evaluate_condition(
        self,
        entity_value: any,
        operator: str,
        expected_value: any,
    ) -> bool:
        """Avalia condicao.

        Args:
            entity_value: Valor da entidade.
            operator: Operador.
            expected_value: Valor esperado.

        Returns:
            Resultado da avaliacao.
        """
        operators = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">": lambda a, b: a > b,
            ">=": lambda a, b: a >= b,
            "<": lambda a, b: a < b,
            "<=": lambda a, b: a <= b,
            "in": lambda a, b: a in b,
            "not_in": lambda a, b: a not in b,
            "contains": lambda a, b: b in a if isinstance(a, str) else False,
            "starts_with": lambda a, b: a.startswith(b) if isinstance(a, str) else False,
            "ends_with": lambda a, b: a.endswith(b) if isinstance(a, str) else False,
        }

        op_func = operators.get(operator)
        if op_func:
            try:
                return op_func(entity_value, expected_value)
            except (TypeError, ValueError):
                return False

        return False
