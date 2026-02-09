"""
Schemas para EFD-Reinf.

Pydantic models para validação de entrada/saída da API.
"""

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class ClassificacaoTributariaEnum(StrEnum):
    """Classificação tributária."""

    EMPRESA_GERAL = "01"
    EMPRESA_SIMPLES = "02"
    MEI = "03"
    PRODUTOR_RURAL_PJ = "04"
    AGROINDUSTRIA = "06"
    PRODUTOR_RURAL_PF = "07"
    CONSORCIO = "08"
    ENTIDADE_IMUNE = "09"
    MISSAO_DIPLOMATICA = "10"
    ORGAO_PUBLICO = "11"


class TipoAmbienteEnum(StrEnum):
    """Tipo de ambiente."""

    PRODUCAO = "1"
    PRODUCAO_RESTRITA = "2"


class StatusEventoEnum(StrEnum):
    """Status do evento."""

    GERADO = "gerado"
    ENVIADO = "enviado"
    PROCESSADO = "processado"
    ACEITO = "aceito"
    REJEITADO = "rejeitado"
    ERRO = "erro"


# ============== Schemas R-1000 ==============


class GerarR1000Request(BaseModel):
    """Request para gerar evento R-1000 - Informações do Contribuinte."""

    razao_social: str = Field(..., min_length=2, max_length=150, description="Razão social do contribuinte")
    classificacao_tributaria: ClassificacaoTributariaEnum = Field(
        default=ClassificacaoTributariaEnum.EMPRESA_SIMPLES, description="Classificação tributária"
    )
    inicio_validade: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Início da validade (YYYY-MM)")
    fim_validade: str | None = Field(None, pattern=r"^\d{4}-\d{2}$", description="Fim da validade (YYYY-MM)")
    natureza_juridica: str | None = Field(None, max_length=4, description="Código da natureza jurídica")
    ind_coop: str = Field(default="0", pattern=r"^[0-3]$", description="Indicador de cooperativa (0=Não)")
    ind_constr: str = Field(default="0", pattern=r"^[0-1]$", description="Indicador de construtora (0=Não)")
    ind_desoneracao: str = Field(default="0", pattern=r"^[0-1]$", description="Indicador de desoneração (0=Não)")
    telefone: str | None = Field(None, max_length=13, description="Telefone de contato")
    email: str | None = Field(None, max_length=60, description="Email de contato")
    retificacao: bool = Field(default=False, description="Se é retificação de evento anterior")

    class Config:
        json_schema_extra = {
            "example": {
                "razao_social": "Conecta Segurança LTDA",
                "classificacao_tributaria": "02",
                "inicio_validade": "2026-01",
                "ind_coop": "0",
                "ind_constr": "0",
                "ind_desoneracao": "0",
                "email": "contato@conectaseguranca.com.br",
            }
        }


# ============== Schemas R-2010 ==============


class RetencaoServicoRequest(BaseModel):
    """Dados de retenção de serviço tomado."""

    cnpj_prestador: str = Field(..., min_length=14, max_length=18, description="CNPJ do prestador do serviço")
    valor_bruto: Decimal = Field(..., gt=0, description="Valor bruto da nota fiscal")
    valor_base_retencao: Decimal | None = Field(
        None, ge=0, description="Base de cálculo da retenção (default: valor_bruto)"
    )
    valor_retencao: Decimal = Field(..., ge=0, description="Valor da retenção (11% ou 3.5%)")
    valor_retencao_adicional: Decimal = Field(default=Decimal("0"), ge=0, description="Valor adicional de retenção")
    serie_nf: str = Field(default="1", max_length=5, description="Série da nota fiscal")
    numero_nf: str = Field(..., max_length=15, description="Número da nota fiscal")
    data_emissao_nf: str | None = Field(
        None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Data de emissão (YYYY-MM-DD)"
    )
    codigo_servico: str = Field(default="100000001", description="Código do tipo de serviço")
    ind_cprb: str = Field(default="0", pattern=r"^[0-1]$", description="Indicador CPRB (0=Não)")

    @field_validator("cnpj_prestador")
    @classmethod
    def validar_cnpj(cls, v: str) -> str:
        """Remove formatação do CNPJ."""
        return v.replace(".", "").replace("/", "").replace("-", "")


class GerarR2010Request(BaseModel):
    """Request para gerar evento R-2010 - Retenção Serviços Tomados."""

    periodo_apuracao: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Período de apuração (YYYY-MM)")
    retencoes: list[RetencaoServicoRequest] = Field(
        ..., min_length=1, description="Lista de retenções de serviços tomados"
    )
    retificacao: bool = Field(default=False, description="Se é retificação")

    class Config:
        json_schema_extra = {
            "example": {
                "periodo_apuracao": "2026-01",
                "retencoes": [
                    {
                        "cnpj_prestador": "12345678000199",
                        "valor_bruto": "10000.00",
                        "valor_retencao": "1100.00",
                        "numero_nf": "123456",
                        "data_emissao_nf": "2026-01-15",
                        "codigo_servico": "100000001",
                    }
                ],
            }
        }


# ============== Schemas R-4010 ==============


class PagamentoPFRequest(BaseModel):
    """Dados de pagamento a pessoa física."""

    cpf_beneficiario: str = Field(..., min_length=11, max_length=14, description="CPF do beneficiário")
    nome_beneficiario: str = Field(..., min_length=2, max_length=70, description="Nome do beneficiário")
    natureza_rendimento: str = Field(..., description="Código da natureza do rendimento")
    valor_bruto: Decimal = Field(..., gt=0, description="Valor bruto do pagamento")
    valor_irrf: Decimal = Field(default=Decimal("0"), ge=0, description="Valor do IRRF retido")
    valor_inss: Decimal = Field(default=Decimal("0"), ge=0, description="Valor do INSS retido")
    data_pagamento: str | None = Field(
        None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Data do pagamento (YYYY-MM-DD)"
    )
    descricao: str | None = Field(None, max_length=200, description="Descrição do pagamento")

    @field_validator("cpf_beneficiario")
    @classmethod
    def validar_cpf(cls, v: str) -> str:
        """Remove formatação do CPF."""
        return v.replace(".", "").replace("-", "")


class GerarR4010Request(BaseModel):
    """Request para gerar evento R-4010 - Pagamentos PF."""

    periodo_apuracao: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Período de apuração (YYYY-MM)")
    pagamentos: list[PagamentoPFRequest] = Field(..., min_length=1, description="Lista de pagamentos a pessoas físicas")
    retificacao: bool = Field(default=False, description="Se é retificação")

    class Config:
        json_schema_extra = {
            "example": {
                "periodo_apuracao": "2026-01",
                "pagamentos": [
                    {
                        "cpf_beneficiario": "12345678901",
                        "nome_beneficiario": "João da Silva",
                        "natureza_rendimento": "10008",
                        "valor_bruto": "5000.00",
                        "valor_irrf": "750.00",
                        "data_pagamento": "2026-01-20",
                        "descricao": "Prestação de serviços autônomos",
                    }
                ],
            }
        }


# ============== Schemas R-4020 ==============


class PagamentoPJRequest(BaseModel):
    """Dados de pagamento a pessoa jurídica."""

    cnpj_beneficiario: str = Field(..., min_length=14, max_length=18, description="CNPJ do beneficiário")
    razao_social: str = Field(..., min_length=2, max_length=150, description="Razão social do beneficiário")
    natureza_rendimento: str = Field(..., description="Código da natureza do rendimento")
    valor_bruto: Decimal = Field(..., gt=0, description="Valor bruto do pagamento")
    valor_irrf: Decimal = Field(default=Decimal("0"), ge=0, description="Valor do IRRF retido")
    valor_csll: Decimal = Field(default=Decimal("0"), ge=0, description="Valor da CSLL retida")
    valor_cofins: Decimal = Field(default=Decimal("0"), ge=0, description="Valor da COFINS retida")
    valor_pis: Decimal = Field(default=Decimal("0"), ge=0, description="Valor do PIS retido")
    data_pagamento: str | None = Field(
        None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="Data do pagamento (YYYY-MM-DD)"
    )
    numero_nf: str | None = Field(None, max_length=15, description="Número da nota fiscal")

    @field_validator("cnpj_beneficiario")
    @classmethod
    def validar_cnpj(cls, v: str) -> str:
        """Remove formatação do CNPJ."""
        return v.replace(".", "").replace("/", "").replace("-", "")


class GerarR4020Request(BaseModel):
    """Request para gerar evento R-4020 - Pagamentos PJ."""

    periodo_apuracao: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Período de apuração (YYYY-MM)")
    pagamentos: list[PagamentoPJRequest] = Field(
        ..., min_length=1, description="Lista de pagamentos a pessoas jurídicas"
    )
    retificacao: bool = Field(default=False, description="Se é retificação")

    class Config:
        json_schema_extra = {
            "example": {
                "periodo_apuracao": "2026-01",
                "pagamentos": [
                    {
                        "cnpj_beneficiario": "98765432000188",
                        "razao_social": "Empresa Prestadora LTDA",
                        "natureza_rendimento": "15004",
                        "valor_bruto": "25000.00",
                        "valor_irrf": "375.00",
                        "valor_csll": "250.00",
                        "valor_cofins": "750.00",
                        "valor_pis": "162.50",
                        "data_pagamento": "2026-01-25",
                        "numero_nf": "789012",
                    }
                ],
            }
        }


# ============== Schemas R-2099 ==============


class GerarR2099Request(BaseModel):
    """Request para gerar evento R-2099 - Fechamento."""

    periodo_apuracao: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Período de apuração (YYYY-MM)")
    retificacao: bool = Field(default=False, description="Se é retificação")

    class Config:
        json_schema_extra = {"example": {"periodo_apuracao": "2026-01", "retificacao": False}}


# ============== Schemas de Resposta ==============


class EventoResponse(BaseModel):
    """Response padrão para geração de evento."""

    evento: str = Field(..., description="Código do evento (R-XXXX)")
    descricao: str = Field(..., description="Descrição do evento")
    xml: str = Field(..., description="XML do evento gerado")
    cnpj: str = Field(..., description="CNPJ do contribuinte")
    periodo_apuracao: str | None = Field(None, description="Período de apuração")
    ambiente: str = Field(..., description="Ambiente (1=Prod, 2=Restrita)")
    status: StatusEventoEnum = Field(..., description="Status do evento")


class R1000Response(EventoResponse):
    """Response específico para R-1000."""

    inicio_validade: str = Field(..., description="Início da validade")
    classificacao_tributaria: str = Field(..., description="Classificação tributária")


class R2010Response(EventoResponse):
    """Response específico para R-2010."""

    quantidade_retencoes: int = Field(..., description="Quantidade de retenções")
    valor_total_bruto: str = Field(..., description="Valor total bruto")
    valor_total_retencao: str = Field(..., description="Valor total retido")


class R4010Response(EventoResponse):
    """Response específico para R-4010."""

    quantidade_pagamentos: int = Field(..., description="Quantidade de pagamentos")
    valor_total_bruto: str = Field(..., description="Valor total bruto")
    valor_total_irrf: str = Field(..., description="Valor total IRRF")


class R4020Response(EventoResponse):
    """Response específico para R-4020."""

    quantidade_pagamentos: int = Field(..., description="Quantidade de pagamentos")
    valor_total_bruto: str = Field(..., description="Valor total bruto")
    valor_total_retencoes: str = Field(..., description="Valor total retenções")


class LoteResponse(BaseModel):
    """Response para envio de lote."""

    xml_envio: str = Field(..., description="XML do lote")
    quantidade_eventos: int = Field(..., description="Quantidade de eventos")
    ambiente: str = Field(..., description="Ambiente")
    status: str = Field(..., description="Status do envio")
    mensagem: str | None = Field(None, description="Mensagem adicional")


class StatusReinfResponse(BaseModel):
    """Response para status do EFD-Reinf."""

    ambiente: str = Field(..., description="Ambiente configurado")
    url: str = Field(..., description="URL do WebService")
    cnpj: str = Field(..., description="CNPJ configurado")
    certificado_configurado: bool = Field(..., description="Se certificado está configurado")
    certificado_valido: bool = Field(..., description="Se certificado é válido")
    versao_layout: str = Field(..., description="Versão do layout")
    eventos_disponiveis: list[str] = Field(..., description="Lista de eventos disponíveis")


class NaturezaRendimento(BaseModel):
    """Natureza de rendimento."""

    codigo: str
    descricao: str


class NaturezasRendimentoResponse(BaseModel):
    """Response para lista de naturezas de rendimento."""

    pessoa_fisica: list[NaturezaRendimento]
    pessoa_juridica: list[NaturezaRendimento]


class ClassificacaoTributaria(BaseModel):
    """Classificação tributária."""

    codigo: str
    descricao: str


class ClassificacoesResponse(BaseModel):
    """Response para lista de classificações tributárias."""

    classificacoes: list[ClassificacaoTributaria]
