"""Chart of Accounts model - Plano de Contas Contábil."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base

if TYPE_CHECKING:
    from modules.financial.models.accounting_account import AccountingAccount


class ChartType(str, enum.Enum):
    """Tipo do plano de contas."""

    STANDARD = "STANDARD"  # Plano padrão
    REFERENCIAL = "REFERENCIAL"  # Plano referencial (SPED)
    CUSTOM = "CUSTOM"  # Personalizado


class ChartStatus(str, enum.Enum):
    """Status do plano de contas."""

    DRAFT = "DRAFT"  # Rascunho
    ACTIVE = "ACTIVE"  # Ativo
    INACTIVE = "INACTIVE"  # Inativo
    ARCHIVED = "ARCHIVED"  # Arquivado


class ChartStandard(str, enum.Enum):
    """Padrão do plano de contas."""

    CUSTOM = "CUSTOM"  # Personalizado
    SPED_ECF = "SPED_ECF"  # SPED ECF
    SPED_ECD = "SPED_ECD"  # SPED ECD
    CFC = "CFC"  # Conselho Federal de Contabilidade
    IFRS = "IFRS"  # International Financial Reporting Standards
    US_GAAP = "US_GAAP"  # US Generally Accepted Accounting Principles


class ChartOfAccounts(Base):
    """Plano de Contas - estrutura hierárquica de contas contábeis."""

    __tablename__ = "fin_charts_of_accounts"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    condominio_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Identificação
    code = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Tipo e Status
    chart_type = Column(
        Enum(ChartType, name="charttype", create_type=True),
        nullable=False,
        default=ChartType.STANDARD,
    )
    status = Column(
        Enum(ChartStatus, name="chartstatus", create_type=True),
        nullable=False,
        default=ChartStatus.DRAFT,
    )
    standard = Column(
        Enum(ChartStandard, name="chartstandard", create_type=True),
        nullable=False,
        default=ChartStandard.CUSTOM,
    )

    # Versão
    version = Column(String(20), nullable=True)
    version_date = Column(DateTime(timezone=True), nullable=True)

    # Configurações
    max_levels = Column(Integer, default=5, nullable=False)
    account_mask = Column(String(50), default="9.9.99.999.9999", nullable=True)
    separator = Column(String(1), default=".", nullable=True)

    # Período de Vigência
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)

    # Referência SPED
    sped_layout_code = Column(String(10), nullable=True)
    sped_version = Column(String(20), nullable=True)

    # Estatísticas (atualizadas automaticamente)
    total_accounts = Column(Integer, default=0, nullable=False)
    total_analytical = Column(Integer, default=0, nullable=False)
    total_synthetic = Column(Integer, default=0, nullable=False)

    # Integração
    external_code = Column(String(50), nullable=True)
    integration_data = Column(JSONB, nullable=True)

    # Flags
    is_default = Column(Boolean, default=False, nullable=False)
    allow_modifications = Column(Boolean, default=True, nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    # Observações
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    accounts: list["AccountingAccount"] = relationship(
        "AccountingAccount",
        back_populates="chart_of_accounts",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        """Representação string."""
        return f"<ChartOfAccounts {self.code} - {self.name}>"

    @property
    def is_active(self) -> bool:
        """Verifica se o plano está ativo."""
        return self.status == ChartStatus.ACTIVE and self.active

    @property
    def is_editable(self) -> bool:
        """Verifica se o plano pode ser editado."""
        return self.allow_modifications and self.status in [ChartStatus.DRAFT, ChartStatus.ACTIVE]
