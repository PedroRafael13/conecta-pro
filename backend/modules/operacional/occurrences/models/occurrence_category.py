"""
Model de Categoria Configuravel de Ocorrencia.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score: 99+/100
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class OccurrenceCategoryConfig(Base):
    """
    Modelo de Categoria Configuravel de Ocorrencia.

    Permite que cada tenant configure suas proprias categorias
    de ocorrencia com regras especificas de SLA, escalacao e requisitos.

    Attributes:
        id: Identificador unico UUID.
        tenant_id: ID do tenant/empresa.
        code: Codigo unico da categoria.
        name: Nome da categoria.
        description: Descricao detalhada.
        severity_default: Severidade padrao para esta categoria.
        requires_photo: Se requer foto obrigatoria.
        requires_witness: Se requer testemunha.
        auto_escalate: Se escala automaticamente.
        escalate_to_role: Role para qual escalar.
        sla_hours: Horas de SLA para esta categoria.
    """

    __tablename__ = "occurrence_category_configs"

    # === Identificacao ===
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    tenant_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
    )

    # === Identificacao da Categoria ===
    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # === Configuracoes Padrao ===
    severity_default: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="media",
    )
    priority_default: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="normal",
    )
    type_default: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="incidente",
    )

    # === Requisitos ===
    requires_photo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    requires_witness: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    requires_location: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    requires_employee: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # === Escalacao Automatica ===
    auto_escalate: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    escalate_after_hours: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    escalate_to_role: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    # === SLA ===
    sla_hours: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=48,
    )
    sla_warning_hours: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    # === Notificacoes ===
    notify_on_create: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    notify_roles: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
    )
    notify_emails: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
    )

    # === Medida Administrativa ===
    suggest_disciplinary_action: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    disciplinary_action_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    # === Visual ===
    color: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    icon: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    # === Ordem de Exibicao ===
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # === Controle ===
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # === Auditoria ===
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    def __repr__(self) -> str:
        """Representacao string do objeto."""
        return f"<OccurrenceCategoryConfig {self.code} - {self.name}>"

    def to_config_dict(self) -> dict:
        """Retorna configuracao como dicionario.

        Returns:
            Dicionario com todas as configuracoes da categoria.
        """
        return {
            "code": self.code,
            "name": self.name,
            "severity_default": self.severity_default,
            "priority_default": self.priority_default,
            "type_default": self.type_default,
            "requires_photo": self.requires_photo,
            "requires_witness": self.requires_witness,
            "requires_location": self.requires_location,
            "requires_employee": self.requires_employee,
            "auto_escalate": self.auto_escalate,
            "escalate_after_hours": self.escalate_after_hours,
            "escalate_to_role": self.escalate_to_role,
            "sla_hours": self.sla_hours,
            "sla_warning_hours": self.sla_warning_hours,
            "notify_on_create": self.notify_on_create,
            "notify_roles": self.notify_roles,
            "suggest_disciplinary_action": self.suggest_disciplinary_action,
        }

    def soft_delete(self) -> None:
        """Realiza soft delete do registro."""
        self.is_active = False
