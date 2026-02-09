"""
Schemas de Proposta - Licitacoes
================================
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProposalItemBase(BaseModel):
    """Schema base para item da proposta."""

    numero_item: int = Field(..., ge=1)
    codigo: str | None = Field(None, max_length=50)
    descricao: str = Field(..., min_length=1)
    unidade: str = Field(..., max_length=20)
    quantidade: Decimal = Field(..., gt=0)
    valor_unitario: Decimal = Field(..., ge=0)


class ProposalItemCreate(ProposalItemBase):
    """Schema para criacao de item da proposta."""

    custo_direto: Decimal | None = None
    custo_indireto: Decimal | None = None
    margem: Decimal | None = None
    composicao: dict = Field(default_factory=dict)

    @field_validator("valor_unitario")
    @classmethod
    def valor_unitario_positivo(cls, v):
        if v < 0:
            raise ValueError("Valor unitario deve ser positivo")
        return v


class ProposalItemResponse(ProposalItemBase):
    """Schema de resposta para item da proposta."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    proposal_id: UUID
    valor_total: Decimal
    custo_direto: Decimal | None = None
    custo_indireto: Decimal | None = None
    margem: Decimal | None = None
    composicao: dict = {}
    created_at: datetime


class ProposalBase(BaseModel):
    """Schema base para proposta."""

    tender_id: UUID
    numero: str = Field(..., min_length=1, max_length=50)


class ProposalCreate(ProposalBase):
    """Schema para criacao de proposta."""

    valor_total: Decimal = Field(..., gt=0)
    valor_unitario: Decimal | None = None
    desconto_percentual: Decimal | None = Field(None, ge=0, le=100)

    # BDI
    bdi_percentual: Decimal | None = Field(None, ge=0, le=100)
    bdi_detalhamento: dict = Field(default_factory=dict)

    # Encargos
    encargos_sociais: Decimal | None = Field(None, ge=0, le=200)
    encargos_detalhamento: dict = Field(default_factory=dict)

    # Itens
    itens: list[ProposalItemCreate] = Field(default_factory=list)

    # Outros
    justificativa_preco: str | None = None
    observacoes: str | None = None


class ProposalUpdate(BaseModel):
    """Schema para atualizacao de proposta."""

    numero: str | None = None
    valor_total: Decimal | None = None
    valor_unitario: Decimal | None = None
    desconto_percentual: Decimal | None = None

    # BDI
    bdi_percentual: Decimal | None = None
    bdi_detalhamento: dict | None = None

    # Encargos
    encargos_sociais: Decimal | None = None
    encargos_detalhamento: dict | None = None

    # Status
    status: str | None = None

    # Itens (substituicao completa)
    itens: list[ProposalItemCreate] | None = None

    # Outros
    justificativa_preco: str | None = None
    observacoes: str | None = None


class ProposalResponse(ProposalBase):
    """Schema de resposta para proposta."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    versao: int
    status: str
    ativo: bool

    # Valores
    valor_total: Decimal
    valor_unitario: Decimal | None = None
    desconto_percentual: Decimal | None = None

    # BDI
    bdi_percentual: Decimal | None = None
    bdi_detalhamento: dict = {}

    # Encargos
    encargos_sociais: Decimal | None = None
    encargos_detalhamento: dict = {}

    # Itens (como JSONB)
    itens: list[dict] = []

    # Classificacao
    posicao_classificacao: int | None = None
    valor_lance_final: Decimal | None = None
    historico_lances: list[dict] = []

    # Arquivos
    arquivo_pdf_url: str | None = None
    arquivo_planilha_url: str | None = None

    # Datas
    data_envio: datetime | None = None
    data_resultado: datetime | None = None

    # Propriedade calculada
    valor_com_bdi: Decimal | None = None

    # Outros
    justificativa_preco: str | None = None
    observacoes: str | None = None

    # Auditoria
    created_at: datetime
    updated_at: datetime | None = None


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
    data: datetime | None = None


class ProposalListResponse(BaseModel):
    """Schema de lista de propostas com paginacao."""

    items: list[ProposalResponse]
    total: int
    page: int
    size: int
