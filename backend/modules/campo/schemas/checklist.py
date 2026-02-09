"""
Schemas de Checklist - Modulo Campo
===================================

Pydantic schemas para validacao e serializacao de Checklists.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# =============================================================================
# ENUMS (importados do model)
# =============================================================================
from modules.campo.models.checklist import (
    CategoriaItem,
    TipoResposta,
    TipoServico,
)

# =============================================================================
# SCHEMAS AUXILIARES
# =============================================================================


class OpcaoItem(BaseModel):
    """Schema para opcao de multipla escolha."""

    valor: str
    label: str
    descricao: str | None = None


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
    descricao: str | None = None
    tipo_servico: TipoServico = TipoServico.GERAL
    categoria_equipamento: str | None = Field(None, max_length=100)

    is_obrigatorio: bool = False
    permite_itens_adicionais: bool = False
    tempo_estimado_minutos: int = 15
    pontuacao_maxima: int | None = None

    visivel_cliente: bool = False

    tags: list[str] | None = None


class ChecklistTemplateUpdate(BaseModel):
    """Schema para atualizacao de template."""

    model_config = ConfigDict(from_attributes=True)

    nome: str | None = Field(None, min_length=3, max_length=200)
    descricao: str | None = None
    tipo_servico: TipoServico | None = None
    categoria_equipamento: str | None = Field(None, max_length=100)

    is_obrigatorio: bool | None = None
    permite_itens_adicionais: bool | None = None
    tempo_estimado_minutos: int | None = None
    pontuacao_maxima: int | None = None

    visivel_cliente: bool | None = None
    is_ativo: bool | None = None

    tags: list[str] | None = None


class ChecklistTemplateRead(BaseModel):
    """Schema de leitura de template."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    codigo: str
    nome: str
    descricao: str | None = None
    tipo_servico: TipoServico
    categoria_equipamento: str | None = None
    versao: str

    is_obrigatorio: bool
    permite_itens_adicionais: bool
    tempo_estimado_minutos: int
    pontuacao_maxima: int | None = None

    is_ativo: bool
    visivel_cliente: bool

    total_itens: int = 0
    itens_obrigatorios: int = 0

    tags: list[str] | None = None
    created_at: datetime
    updated_at: datetime


class ChecklistTemplateListItem(BaseModel):
    """Schema resumido para listagem de templates."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    codigo: str
    nome: str
    tipo_servico: TipoServico
    categoria_equipamento: str | None = None

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

    ordem: int | None = None
    secao: str | None = Field(None, max_length=100)
    secao_ordem: int = 1

    pergunta: str = Field(..., min_length=3, max_length=500)
    descricao: str | None = None
    categoria: CategoriaItem = CategoriaItem.VERIFICACAO

    tipo_resposta: TipoResposta = TipoResposta.SIM_NAO
    opcoes: list[OpcaoItem] | None = None

    valor_minimo: Decimal | None = None
    valor_maximo: Decimal | None = None
    unidade_medida: str | None = Field(None, max_length=20)
    valor_padrao: str | None = Field(None, max_length=500)

    obrigatorio: bool = True

    condicional_item_id: UUID | None = None
    condicional_valor: str | None = Field(None, max_length=100)

    pontos: int = 0
    peso: Decimal = Decimal("1.0")

    gera_alerta: bool = False
    alerta_condicao: str | None = Field(None, max_length=100)
    alerta_mensagem: str | None = Field(None, max_length=300)
    alerta_severidade: str = "warning"


class ChecklistItemUpdate(BaseModel):
    """Schema para atualizacao de item."""

    model_config = ConfigDict(from_attributes=True)

    ordem: int | None = None
    secao: str | None = Field(None, max_length=100)
    secao_ordem: int | None = None

    pergunta: str | None = Field(None, min_length=3, max_length=500)
    descricao: str | None = None
    categoria: CategoriaItem | None = None

    tipo_resposta: TipoResposta | None = None
    opcoes: list[OpcaoItem] | None = None

    valor_minimo: Decimal | None = None
    valor_maximo: Decimal | None = None
    unidade_medida: str | None = Field(None, max_length=20)
    valor_padrao: str | None = Field(None, max_length=500)

    obrigatorio: bool | None = None

    condicional_item_id: UUID | None = None
    condicional_valor: str | None = Field(None, max_length=100)

    pontos: int | None = None
    peso: Decimal | None = None

    gera_alerta: bool | None = None
    alerta_condicao: str | None = Field(None, max_length=100)
    alerta_mensagem: str | None = Field(None, max_length=300)
    alerta_severidade: str | None = None

    is_active: bool | None = None


class ChecklistItemRead(BaseModel):
    """Schema de leitura de item."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    template_id: UUID

    ordem: int
    secao: str | None = None
    secao_ordem: int

    pergunta: str
    descricao: str | None = None
    categoria: CategoriaItem

    tipo_resposta: TipoResposta
    opcoes: list[Any] | None = None

    valor_minimo: Decimal | None = None
    valor_maximo: Decimal | None = None
    unidade_medida: str | None = None
    valor_padrao: str | None = None

    obrigatorio: bool

    condicional_item_id: UUID | None = None
    condicional_valor: str | None = None

    pontos: int
    peso: Decimal

    gera_alerta: bool
    alerta_condicao: str | None = None
    alerta_mensagem: str | None = None
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
    valor: str | int | float | bool | list | dict | None = None

    # URLs de arquivos
    foto_url: str | None = None
    fotos_urls: list[str] | None = None
    assinatura_url: str | None = None
    arquivo_url: str | None = None

    # Geolocalizacao
    latitude: Decimal | None = None
    longitude: Decimal | None = None

    observacao: str | None = None


class ChecklistRespostaUpdate(BaseModel):
    """Schema para atualizacao de resposta."""

    model_config = ConfigDict(from_attributes=True)

    valor: str | int | float | bool | list | dict | None = None

    foto_url: str | None = None
    fotos_urls: list[str] | None = None
    assinatura_url: str | None = None

    observacao: str | None = None


class ChecklistRespostaRead(BaseModel):
    """Schema de leitura de resposta."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ordem_servico_id: UUID
    template_id: UUID
    item_id: UUID

    # Valores
    resposta_texto: str | None = None
    resposta_numero: Decimal | None = None
    resposta_boolean: bool | None = None
    resposta_data: datetime | None = None
    resposta_json: Any | None = None

    # Arquivos
    resposta_foto_url: str | None = None
    resposta_fotos_urls: list[str] | None = None
    resposta_assinatura_url: str | None = None
    resposta_arquivo_url: str | None = None

    # Validacao
    is_valida: bool
    mensagem_validacao: str | None = None

    # Alerta
    gerou_alerta: bool
    alerta_data: dict | None = None

    # Metadata
    respondido_por: UUID | None = None
    respondido_at: datetime
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    observacao: str | None = None


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
    iniciado_at: datetime | None = None
    concluido: bool
    concluido_at: datetime | None = None

    total_itens: int
    itens_respondidos: int
    itens_obrigatorios: int
    itens_obrigatorios_respondidos: int
    percentual_conclusao: Decimal

    pontuacao_obtida: int
    pontuacao_maxima: int
    percentual_conformidade: Decimal | None = None

    total_alertas: int
    alertas: list[Any] | None = None

    preenchido_por: UUID | None = None
    preenchido_offline: bool
    observacoes_finais: str | None = None

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
    valor: str | int | float | bool | list | dict | None = None
    foto_url: str | None = None
    fotos_urls: list[str] | None = None
    assinatura_url: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    observacao: str | None = None


class ChecklistConcluirRequest(BaseModel):
    """Schema para concluir checklist."""

    observacoes_finais: str | None = None


class ReordenarItensRequest(BaseModel):
    """Schema para reordenar itens."""

    nova_ordem: list[UUID]


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================


class ChecklistComItens(BaseModel):
    """Template com seus itens."""

    model_config = ConfigDict(from_attributes=True)

    template: ChecklistTemplateRead
    itens: list[ChecklistItemRead]


class ChecklistPreenchidoCompleto(BaseModel):
    """Checklist preenchido com template, itens e respostas."""

    model_config = ConfigDict(from_attributes=True)

    preenchimento: ChecklistPreenchidoRead
    template: ChecklistTemplateRead
    itens: list[ChecklistItemRead]
    respostas: list[ChecklistRespostaRead]


class ValidacaoResult(BaseModel):
    """Resultado de validacao de resposta."""

    valido: bool
    mensagem: str | None = None
    alerta: dict | None = None


class TemplatePaginatedResponse(BaseModel):
    """Response paginado de templates."""

    items: list[ChecklistTemplateListItem]
    total: int
    page: int
    page_size: int
    pages: int


# =============================================================================
# FILTER SCHEMAS
# =============================================================================


class TemplateFiltro(BaseModel):
    """Schema para filtros de templates."""

    tipo_servico: TipoServico | None = None
    categoria_equipamento: str | None = None
    is_obrigatorio: bool | None = None
    is_ativo: bool | None = True
    busca: str | None = None
