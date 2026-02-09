"""
IntegrationSettings Model - Configurações de Integração
Sprint 30: Cadastro de Clientes/Condomínios
"""

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from core.database import Base

if TYPE_CHECKING:
    from modules.clients.models.client import Client


class IntegrationType(StrEnum):
    """Tipo de integração."""

    GUARDIAN = "guardian"
    PLUS = "plus"
    ERP_EXTERNO = "erp_externo"
    CONTABILIDADE = "contabilidade"
    BANCO = "banco"
    NFE = "nfe"
    WEBHOOK = "webhook"
    API = "api"
    OUTRO = "outro"


class SyncStatus(StrEnum):
    """Status de sincronização."""

    PENDENTE = "pendente"
    SINCRONIZANDO = "sincronizando"
    SINCRONIZADO = "sincronizado"
    ERRO = "erro"
    DESABILITADO = "desabilitado"


class SyncDirection(StrEnum):
    """Direção da sincronização."""

    ERP_TO_EXTERNAL = "erp_to_external"
    EXTERNAL_TO_ERP = "external_to_erp"
    BIDIRECTIONAL = "bidirectional"


class IntegrationSettings(Base):
    """
    Model de Configurações de Integração.

    Armazena configurações de integração entre o ERP e sistemas externos
    (Guardian, Plus, ERPs de terceiros, etc.) para cada cliente.
    """

    __tablename__ = "integration_settings"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)

    # Tipo de integração
    integration_type = Column(Enum(IntegrationType), nullable=False, default=IntegrationType.GUARDIAN)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)

    # Status
    sync_status = Column(Enum(SyncStatus), nullable=False, default=SyncStatus.PENDENTE)
    sync_direction = Column(Enum(SyncDirection), nullable=False, default=SyncDirection.BIDIRECTIONAL)

    # Credenciais (criptografadas)
    api_url = Column(String(500), nullable=True)
    api_key = Column(String(500), nullable=True)
    api_secret = Column(String(500), nullable=True)
    username = Column(String(100), nullable=True)
    password_hash = Column(String(500), nullable=True)
    token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)

    # IDs externos
    external_client_id = Column(String(100), nullable=True)
    external_tenant_id = Column(String(100), nullable=True)

    # Webhook
    webhook_url = Column(String(500), nullable=True)
    webhook_secret = Column(String(200), nullable=True)
    webhook_events = Column(JSONB, nullable=True, default=list)

    # Configurações de sincronização
    sync_interval_minutes = Column(Integer, nullable=True, default=15)
    sync_batch_size = Column(Integer, nullable=True, default=100)
    retry_attempts = Column(Integer, nullable=True, default=3)
    retry_delay_seconds = Column(Integer, nullable=True, default=60)

    # Mapeamento de campos
    field_mapping = Column(JSONB, nullable=True, default=dict)
    entity_mapping = Column(JSONB, nullable=True, default=dict)

    # Filtros
    sync_filters = Column(JSONB, nullable=True, default=dict)
    excluded_entities = Column(JSONB, nullable=True, default=list)

    # Estatísticas
    last_sync_at = Column(DateTime, nullable=True)
    last_sync_success_at = Column(DateTime, nullable=True)
    last_sync_error_at = Column(DateTime, nullable=True)
    last_sync_error = Column(Text, nullable=True)
    total_syncs = Column(Integer, nullable=False, default=0)
    successful_syncs = Column(Integer, nullable=False, default=0)
    failed_syncs = Column(Integer, nullable=False, default=0)
    records_synced = Column(Integer, nullable=False, default=0)

    # Configurações extras
    settings = Column(JSONB, nullable=True, default=dict)
    notes = Column(Text, nullable=True)

    # Flags
    is_active = Column(Boolean, nullable=False, default=True)
    is_enabled = Column(Boolean, nullable=False, default=False)
    auto_sync = Column(Boolean, nullable=False, default=True)
    sync_on_change = Column(Boolean, nullable=False, default=True)

    # Auditoria
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relacionamentos
    client: "Client" = relationship("Client", back_populates="integration_settings")

    # Índices
    __table_args__ = (
        Index("ix_integration_settings_client_type", "client_id", "integration_type"),
        Index("ix_integration_settings_status", "sync_status"),
        Index("ix_integration_settings_external", "external_client_id"),
    )

    def __repr__(self) -> str:
        return f"<IntegrationSettings(id={self.id}, type={self.integration_type}, client_id={self.client_id})>"

    @property
    def is_guardian(self) -> bool:
        """Verifica se é integração Guardian."""
        return self.integration_type == IntegrationType.GUARDIAN

    @property
    def is_plus(self) -> bool:
        """Verifica se é integração Plus."""
        return self.integration_type == IntegrationType.PLUS

    @property
    def is_configured(self) -> bool:
        """Verifica se está configurado."""
        if self.integration_type in (IntegrationType.GUARDIAN, IntegrationType.PLUS):
            return bool(self.api_url and self.api_key)
        if self.integration_type == IntegrationType.WEBHOOK:
            return bool(self.webhook_url)
        return bool(self.api_url)

    @property
    def is_token_expired(self) -> bool:
        """Verifica se o token está expirado."""
        if not self.token_expires_at:
            return False
        return datetime.utcnow() > self.token_expires_at

    @property
    def success_rate(self) -> float:
        """Taxa de sucesso das sincronizações."""
        if self.total_syncs == 0:
            return 0.0
        return (self.successful_syncs / self.total_syncs) * 100

    @property
    def needs_sync(self) -> bool:
        """Verifica se precisa sincronizar."""
        if not self.is_enabled or not self.auto_sync:
            return False
        if not self.last_sync_at:
            return True
        if not self.sync_interval_minutes:
            return False
        minutes_since_sync = (datetime.utcnow() - self.last_sync_at).total_seconds() / 60
        return minutes_since_sync >= self.sync_interval_minutes

    def enable(self) -> None:
        """Habilita a integração."""
        self.is_enabled = True
        self.sync_status = SyncStatus.PENDENTE
        self.updated_at = datetime.utcnow()

    def disable(self) -> None:
        """Desabilita a integração."""
        self.is_enabled = False
        self.sync_status = SyncStatus.DESABILITADO
        self.updated_at = datetime.utcnow()

    def start_sync(self) -> None:
        """Marca início da sincronização."""
        self.sync_status = SyncStatus.SINCRONIZANDO
        self.last_sync_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def complete_sync(self, records_count: int = 0) -> None:
        """Marca sincronização como concluída."""
        self.sync_status = SyncStatus.SINCRONIZADO
        self.last_sync_success_at = datetime.utcnow()
        self.total_syncs += 1
        self.successful_syncs += 1
        self.records_synced += records_count
        self.last_sync_error = None
        self.updated_at = datetime.utcnow()

    def fail_sync(self, error: str) -> None:
        """Marca sincronização como falha."""
        self.sync_status = SyncStatus.ERRO
        self.last_sync_error_at = datetime.utcnow()
        self.last_sync_error = error
        self.total_syncs += 1
        self.failed_syncs += 1
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

    def set_token(self, token: str, expires_at: datetime | None = None) -> None:
        """Define token de autenticação."""
        self.token = token
        self.token_expires_at = expires_at
        self.updated_at = datetime.utcnow()

    def set_webhook(self, url: str, secret: str | None = None, events: list | None = None) -> None:
        """Configura webhook."""
        self.webhook_url = url
        self.webhook_secret = secret
        self.webhook_events = events or []
        self.updated_at = datetime.utcnow()

    def set_external_ids(self, client_id: str | None = None, tenant_id: str | None = None) -> None:
        """Define IDs externos."""
        if client_id:
            self.external_client_id = client_id
        if tenant_id:
            self.external_tenant_id = tenant_id
        self.updated_at = datetime.utcnow()

    def update_field_mapping(self, mapping: dict) -> None:
        """Atualiza mapeamento de campos."""
        self.field_mapping = mapping
        self.updated_at = datetime.utcnow()

    def update_entity_mapping(self, mapping: dict) -> None:
        """Atualiza mapeamento de entidades."""
        self.entity_mapping = mapping
        self.updated_at = datetime.utcnow()

    def update_sync_config(
        self,
        interval_minutes: int | None = None,
        batch_size: int | None = None,
        retry_attempts: int | None = None,
        retry_delay: int | None = None,
    ) -> None:
        """Atualiza configurações de sincronização."""
        if interval_minutes is not None:
            self.sync_interval_minutes = interval_minutes
        if batch_size is not None:
            self.sync_batch_size = batch_size
        if retry_attempts is not None:
            self.retry_attempts = retry_attempts
        if retry_delay is not None:
            self.retry_delay_seconds = retry_delay
        self.updated_at = datetime.utcnow()

    def reset_stats(self) -> None:
        """Reseta estatísticas."""
        self.total_syncs = 0
        self.successful_syncs = 0
        self.failed_syncs = 0
        self.records_synced = 0
        self.last_sync_at = None
        self.last_sync_success_at = None
        self.last_sync_error_at = None
        self.last_sync_error = None
        self.updated_at = datetime.utcnow()
