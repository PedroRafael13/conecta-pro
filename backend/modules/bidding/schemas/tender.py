"""
Schemas de Edital (Tender) - Licitacoes
=======================================
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.bidding.models.tender import BiddingCriteria


class TenderDocumentBase(BaseModel):
    """Schema base para documento do edital."""

    nome: str = Field(..., min_length=1, max_length=255)
    descricao: str | None = None
    tipo: str = Field(..., max_length=50)
    ordem: int = Field(default=0)
    obrigatorio: bool = Field(default=False)


class TenderDocumentCreate(TenderDocumentBase):
    """Schema para criacao de documento do edital."""

    arquivo_url: str | None = None
    arquivo_nome: str | None = None
    arquivo_tamanho: int | None = None


class TenderDocumentResponse(TenderDocumentBase):
    """Schema de resposta para documento do edital."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tender_id: UUID
    arquivo_url: str | None = None
    arquivo_nome: str | None = None
    arquivo_tamanho: int | None = None
    arquivo_hash: str | None = None
    created_at: datetime


class TenderBase(BaseModel):
    """Schema base para edital."""

    numero: str = Field(..., min_length=1, max_length=50)
    numero_processo: str | None = Field(None, max_length=50)
    ano: int = Field(..., ge=2000, le=2100)

    # Orgao
    orgao_cnpj: str = Field(..., min_length=14, max_length=18)
    orgao_nome: str = Field(..., min_length=1, max_length=255)
    orgao_uf: str = Field(default="AM", min_length=2, max_length=2)
    orgao_municipio: str | None = Field(None, max_length=100)
    unidade_gestora: str | None = Field(None, max_length=100)

    # Modalidade e Tipo
    modalidade: str = Field(..., max_length=50)
    criterio_julgamento: str = Field(default=BiddingCriteria.MENOR_PRECO.value)
    tipo_contratacao: str | None = None
    regime_execucao: str | None = None

    # Objeto
    objeto: str = Field(..., min_length=10)
    objeto_resumido: str | None = Field(None, max_length=500)

    # Valores
    valor_estimado: Decimal | None = Field(None, ge=0)


class TenderCreate(TenderBase):
    """Schema para criacao de edital."""

    # Datas
    data_publicacao: datetime | None = None
    data_abertura: datetime | None = None
    data_encerramento_propostas: datetime | None = None
    data_impugnacao_limite: datetime | None = None
    data_esclarecimentos_limite: datetime | None = None

    # Participacao
    participando: bool = Field(default=False)
    interesse: bool = Field(default=False)

    # Segmentacao
    segmento: str | None = None
    tags: list[str] = Field(default_factory=list)

    # Requisitos
    requisitos: list[dict] = Field(default_factory=list)
    documentos_exigidos: list[dict] = Field(default_factory=list)

    # Anexos
    anexos: list[dict] = Field(default_factory=list)

    # PNCP
    pncp_id: str | None = None
    pncp_link: str | None = None

    # Outros
    observacoes: str | None = None
    fonte: str = Field(default="manual")


class TenderUpdate(BaseModel):
    """Schema para atualizacao de edital."""

    numero: str | None = Field(None, min_length=1, max_length=50)
    numero_processo: str | None = None
    orgao_nome: str | None = None
    objeto: str | None = None
    objeto_resumido: str | None = None
    valor_estimado: Decimal | None = None
    valor_homologado: Decimal | None = None

    # Datas
    data_publicacao: datetime | None = None
    data_abertura: datetime | None = None
    data_encerramento_propostas: datetime | None = None
    data_impugnacao_limite: datetime | None = None
    data_esclarecimentos_limite: datetime | None = None
    data_resultado: datetime | None = None
    data_homologacao: datetime | None = None

    # Status
    status: str | None = None

    # Participacao
    participando: bool | None = None
    interesse: bool | None = None
    motivo_nao_participacao: str | None = None

    # Segmentacao
    segmento: str | None = None
    tags: list[str] | None = None

    # Requisitos
    requisitos: list[dict] | None = None
    documentos_exigidos: list[dict] | None = None
    anexos: list[dict] | None = None

    # Outros
    observacoes: str | None = None


class TenderResponse(TenderBase):
    """Schema de resposta para edital."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    ativo: bool

    # Datas
    data_publicacao: datetime | None = None
    data_abertura: datetime | None = None
    data_encerramento_propostas: datetime | None = None
    data_impugnacao_limite: datetime | None = None
    data_esclarecimentos_limite: datetime | None = None
    data_resultado: datetime | None = None
    data_homologacao: datetime | None = None

    # Valores
    valor_homologado: Decimal | None = None

    # PNCP
    pncp_id: str | None = None
    pncp_link: str | None = None
    pncp_ultima_sync: datetime | None = None

    # Participacao
    participando: bool
    interesse: bool
    motivo_nao_participacao: str | None = None

    # Segmentacao
    segmento: str | None = None
    tags: list[str] = []

    # Requisitos
    requisitos: list[dict] = []
    documentos_exigidos: list[dict] = []
    anexos: list[dict] = []

    # Propriedades calculadas
    esta_aberto: bool | None = None
    prazo_impugnacao_valido: bool | None = None
    dias_para_abertura: int | None = None

    # Outros
    observacoes: str | None = None
    fonte: str

    # Auditoria
    created_at: datetime
    updated_at: datetime | None = None


class TenderListResponse(BaseModel):
    """Schema de lista de editais com paginacao."""

    items: list[TenderResponse]
    total: int
    page: int
    size: int
    pages: int


class TenderSearchParams(BaseModel):
    """Parametros de busca de editais."""

    uf: str | None = Field(default="AM", max_length=2)
    municipio: str | None = None
    modalidade: str | None = None
    segmento: str | None = None
    status: str | None = None
    participando: bool | None = None
    interesse: bool | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    valor_min: Decimal | None = None
    valor_max: Decimal | None = None
    termo_busca: str | None = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
