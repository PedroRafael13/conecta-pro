"""
IntegrationSettings Model - Configurações de Integração
Sprint 30: Cadastro de Clientes/Condomínios

NOTA: Este model foi sincronizado com o banco de dados real em 29/03/2026.
Colunas correspondem EXATAMENTE ao schema da tabela integration_settings.
"""

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.clients.models.client import Client


class IntegrationType(StrEnum):
    """Tipo de integração."""

    GUARDIAN = "guardian"
    PLUS = "plus"
    ERP_EXTERNAL = "erp_external"
    BANKING = "banking"
    NFE = "nfe"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"


class SyncStatus(StrEnum):
    """Status de sincronização."""

    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    ERROR = "error"
    DISABLED = "disabled"


class SyncDirection(StrEnum):
    """Direção de sincronização."""

    PUSH = "push"
    PULL = "pull"
    BIDIRECTIONAL = "bidirectional"


class IntegrationSettings(Base):
    """
    Model de Configurações de Integração — sincronizado com banco real.

    Armazena configurações de integração entre o ERP e sistemas externos
    (Guardian, Plus, ERPs de terceiros, etc.) para cada cliente.
    """

    __tablename__ = "integration_settings"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    condominium_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Tipo de integração — string, não enum SQLAlchemy
    integration_type = Column("integration_type", String(30), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Status
    enabled = Column(Boolean, nullable=False, default=False, index=True)
    sync_status = Column("sync_status", String(30), nullable=False, default="pending")
    sync_direction = Column("sync_direction", String(30), nullable=False, default="bidirectional")

    # Credenciais
    api_url = Column(String(500), nullable=True)
    api_key = Column(String(255), nullable=True)
    api_secret = Column(String(255), nullable=True)
    api_token = Column(Text, nullable=True)
    api_version = Column(String(20), nullable=True)

    # Auth
    auth_type = Column(String(50), nullable=True)
    auth_config = Column(JSONB, nullable=True)

    # Webhook
    webhook_url = Column(String(500), nullable=True)
    webhook_secret = Column(String(255), nullable=True)
    webhook_events = Column(ARRAY(String), nullable=True)

    # Sincronização
    sync_interval_minutes = Column(Integer, nullable=True)
    last_sync_at = Column(DateTime, nullable=True)
    next_sync_at = Column(DateTime, nullable=True)
    last_sync_status = Column(String(50), nullable=True)
    last_sync_message = Column(Text, nullable=True)
    sync_config = Column(JSONB, nullable=True)

    # IDs externos
    external_client_id = Column(String(100), nullable=True)
    external_config = Column(JSONB, nullable=True)

    # Metadata
    notes = Column(Text, nullable=True)
    extra_metadata = Column("metadata", JSONB, nullable=True)

    # Flags — banco usa 'ativo' não 'is_active'
    ativo = Column(Boolean, nullable=False, default=True)

    # Auditoria
    created_at = Column(DateTime, nullable=False, server_default="now()")
    updated_at = Column(DateTime, nullable=False, server_default="now()", onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relacionamentos
    client: "Client" = relationship("Client", back_populates="integration_settings")

    def __repr__(self) -> str:
        return f"<IntegrationSettings(id={self.id}, type={self.integration_type}, client_id={self.client_id})>"

    # Properties computadas (não são colunas)
    @property
    def is_active(self) -> bool:
        """Alias para ativo."""
        return bool(self.ativo)

    @property
    def is_enabled(self) -> bool:
        """Alias para enabled."""
        return bool(self.enabled)

    @property
    def is_configured(self) -> bool:
        """Verifica se está configurado."""
        return bool(self.api_url and (self.api_key or self.api_token))

    @property
    def success_rate(self) -> float:
        """Taxa de sucesso — placeholder."""
        return 0.0

    @property
    def total_syncs(self) -> int:
        """Total de sincs — placeholder."""
        return 0

    @property
    def records_synced(self) -> int:
        """Registros sincronizados — placeholder."""
        return 0

    @property
    def last_sync_success_at(self) -> datetime | None:
        """Última sinc com sucesso."""
        if self.last_sync_status == "success" and self.last_sync_at:
            return self.last_sync_at
        return None

    @property
    def last_sync_error(self) -> str | None:
        """Último erro de sinc."""
        if self.last_sync_status == "error":
            return self.last_sync_message
        return None

    @property
    def auto_sync(self) -> bool:
        """Verifica se auto-sync está habilitado."""
        if self.sync_config and isinstance(self.sync_config, dict):
            return self.sync_config.get("auto_sync", False)
        return False

    @property
    def is_plus(self) -> bool:
        """Verifica se é integração Plus."""
        return self.integration_type == "plus"

    def enable_integration(self) -> None:
        """Habilita a integração."""
        self.enabled = True
        self.sync_status = "pending"
        self.updated_at = datetime.utcnow()

    def disable_integration(self) -> None:
        """Desabilita a integração."""
        self.enabled = False
        self.sync_status = "disabled"
        self.updated_at = datetime.utcnow()

    def start_sync(self) -> None:
        """Marca início da sincronização."""
        self.sync_status = "syncing"
        self.last_sync_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def complete_sync(self, message: str | None = None) -> None:
        """Marca sincronização como concluída."""
        self.sync_status = "synced"
        self.last_sync_status = "success"
        self.last_sync_message = message
        self.updated_at = datetime.utcnow()

    def fail_sync(self, error: str) -> None:
        """Marca sincronização como falha."""
        self.sync_status = "error"
        self.last_sync_status = "error"
        self.last_sync_message = error
        self.updated_at = datetime.utcnow()

    def set_credentials(
        self, api_url: str | None = None, api_key: str | None = None, api_secret: str | None = None
    ) -> None:
        """Define credenciais."""
        if api_url:
            self.api_url = api_url
        if api_key:
            self.api_key = api_key
        if api_secret:
            self.api_secret = api_secret
        self.updated_at = datetime.utcnow()

    def set_token(self, token: str) -> None:
        """Define token de autenticação."""
        self.api_token = token
        self.updated_at = datetime.utcnow()

    def set_webhook(self, url: str, secret: str | None = None, events: list | None = None) -> None:
        """Configura webhook."""
        self.webhook_url = url
        self.webhook_secret = secret
        self.webhook_events = events or []
        self.updated_at = datetime.utcnow()

    def set_external_ids(self, client_id: str | None = None) -> None:
        """Define IDs externos."""
        if client_id:
            self.external_client_id = client_id
        self.updated_at = datetime.utcnow()
