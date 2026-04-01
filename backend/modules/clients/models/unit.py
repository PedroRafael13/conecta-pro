"""
Unit Model - Cadastro de Unidades
Sprint 30: Cadastro de Clientes/Condomínios

NOTA: Este model foi sincronizado com o banco de dados real em 29/03/2026.
Colunas correspondem EXATAMENTE ao schema da tabela units.
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
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.clients.models.condominium import Condominium


class UnitType(StrEnum):
    """Tipo de unidade."""

    APARTMENT = "apartment"
    HOUSE = "house"
    STORE = "store"
    OFFICE = "office"
    WAREHOUSE = "warehouse"
    PARKING = "parking"
    STORAGE = "storage"
    PENTHOUSE = "penthouse"
    DUPLEX = "duplex"
    TRIPLEX = "triplex"
    GARDEN = "garden"
    ROOFTOP = "rooftop"
    COMMON_AREA = "common_area"
    COMMERCIAL = "commercial"


class UnitStatus(StrEnum):
    """Status da unidade."""

    AVAILABLE = "available"
    OCCUPIED = "occupied"
    VACANT = "vacant"
    RENOVATION = "renovation"
    BLOCKED = "blocked"
    RESERVED = "reserved"
    DEFAULTER = "defaulter"


class Unit(Base):
    """
    Model de Unidade — sincronizado com banco real.

    Representa uma unidade (apartamento, sala, etc.) dentro de um condomínio.
    """

    __tablename__ = "units"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominium_id = Column(
        UUID(as_uuid=True), ForeignKey("condominiums.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Identificação da unidade
    code = Column(String(50), nullable=False)
    unit_number = Column("unit_number", String(20), nullable=False, index=True)
    block = Column(String(50), nullable=True, index=True)
    tower = Column(String(50), nullable=True, index=True)
    floor = Column(Integer, nullable=True)

    # Tipo e status — strings, não enums SQLAlchemy
    unit_type = Column("unit_type", String(30), nullable=False)
    status = Column("status", String(30), nullable=False, default="available")

    # Características
    private_area = Column(Float, nullable=True)
    total_area = Column(Float, nullable=True)
    bedrooms = Column(Integer, nullable=True)
    bathrooms = Column(Integer, nullable=True)
    parking_spaces = Column(Integer, nullable=True)

    # Proprietário
    owner_name = Column(String(200), nullable=True)
    owner_document = Column(String(20), nullable=True, index=True)
    owner_email = Column(String(255), nullable=True)
    owner_phone = Column(String(20), nullable=True)
    owner_mobile = Column(String(20), nullable=True)

    # Morador/Inquilino atual
    resident_name = Column(String(200), nullable=True)
    resident_document = Column(String(20), nullable=True, index=True)
    resident_email = Column(String(255), nullable=True)
    resident_phone = Column(String(20), nullable=True)
    resident_mobile = Column(String(20), nullable=True)
    resident_type = Column(String(20), nullable=True)

    # Financeiro
    condominium_fee = Column(Numeric(10, 2), nullable=True)
    extra_fee = Column(Numeric(10, 2), nullable=True)
    is_defaulter = Column(Boolean, nullable=False, default=False, index=True)
    debt_amount = Column(Numeric(15, 2), nullable=True)
    last_payment_date = Column(Date, nullable=True)

    # Acesso
    access_card = Column(String(50), nullable=True)
    access_tag = Column(String(50), nullable=True)
    biometric_registered = Column(Boolean, nullable=False, default=False)
    facial_registered = Column(Boolean, nullable=False, default=False)
    app_registered = Column(Boolean, nullable=False, default=False)

    # Veículos e contato de emergência
    vehicles = Column(JSONB, nullable=True)
    emergency_contact_name = Column(String(200), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relationship = Column(String(50), nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)
    tags = Column(JSONB, nullable=True)
    extra_metadata = Column("metadata", JSONB, nullable=True)

    # Flags — banco usa 'ativo' não 'is_active'
    ativo = Column(Boolean, nullable=False, default=True)

    # Auditoria
    created_at = Column(DateTime, nullable=False, server_default="now()")
    updated_at = Column(DateTime, nullable=False, server_default="now()", onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relacionamentos
    condominium: "Condominium" = relationship("Condominium", back_populates="units")

    # Índices e constraints
    __table_args__ = (UniqueConstraint("condominium_id", "code", name="uq_units_condominium_code"),)

    def __repr__(self) -> str:
        return f"<Unit(id={self.id}, code={self.code}, unit_number={self.unit_number})>"

    # Properties computadas (não são colunas)
    @property
    def is_active(self) -> bool:
        """Alias para ativo."""
        return bool(self.ativo)

    @property
    def number(self) -> str:
        """Alias para unit_number (compatibilidade)."""
        return self.unit_number or ""

    @property
    def type(self) -> str:
        """Alias para unit_type."""
        return self.unit_type or ""

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
        parts.append(f"Unidade {self.unit_number}")
        return " - ".join(parts)

    @property
    def short_name(self) -> str:
        """Nome curto."""
        if self.block:
            return f"{self.block}-{self.unit_number}"
        return self.unit_number or ""

    @property
    def is_occupied(self) -> bool:
        """Verifica se a unidade está ocupada."""
        return self.status in ("occupied", "reserved")

    @property
    def current_resident(self) -> str | None:
        """Morador atual (ou proprietário se não houver morador)."""
        if self.resident_name:
            return self.resident_name
        return self.owner_name

    @property
    def current_contact_phone(self) -> str | None:
        """Telefone de contato atual."""
        if self.resident_phone:
            return self.resident_phone
        return self.owner_phone

    @property
    def current_contact_email(self) -> str | None:
        """Email de contato atual."""
        if self.resident_email:
            return self.resident_email
        return self.owner_email

    @property
    def is_tenant(self) -> bool:
        """Verifica se o morador é inquilino."""
        return self.resident_type == "tenant" if self.resident_type else False

    @property
    def monthly_fee(self) -> Decimal | None:
        """Alias para condominium_fee."""
        return self.condominium_fee

    @property
    def has_access_credentials(self) -> bool:
        """Verifica se tem credenciais de acesso cadastradas."""
        return bool(self.access_card or self.access_tag or self.biometric_registered or self.facial_registered)

    @property
    def total_fee(self) -> Decimal:
        """Taxa total (mensal + extra)."""
        monthly = self.condominium_fee or Decimal("0")
        extra = self.extra_fee or Decimal("0")
        return monthly + extra

    @property
    def area_m2(self) -> float | None:
        """Alias para private_area (compatibilidade)."""
        return self.private_area

    @property
    def parking_spots(self) -> int | None:
        """Alias para parking_spaces (compatibilidade)."""
        return self.parking_spaces

    @property
    def total_authorized_persons(self) -> int:
        """Placeholder — não existe no banco."""
        return 0

    @property
    def total_vehicles(self) -> int:
        """Contagem de veículos do JSONB."""
        if not self.vehicles:
            return 0
        if isinstance(self.vehicles, list):
            return len(self.vehicles)
        return 0

    def set_owner(
        self,
        name: str,
        document: str | None = None,
        phone: str | None = None,
        email: str | None = None,
    ) -> None:
        """Define o proprietário."""
        self.owner_name = name
        self.owner_document = document
        self.owner_phone = phone
        self.owner_email = email
        self.updated_at = datetime.utcnow()

    def set_resident(
        self,
        name: str,
        document: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        resident_type: str = "owner",
    ) -> None:
        """Define o morador/inquilino."""
        self.resident_name = name
        self.resident_document = document
        self.resident_phone = phone
        self.resident_email = email
        self.resident_type = resident_type
        self.status = "occupied"
        self.updated_at = datetime.utcnow()

    def clear_resident(self) -> None:
        """Remove o morador."""
        self.resident_name = None
        self.resident_document = None
        self.resident_phone = None
        self.resident_email = None
        self.resident_mobile = None
        self.resident_type = None
        self.status = "available"
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
        self.status = "blocked"
        if reason:
            self.notes = f"{self.notes or ''}\n[BLOQUEADO] {datetime.now()}: {reason}".strip()
        self.updated_at = datetime.utcnow()

    def unblock(self) -> None:
        """Desbloqueia a unidade."""
        if self.resident_name:
            self.status = "occupied"
        else:
            self.status = "available"
        self.updated_at = datetime.utcnow()

    def activate(self) -> None:
        """Ativa a unidade."""
        self.ativo = True
        if self.status == "blocked":
            self.status = "available"
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Desativa a unidade."""
        self.ativo = False
        self.updated_at = datetime.utcnow()

    @staticmethod
    def generate_code(condominium_code: str, block: str | None, number: str) -> str:
        """Gera código da unidade."""
        if block:
            return f"{condominium_code}-{block}-{number}"
        return f"{condominium_code}-{number}"
