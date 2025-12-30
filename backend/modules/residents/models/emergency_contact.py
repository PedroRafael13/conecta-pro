"""Modelo de Contato de Emergência do Morador."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.residents.models.resident import Resident


class ContactRelationship(str, Enum):
    """Tipo de relacionamento do contato."""

    FAMILIAR = "familiar"
    AMIGO = "amigo"
    VIZINHO = "vizinho"
    COLEGA_TRABALHO = "colega_trabalho"
    MEDICO = "medico"
    ADVOGADO = "advogado"
    SINDICO = "sindico"
    ADMINISTRADOR = "administrador"
    OUTRO = "outro"


class ResidentEmergencyContact(Base):
    """Modelo de Contato de Emergência do Morador."""

    __tablename__ = "resident_emergency_contacts"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Relacionamento com morador
    resident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("residents.id"), nullable=False, index=True
    )

    # Dados do contato
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    relationship: Mapped[ContactRelationship] = mapped_column(
        String(30), default=ContactRelationship.FAMILIAR
    )
    relationship_description: Mapped[Optional[str]] = mapped_column(String(100))

    # Contato
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    phone_secondary: Mapped[Optional[str]] = mapped_column(String(20))
    whatsapp: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(200))

    # Endereço
    address: Mapped[Optional[str]] = mapped_column(String(500))
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(2))

    # Prioridade
    priority: Mapped[int] = mapped_column(Integer, default=1)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Observações
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Auditoria
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relacionamentos
    resident: Mapped["Resident"] = relationship(
        "Resident", back_populates="emergency_contacts"
    )

    def set_as_primary(self) -> None:
        """Define como contato principal."""
        self.is_primary = True
        self.priority = 1

    def deactivate(self) -> None:
        """Desativa o contato."""
        self.is_active = False
        self.is_primary = False

    def activate(self) -> None:
        """Ativa o contato."""
        self.is_active = True

    @property
    def full_contact_info(self) -> str:
        """Informações completas de contato."""
        parts = [self.name]
        if self.phone:
            parts.append(f"Tel: {self.phone}")
        if self.whatsapp and self.whatsapp != self.phone:
            parts.append(f"WhatsApp: {self.whatsapp}")
        return " | ".join(parts)

    @property
    def relationship_display(self) -> str:
        """Exibição do relacionamento."""
        relationship_map = {
            ContactRelationship.FAMILIAR: "Familiar",
            ContactRelationship.AMIGO: "Amigo(a)",
            ContactRelationship.VIZINHO: "Vizinho(a)",
            ContactRelationship.COLEGA_TRABALHO: "Colega de Trabalho",
            ContactRelationship.MEDICO: "Médico(a)",
            ContactRelationship.ADVOGADO: "Advogado(a)",
            ContactRelationship.SINDICO: "Síndico(a)",
            ContactRelationship.ADMINISTRADOR: "Administrador(a)",
            ContactRelationship.OUTRO: "Outro",
        }
        base = relationship_map.get(self.relationship, "Outro")
        if self.relationship_description:
            return f"{base} - {self.relationship_description}"
        return base
