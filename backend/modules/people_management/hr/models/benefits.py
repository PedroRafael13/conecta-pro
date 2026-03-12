"""
Modelo EmployeeBenefit — Benefícios do Colaborador.

Gerencia os benefícios atribuídos a cada colaborador:
VT, VR, VA, plano de saúde, odontológico, seguro de vida, etc.
"""

from datetime import date, datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Date, DateTime, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class BenefitType(StrEnum):
    """Tipo de benefício."""

    VALE_TRANSPORTE = "vale_transporte"
    VALE_REFEICAO = "vale_refeicao"
    VALE_ALIMENTACAO = "vale_alimentacao"
    PLANO_SAUDE = "plano_saude"
    PLANO_ODONTOLOGICO = "plano_odontologico"
    SEGURO_VIDA = "seguro_vida"
    AUXILIO_CRECHE = "auxilio_creche"
    GYM_PASS = "gym_pass"  # noqa: S105
    OTHER = "other"


class BenefitStatus(StrEnum):
    """Status do benefício."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class EmployeeBenefit(Base):
    """Modelo de Benefício do Colaborador.

    Registra cada benefício concedido, com valores de contribuição
    do empregado e da empresa, operadora, plano e vigência.
    """

    __tablename__ = "employee_benefits"

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
        index=True,
    )
    provider: Mapped[str | None] = mapped_column(String(200), nullable=True)
    plan_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Valores
    employee_contribution: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True, default=0)
    company_contribution: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True, default=0)

    # Vigência
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default=BenefitStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    # Dados adicionais
    card_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

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
            f"<EmployeeBenefit(id={self.id}, employee_id={self.employee_id}, type={self.type}, status={self.status})>"
        )
