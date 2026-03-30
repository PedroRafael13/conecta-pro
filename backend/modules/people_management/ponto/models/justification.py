"""Model de justificativa de atraso/falta."""

import enum
from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Index,
    Integer,
    String,
    Text,
)

try:
    from core.database import Base
except ImportError:  # pragma: no cover
    from sqlalchemy.orm import declarative_base

    Base = declarative_base()


class JustificationCategory(enum.StrEnum):
    TRANSITO = "transito"
    SAUDE = "saude"
    FAMILIAR = "familiar"
    TRANSPORTE_PUBLICO = "transporte_publico"
    ACIDENTE = "acidente"
    OUTRO = "outro"


class JustificationStatus(enum.StrEnum):
    PENDENTE = "pendente"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"


class JustificationModel(Base):
    """Justificativa de atraso ou falta."""

    __tablename__ = "gp_justifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    justification_id = Column(String(36), unique=True, nullable=False, index=True)
    punch_id = Column(String(36), nullable=True, index=True)
    employee_id = Column(Integer, nullable=False, index=True)

    justification_type = Column(String(20), nullable=False)  # atraso, falta
    reason = Column(Text, nullable=False)
    category = Column(String(30), nullable=False)
    status = Column(
        String(20),
        nullable=False,
        default="pendente",
    )

    # Anexos (fotos, documentos)
    attachments = Column(JSON, nullable=True, default=list)

    # Integração Sólides — rastreabilidade da origem
    source = Column(String(50), nullable=True, default=None)
    source_id = Column(String(200), nullable=True, default=None, index=True)

    # Revisao
    reviewed_by = Column(String(36), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)

    # Auditoria
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    __table_args__ = (Index("ix_gp_justification_status", "status", "employee_id"),)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "justification_id": self.justification_id,
            "punch_id": self.punch_id,
            "employee_id": self.employee_id,
            "type": self.justification_type,
            "reason": self.reason,
            "category": self.category,
            "status": self.status,
            "attachments": self.attachments or [],
            "source": self.source,
            "source_id": self.source_id,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
