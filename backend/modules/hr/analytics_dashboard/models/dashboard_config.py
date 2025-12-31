"""Modelo DashboardConfig - Configuração de dashboards personalizados."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from .dashboard_widget import DashboardWidget


class DashboardType(str, Enum):
    """Tipo de dashboard."""
    EXECUTIVE = "executive"          # Visão executiva
    OPERATIONAL = "operational"      # Operacional diário
    ANALYTICAL = "analytical"        # Análises detalhadas
    COMPLIANCE = "compliance"        # Conformidade CLT
    CUSTOM = "custom"                # Personalizado


class DashboardVisibility(str, Enum):
    """Visibilidade do dashboard."""
    PRIVATE = "private"              # Só o criador
    TEAM = "team"                    # Equipe/departamento
    ORGANIZATION = "organization"   # Toda organização
    PUBLIC = "public"                # Todos os condôminos


class RefreshInterval(str, Enum):
    """Intervalo de atualização."""
    REALTIME = "realtime"            # Tempo real
    MINUTE_1 = "1m"                  # 1 minuto
    MINUTE_5 = "5m"                  # 5 minutos
    MINUTE_15 = "15m"                # 15 minutos
    MINUTE_30 = "30m"                # 30 minutos
    HOUR_1 = "1h"                    # 1 hora
    HOUR_6 = "6h"                    # 6 horas
    DAILY = "daily"                  # Diário
    MANUAL = "manual"                # Manual


class DashboardConfig(Base):
    """Modelo de configuração de dashboard."""

    __tablename__ = "dashboard_configs"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    condominio_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # Informações básicas
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Tipo e visibilidade
    dashboard_type: Mapped[str] = mapped_column(
        String(20),
        default=DashboardType.CUSTOM.value,
    )
    visibility: Mapped[str] = mapped_column(
        String(20),
        default=DashboardVisibility.PRIVATE.value,
    )

    # Layout
    layout_type: Mapped[str] = mapped_column(
        String(20),
        default="grid",
    )  # grid, freeform, tabs
    columns: Mapped[int] = mapped_column(Integer, default=12)
    row_height: Mapped[int] = mapped_column(Integer, default=100)  # pixels

    # Configurações de atualização
    refresh_interval: Mapped[str] = mapped_column(
        String(20),
        default=RefreshInterval.MINUTE_15.value,
    )
    auto_refresh: Mapped[bool] = mapped_column(Boolean, default=True)

    # Filtros padrão
    default_period: Mapped[str] = mapped_column(
        String(20),
        default="last_30_days",
    )  # today, yesterday, last_7_days, last_30_days, this_month, last_month, custom
    default_filters: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    # Compartilhamento
    shared_with_users: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    shared_with_roles: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    shared_with_departments: Mapped[Optional[list]] = mapped_column(JSONB, default=list)

    # Tema e estilo
    theme: Mapped[str] = mapped_column(String(20), default="light")
    color_scheme: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    custom_css: Mapped[Optional[str]] = mapped_column(Text)

    # Favoritos e ordenação
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Estatísticas
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    last_viewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Metadados
    settings: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    tags: Mapped[Optional[list]] = mapped_column(JSONB, default=list)

    # Auditoria
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relacionamentos
    widgets: Mapped[List["DashboardWidget"]] = relationship(
        "DashboardWidget",
        back_populates="dashboard",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # Índices
    __table_args__ = (
        Index("ix_dashboard_configs_condominio_owner", "condominio_id", "owner_id"),
        Index("ix_dashboard_configs_type", "dashboard_type"),
        Index("ix_dashboard_configs_visibility", "visibility"),
    )

    @property
    def widget_count(self) -> int:
        """Retorna número de widgets."""
        return self.widgets.count() if self.widgets else 0

    @property
    def is_shared(self) -> bool:
        """Verifica se dashboard é compartilhado."""
        return (
            self.visibility != DashboardVisibility.PRIVATE.value
            or bool(self.shared_with_users)
            or bool(self.shared_with_roles)
            or bool(self.shared_with_departments)
        )

    def can_view(self, user_id: uuid.UUID, user_role: str = None, department_id: uuid.UUID = None) -> bool:
        """Verifica se usuário pode visualizar."""
        if self.owner_id == user_id:
            return True
        if self.visibility == DashboardVisibility.PUBLIC.value:
            return True
        if self.visibility == DashboardVisibility.ORGANIZATION.value:
            return True
        if str(user_id) in [str(u) for u in (self.shared_with_users or [])]:
            return True
        if user_role and user_role in (self.shared_with_roles or []):
            return True
        if department_id and str(department_id) in [str(d) for d in (self.shared_with_departments or [])]:
            return True
        return False

    def can_edit(self, user_id: uuid.UUID) -> bool:
        """Verifica se usuário pode editar."""
        return self.owner_id == user_id

    def increment_view(self) -> None:
        """Incrementa contador de visualizações."""
        self.view_count += 1
        self.last_viewed_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "name": self.name,
            "slug": self.slug,
            "dashboard_type": self.dashboard_type,
            "visibility": self.visibility,
            "widget_count": self.widget_count,
            "is_default": self.is_default,
            "is_pinned": self.is_pinned,
            "view_count": self.view_count,
        }
