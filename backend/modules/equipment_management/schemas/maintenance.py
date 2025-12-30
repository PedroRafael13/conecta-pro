"""
Schemas Pydantic para EquipmentMaintenance.
"""

from datetime import datetime
from typing import Optional

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
    serial_number: Optional[str] = Field(None, max_length=100, description="Número de série")

    client_id: Optional[str] = Field(None, description="ID do cliente")
    client_name: Optional[str] = Field(None, max_length=200, description="Nome do cliente")
    contract_id: Optional[str] = Field(None, description="ID do contrato")

    title: str = Field(..., min_length=1, max_length=200, description="Título")
    description: Optional[str] = Field(None, description="Descrição")
    symptoms: Optional[str] = Field(None, description="Sintomas reportados")
    reported_by: Optional[str] = Field(None, max_length=200, description="Reportado por")

    scheduled_date: Optional[datetime] = Field(None, description="Data agendada")
    scheduled_time: Optional[str] = Field(None, description="Hora (HH:MM)")
    estimated_duration_hours: Optional[float] = Field(None, ge=0, description="Duração estimada")
    sla_deadline: Optional[datetime] = Field(None, description="Prazo SLA")

    technician_id: Optional[str] = Field(None, description="ID do técnico")
    technician_name: Optional[str] = Field(None, max_length=200, description="Nome do técnico")

    checklist_template_id: Optional[str] = Field(None, description="Template de checklist")

    is_recurring: bool = Field(default=False, description="É recorrente?")
    recurrence_interval_days: Optional[int] = Field(None, ge=1, description="Intervalo em dias")

    notes: Optional[str] = Field(None, description="Observações")

    model_config = ConfigDict(use_enum_values=True)


class MaintenanceUpdate(BaseModel):
    """Schema para atualizar manutenção."""

    status: Optional[MaintenanceStatus] = Field(None, description="Status")
    priority: Optional[MaintenancePriority] = Field(None, description="Prioridade")

    scheduled_date: Optional[datetime] = Field(None, description="Data agendada")
    scheduled_time: Optional[str] = Field(None, description="Hora")
    sla_deadline: Optional[datetime] = Field(None, description="Prazo SLA")

    technician_id: Optional[str] = Field(None, description="ID do técnico")
    technician_name: Optional[str] = Field(None, max_length=200, description="Nome do técnico")
    team_members: Optional[list] = Field(None, description="Equipe")

    diagnosis: Optional[str] = Field(None, description="Diagnóstico")
    root_cause: Optional[str] = Field(None, description="Causa raiz")
    actions_taken: Optional[str] = Field(None, description="Ações realizadas")

    checklist_items: Optional[list] = Field(None, description="Itens do checklist")
    checklist_score: Optional[float] = Field(None, ge=0, le=100, description="Score checklist")

    parts_replaced: Optional[list] = Field(None, description="Peças substituídas")

    labor_cost: Optional[float] = Field(None, ge=0, description="Custo mão de obra")
    parts_cost: Optional[float] = Field(None, ge=0, description="Custo peças")
    transport_cost: Optional[float] = Field(None, ge=0, description="Custo transporte")
    is_billable: Optional[bool] = Field(None, description="Cobrável?")

    technical_report: Optional[str] = Field(None, description="Relatório técnico")
    recommendations: Optional[list] = Field(None, description="Recomendações")

    needs_followup: Optional[bool] = Field(None, description="Precisa follow-up?")
    followup_date: Optional[datetime] = Field(None, description="Data follow-up")
    followup_notes: Optional[str] = Field(None, description="Notas follow-up")

    notes: Optional[str] = Field(None, description="Observações")
    internal_notes: Optional[str] = Field(None, description="Notas internas")

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
    serial_number: Optional[str]

    client_id: Optional[str]
    client_name: Optional[str]
    contract_id: Optional[str]

    title: str
    description: Optional[str]
    symptoms: Optional[str]
    reported_by: Optional[str]
    reported_at: Optional[datetime]

    scheduled_date: Optional[datetime]
    scheduled_time: Optional[str]
    estimated_duration_hours: Optional[float]
    sla_deadline: Optional[datetime]

    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    actual_duration_hours: Optional[float]

    technician_id: Optional[str]
    technician_name: Optional[str]
    team_members: Optional[list]

    checklist_template_id: Optional[str]
    checklist_items: Optional[list]
    checklist_score: Optional[float]

    diagnosis: Optional[str]
    root_cause: Optional[str]
    is_warranty_repair: bool

    actions_taken: Optional[str]
    firmware_updated: bool
    firmware_version_before: Optional[str]
    firmware_version_after: Optional[str]
    settings_changed: Optional[dict]

    parts_replaced: Optional[list]
    parts_requested: Optional[list]

    labor_cost: Optional[float]
    parts_cost: Optional[float]
    transport_cost: Optional[float]
    other_costs: Optional[float]
    total_cost: Optional[float]
    is_billable: bool
    invoice_id: Optional[str]

    equipment_status_after: Optional[str]
    problem_resolved: bool
    needs_followup: bool
    followup_date: Optional[datetime]
    followup_notes: Optional[str]

    photos_before: Optional[list]
    photos_after: Optional[list]
    photos_parts: Optional[list]

    technical_report: Optional[str]
    recommendations: Optional[list]

    client_signature: Optional[str]
    signed_by: Optional[str]
    signed_at: Optional[datetime]

    response_time_hours: Optional[float]
    resolution_time_hours: Optional[float]
    sla_met: Optional[bool]

    is_recurring: bool
    recurrence_interval_days: Optional[int]
    next_maintenance_date: Optional[datetime]
    parent_maintenance_id: Optional[str]

    notes: Optional[str]
    tags: Optional[list]

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

    search: Optional[str] = Field(None, description="Busca textual")
    maintenance_type: Optional[MaintenanceType] = Field(None, description="Tipo")
    status: Optional[MaintenanceStatus] = Field(None, description="Status")
    priority: Optional[MaintenancePriority] = Field(None, description="Prioridade")
    equipment_id: Optional[str] = Field(None, description="Equipamento")
    client_id: Optional[str] = Field(None, description="Cliente")
    technician_id: Optional[str] = Field(None, description="Técnico")
    is_overdue: Optional[bool] = Field(None, description="Atrasadas")
    is_warranty: Optional[bool] = Field(None, description="Em garantia")
    problem_resolved: Optional[bool] = Field(None, description="Problema resolvido")
    needs_followup: Optional[bool] = Field(None, description="Precisa follow-up")
    date_from: Optional[datetime] = Field(None, description="Data inicial")
    date_to: Optional[datetime] = Field(None, description="Data final")

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
    by_status: dict = Field(default_factory=dict, description="Por status")
    by_type: dict = Field(default_factory=dict, description="Por tipo")
    by_priority: dict = Field(default_factory=dict, description="Por prioridade")

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
