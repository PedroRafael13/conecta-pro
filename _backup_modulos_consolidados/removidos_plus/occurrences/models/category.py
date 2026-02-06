"""Modelo de Categoria de Ocorrência."""

import random
import string
import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.occurrences.models.occurrence import Occurrence


class OccurrenceCategory(Base):
    """Modelo de Categoria de Ocorrência."""

    __tablename__ = "occurrence_categories"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Visual
    icon: Mapped[Optional[str]] = mapped_column(String(50))
    color: Mapped[Optional[str]] = mapped_column(String(20))
    order: Mapped[int] = mapped_column(Integer, default=0)

    # Hierarquia
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("occurrence_categories.id"), nullable=True
    )
    level: Mapped[int] = mapped_column(Integer, default=0)
    path: Mapped[Optional[str]] = mapped_column(String(500))

    # SLA Padrão
    default_sla_response_hours: Mapped[Optional[int]] = mapped_column(Integer)
    default_sla_resolution_hours: Mapped[Optional[int]] = mapped_column(Integer)
    default_priority: Mapped[Optional[str]] = mapped_column(String(20))

    # Atribuição automática
    auto_assign_to_id: Mapped[Optional[str]] = mapped_column(String(50))
    auto_assign_to_name: Mapped[Optional[str]] = mapped_column(String(200))
    auto_assign_department: Mapped[Optional[str]] = mapped_column(String(100))

    # Configurações
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_attachment: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_anonymous: Mapped[bool] = mapped_column(Boolean, default=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_on_create: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_on_update: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_on_resolve: Mapped[bool] = mapped_column(Boolean, default=True)

    # Notificação
    notification_emails: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    notification_template: Mapped[Optional[str]] = mapped_column(String(100))

    # Estatísticas
    occurrence_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_resolution_hours: Mapped[Optional[float]] = mapped_column(Integer)

    # Metadados
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    # Controle
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_by_id: Mapped[Optional[str]] = mapped_column(String(50))
    created_by_name: Mapped[Optional[str]] = mapped_column(String(200))

    # Relacionamentos
    occurrences: Mapped[list["Occurrence"]] = relationship(
        "Occurrence", back_populates="category"
    )
    children: Mapped[list["OccurrenceCategory"]] = relationship(
        "OccurrenceCategory", back_populates="parent", remote_side=[id]
    )
    parent: Mapped[Optional["OccurrenceCategory"]] = relationship(
        "OccurrenceCategory", back_populates="children", remote_side=[parent_id]
    )

    def __init__(self, **kwargs):
        """Inicializa a categoria."""
        super().__init__(**kwargs)
        if not self.code:
            self.code = self._generate_code()

    def _generate_code(self) -> str:
        """Gera código único."""
        chars = string.ascii_uppercase + string.digits
        random_part = "".join(random.choices(chars, k=6))
        return f"CAT-{random_part}"

    def increment_count(self) -> None:
        """Incrementa contador de ocorrências."""
        self.occurrence_count += 1

    def decrement_count(self) -> None:
        """Decrementa contador de ocorrências."""
        if self.occurrence_count > 0:
            self.occurrence_count -= 1

    def update_avg_resolution(self, new_resolution_hours: float) -> None:
        """Atualiza média de resolução."""
        if self.avg_resolution_hours is None:
            self.avg_resolution_hours = new_resolution_hours
        else:
            # Média móvel simples
            self.avg_resolution_hours = (
                self.avg_resolution_hours * 0.9 + new_resolution_hours * 0.1
            )

    def set_parent(self, parent: "OccurrenceCategory") -> None:
        """Define categoria pai."""
        self.parent_id = parent.id
        self.level = parent.level + 1
        self.path = f"{parent.path}/{self.code}" if parent.path else f"/{parent.code}/{self.code}"

    @property
    def has_children(self) -> bool:
        """Verifica se tem subcategorias."""
        return len(self.children) > 0 if self.children else False

    @property
    def is_root(self) -> bool:
        """Verifica se é categoria raiz."""
        return self.parent_id is None

    @property
    def full_name(self) -> str:
        """Retorna nome completo com hierarquia."""
        if self.parent:
            return f"{self.parent.full_name} > {self.name}"
        return self.name
