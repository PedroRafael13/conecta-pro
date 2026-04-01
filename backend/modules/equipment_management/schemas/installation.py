"""
Schemas Pydantic para EquipmentInstallation.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from modules.equipment_management.models.installation import InstallationStatus


class InstallationCreate(BaseModel):
    """Schema para criar instalação."""

    client_id: str = Field(..., description="ID do cliente")
    client_name: str = Field(..., min_length=1, max_length=200, description="Nome do cliente")
    contract_id: str | None = Field(None, description="ID do contrato")
    post_id: str | None = Field(None, description="ID do posto")

    # Local
    address: str = Field(..., min_length=1, description="Endereço")
    address_complement: str | None = Field(None, max_length=200, description="Complemento")
    city: str | None = Field(None, max_length=100, description="Cidade")
    state: str | None = Field(None, max_length=2, description="Estado")
    zip_code: str | None = Field(None, max_length=10, description="CEP")
    gps_latitude: float | None = Field(None, description="Latitude")
    gps_longitude: float | None = Field(None, description="Longitude")
    location_details: str | None = Field(None, description="Detalhes do local")

    # Agendamento
    scheduled_date: datetime = Field(..., description="Data agendada")
    scheduled_time_start: str | None = Field(None, description="Hora início (HH:MM)")
    scheduled_time_end: str | None = Field(None, description="Hora fim (HH:MM)")
    estimated_duration_hours: float | None = Field(None, ge=0, description="Duração estimada")

    # Equipamentos
    equipment_ids: list[str] = Field(..., min_length=1, description="IDs dos equipamentos")

    # Técnico
    technician_id: str | None = Field(None, description="ID do técnico")
    technician_name: str | None = Field(None, max_length=200, description="Nome do técnico")

    # Metadados
    priority: str = Field(default="normal", description="Prioridade")
    notes: str | None = Field(None, description="Observações")

    model_config = ConfigDict(use_enum_values=True)


class InstallationUpdate(BaseModel):
    """Schema para atualizar instalação."""

    status: InstallationStatus | None = Field(None, description="Status")
    scheduled_date: datetime | None = Field(None, description="Data agendada")
    scheduled_time_start: str | None = Field(None, description="Hora início")
    scheduled_time_end: str | None = Field(None, description="Hora fim")
    estimated_duration_hours: float | None = Field(None, ge=0, description="Duração")

    technician_id: str | None = Field(None, description="ID do técnico")
    technician_name: str | None = Field(None, max_length=200, description="Nome do técnico")
    team_members: list | None = Field(None, description="Membros da equipe")

    configurations: dict | None = Field(None, description="Configurações")
    network_config: dict | None = Field(None, description="Configuração de rede")

    technical_report: str | None = Field(None, description="Relatório técnico")
    issues_found: list | None = Field(None, description="Problemas encontrados")
    recommendations: list | None = Field(None, description="Recomendações")

    labor_cost: float | None = Field(None, ge=0, description="Custo mão de obra")
    transport_cost: float | None = Field(None, ge=0, description="Custo transporte")

    priority: str | None = Field(None, description="Prioridade")
    notes: str | None = Field(None, description="Observações")
    internal_notes: str | None = Field(None, description="Notas internas")

    model_config = ConfigDict(use_enum_values=True)


class InstallationResponse(BaseModel):
    """Schema de resposta para instalação."""

    id: str
    installation_code: str
    status: str
    client_id: str
    client_name: str
    contract_id: str | None
    post_id: str | None

    address: str
    address_complement: str | None
    city: str | None
    state: str | None
    zip_code: str | None
    gps_latitude: float | None
    gps_longitude: float | None
    location_details: str | None

    scheduled_date: datetime
    scheduled_time_start: str | None
    scheduled_time_end: str | None
    estimated_duration_hours: float | None

    started_at: datetime | None
    completed_at: datetime | None
    actual_duration_hours: float | None

    technician_id: str | None
    technician_name: str | None
    team_members: list | None

    equipment_ids: list
    equipment_count: int
    equipment_details: list | None

    configurations: dict | None
    network_config: dict | None

    photos_before: list | None
    photos_after: list | None
    photos_equipment: list | None
    documents: list | None

    materials_used: list | None
    total_materials_value: float | None

    client_accepted: bool
    client_accepted_at: datetime | None
    client_accepted_by: str | None

    technical_report: str | None
    issues_found: list | None
    recommendations: list | None

    labor_cost: float | None
    transport_cost: float | None
    total_cost: float | None

    rescheduled_count: int
    rescheduled_reason: str | None
    original_date: datetime | None

    cancelled_at: datetime | None
    cancellation_reason: str | None

    priority: str
    notes: str | None
    tags: list | None

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

    search: str | None = Field(None, description="Busca textual")
    status: InstallationStatus | None = Field(None, description="Status")
    client_id: str | None = Field(None, description="Cliente")
    technician_id: str | None = Field(None, description="Técnico")
    priority: str | None = Field(None, description="Prioridade")
    date_from: datetime | None = Field(None, description="Data inicial")
    date_to: datetime | None = Field(None, description="Data final")
    is_overdue: bool | None = Field(None, description="Atrasadas")
    has_acceptance: bool | None = Field(None, description="Com aceite do cliente")

    model_config = ConfigDict(use_enum_values=True)


class InstallationListResponse(BaseModel):
    """Schema para lista paginada de instalações."""

    items: list[InstallationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
