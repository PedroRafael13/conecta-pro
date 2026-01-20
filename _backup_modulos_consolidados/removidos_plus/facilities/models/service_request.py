"""
Modelo ServiceRequest (Solicitação de Serviço) para Facilities.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base
from modules.facilities.models.maintenance import Maintenance

if TYPE_CHECKING:
    from .area import Area


class ServiceRequestStatus(str, Enum):
    """Status da solicitação de serviço."""

    OPEN = "open"  # Aberta
    ACKNOWLEDGED = "acknowledged"  # Recebida/Reconhecida
    IN_ANALYSIS = "in_analysis"  # Em análise
    APPROVED = "approved"  # Aprovada
    REJECTED = "rejected"  # Rejeitada
    IN_PROGRESS = "in_progress"  # Em andamento
    WAITING_PARTS = "waiting_parts"  # Aguardando peças
    WAITING_APPROVAL = "waiting_approval"  # Aguardando aprovação
    COMPLETED = "completed"  # Concluída
    CLOSED = "closed"  # Fechada
    CANCELLED = "cancelled"  # Cancelada


class ServiceRequestPriority(str, Enum):
    """Prioridade da solicitação."""

    LOW = "low"  # Baixa
    MEDIUM = "medium"  # Média
    HIGH = "high"  # Alta
    URGENT = "urgent"  # Urgente
    CRITICAL = "critical"  # Crítica


class ServiceRequestCategory(str, Enum):
    """Categoria da solicitação."""

    MANUTENCAO = "manutencao"  # Manutenção geral
    ELETRICA = "eletrica"  # Elétrica
    HIDRAULICA = "hidraulica"  # Hidráulica
    LIMPEZA = "limpeza"  # Limpeza
    SEGURANCA = "seguranca"  # Segurança
    JARDINAGEM = "jardinagem"  # Jardinagem
    PINTURA = "pintura"  # Pintura
    CIVIL = "civil"  # Construção civil
    CLIMATIZACAO = "climatizacao"  # Ar condicionado
    ELEVADORES = "elevadores"  # Elevadores
    OUTROS = "outros"  # Outros


class ServiceRequest(Base):
    """
    Modelo de Solicitação de Serviço.

    Representa uma solicitação de serviço feita por um morador ou funcionário.

    Attributes:
        id: Identificador único
        code: Código da solicitação (SR-001)
        title: Título da solicitação
        description: Descrição detalhada
        category: Categoria do serviço
        status: Status atual
        priority: Prioridade
        area_id: Área relacionada
        requester_id: Solicitante
        requester_name: Nome do solicitante
        requester_unit: Unidade do solicitante
        requester_contact: Contato do solicitante
        assigned_to: Responsável atribuído
        scheduled_date: Data agendada
        deadline: Prazo limite
        started_at: Início do atendimento
        completed_at: Conclusão do atendimento
        estimated_cost: Custo estimado
        actual_cost: Custo real
        photos: Fotos anexadas
        feedback: Avaliação do solicitante
        satisfaction_rating: Nota de satisfação
    """

    __tablename__ = "service_requests"

    # Identificação
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Categoria, Status e Prioridade
    category: Mapped[str] = mapped_column(
        String(50),
        default=ServiceRequestCategory.MANUTENCAO.value,
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=ServiceRequestStatus.OPEN.value,
        nullable=False,
        index=True,
    )
    priority: Mapped[str] = mapped_column(
        String(50),
        default=ServiceRequestPriority.MEDIUM.value,
        nullable=False,
        index=True,
    )

    # Relacionamentos
    area_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("areas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    client_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    condominium_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )

    # Solicitante
    requester_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    requester_name: Mapped[str] = mapped_column(String(255), nullable=False)
    requester_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    requester_contact: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    requester_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Localização específica
    location_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    floor: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    building: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Responsáveis
    assigned_to: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    assigned_team: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    acknowledged_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Datas
    scheduled_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    deadline: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Custos
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    actual_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    requires_budget_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    budget_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    budget_approved_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    budget_approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Evidências
    photos: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    documents: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    completion_photos: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    # Resolução
    resolution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    root_cause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    work_performed: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Avaliação
    satisfaction_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # SLA
    sla_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sla_breached: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    response_time_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    resolution_time_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Rejeição/Cancelamento
    rejection_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Análise IA
    ai_category_suggestion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ai_priority_suggestion: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    ai_analysis: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Observações
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    internal_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Histórico
    status_history: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    # Campos de controle
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # Relacionamentos
    area: Mapped[Optional["Area"]] = relationship(
        "Area",
        back_populates="service_requests",
        lazy="selectin",
    )
    maintenances: Mapped[List["Maintenance"]] = relationship(
        "Maintenance",
        back_populates="service_request",
        foreign_keys="Maintenance.service_request_id",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<ServiceRequest {self.code} - {self.title}>"

    @property
    def is_open(self) -> bool:
        """Verifica se está aberta."""
        return self.status in (
            ServiceRequestStatus.OPEN.value,
            ServiceRequestStatus.ACKNOWLEDGED.value,
            ServiceRequestStatus.IN_ANALYSIS.value,
        )

    @property
    def is_in_progress(self) -> bool:
        """Verifica se está em andamento."""
        return self.status in (
            ServiceRequestStatus.APPROVED.value,
            ServiceRequestStatus.IN_PROGRESS.value,
            ServiceRequestStatus.WAITING_PARTS.value,
        )

    @property
    def is_completed(self) -> bool:
        """Verifica se está concluída."""
        return self.status in (
            ServiceRequestStatus.COMPLETED.value,
            ServiceRequestStatus.CLOSED.value,
        )

    @property
    def is_overdue(self) -> bool:
        """Verifica se está atrasada."""
        if not self.deadline:
            return False
        if self.is_completed:
            return False
        return date.today() > self.deadline

    @property
    def days_open(self) -> int:
        """Calcula dias em aberto."""
        if self.closed_at:
            return (self.closed_at.date() - self.created_at.date()).days
        return (date.today() - self.created_at.date()).days

    @property
    def has_sla_breach(self) -> bool:
        """Verifica se houve violação de SLA."""
        if not self.sla_hours:
            return False
        if self.response_time_hours and self.response_time_hours > self.sla_hours:
            return True
        return self.sla_breached

    def add_status_history(self, new_status: str, user_id: Optional[str] = None) -> None:
        """Adiciona entrada ao histórico de status."""
        if not self.status_history:
            self.status_history = []

        self.status_history.append(
            {
                "status": new_status,
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "previous_status": self.status,
            }
        )

    def calculate_response_time(self) -> Optional[float]:
        """Calcula tempo de resposta em horas."""
        if not self.acknowledged_at:
            return None
        delta = self.acknowledged_at - self.created_at
        return round(delta.total_seconds() / 3600, 2)

    def calculate_resolution_time(self) -> Optional[float]:
        """Calcula tempo de resolução em horas."""
        if not self.completed_at:
            return None
        delta = self.completed_at - self.created_at
        return round(delta.total_seconds() / 3600, 2)


# Adicionar relacionamento reverso no Maintenance
Maintenance.service_request = relationship(
    "ServiceRequest",
    back_populates="maintenances",
    foreign_keys=[Maintenance.service_request_id],
    lazy="selectin",
)
