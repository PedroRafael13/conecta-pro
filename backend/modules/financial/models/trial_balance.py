"""Trial Balance model - Balancete de Verificação."""

import enum
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class BalanceType(str, enum.Enum):
    """Tipo de balancete."""

    VERIFICATION = "VERIFICATION"  # Balancete de Verificação
    ANALYTICAL = "ANALYTICAL"  # Analítico
    SYNTHETIC = "SYNTHETIC"  # Sintético
    COMPARISON = "COMPARISON"  # Comparativo
    CONSOLIDATED = "CONSOLIDATED"  # Consolidado


class BalanceStatus(str, enum.Enum):
    """Status do balancete."""

    DRAFT = "DRAFT"  # Rascunho
    GENERATED = "GENERATED"  # Gerado
    APPROVED = "APPROVED"  # Aprovado
    PUBLISHED = "PUBLISHED"  # Publicado
    ARCHIVED = "ARCHIVED"  # Arquivado


class BalancePeriod(str, enum.Enum):
    """Período do balancete."""

    MONTHLY = "MONTHLY"  # Mensal
    QUARTERLY = "QUARTERLY"  # Trimestral
    SEMIANNUAL = "SEMIANNUAL"  # Semestral
    ANNUAL = "ANNUAL"  # Anual
    CUSTOM = "CUSTOM"  # Personalizado


class TrialBalance(Base):
    """Balancete de Verificação - relatório de saldos das contas."""

    __tablename__ = "fin_trial_balances"
    __table_args__ = (UniqueConstraint("condominio_id", "code", name="uq_trial_balance_code"),)

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    condominio_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Referências
    chart_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_charts_of_accounts.id"),
        nullable=False,
    )
    period_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_accounting_periods.id"),
        nullable=True,
    )

    # Identificação
    code = Column(String(30), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)

    # Tipo e Status
    balance_type = Column(
        Enum(BalanceType, name="balancetype", create_type=True),
        nullable=False,
        default=BalanceType.VERIFICATION,
    )
    status = Column(
        Enum(BalanceStatus, name="balancestatus", create_type=True),
        nullable=False,
        default=BalanceStatus.DRAFT,
    )
    balance_period = Column(
        Enum(BalancePeriod, name="balanceperiod", create_type=True),
        nullable=False,
        default=BalancePeriod.MONTHLY,
    )

    # Período de Referência
    reference_date = Column(Date, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=True)

    # Totais Gerais
    total_accounts = Column(Integer, default=0, nullable=False)
    total_analytical = Column(Integer, default=0, nullable=False)

    # Saldos Anteriores
    previous_debit_total = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    previous_credit_total = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    previous_balance_debit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    previous_balance_credit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Movimentos do Período
    period_debit_total = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    period_credit_total = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Saldos Atuais
    current_debit_total = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    current_credit_total = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    current_balance_debit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    current_balance_credit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Verificação (devem ser iguais)
    is_balanced = Column(Boolean, default=True, nullable=False)
    difference_amount = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Resultado
    total_revenue = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_expenses = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    period_result = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Patrimônio
    total_assets = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_liabilities = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    total_equity = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Geração
    generated_at = Column(DateTime(timezone=True), nullable=True)
    generated_by = Column(UUID(as_uuid=True), nullable=True)
    generation_time_ms = Column(Integer, nullable=True)  # Tempo de geração

    # Aprovação
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_notes = Column(Text, nullable=True)

    # Publicação
    published_by = Column(UUID(as_uuid=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Comparativo
    comparison_balance_id = Column(UUID(as_uuid=True), nullable=True)
    variation_absolute = Column(Numeric(18, 2), nullable=True)
    variation_percentage = Column(Numeric(8, 4), nullable=True)

    # Filtros utilizados
    filter_account_types = Column(JSONB, nullable=True)  # Tipos de conta filtrados
    filter_levels = Column(JSONB, nullable=True)  # Níveis incluídos
    filter_cost_centers = Column(JSONB, nullable=True)  # Centros de custo

    # Integração
    external_reference = Column(String(100), nullable=True)
    integration_data = Column(JSONB, nullable=True)

    # Exportações
    exported_pdf = Column(Boolean, default=False, nullable=False)
    exported_excel = Column(Boolean, default=False, nullable=False)
    exported_sped = Column(Boolean, default=False, nullable=False)
    last_export_date = Column(DateTime(timezone=True), nullable=True)

    # Flags
    include_zero_balance = Column(Boolean, default=False, nullable=False)
    include_inactive = Column(Boolean, default=False, nullable=False)
    show_cost_centers = Column(Boolean, default=False, nullable=False)
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
    items: list["TrialBalanceItem"] = relationship(
        "TrialBalanceItem",
        back_populates="trial_balance",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        """Representação string."""
        return f"<TrialBalance {self.code} - {self.reference_date}>"

    @property
    def can_approve(self) -> bool:
        """Verifica se pode ser aprovado."""
        return self.status == BalanceStatus.GENERATED and self.is_balanced

    @property
    def can_publish(self) -> bool:
        """Verifica se pode ser publicado."""
        return self.status == BalanceStatus.APPROVED


class TrialBalanceItem(Base):
    """Item do Balancete - saldo de uma conta específica."""

    __tablename__ = "fin_trial_balance_items"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Referência ao Balancete
    trial_balance_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_trial_balances.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Conta Contábil
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("fin_accounting_accounts.id"),
        nullable=False,
        index=True,
    )

    # Dados da Conta (snapshot)
    account_code = Column(String(30), nullable=False)
    account_name = Column(String(150), nullable=False)
    account_type = Column(String(20), nullable=False)
    account_nature = Column(String(10), nullable=False)
    account_level = Column(Integer, nullable=False)
    is_analytical = Column(Boolean, nullable=False)

    # Centro de Custo (opcional)
    cost_center_id = Column(UUID(as_uuid=True), nullable=True)
    cost_center_code = Column(String(20), nullable=True)
    cost_center_name = Column(String(100), nullable=True)

    # Saldo Anterior
    previous_debit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    previous_credit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    previous_balance = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Movimento do Período
    period_debit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    period_credit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Saldo Atual
    current_debit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    current_credit = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)
    current_balance = Column(Numeric(18, 2), default=Decimal("0"), nullable=False)

    # Variação (para comparativos)
    variation_absolute = Column(Numeric(18, 2), nullable=True)
    variation_percentage = Column(Numeric(8, 4), nullable=True)

    # Ordem de exibição
    display_order = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    # Relationships
    trial_balance: "TrialBalance" = relationship(
        "TrialBalance",
        back_populates="items",
    )

    def __repr__(self) -> str:
        """Representação string."""
        return f"<TrialBalanceItem {self.account_code} - {self.current_balance}>"

    @property
    def has_movement(self) -> bool:
        """Verifica se teve movimento no período."""
        return self.period_debit > 0 or self.period_credit > 0

    @property
    def balance_type(self) -> str:
        """Retorna se o saldo é devedor ou credor."""
        return "D" if self.current_balance >= 0 else "C"
