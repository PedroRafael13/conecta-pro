"""
Schemas Pydantic para AccessLog.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.guardian.models.access_log import AccessLogType


class AccessLogCreate(BaseModel):
    """Schema para criar log de acesso."""

    guardian_id: str = Field(..., min_length=1, max_length=100)
    log_type: AccessLogType = Field(default=AccessLogType.ENTRY)
    client_id: str = Field(..., description="ID do cliente")
    contract_id: Optional[str] = Field(None, description="ID do contrato")
    post_id: Optional[str] = Field(None, description="ID do posto")

    # Pessoa
    person_name: str = Field(..., min_length=1, max_length=255)
    person_document: Optional[str] = Field(None, max_length=20)
    person_type: Optional[str] = Field(None, max_length=30)
    person_id: Optional[str] = Field(None)

    # Localização
    unit_code: Optional[str] = Field(None, max_length=20)
    unit_block: Optional[str] = Field(None, max_length=20)
    access_point: Optional[str] = Field(None, max_length=100)
    access_point_id: Optional[str] = Field(None, max_length=50)

    # Método
    access_method: Optional[str] = Field(None, max_length=30)
    device_id: Optional[str] = Field(None, max_length=50)
    device_name: Optional[str] = Field(None, max_length=100)

    # Veículo
    vehicle_plate: Optional[str] = Field(None, max_length=10)
    vehicle_model: Optional[str] = Field(None, max_length=50)
    vehicle_color: Optional[str] = Field(None, max_length=30)

    # Operador
    operator_id: Optional[str] = Field(None)
    operator_name: Optional[str] = Field(None, max_length=100)
    authorization_type: Optional[str] = Field(None, max_length=30)

    # Mídia
    photos: Optional[List[str]] = Field(None)
    video_clip_url: Optional[str] = Field(None, max_length=500)

    # Observações
    notes: Optional[str] = Field(None)
    denial_reason: Optional[str] = Field(None)

    # Timestamp
    event_timestamp: datetime = Field(..., description="Data/hora do evento")

    # Geo
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

    # Metadados
    guardian_metadata: Optional[dict] = Field(None)

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
    guardian_id: str
    log_type: str
    client_id: str
    contract_id: Optional[str]
    post_id: Optional[str]
    person_name: str
    person_document: Optional[str]
    person_type: Optional[str]
    person_id: Optional[str]
    unit_code: Optional[str]
    unit_block: Optional[str]
    access_point: Optional[str]
    access_point_id: Optional[str]
    access_method: Optional[str]
    device_id: Optional[str]
    device_name: Optional[str]
    vehicle_plate: Optional[str]
    vehicle_model: Optional[str]
    vehicle_color: Optional[str]
    operator_id: Optional[str]
    operator_name: Optional[str]
    authorization_type: Optional[str]
    photos: Optional[list]
    video_clip_url: Optional[str]
    notes: Optional[str]
    denial_reason: Optional[str]
    event_timestamp: datetime
    received_at: datetime
    latitude: Optional[float]
    longitude: Optional[float]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AccessLogFilter(BaseModel):
    """Schema para filtrar logs de acesso."""

    search: Optional[str] = Field(None, description="Busca textual")
    log_type: Optional[AccessLogType] = Field(None, description="Tipo de log")
    client_id: Optional[str] = Field(None, description="ID do cliente")
    post_id: Optional[str] = Field(None, description="ID do posto")
    person_type: Optional[str] = Field(None, description="Tipo de pessoa")
    access_method: Optional[str] = Field(None, description="Método de acesso")
    unit_code: Optional[str] = Field(None, description="Código da unidade")
    vehicle_plate: Optional[str] = Field(None, description="Placa do veículo")
    date_from: Optional[datetime] = Field(None, description="Data inicial")
    date_to: Optional[datetime] = Field(None, description="Data final")
    is_denied: Optional[bool] = Field(None, description="Foi negado")

    model_config = ConfigDict(use_enum_values=True)


class AccessLogListResponse(BaseModel):
    """Schema para lista paginada de logs de acesso."""

    items: List[AccessLogResponse]
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
    peak_hours: List[int] = Field(default_factory=list, description="Horários de pico")
    avg_daily: float = Field(default=0.0, description="Média diária")
