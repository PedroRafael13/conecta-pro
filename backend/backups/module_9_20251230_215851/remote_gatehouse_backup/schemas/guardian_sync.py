"""
Schemas Pydantic para GuardianSync.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from modules.remote_gatehouse.models.guardian_sync import (
    SyncDirection,
    SyncEntityType,
    SyncStatus,
)


class GuardianSyncCreate(BaseModel):
    """Schema para criar sincronização."""

    direction: SyncDirection = Field(
        default=SyncDirection.ERP_TO_GUARDIAN,
        description="Direção da sincronização",
    )
    entity_type: SyncEntityType = Field(..., description="Tipo de entidade")
    entity_id: str = Field(..., min_length=1, max_length=100, description="ID da entidade")
    external_id: Optional[str] = Field(None, max_length=100, description="ID externo")
    client_id: Optional[str] = Field(None, description="ID do cliente")
    contract_id: Optional[str] = Field(None, description="ID do contrato")
    post_id: Optional[str] = Field(None, description="ID do posto")
    payload: Optional[dict] = Field(None, description="Dados a sincronizar")
    metadata_extra: Optional[dict] = Field(None, description="Metadados adicionais")

    model_config = ConfigDict(use_enum_values=True)


class GuardianSyncResponse(BaseModel):
    """Schema de resposta para sincronização."""

    id: str
    sync_code: str
    direction: str
    entity_type: str
    entity_id: str
    external_id: Optional[str]
    status: str
    client_id: Optional[str]
    contract_id: Optional[str]
    post_id: Optional[str]
    payload: Optional[dict]
    response: Optional[dict]
    error_message: Optional[str]
    error_details: Optional[dict]
    retry_count: int
    max_retries: int
    last_retry_at: Optional[datetime]
    next_retry_at: Optional[datetime]
    synced_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    metadata_extra: Optional[dict]

    model_config = ConfigDict(from_attributes=True)


class GuardianSyncFilter(BaseModel):
    """Schema para filtrar sincronizações."""

    search: Optional[str] = Field(None, description="Busca textual")
    direction: Optional[SyncDirection] = Field(None, description="Direção")
    entity_type: Optional[SyncEntityType] = Field(None, description="Tipo de entidade")
    status: Optional[SyncStatus] = Field(None, description="Status")
    client_id: Optional[str] = Field(None, description="ID do cliente")
    contract_id: Optional[str] = Field(None, description="ID do contrato")
    can_retry: Optional[bool] = Field(None, description="Pode tentar novamente")
    date_from: Optional[datetime] = Field(None, description="Data inicial")
    date_to: Optional[datetime] = Field(None, description="Data final")

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

    notes: Optional[str] = Field(None, max_length=500, description="Observações")


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
    last_sync_at: Optional[datetime] = Field(None, description="Última sincronização")
