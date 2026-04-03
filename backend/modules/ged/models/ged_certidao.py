"""Model SQLAlchemy para Certidões da Empresa (GED)."""

from datetime import date, datetime, timedelta
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Date, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class CertidaoStatus(StrEnum):
    """Status calculado da certidão baseado em expiry_date."""

    VALIDA = "valida"
    A_VENCER = "a_vencer"
    VENCIDA = "vencida"
    SEM_VENCIMENTO = "sem_vencimento"


class GedCertidao(Base):
    """
    Certidões da empresa (Conecta Mais) gerenciadas pelo módulo GED.

    Exemplos: Certidão Negativa Federal, Alvará de Funcionamento,
    Certidão FGTS, Certidão Trabalhista, Certidão Estadual/Municipal.
    """

    __tablename__ = "ged_certidoes"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)
    issuing_body: Mapped[str | None] = mapped_column(String(255), nullable=True)
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    file_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    @property
    def status(self) -> str:
        """Calcula status dinamicamente baseado em expiry_date."""
        if self.expiry_date is None:
            return CertidaoStatus.SEM_VENCIMENTO
        hoje = date.today()
        if self.expiry_date < hoje:
            return CertidaoStatus.VENCIDA
        if self.expiry_date < hoje + timedelta(days=30):
            return CertidaoStatus.A_VENCER
        return CertidaoStatus.VALIDA

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "document_type": self.document_type,
            "issuing_body": self.issuing_body,
            "issue_date": self.issue_date.isoformat() if self.issue_date else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "status": self.status,
            "file_path": self.file_path,
            "file_url": self.file_url,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
