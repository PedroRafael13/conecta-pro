"""
Modelo SQLAlchemy para Férias e Afastamentos.
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, Date, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base


class VacationRequest(Base):
    """Modelo para solicitações de férias e afastamentos.

    DEPRECATED: Use modules.gestao_pessoas.ferias.models.HRVacationRequest como fonte única.
    Esta tabela (vacation_requests) é mantida apenas para compatibilidade com o módulo operacional.
    Os registros históricos foram migrados para hr_vacation_requests em 2026-04-06.
    """

    __tablename__ = "vacation_requests"

    id = Column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    tenant_id = Column(UUID(as_uuid=False), nullable=True, index=True)
    employee_id = Column(UUID(as_uuid=False), nullable=False, index=True)
    employee_name = Column(String(255), nullable=True)
    type = Column(String(30), nullable=False, default="ferias")  # ferias, afastamento, licenca, folga
    status = Column(String(20), nullable=False, default="pendente")  # pendente, aprovado, rejeitado, cancelado
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days = Column(String(10), nullable=True)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    approved_by = Column(UUID(as_uuid=False), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejected_reason = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(UUID(as_uuid=False), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<VacationRequest {self.employee_name} {self.type} {self.start_date}>"
