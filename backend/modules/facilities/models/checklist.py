"""
Modelo Checklist e ChecklistItem para Facilities.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    from .area import Area
    from .inspection import Inspection


class ChecklistStatus(str, Enum):
    """Status do checklist."""

    DRAFT = "draft"  # Rascunho
    ACTIVE = "active"  # Ativo
    IN_PROGRESS = "in_progress"  # Em preenchimento
    COMPLETED = "completed"  # Concluído
    ARCHIVED = "archived"  # Arquivado


class ItemStatus(str, Enum):
    """Status de item do checklist."""

    PENDING = "pending"  # Pendente
    OK = "ok"  # Conforme
    WARNING = "warning"  # Alerta
    CRITICAL = "critical"  # Crítico
    NA = "na"  # Não aplicável


class Checklist(Base):
    """
    Modelo de Checklist.

    Representa um checklist de vistoria que pode ser usado em inspeções.

    Attributes:
        id: Identificador único
        code: Código do checklist (CHK-001)
        name: Nome do checklist
        description: Descrição
        version: Versão do checklist
        status: Status atual
        area_id: Área associada (se específico)
        inspection_id: Inspeção associada
        is_template: Se é um template reutilizável
        category: Categoria do checklist
        total_items: Total de itens
        completed_items: Itens preenchidos
        score: Pontuação calculada
        filled_by: Preenchido por
        filled_at: Data preenchimento
        reviewed_by: Revisado por
        reviewed_at: Data revisão
    """

    __tablename__ = "checklists"

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
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(String(10), default="1.0", nullable=False)

    # Status e Tipo
    status: Mapped[str] = mapped_column(
        String(50),
        default=ChecklistStatus.DRAFT.value,
        nullable=False,
        index=True,
    )
    is_template: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Relacionamentos
    area_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("areas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    inspection_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("inspections.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    template_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("checklists.id", ondelete="SET NULL"),
        nullable=True,
    )
    client_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )

    # Métricas
    total_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_ok: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_warning: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_critical: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Preenchimento
    filled_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    filled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reviewed_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Observações
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    general_observations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadados
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

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
        back_populates="checklists",
        lazy="selectin",
    )
    inspection: Mapped[Optional["Inspection"]] = relationship(
        "Inspection",
        back_populates="checklists",
        lazy="selectin",
    )
    items: Mapped[List["ChecklistItem"]] = relationship(
        "ChecklistItem",
        back_populates="checklist",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    template: Mapped[Optional["Checklist"]] = relationship(
        "Checklist",
        remote_side=[id],
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Checklist {self.code} - {self.name}>"

    @property
    def is_completed(self) -> bool:
        """Verifica se está completo."""
        return self.status == ChecklistStatus.COMPLETED.value

    @property
    def completion_rate(self) -> float:
        """Calcula taxa de preenchimento."""
        if self.total_items == 0:
            return 0.0
        return (self.completed_items / self.total_items) * 100

    @property
    def compliance_rate(self) -> Optional[float]:
        """Calcula taxa de conformidade."""
        filled = self.items_ok + self.items_warning + self.items_critical
        if filled == 0:
            return None
        return (self.items_ok / filled) * 100

    @property
    def has_critical_items(self) -> bool:
        """Verifica se há itens críticos."""
        return self.items_critical > 0

    def calculate_score(self) -> float:
        """Calcula pontuação do checklist."""
        filled = self.items_ok + self.items_warning + self.items_critical
        if filled == 0:
            return 0.0

        # Pesos: OK=100%, Warning=50%, Critical=0%
        weighted = (self.items_ok * 100) + (self.items_warning * 50)
        return round((weighted / (filled * 100)) * 100, 2)

    def update_metrics(self) -> None:
        """Atualiza métricas baseado nos itens."""
        if not self.items:
            return

        self.total_items = len(self.items)
        self.completed_items = sum(1 for i in self.items if i.status != ItemStatus.PENDING.value)
        self.items_ok = sum(1 for i in self.items if i.status == ItemStatus.OK.value)
        self.items_warning = sum(1 for i in self.items if i.status == ItemStatus.WARNING.value)
        self.items_critical = sum(1 for i in self.items if i.status == ItemStatus.CRITICAL.value)
        self.score = self.calculate_score()


class ChecklistItem(Base):
    """
    Modelo de Item de Checklist.

    Representa um item individual dentro de um checklist.

    Attributes:
        id: Identificador único
        checklist_id: Checklist pai
        order: Ordem de exibição
        category: Categoria do item
        question: Pergunta/descrição do item
        description: Descrição detalhada
        status: Status (ok, warning, critical, na)
        answer: Resposta/valor
        notes: Observações
        photo_url: URL da foto
        is_required: Se é obrigatório
        weight: Peso na pontuação
    """

    __tablename__ = "checklist_items"

    # Identificação
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    checklist_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("checklists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Ordenação e Categoria
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Conteúdo
    question: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    help_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Resposta
    status: Mapped[str] = mapped_column(
        String(50),
        default=ItemStatus.PENDING.value,
        nullable=False,
    )
    answer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answer_type: Mapped[str] = mapped_column(
        String(50),
        default="boolean",
        nullable=False,
    )  # boolean, text, number, select, photo
    answer_options: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    # Observações e Evidências
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photos: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    # Configurações
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    requires_photo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_notes_on_fail: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Referência normativa
    reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    norm_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Timestamps
    answered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    answered_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

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

    # Relacionamentos
    checklist: Mapped["Checklist"] = relationship(
        "Checklist",
        back_populates="items",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<ChecklistItem {self.order} - {self.question[:30]}>"

    @property
    def is_answered(self) -> bool:
        """Verifica se foi respondido."""
        return self.status != ItemStatus.PENDING.value

    @property
    def is_conforming(self) -> bool:
        """Verifica se está conforme."""
        return self.status == ItemStatus.OK.value

    @property
    def needs_attention(self) -> bool:
        """Verifica se precisa de atenção."""
        return self.status in (ItemStatus.WARNING.value, ItemStatus.CRITICAL.value)

    @property
    def score_contribution(self) -> float:
        """Calcula contribuição para pontuação."""
        if self.status in (ItemStatus.PENDING.value, ItemStatus.NA.value):
            return 0.0
        if self.status == ItemStatus.OK.value:
            return 100.0 * self.weight
        if self.status == ItemStatus.WARNING.value:
            return 50.0 * self.weight
        return 0.0  # CRITICAL
