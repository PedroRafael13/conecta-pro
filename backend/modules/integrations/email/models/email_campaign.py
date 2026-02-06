"""Email Campaign Model - Campanhas de Email.

Sprint 32 - Automacoes Email.
"""

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class CampaignType(str, enum.Enum):
    """Tipo de campanha."""

    REGULAR = "REGULAR"  # Campanha unica
    AUTOMATED = "AUTOMATED"  # Automatizada por trigger
    DRIP = "DRIP"  # Sequencia (drip campaign)
    AB_TEST = "AB_TEST"  # Teste A/B
    TRANSACTIONAL = "TRANSACTIONAL"  # Transacional


class CampaignStatus(str, enum.Enum):
    """Status da campanha."""

    DRAFT = "DRAFT"  # Rascunho
    SCHEDULED = "SCHEDULED"  # Agendada
    SENDING = "SENDING"  # Enviando
    SENT = "SENT"  # Enviada
    PAUSED = "PAUSED"  # Pausada
    CANCELLED = "CANCELLED"  # Cancelada
    COMPLETED = "COMPLETED"  # Concluida


class TriggerType(str, enum.Enum):
    """Tipo de trigger para campanhas automatizadas."""

    SIGNUP = "SIGNUP"  # Novo cadastro
    PURCHASE = "PURCHASE"  # Compra realizada
    ABANDONED_CART = "ABANDONED_CART"  # Carrinho abandonado
    BIRTHDAY = "BIRTHDAY"  # Aniversario
    INACTIVITY = "INACTIVITY"  # Inatividade
    CUSTOM_EVENT = "CUSTOM_EVENT"  # Evento customizado
    DATE_FIELD = "DATE_FIELD"  # Campo de data
    SEGMENT_ENTRY = "SEGMENT_ENTRY"  # Entrada em segmento


class EmailCampaign(Base):
    """Campanha de email marketing."""

    __tablename__ = "email_campaigns"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Relacionamento com Config
    config_id = Column(
        UUID(as_uuid=True),
        ForeignKey("email_configs.id"),
        nullable=False,
        index=True,
    )

    # Relacionamento com Template
    template_id = Column(
        UUID(as_uuid=True),
        ForeignKey("email_templates.id"),
        nullable=True,
        index=True,
    )

    # Identificacao
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Tipo e Status
    campaign_type = Column(
        Enum(CampaignType, name="campaigntype", create_type=True),
        nullable=False,
        default=CampaignType.REGULAR,
    )
    status = Column(
        Enum(CampaignStatus, name="campaignstatus", create_type=True),
        nullable=False,
        default=CampaignStatus.DRAFT,
    )

    # Remetente (override do config)
    from_email = Column(String(255), nullable=True)
    from_name = Column(String(100), nullable=True)
    reply_to = Column(String(255), nullable=True)

    # Assunto (override do template)
    subject = Column(String(255), nullable=True)
    preheader = Column(String(255), nullable=True)

    # Segmentacao
    # Ex: {"field": "status", "operator": "eq", "value": "active"}
    segment_filters = Column(JSONB, nullable=True)
    recipient_list_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    exclude_list_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)

    # Agendamento
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    timezone = Column(String(50), default="America/Sao_Paulo", nullable=False)
    send_optimal_time = Column(Boolean, default=False, nullable=False)

    # Automacao
    trigger_type = Column(
        Enum(TriggerType, name="triggertype", create_type=True),
        nullable=True,
    )
    trigger_config = Column(JSONB, nullable=True)  # Configuracao do trigger
    trigger_delay_minutes = Column(Integer, default=0, nullable=True)

    # Drip Campaign
    is_drip_step = Column(Boolean, default=False, nullable=False)
    drip_parent_id = Column(UUID(as_uuid=True), nullable=True)
    drip_step_number = Column(Integer, nullable=True)
    drip_delay_days = Column(Integer, nullable=True)
    drip_delay_hours = Column(Integer, nullable=True)
    drip_condition = Column(JSONB, nullable=True)  # Condicao para proximo passo

    # A/B Testing
    is_ab_test = Column(Boolean, default=False, nullable=False)
    ab_variants = Column(JSONB, nullable=True)  # Lista de variantes
    ab_test_size = Column(Integer, default=20, nullable=True)  # % para teste
    ab_winner_criteria = Column(String(50), default="open_rate", nullable=True)
    ab_winner_wait_hours = Column(Integer, default=4, nullable=True)
    ab_winner_id = Column(UUID(as_uuid=True), nullable=True)

    # Metricas
    total_recipients = Column(Integer, default=0, nullable=False)
    total_sent = Column(Integer, default=0, nullable=False)
    total_delivered = Column(Integer, default=0, nullable=False)
    total_opened = Column(Integer, default=0, nullable=False)
    total_clicked = Column(Integer, default=0, nullable=False)
    total_bounced = Column(Integer, default=0, nullable=False)
    total_unsubscribed = Column(Integer, default=0, nullable=False)
    total_complained = Column(Integer, default=0, nullable=False)

    # Metricas financeiras (para campanhas de marketing)
    total_revenue = Column(Numeric(15, 2), default=Decimal("0.00"), nullable=True)
    total_conversions = Column(Integer, default=0, nullable=True)

    # Tags
    tags = Column(ARRAY(String), nullable=True)

    # Flags
    active = Column(Boolean, default=True, nullable=False)
    track_opens = Column(Boolean, default=True, nullable=False)
    track_clicks = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    config = relationship("EmailConfig", lazy="joined")
    template = relationship("EmailTemplate", lazy="joined")

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<EmailCampaign {self.name} ({self.status.value})>"

    @property
    def is_scheduled(self) -> bool:
        """Verifica se esta agendada."""
        return self.status == CampaignStatus.SCHEDULED and self.scheduled_at is not None

    @property
    def is_sending(self) -> bool:
        """Verifica se esta enviando."""
        return self.status == CampaignStatus.SENDING

    @property
    def is_completed(self) -> bool:
        """Verifica se esta concluida."""
        return self.status in (CampaignStatus.SENT, CampaignStatus.COMPLETED)

    @property
    def open_rate(self) -> float:
        """Calcula taxa de abertura."""
        if not self.total_delivered:
            return 0.0
        return ((self.total_opened or 0) / self.total_delivered) * 100

    @property
    def click_rate(self) -> float:
        """Calcula taxa de cliques."""
        if not self.total_delivered:
            return 0.0
        return ((self.total_clicked or 0) / self.total_delivered) * 100

    @property
    def bounce_rate(self) -> float:
        """Calcula taxa de bounce."""
        if not self.total_sent:
            return 0.0
        return ((self.total_bounced or 0) / self.total_sent) * 100

    @property
    def unsubscribe_rate(self) -> float:
        """Calcula taxa de descadastro."""
        if not self.total_delivered:
            return 0.0
        return ((self.total_unsubscribed or 0) / self.total_delivered) * 100

    @property
    def delivery_rate(self) -> float:
        """Calcula taxa de entrega."""
        if not self.total_sent:
            return 0.0
        return ((self.total_delivered or 0) / self.total_sent) * 100

    @property
    def click_to_open_rate(self) -> float:
        """Calcula taxa de clique por abertura (CTOR)."""
        if not self.total_opened:
            return 0.0
        return ((self.total_clicked or 0) / self.total_opened) * 100

    def start_sending(self) -> None:
        """Inicia envio da campanha."""
        self.status = CampaignStatus.SENDING
        self.started_at = datetime.utcnow()

    def complete(self) -> None:
        """Marca campanha como concluida."""
        self.status = CampaignStatus.COMPLETED
        self.completed_at = datetime.utcnow()

    def pause(self) -> None:
        """Pausa a campanha."""
        if self.status == CampaignStatus.SENDING:
            self.status = CampaignStatus.PAUSED

    def resume(self) -> None:
        """Retoma a campanha."""
        if self.status == CampaignStatus.PAUSED:
            self.status = CampaignStatus.SENDING

    def cancel(self) -> None:
        """Cancela a campanha."""
        if self.status in (CampaignStatus.DRAFT, CampaignStatus.SCHEDULED):
            self.status = CampaignStatus.CANCELLED

    def schedule(self, send_at: datetime) -> None:
        """Agenda a campanha.

        Args:
            send_at: Data/hora de envio.
        """
        self.scheduled_at = send_at
        self.status = CampaignStatus.SCHEDULED

    def increment_metrics(
        self,
        sent: int = 0,
        delivered: int = 0,
        opened: int = 0,
        clicked: int = 0,
        bounced: int = 0,
        unsubscribed: int = 0,
    ) -> None:
        """Incrementa metricas da campanha.

        Args:
            sent: Emails enviados.
            delivered: Emails entregues.
            opened: Emails abertos.
            clicked: Links clicados.
            bounced: Emails retornados.
            unsubscribed: Descadastros.
        """
        self.total_sent = (self.total_sent or 0) + sent
        self.total_delivered = (self.total_delivered or 0) + delivered
        self.total_opened = (self.total_opened or 0) + opened
        self.total_clicked = (self.total_clicked or 0) + clicked
        self.total_bounced = (self.total_bounced or 0) + bounced
        self.total_unsubscribed = (self.total_unsubscribed or 0) + unsubscribed
