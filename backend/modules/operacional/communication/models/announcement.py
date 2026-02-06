"""
Model de Comunicado Operacional.

Author: Conecta PRO Team
Date: 2026-01-18
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    from .announcement_read import AnnouncementRead


class AnnouncementTargetType(str, Enum):
    """Tipo de destinatario do comunicado."""
    ALL = "all"
    DEPARTMENT = "department"
    CLIENT = "client"
    POST = "post"
    EMPLOYEE = "employee"
    ROLE = "role"


class AnnouncementType(str, Enum):
    """Tipo de comunicado."""
    INFORMATIVO = "informativo"
    URGENTE = "urgente"
    ALERTA = "alerta"
    PROCEDIMENTO = "procedimento"
    ESCALA = "escala"


class AnnouncementCategory(str, Enum):
    """Categoria do comunicado."""
    INFORMATIVO = "informativo"
    PROCEDIMENTO = "procedimento"
    ALERTA = "alerta"
    TREINAMENTO = "treinamento"
    POLITICA = "politica"


class AnnouncementPriority(str, Enum):
    """Prioridade do comunicado."""
    BAIXA = "baixa"
    NORMAL = "normal"
    ALTA = "alta"
    URGENTE = "urgente"


class AnnouncementStatus(str, Enum):
    """Status do comunicado."""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    RASCUNHO = "rascunho"
    AGENDADO = "agendado"
    PUBLICADO = "publicado"
    ARQUIVADO = "arquivado"


class Announcement(Base):
    """Modelo de Comunicado."""

    __tablename__ = "communication_announcements"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(30), default=AnnouncementType.INFORMATIVO.value, nullable=False, index=True)
    prioridade: Mapped[str] = mapped_column(String(20), default=AnnouncementPriority.NORMAL.value, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default=AnnouncementStatus.RASCUNHO.value, nullable=False, index=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    resumo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    anexos: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True, default=list)
    destinatarios_tipo: Mapped[str] = mapped_column(String(30), default="todos", nullable=False)
    destinatarios_postos: Mapped[Optional[List[str]]] = mapped_column(ARRAY(UUID(as_uuid=False)), nullable=True)
    destinatarios_funcionarios: Mapped[Optional[List[str]]] = mapped_column(ARRAY(UUID(as_uuid=False)), nullable=True)
    data_publicacao: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    data_expiracao: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    requer_confirmacao: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    enviar_push: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    enviar_email: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    total_destinatarios: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_visualizacoes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_confirmacoes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fixado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    extra_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True, default=dict)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    reads: Mapped[List["AnnouncementRead"]] = relationship(
        "AnnouncementRead",
        back_populates="announcement",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Announcement {self.titulo[:50]}>"
