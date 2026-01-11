"""
Schemas de Edital (Tender) - Licitacoes
=======================================
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from modules.bidding.models.tender import TenderStatus, BiddingModality, BiddingCriteria


class TenderDocumentBase(BaseModel):
    """Schema base para documento do edital."""
    nome: str = Field(..., min_length=1, max_length=255)
    descricao: Optional[str] = None
    tipo: str = Field(..., max_length=50)
    ordem: int = Field(default=0)
    obrigatorio: bool = Field(default=False)


class TenderDocumentCreate(TenderDocumentBase):
    """Schema para criacao de documento do edital."""
    arquivo_url: Optional[str] = None
    arquivo_nome: Optional[str] = None
    arquivo_tamanho: Optional[int] = None


class TenderDocumentResponse(TenderDocumentBase):
    """Schema de resposta para documento do edital."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tender_id: UUID
    arquivo_url: Optional[str] = None
    arquivo_nome: Optional[str] = None
    arquivo_tamanho: Optional[int] = None
    arquivo_hash: Optional[str] = None
    created_at: datetime


class TenderBase(BaseModel):
    """Schema base para edital."""
    numero: str = Field(..., min_length=1, max_length=50)
    numero_processo: Optional[str] = Field(None, max_length=50)
    ano: int = Field(..., ge=2000, le=2100)

    # Orgao
    orgao_cnpj: str = Field(..., min_length=14, max_length=18)
    orgao_nome: str = Field(..., min_length=1, max_length=255)
    orgao_uf: str = Field(default="AM", min_length=2, max_length=2)
    orgao_municipio: Optional[str] = Field(None, max_length=100)
    unidade_gestora: Optional[str] = Field(None, max_length=100)

    # Modalidade e Tipo
    modalidade: str = Field(..., max_length=50)
    criterio_julgamento: str = Field(default=BiddingCriteria.MENOR_PRECO.value)
    tipo_contratacao: Optional[str] = None
    regime_execucao: Optional[str] = None

    # Objeto
    objeto: str = Field(..., min_length=10)
    objeto_resumido: Optional[str] = Field(None, max_length=500)

    # Valores
    valor_estimado: Optional[Decimal] = Field(None, ge=0)


class TenderCreate(TenderBase):
    """Schema para criacao de edital."""
    # Datas
    data_publicacao: Optional[datetime] = None
    data_abertura: Optional[datetime] = None
    data_encerramento_propostas: Optional[datetime] = None
    data_impugnacao_limite: Optional[datetime] = None
    data_esclarecimentos_limite: Optional[datetime] = None

    # Participacao
    participando: bool = Field(default=False)
    interesse: bool = Field(default=False)

    # Segmentacao
    segmento: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    # Requisitos
    requisitos: List[dict] = Field(default_factory=list)
    documentos_exigidos: List[dict] = Field(default_factory=list)

    # Anexos
    anexos: List[dict] = Field(default_factory=list)

    # PNCP
    pncp_id: Optional[str] = None
    pncp_link: Optional[str] = None

    # Outros
    observacoes: Optional[str] = None
    fonte: str = Field(default="manual")


class TenderUpdate(BaseModel):
    """Schema para atualizacao de edital."""
    numero: Optional[str] = Field(None, min_length=1, max_length=50)
    numero_processo: Optional[str] = None
    orgao_nome: Optional[str] = None
    objeto: Optional[str] = None
    objeto_resumido: Optional[str] = None
    valor_estimado: Optional[Decimal] = None
    valor_homologado: Optional[Decimal] = None

    # Datas
    data_publicacao: Optional[datetime] = None
    data_abertura: Optional[datetime] = None
    data_encerramento_propostas: Optional[datetime] = None
    data_impugnacao_limite: Optional[datetime] = None
    data_esclarecimentos_limite: Optional[datetime] = None
    data_resultado: Optional[datetime] = None
    data_homologacao: Optional[datetime] = None

    # Status
    status: Optional[str] = None

    # Participacao
    participando: Optional[bool] = None
    interesse: Optional[bool] = None
    motivo_nao_participacao: Optional[str] = None

    # Segmentacao
    segmento: Optional[str] = None
    tags: Optional[List[str]] = None

    # Requisitos
    requisitos: Optional[List[dict]] = None
    documentos_exigidos: Optional[List[dict]] = None
    anexos: Optional[List[dict]] = None

    # Outros
    observacoes: Optional[str] = None


class TenderResponse(TenderBase):
    """Schema de resposta para edital."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    ativo: bool

    # Datas
    data_publicacao: Optional[datetime] = None
    data_abertura: Optional[datetime] = None
    data_encerramento_propostas: Optional[datetime] = None
    data_impugnacao_limite: Optional[datetime] = None
    data_esclarecimentos_limite: Optional[datetime] = None
    data_resultado: Optional[datetime] = None
    data_homologacao: Optional[datetime] = None

    # Valores
    valor_homologado: Optional[Decimal] = None

    # PNCP
    pncp_id: Optional[str] = None
    pncp_link: Optional[str] = None
    pncp_ultima_sync: Optional[datetime] = None

    # Participacao
    participando: bool
    interesse: bool
    motivo_nao_participacao: Optional[str] = None

    # Segmentacao
    segmento: Optional[str] = None
    tags: List[str] = []

    # Requisitos
    requisitos: List[dict] = []
    documentos_exigidos: List[dict] = []
    anexos: List[dict] = []

    # Propriedades calculadas
    esta_aberto: Optional[bool] = None
    prazo_impugnacao_valido: Optional[bool] = None
    dias_para_abertura: Optional[int] = None

    # Outros
    observacoes: Optional[str] = None
    fonte: str

    # Auditoria
    created_at: datetime
    updated_at: Optional[datetime] = None


class TenderListResponse(BaseModel):
    """Schema de lista de editais com paginacao."""
    items: List[TenderResponse]
    total: int
    page: int
    size: int
    pages: int


class TenderSearchParams(BaseModel):
    """Parametros de busca de editais."""
    uf: Optional[str] = Field(default="AM", max_length=2)
    municipio: Optional[str] = None
    modalidade: Optional[str] = None
    segmento: Optional[str] = None
    status: Optional[str] = None
    participando: Optional[bool] = None
    interesse: Optional[bool] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    valor_min: Optional[Decimal] = None
    valor_max: Optional[Decimal] = None
    termo_busca: Optional[str] = None
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
