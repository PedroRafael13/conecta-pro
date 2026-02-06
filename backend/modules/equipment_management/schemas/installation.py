"""
Schemas Pydantic para EquipmentInstallation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from modules.equipment_management.models.installation import InstallationStatus


class InstallationCreate(BaseModel):
    """Schema para criar instalação."""

    client_id: str = Field(..., description="ID do cliente")
    client_name: str = Field(..., min_length=1, max_length=200, description="Nome do cliente")
    contract_id: Optional[str] = Field(None, description="ID do contrato")
    post_id: Optional[str] = Field(None, description="ID do posto")

    # Local
    address: str = Field(..., min_length=1, description="Endereço")
    address_complement: Optional[str] = Field(None, max_length=200, description="Complemento")
    city: Optional[str] = Field(None, max_length=100, description="Cidade")
    state: Optional[str] = Field(None, max_length=2, description="Estado")
    zip_code: Optional[str] = Field(None, max_length=10, description="CEP")
    gps_latitude: Optional[float] = Field(None, description="Latitude")
    gps_longitude: Optional[float] = Field(None, description="Longitude")
    location_details: Optional[str] = Field(None, description="Detalhes do local")

    # Agendamento
    scheduled_date: datetime = Field(..., description="Data agendada")
    scheduled_time_start: Optional[str] = Field(None, description="Hora início (HH:MM)")
    scheduled_time_end: Optional[str] = Field(None, description="Hora fim (HH:MM)")
    estimated_duration_hours: Optional[float] = Field(None, ge=0, description="Duração estimada")

    # Equipamentos
    equipment_ids: list[str] = Field(..., min_length=1, description="IDs dos equipamentos")

    # Técnico
    technician_id: Optional[str] = Field(None, description="ID do técnico")
    technician_name: Optional[str] = Field(None, max_length=200, description="Nome do técnico")

    # Metadados
    priority: str = Field(default="normal", description="Prioridade")
    notes: Optional[str] = Field(None, description="Observações")

    model_config = ConfigDict(use_enum_values=True)


class InstallationUpdate(BaseModel):
    """Schema para atualizar instalação."""

    status: Optional[InstallationStatus] = Field(None, description="Status")
    scheduled_date: Optional[datetime] = Field(None, description="Data agendada")
    scheduled_time_start: Optional[str] = Field(None, description="Hora início")
    scheduled_time_end: Optional[str] = Field(None, description="Hora fim")
    estimated_duration_hours: Optional[float] = Field(None, ge=0, description="Duração")

    technician_id: Optional[str] = Field(None, description="ID do técnico")
    technician_name: Optional[str] = Field(None, max_length=200, description="Nome do técnico")
    team_members: Optional[list] = Field(None, description="Membros da equipe")

    configurations: Optional[dict] = Field(None, description="Configurações")
    network_config: Optional[dict] = Field(None, description="Configuração de rede")

    technical_report: Optional[str] = Field(None, description="Relatório técnico")
    issues_found: Optional[list] = Field(None, description="Problemas encontrados")
    recommendations: Optional[list] = Field(None, description="Recomendações")

    labor_cost: Optional[float] = Field(None, ge=0, description="Custo mão de obra")
    transport_cost: Optional[float] = Field(None, ge=0, description="Custo transporte")

    priority: Optional[str] = Field(None, description="Prioridade")
    notes: Optional[str] = Field(None, description="Observações")
    internal_notes: Optional[str] = Field(None, description="Notas internas")

    model_config = ConfigDict(use_enum_values=True)


class InstallationResponse(BaseModel):
    """Schema de resposta para instalação."""

    id: str
    installation_code: str
    status: str
    client_id: str
    client_name: str
    contract_id: Optional[str]
    post_id: Optional[str]

    address: str
    address_complement: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    gps_latitude: Optional[float]
    gps_longitude: Optional[float]
    location_details: Optional[str]

    scheduled_date: datetime
    scheduled_time_start: Optional[str]
    scheduled_time_end: Optional[str]
    estimated_duration_hours: Optional[float]

    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    actual_duration_hours: Optional[float]

    technician_id: Optional[str]
    technician_name: Optional[str]
    team_members: Optional[list]

    equipment_ids: list
    equipment_count: int
    equipment_details: Optional[list]

    configurations: Optional[dict]
    network_config: Optional[dict]

    photos_before: Optional[list]
    photos_after: Optional[list]
    photos_equipment: Optional[list]
    documents: Optional[list]

    materials_used: Optional[list]
    total_materials_value: Optional[float]

    client_accepted: bool
    client_accepted_at: Optional[datetime]
    client_accepted_by: Optional[str]

    technical_report: Optional[str]
    issues_found: Optional[list]
    recommendations: Optional[list]

    labor_cost: Optional[float]
    transport_cost: Optional[float]
    total_cost: Optional[float]

    rescheduled_count: int
    rescheduled_reason: Optional[str]
    original_date: Optional[datetime]

    cancelled_at: Optional[datetime]
    cancellation_reason: Optional[str]

    priority: str
    notes: Optional[str]
    tags: Optional[list]

    is_completed: bool
    is_overdue: bool
    days_overdue: int
    has_client_acceptance: bool

    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InstallationFilter(BaseModel):
    """Schema para filtrar instalações."""

    search: Optional[str] = Field(None, description="Busca textual")
    status: Optional[InstallationStatus] = Field(None, description="Status")
    client_id: Optional[str] = Field(None, description="Cliente")
    technician_id: Optional[str] = Field(None, description="Técnico")
    priority: Optional[str] = Field(None, description="Prioridade")
    date_from: Optional[datetime] = Field(None, description="Data inicial")
    date_to: Optional[datetime] = Field(None, description="Data final")
    is_overdue: Optional[bool] = Field(None, description="Atrasadas")
    has_acceptance: Optional[bool] = Field(None, description="Com aceite do cliente")

    model_config = ConfigDict(use_enum_values=True)


class InstallationListResponse(BaseModel):
    """Schema para lista paginada de instalações."""

    items: list[InstallationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
