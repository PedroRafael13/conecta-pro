"""
Schemas Pydantic para EquipmentStatus.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.guardian.models.equipment_status import EquipmentStatusType


class EquipmentStatusCreate(BaseModel):
    """Schema para criar status de equipamento."""

    guardian_id: str = Field(..., min_length=1, max_length=100)
    equipment_id: str = Field(..., min_length=1, max_length=100)
    equipment_type: str = Field(..., min_length=1, max_length=50)
    equipment_name: str = Field(..., min_length=1, max_length=100)
    equipment_model: Optional[str] = Field(None, max_length=100)
    equipment_brand: Optional[str] = Field(None, max_length=50)
    serial_number: Optional[str] = Field(None, max_length=50)
    firmware_version: Optional[str] = Field(None, max_length=30)

    status: EquipmentStatusType = Field(default=EquipmentStatusType.OFFLINE)
    status_message: Optional[str] = Field(None, max_length=255)
    status_code: Optional[int] = Field(None)

    client_id: str = Field(..., description="ID do cliente")
    contract_id: Optional[str] = Field(None, description="ID do contrato")
    post_id: Optional[str] = Field(None, description="ID do posto")

    location: Optional[str] = Field(None, max_length=255)
    location_details: Optional[str] = Field(None)

    ip_address: Optional[str] = Field(None, max_length=45)
    mac_address: Optional[str] = Field(None, max_length=17)
    port: Optional[int] = Field(None, ge=1, le=65535)

    last_ping_at: Optional[datetime] = Field(None)
    ping_latency_ms: Optional[int] = Field(None, ge=0)

    uptime_percentage: Optional[float] = Field(None, ge=0, le=100)
    metrics: Optional[dict] = Field(None)

    has_alerts: bool = Field(default=False)
    active_alerts: Optional[List[dict]] = Field(None)

    next_maintenance_at: Optional[datetime] = Field(None)
    maintenance_notes: Optional[str] = Field(None)

    guardian_metadata: Optional[dict] = Field(None)

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("equipment_type")
    @classmethod
    def validate_equipment_type(cls, value: str) -> str:
        """Valida tipo de equipamento."""
        valid_types = [
            "camera",
            "dvr",
            "nvr",
            "alarm",
            "sensor",
            "access_control",
            "intercom",
            "gate",
            "barrier",
            "turnstile",
        ]
        if value.lower() not in valid_types:
            return value.lower()
        return value.lower()

    @field_validator("mac_address")
    @classmethod
    def validate_mac_address(cls, value: str | None) -> str | None:
        """Normaliza MAC address."""
        if value:
            return value.upper().replace("-", ":").strip()
        return value


class EquipmentStatusUpdate(BaseModel):
    """Schema para atualizar status de equipamento."""

    status: Optional[EquipmentStatusType] = Field(None, description="Novo status")
    status_message: Optional[str] = Field(None, max_length=255)
    status_code: Optional[int] = Field(None)
    last_ping_at: Optional[datetime] = Field(None)
    ping_latency_ms: Optional[int] = Field(None, ge=0)
    uptime_percentage: Optional[float] = Field(None, ge=0, le=100)
    metrics: Optional[dict] = Field(None)
    has_alerts: Optional[bool] = Field(None)
    active_alerts: Optional[List[dict]] = Field(None)
    last_event_type: Optional[str] = Field(None, max_length=50)
    last_event_at: Optional[datetime] = Field(None)
    last_event_description: Optional[str] = Field(None, max_length=255)

    model_config = ConfigDict(use_enum_values=True)


class EquipmentStatusResponse(BaseModel):
    """Schema de resposta para status de equipamento."""

    id: str
    guardian_id: str
    equipment_id: str
    equipment_type: str
    equipment_name: str
    equipment_model: Optional[str]
    equipment_brand: Optional[str]
    serial_number: Optional[str]
    firmware_version: Optional[str]
    status: str
    status_message: Optional[str]
    status_code: Optional[int]
    client_id: str
    contract_id: Optional[str]
    post_id: Optional[str]
    location: Optional[str]
    location_details: Optional[str]
    ip_address: Optional[str]
    mac_address: Optional[str]
    port: Optional[int]
    last_ping_at: Optional[datetime]
    ping_latency_ms: Optional[int]
    last_online_at: Optional[datetime]
    last_offline_at: Optional[datetime]
    uptime_percentage: Optional[float]
    uptime_hours_24h: Optional[float]
    uptime_hours_7d: Optional[float]
    uptime_hours_30d: Optional[float]
    incidents_count_30d: int
    last_event_type: Optional[str]
    last_event_at: Optional[datetime]
    last_event_description: Optional[str]
    metrics: Optional[dict]
    has_alerts: bool
    active_alerts: Optional[list]
    alert_count: int
    next_maintenance_at: Optional[datetime]
    maintenance_notes: Optional[str]
    received_at: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EquipmentStatusFilter(BaseModel):
    """Schema para filtrar status de equipamentos."""

    search: Optional[str] = Field(None, description="Busca textual")
    equipment_type: Optional[str] = Field(None, description="Tipo de equipamento")
    status: Optional[EquipmentStatusType] = Field(None, description="Status")
    client_id: Optional[str] = Field(None, description="ID do cliente")
    post_id: Optional[str] = Field(None, description="ID do posto")
    is_online: Optional[bool] = Field(None, description="Está online")
    has_alerts: Optional[bool] = Field(None, description="Tem alertas")
    has_issues: Optional[bool] = Field(None, description="Tem problemas")
    needs_maintenance: Optional[bool] = Field(None, description="Precisa manutenção")

    model_config = ConfigDict(use_enum_values=True)


class EquipmentStatusListResponse(BaseModel):
    """Schema para lista paginada de status de equipamentos."""

    items: List[EquipmentStatusResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class EquipmentStatusStats(BaseModel):
    """Estatísticas de status de equipamentos."""

    total: int = Field(default=0, description="Total de equipamentos")
    online: int = Field(default=0, description="Online")
    offline: int = Field(default=0, description="Offline")
    warning: int = Field(default=0, description="Com alerta")
    error: int = Field(default=0, description="Com erro")
    maintenance: int = Field(default=0, description="Em manutenção")
    disabled: int = Field(default=0, description="Desativados")
    availability_rate: float = Field(default=0.0, description="Taxa de disponibilidade")
    by_type: dict = Field(default_factory=dict, description="Por tipo")
    by_client: dict = Field(default_factory=dict, description="Por cliente")
    with_alerts: int = Field(default=0, description="Com alertas ativos")
    needs_maintenance: int = Field(default=0, description="Precisam manutenção")
    avg_uptime_percentage: float = Field(
        default=0.0,
        description="Média de uptime",
    )
    avg_ping_latency_ms: float = Field(
        default=0.0,
        description="Latência média de ping",
    )
