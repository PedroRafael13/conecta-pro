"""Modelo de Visitante."""

import random
import string
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.visitors.models.authorization import VisitorAuthorization
    from modules.visitors.models.log import VisitorLog


class VisitorType(str, Enum):
    """Tipos de visitante."""

    FAMILIAR = "familiar"
    AMIGO = "amigo"
    PRESTADOR = "prestador"
    ENTREGADOR = "entregador"
    CORREIO = "correio"
    IMOBILIARIA = "imobiliaria"
    TECNICO = "tecnico"
    MOTORISTA = "motorista"
    FUNCIONARIO_TERCEIRO = "funcionario_terceiro"
    REPRESENTANTE = "representante"
    AUTORIDADE = "autoridade"
    EMERGENCIA = "emergencia"
    OUTRO = "outro"


class VisitorStatus(str, Enum):
    """Status do visitante."""

    ATIVO = "ativo"
    BLOQUEADO = "bloqueado"
    TEMPORARIO = "temporario"
    VIP = "vip"
    INATIVO = "inativo"


class DocumentType(str, Enum):
    """Tipos de documento."""

    RG = "rg"
    CPF = "cpf"
    CNH = "cnh"
    PASSAPORTE = "passaporte"
    CTPS = "ctps"
    RNE = "rne"
    CREA = "crea"
    OAB = "oab"
    CRM = "crm"
    OUTRO = "outro"


class Visitor(Base):
    """Modelo de Visitante."""

    __tablename__ = "visitors"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    visitor_type: Mapped[VisitorType] = mapped_column(
        String(30), default=VisitorType.OUTRO
    )
    status: Mapped[VisitorStatus] = mapped_column(
        String(20), default=VisitorStatus.ATIVO
    )

    # Documentos
    document_type: Mapped[Optional[DocumentType]] = mapped_column(String(20))
    document_number: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    cpf: Mapped[Optional[str]] = mapped_column(String(14), index=True)
    rg: Mapped[Optional[str]] = mapped_column(String(20))

    # Contato
    email: Mapped[Optional[str]] = mapped_column(String(200))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    phone_secondary: Mapped[Optional[str]] = mapped_column(String(20))

    # Empresa (para prestadores/técnicos)
    company_name: Mapped[Optional[str]] = mapped_column(String(200))
    company_cnpj: Mapped[Optional[str]] = mapped_column(String(18))
    company_role: Mapped[Optional[str]] = mapped_column(String(100))
    badge_number: Mapped[Optional[str]] = mapped_column(String(50))

    # Veículo
    vehicle_plate: Mapped[Optional[str]] = mapped_column(String(10), index=True)
    vehicle_model: Mapped[Optional[str]] = mapped_column(String(100))
    vehicle_color: Mapped[Optional[str]] = mapped_column(String(50))
    vehicle_type: Mapped[Optional[str]] = mapped_column(String(50))

    # Biometria e Reconhecimento
    photo_url: Mapped[Optional[str]] = mapped_column(String(500))
    face_encoding: Mapped[Optional[str]] = mapped_column(Text)
    qr_code: Mapped[Optional[str]] = mapped_column(String(100))
    card_number: Mapped[Optional[str]] = mapped_column(String(50))
    biometric_template: Mapped[Optional[str]] = mapped_column(Text)

    # Condomínio padrão
    default_condominium_id: Mapped[Optional[str]] = mapped_column(String(50))
    default_condominium_name: Mapped[Optional[str]] = mapped_column(String(200))

    # Restrições
    blocked_reason: Mapped[Optional[str]] = mapped_column(Text)
    blocked_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    blocked_by_id: Mapped[Optional[str]] = mapped_column(String(50))
    blocked_by_name: Mapped[Optional[str]] = mapped_column(String(200))
    blocked_until: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Validade
    valid_from: Mapped[Optional[datetime]] = mapped_column(DateTime)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Estatísticas
    visit_count: Mapped[int] = mapped_column(Integer, default=0)
    last_visit_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    first_visit_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    avg_visit_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)

    # Observações e metadados
    notes: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    # Controle
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_by_id: Mapped[Optional[str]] = mapped_column(String(50))
    created_by_name: Mapped[Optional[str]] = mapped_column(String(200))

    # Relacionamentos
    authorizations: Mapped[list["VisitorAuthorization"]] = relationship(
        "VisitorAuthorization", back_populates="visitor"
    )
    logs: Mapped[list["VisitorLog"]] = relationship(
        "VisitorLog", back_populates="visitor"
    )

    def __init__(self, **kwargs):
        """Inicializa o visitante."""
        super().__init__(**kwargs)
        if not self.code:
            self.code = self._generate_code()

    def _generate_code(self) -> str:
        """Gera código único."""
        chars = string.ascii_uppercase + string.digits
        random_part = "".join(random.choices(chars, k=8))
        return f"VIS-{random_part}"

    def block(
        self,
        reason: str,
        blocked_by_id: str = None,
        blocked_by_name: str = None,
        until: datetime = None,
    ) -> None:
        """Bloqueia o visitante."""
        self.status = VisitorStatus.BLOQUEADO
        self.blocked_reason = reason
        self.blocked_at = datetime.utcnow()
        self.blocked_by_id = blocked_by_id
        self.blocked_by_name = blocked_by_name
        self.blocked_until = until

    def unblock(self) -> None:
        """Desbloqueia o visitante."""
        self.status = VisitorStatus.ATIVO
        self.blocked_reason = None
        self.blocked_at = None
        self.blocked_by_id = None
        self.blocked_by_name = None
        self.blocked_until = None

    def set_vip(self) -> None:
        """Define como VIP."""
        self.status = VisitorStatus.VIP

    def set_temporary(self, valid_until: datetime) -> None:
        """Define como temporário com validade."""
        self.status = VisitorStatus.TEMPORARIO
        self.valid_until = valid_until

    def deactivate(self) -> None:
        """Desativa o visitante."""
        self.status = VisitorStatus.INATIVO

    def activate(self) -> None:
        """Ativa o visitante."""
        self.status = VisitorStatus.ATIVO

    def register_visit(self, duration_minutes: int = None) -> None:
        """Registra uma visita."""
        now = datetime.utcnow()
        self.visit_count += 1
        self.last_visit_at = now

        if not self.first_visit_at:
            self.first_visit_at = now

        if duration_minutes:
            if self.avg_visit_duration_minutes:
                # Média móvel
                self.avg_visit_duration_minutes = int(
                    self.avg_visit_duration_minutes * 0.8 + duration_minutes * 0.2
                )
            else:
                self.avg_visit_duration_minutes = duration_minutes

    def soft_delete(self) -> None:
        """Soft delete do visitante."""
        self.is_deleted = True

    def generate_qr_code(self) -> str:
        """Gera QR Code único."""
        chars = string.ascii_uppercase + string.digits
        qr = "".join(random.choices(chars, k=16))
        self.qr_code = f"QR-{qr}"
        return self.qr_code

    @property
    def is_blocked(self) -> bool:
        """Verifica se está bloqueado."""
        if self.status != VisitorStatus.BLOQUEADO:
            return False
        if self.blocked_until and self.blocked_until < datetime.utcnow():
            return False
        return True

    @property
    def is_valid(self) -> bool:
        """Verifica se está dentro da validade."""
        now = datetime.utcnow()
        if self.valid_from and self.valid_from > now:
            return False
        if self.valid_until and self.valid_until < now:
            return False
        return True

    @property
    def is_active(self) -> bool:
        """Verifica se está ativo."""
        return (
            self.status in [VisitorStatus.ATIVO, VisitorStatus.VIP]
            and not self.is_blocked
            and self.is_valid
            and not self.is_deleted
        )

    @property
    def has_vehicle(self) -> bool:
        """Verifica se tem veículo cadastrado."""
        return bool(self.vehicle_plate)

    @property
    def has_biometric(self) -> bool:
        """Verifica se tem biometria cadastrada."""
        return bool(self.biometric_template or self.face_encoding)

    @property
    def display_name(self) -> str:
        """Nome para exibição."""
        if self.company_name:
            return f"{self.name} ({self.company_name})"
        return self.name

    @property
    def frequency_category(self) -> str:
        """Categoria de frequência."""
        if self.visit_count >= 50:
            return "frequente"
        if self.visit_count >= 20:
            return "regular"
        if self.visit_count >= 5:
            return "ocasional"
        return "raro"
