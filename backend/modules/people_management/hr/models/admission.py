"""
Modelo AdmissionProcess — Processo de Admissão.

Rastreia todo o workflow de admissão de um novo colaborador:
documentação, exame médico, assinatura de contrato e conclusão.
"""

from datetime import date, datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Date, DateTime, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class AdmissionStatus(StrEnum):
    """Status do processo de admissão."""

    DOCUMENTS_PENDING = "documents_pending"
    MEDICAL_EXAM = "medical_exam"
    CONTRACT_SIGNING = "contract_signing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AdmissionProcess(Base):
    """Modelo de Processo de Admissão.

    Controla o fluxo completo de admissão, desde a coleta de documentos
    até a assinatura do contrato e criação do registro de funcionário.
    """

    __tablename__ = "admission_processes"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    # Dados do candidato (preenchidos pelo form)
    candidate_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cpf: Mapped[str | None] = mapped_column(String(20), nullable=True)
    position: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    contract_type: Mapped[str | None] = mapped_column(String(20), nullable=True, default="CLT")

    candidate_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="FK para candidato (recruitment)",
    )
    employee_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="FK para funcionário criado após conclusão",
    )
    job_position_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="FK para vaga/posto",
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default=AdmissionStatus.DOCUMENTS_PENDING,
        nullable=False,
        index=True,
    )
    expected_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    salary_proposed: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    workplace_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="FK para local de trabalho",
    )

    # Checklist e documentos
    checklist: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)
    documents_received: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)

    # Exame médico
    medical_exam_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    medical_exam_result: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Contrato
    contract_signed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Observações
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Auditoria
    created_by_id: Mapped[str | None] = mapped_column(UUID(as_uuid=True), nullable=True)
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
        return f"<AdmissionProcess(id={self.id}, status={self.status}, expected_start={self.expected_start_date})>"
