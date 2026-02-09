"""
Schemas Pydantic para GuardianSync.
"""

from datetime import datetime

from modules.remote_gatehouse.models.guardian_sync import (
    SyncDirection,
    SyncEntityType,
    SyncStatus,
)
from pydantic import BaseModel, ConfigDict, Field


class GuardianSyncCreate(BaseModel):
    """Schema para criar sincronização."""

    direction: SyncDirection = Field(
        default=SyncDirection.ERP_TO_GUARDIAN,
        description="Direção da sincronização",
    )
    entity_type: SyncEntityType = Field(..., description="Tipo de entidade")
    entity_id: str = Field(..., min_length=1, max_length=100, description="ID da entidade")
    external_id: str | None = Field(None, max_length=100, description="ID externo")
    client_id: str | None = Field(None, description="ID do cliente")
    contract_id: str | None = Field(None, description="ID do contrato")
    post_id: str | None = Field(None, description="ID do posto")
    payload: dict | None = Field(None, description="Dados a sincronizar")
    metadata_extra: dict | None = Field(None, description="Metadados adicionais")

    model_config = ConfigDict(use_enum_values=True)


class GuardianSyncResponse(BaseModel):
    """Schema de resposta para sincronização."""

    id: str
    sync_code: str
    direction: str
    entity_type: str
    entity_id: str
    external_id: str | None
    status: str
    client_id: str | None
    contract_id: str | None
    post_id: str | None
    payload: dict | None
    response: dict | None
    error_message: str | None
    error_details: dict | None
    retry_count: int
    max_retries: int
    last_retry_at: datetime | None
    next_retry_at: datetime | None
    synced_at: datetime | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    metadata_extra: dict | None

    model_config = ConfigDict(from_attributes=True)


class GuardianSyncFilter(BaseModel):
    """Schema para filtrar sincronizações."""

    search: str | None = Field(None, description="Busca textual")
    direction: SyncDirection | None = Field(None, description="Direção")
    entity_type: SyncEntityType | None = Field(None, description="Tipo de entidade")
    status: SyncStatus | None = Field(None, description="Status")
    client_id: str | None = Field(None, description="ID do cliente")
    contract_id: str | None = Field(None, description="ID do contrato")
    can_retry: bool | None = Field(None, description="Pode tentar novamente")
    date_from: datetime | None = Field(None, description="Data inicial")
    date_to: datetime | None = Field(None, description="Data final")

    model_config = ConfigDict(use_enum_values=True)


class GuardianSyncListResponse(BaseModel):
    """Schema para lista paginada de sincronizações."""

    items: list[GuardianSyncResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class GuardianSyncRetry(BaseModel):
    """Schema para retentativa de sincronização."""

    notes: str | None = Field(None, max_length=500, description="Observações")


class GuardianSyncStats(BaseModel):
    """Estatísticas de sincronização."""

    total: int = Field(default=0, description="Total de sincronizações")
    pending: int = Field(default=0, description="Pendentes")
    in_progress: int = Field(default=0, description="Em andamento")
    completed: int = Field(default=0, description="Concluídas")
    failed: int = Field(default=0, description="Falhas")
    partial: int = Field(default=0, description="Parciais")
    success_rate: float = Field(default=0.0, description="Taxa de sucesso")
    by_direction: dict = Field(default_factory=dict, description="Por direção")
    by_entity_type: dict = Field(default_factory=dict, description="Por tipo de entidade")
    avg_retry_count: float = Field(default=0.0, description="Média de retentativas")
    last_sync_at: datetime | None = Field(None, description="Última sincronização")
