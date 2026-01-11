"""
Schemas de Proposta - Licitacoes
================================
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator

from modules.bidding.models.proposal import ProposalStatus


class ProposalItemBase(BaseModel):
    """Schema base para item da proposta."""
    numero_item: int = Field(..., ge=1)
    codigo: Optional[str] = Field(None, max_length=50)
    descricao: str = Field(..., min_length=1)
    unidade: str = Field(..., max_length=20)
    quantidade: Decimal = Field(..., gt=0)
    valor_unitario: Decimal = Field(..., ge=0)


class ProposalItemCreate(ProposalItemBase):
    """Schema para criacao de item da proposta."""
    custo_direto: Optional[Decimal] = None
    custo_indireto: Optional[Decimal] = None
    margem: Optional[Decimal] = None
    composicao: dict = Field(default_factory=dict)

    @field_validator('valor_unitario')
    @classmethod
    def valor_unitario_positivo(cls, v):
        if v < 0:
            raise ValueError('Valor unitario deve ser positivo')
        return v


class ProposalItemResponse(ProposalItemBase):
    """Schema de resposta para item da proposta."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    proposal_id: UUID
    valor_total: Decimal
    custo_direto: Optional[Decimal] = None
    custo_indireto: Optional[Decimal] = None
    margem: Optional[Decimal] = None
    composicao: dict = {}
    created_at: datetime


class ProposalBase(BaseModel):
    """Schema base para proposta."""
    tender_id: UUID
    numero: str = Field(..., min_length=1, max_length=50)


class ProposalCreate(ProposalBase):
    """Schema para criacao de proposta."""
    valor_total: Decimal = Field(..., gt=0)
    valor_unitario: Optional[Decimal] = None
    desconto_percentual: Optional[Decimal] = Field(None, ge=0, le=100)

    # BDI
    bdi_percentual: Optional[Decimal] = Field(None, ge=0, le=100)
    bdi_detalhamento: dict = Field(default_factory=dict)

    # Encargos
    encargos_sociais: Optional[Decimal] = Field(None, ge=0, le=200)
    encargos_detalhamento: dict = Field(default_factory=dict)

    # Itens
    itens: List[ProposalItemCreate] = Field(default_factory=list)

    # Outros
    justificativa_preco: Optional[str] = None
    observacoes: Optional[str] = None


class ProposalUpdate(BaseModel):
    """Schema para atualizacao de proposta."""
    numero: Optional[str] = None
    valor_total: Optional[Decimal] = None
    valor_unitario: Optional[Decimal] = None
    desconto_percentual: Optional[Decimal] = None

    # BDI
    bdi_percentual: Optional[Decimal] = None
    bdi_detalhamento: Optional[dict] = None

    # Encargos
    encargos_sociais: Optional[Decimal] = None
    encargos_detalhamento: Optional[dict] = None

    # Status
    status: Optional[str] = None

    # Itens (substituicao completa)
    itens: Optional[List[ProposalItemCreate]] = None

    # Outros
    justificativa_preco: Optional[str] = None
    observacoes: Optional[str] = None


class ProposalResponse(ProposalBase):
    """Schema de resposta para proposta."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    versao: int
    status: str
    ativo: bool

    # Valores
    valor_total: Decimal
    valor_unitario: Optional[Decimal] = None
    desconto_percentual: Optional[Decimal] = None

    # BDI
    bdi_percentual: Optional[Decimal] = None
    bdi_detalhamento: dict = {}

    # Encargos
    encargos_sociais: Optional[Decimal] = None
    encargos_detalhamento: dict = {}

    # Itens (como JSONB)
    itens: List[dict] = []

    # Classificacao
    posicao_classificacao: Optional[int] = None
    valor_lance_final: Optional[Decimal] = None
    historico_lances: List[dict] = []

    # Arquivos
    arquivo_pdf_url: Optional[str] = None
    arquivo_planilha_url: Optional[str] = None

    # Datas
    data_envio: Optional[datetime] = None
    data_resultado: Optional[datetime] = None

    # Propriedade calculada
    valor_com_bdi: Optional[Decimal] = None

    # Outros
    justificativa_preco: Optional[str] = None
    observacoes: Optional[str] = None

    # Auditoria
    created_at: datetime
    updated_at: Optional[datetime] = None


class ProposalCalculateBDI(BaseModel):
    """Schema para calculo de BDI."""
    valor_base: Decimal = Field(..., gt=0)

    # Componentes do BDI (percentuais)
    administracao_central: Decimal = Field(default=Decimal("4.0"), ge=0, le=20)
    seguro: Decimal = Field(default=Decimal("0.8"), ge=0, le=5)
    garantia: Decimal = Field(default=Decimal("0.5"), ge=0, le=5)
    risco: Decimal = Field(default=Decimal("1.0"), ge=0, le=10)
    despesas_financeiras: Decimal = Field(default=Decimal("1.0"), ge=0, le=10)
    lucro: Decimal = Field(default=Decimal("7.0"), ge=0, le=15)

    # Tributos
    pis: Decimal = Field(default=Decimal("0.65"), ge=0, le=5)
    cofins: Decimal = Field(default=Decimal("3.0"), ge=0, le=10)
    iss: Decimal = Field(default=Decimal("5.0"), ge=0, le=5)


class ProposalBDIResponse(BaseModel):
    """Resposta do calculo de BDI."""
    valor_base: Decimal
    bdi_percentual: Decimal
    valor_bdi: Decimal
    valor_total: Decimal
    detalhamento: dict


class ProposalLanceCreate(BaseModel):
    """Schema para registro de lance em pregao."""
    valor: Decimal = Field(..., gt=0)
    data: Optional[datetime] = None


class ProposalListResponse(BaseModel):
    """Schema de lista de propostas com paginacao."""
    items: List[ProposalResponse]
    total: int
    page: int
    size: int
