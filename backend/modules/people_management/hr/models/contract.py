"""
Modelo EmploymentContract — Contrato de Trabalho.

Gerencia contratos de trabalho (CLT, temporário, intermitente, etc.)
com dados de jornada, salário, adicionais e sindicato.
"""

from datetime import date, datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class ContractType(StrEnum):
    """Tipo de contrato de trabalho."""

    CLT_INDETERMINATE = "clt_indeterminate"
    CLT_DETERMINATE = "clt_determinate"
    TEMPORARY = "temporary"
    INTERMITTENT = "intermittent"
    APPRENTICE = "apprentice"
    INTERN = "intern"


class EmploymentContract(Base):
    """Modelo de Contrato de Trabalho.

    Registra contratos vigentes e históricos de cada colaborador,
    incluindo dados de jornada, remuneração e adicionais legais.
    """

    __tablename__ = "employment_contracts"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    employee_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="FK para employees",
    )
    type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    # Vigência
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Jornada
    work_schedule: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        comment="Ex: 12x36, 44h/sem, 6x1",
    )
    weekly_hours: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    # Remuneração
    base_salary: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    hazard_pay_percent: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True, default=0, comment="Periculosidade %"
    )
    unhealthy_pay_percent: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True, default=0, comment="Insalubridade %"
    )
    night_shift_percent: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True, default=0, comment="Adicional noturno %"
    )

    # Cargo e lotação
    job_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cost_center: Mapped[str | None] = mapped_column(String(50), nullable=True)
    workplace_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, comment="FK para local de trabalho"
    )

    # Sindicato
    union_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    union_code: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Controle
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    previous_contract_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, comment="FK para contrato anterior"
    )

    # Documentos
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    signed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Auditoria
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<EmploymentContract(id={self.id}, employee_id={self.employee_id}, "
            f"type={self.type}, is_current={self.is_current})>"
        )
