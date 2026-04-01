"""Model de Configuracao de Dashboard Financeiro."""

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from core.models.base import Base


class DashboardType(StrEnum):
    """Tipo de dashboard."""

    EXECUTIVE = "EXECUTIVE"
    OPERATIONAL = "OPERATIONAL"
    ANALYTICAL = "ANALYTICAL"
    TACTICAL = "TACTICAL"
    CUSTOM = "CUSTOM"


class DashboardStatus(StrEnum):
    """Status do dashboard."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DRAFT = "DRAFT"
    ARCHIVED = "ARCHIVED"


class DashboardLayout(StrEnum):
    """Layout do dashboard."""

    GRID_2X2 = "GRID_2X2"
    GRID_3X2 = "GRID_3X2"
    GRID_4X2 = "GRID_4X2"
    GRID_3X3 = "GRID_3X3"
    FREEFORM = "FREEFORM"
    RESPONSIVE = "RESPONSIVE"


class RefreshInterval(StrEnum):
    """Intervalo de atualizacao."""

    REAL_TIME = "REAL_TIME"
    MINUTE_1 = "MINUTE_1"
    MINUTE_5 = "MINUTE_5"
    MINUTE_15 = "MINUTE_15"
    MINUTE_30 = "MINUTE_30"
    HOUR_1 = "HOUR_1"
    HOUR_6 = "HOUR_6"
    DAILY = "DAILY"
    MANUAL = "MANUAL"


class FinancialDashboard(Base):
    """Dashboard Financeiro configuravel."""

    __tablename__ = "financial_dashboards"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Identificacao
    codigo = Column(String(50), nullable=False, index=True)
    nome = Column(String(200), nullable=False)
    descricao = Column(Text)

    # Configuracao
    tipo = Column(
        SQLEnum(DashboardType, name="dashboard_type_enum"),
        default=DashboardType.OPERATIONAL,
        nullable=False,
    )
    status = Column(
        SQLEnum(DashboardStatus, name="dashboard_status_enum"),
        default=DashboardStatus.DRAFT,
        nullable=False,
    )
    layout = Column(
        SQLEnum(DashboardLayout, name="dashboard_layout_enum"),
        default=DashboardLayout.GRID_3X2,
        nullable=False,
    )
    refresh_interval = Column(
        SQLEnum(RefreshInterval, name="refresh_interval_enum"),
        default=RefreshInterval.MINUTE_15,
        nullable=False,
    )

    # Acesso e Permissoes
    is_public = Column(Boolean, default=False, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    owner_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    allowed_roles = Column(JSONB, default=list)
    allowed_users = Column(JSONB, default=list)

    # Aparencia
    theme = Column(String(50), default="light")
    primary_color = Column(String(20), default="#1976d2")
    background_color = Column(String(20), default="#ffffff")
    custom_css = Column(Text)

    # Filtros Globais
    default_period_days = Column(Integer, default=30)
    default_filters = Column(JSONB, default=dict)
    available_filters = Column(JSONB, default=list)

    # Metadados
    version = Column(Integer, default=1, nullable=False)
    tags = Column(JSONB, default=list)
    extra_metadata = Column(JSONB, default=dict)

    # Estatisticas
    view_count = Column(Integer, default=0, nullable=False)
    last_viewed_at = Column(DateTime)
    last_modified_at = Column(DateTime, default=datetime.utcnow)

    # Auditoria
    created_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime)

    # Relacionamentos
    widgets = relationship(
        "FinancialWidget",
        back_populates="dashboard",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """Representacao do dashboard."""
        return f"<FinancialDashboard {self.codigo}: {self.nome}>"

    @property
    def is_active(self) -> bool:
        """Verifica se dashboard esta ativo."""
        return self.status == DashboardStatus.ACTIVE and self.deleted_at is None

    @property
    def widget_count(self) -> int:
        """Conta widgets do dashboard."""
        if self.widgets:
            return len(self.widgets)
        return 0

    @property
    def refresh_seconds(self) -> int:
        """Retorna intervalo de refresh em segundos."""
        intervals = {
            RefreshInterval.REAL_TIME: 5,
            RefreshInterval.MINUTE_1: 60,
            RefreshInterval.MINUTE_5: 300,
            RefreshInterval.MINUTE_15: 900,
            RefreshInterval.MINUTE_30: 1800,
            RefreshInterval.HOUR_1: 3600,
            RefreshInterval.HOUR_6: 21600,
            RefreshInterval.DAILY: 86400,
            RefreshInterval.MANUAL: 0,
        }
        return intervals.get(self.refresh_interval, 900)

    def increment_view(self) -> None:
        """Incrementa contador de visualizacoes."""
        self.view_count += 1
        self.last_viewed_at = datetime.utcnow()

    def publish(self) -> None:
        """Publica o dashboard."""
        self.status = DashboardStatus.ACTIVE
        self.last_modified_at = datetime.utcnow()

    def archive(self) -> None:
        """Arquiva o dashboard."""
        self.status = DashboardStatus.ARCHIVED
        self.last_modified_at = datetime.utcnow()

    def duplicate(self, new_name: str) -> "FinancialDashboard":
        """Duplica o dashboard."""
        return FinancialDashboard(
            condominio_id=self.condominio_id,
            codigo=f"{self.codigo}-COPY",
            nome=new_name,
            descricao=self.descricao,
            tipo=self.tipo,
            status=DashboardStatus.DRAFT,
            layout=self.layout,
            refresh_interval=self.refresh_interval,
            theme=self.theme,
            primary_color=self.primary_color,
            background_color=self.background_color,
            default_period_days=self.default_period_days,
            default_filters=self.default_filters,
            available_filters=self.available_filters,
            tags=self.tags,
        )
