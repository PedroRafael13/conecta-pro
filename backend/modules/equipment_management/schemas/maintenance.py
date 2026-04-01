"""
Schemas Pydantic para EquipmentMaintenance.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from modules.equipment_management.models.maintenance import (
    MaintenancePriority,
    MaintenanceStatus,
    MaintenanceType,
)


class MaintenanceCreate(BaseModel):
    """Schema para criar manutenção."""

    maintenance_type: MaintenanceType = Field(..., description="Tipo de manutenção")
    priority: MaintenancePriority = Field(
        default=MaintenancePriority.MEDIUM,
        description="Prioridade",
    )

    equipment_id: str = Field(..., description="ID do equipamento")
    equipment_code: str = Field(..., description="Código do equipamento")
    equipment_name: str = Field(..., max_length=200, description="Nome do equipamento")
    equipment_type: str = Field(..., max_length=50, description="Tipo do equipamento")
    serial_number: str | None = Field(None, max_length=100, description="Número de série")

    client_id: str | None = Field(None, description="ID do cliente")
    client_name: str | None = Field(None, max_length=200, description="Nome do cliente")
    contract_id: str | None = Field(None, description="ID do contrato")

    title: str = Field(..., min_length=1, max_length=200, description="Título")
    description: str | None = Field(None, description="Descrição")
    symptoms: str | None = Field(None, description="Sintomas reportados")
    reported_by: str | None = Field(None, max_length=200, description="Reportado por")

    scheduled_date: datetime | None = Field(None, description="Data agendada")
    scheduled_time: str | None = Field(None, description="Hora (HH:MM)")
    estimated_duration_hours: float | None = Field(None, ge=0, description="Duração estimada")
    sla_deadline: datetime | None = Field(None, description="Prazo SLA")

    technician_id: str | None = Field(None, description="ID do técnico")
    technician_name: str | None = Field(None, max_length=200, description="Nome do técnico")

    checklist_template_id: str | None = Field(None, description="Template de checklist")

    is_recurring: bool = Field(default=False, description="É recorrente?")
    recurrence_interval_days: int | None = Field(None, ge=1, description="Intervalo em dias")

    notes: str | None = Field(None, description="Observações")

    model_config = ConfigDict(use_enum_values=True)


class MaintenanceUpdate(BaseModel):
    """Schema para atualizar manutenção."""

    status: MaintenanceStatus | None = Field(None, description="Status")
    priority: MaintenancePriority | None = Field(None, description="Prioridade")

    scheduled_date: datetime | None = Field(None, description="Data agendada")
    scheduled_time: str | None = Field(None, description="Hora")
    sla_deadline: datetime | None = Field(None, description="Prazo SLA")

    technician_id: str | None = Field(None, description="ID do técnico")
    technician_name: str | None = Field(None, max_length=200, description="Nome do técnico")
    team_members: list | None = Field(None, description="Equipe")

    diagnosis: str | None = Field(None, description="Diagnóstico")
    root_cause: str | None = Field(None, description="Causa raiz")
    actions_taken: str | None = Field(None, description="Ações realizadas")

    checklist_items: list | None = Field(None, description="Itens do checklist")
    checklist_score: float | None = Field(None, ge=0, le=100, description="Score checklist")

    parts_replaced: list | None = Field(None, description="Peças substituídas")

    labor_cost: float | None = Field(None, ge=0, description="Custo mão de obra")
    parts_cost: float | None = Field(None, ge=0, description="Custo peças")
    transport_cost: float | None = Field(None, ge=0, description="Custo transporte")
    is_billable: bool | None = Field(None, description="Cobrável?")

    technical_report: str | None = Field(None, description="Relatório técnico")
    recommendations: list | None = Field(None, description="Recomendações")

    needs_followup: bool | None = Field(None, description="Precisa follow-up?")
    followup_date: datetime | None = Field(None, description="Data follow-up")
    followup_notes: str | None = Field(None, description="Notas follow-up")

    notes: str | None = Field(None, description="Observações")
    internal_notes: str | None = Field(None, description="Notas internas")

    model_config = ConfigDict(use_enum_values=True)


class MaintenanceResponse(BaseModel):
    """Schema de resposta para manutenção."""

    id: str
    maintenance_code: str
    maintenance_type: str
    status: str
    priority: str

    equipment_id: str
    equipment_code: str
    equipment_name: str
    equipment_type: str
    serial_number: str | None

    client_id: str | None
    client_name: str | None
    contract_id: str | None

    title: str
    description: str | None
    symptoms: str | None
    reported_by: str | None
    reported_at: datetime | None

    scheduled_date: datetime | None
    scheduled_time: str | None
    estimated_duration_hours: float | None
    sla_deadline: datetime | None

    started_at: datetime | None
    completed_at: datetime | None
    actual_duration_hours: float | None

    technician_id: str | None
    technician_name: str | None
    team_members: list | None

    checklist_template_id: str | None
    checklist_items: list | None
    checklist_score: float | None

    diagnosis: str | None
    root_cause: str | None
    is_warranty_repair: bool

    actions_taken: str | None
    firmware_updated: bool
    firmware_version_before: str | None
    firmware_version_after: str | None
    settings_changed: dict | None

    parts_replaced: list | None
    parts_requested: list | None

    labor_cost: float | None
    parts_cost: float | None
    transport_cost: float | None
    other_costs: float | None
    total_cost: float | None
    is_billable: bool
    invoice_id: str | None

    equipment_status_after: str | None
    problem_resolved: bool
    needs_followup: bool
    followup_date: datetime | None
    followup_notes: str | None

    photos_before: list | None
    photos_after: list | None
    photos_parts: list | None

    technical_report: str | None
    recommendations: list | None

    client_signature: str | None
    signed_by: str | None
    signed_at: datetime | None

    response_time_hours: float | None
    resolution_time_hours: float | None
    sla_met: bool | None

    is_recurring: bool
    recurrence_interval_days: int | None
    next_maintenance_date: datetime | None
    parent_maintenance_id: str | None

    notes: str | None
    tags: list | None

    is_completed: bool
    is_overdue: bool
    is_preventive: bool
    is_corrective: bool

    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MaintenanceFilter(BaseModel):
    """Schema para filtrar manutenções."""

    search: str | None = Field(None, description="Busca textual")
    maintenance_type: MaintenanceType | None = Field(None, description="Tipo")
    status: MaintenanceStatus | None = Field(None, description="Status")
    priority: MaintenancePriority | None = Field(None, description="Prioridade")
    equipment_id: str | None = Field(None, description="Equipamento")
    client_id: str | None = Field(None, description="Cliente")
    technician_id: str | None = Field(None, description="Técnico")
    is_overdue: bool | None = Field(None, description="Atrasadas")
    is_warranty: bool | None = Field(None, description="Em garantia")
    problem_resolved: bool | None = Field(None, description="Problema resolvido")
    needs_followup: bool | None = Field(None, description="Precisa follow-up")
    date_from: datetime | None = Field(None, description="Data inicial")
    date_to: datetime | None = Field(None, description="Data final")

    model_config = ConfigDict(use_enum_values=True)


class MaintenanceListResponse(BaseModel):
    """Schema para lista paginada de manutenções."""

    items: list[MaintenanceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class MaintenanceStats(BaseModel):
    """Estatísticas de manutenções."""

    total: int = Field(default=0, description="Total")
    by_status: dict[str, int] = Field(default_factory=dict, description="Por status")
    by_type: dict[str, int] = Field(default_factory=dict, description="Por tipo")
    by_priority: dict[str, int] = Field(default_factory=dict, description="Por prioridade")

    scheduled: int = Field(default=0, description="Agendadas")
    in_progress: int = Field(default=0, description="Em andamento")
    completed: int = Field(default=0, description="Concluídas")
    overdue: int = Field(default=0, description="Atrasadas")
    waiting_parts: int = Field(default=0, description="Aguardando peças")

    preventive: int = Field(default=0, description="Preventivas")
    corrective: int = Field(default=0, description="Corretivas")

    avg_response_time_hours: float = Field(default=0.0, description="Tempo médio de resposta")
    avg_resolution_time_hours: float = Field(default=0.0, description="Tempo médio de resolução")
    sla_compliance_rate: float = Field(default=0.0, description="Taxa de cumprimento SLA")
    first_time_fix_rate: float = Field(default=0.0, description="Taxa de resolução na primeira")

    total_cost: float = Field(default=0.0, description="Custo total")
    avg_cost: float = Field(default=0.0, description="Custo médio")
