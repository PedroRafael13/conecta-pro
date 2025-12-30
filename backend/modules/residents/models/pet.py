"""Modelo de Pet do Morador."""

import uuid
from datetime import datetime, date
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.residents.models.resident import Resident


class PetType(str, Enum):
    """Tipo de pet."""

    CACHORRO = "cachorro"
    GATO = "gato"
    PASSARO = "passaro"
    PEIXE = "peixe"
    HAMSTER = "hamster"
    COELHO = "coelho"
    TARTARUGA = "tartaruga"
    REPTIL = "reptil"
    OUTRO = "outro"


class PetSize(str, Enum):
    """Porte do pet."""

    MINI = "mini"
    PEQUENO = "pequeno"
    MEDIO = "medio"
    GRANDE = "grande"
    GIGANTE = "gigante"


class PetStatus(str, Enum):
    """Status do pet."""

    ATIVO = "ativo"
    INATIVO = "inativo"
    FALECIDO = "falecido"
    DOADO = "doado"
    PERDIDO = "perdido"


class ResidentPet(Base):
    """Modelo de Pet do Morador."""

    __tablename__ = "resident_pets"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Relacionamento com morador
    resident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("residents.id"), nullable=False, index=True
    )

    # Dados do pet
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    pet_type: Mapped[PetType] = mapped_column(String(20), nullable=False)
    status: Mapped[PetStatus] = mapped_column(String(20), default=PetStatus.ATIVO)

    # Características
    breed: Mapped[Optional[str]] = mapped_column(String(100))
    color: Mapped[Optional[str]] = mapped_column(String(50))
    size: Mapped[Optional[PetSize]] = mapped_column(String(20))
    weight_kg: Mapped[Optional[float]] = mapped_column(Float)
    birth_date: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[Optional[str]] = mapped_column(String(20))

    # Identificação
    microchip_number: Mapped[Optional[str]] = mapped_column(String(50))
    registration_number: Mapped[Optional[str]] = mapped_column(String(50))

    # Saúde
    is_vaccinated: Mapped[bool] = mapped_column(Boolean, default=False)
    vaccination_date: Mapped[Optional[date]] = mapped_column(Date)
    vaccination_expiry: Mapped[Optional[date]] = mapped_column(Date)
    is_neutered: Mapped[bool] = mapped_column(Boolean, default=False)
    has_special_needs: Mapped[bool] = mapped_column(Boolean, default=False)
    special_needs_description: Mapped[Optional[str]] = mapped_column(Text)
    veterinarian_name: Mapped[Optional[str]] = mapped_column(String(200))
    veterinarian_phone: Mapped[Optional[str]] = mapped_column(String(20))

    # Comportamento
    is_aggressive: Mapped[bool] = mapped_column(Boolean, default=False)
    aggression_notes: Mapped[Optional[str]] = mapped_column(Text)
    is_noisy: Mapped[bool] = mapped_column(Boolean, default=False)
    behavior_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Permissões
    can_use_common_areas: Mapped[bool] = mapped_column(Boolean, default=True)
    allowed_areas: Mapped[Optional[list]] = mapped_column(JSONB, default=list)
    walking_schedule: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    # Foto
    photo_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Documentos (vacinas, etc)
    documents: Mapped[Optional[list]] = mapped_column(JSONB, default=list)

    # Datas
    registration_date: Mapped[date] = mapped_column(Date, default=date.today)
    deactivation_date: Mapped[Optional[date]] = mapped_column(Date)

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
    resident: Mapped["Resident"] = relationship("Resident", back_populates="pets")

    def deactivate(self, reason: str = None) -> None:
        """Desativa o pet."""
        self.status = PetStatus.INATIVO
        self.deactivation_date = date.today()
        if reason:
            self.notes = f"Desativado: {reason}"

    def mark_as_deceased(self) -> None:
        """Marca como falecido."""
        self.status = PetStatus.FALECIDO
        self.deactivation_date = date.today()

    def mark_as_donated(self) -> None:
        """Marca como doado."""
        self.status = PetStatus.DOADO
        self.deactivation_date = date.today()

    def mark_as_lost(self) -> None:
        """Marca como perdido."""
        self.status = PetStatus.PERDIDO

    def update_vaccination(self, vaccination_date: date, expiry_date: date) -> None:
        """Atualiza vacinação."""
        self.is_vaccinated = True
        self.vaccination_date = vaccination_date
        self.vaccination_expiry = expiry_date

    def restrict_areas(self) -> None:
        """Restringe acesso a áreas comuns."""
        self.can_use_common_areas = False
        self.allowed_areas = []

    def allow_areas(self, areas: list = None) -> None:
        """Permite acesso a áreas comuns."""
        self.can_use_common_areas = True
        if areas:
            self.allowed_areas = areas

    @property
    def is_active(self) -> bool:
        """Verifica se está ativo."""
        return self.status == PetStatus.ATIVO

    @property
    def age(self) -> Optional[int]:
        """Calcula idade em anos."""
        if not self.birth_date:
            return None
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )

    @property
    def age_months(self) -> Optional[int]:
        """Calcula idade em meses."""
        if not self.birth_date:
            return None
        today = date.today()
        months = (today.year - self.birth_date.year) * 12
        months += today.month - self.birth_date.month
        if today.day < self.birth_date.day:
            months -= 1
        return max(0, months)

    @property
    def vaccination_status(self) -> str:
        """Status da vacinação."""
        if not self.is_vaccinated:
            return "nao_vacinado"
        if not self.vaccination_expiry:
            return "vacinado"
        today = date.today()
        if self.vaccination_expiry < today:
            return "vencida"
        days_remaining = (self.vaccination_expiry - today).days
        if days_remaining <= 30:
            return "vencendo"
        return "em_dia"

    @property
    def full_description(self) -> str:
        """Descrição completa do pet."""
        parts = [self.name]
        if self.breed:
            parts.append(f"({self.breed})")
        if self.color:
            parts.append(f"- {self.color}")
        return " ".join(parts)
