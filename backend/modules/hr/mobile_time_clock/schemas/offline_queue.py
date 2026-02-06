"""Schemas para OfflineQueue."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class OfflineQueueItemCreate(BaseModel):
    """Schema para criar item na fila offline."""
    offline_id: str = Field(..., min_length=10, max_length=100)
    checkin_data: dict
    checkin_type: str
    device_timestamp: datetime
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    accuracy_meters: Optional[float] = Field(None, ge=0)
    local_validation: Optional[dict] = None
    local_geofence_check: bool = Field(default=False)
    local_biometric_check: bool = Field(default=False)
    app_version: Optional[str] = Field(None, max_length=20)
    device_info: Optional[dict] = None
    network_type: Optional[str] = Field(None, max_length=20)
    expires_hours: int = Field(default=24, ge=1, le=168)


class OfflineQueueBatch(BaseModel):
    """Schema para batch de itens offline."""
    items: List[OfflineQueueItemCreate] = Field(..., min_length=1, max_length=100)


class OfflineQueueResponse(BaseModel):
    """Schema de resposta para item da fila."""
    id: UUID
    device_id: UUID
    employee_id: UUID
    condominio_id: UUID
    offline_id: str
    checkin_type: str
    device_timestamp: datetime
    latitude: Optional[float]
    longitude: Optional[float]
    accuracy_meters: Optional[float]
    local_geofence_check: bool
    local_biometric_check: bool
    status: str
    priority: str
    checkin_id: Optional[UUID]
    synced_at: Optional[datetime]
    error_message: Optional[str]
    error_code: Optional[str]
    retry_count: int
    max_retries: int
    next_retry_at: Optional[datetime]
    expires_at: datetime
    is_expired: bool
    app_version: Optional[str]
    network_type: Optional[str]
    queued_at: datetime
    received_at: datetime
    processed_at: Optional[datetime]

    class Config:  # pylint: disable=too-few-public-methods
        """Configuracao do Pydantic."""

        from_attributes = True


class OfflineQueueList(BaseModel):
    """Schema de lista de itens da fila."""
    items: List[OfflineQueueResponse]
    total: int
    page: int
    page_size: int
    pages: int


class OfflineQueueFilter(BaseModel):
    """Filtros para busca na fila."""
    device_id: Optional[UUID] = None
    employee_id: Optional[UUID] = None
    condominio_id: Optional[UUID] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    is_expired: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class OfflineQueueStats(BaseModel):
    """Estatísticas da fila offline."""
    total_items: int
    pending_items: int
    processing_items: int
    synced_items: int
    failed_items: int
    expired_items: int
    by_status: dict
    by_priority: dict
    avg_age_hours: float
    avg_retry_count: float
    oldest_pending: Optional[datetime]


class SyncResult(BaseModel):
    """Resultado da sincronização de um item."""
    offline_id: str
    success: bool
    checkin_id: Optional[UUID] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None


class SyncBatchResult(BaseModel):
    """Resultado da sincronização em batch."""
    total_submitted: int
    total_synced: int
    total_failed: int
    total_duplicate: int
    total_expired: int
    results: List[SyncResult]
    server_time: datetime


class OfflineQueueRetry(BaseModel):
    """Schema para retry manual."""
    item_ids: List[UUID] = Field(..., min_length=1, max_length=50)
    force: bool = Field(default=False)


class OfflineQueueCleanup(BaseModel):
    """Schema para limpeza da fila."""
    older_than_hours: int = Field(default=72, ge=24, le=720)
    statuses: List[str] = Field(default=["synced", "expired", "duplicate", "invalid"])
    dry_run: bool = Field(default=True)


class OfflineQueueCleanupResult(BaseModel):
    """Resultado da limpeza."""
    deleted_count: int
    by_status: dict
    dry_run: bool
