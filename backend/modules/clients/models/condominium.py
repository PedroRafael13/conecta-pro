"""
Condominium Model - Cadastro de Condomínios
Sprint 30: Cadastro de Clientes/Condomínios
"""

import enum
from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Date,
    Numeric, Integer, Enum, ForeignKey, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.clients.models.client import Client
    from modules.clients.models.unit import Unit


class CondominiumType(str, enum.Enum):
    """Tipo de condomínio."""
    RESIDENCIAL = "residencial"
    COMERCIAL = "comercial"
    MISTO = "misto"
    INDUSTRIAL = "industrial"
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    LOTEAMENTO = "loteamento"


class CondominiumStatus(str, enum.Enum):
    """Status do condomínio."""
    ATIVO = "ativo"
    INATIVO = "inativo"
    EM_IMPLANTACAO = "em_implantacao"
    SUSPENSO = "suspenso"
    ENCERRADO = "encerrado"


class AdministrationType(str, enum.Enum):
    """Tipo de administração."""
    PROPRIA = "propria"
    ADMINISTRADORA = "administradora"
    SINDICO_PROFISSIONAL = "sindico_profissional"
    AUTOGESTAO = "autogestao"


class Condominium(Base):
    """
    Model de Condomínio.

    Representa um condomínio gerenciado pelo cliente.
    Um cliente pode ter múltiplos condomínios.
    """

    __tablename__ = "condominiums"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    code = Column(String(20), unique=True, nullable=False, index=True)
    client_id = Column(
        UUID(as_uuid=True),
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Dados básicos
    name = Column(String(200), nullable=False)
    # REMOVED: type field (não existe no banco de dados)
    # type = Column(Enum(CondominiumType), nullable=False, default=CondominiumType.RESIDENCIAL)
    status = Column(
        Enum(CondominiumStatus), nullable=False, default=CondominiumStatus.EM_IMPLANTACAO
    )
    administration_type = Column(
        Enum(AdministrationType),
        nullable=True,
        default=AdministrationType.ADMINISTRADORA
    )

    # CNPJ do condomínio
    cnpj = Column(String(20), nullable=True, index=True)

    # Endereço
    address_street = Column(String(200), nullable=False)
    address_number = Column(String(20), nullable=True)
    address_complement = Column(String(100), nullable=True)
    address_neighborhood = Column(String(100), nullable=True)
    address_city = Column(String(100), nullable=False)
    address_state = Column(String(2), nullable=False)
    address_zipcode = Column(String(10), nullable=True)
    latitude = Column(Numeric(10, 8), nullable=True)
    longitude = Column(Numeric(11, 8), nullable=True)

    # Contatos
    phone = Column(String(20), nullable=True)
    phone_portaria = Column(String(20), nullable=True)
    email = Column(String(200), nullable=True)

    # Síndico
    syndic_name = Column(String(100), nullable=True)
    syndic_phone = Column(String(20), nullable=True)
    syndic_email = Column(String(200), nullable=True)
    syndic_cpf = Column(String(14), nullable=True)
    syndic_start_date = Column(Date, nullable=True)
    syndic_end_date = Column(Date, nullable=True)

    # Zelador/Gerente
    manager_name = Column(String(100), nullable=True)
    manager_phone = Column(String(20), nullable=True)
    manager_email = Column(String(200), nullable=True)

    # Características físicas
    total_units = Column(Integer, nullable=False, default=0)
    total_towers = Column(Integer, nullable=True, default=1)
    total_floors = Column(Integer, nullable=True)
    total_elevators = Column(Integer, nullable=True, default=0)
    total_parking_spots = Column(Integer, nullable=True, default=0)
    total_area_m2 = Column(Numeric(12, 2), nullable=True)
    built_area_m2 = Column(Numeric(12, 2), nullable=True)
    common_area_m2 = Column(Numeric(12, 2), nullable=True)
    construction_year = Column(Integer, nullable=True)

    # Áreas comuns
    has_pool = Column(Boolean, nullable=False, default=False)
    has_gym = Column(Boolean, nullable=False, default=False)
    has_party_room = Column(Boolean, nullable=False, default=False)
    has_playground = Column(Boolean, nullable=False, default=False)
    has_sports_court = Column(Boolean, nullable=False, default=False)
    has_barbecue = Column(Boolean, nullable=False, default=False)
    has_sauna = Column(Boolean, nullable=False, default=False)
    has_garden = Column(Boolean, nullable=False, default=False)
    common_areas = Column(ARRAY(String), nullable=True, default=list)

    # Segurança
    has_24h_security = Column(Boolean, nullable=False, default=False)
    has_cctv = Column(Boolean, nullable=False, default=False)
    has_access_control = Column(Boolean, nullable=False, default=False)
    has_electric_fence = Column(Boolean, nullable=False, default=False)
    has_alarm = Column(Boolean, nullable=False, default=False)
    has_intercom = Column(Boolean, nullable=False, default=False)
    total_access_points = Column(Integer, nullable=True, default=1)
    total_cameras = Column(Integer, nullable=True, default=0)

    # Dados operacionais
    implantation_date = Column(Date, nullable=True)
    activation_date = Column(Date, nullable=True)
    monthly_fee = Column(Numeric(12, 2), nullable=True)

    # Integrações
    guardian_id = Column(String(50), nullable=True)
    guardian_enabled = Column(Boolean, nullable=False, default=False)
    plus_id = Column(String(50), nullable=True)
    plus_enabled = Column(Boolean, nullable=False, default=False)

    # Configurações
    settings = Column(JSONB, nullable=True, default=dict)
    operating_hours = Column(JSONB, nullable=True)
    rules = Column(Text, nullable=True)
    tags = Column(ARRAY(String), nullable=True, default=list)
    notes = Column(Text, nullable=True)

    # Flags
    is_active = Column(Boolean, nullable=False, default=True)
    is_premium = Column(Boolean, nullable=False, default=False)

    # Auditoria
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relacionamentos
    client: "Client" = relationship("Client", back_populates="condominiums")
    units: List["Unit"] = relationship(
        "Unit",
        back_populates="condominium",
        cascade="all, delete-orphan"
    )

    # Índices
    __table_args__ = (
        Index("ix_condominiums_client_status", "client_id", "status"),
        Index("ix_condominiums_city_state", "address_city", "address_state"),
        # REMOVED: Index for "type" field (field doesn't exist in database)
        # Index("ix_condominiums_type", "type"),
    )

    def __repr__(self) -> str:
        return f"<Condominium(id={self.id}, code={self.code}, name={self.name})>"

    @property
    def full_address(self) -> str:
        """Endereço completo."""
        parts = []
        if self.address_street:
            addr = self.address_street
            if self.address_number:
                addr += f", {self.address_number}"
            if self.address_complement:
                addr += f" - {self.address_complement}"
            parts.append(addr)

        if self.address_neighborhood:
            parts.append(self.address_neighborhood)

        if self.address_city and self.address_state:
            parts.append(f"{self.address_city}/{self.address_state}")

        if self.address_zipcode:
            parts.append(f"CEP: {self.address_zipcode}")

        return ", ".join(parts)

    @property
    def occupied_units(self) -> int:
        """Quantidade de unidades ocupadas."""
        if not self.units:
            return 0
        return sum(1 for u in self.units if u.is_occupied)

    @property
    def occupancy_rate(self) -> float:
        """Taxa de ocupação."""
        if self.total_units == 0:
            return 0.0
        return (self.occupied_units / self.total_units) * 100

    @property
    def security_level(self) -> str:
        """Nível de segurança baseado nos recursos."""
        score = 0
        if self.has_24h_security:
            score += 3
        if self.has_cctv:
            score += 2
        if self.has_access_control:
            score += 2
        if self.has_electric_fence:
            score += 1
        if self.has_alarm:
            score += 1
        if self.has_intercom:
            score += 1

        if score >= 8:
            return "alto"
        elif score >= 5:
            return "medio"
        elif score >= 2:
            return "basico"
        return "minimo"

    @property
    def amenities_count(self) -> int:
        """Quantidade de áreas de lazer."""
        count = 0
        if self.has_pool:
            count += 1
        if self.has_gym:
            count += 1
        if self.has_party_room:
            count += 1
        if self.has_playground:
            count += 1
        if self.has_sports_court:
            count += 1
        if self.has_barbecue:
            count += 1
        if self.has_sauna:
            count += 1
        if self.has_garden:
            count += 1
        if self.common_areas:
            count += len(self.common_areas)
        return count

    @property
    def syndic_mandate_active(self) -> bool:
        """Verifica se o mandato do síndico está ativo."""
        if not self.syndic_start_date:
            return False
        today = date.today()
        if self.syndic_end_date and today > self.syndic_end_date:
            return False
        return today >= self.syndic_start_date

    @property
    def days_until_syndic_end(self) -> Optional[int]:
        """Dias até o fim do mandato do síndico."""
        if not self.syndic_end_date:
            return None
        return (self.syndic_end_date - date.today()).days

    def activate(self) -> None:
        """Ativa o condomínio."""
        self.status = CondominiumStatus.ATIVO
        self.is_active = True
        if not self.activation_date:
            self.activation_date = date.today()
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Desativa o condomínio."""
        self.status = CondominiumStatus.INATIVO
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def suspend(self, reason: Optional[str] = None) -> None:
        """Suspende o condomínio."""
        self.status = CondominiumStatus.SUSPENSO
        if reason:
            self.notes = f"{self.notes or ''}\n[SUSPENSO] {datetime.now()}: {reason}".strip()
        self.updated_at = datetime.utcnow()

    def start_implantation(self) -> None:
        """Inicia implantação."""
        self.status = CondominiumStatus.EM_IMPLANTACAO
        self.implantation_date = date.today()
        self.updated_at = datetime.utcnow()

    def finish_implantation(self) -> None:
        """Finaliza implantação e ativa."""
        self.activation_date = date.today()
        self.status = CondominiumStatus.ATIVO
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def update_syndic(
        self,
        name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        cpf: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> None:
        """Atualiza dados do síndico."""
        self.syndic_name = name
        self.syndic_phone = phone
        self.syndic_email = email
        self.syndic_cpf = cpf
        self.syndic_start_date = start_date or date.today()
        self.syndic_end_date = end_date
        self.updated_at = datetime.utcnow()

    def enable_guardian(self, guardian_id: str) -> None:
        """Habilita integração com Guardian."""
        self.guardian_enabled = True
        self.guardian_id = guardian_id
        self.updated_at = datetime.utcnow()

    def enable_plus(self, plus_id: str) -> None:
        """Habilita integração com Conecta Plus."""
        self.plus_enabled = True
        self.plus_id = plus_id
        self.updated_at = datetime.utcnow()

    def update_unit_count(self, count: int) -> None:
        """Atualiza contagem de unidades."""
        self.total_units = count
        self.updated_at = datetime.utcnow()

    @staticmethod
    def generate_code(client_code: str, sequence: int) -> str:
        """Gera código do condomínio."""
        return f"{client_code}-COND-{sequence:03d}"
