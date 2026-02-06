"""
Modelo Scale (Escala de Trabalho) para Operações.
"""

from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    from .post import Post
    from .shift import Shift


class ScaleType(str, Enum):
    """Tipo de escala de trabalho."""

    SCALE_12X36 = "12x36"  # 12h trabalho, 36h descanso
    SCALE_6X1 = "6x1"  # 6 dias trabalho, 1 folga
    SCALE_5X2 = "5x2"  # 5 dias trabalho, 2 folgas (seg-sex)
    SCALE_5X1 = "5x1"  # 5 dias trabalho, 1 folga
    SCALE_4X2 = "4x2"  # 4 dias trabalho, 2 folgas
    TURNO_REVEZAMENTO = "turno_revezamento"  # Rodízio manhã/tarde/noite
    ADMINISTRATIVO = "administrativo"  # Segunda a sexta, horário comercial
    PERSONALIZADO = "personalizado"  # Escala customizada


class ScaleStatus(str, Enum):
    """Status da escala."""

    DRAFT = "draft"  # Rascunho
    PENDING_APPROVAL = "pending_approval"  # Aguardando aprovação
    APPROVED = "approved"  # Aprovada
    PUBLISHED = "published"  # Publicada (enviada aos funcionários)
    IN_PROGRESS = "in_progress"  # Em execução (mês atual)
    COMPLETED = "completed"  # Concluída
    CANCELLED = "cancelled"  # Cancelada


class Scale(Base):
    """
    Modelo de Escala de Trabalho.

    Representa a escala mensal de um posto com todos os turnos.

    Attributes:
        id: Identificador único
        code: Código da escala (ESC-2024-01-POST001)
        post_id: Posto associado
        scale_type: Tipo de escala (12x36, 6x1, etc)
        status: Status da escala
        month: Mês da escala (1-12)
        year: Ano da escala
        start_date: Data de início
        end_date: Data de fim
        total_shifts: Total de turnos gerados
        total_hours: Total de horas na escala
        estimated_cost: Custo estimado
        overtime_hours: Horas extras previstas
    """

    __tablename__ = "scales"

    # Identificação
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Relacionamentos
    post_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Tipo e Status
    scale_type: Mapped[str] = mapped_column(
        String(50),
        default=ScaleType.SCALE_12X36.value,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=ScaleStatus.DRAFT.value,
        nullable=False,
        index=True,
    )

    # Período
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Métricas
    total_shifts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    filled_shifts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    overtime_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Configurações da escala (JSON)
    config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    """
    Exemplo de config:
    {
        "shift_duration_hours": 12,
        "rest_duration_hours": 36,
        "night_shift_start": "19:00",
        "day_shift_start": "07:00",
        "consider_holidays": true,
        "holiday_multiplier": 2.0
    }
    """

    # Observações
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Aprovação
    approved_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approval_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Publicação
    published_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

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

    # Relacionamentos (lazy="noload" para evitar erros de schema em tabelas relacionadas)
    post: Mapped["Post"] = relationship(
        "Post",
        back_populates="scales",
        lazy="noload",
    )
    shifts: Mapped[List["Shift"]] = relationship(
        "Shift",
        back_populates="scale",
        lazy="noload",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Scale {self.month}/{self.year} - {self.name or 'Sem nome'}>"

    @property
    def is_current_month(self) -> bool:
        """Verifica se é a escala do mês atual."""
        today = date.today()
        return self.month == today.month and self.year == today.year

    @property
    def is_published(self) -> bool:
        """Verifica se a escala foi publicada."""
        return self.status == ScaleStatus.PUBLISHED.value

    @property
    def can_edit(self) -> bool:
        """Verifica se a escala pode ser editada."""
        return self.status in (
            ScaleStatus.DRAFT.value,
            ScaleStatus.PENDING_APPROVAL.value,
        )

    @property
    def fill_rate(self) -> float:
        """Calcula taxa de preenchimento da escala (%)."""
        if self.total_shifts == 0:
            return 0.0
        return (self.filled_shifts / self.total_shifts) * 100
