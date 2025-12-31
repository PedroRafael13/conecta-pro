"""Model para contracheques/holerites."""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
import uuid

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    Index,
    UniqueConstraint,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from core.database import Base


class PaySlipStatus(str, Enum):
    """Status do contracheque."""

    DRAFT = "draft"  # Rascunho (em processamento)
    GENERATED = "generated"  # Gerado (aguardando aprovação)
    APPROVED = "approved"  # Aprovado (pronto para visualização)
    PUBLISHED = "published"  # Publicado (visível para funcionário)
    RECTIFIED = "rectified"  # Retificado (houve correção)
    CANCELLED = "cancelled"  # Cancelado


class PaySlipType(str, Enum):
    """Tipo de contracheque."""

    MONTHLY = "monthly"  # Mensal (normal)
    BIWEEKLY = "biweekly"  # Quinzenal
    ADVANCE = "advance"  # Adiantamento
    THIRTEENTH_1ST = "thirteenth_1st"  # 13º - 1ª parcela
    THIRTEENTH_2ND = "thirteenth_2nd"  # 13º - 2ª parcela
    VACATION = "vacation"  # Férias
    VACATION_BONUS = "vacation_bonus"  # 1/3 férias
    TERMINATION = "termination"  # Rescisão
    PLR = "plr"  # Participação nos Lucros
    BONUS = "bonus"  # Bônus
    COMPLEMENTARY = "complementary"  # Complementar


class PaySlip(Base):
    """Contracheque/Holerite do funcionário."""

    __tablename__ = "employee_payslips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    condominio_id = Column(
        UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )
    employee_id = Column(
        UUID(as_uuid=True),
        ForeignKey("funcionarios.id"),
        nullable=False,
        index=True,
    )
    period_id = Column(
        UUID(as_uuid=True),
        ForeignKey("hr_payroll_periods.id"),
        nullable=True,
        index=True,
    )

    # Identificação
    payslip_code = Column(String(30), nullable=False, index=True)
    payslip_type = Column(
        String(20),
        nullable=False,
        default=PaySlipType.MONTHLY.value,
    )
    status = Column(
        String(20),
        nullable=False,
        default=PaySlipStatus.DRAFT.value,
        index=True,
    )

    # Período de referência
    reference_month = Column(Integer, nullable=False)  # 1-12
    reference_year = Column(Integer, nullable=False)
    payment_date = Column(Date, nullable=True)

    # Dados do funcionário no momento
    employee_name = Column(String(200), nullable=False)
    employee_cpf = Column(String(14), nullable=False)
    employee_position = Column(String(100), nullable=True)
    employee_department = Column(String(100), nullable=True)
    employee_admission_date = Column(Date, nullable=True)

    # Valores totais
    gross_salary = Column(Numeric(15, 2), nullable=False, default=0)
    total_earnings = Column(Numeric(15, 2), nullable=False, default=0)
    total_deductions = Column(Numeric(15, 2), nullable=False, default=0)
    net_salary = Column(Numeric(15, 2), nullable=False, default=0)

    # Bases de cálculo
    inss_base = Column(Numeric(15, 2), nullable=True)
    irrf_base = Column(Numeric(15, 2), nullable=True)
    fgts_base = Column(Numeric(15, 2), nullable=True)

    # Tributos calculados
    inss_value = Column(Numeric(15, 2), nullable=True)
    irrf_value = Column(Numeric(15, 2), nullable=True)
    fgts_value = Column(Numeric(15, 2), nullable=True)
    fgts_deposit = Column(Numeric(15, 2), nullable=True)

    # Detalhamento de proventos e descontos
    earnings = Column(JSONB, default=list)
    # [{"code": "001", "description": "Salário Base", "reference": 30, "value": 5000.00}, ...]
    deductions = Column(JSONB, default=list)
    # [{"code": "101", "description": "INSS", "reference": 14, "value": 500.00}, ...]

    # Horas trabalhadas
    worked_days = Column(Integer, nullable=True)
    worked_hours = Column(Numeric(10, 2), nullable=True)
    overtime_hours_50 = Column(Numeric(10, 2), nullable=True)
    overtime_hours_100 = Column(Numeric(10, 2), nullable=True)
    night_hours = Column(Numeric(10, 2), nullable=True)
    absence_days = Column(Integer, nullable=True)
    absence_hours = Column(Numeric(10, 2), nullable=True)

    # Dependentes
    dependents_count = Column(Integer, default=0)
    dependents_irrf_deduction = Column(Numeric(10, 2), nullable=True)

    # PDF e arquivo
    pdf_path = Column(String(500), nullable=True)
    pdf_generated_at = Column(DateTime, nullable=True)
    pdf_hash = Column(String(64), nullable=True)  # SHA-256 do PDF

    # Visualização pelo funcionário
    first_viewed_at = Column(DateTime, nullable=True)
    view_count = Column(Integer, default=0)
    downloaded_at = Column(DateTime, nullable=True)
    download_count = Column(Integer, default=0)

    # Aceite/Contestação
    acknowledged_at = Column(DateTime, nullable=True)
    contested = Column(Boolean, default=False)
    contest_reason = Column(Text, nullable=True)
    contest_date = Column(DateTime, nullable=True)
    contest_resolved = Column(Boolean, nullable=True)
    contest_resolution = Column(Text, nullable=True)

    # Retificação
    is_rectification = Column(Boolean, default=False)
    original_payslip_id = Column(
        UUID(as_uuid=True),
        ForeignKey("employee_payslips.id"),
        nullable=True,
    )
    rectification_reason = Column(Text, nullable=True)

    # Assinatura digital
    digital_signature = Column(Text, nullable=True)
    signed_at = Column(DateTime, nullable=True)
    signed_by = Column(UUID(as_uuid=True), nullable=True)

    # Observações
    internal_notes = Column(Text, nullable=True)  # Visível apenas para RH
    employee_notes = Column(Text, nullable=True)  # Visível para funcionário

    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    published_at = Column(DateTime, nullable=True)
    published_by = Column(UUID(as_uuid=True), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "condominio_id",
            "employee_id",
            "payslip_type",
            "reference_month",
            "reference_year",
            "is_rectification",
            name="uq_payslip_employee_period_type",
        ),
        Index("ix_payslip_reference", "reference_year", "reference_month"),
        Index("ix_payslip_payment", "payment_date"),
        Index("ix_payslip_viewed", "first_viewed_at"),
    )

    def __repr__(self) -> str:
        return f"<PaySlip {self.payslip_code} - {self.employee_name}>"

    @property
    def reference_period(self) -> str:
        """Retorna período formatado (MM/YYYY)."""
        return f"{self.reference_month:02d}/{self.reference_year}"

    @property
    def is_published(self) -> bool:
        """Verifica se está publicado."""
        return self.status == PaySlipStatus.PUBLISHED.value

    @property
    def is_viewable(self) -> bool:
        """Verifica se pode ser visualizado pelo funcionário."""
        return self.status in [
            PaySlipStatus.PUBLISHED.value,
            PaySlipStatus.RECTIFIED.value,
        ]

    @property
    def can_contest(self) -> bool:
        """Verifica se pode ser contestado."""
        return (
            self.is_viewable
            and not self.contested
            and not self.acknowledged_at
        )

    def record_view(self) -> None:
        """Registra visualização do contracheque."""
        if not self.first_viewed_at:
            self.first_viewed_at = datetime.utcnow()
        self.view_count = (self.view_count or 0) + 1

    def record_download(self) -> None:
        """Registra download do contracheque."""
        self.downloaded_at = datetime.utcnow()
        self.download_count = (self.download_count or 0) + 1

    def to_summary(self) -> dict:
        """Retorna resumo para listagem."""
        return {
            "id": str(self.id),
            "payslip_code": self.payslip_code,
            "payslip_type": self.payslip_type,
            "reference_period": self.reference_period,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "net_salary": float(self.net_salary),
            "status": self.status,
            "viewed": self.first_viewed_at is not None,
            "downloaded": self.downloaded_at is not None,
            "acknowledged": self.acknowledged_at is not None,
            "contested": self.contested,
        }
