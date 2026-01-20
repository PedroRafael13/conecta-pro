"""
Modelo Area (Área Física) para Facilities.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base
from modules.facilities.models.maintenance import MaintenanceStatus

if TYPE_CHECKING:
    from .checklist import Checklist
    from .inspection import Inspection
    from .maintenance import Maintenance
    from .service_request import ServiceRequest


class AreaType(str, Enum):
    """Tipo de área."""

    COMUM = "comum"  # Área comum (salão, piscina)
    PRIVATIVA = "privativa"  # Área privativa
    TECNICA = "tecnica"  # Área técnica (casa de máquinas)
    EXTERNA = "externa"  # Área externa (jardim, estacionamento)
    ADMINISTRATIVA = "administrativa"  # Área administrativa
    SEGURANCA = "seguranca"  # Portaria, guarita
    SERVICO = "servico"  # Área de serviço


class AreaStatus(str, Enum):
    """Status da área."""

    ACTIVE = "active"  # Ativa e operacional
    INACTIVE = "inactive"  # Desativada
    MAINTENANCE = "maintenance"  # Em manutenção
    RENOVATION = "renovation"  # Em reforma
    RESTRICTED = "restricted"  # Acesso restrito


class Area(Base):
    """
    Modelo de Área Física.

    Representa uma área física de um condomínio ou cliente.

    Attributes:
        id: Identificador único
        code: Código da área (AREA-001)
        name: Nome da área
        description: Descrição detalhada
        area_type: Tipo de área
        status: Status da área
        parent_id: Área pai (hierarquia)
        client_id: Cliente associado
        condominium_id: Condomínio associado
        floor: Andar/Pavimento
        building: Bloco/Prédio
        area_m2: Área em metros quadrados
        capacity: Capacidade de pessoas
        location_details: Detalhes de localização
        latitude: Latitude GPS
        longitude: Longitude GPS
        equipment: Equipamentos na área
        access_restrictions: Restrições de acesso
        responsible_id: Responsável pela área
        last_inspection_date: Data última inspeção
        next_inspection_date: Data próxima inspeção
    """

    __tablename__ = "areas"

    # Identificação
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Tipo e Status
    area_type: Mapped[str] = mapped_column(
        String(50),
        default=AreaType.COMUM.value,
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default=AreaStatus.ACTIVE.value,
        nullable=False,
        index=True,
    )

    # Hierarquia
    parent_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("areas.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relacionamentos externos
    client_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    condominium_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )

    # Localização física
    floor: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    building: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    area_m2: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    location_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Coordenadas GPS
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Detalhes (JSON)
    equipment: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    access_restrictions: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    extra_metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Responsável
    responsible_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # Datas de inspeção
    last_inspection_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_inspection_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Configurações
    requires_reservation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_rentable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rental_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Campos de controle
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # Relacionamentos
    parent: Mapped[Optional["Area"]] = relationship(
        "Area",
        remote_side=[id],
        back_populates="children",
        lazy="selectin",
    )
    children: Mapped[List["Area"]] = relationship(
        "Area",
        back_populates="parent",
        lazy="selectin",
    )
    maintenances: Mapped[List["Maintenance"]] = relationship(
        "Maintenance",
        back_populates="area",
        lazy="selectin",
    )
    inspections: Mapped[List["Inspection"]] = relationship(
        "Inspection",
        back_populates="area",
        lazy="selectin",
    )
    checklists: Mapped[List["Checklist"]] = relationship(
        "Checklist",
        back_populates="area",
        lazy="selectin",
    )
    service_requests: Mapped[List["ServiceRequest"]] = relationship(
        "ServiceRequest",
        back_populates="area",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Area {self.code} - {self.name}>"

    @property
    def is_available(self) -> bool:
        """Verifica se a área está disponível para uso."""
        return self.status == AreaStatus.ACTIVE.value and self.is_active

    @property
    def needs_inspection(self) -> bool:
        """Verifica se a área precisa de inspeção."""
        if not self.next_inspection_date:
            return True
        return datetime.now() >= self.next_inspection_date

    @property
    def has_pending_maintenance(self) -> bool:
        """Verifica se há manutenção pendente."""
        return any(
            m.status
            in (
                MaintenanceStatus.PENDING.value,
                MaintenanceStatus.IN_PROGRESS.value,
            )
            for m in self.maintenances
        )

    @property
    def child_count(self) -> int:
        """Retorna quantidade de subáreas."""
        return len(self.children) if self.children else 0
