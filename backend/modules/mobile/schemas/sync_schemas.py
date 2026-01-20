"""Schemas de sincronização mobile."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MobileSyncOperation(BaseModel):
    """Operação de sincronização mobile."""

    id: str = Field(..., description="ID único da operação")
    table: str = Field(..., description="Tabela afetada")
    operation: str = Field(..., description="Tipo: create, update, delete")
    record_id: str = Field(..., description="ID do registro")
    data: Optional[dict[str, Any]] = Field(default=None, description="Dados da operação")
    changed_fields: list[str] = Field(default=[], description="Campos alterados")
    timestamp: datetime = Field(..., description="Timestamp do cliente")
    can_parallelize: bool = Field(default=True, description="Pode executar em paralelo")
    depends_on: Optional[str] = Field(default=None, description="Operação dependente")
    version: Optional[int] = Field(default=None, description="Versão do registro")

    model_config = {"from_attributes": True}


class SyncConflict(BaseModel):
    """Conflito de sincronização."""

    operation_id: str = Field(..., description="ID da operação com conflito")
    table: str = Field(..., description="Tabela do conflito")
    record_id: str = Field(..., description="ID do registro")
    client_data: dict[str, Any] = Field(..., description="Dados do cliente")
    server_data: dict[str, Any] = Field(..., description="Dados do servidor")
    conflicting_fields: list[str] = Field(..., description="Campos em conflito")
    client_timestamp: datetime = Field(..., description="Timestamp do cliente")
    server_timestamp: datetime = Field(..., description="Timestamp do servidor")
    resolution_strategy: str = Field(
        default="last_write_wins",
        description="Estratégia de resolução",
    )
    resolved: bool = Field(default=False, description="Se foi resolvido")
    resolved_data: Optional[dict[str, Any]] = Field(
        default=None,
        description="Dados após resolução",
    )

    model_config = {"from_attributes": True}


class DeviceInfo(BaseModel):
    """Informações do dispositivo."""

    device_id: Optional[str] = None
    platform: str = Field(..., description="ios, android, web")
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    connection_type: Optional[str] = Field(
        default="unknown",
        description="wifi, 4g, 3g, slow, unknown",
    )
    battery_level: Optional[int] = Field(default=None, ge=0, le=100)
    storage_available_mb: Optional[int] = None

    model_config = {"from_attributes": True}


class MobileSyncRequest(BaseModel):
    """Request de sincronização."""

    operations: list[MobileSyncOperation] = Field(
        default=[],
        description="Lista de operações a sincronizar",
    )
    last_sync_token: Optional[str] = Field(
        default=None,
        description="Token da última sincronização",
    )
    device_info: Optional[DeviceInfo] = Field(
        default=None,
        description="Informações do dispositivo",
    )
    modules: list[str] = Field(
        default=[],
        description="Módulos a sincronizar",
    )
    full_sync: bool = Field(
        default=False,
        description="Se é sincronização completa",
    )

    model_config = {"from_attributes": True}


class SyncOperationResult(BaseModel):
    """Resultado de uma operação de sync."""

    id: str = Field(..., description="ID da operação")
    status: str = Field(..., description="success, error, conflict")
    data: Optional[dict[str, Any]] = Field(default=None)
    error: Optional[str] = Field(default=None)
    server_version: Optional[int] = Field(default=None)

    model_config = {"from_attributes": True}


class ServerChange(BaseModel):
    """Mudança no servidor para sincronizar com cliente."""

    table: str
    record_id: str
    operation: str = Field(..., description="create, update, delete")
    data: Optional[dict[str, Any]] = None
    timestamp: datetime
    version: int

    model_config = {"from_attributes": True}


class MobileSyncResponse(BaseModel):
    """Response de sincronização."""

    timestamp: datetime = Field(..., description="Timestamp do servidor")
    user_id: int
    operations: list[SyncOperationResult] = Field(
        default=[],
        description="Resultados das operações",
    )
    server_changes: list[ServerChange] = Field(
        default=[],
        description="Mudanças do servidor",
    )
    conflicts: list[SyncConflict] = Field(
        default=[],
        description="Conflitos detectados",
    )
    new_sync_token: str = Field(..., description="Novo token de sync")
    sync_complete: bool = Field(default=True)
    next_sync_token: Optional[str] = Field(
        default=None,
        description="Token para continuar sync paginada",
    )
    stats: dict[str, Any] = Field(
        default_factory=dict,
        description="Estatísticas da sincronização",
    )

    model_config = {"from_attributes": True}


class SyncStatusResponse(BaseModel):
    """Status da sincronização."""

    user_id: int
    last_sync_at: Optional[datetime] = None
    pending_operations: int = 0
    sync_token: str
    cached_modules: list[str] = []
    cache_version: int = 1
    is_syncing: bool = False

    model_config = {"from_attributes": True}
