"""
Schemas EPI (NR-6) - Equipamentos de Protecao Individual
=========================================================

Schemas Pydantic para endpoints EPI.
"""

from datetime import datetime, date
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator

from modules.health_occupational.models.epi import EPICategory, EPIStatus, DeliveryReason


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
    descricao: Optional[str] = Field(None, max_length=500)
    codigo_interno: Optional[str] = Field(None, max_length=30)
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
    ca_validade: Optional[date] = Field(None, description="Validade do CA")
    fabricante: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Fabricante",
    )
    modelo: Optional[str] = Field(None, max_length=100)
    validade_dias: int = Field(
        default=365,
        ge=30,
        le=1825,
        description="Validade em dias apos entrega",
    )
    especificacoes: Optional[dict] = Field(default_factory=dict)
    riscos_protegidos: List[str] = Field(default_factory=list)
    instrucoes_uso: Optional[str] = None
    instrucoes_higienizacao: Optional[str] = None
    instrucoes_armazenamento: Optional[str] = None
    imagem_url: Optional[str] = None


class EPIUpdateRequest(BaseModel):
    """Request para atualizacao de EPI."""

    nome: Optional[str] = Field(None, min_length=3, max_length=100)
    descricao: Optional[str] = None
    ca_validade: Optional[date] = None
    validade_dias: Optional[int] = Field(None, ge=30, le=1825)
    especificacoes: Optional[dict] = None
    riscos_protegidos: Optional[List[str]] = None
    instrucoes_uso: Optional[str] = None
    instrucoes_higienizacao: Optional[str] = None
    instrucoes_armazenamento: Optional[str] = None
    imagem_url: Optional[str] = None
    ativo: Optional[bool] = None


class EPIResponse(BaseModel):
    """Response de EPI."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nome: str
    descricao: Optional[str] = None
    codigo_interno: Optional[str] = None
    categoria: str
    ca_number: str
    ca_validade: Optional[date] = None
    fabricante: str
    modelo: Optional[str] = None
    validade_dias: int
    especificacoes: dict
    riscos_protegidos: List[str]
    instrucoes_uso: Optional[str] = None
    instrucoes_higienizacao: Optional[str] = None
    instrucoes_armazenamento: Optional[str] = None
    imagem_url: Optional[str] = None
    ativo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Campos calculados
    ca_esta_valido: Optional[bool] = None


class EPIListResponse(BaseModel):
    """Response de lista de EPIs."""
    items: List[EPIResponse]
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
    observacoes: Optional[str] = Field(None, max_length=500)
    treinamento_realizado: bool = Field(default=False)


class EPIDeliveryUpdateRequest(BaseModel):
    """Request para atualizacao de entrega."""

    devolvido: Optional[bool] = None
    data_devolucao: Optional[datetime] = None
    motivo_devolucao: Optional[str] = None
    condicao_devolucao: Optional[str] = None
    assinatura_funcionario: Optional[bool] = None
    observacoes: Optional[str] = None


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
    data_validade: Optional[date] = None
    devolvido: bool
    data_devolucao: Optional[datetime] = None
    motivo_devolucao: Optional[str] = None
    condicao_devolucao: Optional[str] = None
    assinatura_funcionario: bool
    data_assinatura: Optional[datetime] = None
    entregue_por: Optional[UUID] = None
    observacoes: Optional[str] = None
    treinamento_realizado: bool
    data_treinamento: Optional[datetime] = None
    created_at: datetime

    # Campos calculados
    esta_vencido: Optional[bool] = None
    dias_para_vencer: Optional[int] = None

    # EPI relacionado (opcional, para detalhes)
    epi: Optional[EPISummary] = None


class EPIDeliveryListResponse(BaseModel):
    """Response de lista de entregas."""
    items: List[EPIDeliveryResponse]
    total: int
    page: int = 1
    size: int = 20


class EPIRecordResponse(BaseModel):
    """Ficha de EPI do funcionario."""
    funcionario_id: UUID
    entregas: List[EPIDeliveryResponse]
    total_entregas: int
    epis_ativos: List[EPIDeliveryResponse]
    epis_vencidos: List[EPIDeliveryResponse]
    epis_devolvidos: List[EPIDeliveryResponse]


# ==============================================================================
# EPI Inventory Schemas
# ==============================================================================

class EPIInventoryUpdateRequest(BaseModel):
    """Request para atualizacao de estoque."""

    quantidade_atual: Optional[int] = Field(None, ge=0)
    quantidade_minima: Optional[int] = Field(None, ge=0)
    quantidade_maxima: Optional[int] = Field(None, ge=0)
    local_armazenamento: Optional[str] = None
    lote_atual: Optional[str] = None
    data_validade_lote: Optional[date] = None
    custo_unitario: Optional[float] = Field(None, ge=0)
    fornecedor: Optional[str] = None


class EPIInventoryResponse(BaseModel):
    """Response de estoque de EPI."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    epi_id: UUID
    quantidade_atual: int
    quantidade_minima: int
    quantidade_maxima: Optional[int] = None
    local_armazenamento: Optional[str] = None
    lote_atual: Optional[str] = None
    data_validade_lote: Optional[date] = None
    custo_unitario: Optional[float] = None
    fornecedor: Optional[str] = None
    ultima_entrada: Optional[datetime] = None
    ultima_saida: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Campos calculados
    estoque_baixo: Optional[bool] = None
    percentual_estoque: Optional[float] = None

    # EPI relacionado
    epi: Optional[EPISummary] = None


class EPIInventoryListResponse(BaseModel):
    """Response de lista de estoque."""
    items: List[EPIInventoryResponse]
    total: int
    itens_baixo_estoque: int = 0


# ==============================================================================
# EPI Category Info
# ==============================================================================

class EPICategoryInfo(BaseModel):
    """Informacoes de categoria de EPI."""
    id: str
    nome: str
    exemplos: List[str]


class EPICategoriesResponse(BaseModel):
    """Response com categorias de EPI."""
    categorias: List[EPICategoryInfo]
