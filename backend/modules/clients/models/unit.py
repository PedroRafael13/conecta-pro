"""
Unit Model - Cadastro de Unidades
Sprint 30: Cadastro de Clientes/Condomínios
"""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.clients.models.condominium import Condominium


class UnitType(StrEnum):
    """Tipo de unidade."""

    APARTAMENTO = "apartamento"
    CASA = "casa"
    SALA_COMERCIAL = "sala_comercial"
    LOJA = "loja"
    COBERTURA = "cobertura"
    DUPLEX = "duplex"
    TRIPLEX = "triplex"
    STUDIO = "studio"
    KITNET = "kitnet"
    GARAGEM = "garagem"
    DEPOSITO = "deposito"
    GALPAO = "galpao"
    TERRENO = "terreno"
    OUTRO = "outro"


class UnitStatus(StrEnum):
    """Status da unidade."""

    DISPONIVEL = "disponivel"
    OCUPADA = "ocupada"
    ALUGADA = "alugada"
    VENDA = "venda"
    REFORMA = "reforma"
    BLOQUEADA = "bloqueada"
    INATIVA = "inativa"


class Unit(Base):
    """
    Model de Unidade.

    Representa uma unidade (apartamento, sala, etc.) dentro de um condomínio.
    """

    __tablename__ = "units"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominium_id = Column(
        UUID(as_uuid=True), ForeignKey("condominiums.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Identificação da unidade
    code = Column(String(20), nullable=False)
    number = Column(String(20), nullable=False)
    block = Column(String(20), nullable=True)
    tower = Column(String(50), nullable=True)
    floor = Column(Integer, nullable=True)

    # Tipo e status
    type = Column(Enum(UnitType), nullable=False, default=UnitType.APARTAMENTO)
    status = Column(Enum(UnitStatus), nullable=False, default=UnitStatus.DISPONIVEL)

    # Características
    area_m2 = Column(Numeric(10, 2), nullable=True)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    parking_spots = Column(Integer, nullable=True, default=0)
    has_balcony = Column(Boolean, nullable=False, default=False)
    has_service_area = Column(Boolean, nullable=False, default=False)
    has_storage = Column(Boolean, nullable=False, default=False)
    floor_type = Column(String(50), nullable=True)
    position = Column(String(50), nullable=True)

    # Proprietário
    owner_name = Column(String(200), nullable=True)
    owner_document = Column(String(20), nullable=True)
    owner_phone = Column(String(20), nullable=True)
    owner_email = Column(String(200), nullable=True)
    ownership_start_date = Column(Date, nullable=True)

    # Morador/Inquilino atual
    resident_name = Column(String(200), nullable=True)
    resident_document = Column(String(20), nullable=True)
    resident_phone = Column(String(20), nullable=True)
    resident_email = Column(String(200), nullable=True)
    resident_start_date = Column(Date, nullable=True)
    resident_end_date = Column(Date, nullable=True)
    is_tenant = Column(Boolean, nullable=False, default=False)

    # Contatos adicionais
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)

    # Vagas de garagem
    parking_spot_numbers = Column(ARRAY(String), nullable=True, default=list)

    # Financeiro
    monthly_fee = Column(Numeric(12, 2), nullable=True)
    extra_fee = Column(Numeric(12, 2), nullable=True, default=0)
    fraction = Column(Numeric(8, 6), nullable=True)
    is_defaulter = Column(Boolean, nullable=False, default=False)
    debt_amount = Column(Numeric(12, 2), nullable=True, default=0)
    last_payment_date = Column(Date, nullable=True)

    # Acesso
    access_card_number = Column(String(50), nullable=True)
    access_tag_number = Column(String(50), nullable=True)
    biometric_registered = Column(Boolean, nullable=False, default=False)
    facial_registered = Column(Boolean, nullable=False, default=False)
    total_authorized_persons = Column(Integer, nullable=False, default=0)
    total_vehicles = Column(Integer, nullable=False, default=0)
    total_pets = Column(Integer, nullable=False, default=0)

    # Integrações
    guardian_unit_id = Column(String(50), nullable=True)
    plus_unit_id = Column(String(50), nullable=True)

    # Configurações
    settings = Column(JSONB, nullable=True, default=dict)
    notes = Column(Text, nullable=True)
    tags = Column(ARRAY(String), nullable=True, default=list)

    # Flags
    is_active = Column(Boolean, nullable=False, default=True)
    receives_correspondence = Column(Boolean, nullable=False, default=True)
    allows_pets = Column(Boolean, nullable=False, default=True)

    # Auditoria
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relacionamentos
    condominium: "Condominium" = relationship("Condominium", back_populates="units")

    # Índices e constraints
    __table_args__ = (
        UniqueConstraint("condominium_id", "code", name="uq_units_condominium_code"),
        Index("ix_units_condominium_block", "condominium_id", "block"),
        Index("ix_units_condominium_tower", "condominium_id", "tower"),
        Index("ix_units_status", "status"),
        Index("ix_units_owner_document", "owner_document"),
        Index("ix_units_resident_document", "resident_document"),
        Index("ix_units_defaulter", "is_defaulter"),
    )

    def __repr__(self) -> str:
        return f"<Unit(id={self.id}, code={self.code}, number={self.number})>"

    @property
    def display_name(self) -> str:
        """Nome para exibição."""
        parts = []
        if self.tower:
            parts.append(f"Torre {self.tower}")
        if self.block:
            parts.append(f"Bloco {self.block}")
        if self.floor:
            parts.append(f"{self.floor}° andar")
        parts.append(f"Unidade {self.number}")
        return " - ".join(parts)

    @property
    def short_name(self) -> str:
        """Nome curto."""
        if self.block:
            return f"{self.block}-{self.number}"
        return self.number

    @property
    def is_occupied(self) -> bool:
        """Verifica se a unidade está ocupada."""
        return self.status in (UnitStatus.OCUPADA, UnitStatus.ALUGADA)

    @property
    def current_resident(self) -> str | None:
        """Morador atual (ou proprietário se não houver inquilino)."""
        if self.is_tenant and self.resident_name:
            return self.resident_name
        return self.owner_name

    @property
    def current_contact_phone(self) -> str | None:
        """Telefone de contato atual."""
        if self.is_tenant and self.resident_phone:
            return self.resident_phone
        return self.owner_phone

    @property
    def current_contact_email(self) -> str | None:
        """Email de contato atual."""
        if self.is_tenant and self.resident_email:
            return self.resident_email
        return self.owner_email

    @property
    def residency_days(self) -> int | None:
        """Dias de residência do morador atual."""
        start = self.resident_start_date if self.is_tenant else self.ownership_start_date
        if not start:
            return None
        return (date.today() - start).days

    @property
    def has_access_credentials(self) -> bool:
        """Verifica se tem credenciais de acesso cadastradas."""
        return bool(
            self.access_card_number or self.access_tag_number or self.biometric_registered or self.facial_registered
        )

    @property
    def total_fee(self) -> Decimal:
        """Taxa total (mensal + extra)."""
        monthly = self.monthly_fee or Decimal("0")
        extra = self.extra_fee or Decimal("0")
        return monthly + extra

    def set_owner(
        self,
        name: str,
        document: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        start_date: date | None = None,
    ) -> None:
        """Define o proprietário."""
        self.owner_name = name
        self.owner_document = document
        self.owner_phone = phone
        self.owner_email = email
        self.ownership_start_date = start_date or date.today()
        self.updated_at = datetime.utcnow()

    def set_resident(
        self,
        name: str,
        document: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        is_tenant: bool = False,
    ) -> None:
        """Define o morador/inquilino."""
        self.resident_name = name
        self.resident_document = document
        self.resident_phone = phone
        self.resident_email = email
        self.resident_start_date = start_date or date.today()
        self.resident_end_date = end_date
        self.is_tenant = is_tenant
        self.status = UnitStatus.ALUGADA if is_tenant else UnitStatus.OCUPADA
        self.updated_at = datetime.utcnow()

    def clear_resident(self) -> None:
        """Remove o morador."""
        self.resident_name = None
        self.resident_document = None
        self.resident_phone = None
        self.resident_email = None
        self.resident_start_date = None
        self.resident_end_date = None
        self.is_tenant = False
        self.status = UnitStatus.DISPONIVEL
        self.updated_at = datetime.utcnow()

    def set_defaulter(self, amount: Decimal) -> None:
        """Marca como inadimplente."""
        self.is_defaulter = True
        self.debt_amount = amount
        self.updated_at = datetime.utcnow()

    def clear_defaulter(self) -> None:
        """Remove status de inadimplente."""
        self.is_defaulter = False
        self.debt_amount = Decimal("0")
        self.last_payment_date = date.today()
        self.updated_at = datetime.utcnow()

    def block_unit(self, reason: str | None = None) -> None:
        """Bloqueia a unidade."""
        self.status = UnitStatus.BLOQUEADA
        if reason:
            self.notes = f"{self.notes or ''}\n[BLOQUEADO] {datetime.now()}: {reason}".strip()
        self.updated_at = datetime.utcnow()

    def unblock(self) -> None:
        """Desbloqueia a unidade."""
        if self.is_occupied:
            self.status = UnitStatus.ALUGADA if self.is_tenant else UnitStatus.OCUPADA
        else:
            self.status = UnitStatus.DISPONIVEL
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Ativa a unidade."""
        self.is_active = True
        if self.status == UnitStatus.INATIVA:
            self.status = UnitStatus.DISPONIVEL
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Desativa a unidade."""
        self.is_active = False
        self.status = UnitStatus.INATIVA
        self.updated_at = datetime.utcnow()

    def register_access_card(self, card_number: str) -> None:
        """Registra cartão de acesso."""
        self.access_card_number = card_number
        self.updated_at = datetime.utcnow()

    def register_access_tag(self, tag_number: str) -> None:
        """Registra tag de acesso."""
        self.access_tag_number = tag_number
        self.updated_at = datetime.utcnow()

    def register_biometric(self) -> None:
        """Marca biometria como registrada."""
        self.biometric_registered = True
        self.updated_at = datetime.utcnow()

    def register_facial(self) -> None:
        """Marca facial como registrado."""
        self.facial_registered = True
        self.updated_at = datetime.utcnow()

    def update_counts(
        self, authorized_persons: int | None = None, vehicles: int | None = None, pets: int | None = None
    ) -> None:
        """Atualiza contadores."""
        if authorized_persons is not None:
            self.total_authorized_persons = authorized_persons
        if vehicles is not None:
            self.total_vehicles = vehicles
        if pets is not None:
            self.total_pets = pets
        self.updated_at = datetime.utcnow()

    @staticmethod
    def generate_code(condominium_code: str, block: str | None, number: str) -> str:
        """Gera código da unidade."""
        if block:
            return f"{condominium_code}-{block}-{number}"
        return f"{condominium_code}-{number}"
