"""
Schemas Pydantic para Maintenance (Manutenção).
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.facilities.models.maintenance import (
    MaintenancePriority,
    MaintenanceStatus,
    MaintenanceType,
)


class MaintenanceBase(BaseModel):
    """Schema base para Maintenance."""

    title: str = Field(..., min_length=1, max_length=255, description="Título")
    description: Optional[str] = Field(None, max_length=5000, description="Descrição")
    maintenance_type: MaintenanceType = Field(
        default=MaintenanceType.CORRETIVA,
        description="Tipo de manutenção",
    )
    priority: MaintenancePriority = Field(
        default=MaintenancePriority.MEDIUM,
        description="Prioridade",
    )
    area_id: Optional[str] = Field(None, description="ID da área")
    client_id: Optional[str] = Field(None, description="ID do cliente")
    equipment_id: Optional[str] = Field(None, description="ID do equipamento")
    service_request_id: Optional[str] = Field(None, description="ID da solicitação")
    scheduled_date: Optional[date] = Field(None, description="Data agendada")
    deadline: Optional[date] = Field(None, description="Prazo limite")
    assigned_to: Optional[str] = Field(None, description="Responsável")
    team_ids: Optional[List[str]] = Field(None, description="IDs da equipe")
    estimated_hours: float = Field(default=0.0, ge=0, description="Horas estimadas")
    estimated_cost: float = Field(default=0.0, ge=0, description="Custo estimado")
    notes: Optional[str] = Field(None, max_length=2000, description="Observações")
    is_recurring: bool = Field(default=False, description="É recorrente")
    recurrence_pattern: Optional[str] = Field(None, description="Padrão de recorrência")
    recurrence_interval: Optional[int] = Field(None, ge=1, description="Intervalo")
    requires_approval: bool = Field(default=False, description="Requer aprovação")


class MaintenanceCreate(MaintenanceBase):
    """Schema para criação de Maintenance."""

    code: Optional[str] = Field(None, max_length=20, description="Código (auto-gerado se vazio)")
    requested_by: Optional[str] = Field(None, description="Solicitante")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        """Valida e normaliza o código da manutenção."""
        if v:
            return v.upper().strip()
        return v

    @field_validator("deadline")
    @classmethod
    def validate_deadline(cls, v: Optional[date], info) -> Optional[date]:
        """Valida que o prazo não é anterior à data agendada."""
        if v and info.data.get("scheduled_date"):
            if v < info.data["scheduled_date"]:
                raise ValueError("Prazo não pode ser anterior à data agendada")
        return v


class MaintenanceUpdate(BaseModel):
    """Schema para atualização parcial de Maintenance."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    maintenance_type: Optional[MaintenanceType] = None
    status: Optional[MaintenanceStatus] = None
    priority: Optional[MaintenancePriority] = None
    area_id: Optional[str] = None
    equipment_id: Optional[str] = None
    scheduled_date: Optional[date] = None
    deadline: Optional[date] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    team_ids: Optional[List[str]] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    actual_hours: Optional[float] = Field(None, ge=0)
    estimated_cost: Optional[float] = Field(None, ge=0)
    actual_cost: Optional[float] = Field(None, ge=0)
    labor_cost: Optional[float] = Field(None, ge=0)
    material_cost: Optional[float] = Field(None, ge=0)
    materials_used: Optional[Dict[str, Any]] = None
    work_performed: Optional[str] = Field(None, max_length=5000)
    root_cause: Optional[str] = Field(None, max_length=2000)
    preventive_actions: Optional[str] = Field(None, max_length=2000)
    notes: Optional[str] = Field(None, max_length=2000)
    before_photos: Optional[List[str]] = None
    after_photos: Optional[List[str]] = None
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)
    feedback: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None


class MaintenanceApprove(BaseModel):
    """Schema para aprovação de manutenção."""

    notes: Optional[str] = Field(None, max_length=500, description="Observações")


class MaintenanceReject(BaseModel):
    """Schema para rejeição de manutenção."""

    rejection_reason: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Motivo da rejeição",
    )


class MaintenanceComplete(BaseModel):
    """Schema para conclusão de manutenção."""

    work_performed: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Trabalho realizado",
    )
    actual_hours: float = Field(..., ge=0, description="Horas trabalhadas")
    actual_cost: Optional[float] = Field(None, ge=0, description="Custo real")
    labor_cost: Optional[float] = Field(None, ge=0, description="Custo mão de obra")
    material_cost: Optional[float] = Field(None, ge=0, description="Custo materiais")
    materials_used: Optional[Dict[str, Any]] = Field(None, description="Materiais utilizados")
    root_cause: Optional[str] = Field(None, max_length=2000, description="Causa raiz")
    preventive_actions: Optional[str] = Field(
        None, max_length=2000, description="Ações preventivas"
    )
    after_photos: Optional[List[str]] = Field(None, description="Fotos depois")
    notes: Optional[str] = Field(None, max_length=2000, description="Observações")


class MaintenanceResponse(BaseModel):
    """Schema de resposta para Maintenance."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    title: str
    description: Optional[str]
    maintenance_type: str
    status: str
    priority: str
    area_id: Optional[str]
    client_id: Optional[str]
    equipment_id: Optional[str]
    service_request_id: Optional[str]
    scheduled_date: Optional[date]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    deadline: Optional[date]
    assigned_to: Optional[str]
    team_ids: Optional[List[str]]
    requested_by: Optional[str]
    estimated_hours: float
    actual_hours: float
    estimated_cost: float
    actual_cost: float
    labor_cost: float
    material_cost: float
    materials_used: Optional[Dict[str, Any]]
    work_performed: Optional[str]
    root_cause: Optional[str]
    preventive_actions: Optional[str]
    notes: Optional[str]
    is_recurring: bool
    recurrence_pattern: Optional[str]
    recurrence_interval: Optional[int]
    next_occurrence: Optional[date]
    requires_approval: bool
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    before_photos: Optional[List[str]]
    after_photos: Optional[List[str]]
    satisfaction_rating: Optional[int]
    feedback: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Propriedades calculadas
    is_overdue: bool
    is_pending: bool
    is_in_progress: bool
    is_completed: bool
    cost_variance: float
    hours_variance: float
    duration_days: Optional[int]


class MaintenanceListResponse(BaseModel):
    """Schema para listagem paginada de Maintenances."""

    items: List[MaintenanceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class MaintenanceFilter(BaseModel):
    """Schema para filtros de busca de Maintenances."""

    search: Optional[str] = Field(None, description="Busca por título ou código")
    maintenance_type: Optional[MaintenanceType] = None
    status: Optional[MaintenanceStatus] = None
    priority: Optional[MaintenancePriority] = None
    area_id: Optional[str] = None
    client_id: Optional[str] = None
    equipment_id: Optional[str] = None
    assigned_to: Optional[str] = None
    scheduled_start: Optional[date] = None
    scheduled_end: Optional[date] = None
    is_overdue: Optional[bool] = None
    is_recurring: Optional[bool] = None
    requires_approval: Optional[bool] = None


class MaintenanceStats(BaseModel):
    """Estatísticas de manutenções."""

    total: int = Field(..., description="Total de manutenções")
    by_type: Dict[str, int] = Field(..., description="Por tipo")
    by_status: Dict[str, int] = Field(..., description="Por status")
    by_priority: Dict[str, int] = Field(..., description="Por prioridade")
    overdue_count: int = Field(..., description="Atrasadas")
    pending_approval: int = Field(..., description="Aguardando aprovação")
    total_estimated_cost: float = Field(..., description="Custo estimado total")
    total_actual_cost: float = Field(..., description="Custo real total")
    avg_completion_hours: float = Field(..., description="Média de horas para conclusão")
    avg_satisfaction: Optional[float] = Field(None, description="Média de satisfação")
