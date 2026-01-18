"""
Schemas Pydantic para o módulo de Onboarding Digital.

Este módulo define todos os schemas de validação e serialização
para as operações de CRUD e respostas da API de onboarding.

Classes:
    Checklist: Schemas para operações com checklists
    Step: Schemas para operações com etapas
    Progress: Schemas para operações com progresso
    Dashboard: Schemas para métricas e alertas
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    model_validator,
)

from modules.retention.onboarding.models import StepType, ProgressStatus


# =============================================================================
# Schemas Base
# =============================================================================


class MessageResponse(BaseModel):
    """Schema padrão para respostas de mensagem."""

    message: str
    success: bool = True


class PaginationParams(BaseModel):
    """Schema para parâmetros de paginação."""

    skip: int = Field(default=0, ge=0, description="Número de registros para pular")
    limit: int = Field(
        default=20, ge=1, le=100, description="Limite de registros por página"
    )


class PaginatedResponse(BaseModel):
    """Schema base para respostas paginadas."""

    total: int = Field(..., description="Total de registros")
    skip: int = Field(..., description="Registros pulados")
    limit: int = Field(..., description="Limite por página")
    pages: int = Field(..., description="Total de páginas")


# =============================================================================
# Schemas de Step (Etapa)
# =============================================================================


class StepBase(BaseModel):
    """Schema base para etapa de onboarding."""

    nome: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Nome da etapa do onboarding",
    )
    descricao: Optional[str] = Field(
        None,
        max_length=2000,
        description="Descrição detalhada da etapa",
    )
    dias_apos_admissao: int = Field(
        default=0,
        ge=0,
        le=365,
        description="Dias após admissão para conclusão",
    )
    tipo: StepType = Field(
        default=StepType.TAREFA,
        description="Tipo da etapa",
    )
    obrigatorio: bool = Field(
        default=True,
        description="Se a etapa é obrigatória",
    )
    ordem: int = Field(
        default=1,
        ge=1,
        description="Ordem de exibição da etapa",
    )
    tempo_estimado_minutos: int = Field(
        default=60,
        ge=0,
        le=9999,
        description="Tempo estimado em minutos",
    )


class StepCreate(StepBase):
    """Schema para criação de etapa."""

    checklist_id: UUID = Field(
        ...,
        description="ID do checklist pai",
    )
    responsavel_padrao_id: Optional[UUID] = Field(
        None,
        description="ID do responsável padrão",
    )
    recursos: Optional[List[str]] = Field(
        default_factory=list,
        description="Lista de recursos necessários",
    )
    instrucoes: Optional[str] = Field(
        None,
        max_length=5000,
        description="Instruções detalhadas",
    )
    link_material: Optional[str] = Field(
        None,
        max_length=500,
        description="Link para material de apoio",
    )
    permite_pular: bool = Field(
        default=False,
        description="Se permite pular a etapa",
    )
    notificar_supervisor: bool = Field(
        default=True,
        description="Notificar supervisor",
    )
    notificar_rh: bool = Field(
        default=False,
        description="Notificar RH",
    )
    dependencia_step_id: Optional[UUID] = Field(
        None,
        description="ID da etapa de dependência",
    )

    @field_validator("link_material")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Valida se o link é uma URL válida."""
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("Link deve ser uma URL válida (http:// ou https://)")
        return v


class StepUpdate(BaseModel):
    """Schema para atualização de etapa."""

    nome: Optional[str] = Field(
        None,
        min_length=3,
        max_length=200,
    )
    descricao: Optional[str] = Field(
        None,
        max_length=2000,
    )
    dias_apos_admissao: Optional[int] = Field(
        None,
        ge=0,
        le=365,
    )
    tipo: Optional[StepType] = None
    obrigatorio: Optional[bool] = None
    ordem: Optional[int] = Field(None, ge=1)
    tempo_estimado_minutos: Optional[int] = Field(None, ge=0, le=9999)
    responsavel_padrao_id: Optional[UUID] = None
    recursos: Optional[List[str]] = None
    instrucoes: Optional[str] = Field(None, max_length=5000)
    link_material: Optional[str] = Field(None, max_length=500)
    permite_pular: Optional[bool] = None
    notificar_supervisor: Optional[bool] = None
    notificar_rh: Optional[bool] = None
    dependencia_step_id: Optional[UUID] = None


class StepResponse(StepBase):
    """Schema de resposta para etapa."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    checklist_id: UUID
    responsavel_padrao_id: Optional[UUID] = None
    recursos: Optional[List[str]] = None
    instrucoes: Optional[str] = None
    link_material: Optional[str] = None
    permite_pular: bool = False
    notificar_supervisor: bool = True
    notificar_rh: bool = False
    dependencia_step_id: Optional[UUID] = None
    metadata_info: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    tem_dependencia: bool = False


# =============================================================================
# Schemas de Checklist
# =============================================================================


class ChecklistBase(BaseModel):
    """Schema base para checklist de onboarding."""

    nome: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Nome do checklist",
    )
    descricao: Optional[str] = Field(
        None,
        max_length=2000,
        description="Descrição do checklist",
    )
    dias_duracao_total: int = Field(
        default=90,
        ge=1,
        le=365,
        description="Duração total em dias",
    )


class ChecklistCreate(ChecklistBase):
    """Schema para criação de checklist."""

    condominium_id: UUID = Field(
        ...,
        description="ID do condomínio/empresa",
    )
    cargo_id: Optional[UUID] = Field(
        None,
        description="ID do cargo associado",
    )
    departamento: Optional[str] = Field(
        None,
        max_length=100,
        description="Departamento associado",
    )
    is_default: bool = Field(
        default=False,
        description="Se é o checklist padrão",
    )
    etapas: Optional[List[StepCreate]] = Field(
        default=None,
        description="Etapas do checklist (criação em lote)",
    )


class ChecklistUpdate(BaseModel):
    """Schema para atualização de checklist."""

    nome: Optional[str] = Field(
        None,
        min_length=3,
        max_length=200,
    )
    descricao: Optional[str] = Field(
        None,
        max_length=2000,
    )
    cargo_id: Optional[UUID] = None
    departamento: Optional[str] = Field(
        None,
        max_length=100,
    )
    dias_duracao_total: Optional[int] = Field(
        None,
        ge=1,
        le=365,
    )
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class ChecklistResponse(ChecklistBase):
    """Schema de resposta para checklist."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    cargo_id: Optional[UUID] = None
    departamento: Optional[str] = None
    condominium_id: UUID
    is_active: bool = True
    is_default: bool = False
    metadata_info: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    total_etapas: int = 0
    etapas_obrigatorias: int = 0


class ChecklistDetailResponse(ChecklistResponse):
    """Schema de resposta detalhada para checklist com etapas."""

    etapas: List[StepResponse] = Field(
        default_factory=list,
        description="Lista de etapas do checklist",
    )


class ChecklistListResponse(PaginatedResponse):
    """Schema de lista de checklists."""

    items: List[ChecklistResponse]


# =============================================================================
# Schemas de Progress (Progresso)
# =============================================================================


class ProgressBase(BaseModel):
    """Schema base para progresso de onboarding."""

    status: ProgressStatus = Field(
        default=ProgressStatus.PENDENTE,
        description="Status atual do progresso",
    )
    observacoes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Observações sobre o progresso",
    )


class ProgressCreate(BaseModel):
    """Schema para criação de progresso."""

    funcionario_id: UUID = Field(
        ...,
        description="ID do funcionário",
    )
    checklist_id: UUID = Field(
        ...,
        description="ID do checklist",
    )
    step_id: UUID = Field(
        ...,
        description="ID da etapa",
    )
    data_prevista: date = Field(
        ...,
        description="Data prevista para conclusão",
    )
    supervisor_id: Optional[UUID] = Field(
        None,
        description="ID do supervisor responsável",
    )
    responsavel_id: Optional[UUID] = Field(
        None,
        description="ID do responsável pela execução",
    )


class ProgressUpdate(BaseModel):
    """Schema para atualização de progresso."""

    status: Optional[ProgressStatus] = None
    observacoes: Optional[str] = Field(
        None,
        max_length=2000,
    )
    data_prevista: Optional[date] = None
    supervisor_id: Optional[UUID] = None
    responsavel_id: Optional[UUID] = None
    evidencia_url: Optional[str] = Field(
        None,
        max_length=500,
    )


class ProgressComplete(BaseModel):
    """Schema para completar uma etapa."""

    observacoes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Observações sobre a conclusão",
    )
    evidencia_url: Optional[str] = Field(
        None,
        max_length=500,
        description="URL da evidência de conclusão",
    )
    avaliacao_nota: Optional[float] = Field(
        None,
        ge=0,
        le=10,
        description="Nota de avaliação (0-10)",
    )
    avaliacao_comentario: Optional[str] = Field(
        None,
        max_length=1000,
        description="Comentário da avaliação",
    )


class ProgressResponse(BaseModel):
    """Schema de resposta para progresso."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    funcionario_id: UUID
    checklist_id: UUID
    step_id: UUID
    status: ProgressStatus
    data_prevista: date
    data_inicio: Optional[datetime] = None
    data_conclusao: Optional[datetime] = None
    observacoes: Optional[str] = None
    supervisor_id: Optional[UUID] = None
    responsavel_id: Optional[UUID] = None
    notificacoes_enviadas: int = 0
    ultima_notificacao_at: Optional[datetime] = None
    evidencia_url: Optional[str] = None
    avaliacao_nota: Optional[float] = None
    avaliacao_comentario: Optional[str] = None
    metadata_info: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    dias_restantes: int = 0
    esta_atrasado: bool = False
    tempo_execucao_dias: Optional[int] = None


class ProgressDetailResponse(ProgressResponse):
    """Schema de resposta detalhada para progresso com etapa."""

    step: Optional[StepResponse] = None


class ProgressListResponse(PaginatedResponse):
    """Schema de lista de progressos."""

    items: List[ProgressResponse]


# =============================================================================
# Schemas de Funcionário Onboarding
# =============================================================================


class FuncionarioOnboardingCreate(BaseModel):
    """Schema para iniciar onboarding de funcionário."""

    funcionario_id: UUID = Field(
        ...,
        description="ID do funcionário",
    )
    checklist_id: Optional[UUID] = Field(
        None,
        description="ID do checklist (opcional, usa padrão se não informado)",
    )
    data_admissao: date = Field(
        ...,
        description="Data de admissão do funcionário",
    )
    supervisor_id: Optional[UUID] = Field(
        None,
        description="ID do supervisor responsável",
    )


class FuncionarioOnboardingResponse(BaseModel):
    """Schema de resposta para onboarding de funcionário."""

    model_config = ConfigDict(from_attributes=True)

    funcionario_id: UUID
    checklist_id: UUID
    checklist_nome: str
    data_admissao: date
    supervisor_id: Optional[UUID] = None
    total_etapas: int = 0
    etapas_concluidas: int = 0
    etapas_pendentes: int = 0
    etapas_atrasadas: int = 0
    progresso_percentual: float = 0.0
    proxima_etapa: Optional[ProgressDetailResponse] = None
    progressos: List[ProgressDetailResponse] = Field(default_factory=list)


# =============================================================================
# Schemas de Dashboard e Métricas
# =============================================================================


class OnboardingAlert(BaseModel):
    """Schema para alerta de onboarding."""

    id: UUID
    tipo: str = Field(..., description="Tipo do alerta (atrasado, proximo_vencer)")
    nivel: str = Field(..., description="Nível (critico, alto, medio, baixo)")
    funcionario_id: UUID
    funcionario_nome: Optional[str] = None
    step_id: UUID
    step_nome: Optional[str] = None
    checklist_nome: Optional[str] = None
    dias_atraso: int = 0
    supervisor_id: Optional[UUID] = None
    supervisor_nome: Optional[str] = None
    mensagem: str
    created_at: datetime


class OnboardingStats(BaseModel):
    """Schema para estatísticas de onboarding."""

    total_funcionarios_em_onboarding: int = 0
    total_funcionarios_concluidos: int = 0
    total_etapas_pendentes: int = 0
    total_etapas_em_andamento: int = 0
    total_etapas_concluidas: int = 0
    total_etapas_atrasadas: int = 0
    tempo_medio_conclusao_dias: float = 0.0
    taxa_conclusao_no_prazo: float = 0.0
    taxa_aprovacao_avaliacoes: float = 0.0
    nota_media_avaliacoes: float = 0.0
    por_departamento: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    por_tipo_etapa: Dict[str, int] = Field(default_factory=dict)
    por_status: Dict[str, int] = Field(default_factory=dict)


class OnboardingDashboard(BaseModel):
    """Schema para dashboard de onboarding."""

    stats: OnboardingStats
    alerts: List[OnboardingAlert] = Field(default_factory=list)
    funcionarios_ativos: int = 0
    funcionarios_atrasados: int = 0
    checklists_ativos: int = 0
    tendencia_conclusao: List[Dict[str, Any]] = Field(default_factory=list)
    ultimas_conclusoes: List[Dict[str, Any]] = Field(default_factory=list)


class OnboardingFilter(BaseModel):
    """Schema para filtros de listagem."""

    condominium_id: Optional[UUID] = None
    funcionario_id: Optional[UUID] = None
    checklist_id: Optional[UUID] = None
    supervisor_id: Optional[UUID] = None
    departamento: Optional[str] = None
    status: Optional[ProgressStatus] = None
    tipo: Optional[StepType] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    apenas_atrasados: bool = False
    apenas_obrigatorios: bool = False
    search: Optional[str] = Field(
        None,
        max_length=100,
        description="Termo de busca",
    )

    @model_validator(mode="after")
    def validate_dates(self) -> "OnboardingFilter":
        """Valida se data_inicio <= data_fim."""
        if self.data_inicio and self.data_fim:
            if self.data_inicio > self.data_fim:
                raise ValueError("data_inicio deve ser anterior ou igual a data_fim")
        return self


class BulkProgressUpdate(BaseModel):
    """Schema para atualização em lote de progressos."""

    progress_ids: List[UUID] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="IDs dos progressos a atualizar",
    )
    status: Optional[ProgressStatus] = None
    observacoes: Optional[str] = Field(
        None,
        max_length=2000,
    )


class OnboardingReport(BaseModel):
    """Schema para relatório de onboarding."""

    periodo_inicio: date
    periodo_fim: date
    condominium_id: UUID
    total_iniciados: int = 0
    total_concluidos: int = 0
    total_em_andamento: int = 0
    total_cancelados: int = 0
    tempo_medio_dias: float = 0.0
    taxa_conclusao: float = 0.0
    taxa_atraso: float = 0.0
    por_cargo: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    por_departamento: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    evolucao_diaria: List[Dict[str, Any]] = Field(default_factory=list)
    etapas_mais_demoradas: List[Dict[str, Any]] = Field(default_factory=list)
    etapas_mais_atrasadas: List[Dict[str, Any]] = Field(default_factory=list)
    gerado_em: datetime = Field(default_factory=datetime.utcnow)
