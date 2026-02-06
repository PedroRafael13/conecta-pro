"""
Schemas Pydantic para o modulo de Predicao de Turnover.

Define os schemas de entrada, saida e validacao para todos os
endpoints da API de turnover.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
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
    recomendacao_acao: Optional[str] = None
    dados_brutos: Optional[Dict[str, Any]] = None


class RiskFactorResponse(RiskFactorBase):
    """Schema de resposta para fator de risco."""

    id: UUID
    peso: Decimal
    valor_atual: Decimal
    valor_normalizado: Decimal
    contribuicao_score: Decimal
    threshold_violado: bool
    recomendacao_acao: Optional[str] = None
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
    features_usadas: Dict[str, Any] = Field(default_factory=dict)
    metricas_modelo: Optional[Dict[str, Any]] = None
    valido_ate: Optional[datetime] = None
    calculado_por: Optional[UUID] = None


class PredictionResponse(PredictionBase):
    """Schema de resposta para predicao."""

    id: UUID
    data_calculo: datetime
    score_risco: Decimal
    nivel: NivelRisco
    modelo_versao: str
    features_usadas: Dict[str, Any]
    metricas_modelo: Optional[Dict[str, Any]] = None
    valido_ate: Optional[datetime] = None
    recalculado: bool
    is_alerta_necessario: bool
    is_critico: bool
    fatores: List[RiskFactorResponse] = Field(default_factory=list)
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
    principais_fatores: List[RiskFactorSummary] = Field(default_factory=list)


class PredictionListResponse(TurnoverBaseSchema):
    """Schema de lista paginada de predicoes."""

    items: List[PredictionSummary]
    total: int
    skip: int
    limit: int
    nivel_filtro: Optional[NivelRisco] = None


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
    score_anterior: Optional[Decimal] = Field(None, ge=0, le=100)
    variacao_score: Optional[Decimal] = None
    nivel_atual: NivelRisco
    nivel_anterior: Optional[NivelRisco] = None
    enviado_para: List[str] = Field(default_factory=list)
    prioridade: int = Field(default=3, ge=1, le=5)
    expira_em: Optional[datetime] = None
    dados_extras: Optional[Dict[str, Any]] = None


class AlertResponse(AlertBase):
    """Schema de resposta para alerta."""

    id: UUID
    prediction_id: UUID
    condominium_id: UUID
    score_atual: Decimal
    score_anterior: Optional[Decimal] = None
    variacao_score: Optional[Decimal] = None
    nivel_atual: NivelRisco
    nivel_anterior: Optional[NivelRisco] = None
    enviado_para: List[str]
    visualizado: bool
    data_visualizacao: Optional[datetime] = None
    visualizado_por: Optional[UUID] = None
    acao_tomada: Optional[str] = None
    acao_por: Optional[UUID] = None
    data_acao: Optional[datetime] = None
    prioridade: int
    expira_em: Optional[datetime] = None
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

    items: List[AlertSummary]
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

    motivo: Optional[str] = Field(
        None,
        max_length=500,
        description="Motivo do recalculo manual",
    )


class RecalcularBatchRequest(TurnoverBaseSchema):
    """Schema para recalculo em lote."""

    funcionario_ids: Optional[List[UUID]] = Field(
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
    score_anterior: Optional[Decimal] = None
    score_novo: Decimal
    nivel_anterior: Optional[NivelRisco] = None
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
    erros: List[Dict[str, Any]] = Field(default_factory=list)


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
    distribuicao_niveis: List[DashboardDistribuicaoNivel]

    # Alertas
    alertas_pendentes: int
    alertas_ultimo_mes: int

    # Top fatores
    fatores_mais_frequentes: List[DashboardFatorFrequente]

    # Tendencia
    tendencia_30_dias: List[DashboardTendencia]

    # Comparativo
    variacao_score_medio_mensal: Optional[Decimal] = None
    funcionarios_risco_crescente: int = 0
    funcionarios_risco_decrescente: int = 0

    # Meta
    data_atualizacao: datetime


class DashboardFiltro(TurnoverBaseSchema):
    """Filtro para dashboard."""

    condominium_id: UUID
    setor_id: Optional[UUID] = None
    cargo_id: Optional[UUID] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None


# =============================================================================
# Historico Schemas
# =============================================================================

class HistoricoItemResponse(TurnoverBaseSchema):
    """Item do historico de predicoes."""

    predicao_id: UUID
    data_calculo: datetime
    score_risco: Decimal
    nivel: NivelRisco
    variacao_anterior: Optional[Decimal] = None
    alertas_gerados: int
    principais_fatores: List[RiskFactorSummary]


class HistoricoResponse(TurnoverBaseSchema):
    """Historico completo de predicoes do funcionario."""

    funcionario_id: UUID
    total_predicoes: int
    predicao_atual: Optional[PredictionResponse] = None
    score_minimo: Optional[Decimal] = None
    score_maximo: Optional[Decimal] = None
    score_medio: Optional[Decimal] = None
    tendencia: str = Field(
        default="estavel",
        description="estavel, crescente, decrescente",
    )
    historico: List[HistoricoItemResponse]


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
    recomendacoes_comuns: List[str]


class FatoresListResponse(TurnoverBaseSchema):
    """Lista de fatores agregados."""

    items: List[FatorAgregadoResponse]
    total_fatores: int
    categoria_filtro: Optional[CategoriaFator] = None


# =============================================================================
# Filtros e Queries
# =============================================================================

class PredictionFilter(TurnoverBaseSchema):
    """Filtros para consulta de predicoes."""

    condominium_id: UUID
    nivel: Optional[NivelRisco] = None
    score_minimo: Optional[Decimal] = Field(None, ge=0, le=100)
    score_maximo: Optional[Decimal] = Field(None, ge=0, le=100)
    apenas_alerta: bool = False
    setor_id: Optional[UUID] = None
    cargo_id: Optional[UUID] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None

    @field_validator("score_maximo")
    @classmethod
    def validar_score_maximo(
        cls,
        v: Optional[Decimal],
        info
    ) -> Optional[Decimal]:
        """Valida que score_maximo >= score_minimo."""
        if v is not None:
            score_minimo = info.data.get("score_minimo")
            if score_minimo is not None and v < score_minimo:
                raise ValueError(
                    "score_maximo deve ser maior ou igual a score_minimo"
                )
        return v


class AlertFilter(TurnoverBaseSchema):
    """Filtros para consulta de alertas."""

    condominium_id: UUID
    tipo: Optional[TipoAlerta] = None
    visualizado: Optional[bool] = None
    prioridade_maxima: Optional[int] = Field(None, ge=1, le=5)
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None


# =============================================================================
# Features Configuration Schema
# =============================================================================

class FeatureConfig(TurnoverBaseSchema):
    """Configuracao de uma feature do modelo."""

    nome: str
    categoria: CategoriaFator
    peso: Decimal = Field(..., ge=0, le=1)
    descricao: str
    threshold_alto: Optional[Decimal] = None
    threshold_baixo: Optional[Decimal] = None
    threshold_negativo: Optional[Decimal] = None
    threshold_critico: Optional[Decimal] = None
    ativo: bool = True


class FeaturesConfigResponse(TurnoverBaseSchema):
    """Lista de configuracoes de features."""

    features: List[FeatureConfig]
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
    filtros: Optional[PredictionFilter] = None


class ExportResponse(TurnoverBaseSchema):
    """Resposta de exportacao."""

    arquivo_url: str
    nome_arquivo: str
    tamanho_bytes: int
    total_registros: int
    expira_em: datetime
