"""
Modelo Alert (Alerta em Tempo Real) para Comunicacao Operacional.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class AlertType(StrEnum):
    """Tipo de alerta."""

    OCORRENCIA_CRITICA = "ocorrencia_critica"  # Ocorrencia critica registrada
    SLA_VENCENDO = "sla_vencendo"  # SLA prestes a vencer
    FALTA_DETECTADA = "falta_detectada"  # Falta de funcionario detectada
    POSTO_DESCOBERTO = "posto_descoberto"  # Posto sem cobertura
    SUBSTITUICAO_URGENTE = "substituicao_urgente"  # Substituicao urgente necessaria
    EQUIPAMENTO_FALHA = "equipamento_falha"  # Falha em equipamento
    ACESSO_NEGADO = "acesso_negado"  # Tentativa de acesso negada
    INVASAO_DETECTADA = "invasao_detectada"  # Deteccao de invasao
    PANICO_ACIONADO = "panico_acionado"  # Botao de panico acionado
    CERCA_VIRTUAL = "cerca_virtual"  # Violacao de cerca virtual
    SISTEMA = "sistema"  # Alerta do sistema


class AlertSeverity(StrEnum):
    """Severidade do alerta."""

    INFO = "info"  # Informativo
    WARNING = "warning"  # Aviso
    ERROR = "error"  # Erro
    CRITICAL = "critical"  # Critico


class Alert(Base):
    """
    Modelo de Alerta em Tempo Real.

    Representa alertas criticos enviados via WebSocket para usuarios.
    Suporta multiplos destinatarios por usuario ou role.

    Attributes:
        id: Identificador unico (UUID)
        tenant_id: ID do tenant (multi-tenancy)
        alert_type: Tipo do alerta
        severity: Severidade do alerta
        title: Titulo do alerta
        message: Mensagem detalhada
        reference_type: Tipo da entidade referenciada
        reference_id: ID da entidade referenciada
        target_users: Lista de IDs de usuarios destinatarios
        target_roles: Lista de roles destinatarias
        acknowledged_by: Lista de usuarios que confirmaram
        expires_at: Data/hora de expiracao
        is_active: Se o alerta esta ativo
        created_at: Data de criacao

    Example:
        >>> alert = Alert(
        ...     tenant_id="tenant-123",
        ...     alert_type=AlertType.OCORRENCIA_CRITICA,
        ...     severity=AlertSeverity.CRITICAL,
        ...     title="Ocorrencia Critica Registrada",
        ...     message="Uma ocorrencia de alta prioridade foi registrada.",
        ...     reference_type="occurrence",
        ...     reference_id="occurrence-789",
        ...     target_roles=["supervisor", "gerente"],
        ... )
    """

    __tablename__ = "communication_alerts"

    # Identificacao
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

    # Classificacao
    alert_type: Mapped[str] = mapped_column(
        String(50),
        default=AlertType.SISTEMA.value,
        nullable=False,
        index=True,
    )
    severity: Mapped[str] = mapped_column(
        String(20),
        default=AlertSeverity.INFO.value,
        nullable=False,
        index=True,
    )

    # Conteudo
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # Referencia (entidade relacionada)
    reference_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="Tipo da entidade referenciada (occurrence, post, etc)",
    )
    reference_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
        comment="ID da entidade referenciada",
    )

    # Destinatarios
    target_users: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="Lista de UUIDs de usuarios destinatarios",
    )
    target_roles: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="Lista de roles destinatarias",
    )

    # Confirmacao
    acknowledged_by: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="Lista de usuarios que confirmaram o alerta",
    )

    # Expiracao
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Data/hora de expiracao do alerta",
    )

    # Controle
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Representacao string do alerta."""
        return f"<Alert {self.id[:8]}... [{self.severity}] - {self.title[:30]}>"

    @property
    def is_critical(self) -> bool:
        """Verifica se o alerta e critico."""
        return self.severity == AlertSeverity.CRITICAL.value

    @property
    def is_expired(self) -> bool:
        """Verifica se o alerta esta expirado."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def acknowledgment_count(self) -> int:
        """Retorna quantidade de confirmacoes."""
        if self.acknowledged_by is None:
            return 0
        return len(self.acknowledged_by)

    @property
    def is_fully_acknowledged(self) -> bool:
        """
        Verifica se todos os destinatarios confirmaram.

        Returns:
            True se todos confirmaram ou se nao ha destinatarios especificos
        """
        if not self.target_users:
            return self.acknowledgment_count > 0
        return set(self.target_users or []).issubset(set(self.acknowledged_by or []))

    def acknowledge(self, user_id: str) -> bool:
        """
        Registra confirmacao de um usuario.

        Args:
            user_id: ID do usuario que confirma

        Returns:
            True se a confirmacao foi registrada (nova)
        """
        if self.acknowledged_by is None:
            self.acknowledged_by = []

        if user_id not in self.acknowledged_by:
            self.acknowledged_by.append(user_id)
            return True
        return False

    def is_acknowledged_by(self, user_id: str) -> bool:
        """
        Verifica se um usuario especifico confirmou o alerta.

        Args:
            user_id: ID do usuario

        Returns:
            True se o usuario confirmou
        """
        return self.acknowledged_by is not None and user_id in self.acknowledged_by

    def is_target_user(self, user_id: str) -> bool:
        """
        Verifica se um usuario e destinatario do alerta.

        Args:
            user_id: ID do usuario

        Returns:
            True se o usuario e destinatario
        """
        # Se nao ha usuarios especificos, todos sao destinatarios
        if not self.target_users:
            return True
        return user_id in self.target_users

    def is_target_role(self, role: str) -> bool:
        """
        Verifica se uma role e destinataria do alerta.

        Args:
            role: Nome da role

        Returns:
            True se a role e destinataria
        """
        # Se nao ha roles especificas, todas sao destinatarias
        if not self.target_roles:
            return True
        return role in self.target_roles

    def add_target_user(self, user_id: str) -> None:
        """
        Adiciona um usuario como destinatario.

        Args:
            user_id: ID do usuario
        """
        if self.target_users is None:
            self.target_users = []
        if user_id not in self.target_users:
            self.target_users.append(user_id)

    def add_target_role(self, role: str) -> None:
        """
        Adiciona uma role como destinataria.

        Args:
            role: Nome da role
        """
        if self.target_roles is None:
            self.target_roles = []
        if role not in self.target_roles:
            self.target_roles.append(role)

    @classmethod
    def create_critical(
        cls,
        tenant_id: str,
        title: str,
        message: str,
        alert_type: AlertType = AlertType.SISTEMA,
        reference_type: str | None = None,
        reference_id: str | None = None,
        target_roles: list[str] | None = None,
        target_users: list[str] | None = None,
        expires_in_minutes: int = 60,
    ) -> Alert:
        """
        Factory method para criar alerta critico.

        Args:
            tenant_id: ID do tenant
            title: Titulo do alerta
            message: Mensagem detalhada
            alert_type: Tipo do alerta
            reference_type: Tipo da referencia
            reference_id: ID da referencia
            target_roles: Roles destinatarias
            target_users: Usuarios destinatarios
            expires_in_minutes: Minutos ate expirar

        Returns:
            Nova instancia de Alert com severidade CRITICAL
        """
        from datetime import timedelta

        return cls(
            tenant_id=tenant_id,
            alert_type=alert_type.value,
            severity=AlertSeverity.CRITICAL.value,
            title=title,
            message=message,
            reference_type=reference_type,
            reference_id=reference_id,
            target_roles=target_roles or [],
            target_users=target_users or [],
            expires_at=datetime.utcnow() + timedelta(minutes=expires_in_minutes),
        )

    @classmethod
    def create_warning(
        cls,
        tenant_id: str,
        title: str,
        message: str,
        alert_type: AlertType = AlertType.SISTEMA,
        reference_type: str | None = None,
        reference_id: str | None = None,
        target_roles: list[str] | None = None,
        expires_in_minutes: int = 120,
    ) -> Alert:
        """
        Factory method para criar alerta de aviso.

        Args:
            tenant_id: ID do tenant
            title: Titulo do alerta
            message: Mensagem detalhada
            alert_type: Tipo do alerta
            reference_type: Tipo da referencia
            reference_id: ID da referencia
            target_roles: Roles destinatarias
            expires_in_minutes: Minutos ate expirar

        Returns:
            Nova instancia de Alert com severidade WARNING
        """
        from datetime import timedelta

        return cls(
            tenant_id=tenant_id,
            alert_type=alert_type.value,
            severity=AlertSeverity.WARNING.value,
            title=title,
            message=message,
            reference_type=reference_type,
            reference_id=reference_id,
            target_roles=target_roles or [],
            expires_at=datetime.utcnow() + timedelta(minutes=expires_in_minutes),
        )

    def to_websocket_message(self) -> dict:
        """
        Converte o alerta para formato de mensagem WebSocket.

        Returns:
            Dicionario com dados do alerta para WebSocket
        """
        return {
            "type": "alert",
            "data": {
                "id": self.id,
                "alert_type": self.alert_type,
                "severity": self.severity,
                "title": self.title,
                "message": self.message,
                "reference_type": self.reference_type,
                "reference_id": self.reference_id,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            },
        }
