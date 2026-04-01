"""
Modelo GedClient — Clientes do módulo GED.

Representa condomínios, administradoras e demais tomadores de serviço
que recebem kits documentais mensais.
"""

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class GedClientType(StrEnum):
    """Tipo de cliente GED."""

    CONDOMINIO = "condominio"
    ADMINISTRADORA = "administradora"


class GedClient(Base):
    """Cliente que recebe kits documentais.

    Pode ser um condomínio ou uma administradora de condomínios.
    Possui acesso opcional ao portal do cliente para download de kits.
    """

    __tablename__ = "ged_clients"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Razão social ou nome do condomínio",
    )
    type: Mapped[str] = mapped_column(
        String(30),
        default=GedClientType.CONDOMINIO,
        nullable=False,
        index=True,
        comment="Tipo: condominio ou administradora",
    )
    cnpj: Mapped[str | None] = mapped_column(
        String(18),
        unique=True,
        nullable=True,
        index=True,
        comment="CNPJ formatado (XX.XXX.XXX/XXXX-XX)",
    )
    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Endereço completo do cliente",
    )
    contact_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Nome do contato principal (síndico/gerente)",
    )
    contact_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="E-mail principal para envio de kits",
    )
    contact_phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Telefone do contato principal",
    )

    # Google Drive integration
    google_drive_folder_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="ID da pasta no Google Drive para envio automático",
    )

    # Portal access
    portal_access_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Se o cliente pode acessar o portal para baixar kits",
    )
    portal_username: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
        comment="Login de acesso ao portal do cliente",
    )
    portal_password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Hash bcrypt da senha do portal",
    )

    # Audit
    created_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        comment="FK para users.id — quem cadastrou",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<GedClient(id={self.id}, name={self.name}, type={self.type})>"
