"""
Schemas Pydantic para EquipmentStatus.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.campo.models.equipment_status import EquipmentStatusType


class EquipmentStatusCreate(BaseModel):
    """Schema para criar status de equipamento."""

    external_id: str = Field(..., min_length=1, max_length=100)
    equipment_id: str = Field(..., min_length=1, max_length=100)
    equipment_type: str = Field(..., min_length=1, max_length=50)
    equipment_name: str = Field(..., min_length=1, max_length=100)
    equipment_model: str | None = Field(None, max_length=100)
    equipment_brand: str | None = Field(None, max_length=50)
    serial_number: str | None = Field(None, max_length=50)
    firmware_version: str | None = Field(None, max_length=30)

    status: EquipmentStatusType = Field(default=EquipmentStatusType.OFFLINE)
    status_message: str | None = Field(None, max_length=255)
    status_code: int | None = Field(None)

    client_id: str = Field(..., description="ID do cliente")
    contract_id: str | None = Field(None, description="ID do contrato")
    post_id: str | None = Field(None, description="ID do posto")

    location: str | None = Field(None, max_length=255)
    location_details: str | None = Field(None)

    ip_address: str | None = Field(None, max_length=45)
    mac_address: str | None = Field(None, max_length=17)
    port: int | None = Field(None, ge=1, le=65535)

    last_ping_at: datetime | None = Field(None)
    ping_latency_ms: int | None = Field(None, ge=0)

    uptime_percentage: float | None = Field(None, ge=0, le=100)
    metrics: dict | None = Field(None)

    has_alerts: bool = Field(default=False)
    active_alerts: list[dict] | None = Field(None)

    next_maintenance_at: datetime | None = Field(None)
    maintenance_notes: str | None = Field(None)

    external_metadata: dict | None = Field(None)

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

    status: EquipmentStatusType | None = Field(None, description="Novo status")
    status_message: str | None = Field(None, max_length=255)
    status_code: int | None = Field(None)
    last_ping_at: datetime | None = Field(None)
    ping_latency_ms: int | None = Field(None, ge=0)
    uptime_percentage: float | None = Field(None, ge=0, le=100)
    metrics: dict | None = Field(None)
    has_alerts: bool | None = Field(None)
    active_alerts: list[dict] | None = Field(None)
    last_event_type: str | None = Field(None, max_length=50)
    last_event_at: datetime | None = Field(None)
    last_event_description: str | None = Field(None, max_length=255)

    model_config = ConfigDict(use_enum_values=True)


class EquipmentStatusResponse(BaseModel):
    """Schema de resposta para status de equipamento."""

    id: str
    external_id: str
    equipment_id: str
    equipment_type: str
    equipment_name: str
    equipment_model: str | None
    equipment_brand: str | None
    serial_number: str | None
    firmware_version: str | None
    status: str
    status_message: str | None
    status_code: int | None
    client_id: str
    contract_id: str | None
    post_id: str | None
    location: str | None
    location_details: str | None
    ip_address: str | None
    mac_address: str | None
    port: int | None
    last_ping_at: datetime | None
    ping_latency_ms: int | None
    last_online_at: datetime | None
    last_offline_at: datetime | None
    uptime_percentage: float | None
    uptime_hours_24h: float | None
    uptime_hours_7d: float | None
    uptime_hours_30d: float | None
    incidents_count_30d: int
    last_event_type: str | None
    last_event_at: datetime | None
    last_event_description: str | None
    metrics: dict | None
    has_alerts: bool
    active_alerts: list | None
    alert_count: int
    next_maintenance_at: datetime | None
    maintenance_notes: str | None
    received_at: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EquipmentStatusFilter(BaseModel):
    """Schema para filtrar status de equipamentos."""

    search: str | None = Field(None, description="Busca textual")
    equipment_type: str | None = Field(None, description="Tipo de equipamento")
    status: EquipmentStatusType | None = Field(None, description="Status")
    client_id: str | None = Field(None, description="ID do cliente")
    post_id: str | None = Field(None, description="ID do posto")
    is_online: bool | None = Field(None, description="Está online")
    has_alerts: bool | None = Field(None, description="Tem alertas")
    has_issues: bool | None = Field(None, description="Tem problemas")
    needs_maintenance: bool | None = Field(None, description="Precisa manutenção")

    model_config = ConfigDict(use_enum_values=True)


class EquipmentStatusListResponse(BaseModel):
    """Schema para lista paginada de status de equipamentos."""

    items: list[EquipmentStatusResponse]
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
