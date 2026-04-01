"""
Schemas Pydantic para AccessLog.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.campo.models.access_log import AccessLogType


class AccessLogCreate(BaseModel):
    """Schema para criar log de acesso."""

    external_id: str = Field(..., min_length=1, max_length=100)
    log_type: AccessLogType = Field(default=AccessLogType.ENTRY)
    client_id: str = Field(..., description="ID do cliente")
    contract_id: str | None = Field(None, description="ID do contrato")
    post_id: str | None = Field(None, description="ID do posto")

    # Pessoa
    person_name: str = Field(..., min_length=1, max_length=255)
    person_document: str | None = Field(None, max_length=20)
    person_type: str | None = Field(None, max_length=30)
    person_id: str | None = Field(None)

    # Localização
    unit_code: str | None = Field(None, max_length=20)
    unit_block: str | None = Field(None, max_length=20)
    access_point: str | None = Field(None, max_length=100)
    access_point_id: str | None = Field(None, max_length=50)

    # Método
    access_method: str | None = Field(None, max_length=30)
    device_id: str | None = Field(None, max_length=50)
    device_name: str | None = Field(None, max_length=100)

    # Veículo
    vehicle_plate: str | None = Field(None, max_length=10)
    vehicle_model: str | None = Field(None, max_length=50)
    vehicle_color: str | None = Field(None, max_length=30)

    # Operador
    operator_id: str | None = Field(None)
    operator_name: str | None = Field(None, max_length=100)
    authorization_type: str | None = Field(None, max_length=30)

    # Mídia
    photos: list[str] | None = Field(None)
    video_clip_url: str | None = Field(None, max_length=500)

    # Observações
    notes: str | None = Field(None)
    denial_reason: str | None = Field(None)

    # Timestamp
    event_timestamp: datetime = Field(..., description="Data/hora do evento")

    # Geo
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)

    # Metadados
    external_metadata: dict | None = Field(None)

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("person_document")
    @classmethod
    def validate_document(cls, value: str | None) -> str | None:
        """Valida e limpa o documento."""
        if value:
            return value.replace(".", "").replace("-", "").strip()
        return value

    @field_validator("vehicle_plate")
    @classmethod
    def validate_plate(cls, value: str | None) -> str | None:
        """Normaliza a placa do veículo."""
        if value:
            return value.upper().replace("-", "").replace(" ", "").strip()
        return value


class AccessLogResponse(BaseModel):
    """Schema de resposta para log de acesso."""

    id: str
    external_id: str
    log_type: str
    client_id: str
    contract_id: str | None
    post_id: str | None
    person_name: str
    person_document: str | None
    person_type: str | None
    person_id: str | None
    unit_code: str | None
    unit_block: str | None
    access_point: str | None
    access_point_id: str | None
    access_method: str | None
    device_id: str | None
    device_name: str | None
    vehicle_plate: str | None
    vehicle_model: str | None
    vehicle_color: str | None
    operator_id: str | None
    operator_name: str | None
    authorization_type: str | None
    photos: list | None
    video_clip_url: str | None
    notes: str | None
    denial_reason: str | None
    event_timestamp: datetime
    received_at: datetime
    latitude: float | None
    longitude: float | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AccessLogFilter(BaseModel):
    """Schema para filtrar logs de acesso."""

    search: str | None = Field(None, description="Busca textual")
    log_type: AccessLogType | None = Field(None, description="Tipo de log")
    client_id: str | None = Field(None, description="ID do cliente")
    post_id: str | None = Field(None, description="ID do posto")
    person_type: str | None = Field(None, description="Tipo de pessoa")
    access_method: str | None = Field(None, description="Método de acesso")
    unit_code: str | None = Field(None, description="Código da unidade")
    vehicle_plate: str | None = Field(None, description="Placa do veículo")
    date_from: datetime | None = Field(None, description="Data inicial")
    date_to: datetime | None = Field(None, description="Data final")
    is_denied: bool | None = Field(None, description="Foi negado")

    model_config = ConfigDict(use_enum_values=True)


class AccessLogListResponse(BaseModel):
    """Schema para lista paginada de logs de acesso."""

    items: list[AccessLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AccessLogStats(BaseModel):
    """Estatísticas de logs de acesso."""

    total: int = Field(default=0, description="Total de logs")
    entries: int = Field(default=0, description="Entradas")
    exits: int = Field(default=0, description="Saídas")
    denied: int = Field(default=0, description="Negados")
    visitors: int = Field(default=0, description="Visitantes")
    deliveries: int = Field(default=0, description="Entregas")
    by_access_method: dict = Field(default_factory=dict, description="Por método")
    by_access_point: dict = Field(default_factory=dict, description="Por ponto")
    by_hour: dict = Field(default_factory=dict, description="Por hora")
    by_day_of_week: dict = Field(default_factory=dict, description="Por dia da semana")
    peak_hours: list[int] = Field(default_factory=list, description="Horários de pico")
    avg_daily: float = Field(default=0.0, description="Média diária")
