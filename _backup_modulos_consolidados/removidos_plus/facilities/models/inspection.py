"""
Modelo Inspection (Inspeção/Vistoria) para Facilities.
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

if TYPE_CHECKING:
    from .area import Area
    from .checklist import Checklist


class InspectionType(str, Enum):
    """Tipo de inspeção."""

    ROTINA = "rotina"  # Inspeção de rotina
    SEGURANCA = "seguranca"  # Inspeção de segurança
    MANUTENCAO = "manutencao"  # Inspeção de manutenção
    CONFORMIDADE = "conformidade"  # Inspeção de conformidade
    ENTREGA = "entrega"  # Vistoria de entrega
    SAIDA = "saida"  # Vistoria de saída
    PERIODICA = "periodica"  # Inspeção periódica
    ESPECIAL = "especial"  # Inspeção especial


class InspectionStatus(str, Enum):
    """Status da inspeção."""

    SCHEDULED = "scheduled"  # Agendada
    IN_PROGRESS = "in_progress"  # Em andamento
    COMPLETED = "completed"  # Concluída
    CANCELLED = "cancelled"  # Cancelada
    PENDING_REVIEW = "pending_review"  # Aguardando revisão
    APPROVED = "approved"  # Aprovada
    REJECTED = "rejected"  # Rejeitada


class InspectionResult(str, Enum):
    """Resultado da inspeção."""

    APPROVED = "approved"  # Aprovado
    APPROVED_WITH_REMARKS = "approved_with_remarks"  # Aprovado com ressalvas
    REPROVED = "reproved"  # Reprovado
    INCONCLUSIVE = "inconclusive"  # Inconclusivo


class Inspection(Base):
    """
    Modelo de Inspeção/Vistoria.

    Representa uma inspeção realizada em uma área.

    Attributes:
        id: Identificador único
        code: Código da inspeção (INS-001)
        title: Título da inspeção
        description: Descrição
        inspection_type: Tipo de inspeção
        status: Status atual
        result: Resultado da inspeção
        area_id: Área inspecionada
        client_id: Cliente associado
        scheduled_date: Data agendada
        started_at: Início da inspeção
        completed_at: Fim da inspeção
        inspector_id: Inspetor responsável
        checklist_template_id: Template de checklist usado
        score: Pontuação (0-100)
        findings: Achados/Observações
        recommendations: Recomendações
        non_conformities: Não conformidades
        photos: Fotos tiradas
        signature: Assinatura digital
        next_inspection_date: Data próxima inspeção
    """

    __tablename__ = "inspections"

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
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Tipo, Status e Resultado
    inspection_type: Mapped[str] = mapped_column(
        String(50),
        default=InspectionType.ROTINA.value,
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=InspectionStatus.SCHEDULED.value,
        nullable=False,
        index=True,
    )
    result: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
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
    checklist_template_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # Datas
    scheduled_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_inspection_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Responsáveis
    inspector_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    inspector_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reviewed_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Pontuação e Métricas
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_ok: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_warning: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_critical: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Achados e Recomendações
    findings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommendations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    non_conformities: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    corrective_actions: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Evidências
    photos: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    documents: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    signature_inspector: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    signature_responsible: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Análise IA
    ai_analysis: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    ai_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ai_recommendations: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    # Observações
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    internal_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Recorrência
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recurrence_pattern: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    recurrence_interval: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

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
        back_populates="inspections",
        lazy="selectin",
    )
    checklists: Mapped[List["Checklist"]] = relationship(
        "Checklist",
        back_populates="inspection",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Inspection {self.code} - {self.title}>"

    @property
    def is_completed(self) -> bool:
        """Verifica se está concluída."""
        return self.status in (
            InspectionStatus.COMPLETED.value,
            InspectionStatus.APPROVED.value,
        )

    @property
    def is_pending(self) -> bool:
        """Verifica se está pendente."""
        return self.status in (
            InspectionStatus.SCHEDULED.value,
            InspectionStatus.PENDING_REVIEW.value,
        )

    @property
    def compliance_rate(self) -> Optional[float]:
        """Calcula taxa de conformidade."""
        if self.total_items == 0:
            return None
        return (self.items_ok / self.total_items) * 100

    @property
    def has_critical_issues(self) -> bool:
        """Verifica se há itens críticos."""
        return self.items_critical > 0

    @property
    def duration_minutes(self) -> Optional[int]:
        """Calcula duração em minutos."""
        if not self.started_at or not self.completed_at:
            return None
        delta = self.completed_at - self.started_at
        return int(delta.total_seconds() / 60)

    def calculate_score(self) -> float:
        """Calcula pontuação baseada nos itens."""
        if self.total_items == 0:
            return 0.0

        # Pesos: OK=100%, Warning=50%, Critical=0%
        weighted_sum = (self.items_ok * 100) + (self.items_warning * 50)
        max_possible = self.total_items * 100

        return round((weighted_sum / max_possible) * 100, 2)
