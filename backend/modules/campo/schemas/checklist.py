"""
Schemas de Checklist - Modulo Campo
===================================

Pydantic schemas para validacao e serializacao de Checklists.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# =============================================================================
# ENUMS (importados do model)
# =============================================================================
from modules.campo.models.checklist import (
    TipoServico,
    TipoResposta,
    CategoriaItem,
)


# =============================================================================
# SCHEMAS AUXILIARES
# =============================================================================

class OpcaoItem(BaseModel):
    """Schema para opcao de multipla escolha."""
    valor: str
    label: str
    descricao: Optional[str] = None


class AlertaConfig(BaseModel):
    """Schema para configuracao de alerta."""
    condicao: str = Field(..., max_length=100)  # "valor < 10", "resposta = nao"
    mensagem: str = Field(..., max_length=300)
    severidade: str = Field("warning", pattern="^(info|warning|critical)$")


# =============================================================================
# TEMPLATE SCHEMAS
# =============================================================================

class ChecklistTemplateCreate(BaseModel):
    """Schema para criacao de template."""
    model_config = ConfigDict(from_attributes=True)

    nome: str = Field(..., min_length=3, max_length=200)
    descricao: Optional[str] = None
    tipo_servico: TipoServico = TipoServico.GERAL
    categoria_equipamento: Optional[str] = Field(None, max_length=100)

    is_obrigatorio: bool = False
    permite_itens_adicionais: bool = False
    tempo_estimado_minutos: int = 15
    pontuacao_maxima: Optional[int] = None

    visivel_cliente: bool = False

    tags: Optional[List[str]] = None


class ChecklistTemplateUpdate(BaseModel):
    """Schema para atualizacao de template."""
    model_config = ConfigDict(from_attributes=True)

    nome: Optional[str] = Field(None, min_length=3, max_length=200)
    descricao: Optional[str] = None
    tipo_servico: Optional[TipoServico] = None
    categoria_equipamento: Optional[str] = Field(None, max_length=100)

    is_obrigatorio: Optional[bool] = None
    permite_itens_adicionais: Optional[bool] = None
    tempo_estimado_minutos: Optional[int] = None
    pontuacao_maxima: Optional[int] = None

    visivel_cliente: Optional[bool] = None
    is_ativo: Optional[bool] = None

    tags: Optional[List[str]] = None


class ChecklistTemplateRead(BaseModel):
    """Schema de leitura de template."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    codigo: str
    nome: str
    descricao: Optional[str] = None
    tipo_servico: TipoServico
    categoria_equipamento: Optional[str] = None
    versao: str

    is_obrigatorio: bool
    permite_itens_adicionais: bool
    tempo_estimado_minutos: int
    pontuacao_maxima: Optional[int] = None

    is_ativo: bool
    visivel_cliente: bool

    total_itens: int = 0
    itens_obrigatorios: int = 0

    tags: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime


class ChecklistTemplateListItem(BaseModel):
    """Schema resumido para listagem de templates."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    codigo: str
    nome: str
    tipo_servico: TipoServico
    categoria_equipamento: Optional[str] = None

    is_obrigatorio: bool
    is_ativo: bool

    total_itens: int = 0
    tempo_estimado_minutos: int

    created_at: datetime


# =============================================================================
# ITEM SCHEMAS
# =============================================================================

class ChecklistItemCreate(BaseModel):
    """Schema para criacao de item."""
    model_config = ConfigDict(from_attributes=True)

    template_id: UUID

    ordem: Optional[int] = None
    secao: Optional[str] = Field(None, max_length=100)
    secao_ordem: int = 1

    pergunta: str = Field(..., min_length=3, max_length=500)
    descricao: Optional[str] = None
    categoria: CategoriaItem = CategoriaItem.VERIFICACAO

    tipo_resposta: TipoResposta = TipoResposta.SIM_NAO
    opcoes: Optional[List[OpcaoItem]] = None

    valor_minimo: Optional[Decimal] = None
    valor_maximo: Optional[Decimal] = None
    unidade_medida: Optional[str] = Field(None, max_length=20)
    valor_padrao: Optional[str] = Field(None, max_length=500)

    obrigatorio: bool = True

    condicional_item_id: Optional[UUID] = None
    condicional_valor: Optional[str] = Field(None, max_length=100)

    pontos: int = 0
    peso: Decimal = Decimal("1.0")

    gera_alerta: bool = False
    alerta_condicao: Optional[str] = Field(None, max_length=100)
    alerta_mensagem: Optional[str] = Field(None, max_length=300)
    alerta_severidade: str = "warning"


class ChecklistItemUpdate(BaseModel):
    """Schema para atualizacao de item."""
    model_config = ConfigDict(from_attributes=True)

    ordem: Optional[int] = None
    secao: Optional[str] = Field(None, max_length=100)
    secao_ordem: Optional[int] = None

    pergunta: Optional[str] = Field(None, min_length=3, max_length=500)
    descricao: Optional[str] = None
    categoria: Optional[CategoriaItem] = None

    tipo_resposta: Optional[TipoResposta] = None
    opcoes: Optional[List[OpcaoItem]] = None

    valor_minimo: Optional[Decimal] = None
    valor_maximo: Optional[Decimal] = None
    unidade_medida: Optional[str] = Field(None, max_length=20)
    valor_padrao: Optional[str] = Field(None, max_length=500)

    obrigatorio: Optional[bool] = None

    condicional_item_id: Optional[UUID] = None
    condicional_valor: Optional[str] = Field(None, max_length=100)

    pontos: Optional[int] = None
    peso: Optional[Decimal] = None

    gera_alerta: Optional[bool] = None
    alerta_condicao: Optional[str] = Field(None, max_length=100)
    alerta_mensagem: Optional[str] = Field(None, max_length=300)
    alerta_severidade: Optional[str] = None

    is_active: Optional[bool] = None


class ChecklistItemRead(BaseModel):
    """Schema de leitura de item."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    template_id: UUID

    ordem: int
    secao: Optional[str] = None
    secao_ordem: int

    pergunta: str
    descricao: Optional[str] = None
    categoria: CategoriaItem

    tipo_resposta: TipoResposta
    opcoes: Optional[List[Any]] = None

    valor_minimo: Optional[Decimal] = None
    valor_maximo: Optional[Decimal] = None
    unidade_medida: Optional[str] = None
    valor_padrao: Optional[str] = None

    obrigatorio: bool

    condicional_item_id: Optional[UUID] = None
    condicional_valor: Optional[str] = None

    pontos: int
    peso: Decimal

    gera_alerta: bool
    alerta_condicao: Optional[str] = None
    alerta_mensagem: Optional[str] = None
    alerta_severidade: str

    is_active: bool


# =============================================================================
# RESPOSTA SCHEMAS
# =============================================================================

class ChecklistRespostaCreate(BaseModel):
    """Schema para criacao de resposta."""
    model_config = ConfigDict(from_attributes=True)

    ordem_servico_id: UUID
    template_id: UUID
    item_id: UUID

    # O valor pode ser de diferentes tipos
    valor: Union[str, int, float, bool, list, dict, None] = None

    # URLs de arquivos
    foto_url: Optional[str] = None
    fotos_urls: Optional[List[str]] = None
    assinatura_url: Optional[str] = None
    arquivo_url: Optional[str] = None

    # Geolocalizacao
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

    observacao: Optional[str] = None


class ChecklistRespostaUpdate(BaseModel):
    """Schema para atualizacao de resposta."""
    model_config = ConfigDict(from_attributes=True)

    valor: Union[str, int, float, bool, list, dict, None] = None

    foto_url: Optional[str] = None
    fotos_urls: Optional[List[str]] = None
    assinatura_url: Optional[str] = None

    observacao: Optional[str] = None


class ChecklistRespostaRead(BaseModel):
    """Schema de leitura de resposta."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ordem_servico_id: UUID
    template_id: UUID
    item_id: UUID

    # Valores
    resposta_texto: Optional[str] = None
    resposta_numero: Optional[Decimal] = None
    resposta_boolean: Optional[bool] = None
    resposta_data: Optional[datetime] = None
    resposta_json: Optional[Any] = None

    # Arquivos
    resposta_foto_url: Optional[str] = None
    resposta_fotos_urls: Optional[List[str]] = None
    resposta_assinatura_url: Optional[str] = None
    resposta_arquivo_url: Optional[str] = None

    # Validacao
    is_valida: bool
    mensagem_validacao: Optional[str] = None

    # Alerta
    gerou_alerta: bool
    alerta_data: Optional[dict] = None

    # Metadata
    respondido_por: Optional[UUID] = None
    respondido_at: datetime
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    observacao: Optional[str] = None


# =============================================================================
# PREENCHIDO SCHEMAS
# =============================================================================

class ChecklistPreenchidoCreate(BaseModel):
    """Schema para iniciar preenchimento."""
    model_config = ConfigDict(from_attributes=True)

    ordem_servico_id: UUID
    template_id: UUID
    preenchido_offline: bool = False


class ChecklistPreenchidoRead(BaseModel):
    """Schema de leitura de checklist preenchido."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ordem_servico_id: UUID
    template_id: UUID

    iniciado: bool
    iniciado_at: Optional[datetime] = None
    concluido: bool
    concluido_at: Optional[datetime] = None

    total_itens: int
    itens_respondidos: int
    itens_obrigatorios: int
    itens_obrigatorios_respondidos: int
    percentual_conclusao: Decimal

    pontuacao_obtida: int
    pontuacao_maxima: int
    percentual_conformidade: Optional[Decimal] = None

    total_alertas: int
    alertas: Optional[List[Any]] = None

    preenchido_por: Optional[UUID] = None
    preenchido_offline: bool
    observacoes_finais: Optional[str] = None

    created_at: datetime
    updated_at: datetime


# =============================================================================
# ACTION SCHEMAS
# =============================================================================

class ChecklistIniciarRequest(BaseModel):
    """Schema para iniciar checklist."""
    template_id: UUID


class ChecklistResponderRequest(BaseModel):
    """Schema para responder item."""
    item_id: UUID
    valor: Union[str, int, float, bool, list, dict, None] = None
    foto_url: Optional[str] = None
    fotos_urls: Optional[List[str]] = None
    assinatura_url: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    observacao: Optional[str] = None


class ChecklistConcluirRequest(BaseModel):
    """Schema para concluir checklist."""
    observacoes_finais: Optional[str] = None


class ReordenarItensRequest(BaseModel):
    """Schema para reordenar itens."""
    nova_ordem: List[UUID]


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class ChecklistComItens(BaseModel):
    """Template com seus itens."""
    model_config = ConfigDict(from_attributes=True)

    template: ChecklistTemplateRead
    itens: List[ChecklistItemRead]


class ChecklistPreenchidoCompleto(BaseModel):
    """Checklist preenchido com template, itens e respostas."""
    model_config = ConfigDict(from_attributes=True)

    preenchimento: ChecklistPreenchidoRead
    template: ChecklistTemplateRead
    itens: List[ChecklistItemRead]
    respostas: List[ChecklistRespostaRead]


class ValidacaoResult(BaseModel):
    """Resultado de validacao de resposta."""
    valido: bool
    mensagem: Optional[str] = None
    alerta: Optional[dict] = None


class TemplatePaginatedResponse(BaseModel):
    """Response paginado de templates."""
    items: List[ChecklistTemplateListItem]
    total: int
    page: int
    page_size: int
    pages: int


# =============================================================================
# FILTER SCHEMAS
# =============================================================================

class TemplateFiltro(BaseModel):
    """Schema para filtros de templates."""
    tipo_servico: Optional[TipoServico] = None
    categoria_equipamento: Optional[str] = None
    is_obrigatorio: Optional[bool] = None
    is_ativo: Optional[bool] = True
    busca: Optional[str] = None
