"""Modelo de Morador."""

import random
import string
import uuid
from datetime import datetime, date
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.residents.models.vehicle import ResidentVehicle
    from modules.residents.models.pet import ResidentPet
    from modules.residents.models.dependent import ResidentDependent
    from modules.residents.models.emergency_contact import ResidentEmergencyContact


class ResidentType(str, Enum):
    """Tipo de morador."""

    PROPRIETARIO = "proprietario"
    INQUILINO = "inquilino"
    COMODATARIO = "comodatario"
    FAMILIAR = "familiar"
    FUNCIONARIO_DOMESTICO = "funcionario_domestico"
    TEMPORARIO = "temporario"
    OUTRO = "outro"


class ResidentStatus(str, Enum):
    """Status do morador."""

    ATIVO = "ativo"
    INATIVO = "inativo"
    SUSPENSO = "suspenso"
    PENDENTE = "pendente"
    BLOQUEADO = "bloqueado"
    MUDANCA = "mudanca"


class DocumentType(str, Enum):
    """Tipo de documento."""

    CPF = "cpf"
    RG = "rg"
    CNH = "cnh"
    PASSAPORTE = "passaporte"
    RNE = "rne"
    OUTRO = "outro"


class Gender(str, Enum):
    """Gênero."""

    MASCULINO = "masculino"
    FEMININO = "feminino"
    NAO_BINARIO = "nao_binario"
    PREFIRO_NAO_INFORMAR = "prefiro_nao_informar"
    OUTRO = "outro"


class MaritalStatus(str, Enum):
    """Estado civil."""

    SOLTEIRO = "solteiro"
    CASADO = "casado"
    DIVORCIADO = "divorciado"
    VIUVO = "viuvo"
    UNIAO_ESTAVEL = "uniao_estavel"
    SEPARADO = "separado"
    OUTRO = "outro"


class AccessMethod(str, Enum):
    """Método de acesso."""

    BIOMETRIA_FACIAL = "biometria_facial"
    BIOMETRIA_DIGITAL = "biometria_digital"
    CARTAO = "cartao"
    TAG_RFID = "tag_rfid"
    CONTROLE = "controle"
    APP = "app"
    QR_CODE = "qr_code"
    SENHA = "senha"


class Resident(Base):
    """Modelo de Morador."""

    __tablename__ = "residents"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    # Dados pessoais
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    social_name: Mapped[Optional[str]] = mapped_column(String(200))
    birth_date: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[Optional[Gender]] = mapped_column(String(30))
    marital_status: Mapped[Optional[MaritalStatus]] = mapped_column(String(20))
    nationality: Mapped[Optional[str]] = mapped_column(String(100))
    profession: Mapped[Optional[str]] = mapped_column(String(100))

    # Documentos
    document_type: Mapped[DocumentType] = mapped_column(String(20), nullable=False)
    document_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    cpf: Mapped[Optional[str]] = mapped_column(String(14), index=True)
    rg: Mapped[Optional[str]] = mapped_column(String(20))
    rg_issuer: Mapped[Optional[str]] = mapped_column(String(20))

    # Contato
    email: Mapped[Optional[str]] = mapped_column(String(200), index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    phone_secondary: Mapped[Optional[str]] = mapped_column(String(20))
    whatsapp: Mapped[Optional[str]] = mapped_column(String(20))

    # Tipo e status
    resident_type: Mapped[ResidentType] = mapped_column(
        String(30), default=ResidentType.PROPRIETARIO
    )
    status: Mapped[ResidentStatus] = mapped_column(
        String(20), default=ResidentStatus.ATIVO
    )

    # Localização no condomínio
    condominium_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    condominium_name: Mapped[Optional[str]] = mapped_column(String(200))
    unit_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    unit_number: Mapped[Optional[str]] = mapped_column(String(20))
    block: Mapped[Optional[str]] = mapped_column(String(20))
    floor: Mapped[Optional[str]] = mapped_column(String(10))

    # Responsável pela unidade
    is_unit_owner: Mapped[bool] = mapped_column(Boolean, default=False)
    is_main_resident: Mapped[bool] = mapped_column(Boolean, default=False)
    is_representative: Mapped[bool] = mapped_column(Boolean, default=False)

    # Foto e biometria
    photo_url: Mapped[Optional[str]] = mapped_column(String(500))
    facial_id: Mapped[Optional[str]] = mapped_column(String(100))
    fingerprint_id: Mapped[Optional[str]] = mapped_column(String(100))

    # Métodos de acesso habilitados
    access_methods: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    access_card_number: Mapped[Optional[str]] = mapped_column(String(50))
    access_tag_rfid: Mapped[Optional[str]] = mapped_column(String(50))
    access_control_code: Mapped[Optional[str]] = mapped_column(String(50))
    app_user_id: Mapped[Optional[str]] = mapped_column(String(50))

    # QR Code
    qr_code: Mapped[Optional[str]] = mapped_column(String(200))
    qr_code_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Datas de movimentação
    move_in_date: Mapped[Optional[date]] = mapped_column(Date)
    move_out_date: Mapped[Optional[date]] = mapped_column(Date)
    contract_start_date: Mapped[Optional[date]] = mapped_column(Date)
    contract_end_date: Mapped[Optional[date]] = mapped_column(Date)

    # Bloqueio
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    block_reason: Mapped[Optional[str]] = mapped_column(Text)
    blocked_by: Mapped[Optional[str]] = mapped_column(String(100))
    blocked_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Inadimplência
    is_defaulter: Mapped[bool] = mapped_column(Boolean, default=False)
    defaulter_since: Mapped[Optional[date]] = mapped_column(Date)
    debt_amount: Mapped[Optional[float]] = mapped_column(default=0.0)

    # Permissões especiais
    can_authorize_visitors: Mapped[bool] = mapped_column(Boolean, default=True)
    can_book_common_areas: Mapped[bool] = mapped_column(Boolean, default=True)
    can_vote_assembly: Mapped[bool] = mapped_column(Boolean, default=True)
    can_receive_deliveries: Mapped[bool] = mapped_column(Boolean, default=True)

    # Preferências de comunicação
    receive_email_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    receive_sms_notifications: Mapped[bool] = mapped_column(Boolean, default=False)
    receive_push_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    receive_whatsapp_notifications: Mapped[bool] = mapped_column(Boolean, default=True)

    # Observações
    notes: Mapped[Optional[str]] = mapped_column(Text)
    internal_notes: Mapped[Optional[str]] = mapped_column(Text)
    special_needs: Mapped[Optional[str]] = mapped_column(Text)

    # Metadados
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)
    tags: Mapped[Optional[list]] = mapped_column(JSONB, default=list)

    # Auditoria
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_by: Mapped[Optional[str]] = mapped_column(String(100))
    updated_by: Mapped[Optional[str]] = mapped_column(String(100))
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    deleted_by: Mapped[Optional[str]] = mapped_column(String(100))

    # Relacionamentos
    vehicles: Mapped[list["ResidentVehicle"]] = relationship(
        "ResidentVehicle", back_populates="resident", lazy="selectin"
    )
    pets: Mapped[list["ResidentPet"]] = relationship(
        "ResidentPet", back_populates="resident", lazy="selectin"
    )
    dependents: Mapped[list["ResidentDependent"]] = relationship(
        "ResidentDependent", back_populates="resident", lazy="selectin"
    )
    emergency_contacts: Mapped[list["ResidentEmergencyContact"]] = relationship(
        "ResidentEmergencyContact", back_populates="resident", lazy="selectin"
    )

    def __init__(self, **kwargs):
        """Inicializa o morador."""
        super().__init__(**kwargs)
        if not self.code:
            self.code = self._generate_code()

    def _generate_code(self) -> str:
        """Gera código único para o morador."""
        prefix = "MOR"
        random_part = "".join(random.choices(string.digits, k=8))
        return f"{prefix}{random_part}"

    def generate_qr_code(self) -> str:
        """Gera QR Code para o morador."""
        self.qr_code = f"RES-{self.id}-{uuid.uuid4().hex[:8]}"
        self.qr_code_generated_at = datetime.utcnow()
        return self.qr_code

    def block(self, reason: str, blocked_by: str) -> None:
        """Bloqueia o morador."""
        self.is_blocked = True
        self.status = ResidentStatus.BLOQUEADO
        self.block_reason = reason
        self.blocked_by = blocked_by
        self.blocked_at = datetime.utcnow()

    def unblock(self) -> None:
        """Desbloqueia o morador."""
        self.is_blocked = False
        self.status = ResidentStatus.ATIVO
        self.block_reason = None
        self.blocked_by = None
        self.blocked_at = None

    def set_defaulter(self, debt_amount: float = 0.0) -> None:
        """Marca como inadimplente."""
        self.is_defaulter = True
        self.defaulter_since = date.today()
        self.debt_amount = debt_amount

    def clear_defaulter(self) -> None:
        """Remove status de inadimplente."""
        self.is_defaulter = False
        self.defaulter_since = None
        self.debt_amount = 0.0

    def move_out(self, move_out_date: date = None) -> None:
        """Registra mudança do morador."""
        self.status = ResidentStatus.MUDANCA
        self.move_out_date = move_out_date or date.today()

    def activate(self) -> None:
        """Ativa o morador."""
        self.status = ResidentStatus.ATIVO

    def suspend(self, reason: str = None) -> None:
        """Suspende o morador."""
        self.status = ResidentStatus.SUSPENSO
        if reason:
            self.internal_notes = f"Suspenso: {reason}"

    def enable_access_method(self, method: AccessMethod) -> None:
        """Habilita método de acesso."""
        if not self.access_methods:
            self.access_methods = {}
        self.access_methods[method.value] = True

    def disable_access_method(self, method: AccessMethod) -> None:
        """Desabilita método de acesso."""
        if self.access_methods:
            self.access_methods[method.value] = False

    @property
    def is_active(self) -> bool:
        """Verifica se está ativo."""
        return self.status == ResidentStatus.ATIVO and not self.is_blocked

    @property
    def is_valid(self) -> bool:
        """Verifica se é válido para acesso."""
        if self.is_blocked:
            return False
        if self.status not in [ResidentStatus.ATIVO, ResidentStatus.PENDENTE]:
            return False
        if self.move_out_date and self.move_out_date <= date.today():
            return False
        return True

    @property
    def has_biometric(self) -> bool:
        """Verifica se tem biometria cadastrada."""
        return bool(self.facial_id or self.fingerprint_id)

    @property
    def has_access_card(self) -> bool:
        """Verifica se tem cartão de acesso."""
        return bool(self.access_card_number or self.access_tag_rfid)

    @property
    def full_address(self) -> str:
        """Retorna endereço completo no condomínio."""
        parts = []
        if self.block:
            parts.append(f"Bloco {self.block}")
        if self.unit_number:
            parts.append(f"Unidade {self.unit_number}")
        if self.floor:
            parts.append(f"Andar {self.floor}")
        return ", ".join(parts) if parts else "Não informado"

    @property
    def age(self) -> Optional[int]:
        """Calcula idade."""
        if not self.birth_date:
            return None
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )

    @property
    def display_name(self) -> str:
        """Nome para exibição (social ou civil)."""
        return self.social_name or self.name

    @property
    def contract_status(self) -> str:
        """Status do contrato de locação."""
        if not self.contract_end_date:
            return "sem_contrato"
        today = date.today()
        if self.contract_end_date < today:
            return "expirado"
        days_remaining = (self.contract_end_date - today).days
        if days_remaining <= 30:
            return "expirando"
        return "vigente"
