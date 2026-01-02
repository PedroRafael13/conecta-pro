"""
Modelo SQLAlchemy para Técnicos de Campo - CAMPO Service
Guardian Unified v3.0.0 - Módulo 9
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class CampoTecnico(Base):
    """
    Modelo para técnicos de campo do sistema CAMPO.

    Representa técnicos que prestam suporte em campo para
    instalação, manutenção e suporte técnico.
    """

    __tablename__ = "campo_tecnicos"
    __table_args__ = {"schema": "guardian"}

    # Campos principais
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        comment="ID único do técnico"
    )

    nome: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Nome completo do técnico"
    )

    documento: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="CPF ou documento de identificação"
    )

    telefone: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="Telefone de contato"
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="Email de contato"
    )

    especialidade: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment="Especialidade técnica (ex: Instalação, Manutenção)"
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="ativo",
        comment="Status do técnico (ativo, inativo, ocupado)"
    )

    localizacao_atual: Mapped[Optional[dict]] = mapped_column(
        JSON,
        comment="Localização GPS atual do técnico"
    )

    ultima_atividade: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        comment="Timestamp da última atividade"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        comment="Data de criação do registro"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="Data da última atualização"
    )

    def __repr__(self):
        return f"<CampoTecnico(id={self.id}, nome={self.nome}, status={self.status})>"

    def to_dict(self):
        """Converte o modelo para dicionário."""
        return {
            "id": self.id,
            "name": self.nome,
            "document": self.documento,
            "phone": self.telefone,
            "email": self.email,
            "specialty": self.especialidade,
            "status": self.status,
            "current_location": self.localizacao_atual,
            "ultima_atividade": (
                self.ultima_atividade.isoformat() if self.ultima_atividade else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
