"""
Schemas EPI (NR-6) - Equipamentos de Protecao Individual
=========================================================

Schemas Pydantic para endpoints EPI.
"""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ==============================================================================
# EPI Schemas
# ==============================================================================


class EPICreateRequest(BaseModel):
    """Request para cadastro de EPI."""

    nome: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Nome do EPI",
    )
    descricao: str | None = Field(None, max_length=500)
    codigo_interno: str | None = Field(None, max_length=30)
    categoria: str = Field(
        ...,
        description="Categoria do EPI",
        pattern=r"^(cabeca|olhos|face|auditivo|respiratorio|tronco|membros_superiores|membros_inferiores|corpo_inteiro|quedas)$",
    )
    ca_number: str = Field(
        ...,
        min_length=4,
        max_length=20,
        description="Numero do CA",
    )
    ca_validade: date | None = Field(None, description="Validade do CA")
    fabricante: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Fabricante",
    )
    modelo: str | None = Field(None, max_length=100)
    validade_dias: int = Field(
        default=365,
        ge=30,
        le=1825,
        description="Validade em dias apos entrega",
    )
    especificacoes: dict | None = Field(default_factory=dict)
    riscos_protegidos: list[str] = Field(default_factory=list)
    instrucoes_uso: str | None = None
    instrucoes_higienizacao: str | None = None
    instrucoes_armazenamento: str | None = None
    imagem_url: str | None = None


class EPIUpdateRequest(BaseModel):
    """Request para atualizacao de EPI."""

    nome: str | None = Field(None, min_length=3, max_length=100)
    descricao: str | None = None
    ca_validade: date | None = None
    validade_dias: int | None = Field(None, ge=30, le=1825)
    especificacoes: dict | None = None
    riscos_protegidos: list[str] | None = None
    instrucoes_uso: str | None = None
    instrucoes_higienizacao: str | None = None
    instrucoes_armazenamento: str | None = None
    imagem_url: str | None = None
    ativo: bool | None = None


class EPIResponse(BaseModel):
    """Response de EPI."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nome: str
    descricao: str | None = None
    codigo_interno: str | None = None
    categoria: str
    ca_number: str
    ca_validade: date | None = None
    fabricante: str
    modelo: str | None = None
    validade_dias: int
    especificacoes: dict
    riscos_protegidos: list[str]
    instrucoes_uso: str | None = None
    instrucoes_higienizacao: str | None = None
    instrucoes_armazenamento: str | None = None
    imagem_url: str | None = None
    ativo: bool
    created_at: datetime
    updated_at: datetime | None = None

    # Campos calculados
    ca_esta_valido: bool | None = None


class EPIListResponse(BaseModel):
    """Response de lista de EPIs."""

    items: list[EPIResponse]
    total: int
    page: int = 1
    size: int = 20


class EPISummary(BaseModel):
    """Resumo de EPI para listagens."""

    id: UUID
    nome: str
    categoria: str
    ca_number: str
    fabricante: str
    ativo: bool


# ==============================================================================
# EPI Delivery Schemas
# ==============================================================================


class EPIDeliveryRequest(BaseModel):
    """Request para entrega de EPI."""

    funcionario_id: UUID = Field(..., description="UUID do funcionario")
    epi_id: UUID = Field(..., description="ID do EPI")
    quantidade: int = Field(
        default=1,
        ge=1,
        le=100,
        description="Quantidade",
    )
    motivo: str = Field(
        ...,
        description="Motivo da entrega",
        pattern=r"^(admissao|substituicao|desgaste|perda|troca_funcao|vencimento)$",
    )
    ca_number: str = Field(
        ...,
        min_length=4,
        max_length=20,
        description="Numero do CA",
    )
    observacoes: str | None = Field(None, max_length=500)
    treinamento_realizado: bool = Field(default=False)


class EPIDeliveryUpdateRequest(BaseModel):
    """Request para atualizacao de entrega."""

    devolvido: bool | None = None
    data_devolucao: datetime | None = None
    motivo_devolucao: str | None = None
    condicao_devolucao: str | None = None
    assinatura_funcionario: bool | None = None
    observacoes: str | None = None


class EPIDeliveryResponse(BaseModel):
    """Response de entrega de EPI."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    epi_id: UUID
    funcionario_id: UUID
    quantidade: int
    motivo: str
    ca_number: str
    data_entrega: datetime
    data_validade: date | None = None
    devolvido: bool
    data_devolucao: datetime | None = None
    motivo_devolucao: str | None = None
    condicao_devolucao: str | None = None
    assinatura_funcionario: bool
    data_assinatura: datetime | None = None
    entregue_por: UUID | None = None
    observacoes: str | None = None
    treinamento_realizado: bool
    data_treinamento: datetime | None = None
    created_at: datetime

    # Campos calculados
    esta_vencido: bool | None = None
    dias_para_vencer: int | None = None

    # EPI relacionado (opcional, para detalhes)
    epi: EPISummary | None = None


class EPIDeliveryListResponse(BaseModel):
    """Response de lista de entregas."""

    items: list[EPIDeliveryResponse]
    total: int
    page: int = 1
    size: int = 20


class EPIRecordResponse(BaseModel):
    """Ficha de EPI do funcionario."""

    funcionario_id: UUID
    entregas: list[EPIDeliveryResponse]
    total_entregas: int
    epis_ativos: list[EPIDeliveryResponse]
    epis_vencidos: list[EPIDeliveryResponse]
    epis_devolvidos: list[EPIDeliveryResponse]


# ==============================================================================
# EPI Inventory Schemas
# ==============================================================================


class EPIInventoryUpdateRequest(BaseModel):
    """Request para atualizacao de estoque."""

    quantidade_atual: int | None = Field(None, ge=0)
    quantidade_minima: int | None = Field(None, ge=0)
    quantidade_maxima: int | None = Field(None, ge=0)
    local_armazenamento: str | None = None
    lote_atual: str | None = None
    data_validade_lote: date | None = None
    custo_unitario: float | None = Field(None, ge=0)
    fornecedor: str | None = None


class EPIInventoryResponse(BaseModel):
    """Response de estoque de EPI."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    epi_id: UUID
    quantidade_atual: int
    quantidade_minima: int
    quantidade_maxima: int | None = None
    local_armazenamento: str | None = None
    lote_atual: str | None = None
    data_validade_lote: date | None = None
    custo_unitario: float | None = None
    fornecedor: str | None = None
    ultima_entrada: datetime | None = None
    ultima_saida: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None

    # Campos calculados
    estoque_baixo: bool | None = None
    percentual_estoque: float | None = None

    # EPI relacionado
    epi: EPISummary | None = None


class EPIInventoryListResponse(BaseModel):
    """Response de lista de estoque."""

    items: list[EPIInventoryResponse]
    total: int
    itens_baixo_estoque: int = 0


# ==============================================================================
# EPI Category Info
# ==============================================================================


class EPICategoryInfo(BaseModel):
    """Informacoes de categoria de EPI."""

    id: str
    nome: str
    exemplos: list[str]


class EPICategoriesResponse(BaseModel):
    """Response com categorias de EPI."""

    categorias: list[EPICategoryInfo]
