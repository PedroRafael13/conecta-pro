"""
Schemas de Contrato Publico - Licitacoes
========================================
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from modules.bidding.models.public_contract import ContractStatus, AdjustmentIndex, GuaranteeType


class MeasurementSummary(BaseModel):
    """Resumo de medicao para resposta de contrato."""
    id: UUID
    numero_medicao: int
    competencia: str
    valor_bruto: Decimal
    valor_liquido: Decimal
    status: str
    data_aprovacao: Optional[date] = None


class PublicContractBase(BaseModel):
    """Schema base para contrato publico."""
    numero_contrato: str = Field(..., min_length=1, max_length=50)
    ano_contrato: int = Field(..., ge=2000, le=2100)
    objeto: str = Field(..., min_length=10)
    objeto_resumido: Optional[str] = Field(None, max_length=500)

    # Orgao
    orgao_cnpj: str = Field(..., min_length=14, max_length=18)
    orgao_nome: str = Field(..., min_length=1, max_length=255)
    orgao_uf: str = Field(default="AM", min_length=2, max_length=2)


class PublicContractCreate(PublicContractBase):
    """Schema para criacao de contrato publico."""
    tender_id: Optional[UUID] = None

    # Orgao
    unidade_gestora: Optional[str] = None
    gestor_contrato: Optional[str] = None
    fiscal_contrato: Optional[str] = None

    # Valores
    valor_contrato: Decimal = Field(..., gt=0)

    # Empenho
    numero_empenho: Optional[str] = None
    data_empenho: Optional[date] = None
    nota_empenho_url: Optional[str] = None

    # Vigencia
    data_assinatura: Optional[date] = None
    data_publicacao: Optional[date] = None
    data_vigencia_inicio: date
    data_vigencia_fim: date
    prazo_meses: Optional[int] = None

    # Reajuste
    indice_reajuste: str = Field(default=AdjustmentIndex.IGPM.value)
    data_base_reajuste: Optional[date] = None

    # Garantia
    garantia_tipo: Optional[str] = None
    garantia_valor: Optional[Decimal] = None
    garantia_percentual: Optional[Decimal] = Field(None, ge=0, le=10)
    garantia_vencimento: Optional[date] = None
    garantia_documento_url: Optional[str] = None

    # PNCP
    pncp_id: Optional[str] = None
    pncp_link: Optional[str] = None

    # Arquivos
    arquivo_contrato_url: Optional[str] = None
    arquivo_publicacao_url: Optional[str] = None

    # Outros
    observacoes: Optional[str] = None


class PublicContractUpdate(BaseModel):
    """Schema para atualizacao de contrato publico."""
    objeto: Optional[str] = None
    objeto_resumido: Optional[str] = None

    # Orgao
    gestor_contrato: Optional[str] = None
    fiscal_contrato: Optional[str] = None

    # Valores
    valor_empenhado: Optional[Decimal] = None
    valor_executado: Optional[Decimal] = None
    valor_pago: Optional[Decimal] = None

    # Empenho
    numero_empenho: Optional[str] = None
    data_empenho: Optional[date] = None
    nota_empenho_url: Optional[str] = None

    # Vigencia
    data_assinatura: Optional[date] = None
    data_publicacao: Optional[date] = None

    # Status
    status: Optional[str] = None

    # Garantia
    garantia_tipo: Optional[str] = None
    garantia_valor: Optional[Decimal] = None
    garantia_vencimento: Optional[date] = None
    garantia_documento_url: Optional[str] = None

    # Arquivos
    arquivo_contrato_url: Optional[str] = None
    arquivo_publicacao_url: Optional[str] = None

    # Outros
    observacoes: Optional[str] = None


class PublicContractResponse(PublicContractBase):
    """Schema de resposta para contrato publico."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tender_id: Optional[UUID] = None
    status: str
    ativo: bool

    # Orgao
    unidade_gestora: Optional[str] = None
    gestor_contrato: Optional[str] = None
    fiscal_contrato: Optional[str] = None

    # Valores
    valor_contrato: Decimal
    valor_empenhado: Optional[Decimal] = None
    valor_executado: Optional[Decimal] = None
    valor_pago: Optional[Decimal] = None
    saldo_contrato: Optional[Decimal] = None

    # Empenho
    numero_empenho: Optional[str] = None
    data_empenho: Optional[date] = None
    nota_empenho_url: Optional[str] = None

    # Vigencia
    data_assinatura: Optional[date] = None
    data_publicacao: Optional[date] = None
    data_vigencia_inicio: date
    data_vigencia_fim: date
    prazo_meses: Optional[int] = None

    # Reajuste
    indice_reajuste: Optional[str] = None
    data_base_reajuste: Optional[date] = None
    ultimo_reajuste: Optional[date] = None
    percentual_ultimo_reajuste: Optional[Decimal] = None

    # Garantia
    garantia_tipo: Optional[str] = None
    garantia_valor: Optional[Decimal] = None
    garantia_percentual: Optional[Decimal] = None
    garantia_vencimento: Optional[date] = None
    garantia_documento_url: Optional[str] = None

    # Aditivos
    aditivos: List[dict] = []
    quantidade_aditivos: int = 0

    # PNCP
    pncp_id: Optional[str] = None
    pncp_link: Optional[str] = None

    # Arquivos
    arquivo_contrato_url: Optional[str] = None
    arquivo_publicacao_url: Optional[str] = None

    # Propriedades calculadas
    esta_vigente: Optional[bool] = None
    dias_para_vencer: Optional[int] = None
    percentual_executado: Optional[Decimal] = None
    saldo_a_executar: Optional[Decimal] = None

    # Medicoes (resumo)
    medicoes: List[MeasurementSummary] = []

    # Outros
    observacoes: Optional[str] = None

    # Auditoria
    created_at: datetime
    updated_at: Optional[datetime] = None


class ContractAddendumCreate(BaseModel):
    """Schema para criacao de aditivo."""
    numero: str = Field(..., min_length=1, max_length=50)
    tipo: str = Field(..., pattern="^(valor|prazo|valor_prazo|supressao)$")
    objeto: str = Field(..., min_length=10)
    valor: Optional[Decimal] = None
    prazo_dias: Optional[int] = Field(None, ge=1)
    data_assinatura: Optional[date] = None


class ContractReadjustRequest(BaseModel):
    """Schema para solicitacao de reajuste."""
    percentual: Decimal = Field(..., ge=-50, le=100)
    data_aplicacao: Optional[date] = None
    justificativa: Optional[str] = None


class ContractReadjustResponse(BaseModel):
    """Resposta do calculo de reajuste."""
    contrato_id: UUID
    numero_contrato: str
    valor_original: Decimal
    percentual_reajuste: Decimal
    valor_reajuste: Decimal
    valor_novo: Decimal
    indice_utilizado: str
    data_aplicacao: date


class ContractListResponse(BaseModel):
    """Schema de lista de contratos com paginacao."""
    items: List[PublicContractResponse]
    total: int
    page: int
    size: int
    valor_total_contratos: Decimal
    valor_total_executado: Decimal
