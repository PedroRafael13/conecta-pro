"""
Schemas Pydantic para Rondas de Inspecao.

Author: Conecta PRO Team
Date: 2026-01-23
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# =============================================================================
# ENUMS PARA SCHEMAS
# =============================================================================


class InspectionRoundStatusEnum(str):
    AGENDADA = "agendada"
    EM_ANDAMENTO = "em_andamento"
    PAUSADA = "pausada"
    CONCLUIDA = "concluida"
    CANCELADA = "cancelada"


class InspectorRoleEnum(str):
    GERENTE_OPERACIONAL = "gerente_operacional"
    SUPERVISOR_OPERACIONAL = "supervisor_operacional"
    INSPETOR_OPERACIONAL = "inspetor_operacional"
    LIDER_SERVICO = "lider_servico"


class CheckpointTypeEnum(str):
    VERIFICACAO_POSTO = "verificacao_posto"
    VERIFICACAO_FUNCIONARIO = "verificacao_funcionario"
    REGISTRO_OCORRENCIA = "registro_ocorrencia"
    MEDIDA_DISCIPLINAR = "medida_disciplinar"
    OBSERVACAO_GERAL = "observacao_geral"
    FOTO_EVIDENCIA = "foto_evidencia"


class CheckpointStatusEnum(str):
    CONFORME = "conforme"
    NAO_CONFORME = "nao_conforme"
    PENDENTE = "pendente"
    COM_OCORRENCIA = "com_ocorrencia"


# =============================================================================
# CHECKPOINT SCHEMAS
# =============================================================================


class CheckpointCreate(BaseModel):
    """Schema para criacao de checkpoint."""

    post_id: Optional[UUID] = None
    post_name: Optional[str] = None
    client_id: Optional[UUID] = None
    client_name: Optional[str] = None
    checkpoint_type: str = Field(default="verificacao_posto")
    status: str = Field(default="pendente")
    employee_id: Optional[UUID] = None
    employee_name: Optional[str] = None
    employee_cpf: Optional[str] = None
    employee_position: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    observations: Optional[str] = None
    infraction_category: Optional[str] = None
    infraction_severity: Optional[str] = None
    photos: Optional[List[dict]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CheckpointUpdate(BaseModel):
    """Schema para atualizacao de checkpoint."""

    status: Optional[str] = None
    description: Optional[str] = None
    observations: Optional[str] = None
    infraction_category: Optional[str] = None
    infraction_severity: Optional[str] = None
    photos: Optional[List[dict]] = None


class CheckpointResponse(BaseModel):
    """Schema de resposta de checkpoint."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    inspection_round_id: UUID
    post_id: Optional[UUID] = None
    post_name: Optional[str] = None
    client_id: Optional[UUID] = None
    client_name: Optional[str] = None
    checkpoint_type: str
    status: str
    employee_id: Optional[UUID] = None
    employee_name: Optional[str] = None
    employee_cpf: Optional[str] = None
    employee_position: Optional[str] = None
    occurrence_id: Optional[UUID] = None
    occurrence_code: Optional[str] = None
    disciplinary_action_id: Optional[UUID] = None
    disciplinary_action_code: Optional[str] = None
    disciplinary_action_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    observations: Optional[str] = None
    infraction_category: Optional[str] = None
    infraction_severity: Optional[str] = None
    photos: Optional[List[dict]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    sequence: int
    created_at: datetime


class CheckpointWithOccurrence(CheckpointResponse):
    """Checkpoint com detalhes da ocorrencia."""

    occurrence_title: Optional[str] = None
    occurrence_status: Optional[str] = None
    disciplinary_action_status: Optional[str] = None


# =============================================================================
# INSPECTION ROUND SCHEMAS
# =============================================================================


class InspectionRoundCreate(BaseModel):
    """Schema para criacao de ronda."""

    tenant_id: UUID
    inspector_id: UUID
    inspector_name: str = Field(..., min_length=2, max_length=255)
    inspector_role: str = Field(default="supervisor_operacional")
    scheduled_date: Optional[datetime] = None
    posts_to_visit: Optional[List[UUID]] = None
    observations: Optional[str] = None


class InspectionRoundUpdate(BaseModel):
    """Schema para atualizacao de ronda."""

    scheduled_date: Optional[datetime] = None
    posts_to_visit: Optional[List[UUID]] = None
    observations: Optional[str] = None
    summary: Optional[str] = None


class InspectionRoundResponse(BaseModel):
    """Schema de resposta de ronda."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    tenant_id: UUID
    inspector_id: UUID
    inspector_name: str
    inspector_role: str
    status: str
    scheduled_date: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    posts_to_visit: Optional[List[str]] = None
    posts_visited: Optional[List[str]] = None
    total_checkpoints: int
    total_occurrences: int
    total_disciplinary_actions: int
    total_employees_checked: int
    observations: Optional[str] = None
    summary: Optional[str] = None
    start_latitude: Optional[float] = None
    start_longitude: Optional[float] = None
    end_latitude: Optional[float] = None
    end_longitude: Optional[float] = None
    total_distance_km: Optional[float] = None
    progress_percentage: float = 0.0
    is_active: bool
    created_at: datetime
    updated_at: datetime
    checkpoints: Optional[List[CheckpointResponse]] = None


class InspectionRoundSummary(BaseModel):
    """Resumo de ronda para listagem."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    inspector_name: str
    inspector_role: str
    status: str
    scheduled_date: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_checkpoints: int
    total_occurrences: int
    total_disciplinary_actions: int
    progress_percentage: float = 0.0
    created_at: datetime


class InspectionRoundListResponse(BaseModel):
    """Resposta paginada de rondas."""

    items: List[InspectionRoundSummary]
    total: int
    page: int
    page_size: int
    pages: int


class InspectionRoundFilter(BaseModel):
    """Filtros para listagem de rondas."""

    inspector_id: Optional[UUID] = None
    inspector_role: Optional[str] = None
    status: Optional[str] = None
    post_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    has_occurrences: Optional[bool] = None
    has_disciplinary_actions: Optional[bool] = None


# =============================================================================
# ACTION SCHEMAS
# =============================================================================


class StartRoundRequest(BaseModel):
    """Request para iniciar ronda."""

    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CompleteRoundRequest(BaseModel):
    """Request para concluir ronda."""

    summary: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class RegisterOccurrenceRequest(BaseModel):
    """Request para registrar ocorrencia durante ronda."""

    post_id: UUID
    post_name: str
    employee_id: Optional[UUID] = None
    employee_name: Optional[str] = None
    employee_cpf: Optional[str] = None
    employee_position: Optional[str] = None

    # Dados da ocorrencia
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    category: str = Field(default="comportamento")
    severity: str = Field(default="media")
    type: str = Field(default="incidente")
    priority: str = Field(default="normal")

    # Localizacao
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_description: Optional[str] = None

    # Fotos
    photos: Optional[List[dict]] = None


class ApplyDisciplinaryRequest(BaseModel):
    """Request para aplicar medida disciplinar durante ronda."""

    # Checkpoint/Ocorrencia de origem
    checkpoint_id: Optional[UUID] = None
    occurrence_id: Optional[UUID] = None

    # Dados do funcionario
    employee_id: UUID
    employee_name: str
    employee_cpf: str
    employee_position: Optional[str] = None
    employee_admission_date: Optional[datetime] = None

    # Local
    post_id: UUID
    client_id: Optional[UUID] = None

    # Tipo de medida
    action_type: str = Field(
        ...,
        description="advertencia_verbal, advertencia_escrita, suspensao"
    )

    # Motivo
    reason_category: str = Field(
        ...,
        description="falta, atraso, insubordinacao, indisciplina, negligencia, etc"
    )
    reason_description: str = Field(..., min_length=20)

    # Data do incidente
    incident_date: datetime

    # Suspensao (se aplicavel)
    suspension_days: Optional[int] = Field(None, ge=1, le=30)
    suspension_start_date: Optional[datetime] = None

    # Testemunhas
    witness_1_name: Optional[str] = None
    witness_1_cpf: Optional[str] = None
    witness_2_name: Optional[str] = None
    witness_2_cpf: Optional[str] = None


class RegisterOccurrenceResponse(BaseModel):
    """Response para registro de ocorrência durante ronda."""

    model_config = ConfigDict(from_attributes=True)

    success: bool = Field(..., description="Se o registro foi bem-sucedido")
    occurrence_id: UUID = Field(..., description="ID da ocorrência criada")
    checkpoint_id: Optional[UUID] = Field(None, description="ID do checkpoint atualizado")
    message: str = Field(default="Ocorrência registrada com sucesso")

    # Dados da ocorrência criada
    occurrence_type: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None


class ApplyDisciplinaryResponse(BaseModel):
    """Response para aplicação de medida disciplinar durante ronda."""

    model_config = ConfigDict(from_attributes=True)

    success: bool = Field(..., description="Se a aplicação foi bem-sucedida")
    disciplinary_action_id: UUID = Field(..., description="ID da medida disciplinar criada")
    occurrence_id: Optional[UUID] = Field(None, description="ID da ocorrência vinculada")
    checkpoint_id: Optional[UUID] = Field(None, description="ID do checkpoint vinculado")
    message: str = Field(default="Medida disciplinar aplicada com sucesso")

    # Dados da medida criada
    action_type: Optional[str] = None
    status: Optional[str] = None
    employee_name: Optional[str] = None
    created_at: Optional[datetime] = None


# =============================================================================
# DASHBOARD SCHEMAS
# =============================================================================


class InspectorStats(BaseModel):
    """Estatisticas por inspetor."""

    inspector_id: UUID
    inspector_name: str
    inspector_role: str
    total_rounds: int
    total_occurrences: int
    total_disciplinary_actions: int
    avg_duration_minutes: float
    last_round_date: Optional[datetime] = None


class InspectionDashboardStats(BaseModel):
    """Estatisticas do dashboard de rondas."""

    # Resumo geral
    total_rounds: int
    rounds_in_progress: int
    rounds_completed: int
    rounds_scheduled: int

    # Ocorrencias
    total_occurrences: int
    occurrences_pending: int
    occurrences_resolved: int

    # Medidas disciplinares
    total_disciplinary_actions: int
    warnings_count: int
    suspensions_count: int

    # Por periodo
    rounds_today: int
    rounds_this_week: int
    rounds_this_month: int

    # Top inspetores
    top_inspectors: List[InspectorStats]

    # Postos mais visitados
    most_visited_posts: List[dict]

    # Categorias de infracoes mais comuns
    top_infraction_categories: List[dict]
