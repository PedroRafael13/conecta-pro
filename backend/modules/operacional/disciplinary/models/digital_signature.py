"""
Model DigitalSignature - Assinatura Digital.

Este modelo armazena assinaturas digitais coletadas em documentos
disciplinares, incluindo dados de rastreabilidade e validacao.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class SignerType(StrEnum):
    """Tipo de signatario."""

    EMPLOYEE = "employee"  # Funcionario
    SUPERVISOR = "supervisor"  # Supervisor
    HR = "hr"  # Recursos Humanos
    WITNESS = "witness"  # Testemunha
    MANAGER = "manager"  # Gerente
    DIRECTOR = "director"  # Diretor


class DigitalSignature(Base):
    """
    Modelo de Assinatura Digital.

    Armazena assinaturas digitais coletadas via canvas ou outro metodo,
    incluindo todos os dados necessarios para validacao e rastreabilidade.

    Attributes:
        id: Identificador unico UUID
        tenant_id: ID do tenant (multi-tenancy)
        signer_id: ID do usuario que assinou
        signer_type: Tipo de signatario (funcionario, supervisor, etc)
        signer_name: Nome do signatario (snapshot)
        signer_cpf: CPF do signatario (snapshot)
        document_type: Tipo do documento assinado
        document_id: ID do documento assinado
        signature_data: Dados da assinatura (Base64 do canvas)
        signature_hash: Hash SHA-256 do documento no momento da assinatura
        ip_address: IP de onde foi assinado
        user_agent: User-Agent do navegador
        latitude: Latitude da localizacao (opcional)
        longitude: Longitude da localizacao (opcional)
        geolocation_accuracy: Precisao da geolocalizacao em metros
        is_valid: Se assinatura e valida
        validated_at: Data/hora da validacao
        invalidated_at: Data/hora da invalidacao
        invalidation_reason: Motivo da invalidacao
        created_at: Data criacao da assinatura
    """

    __tablename__ = "digital_signatures"

    # === Identificacao ===
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    tenant_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
        comment="ID do tenant para multi-tenancy",
    )

    # === Signatario ===
    signer_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
        comment="ID do usuario que assinou",
    )
    signer_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Tipo de signatario: employee, supervisor, hr, witness, etc",
    )
    signer_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Nome do signatario (snapshot)",
    )
    signer_cpf: Mapped[str | None] = mapped_column(
        String(14),
        nullable=True,
        comment="CPF do signatario (snapshot)",
    )
    signer_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Email do signatario (snapshot)",
    )

    # === Documento ===
    document_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Tipo do documento: disciplinary_action, contract, etc",
    )
    document_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
        comment="ID do documento assinado",
    )

    # === Dados da Assinatura ===
    signature_data: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Dados da assinatura em Base64 (imagem do canvas)",
    )
    signature_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="Hash SHA-256 do documento no momento da assinatura",
    )

    # === Rastreabilidade ===
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
        comment="Endereco IP de onde foi assinado (IPv4 ou IPv6)",
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="User-Agent do navegador",
    )

    # === Geolocalizacao ===
    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Latitude da localizacao",
    )
    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Longitude da localizacao",
    )
    geolocation_accuracy: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Precisao da geolocalizacao em metros",
    )
    geolocation_timestamp: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Timestamp da captura de geolocalizacao",
    )

    # === Validacao ===
    is_valid: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Se a assinatura e valida",
    )
    validated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Data/hora da validacao",
    )
    invalidated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="Data/hora da invalidacao",
    )
    invalidation_reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Motivo da invalidacao",
    )

    # === Metadados ===
    device_fingerprint: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Fingerprint do dispositivo",
    )
    session_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="ID da sessao do usuario",
    )

    # === Controle ===
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
        comment="Data de criacao da assinatura",
    )

    def __repr__(self) -> str:
        """Representacao string do objeto."""
        return f"<DigitalSignature {self.id[:8]}... - {self.signer_type} - {self.document_type}>"

    @property
    def signer_type_enum(self) -> SignerType:
        """Retorna o tipo de signatario como enum."""
        return SignerType(self.signer_type)

    @property
    def has_geolocation(self) -> bool:
        """Verifica se possui dados de geolocalizacao."""
        return self.latitude is not None and self.longitude is not None

    @property
    def geolocation_tuple(self) -> tuple[float, float] | None:
        """Retorna tupla (latitude, longitude) ou None."""
        if self.has_geolocation:
            return (self.latitude, self.longitude)  # type: ignore
        return None

    def invalidate(self, reason: str) -> None:
        """
        Invalida a assinatura.

        Args:
            reason: Motivo da invalidacao
        """
        self.is_valid = False
        self.invalidated_at = datetime.utcnow()
        self.invalidation_reason = reason

    def validate(self) -> None:
        """Valida a assinatura."""
        self.is_valid = True
        self.validated_at = datetime.utcnow()
        self.invalidated_at = None
        self.invalidation_reason = None

    @classmethod
    def create_hash(cls, content: str) -> str:
        """
        Cria hash SHA-256 do conteudo.

        Args:
            content: Conteudo do documento para gerar hash

        Returns:
            Hash SHA-256 em hexadecimal
        """
        import hashlib

        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def verify_hash(self, content: str) -> bool:
        """
        Verifica se o hash do conteudo atual corresponde ao hash armazenado.

        Args:
            content: Conteudo do documento para verificar

        Returns:
            True se o hash corresponde, False caso contrario
        """
        current_hash = self.create_hash(content)
        return current_hash == self.signature_hash

    @property
    def signer_type_display_name(self) -> str:
        """Retorna nome de exibicao do tipo de signatario."""
        display_names = {
            SignerType.EMPLOYEE.value: "Funcionario",
            SignerType.SUPERVISOR.value: "Supervisor",
            SignerType.HR.value: "Recursos Humanos",
            SignerType.WITNESS.value: "Testemunha",
            SignerType.MANAGER.value: "Gerente",
            SignerType.DIRECTOR.value: "Diretor",
        }
        return display_names.get(self.signer_type, self.signer_type)
