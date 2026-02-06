"""
Schemas Pydantic v2 para Pesquisa de Clima Operacional.

Define schemas para validacao de entrada e saida de dados,
seguindo padroes de API REST e documentacao OpenAPI.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from modules.retention.climate.models.climate_models import (
    AlertSeverity,
    ClimateDimension,
    EntityType,
    QuestionType,
    SurveyFrequency,
)


# =============================================================================
# Question Schemas
# =============================================================================


class QuestionSchema(BaseModel):
    """Schema para uma pergunta da pesquisa."""

    id: str = Field(..., min_length=1, max_length=50, description="ID unico da pergunta")
    texto: str = Field(..., min_length=5, max_length=500, description="Texto da pergunta")
    tipo: QuestionType = Field(default=QuestionType.ESCALA, description="Tipo de pergunta")
    dimensao: ClimateDimension = Field(..., description="Dimensao avaliada")
    ordem: int = Field(default=0, ge=0, description="Ordem de exibicao")
    obrigatoria: bool = Field(default=True, description="Se e obrigatoria")
    permite_comentario: bool = Field(default=False, description="Permite comentario adicional")


# =============================================================================
# Survey Schemas
# =============================================================================


class SurveyBase(BaseModel):
    """Schema base para pesquisa de clima."""

    nome: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Nome da pesquisa",
        examples=["Pesquisa de Clima Q1 2025"],
    )
    descricao: Optional[str] = Field(
        None,
        max_length=2000,
        description="Descricao detalhada da pesquisa",
    )
    frequencia: SurveyFrequency = Field(
        default=SurveyFrequency.MENSAL,
        description="Frequencia de aplicacao",
    )


class SurveyCreate(SurveyBase):
    """Schema para criacao de pesquisa."""

    perguntas: List[QuestionSchema] = Field(
        default_factory=list,
        min_length=1,
        description="Lista de perguntas",
    )
    data_inicio: Optional[datetime] = Field(
        None,
        description="Data de inicio (default: agora)",
    )
    data_fim: Optional[datetime] = Field(
        None,
        description="Data de termino (opcional)",
    )
    empresa_id: Optional[str] = Field(
        None,
        description="ID da empresa",
    )
    usar_perguntas_padrao: bool = Field(
        default=False,
        description="Usar perguntas padrao do sistema",
    )

    @model_validator(mode="after")
    def validate_dates(self) -> "SurveyCreate":
        """Valida datas de inicio e fim."""
        if self.data_inicio and self.data_fim:
            if self.data_inicio >= self.data_fim:
                raise ValueError("data_inicio deve ser anterior a data_fim")
        return self


class SurveyUpdate(BaseModel):
    """Schema para atualizacao de pesquisa."""

    nome: Optional[str] = Field(None, min_length=3, max_length=200)
    descricao: Optional[str] = Field(None, max_length=2000)
    frequencia: Optional[SurveyFrequency] = None
    perguntas: Optional[List[QuestionSchema]] = None
    ativo: Optional[bool] = None
    data_fim: Optional[datetime] = None


class SurveyResponse(SurveyBase):
    """Schema de resposta para pesquisa."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    perguntas: List[Dict[str, Any]]
    ativo: bool
    data_inicio: datetime
    data_fim: Optional[datetime]
    empresa_id: Optional[str]
    total_respostas: int
    score_medio: float
    total_perguntas: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]


class SurveyListResponse(BaseModel):
    """Schema para listagem paginada de pesquisas."""

    items: List[SurveyResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SurveyActiveResponse(BaseModel):
    """Schema para pesquisa ativa com perguntas formatadas."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    nome: str
    descricao: Optional[str]
    perguntas: List[QuestionSchema]
    total_perguntas: int
    tempo_estimado_minutos: int = Field(
        default=5,
        description="Tempo estimado para responder",
    )


# =============================================================================
# Response Schemas (Respostas da Pesquisa)
# =============================================================================


class ResponseCreate(BaseModel):
    """
    Schema para criacao de resposta (anonima).

    O funcionario_id sera convertido em hash pelo service.
    """

    survey_id: str = Field(..., description="ID da pesquisa")
    funcionario_id: str = Field(
        ...,
        description="ID do funcionario (sera anonimizado)",
    )
    posto_id: Optional[str] = Field(None, description="ID do posto")
    equipe_id: Optional[str] = Field(None, description="ID da equipe")
    empresa_id: Optional[str] = Field(None, description="ID da empresa")
    cliente_id: Optional[str] = Field(None, description="ID do cliente")
    respostas: Dict[str, int] = Field(
        ...,
        description="Respostas: {pergunta_id: valor 1-4}",
        examples=[{"sat_posto": 3, "rel_supervisor": 4, "carga_trabalho": 2}],
    )
    comentarios: Optional[Dict[str, str]] = Field(
        None,
        description="Comentarios opcionais por pergunta",
    )
    tempo_resposta_segundos: int = Field(
        ...,
        ge=0,
        description="Tempo gasto para responder",
    )

    @model_validator(mode="after")
    def validate_respostas(self) -> "ResponseCreate":
        """Valida que respostas estao na escala 1-4."""
        for pergunta_id, valor in self.respostas.items():
            if not isinstance(valor, int) or valor < 1 or valor > 4:
                raise ValueError(
                    f"Resposta para '{pergunta_id}' deve ser entre 1 e 4, recebido: {valor}"
                )
        return self


class ResponseSummary(BaseModel):
    """Schema resumido de resposta (para listagem)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    survey_id: str
    periodo: str
    data_resposta: datetime
    score_calculado: float
    scores_por_dimensao: Dict[str, float]
    is_complete: bool
    tempo_resposta_segundos: int


class ResponseDetail(ResponseSummary):
    """Schema detalhado de resposta."""

    posto_id: Optional[str]
    equipe_id: Optional[str]
    empresa_id: Optional[str]
    respostas: Dict[str, Any]
    comentarios: Optional[Dict[str, str]]


class ResponseConfirmation(BaseModel):
    """Schema de confirmacao de resposta."""

    success: bool = True
    message: str = "Resposta registrada com sucesso"
    score: float = Field(..., description="Score calculado")
    classificacao: str = Field(..., description="Classificacao do score")


# =============================================================================
# Score Schemas
# =============================================================================


class ClimateScoreBase(BaseModel):
    """Schema base para score de clima."""

    entidade_tipo: EntityType
    periodo: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}$",
        description="Periodo no formato YYYY-MM",
        examples=["2025-01"],
    )
    score: float = Field(..., ge=0, le=100, description="Score geral")


class ClimateScoreResponse(ClimateScoreBase):
    """Schema de resposta para score."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    entidade_id: str
    entidade_nome: Optional[str]
    empresa_id: Optional[str]
    scores_dimensao: Dict[str, float]
    tendencia: float
    total_respostas: int
    taxa_participacao: float
    fatores_positivos: List[str]
    fatores_negativos: List[str]
    enps_score: float
    enps_promotores: int
    enps_neutros: int
    enps_detratores: int
    classificacao: str
    has_alert: bool
    alertas: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class ClimateScoreListResponse(BaseModel):
    """Schema para listagem de scores."""

    items: List[ClimateScoreResponse]
    total: int


# =============================================================================
# Trend Schemas
# =============================================================================


class TrendPoint(BaseModel):
    """Ponto de dados para tendencia."""

    periodo: str
    score: float
    total_respostas: int
    variacao: float = 0.0


class ClimateTrend(BaseModel):
    """Schema para tendencia de clima."""

    entidade_tipo: EntityType
    entidade_id: str
    entidade_nome: Optional[str]
    periodos: List[TrendPoint]
    score_atual: float
    score_medio: float
    melhor_periodo: Optional[str]
    pior_periodo: Optional[str]
    tendencia_geral: str = Field(
        ...,
        description="alta, estavel, queda",
    )
    variacao_total: float


class DimensionTrend(BaseModel):
    """Schema para tendencia por dimensao."""

    dimensao: ClimateDimension
    periodos: List[TrendPoint]
    score_atual: float
    tendencia: str


# =============================================================================
# Dashboard Schemas
# =============================================================================


class ScoreByDimension(BaseModel):
    """Score por dimensao."""

    dimensao: ClimateDimension
    score: float
    total_respostas: int
    tendencia: float
    classificacao: str


class EntityScore(BaseModel):
    """Score de uma entidade."""

    entidade_id: str
    entidade_nome: str
    score: float
    total_respostas: int
    tendencia: float
    classificacao: str


class ClimateDashboard(BaseModel):
    """Schema para dashboard geral de clima."""

    periodo_atual: str
    score_geral: float
    score_anterior: float
    variacao: float
    classificacao: str
    total_respostas: int
    taxa_participacao: float
    enps_score: float
    scores_por_dimensao: List[ScoreByDimension]
    top_postos: List[EntityScore]
    bottom_postos: List[EntityScore]
    top_equipes: List[EntityScore]
    bottom_equipes: List[EntityScore]
    alertas_ativos: int
    tendencia_6_meses: List[TrendPoint]
    ultima_atualizacao: datetime


class ClimateByPosto(BaseModel):
    """Schema para clima por posto."""

    posto_id: str
    posto_nome: str
    cliente_nome: Optional[str]
    periodo: str
    score: float
    score_anterior: float
    variacao: float
    classificacao: str
    total_respostas: int
    total_funcionarios: int
    taxa_participacao: float
    scores_dimensao: Dict[str, float]
    enps_score: float
    fatores_positivos: List[str]
    fatores_negativos: List[str]
    alertas: List[Dict[str, Any]]


class ClimateByEquipe(BaseModel):
    """Schema para clima por equipe."""

    equipe_id: str
    equipe_nome: str
    supervisor_nome: Optional[str]
    periodo: str
    score: float
    score_anterior: float
    variacao: float
    classificacao: str
    total_respostas: int
    total_funcionarios: int
    taxa_participacao: float
    scores_dimensao: Dict[str, float]
    enps_score: float
    postos_vinculados: int


class ClimateByEmpresa(BaseModel):
    """Schema para clima da empresa."""

    empresa_id: str
    empresa_nome: str
    periodo: str
    score: float
    score_anterior: float
    variacao: float
    classificacao: str
    total_respostas: int
    total_funcionarios: int
    taxa_participacao: float
    scores_dimensao: Dict[str, float]
    enps_score: float
    total_postos: int
    total_equipes: int
    postos_criticos: int
    equipes_criticas: int


# =============================================================================
# Alert Schemas
# =============================================================================


class AlertResponse(BaseModel):
    """Schema de resposta para alerta."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    empresa_id: Optional[str]
    entidade_tipo: str
    entidade_id: str
    entidade_nome: Optional[str]
    periodo: str
    tipo_alerta: str
    dimensao: Optional[str]
    severidade: str
    mensagem: str
    score_atual: float
    score_anterior: Optional[float]
    variacao: float
    resolvido: bool
    resolvido_em: Optional[datetime]
    resolvido_por: Optional[str]
    notas_resolucao: Optional[str]
    created_at: datetime


class AlertListResponse(BaseModel):
    """Schema para listagem de alertas."""

    items: List[AlertResponse]
    total: int
    total_criticos: int
    total_altos: int
    total_medios: int
    total_baixos: int


class AlertResolve(BaseModel):
    """Schema para resolver alerta."""

    notas_resolucao: Optional[str] = Field(
        None,
        max_length=1000,
        description="Notas sobre a resolucao",
    )


# =============================================================================
# Filter Schemas
# =============================================================================


class ClimateFilter(BaseModel):
    """Schema para filtros de busca."""

    empresa_id: Optional[str] = None
    posto_id: Optional[str] = None
    equipe_id: Optional[str] = None
    cliente_id: Optional[str] = None
    periodo_inicio: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}$",
        description="Periodo inicial YYYY-MM",
    )
    periodo_fim: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}$",
        description="Periodo final YYYY-MM",
    )
    score_min: Optional[float] = Field(None, ge=0, le=100)
    score_max: Optional[float] = Field(None, ge=0, le=100)
    dimensao: Optional[ClimateDimension] = None
    apenas_alertas: bool = False

    @model_validator(mode="after")
    def validate_score_range(self) -> "ClimateFilter":
        """Valida range de scores."""
        if self.score_min is not None and self.score_max is not None:
            if self.score_min > self.score_max:
                raise ValueError("score_min deve ser menor ou igual a score_max")
        return self


# =============================================================================
# Calculation Schemas
# =============================================================================


class CalculationRequest(BaseModel):
    """Schema para solicitacao de calculo de scores."""

    periodo: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}$",
        description="Periodo para calculo YYYY-MM",
    )
    empresa_id: Optional[str] = None
    recalcular: bool = Field(
        default=False,
        description="Recalcular mesmo se ja existir",
    )


class CalculationResult(BaseModel):
    """Schema para resultado do calculo."""

    periodo: str
    scores_calculados: int
    alertas_gerados: int
    tempo_processamento_ms: int
    sucesso: bool
    erros: List[str] = []


# =============================================================================
# Analytics Schemas
# =============================================================================


class DimensionAnalysis(BaseModel):
    """Analise detalhada de uma dimensao."""

    dimensao: ClimateDimension
    score_atual: float
    score_anterior: float
    variacao: float
    classificacao: str
    tendencia_3_meses: str
    perguntas_mais_positivas: List[str]
    perguntas_mais_negativas: List[str]
    recomendacoes: List[str]


class ClimateAnalytics(BaseModel):
    """Schema para analytics de clima."""

    periodo: str
    empresa_id: Optional[str]
    score_geral: float
    analise_dimensoes: List[DimensionAnalysis]
    correlacoes: Dict[str, float]
    insights: List[str]
    recomendacoes_prioritarias: List[str]
    risco_turnover: str = Field(
        ...,
        description="baixo, medio, alto, critico",
    )
    previsao_proximo_periodo: float
