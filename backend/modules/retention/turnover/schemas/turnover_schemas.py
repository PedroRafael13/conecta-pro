"""
Schemas Pydantic para o modulo de Predicao de Turnover.

Define os schemas de entrada, saida e validacao para todos os
endpoints da API de turnover.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.retention.turnover.models.turnover_models import (
    CategoriaFator,
    NivelRisco,
    TipoAlerta,
)

# =============================================================================
# Base Schemas
# =============================================================================


class TurnoverBaseSchema(BaseModel):
    """Schema base com configuracao padrao."""

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


# =============================================================================
# Risk Factor Schemas
# =============================================================================


class RiskFactorBase(TurnoverBaseSchema):
    """Schema base para fatores de risco."""

    nome: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nome identificador do fator",
    )
    categoria: CategoriaFator = Field(
        ...,
        description="Categoria do fator de risco",
    )
    descricao: str = Field(
        ...,
        min_length=1,
        description="Descricao legivel do fator",
    )


class RiskFactorCreate(RiskFactorBase):
    """Schema para criacao de fator de risco."""

    prediction_id: UUID
    peso: Decimal = Field(..., ge=0, le=1)
    valor_atual: Decimal
    valor_normalizado: Decimal = Field(..., ge=0, le=1)
    contribuicao_score: Decimal = Field(..., ge=0)
    threshold_violado: bool = False
    recomendacao_acao: str | None = None
    dados_brutos: dict[str, Any] | None = None


class RiskFactorResponse(RiskFactorBase):
    """Schema de resposta para fator de risco."""

    id: UUID
    peso: Decimal
    valor_atual: Decimal
    valor_normalizado: Decimal
    contribuicao_score: Decimal
    threshold_violado: bool
    recomendacao_acao: str | None = None
    is_critico: bool
    is_significativo: bool
    created_at: datetime


class RiskFactorSummary(TurnoverBaseSchema):
    """Schema resumido de fator de risco para listagens."""

    nome: str
    categoria: CategoriaFator
    contribuicao_score: Decimal
    threshold_violado: bool
    descricao: str


# =============================================================================
# Prediction Schemas
# =============================================================================


class PredictionBase(TurnoverBaseSchema):
    """Schema base para predicao."""

    funcionario_id: UUID = Field(
        ...,
        description="ID do funcionario avaliado",
    )
    condominium_id: UUID = Field(
        ...,
        description="ID do condominio/empresa",
    )


class PredictionCreate(PredictionBase):
    """Schema para criacao de predicao."""

    score_risco: Decimal = Field(..., ge=0, le=100)
    nivel: NivelRisco
    modelo_versao: str = Field(default="heuristic_v1.0", max_length=50)
    features_usadas: dict[str, Any] = Field(default_factory=dict)
    metricas_modelo: dict[str, Any] | None = None
    valido_ate: datetime | None = None
    calculado_por: UUID | None = None


class PredictionResponse(PredictionBase):
    """Schema de resposta para predicao."""

    id: UUID
    data_calculo: datetime
    score_risco: Decimal
    nivel: NivelRisco
    modelo_versao: str
    features_usadas: dict[str, Any]
    metricas_modelo: dict[str, Any] | None = None
    valido_ate: datetime | None = None
    recalculado: bool
    is_alerta_necessario: bool
    is_critico: bool
    fatores: list[RiskFactorResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class PredictionSummary(TurnoverBaseSchema):
    """Schema resumido de predicao para listagens."""

    id: UUID
    funcionario_id: UUID
    data_calculo: datetime
    score_risco: Decimal
    nivel: NivelRisco
    is_alerta_necessario: bool
    principais_fatores: list[RiskFactorSummary] = Field(default_factory=list)


class PredictionListResponse(TurnoverBaseSchema):
    """Schema de lista paginada de predicoes."""

    items: list[PredictionSummary]
    total: int
    skip: int
    limit: int
    nivel_filtro: NivelRisco | None = None


# =============================================================================
# Alert Schemas
# =============================================================================


class AlertBase(TurnoverBaseSchema):
    """Schema base para alerta."""

    funcionario_id: UUID
    tipo: TipoAlerta
    titulo: str = Field(..., min_length=1, max_length=200)
    mensagem: str = Field(..., min_length=1)


class AlertCreate(AlertBase):
    """Schema para criacao de alerta."""

    prediction_id: UUID
    condominium_id: UUID
    score_atual: Decimal = Field(..., ge=0, le=100)
    score_anterior: Decimal | None = Field(None, ge=0, le=100)
    variacao_score: Decimal | None = None
    nivel_atual: NivelRisco
    nivel_anterior: NivelRisco | None = None
    enviado_para: list[str] = Field(default_factory=list)
    prioridade: int = Field(default=3, ge=1, le=5)
    expira_em: datetime | None = None
    dados_extras: dict[str, Any] | None = None


class AlertResponse(AlertBase):
    """Schema de resposta para alerta."""

    id: UUID
    prediction_id: UUID
    condominium_id: UUID
    score_atual: Decimal
    score_anterior: Decimal | None = None
    variacao_score: Decimal | None = None
    nivel_atual: NivelRisco
    nivel_anterior: NivelRisco | None = None
    enviado_para: list[str]
    visualizado: bool
    data_visualizacao: datetime | None = None
    visualizado_por: UUID | None = None
    acao_tomada: str | None = None
    acao_por: UUID | None = None
    data_acao: datetime | None = None
    prioridade: int
    expira_em: datetime | None = None
    is_pendente: bool
    is_expirado: bool
    is_acao_pendente: bool
    created_at: datetime


class AlertSummary(TurnoverBaseSchema):
    """Schema resumido de alerta para listagens."""

    id: UUID
    funcionario_id: UUID
    tipo: TipoAlerta
    titulo: str
    score_atual: Decimal
    nivel_atual: NivelRisco
    visualizado: bool
    prioridade: int
    created_at: datetime


class AlertListResponse(TurnoverBaseSchema):
    """Schema de lista paginada de alertas."""

    items: list[AlertSummary]
    total: int
    skip: int
    limit: int
    apenas_pendentes: bool = False


class AlertVisualizarRequest(TurnoverBaseSchema):
    """Schema para marcar alerta como visualizado."""

    usuario_id: UUID


class AlertAcaoRequest(TurnoverBaseSchema):
    """Schema para registrar acao em alerta."""

    usuario_id: UUID
    acao: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        description="Descricao da acao tomada",
    )


# =============================================================================
# Recalcular Schemas
# =============================================================================


class RecalcularRequest(TurnoverBaseSchema):
    """Schema para solicitar recalculo de risco."""

    motivo: str | None = Field(
        None,
        max_length=500,
        description="Motivo do recalculo manual",
    )


class RecalcularBatchRequest(TurnoverBaseSchema):
    """Schema para recalculo em lote."""

    funcionario_ids: list[UUID] | None = Field(
        None,
        max_length=1000,
        description="Lista de funcionarios (None = todos)",
    )
    apenas_ativos: bool = Field(
        default=True,
        description="Recalcular apenas funcionarios ativos",
    )


class RecalcularResponse(TurnoverBaseSchema):
    """Schema de resposta para recalculo."""

    funcionario_id: UUID
    predicao_id: UUID
    score_anterior: Decimal | None = None
    score_novo: Decimal
    nivel_anterior: NivelRisco | None = None
    nivel_novo: NivelRisco
    alerta_gerado: bool
    data_calculo: datetime


class RecalcularBatchResponse(TurnoverBaseSchema):
    """Schema de resposta para recalculo em lote."""

    total_processados: int
    total_sucesso: int
    total_erros: int
    alertas_gerados: int
    tempo_execucao_segundos: float
    erros: list[dict[str, Any]] = Field(default_factory=list)


# =============================================================================
# Dashboard Schemas
# =============================================================================


class DashboardDistribuicaoNivel(TurnoverBaseSchema):
    """Distribuicao por nivel de risco."""

    nivel: NivelRisco
    quantidade: int
    percentual: Decimal


class DashboardFatorFrequente(TurnoverBaseSchema):
    """Fator de risco mais frequente."""

    nome: str
    categoria: CategoriaFator
    ocorrencias: int
    contribuicao_media: Decimal


class DashboardTendencia(TurnoverBaseSchema):
    """Tendencia temporal de risco."""

    data: datetime
    score_medio: Decimal
    total_criticos: int
    total_altos: int


class DashboardResponse(TurnoverBaseSchema):
    """Schema de resposta do dashboard."""

    # Metricas gerais
    total_funcionarios: int
    total_predicoes_ativas: int
    score_medio_geral: Decimal

    # Distribuicao por nivel
    distribuicao_niveis: list[DashboardDistribuicaoNivel]

    # Alertas
    alertas_pendentes: int
    alertas_ultimo_mes: int

    # Top fatores
    fatores_mais_frequentes: list[DashboardFatorFrequente]

    # Tendencia
    tendencia_30_dias: list[DashboardTendencia]

    # Comparativo
    variacao_score_medio_mensal: Decimal | None = None
    funcionarios_risco_crescente: int = 0
    funcionarios_risco_decrescente: int = 0

    # Meta
    data_atualizacao: datetime


class DashboardFiltro(TurnoverBaseSchema):
    """Filtro para dashboard."""

    condominium_id: UUID
    setor_id: UUID | None = None
    cargo_id: UUID | None = None
    data_inicio: datetime | None = None
    data_fim: datetime | None = None


# =============================================================================
# Historico Schemas
# =============================================================================


class HistoricoItemResponse(TurnoverBaseSchema):
    """Item do historico de predicoes."""

    predicao_id: UUID
    data_calculo: datetime
    score_risco: Decimal
    nivel: NivelRisco
    variacao_anterior: Decimal | None = None
    alertas_gerados: int
    principais_fatores: list[RiskFactorSummary]


class HistoricoResponse(TurnoverBaseSchema):
    """Historico completo de predicoes do funcionario."""

    funcionario_id: UUID
    total_predicoes: int
    predicao_atual: PredictionResponse | None = None
    score_minimo: Decimal | None = None
    score_maximo: Decimal | None = None
    score_medio: Decimal | None = None
    tendencia: str = Field(
        default="estavel",
        description="estavel, crescente, decrescente",
    )
    historico: list[HistoricoItemResponse]


# =============================================================================
# Fatores Agregados Schemas
# =============================================================================


class FatorAgregadoResponse(TurnoverBaseSchema):
    """Fator de risco agregado (estatisticas)."""

    nome: str
    categoria: CategoriaFator
    total_ocorrencias: int
    contribuicao_media: Decimal
    contribuicao_maxima: Decimal
    percentual_threshold_violado: Decimal
    funcionarios_afetados: int
    descricao_padrao: str
    recomendacoes_comuns: list[str]


class FatoresListResponse(TurnoverBaseSchema):
    """Lista de fatores agregados."""

    items: list[FatorAgregadoResponse]
    total_fatores: int
    categoria_filtro: CategoriaFator | None = None


# =============================================================================
# Filtros e Queries
# =============================================================================


class PredictionFilter(TurnoverBaseSchema):
    """Filtros para consulta de predicoes."""

    condominium_id: UUID
    nivel: NivelRisco | None = None
    score_minimo: Decimal | None = Field(None, ge=0, le=100)
    score_maximo: Decimal | None = Field(None, ge=0, le=100)
    apenas_alerta: bool = False
    setor_id: UUID | None = None
    cargo_id: UUID | None = None
    data_inicio: datetime | None = None
    data_fim: datetime | None = None

    @field_validator("score_maximo")
    @classmethod
    def validar_score_maximo(cls, v: Decimal | None, info) -> Decimal | None:
        """Valida que score_maximo >= score_minimo."""
        if v is not None:
            score_minimo = info.data.get("score_minimo")
            if score_minimo is not None and v < score_minimo:
                raise ValueError("score_maximo deve ser maior ou igual a score_minimo")
        return v


class AlertFilter(TurnoverBaseSchema):
    """Filtros para consulta de alertas."""

    condominium_id: UUID
    tipo: TipoAlerta | None = None
    visualizado: bool | None = None
    prioridade_maxima: int | None = Field(None, ge=1, le=5)
    data_inicio: datetime | None = None
    data_fim: datetime | None = None


# =============================================================================
# Features Configuration Schema
# =============================================================================


class FeatureConfig(TurnoverBaseSchema):
    """Configuracao de uma feature do modelo."""

    nome: str
    categoria: CategoriaFator
    peso: Decimal = Field(..., ge=0, le=1)
    descricao: str
    threshold_alto: Decimal | None = None
    threshold_baixo: Decimal | None = None
    threshold_negativo: Decimal | None = None
    threshold_critico: Decimal | None = None
    ativo: bool = True


class FeaturesConfigResponse(TurnoverBaseSchema):
    """Lista de configuracoes de features."""

    features: list[FeatureConfig]
    total_peso: Decimal
    modelo_versao: str


# =============================================================================
# Export Schemas
# =============================================================================


class ExportRequest(TurnoverBaseSchema):
    """Request para exportacao de dados."""

    condominium_id: UUID
    formato: str = Field(
        default="csv",
        pattern="^(csv|xlsx|json)$",
    )
    incluir_fatores: bool = True
    incluir_historico: bool = False
    filtros: PredictionFilter | None = None


class ExportResponse(TurnoverBaseSchema):
    """Resposta de exportacao."""

    arquivo_url: str
    nome_arquivo: str
    tamanho_bytes: int
    total_registros: int
    expira_em: datetime
