"""
Schemas para CT-e (Conhecimento de Transporte Eletronico).

Pydantic models para validacao de entrada/saida da API.
"""

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class ModalTransporteEnum(StrEnum):
    """Modal de transporte."""

    RODOVIARIO = "01"
    AEREO = "02"
    AQUAVIARIO = "03"
    FERROVIARIO = "04"
    DUTOVIARIO = "05"
    MULTIMODAL = "06"


class TipoServicoEnum(StrEnum):
    """Tipo de servico de transporte."""

    NORMAL = "0"
    SUBCONTRATACAO = "1"
    REDESPACHO = "2"
    REDESPACHO_INTERMEDIARIO = "3"
    SERVICO_VINCULADO_MULTIMODAL = "4"


class TomadorServicoEnum(StrEnum):
    """Indicador do tomador do servico."""

    REMETENTE = "0"
    EXPEDIDOR = "1"
    RECEBEDOR = "2"
    DESTINATARIO = "3"
    OUTROS = "4"


class SituacaoCTeEnum(StrEnum):
    """Situacao do CT-e."""

    EM_DIGITACAO = "em_digitacao"
    ASSINADO = "assinado"
    AUTORIZADO = "autorizado"
    CANCELADO = "cancelado"
    DENEGADO = "denegado"
    REJEITADO = "rejeitado"


# ============== Schemas de Entrada ==============


class ParticipanteRequest(BaseModel):
    """Dados do participante do CT-e."""

    tipo: str = Field(..., description="remetente, destinatario, expedidor, recebedor")
    cnpj_cpf: str = Field(..., min_length=11, max_length=14)
    nome: str = Field(..., max_length=60)
    inscricao_estadual: str | None = Field(None, max_length=14)
    endereco: str | None = Field(None, max_length=60)
    numero: str | None = Field(None, max_length=10)
    bairro: str | None = Field(None, max_length=60)
    codigo_municipio: str | None = Field(None, max_length=7)
    municipio: str | None = Field(None, max_length=60)
    uf: str | None = Field(None, max_length=2)
    cep: str | None = Field(None, max_length=8)
    telefone: str | None = Field(None, max_length=14)
    email: str | None = Field(None, max_length=60)

    class Config:
        json_schema_extra = {
            "example": {
                "tipo": "remetente",
                "cnpj_cpf": "12345678000190",
                "nome": "Empresa Remetente Ltda",
                "inscricao_estadual": "123456789",
                "uf": "SP",
            }
        }


class NFReferenciadaRequest(BaseModel):
    """NF-e referenciada no CT-e."""

    chave: str = Field(..., min_length=44, max_length=44)
    pin: str | None = Field(None, max_length=9, description="PIN SUFRAMA se aplicavel")

    class Config:
        json_schema_extra = {"example": {"chave": "35260100000000000000550010000000011000000011"}}


class CargaRequest(BaseModel):
    """Informacoes da carga."""

    valor_total_carga: Decimal = Field(..., ge=0)
    produto_predominante: str = Field(..., max_length=60)
    peso_bruto: Decimal = Field(default=Decimal("0"), ge=0)
    peso_cubado: Decimal = Field(default=Decimal("0"), ge=0)
    peso_aferido: Decimal = Field(default=Decimal("0"), ge=0)
    quantidade_volumes: int = Field(default=0, ge=0)
    unidade_medida: str = Field(default="KG", max_length=5)

    class Config:
        json_schema_extra = {
            "example": {
                "valor_total_carga": "50000.00",
                "produto_predominante": "ELETRONICOS",
                "peso_bruto": "1000.00",
                "quantidade_volumes": 50,
            }
        }


class ComponenteValorRequest(BaseModel):
    """Componente de valor do frete."""

    nome: str = Field(..., max_length=15)
    valor: Decimal = Field(..., ge=0)

    class Config:
        json_schema_extra = {"example": {"nome": "FRETE VALOR", "valor": "1500.00"}}


class CriarCTeRequest(BaseModel):
    """Request para criar CT-e."""

    numero: int = Field(..., gt=0)
    serie: int = Field(default=1, ge=1)
    modal: ModalTransporteEnum = Field(default=ModalTransporteEnum.RODOVIARIO)
    tipo_servico: TipoServicoEnum = Field(default=TipoServicoEnum.NORMAL)
    tomador: TomadorServicoEnum = Field(default=TomadorServicoEnum.REMETENTE)
    municipio_inicio: str | None = Field(None, max_length=7)
    uf_inicio: str | None = Field(None, max_length=2)
    municipio_fim: str | None = Field(None, max_length=7)
    uf_fim: str | None = Field(None, max_length=2)
    remetente: ParticipanteRequest | None = None
    destinatario: ParticipanteRequest | None = None
    expedidor: ParticipanteRequest | None = None
    recebedor: ParticipanteRequest | None = None
    nf_referenciadas: list[NFReferenciadaRequest] | None = None
    carga: CargaRequest | None = None
    valor_total_servico: Decimal = Field(default=Decimal("0"), ge=0)
    valor_receber: Decimal = Field(default=Decimal("0"), ge=0)
    componentes_valor: list[ComponenteValorRequest] | None = None
    icms_base_calculo: Decimal = Field(default=Decimal("0"), ge=0)
    icms_aliquota: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    icms_valor: Decimal = Field(default=Decimal("0"), ge=0)
    icms_cst: str = Field(default="00", max_length=3)

    class Config:
        json_schema_extra = {
            "example": {
                "numero": 1,
                "serie": 1,
                "modal": "01",
                "tipo_servico": "0",
                "tomador": "0",
                "municipio_inicio": "3550308",
                "uf_inicio": "SP",
                "municipio_fim": "3304557",
                "uf_fim": "RJ",
                "valor_total_servico": "1500.00",
                "valor_receber": "1500.00",
                "icms_base_calculo": "1500.00",
                "icms_aliquota": "12.00",
                "icms_valor": "180.00",
            }
        }


class GerarXMLRequest(BaseModel):
    """Request para gerar XML do CT-e."""

    numero: int = Field(..., gt=0)
    serie: int = Field(default=1, ge=1)
    modal: ModalTransporteEnum = Field(default=ModalTransporteEnum.RODOVIARIO)
    tipo_servico: TipoServicoEnum = Field(default=TipoServicoEnum.NORMAL)
    tomador: TomadorServicoEnum = Field(default=TomadorServicoEnum.REMETENTE)
    municipio_inicio: str | None = Field(None, max_length=7)
    uf_inicio: str | None = Field(None, max_length=2)
    municipio_fim: str | None = Field(None, max_length=7)
    uf_fim: str | None = Field(None, max_length=2)
    remetente: ParticipanteRequest | None = None
    destinatario: ParticipanteRequest | None = None
    expedidor: ParticipanteRequest | None = None
    recebedor: ParticipanteRequest | None = None
    nf_referenciadas: list[NFReferenciadaRequest] | None = None
    carga: CargaRequest | None = None
    valor_total_servico: Decimal = Field(default=Decimal("0"), ge=0)
    valor_receber: Decimal = Field(default=Decimal("0"), ge=0)
    componentes_valor: list[ComponenteValorRequest] | None = None
    icms_base_calculo: Decimal = Field(default=Decimal("0"), ge=0)
    icms_aliquota: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    icms_valor: Decimal = Field(default=Decimal("0"), ge=0)
    icms_cst: str = Field(default="00", max_length=3)

    class Config:
        json_schema_extra = {
            "example": {
                "numero": 1,
                "serie": 1,
                "modal": "01",
                "valor_total_servico": "1500.00",
                "valor_receber": "1500.00",
            }
        }


# ============== Schemas de Resposta ==============


class ModalResponse(BaseModel):
    """Modal de transporte."""

    codigo: str
    descricao: str


class ModaisResponse(BaseModel):
    """Lista de modais."""

    modais: list[ModalResponse]


class TipoServicoResponse(BaseModel):
    """Tipo de servico."""

    codigo: str
    descricao: str


class TiposServicoResponse(BaseModel):
    """Lista de tipos de servico."""

    tipos_servico: list[TipoServicoResponse]


class CTeResponse(BaseModel):
    """CT-e criado."""

    numero: int
    serie: int
    modal: str
    tipo_servico: str
    tomador: str
    situacao: str
    municipio_inicio: str | None
    municipio_fim: str | None
    valor_total_servico: str
    valor_receber: str


class XMLResponse(BaseModel):
    """XML gerado."""

    numero: int
    serie: int
    xml: str


class StatusServicoResponse(BaseModel):
    """Status do servico SEFAZ."""

    servico: str
    url: str
    status: str
    mensagem: str


class StatusCTeResponse(BaseModel):
    """Status do CT-e."""

    cnpj: str
    razao_social: str
    inscricao_estadual: str
    uf: str
    ambiente: str
    versao: str
    operacoes_disponiveis: list[str]
