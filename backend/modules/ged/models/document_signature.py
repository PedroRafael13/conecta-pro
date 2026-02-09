"""Model de Assinatura de Documento para GED."""

import secrets
from datetime import datetime, timedelta
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.ged.models.document import Document


class SignatureType(StrEnum):
    """Tipos de assinatura."""

    SIMPLES = "simples"  # Assinatura simples (nome/email)
    ELETRONICA = "eletronica"  # Assinatura eletrônica avançada
    DIGITAL = "digital"  # Assinatura digital com certificado
    BIOMETRICA = "biometrica"  # Assinatura biométrica
    CARIMBO = "carimbo"  # Carimbo de tempo


class SignatureStatus(StrEnum):
    """Status da assinatura."""

    PENDENTE = "pendente"
    ASSINADO = "assinado"
    RECUSADO = "recusado"
    EXPIRADO = "expirado"
    CANCELADO = "cancelado"
    INVALIDO = "invalido"


class SignatureRole(StrEnum):
    """Papel do signatário."""

    PARTE = "parte"  # Parte contratante
    TESTEMUNHA = "testemunha"  # Testemunha
    APROVADOR = "aprovador"  # Aprovador
    FIADOR = "fiador"  # Fiador
    REPRESENTANTE = "representante"  # Representante legal
    OUTRO = "outro"


class DocumentSignature(Base):
    """Model de Assinatura de Documento."""

    __tablename__ = "ged_document_signatures"

    # Identificação
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    document_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("ged_documents.id"), nullable=False, index=True
    )

    # Signatário
    signer_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    signer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    signer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    signer_document: Mapped[str | None] = mapped_column(String(20), nullable=True)  # CPF/CNPJ
    signer_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    signer_role: Mapped[SignatureRole] = mapped_column(
        SQLEnum(SignatureRole, native_enum=False, create_constraint=False), default=SignatureRole.PARTE
    )

    # Tipo e Status
    signature_type: Mapped[SignatureType] = mapped_column(
        SQLEnum(SignatureType, native_enum=False, create_constraint=False), default=SignatureType.ELETRONICA
    )
    status: Mapped[SignatureStatus] = mapped_column(
        SQLEnum(SignatureStatus, native_enum=False, create_constraint=False), default=SignatureStatus.PENDENTE
    )

    # Ordem de assinatura
    order: Mapped[int] = mapped_column(Integer, default=1)
    is_sequential: Mapped[bool] = mapped_column(Boolean, default=False)

    # Token de assinatura
    signature_token: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Dados da assinatura
    signature_data: Mapped[str | None] = mapped_column(Text, nullable=True)  # Base64 da assinatura visual
    signature_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # SHA-256 do documento assinado
    certificate_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # {"issuer": "", "subject": "", "serial": "", "valid_from": "", "valid_until": ""}

    # Localização da assinatura
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position_x: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position_y: Mapped[int | None] = mapped_column(Integer, nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Rastreabilidade
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    geolocation: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # {"latitude": 0.0, "longitude": 0.0, "city": "", "country": ""}

    # Verificação
    verification_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    verification_method: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Recusa
    refusal_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Notificações
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    notification_sent_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reminder_count: Mapped[int] = mapped_column(Integer, default=0)
    last_reminder_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Prazo
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    signed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    refused_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Auditoria
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)

    # Metadados
    extra_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relacionamentos
    document: Mapped["Document"] = relationship("Document", back_populates="signatures")

    def __repr__(self) -> str:
        """Representação string."""
        return f"<DocumentSignature {self.document_id} - {self.signer_email}>"

    @property
    def is_pending(self) -> bool:
        """Verifica se assinatura está pendente."""
        return self.status == SignatureStatus.PENDENTE

    @property
    def is_signed(self) -> bool:
        """Verifica se foi assinado."""
        return self.status == SignatureStatus.ASSINADO

    @property
    def is_refused(self) -> bool:
        """Verifica se foi recusado."""
        return self.status == SignatureStatus.RECUSADO

    @property
    def is_expired(self) -> bool:
        """Verifica se expirou."""
        if not self.deadline:
            return False
        return datetime.utcnow() > self.deadline and self.is_pending

    @property
    def is_token_valid(self) -> bool:
        """Verifica se token é válido."""
        if not self.signature_token or not self.token_expires_at:
            return False
        return datetime.utcnow() < self.token_expires_at

    @property
    def days_until_deadline(self) -> int | None:
        """Retorna dias até o prazo."""
        if not self.deadline:
            return None
        delta = self.deadline - datetime.utcnow()
        return delta.days

    def sign(
        self,
        signature_data: str,
        signature_hash: str,
        ip_address: str = None,
        user_agent: str = None,
        geolocation: dict = None,
    ) -> None:
        """Registra a assinatura."""
        self.status = SignatureStatus.ASSINADO
        self.signature_data = signature_data
        self.signature_hash = signature_hash
        self.signed_at = datetime.utcnow()
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.geolocation = geolocation

    def refuse(self, reason: str) -> None:
        """Recusa a assinatura."""
        self.status = SignatureStatus.RECUSADO
        self.refusal_reason = reason
        self.refused_at = datetime.utcnow()

    def cancel(self) -> None:
        """Cancela a assinatura."""
        self.status = SignatureStatus.CANCELADO

    def mark_as_expired(self) -> None:
        """Marca como expirado."""
        self.status = SignatureStatus.EXPIRADO

    def mark_as_invalid(self) -> None:
        """Marca como inválido."""
        self.status = SignatureStatus.INVALIDO
        self.is_verified = False

    def verify(self, method: str) -> None:
        """Verifica a assinatura."""
        self.is_verified = True
        self.verified_at = datetime.utcnow()
        self.verification_method = method

    def send_notification(self) -> None:
        """Marca notificação como enviada."""
        self.notification_sent = True
        self.notification_sent_at = datetime.utcnow()

    def send_reminder(self) -> None:
        """Registra envio de lembrete."""
        self.reminder_count += 1
        self.last_reminder_at = datetime.utcnow()

    def generate_token(self, expires_in_hours: int = 72) -> str:
        """Gera token de assinatura."""
        self.signature_token = secrets.token_urlsafe(32)
        self.token_expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        return self.signature_token

    def extend_deadline(self, new_deadline: datetime) -> None:
        """Estende o prazo."""
        self.deadline = new_deadline
        if self.status == SignatureStatus.EXPIRADO:
            self.status = SignatureStatus.PENDENTE

    def check_and_expire(self) -> bool:
        """Verifica e atualiza status de expiração."""
        if self.is_expired and self.status == SignatureStatus.PENDENTE:
            self.status = SignatureStatus.EXPIRADO
            return True
        return False

    def set_certificate(
        self,
        issuer: str,
        subject: str,
        serial: str,
        valid_from: str,
        valid_until: str,
    ) -> None:
        """Define dados do certificado."""
        self.certificate_data = {
            "issuer": issuer,
            "subject": subject,
            "serial": serial,
            "valid_from": valid_from,
            "valid_until": valid_until,
        }
