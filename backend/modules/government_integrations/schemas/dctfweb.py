"""
Schemas para DCTFWeb.

Pydantic models para validação de entrada/saída da API.
"""

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class TipoDeclaracaoEnum(StrEnum):
    """Tipo de declaração DCTFWeb."""

    MENSAL = "1"
    ANUAL = "2"
    DIARIA = "3"
    ESPECIAL = "4"


class SituacaoDeclaracaoEnum(StrEnum):
    """Situação da declaração."""

    EM_ANDAMENTO = "em_andamento"
    ATIVA = "ativa"
    RETIFICADA = "retificada"
    EXCLUIDA = "excluida"


class TipoCreditoEnum(StrEnum):
    """Tipo de crédito vinculável."""

    SALARIO_FAMILIA = "1"
    SALARIO_MATERNIDADE = "2"
    RETENCAO_LEI_9711 = "3"
    COMPENSACAO = "4"
    SUSPENSAO = "5"
    PARCELAMENTO = "6"


# ============== Schemas de Entrada ==============


class CriarDeclaracaoRequest(BaseModel):
    """Request para criar declaração DCTFWeb."""

    periodo_apuracao: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Período de apuração (YYYY-MM)")
    tipo: TipoDeclaracaoEnum = Field(default=TipoDeclaracaoEnum.MENSAL, description="Tipo da declaração")

    class Config:
        json_schema_extra = {"example": {"periodo_apuracao": "2026-01", "tipo": "1"}}


class DadosESocialRequest(BaseModel):
    """Dados do eSocial para importação."""

    contribuicao_patronal: Decimal | None = Field(None, ge=0, description="Contribuição patronal (CP)")
    contribuicao_segurado: Decimal | None = Field(None, ge=0, description="Contribuição descontada do segurado")
    rat: Decimal | None = Field(None, ge=0, description="GILRAT/RAT Ajustado")
    terceiros: dict[str, Decimal] | None = Field(None, description="Contribuições a terceiros (Sistema S) por código")
    salario_familia: Decimal | None = Field(None, ge=0, description="Salário-família (crédito)")
    salario_maternidade: Decimal | None = Field(None, ge=0, description="Salário-maternidade (crédito)")

    class Config:
        json_schema_extra = {
            "example": {
                "contribuicao_patronal": "25000.00",
                "contribuicao_segurado": "8500.00",
                "rat": "2500.00",
                "terceiros": {"1184": "1500.00", "1190": "500.00"},
                "salario_familia": "150.00",
            }
        }


class RetencaoReinfRequest(BaseModel):
    """Dados de retenção da EFD-Reinf."""

    cnpj_prestador: str = Field(..., min_length=14, max_length=14, description="CNPJ do prestador")
    valor_retencao: Decimal = Field(..., ge=0, description="Valor da retenção")
    numero_nf: str | None = Field(None, description="Número da nota fiscal")


class DadosReinfRequest(BaseModel):
    """Dados da EFD-Reinf para importação."""

    retencoes_tomados: list[RetencaoReinfRequest] | None = Field(
        None, description="Retenções de serviços tomados (R-2010)"
    )
    retencoes_prestados: list[RetencaoReinfRequest] | None = Field(
        None, description="Retenções de serviços prestados (R-2020)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "retencoes_tomados": [
                    {"cnpj_prestador": "12345678000199", "valor_retencao": "1100.00", "numero_nf": "123456"}
                ]
            }
        }


class ImportarESocialRequest(BaseModel):
    """Request para importar dados do eSocial."""

    periodo_apuracao: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Período de apuração (YYYY-MM)")
    dados_esocial: DadosESocialRequest

    class Config:
        json_schema_extra = {
            "example": {
                "periodo_apuracao": "2026-01",
                "dados_esocial": {
                    "contribuicao_patronal": "25000.00",
                    "contribuicao_segurado": "8500.00",
                    "rat": "2500.00",
                },
            }
        }


class ImportarReinfRequest(BaseModel):
    """Request para importar dados da EFD-Reinf."""

    periodo_apuracao: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Período de apuração (YYYY-MM)")
    dados_reinf: DadosReinfRequest

    class Config:
        json_schema_extra = {
            "example": {
                "periodo_apuracao": "2026-01",
                "dados_reinf": {
                    "retencoes_tomados": [{"cnpj_prestador": "12345678000199", "valor_retencao": "1100.00"}]
                },
            }
        }


class ConsolidarDeclaracaoRequest(BaseModel):
    """Request para consolidar declaração."""

    periodo_apuracao: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Período de apuração (YYYY-MM)")
    dados_esocial: DadosESocialRequest | None = None
    dados_reinf: DadosReinfRequest | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "periodo_apuracao": "2026-01",
                "dados_esocial": {"contribuicao_patronal": "25000.00", "contribuicao_segurado": "8500.00"},
                "dados_reinf": {
                    "retencoes_tomados": [{"cnpj_prestador": "12345678000199", "valor_retencao": "1100.00"}]
                },
            }
        }


class GerarDarfsRequest(BaseModel):
    """Request para gerar DARFs."""

    periodo_apuracao: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Período de apuração (YYYY-MM)")
    dados_esocial: DadosESocialRequest | None = None
    dados_reinf: DadosReinfRequest | None = None
    data_vencimento: str | None = Field(
        None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Data de vencimento (YYYY-MM-DD)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "periodo_apuracao": "2026-01",
                "dados_esocial": {"contribuicao_patronal": "25000.00", "contribuicao_segurado": "8500.00"},
                "data_vencimento": "2026-02-20",
            }
        }


class TransmitirDeclaracaoRequest(BaseModel):
    """Request para transmitir declaração."""

    periodo_apuracao: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Período de apuração (YYYY-MM)")
    dados_esocial: DadosESocialRequest | None = None
    dados_reinf: DadosReinfRequest | None = None

    class Config:
        json_schema_extra = {
            "example": {"periodo_apuracao": "2026-01", "dados_esocial": {"contribuicao_patronal": "25000.00"}}
        }


class ConsultarDeclaracaoRequest(BaseModel):
    """Request para consultar declaração."""

    periodo_apuracao: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Período de apuração (YYYY-MM)")


# ============== Schemas de Resposta ==============


class DebitoResponse(BaseModel):
    """Débito de contribuição."""

    codigo_receita: str
    descricao: str
    valor_principal: str
    valor_acrescimos: str
    valor_total: str
    periodo_apuracao: str


class CreditoResponse(BaseModel):
    """Crédito vinculável."""

    tipo: str
    descricao: str
    valor: str
    periodo_apuracao: str
    numero_documento: str | None = None


class DARFResponse(BaseModel):
    """DARF gerado."""

    codigo_receita: str
    periodo_apuracao: str
    data_vencimento: str
    valor_principal: str
    valor_multa: str
    valor_juros: str
    valor_total: str
    numero_referencia: str | None = None
    codigo_barras: str | None = None
    linha_digitavel: str | None = None


class DeclaracaoResponse(BaseModel):
    """Response completo de declaração."""

    numero_recibo: str | None = None
    tipo: str
    tipo_descricao: str
    situacao: str
    periodo_apuracao: str
    data_transmissao: str | None = None
    cnpj: str
    razao_social: str
    debitos: list[DebitoResponse] = []
    creditos: list[CreditoResponse] = []
    total_debitos: str
    total_creditos: str
    saldo_a_pagar: str
    darfs: list[DARFResponse] = []


class DarfsGeradosResponse(BaseModel):
    """Response para geração de DARFs."""

    periodo_apuracao: str
    total_debitos: str
    total_creditos: str
    saldo_a_pagar: str
    quantidade_darfs: int
    darfs: list[DARFResponse]


class TransmissaoResponse(BaseModel):
    """Response de transmissão."""

    numero_recibo: str
    data_transmissao: str
    situacao: str
    total_debitos: str
    total_creditos: str
    saldo_a_pagar: str
    quantidade_darfs: int


class StatusDCTFWebResponse(BaseModel):
    """Response para status."""

    ambiente: str
    cnpj: str
    razao_social: str
    portal_ecac: str
    operacoes_disponiveis: list[str]


class CodigoReceita(BaseModel):
    """Código de receita."""

    codigo: str
    descricao: str


class CodigosReceitaResponse(BaseModel):
    """Response para códigos de receita."""

    codigos: list[CodigoReceita]


class TipoDeclaracao(BaseModel):
    """Tipo de declaração."""

    codigo: str
    descricao: str


class TiposDeclaracaoResponse(BaseModel):
    """Response para tipos de declaração."""

    tipos: list[TipoDeclaracao]


class TipoCredito(BaseModel):
    """Tipo de crédito."""

    codigo: str
    descricao: str


class TiposCreditoResponse(BaseModel):
    """Response para tipos de crédito."""

    tipos: list[TipoCredito]
