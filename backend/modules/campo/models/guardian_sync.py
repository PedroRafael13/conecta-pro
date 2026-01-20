"""
Modelo GuardianSync para controle de sincronização.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class SyncStatus(str, Enum):
    """Status da sincronização."""

    PENDING = "pending"  # Aguardando envio
    IN_PROGRESS = "in_progress"  # Em andamento
    COMPLETED = "completed"  # Concluída com sucesso
    FAILED = "failed"  # Falhou
    PARTIAL = "partial"  # Parcialmente concluída
    CANCELLED = "cancelled"  # Cancelada


class SyncDirection(str, Enum):
    """Direção da sincronização."""

    ERP_TO_GUARDIAN = "erp_to_guardian"  # ERP envia para Guardian
    GUARDIAN_TO_ERP = "guardian_to_erp"  # Guardian envia para ERP
    BIDIRECTIONAL = "bidirectional"  # Ambas direções


class SyncEntityType(str, Enum):
    """Tipo de entidade sincronizada."""

    # ERP -> Guardian
    CONTRACT = "contract"  # Contratos
    CLIENT = "client"  # Clientes
    POST = "post"  # Postos
    EMPLOYEE = "employee"  # Funcionários
    ACCESS_CONFIG = "access_config"  # Configurações de acesso
    AUTHORIZED_PERSON = "authorized_person"  # Moradores/visitantes autorizados

    # Guardian -> ERP
    OCCURRENCE = "occurrence"  # Ocorrências
    ACCESS_LOG = "access_log"  # Logs de acesso
    EVENT_MEDIA = "event_media"  # Fotos/vídeos
    EQUIPMENT_STATUS = "equipment_status"  # Status de equipamentos
    ATTENDANCE_REPORT = "attendance_report"  # Relatórios de atendimento


class GuardianSync(Base):
    """
    Modelo de Sincronização com Guardian.

    Registra todas as sincronizações entre ERP e Conecta Guardian,
    permitindo rastreabilidade e retentativas em caso de falha.

    Attributes:
        id: Identificador único
        sync_code: Código único da sincronização
        direction: Direção (ERP->Guardian ou Guardian->ERP)
        entity_type: Tipo de entidade sincronizada
        entity_id: ID da entidade no sistema origem
        external_id: ID da entidade no sistema destino
        status: Status atual da sincronização
        client_id: ID do cliente relacionado
        contract_id: ID do contrato relacionado
        payload: Dados enviados/recebidos
        response: Resposta do sistema destino
        error_message: Mensagem de erro (se houver)
        retry_count: Número de tentativas
        last_retry_at: Data da última tentativa
        synced_at: Data da sincronização bem-sucedida
    """

    __tablename__ = "guardian_syncs"

    # Identificação
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    sync_code: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        index=True,
    )

    # Tipo e Direção
    direction: Mapped[str] = mapped_column(
        String(30),
        default=SyncDirection.ERP_TO_GUARDIAN.value,
        nullable=False,
        index=True,
    )
    entity_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )

    # Referências
    entity_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    external_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default=SyncStatus.PENDING.value,
        nullable=False,
        index=True,
    )

    # Relacionamentos com outras entidades
    client_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )
    contract_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )
    post_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )

    # Dados
    payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    response: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Retentativas
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    last_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timestamps
    synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
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
        String(36),
        nullable=True,
    )

    # Metadados
    metadata_extra: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        """Representação textual."""
        return f"<GuardianSync {self.sync_code} {self.entity_type} {self.status}>"

    @property
    def is_completed(self) -> bool:
        """Verifica se a sincronização foi concluída."""
        return self.status == SyncStatus.COMPLETED.value

    @property
    def is_failed(self) -> bool:
        """Verifica se a sincronização falhou."""
        return self.status == SyncStatus.FAILED.value

    @property
    def can_retry(self) -> bool:
        """Verifica se pode tentar novamente."""
        return (
            self.status == SyncStatus.FAILED.value
            and self.retry_count < self.max_retries
        )

    @property
    def is_outbound(self) -> bool:
        """Verifica se é sincronização de saída (ERP -> Guardian)."""
        return self.direction == SyncDirection.ERP_TO_GUARDIAN.value

    @property
    def is_inbound(self) -> bool:
        """Verifica se é sincronização de entrada (Guardian -> ERP)."""
        return self.direction == SyncDirection.GUARDIAN_TO_ERP.value

    def mark_completed(self, response: dict | None = None) -> None:
        """Marca a sincronização como concluída."""
        self.status = SyncStatus.COMPLETED.value
        self.synced_at = datetime.utcnow()
        if response:
            self.response = response

    def mark_failed(self, error: str, details: dict | None = None) -> None:
        """Marca a sincronização como falha."""
        self.status = SyncStatus.FAILED.value
        self.error_message = error
        if details:
            self.error_details = details
        self.last_retry_at = datetime.utcnow()

    def increment_retry(self) -> None:
        """Incrementa contador de retentativas."""
        self.retry_count += 1
        self.last_retry_at = datetime.utcnow()
        self.status = SyncStatus.IN_PROGRESS.value
