"""
Model para preferencias do Portal do Funcionario.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.database import Base


class PortalPreference(Base):
    """Preferencias do funcionario no portal.

    Attributes:
        id: Identificador unico.
        employee_id: FK para o funcionario.
        language: Idioma preferido (default pt-BR).
        theme: Tema visual (light/dark).
        notifications_enabled: Se deseja receber notificacoes.
        email_notifications: Se deseja receber por email.
        push_notifications: Se deseja receber push notifications.
        extra_settings: Configuracoes adicionais em JSON.
        created_at: Data/hora de criacao.
        updated_at: Data/hora da ultima atualizacao.
    """

    __tablename__ = "portal_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    language = Column(String(10), default="pt-BR", nullable=False)
    theme = Column(String(20), default="light", nullable=False)
    notifications_enabled = Column(Boolean, default=True, nullable=False)
    email_notifications = Column(Boolean, default=True, nullable=False)
    push_notifications = Column(Boolean, default=False, nullable=False)
    extra_settings = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
