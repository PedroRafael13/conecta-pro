"""
Schemas de Contrato Publico - Licitacoes
========================================
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.bidding.models.public_contract import AdjustmentIndex


class MeasurementSummary(BaseModel):
    """Resumo de medicao para resposta de contrato."""

    id: UUID
    numero_medicao: int
    competencia: str
    valor_bruto: Decimal
    valor_liquido: Decimal
    status: str
    data_aprovacao: date | None = None


class PublicContractBase(BaseModel):
    """Schema base para contrato publico."""

    numero_contrato: str = Field(..., min_length=1, max_length=50)
    ano_contrato: int = Field(..., ge=2000, le=2100)
    objeto: str = Field(..., min_length=10)
    objeto_resumido: str | None = Field(None, max_length=500)

    # Orgao
    orgao_cnpj: str = Field(..., min_length=14, max_length=18)
    orgao_nome: str = Field(..., min_length=1, max_length=255)
    orgao_uf: str = Field(default="AM", min_length=2, max_length=2)


class PublicContractCreate(PublicContractBase):
    """Schema para criacao de contrato publico."""

    tender_id: UUID | None = None

    # Orgao
    unidade_gestora: str | None = None
    gestor_contrato: str | None = None
    fiscal_contrato: str | None = None

    # Valores
    valor_contrato: Decimal = Field(..., gt=0)

    # Empenho
    numero_empenho: str | None = None
    data_empenho: date | None = None
    nota_empenho_url: str | None = None

    # Vigencia
    data_assinatura: date | None = None
    data_publicacao: date | None = None
    data_vigencia_inicio: date
    data_vigencia_fim: date
    prazo_meses: int | None = None

    # Reajuste
    indice_reajuste: str = Field(default=AdjustmentIndex.IGPM.value)
    data_base_reajuste: date | None = None

    # Garantia
    garantia_tipo: str | None = None
    garantia_valor: Decimal | None = None
    garantia_percentual: Decimal | None = Field(None, ge=0, le=10)
    garantia_vencimento: date | None = None
    garantia_documento_url: str | None = None

    # PNCP
    pncp_id: str | None = None
    pncp_link: str | None = None

    # Arquivos
    arquivo_contrato_url: str | None = None
    arquivo_publicacao_url: str | None = None

    # Outros
    observacoes: str | None = None


class PublicContractUpdate(BaseModel):
    """Schema para atualizacao de contrato publico."""

    objeto: str | None = None
    objeto_resumido: str | None = None

    # Orgao
    gestor_contrato: str | None = None
    fiscal_contrato: str | None = None

    # Valores
    valor_empenhado: Decimal | None = None
    valor_executado: Decimal | None = None
    valor_pago: Decimal | None = None

    # Empenho
    numero_empenho: str | None = None
    data_empenho: date | None = None
    nota_empenho_url: str | None = None

    # Vigencia
    data_assinatura: date | None = None
    data_publicacao: date | None = None

    # Status
    status: str | None = None

    # Garantia
    garantia_tipo: str | None = None
    garantia_valor: Decimal | None = None
    garantia_vencimento: date | None = None
    garantia_documento_url: str | None = None

    # Arquivos
    arquivo_contrato_url: str | None = None
    arquivo_publicacao_url: str | None = None

    # Outros
    observacoes: str | None = None


class PublicContractResponse(PublicContractBase):
    """Schema de resposta para contrato publico."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tender_id: UUID | None = None
    status: str
    ativo: bool

    # Orgao
    unidade_gestora: str | None = None
    gestor_contrato: str | None = None
    fiscal_contrato: str | None = None

    # Valores
    valor_contrato: Decimal
    valor_empenhado: Decimal | None = None
    valor_executado: Decimal | None = None
    valor_pago: Decimal | None = None
    saldo_contrato: Decimal | None = None

    # Empenho
    numero_empenho: str | None = None
    data_empenho: date | None = None
    nota_empenho_url: str | None = None

    # Vigencia
    data_assinatura: date | None = None
    data_publicacao: date | None = None
    data_vigencia_inicio: date
    data_vigencia_fim: date
    prazo_meses: int | None = None

    # Reajuste
    indice_reajuste: str | None = None
    data_base_reajuste: date | None = None
    ultimo_reajuste: date | None = None
    percentual_ultimo_reajuste: Decimal | None = None

    # Garantia
    garantia_tipo: str | None = None
    garantia_valor: Decimal | None = None
    garantia_percentual: Decimal | None = None
    garantia_vencimento: date | None = None
    garantia_documento_url: str | None = None

    # Aditivos
    aditivos: list[dict] = []
    quantidade_aditivos: int = 0

    # PNCP
    pncp_id: str | None = None
    pncp_link: str | None = None

    # Arquivos
    arquivo_contrato_url: str | None = None
    arquivo_publicacao_url: str | None = None

    # Propriedades calculadas
    esta_vigente: bool | None = None
    dias_para_vencer: int | None = None
    percentual_executado: Decimal | None = None
    saldo_a_executar: Decimal | None = None

    # Medicoes (resumo)
    medicoes: list[MeasurementSummary] = []

    # Outros
    observacoes: str | None = None

    # Auditoria
    created_at: datetime
    updated_at: datetime | None = None


class ContractAddendumCreate(BaseModel):
    """Schema para criacao de aditivo."""

    numero: str = Field(..., min_length=1, max_length=50)
    tipo: str = Field(..., pattern="^(valor|prazo|valor_prazo|supressao)$")
    objeto: str = Field(..., min_length=10)
    valor: Decimal | None = None
    prazo_dias: int | None = Field(None, ge=1)
    data_assinatura: date | None = None


class ContractReadjustRequest(BaseModel):
    """Schema para solicitacao de reajuste."""

    percentual: Decimal = Field(..., ge=-50, le=100)
    data_aplicacao: date | None = None
    justificativa: str | None = None


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

    items: list[PublicContractResponse]
    total: int
    page: int
    size: int
    valor_total_contratos: Decimal
    valor_total_executado: Decimal
