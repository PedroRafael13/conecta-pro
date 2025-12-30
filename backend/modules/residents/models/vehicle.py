"""Modelo de Veículo do Morador."""

import uuid
from datetime import datetime, date
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.residents.models.resident import Resident


class VehicleType(str, Enum):
    """Tipo de veículo."""

    CARRO = "carro"
    MOTO = "moto"
    CAMINHONETE = "caminhonete"
    SUV = "suv"
    VAN = "van"
    BICICLETA = "bicicleta"
    BICICLETA_ELETRICA = "bicicleta_eletrica"
    PATINETE = "patinete"
    CAMINHAO = "caminhao"
    OUTRO = "outro"


class VehicleStatus(str, Enum):
    """Status do veículo."""

    ATIVO = "ativo"
    INATIVO = "inativo"
    VENDIDO = "vendido"
    ROUBADO = "roubado"
    BLOQUEADO = "bloqueado"


class FuelType(str, Enum):
    """Tipo de combustível."""

    GASOLINA = "gasolina"
    ETANOL = "etanol"
    FLEX = "flex"
    DIESEL = "diesel"
    GNV = "gnv"
    ELETRICO = "eletrico"
    HIBRIDO = "hibrido"


class ResidentVehicle(Base):
    """Modelo de Veículo do Morador."""

    __tablename__ = "resident_vehicles"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Relacionamento com morador
    resident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("residents.id"), nullable=False, index=True
    )

    # Dados do veículo
    vehicle_type: Mapped[VehicleType] = mapped_column(
        String(30), default=VehicleType.CARRO
    )
    status: Mapped[VehicleStatus] = mapped_column(
        String(20), default=VehicleStatus.ATIVO
    )

    # Identificação do veículo
    plate: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    plate_city: Mapped[Optional[str]] = mapped_column(String(100))
    plate_state: Mapped[Optional[str]] = mapped_column(String(2))

    # Características
    brand: Mapped[Optional[str]] = mapped_column(String(50))
    model: Mapped[Optional[str]] = mapped_column(String(100))
    year: Mapped[Optional[int]] = mapped_column()
    year_model: Mapped[Optional[int]] = mapped_column()
    color: Mapped[Optional[str]] = mapped_column(String(50))
    fuel_type: Mapped[Optional[FuelType]] = mapped_column(String(20))

    # Documentação
    renavam: Mapped[Optional[str]] = mapped_column(String(20))
    chassi: Mapped[Optional[str]] = mapped_column(String(50))

    # Vaga de estacionamento
    parking_spot: Mapped[Optional[str]] = mapped_column(String(20))
    parking_spot_type: Mapped[Optional[str]] = mapped_column(String(50))
    has_reserved_spot: Mapped[bool] = mapped_column(Boolean, default=False)

    # Controle de acesso
    tag_rfid: Mapped[Optional[str]] = mapped_column(String(50))
    control_code: Mapped[Optional[str]] = mapped_column(String(50))
    is_authorized: Mapped[bool] = mapped_column(Boolean, default=True)

    # Foto
    photo_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Datas
    registration_date: Mapped[date] = mapped_column(Date, default=date.today)
    deactivation_date: Mapped[Optional[date]] = mapped_column(Date)

    # Bloqueio
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    block_reason: Mapped[Optional[str]] = mapped_column(Text)
    blocked_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Observações
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Metadados
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    # Auditoria
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relacionamentos
    resident: Mapped["Resident"] = relationship("Resident", back_populates="vehicles")

    def block(self, reason: str) -> None:
        """Bloqueia o veículo."""
        self.is_blocked = True
        self.status = VehicleStatus.BLOQUEADO
        self.block_reason = reason
        self.blocked_at = datetime.utcnow()
        self.is_authorized = False

    def unblock(self) -> None:
        """Desbloqueia o veículo."""
        self.is_blocked = False
        self.status = VehicleStatus.ATIVO
        self.block_reason = None
        self.blocked_at = None
        self.is_authorized = True

    def deactivate(self, reason: str = None) -> None:
        """Desativa o veículo."""
        self.status = VehicleStatus.INATIVO
        self.deactivation_date = date.today()
        self.is_authorized = False
        if reason:
            self.notes = f"Desativado: {reason}"

    def mark_as_sold(self) -> None:
        """Marca como vendido."""
        self.status = VehicleStatus.VENDIDO
        self.deactivation_date = date.today()
        self.is_authorized = False

    def mark_as_stolen(self) -> None:
        """Marca como roubado."""
        self.status = VehicleStatus.ROUBADO
        self.is_blocked = True
        self.is_authorized = False

    def assign_parking_spot(self, spot: str, spot_type: str = None) -> None:
        """Atribui vaga de estacionamento."""
        self.parking_spot = spot
        self.parking_spot_type = spot_type
        self.has_reserved_spot = True

    def remove_parking_spot(self) -> None:
        """Remove vaga de estacionamento."""
        self.parking_spot = None
        self.parking_spot_type = None
        self.has_reserved_spot = False

    @property
    def is_active(self) -> bool:
        """Verifica se está ativo."""
        return self.status == VehicleStatus.ATIVO and not self.is_blocked

    @property
    def is_valid_for_access(self) -> bool:
        """Verifica se pode acessar."""
        return self.is_authorized and self.is_active

    @property
    def full_description(self) -> str:
        """Descrição completa do veículo."""
        parts = []
        if self.brand:
            parts.append(self.brand)
        if self.model:
            parts.append(self.model)
        if self.year:
            parts.append(str(self.year))
        if self.color:
            parts.append(f"({self.color})")
        return " ".join(parts) if parts else "Não informado"

    @property
    def formatted_plate(self) -> str:
        """Placa formatada."""
        if not self.plate:
            return ""
        plate = self.plate.upper().replace("-", "").replace(" ", "")
        if len(plate) == 7:
            # Formato Mercosul ou antigo
            return f"{plate[:3]}-{plate[3:]}"
        return plate
