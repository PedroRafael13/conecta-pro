"""
Schemas Pydantic para Perfil Operacional.

Definicao de todos os schemas de entrada/saida para a API de perfil.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict, field_validator


class ProfileDimensionEnum(str, Enum):
    """Dimensoes do perfil operacional."""

    VIGILANCIA = "vigilancia"
    COMUNICACAO = "comunicacao"
    RESILIENCIA = "resiliencia"
    LIDERANCA = "lideranca"


class PostTypeEnum(str, Enum):
    """Tipos de posto com perfil ideal."""

    CFTV = "cftv"
    PORTARIA = "portaria"
    RECEPCAO = "recepcao"
    RONDA = "ronda"
    EVENTO = "evento"
    SUPERVISOR = "supervisor"
    SEGURANCA_ARMADA = "seguranca_armada"
    VIGILANTE = "vigilante"


class MatchNivelEnum(str, Enum):
    """Niveis de match."""

    BAIXO = "baixo"
    MEDIO = "medio"
    ALTO = "alto"
    EXCELENTE = "excelente"


# ============================================================
# Schemas de Perguntas
# ============================================================


class ProfileQuestionBase(BaseModel):
    """Schema base para pergunta do questionario."""

    codigo: str = Field(..., min_length=1, max_length=10, description="Codigo unico da pergunta")
    texto: str = Field(..., min_length=10, max_length=500, description="Texto da pergunta")
    dimensao: ProfileDimensionEnum = Field(..., description="Dimensao avaliada")
    ordem: int = Field(..., ge=1, le=100, description="Ordem de exibicao")
    peso: float = Field(default=1.0, ge=0.1, le=5.0, description="Peso no calculo")


class ProfileQuestionCreate(ProfileQuestionBase):
    """Schema para criacao de pergunta."""

    versao: str = Field(default="1.0.0", max_length=20)
    condominium_id: Optional[str] = None


class ProfileQuestionUpdate(BaseModel):
    """Schema para atualizacao de pergunta."""

    texto: Optional[str] = Field(None, min_length=10, max_length=500)
    ordem: Optional[int] = Field(None, ge=1, le=100)
    peso: Optional[float] = Field(None, ge=0.1, le=5.0)
    ativo: Optional[bool] = None


class ProfileQuestionResponse(ProfileQuestionBase):
    """Schema de resposta para pergunta."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    ativo: bool
    versao: str
    condominium_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class QuestionnaireResponse(BaseModel):
    """Schema de resposta do questionario completo."""

    perguntas: List[ProfileQuestionResponse]
    total_perguntas: int
    versao: str
    dimensoes: List[str]
    escala: Dict[str, str] = Field(
        default={
            "1": "Discordo totalmente",
            "2": "Discordo parcialmente",
            "3": "Concordo parcialmente",
            "4": "Concordo totalmente",
        }
    )


# ============================================================
# Schemas de Respostas do Questionario
# ============================================================


class RespostaItem(BaseModel):
    """Uma resposta individual."""

    pergunta_id: str = Field(..., description="ID ou codigo da pergunta")
    valor: int = Field(..., ge=1, le=4, description="Valor da resposta (1-4)")

    @field_validator("valor")
    @classmethod
    def validar_valor(cls, v: int) -> int:
        """Valida que o valor esta entre 1 e 4."""
        if v < 1 or v > 4:
            raise ValueError("Valor deve estar entre 1 e 4")
        return v


class SubmitRespostasRequest(BaseModel):
    """Schema para submissao de respostas do questionario."""

    funcionario_id: str = Field(..., description="UUID do funcionario")
    respostas: Dict[str, int] = Field(
        ...,
        description="Respostas no formato {pergunta_id: valor}",
        min_length=20,
    )
    tempo_resposta_segundos: Optional[int] = Field(
        None, ge=0, description="Tempo total em segundos"
    )
    condominium_id: Optional[str] = None

    @field_validator("respostas")
    @classmethod
    def validar_respostas(cls, v: Dict[str, int]) -> Dict[str, int]:
        """Valida todas as respostas."""
        if len(v) < 20:
            raise ValueError(f"Questionario incompleto. Esperado 20 respostas, recebido {len(v)}")

        for pergunta_id, valor in v.items():
            if valor < 1 or valor > 4:
                raise ValueError(f"Resposta invalida para {pergunta_id}: valor deve estar entre 1 e 4")

        return v


class SaveProgressRequest(BaseModel):
    """Schema para salvamento de progresso."""

    funcionario_id: str
    respostas_parciais: Dict[str, int] = Field(default_factory=dict)
    ultima_pergunta: int = Field(ge=0, le=20)
    condominium_id: Optional[str] = None


class ProgressResponse(BaseModel):
    """Schema de resposta do progresso."""

    funcionario_id: str
    respostas_salvas: Dict[str, int]
    ultima_pergunta: int
    total_perguntas: int
    percentual_completo: float
    em_andamento: bool


# ============================================================
# Schemas de Perfil Operacional
# ============================================================


class DimensionScore(BaseModel):
    """Score de uma dimensao."""

    dimensao: ProfileDimensionEnum
    score: int = Field(..., ge=0, le=100)
    nivel: str = Field(..., description="baixo, medio, alto ou excelente")
    descricao: str


class OperationalProfileBase(BaseModel):
    """Schema base do perfil operacional."""

    vigilancia: int = Field(..., ge=0, le=100)
    comunicacao: int = Field(..., ge=0, le=100)
    resiliencia: int = Field(..., ge=0, le=100)
    lideranca: int = Field(..., ge=0, le=100)
    perfil_predominante: ProfileDimensionEnum


class OperationalProfileResponse(OperationalProfileBase):
    """Schema de resposta do perfil operacional."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    funcionario_id: str
    data_avaliacao: datetime
    versao_questionario: str
    tempo_resposta_segundos: Optional[int] = None
    is_valid: bool
    invalidation_reason: Optional[str] = None
    condominium_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Campos computados
    score_medio: float = Field(default=0.0)
    dimensao_mais_fraca: str = Field(default="")


class OperationalProfileDetail(OperationalProfileResponse):
    """Schema detalhado do perfil com analise."""

    scores_detalhados: List[DimensionScore]
    radar_chart_data: Dict[str, int]
    recomendacoes: List[str]
    pontos_fortes: List[str]
    pontos_desenvolvimento: List[str]
    tipos_posto_recomendados: List[str]


class OperationalProfileHistory(BaseModel):
    """Schema para historico de perfis."""

    profiles: List[OperationalProfileResponse]
    total: int
    evolucao: Dict[str, List[Dict[str, Any]]]  # {dimensao: [{data, score}]}


# ============================================================
# Schemas de Match
# ============================================================


class PostMatchBase(BaseModel):
    """Schema base de match."""

    funcionario_id: str
    posto_id: str
    posto_tipo: PostTypeEnum
    score_match: float = Field(..., ge=0, le=100)
    recomendado: bool
    nivel_match: MatchNivelEnum


class PostMatchResponse(PostMatchBase):
    """Schema de resposta de match."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    profile_id: Optional[str] = None
    fatores_positivos: List[str]
    fatores_negativos: List[str]
    scores_detalhados: Optional[Dict[str, Any]] = None
    calculado_em: datetime
    valido_ate: Optional[datetime] = None
    condominium_id: Optional[str] = None
    created_at: datetime


class PostMatchDetail(PostMatchResponse):
    """Schema detalhado de match com analise."""

    analise_dimensoes: List[Dict[str, Any]]
    gap_analysis: Dict[str, int]  # Diferenca entre perfil e ideal
    sugestoes_desenvolvimento: List[str]
    probabilidade_sucesso: float


class CalculateMatchRequest(BaseModel):
    """Schema para calculo de match."""

    funcionario_id: str
    posto_id: str
    posto_tipo: PostTypeEnum
    condominium_id: Optional[str] = None


class BulkMatchRequest(BaseModel):
    """Schema para calculo de match em lote."""

    funcionario_id: str
    posto_ids: List[str] = Field(..., min_length=1, max_length=50)
    condominium_id: Optional[str] = None


class BestMatchesResponse(BaseModel):
    """Schema de resposta com melhores matches."""

    funcionario_id: str
    matches: List[PostMatchResponse]
    total: int
    melhor_tipo_posto: Optional[PostTypeEnum] = None
    pior_tipo_posto: Optional[PostTypeEnum] = None


class BestFuncionariosResponse(BaseModel):
    """Schema de resposta com melhores funcionarios para posto."""

    posto_id: str
    posto_tipo: PostTypeEnum
    matches: List[PostMatchResponse]
    total: int
    media_match: float


# ============================================================
# Schemas de Tipo de Posto
# ============================================================


class IdealProfileByType(BaseModel):
    """Perfil ideal por tipo de posto."""

    tipo: PostTypeEnum
    perfil_ideal: Dict[str, int]
    descricao: str
    requisitos_principais: List[str]


class PostTypesResponse(BaseModel):
    """Lista de tipos de posto com perfis ideais."""

    tipos: List[IdealProfileByType]
    total: int


# ============================================================
# Schemas de Dashboard
# ============================================================


class ProfileDistribution(BaseModel):
    """Distribuicao de perfis."""

    dimensao: ProfileDimensionEnum
    media: float
    minimo: int
    maximo: int
    desvio_padrao: float
    total_avaliados: int


class DashboardStats(BaseModel):
    """Estatisticas do dashboard."""

    total_avaliacoes: int
    avaliacoes_mes: int
    avaliacoes_semana: int
    media_score_geral: float

    distribuicao_perfis: Dict[str, int]  # {perfil_predominante: count}
    distribuicao_scores: List[ProfileDistribution]

    top_matches: List[PostMatchResponse]
    funcionarios_sem_perfil: int

    evolucao_mensal: List[Dict[str, Any]]  # [{mes, total, media}]


class DashboardResponse(BaseModel):
    """Resposta completa do dashboard."""

    stats: DashboardStats
    alertas: List[str]
    recomendacoes: List[str]
    ultima_atualizacao: datetime


# ============================================================
# Schemas de Lista e Paginacao
# ============================================================


class ProfileListResponse(BaseModel):
    """Lista paginada de perfis."""

    items: List[OperationalProfileResponse]
    total: int
    page: int
    page_size: int
    pages: int


class MatchListResponse(BaseModel):
    """Lista paginada de matches."""

    items: List[PostMatchResponse]
    total: int
    page: int
    page_size: int
    pages: int


class ProfileFilter(BaseModel):
    """Filtros para busca de perfis."""

    funcionario_id: Optional[str] = None
    perfil_predominante: Optional[ProfileDimensionEnum] = None
    score_minimo: Optional[int] = Field(None, ge=0, le=100)
    score_maximo: Optional[int] = Field(None, ge=0, le=100)
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    condominium_id: Optional[str] = None
    apenas_validos: bool = True


class MatchFilter(BaseModel):
    """Filtros para busca de matches."""

    funcionario_id: Optional[str] = None
    posto_id: Optional[str] = None
    posto_tipo: Optional[PostTypeEnum] = None
    score_minimo: Optional[float] = Field(None, ge=0, le=100)
    apenas_recomendados: bool = False
    nivel_match: Optional[MatchNivelEnum] = None
    condominium_id: Optional[str] = None
