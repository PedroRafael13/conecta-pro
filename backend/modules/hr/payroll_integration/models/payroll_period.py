"""Model para período de folha de pagamento."""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base

if TYPE_CHECKING:
    from modules.hr.payroll_integration.models.payroll_event import PayrollEvent


class PeriodType(StrEnum):
    """Tipo de período de folha."""

    MONTHLY = "monthly"  # Mensal
    BIWEEKLY = "biweekly"  # Quinzenal
    WEEKLY = "weekly"  # Semanal
    SUPPLEMENTARY = "supplementary"  # Complementar/13º
    VACATION = "vacation"  # Férias
    TERMINATION = "termination"  # Rescisão
    ADVANCE = "advance"  # Adiantamento


class PeriodStatus(StrEnum):
    """Status do período de folha."""

    DRAFT = "draft"  # Rascunho
    OPEN = "open"  # Aberto para lançamentos
    CALCULATING = "calculating"  # Calculando
    CALCULATED = "calculated"  # Calculado
    REVIEWING = "reviewing"  # Em revisão
    APPROVED = "approved"  # Aprovado
    CLOSED = "closed"  # Fechado
    EXPORTED = "exported"  # Exportado para sistema externo
    CANCELLED = "cancelled"  # Cancelado


class PayrollPeriod(Base):
    """Período de folha de pagamento."""

    __tablename__ = "payroll_periods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Identificação do período
    code = Column(String(20), nullable=False)  # Ex: 2024-01, 2024-Q1
    name = Column(String(100), nullable=False)
    period_type = Column(String(20), nullable=False, default=PeriodType.MONTHLY.value)
    reference_month = Column(Integer, nullable=False)  # 1-12
    reference_year = Column(Integer, nullable=False)

    # Datas do período
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    payment_date = Column(Date, nullable=True)

    # Datas de controle
    calculation_date = Column(DateTime, nullable=True)
    approval_date = Column(DateTime, nullable=True)
    closing_date = Column(DateTime, nullable=True)
    export_date = Column(DateTime, nullable=True)

    # Status e workflow
    status = Column(String(20), nullable=False, default=PeriodStatus.DRAFT.value)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)

    # Totalizadores
    total_employees = Column(Integer, default=0)
    total_earnings = Column(Numeric(15, 2), default=0)  # Total proventos
    total_deductions = Column(Numeric(15, 2), default=0)  # Total descontos
    total_net = Column(Numeric(15, 2), default=0)  # Total líquido
    total_employer_cost = Column(Numeric(15, 2), default=0)  # Custo empregador

    # Detalhamento de horas
    total_regular_hours = Column(Numeric(10, 2), default=0)
    total_overtime_hours = Column(Numeric(10, 2), default=0)
    total_night_hours = Column(Numeric(10, 2), default=0)
    total_absence_hours = Column(Numeric(10, 2), default=0)
    total_bank_hours_credit = Column(Numeric(10, 2), default=0)
    total_bank_hours_debit = Column(Numeric(10, 2), default=0)

    # Configurações
    settings = Column(JSONB, default=dict)
    # {
    #   "auto_calculate": true,
    #   "include_inactive": false,
    #   "overtime_threshold": 44,
    #   "bank_hours_enabled": true,
    #   "night_shift_start": "22:00",
    #   "night_shift_end": "05:00"
    # }

    # Observações
    notes = Column(Text, nullable=True)

    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    # Relacionamentos
    events: list["PayrollEvent"] = relationship(
        "PayrollEvent",
        back_populates="period",
        lazy="dynamic",
    )

    __table_args__ = (
        Index("ix_payroll_periods_reference", "reference_year", "reference_month"),
        Index("ix_payroll_periods_dates", "start_date", "end_date"),
        Index("ix_payroll_periods_status", "status"),
        CheckConstraint("end_date >= start_date", name="ck_period_dates"),
        CheckConstraint(
            "reference_month >= 1 AND reference_month <= 12",
            name="ck_reference_month",
        ),
    )

    def __repr__(self) -> str:
        return f"<PayrollPeriod {self.code} - {self.status}>"

    @property
    def is_open(self) -> bool:
        """Verifica se período está aberto para lançamentos."""
        return self.status in [PeriodStatus.DRAFT.value, PeriodStatus.OPEN.value]

    @property
    def is_editable(self) -> bool:
        """Verifica se período pode ser editado."""
        return self.status not in [
            PeriodStatus.CLOSED.value,
            PeriodStatus.EXPORTED.value,
            PeriodStatus.CANCELLED.value,
        ]

    @property
    def can_calculate(self) -> bool:
        """Verifica se pode calcular o período."""
        return self.status in [
            PeriodStatus.DRAFT.value,
            PeriodStatus.OPEN.value,
            PeriodStatus.CALCULATED.value,
        ]

    @property
    def can_approve(self) -> bool:
        """Verifica se pode aprovar o período."""
        return self.status in [
            PeriodStatus.CALCULATED.value,
            PeriodStatus.REVIEWING.value,
        ]

    @property
    def can_close(self) -> bool:
        """Verifica se pode fechar o período."""
        return self.status == PeriodStatus.APPROVED.value

    @property
    def can_export(self) -> bool:
        """Verifica se pode exportar o período."""
        return self.status in [
            PeriodStatus.APPROVED.value,
            PeriodStatus.CLOSED.value,
        ]

    @property
    def days_count(self) -> int:
        """Quantidade de dias no período."""
        return (self.end_date - self.start_date).days + 1

    def calculate_totals(self, events: list["PayrollEvent"]) -> None:
        """Calcula totalizadores baseado nos eventos."""
        self.total_earnings = sum(e.value for e in events if e.event_type == "earning" and e.ativo)
        self.total_deductions = sum(e.value for e in events if e.event_type == "deduction" and e.ativo)
        self.total_net = self.total_earnings - self.total_deductions
        self.total_employees = len({e.employee_id for e in events if e.ativo})

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "code": self.code,
            "name": self.name,
            "period_type": self.period_type,
            "reference_month": self.reference_month,
            "reference_year": self.reference_year,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "payment_date": (self.payment_date.isoformat() if self.payment_date else None),
            "status": self.status,
            "total_employees": self.total_employees,
            "total_earnings": float(self.total_earnings or 0),
            "total_deductions": float(self.total_deductions or 0),
            "total_net": float(self.total_net or 0),
        }
