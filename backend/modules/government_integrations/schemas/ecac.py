"""
Schemas para e-CAC - Centro Virtual de Atendimento ao Contribuinte.

Pydantic models para validacao de entrada/saida da API.
"""

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class TipoCertidaoEnum(StrEnum):
    """Tipo de certidao fiscal."""

    CND = "cnd"
    CPEN = "cpen"
    CPD = "cpd"


class SituacaoFiscalEnum(StrEnum):
    """Situacao fiscal do contribuinte."""

    REGULAR = "regular"
    PENDENTE = "pendente"
    IRREGULAR = "irregular"
    OMISSO = "omisso"


class TipoPendenciaEnum(StrEnum):
    """Tipo de pendencia fiscal."""

    DEBITO = "debito"
    DECLARACAO_OMISSA = "declaracao_omissa"
    MALHA_FISCAL = "malha_fiscal"
    PROCESSO = "processo"
    PARCELAMENTO = "parcelamento"


class TipoDeclaracaoEnum(StrEnum):
    """Tipo de declaracao para consulta."""

    IRPF = "irpf"
    IRPJ = "irpj"
    DCTF = "dctf"
    DCTFWEB = "dctfweb"
    EFD_CONTRIBUICOES = "efd_contribuicoes"
    EFD_REINF = "efd_reinf"
    ECF = "ecf"
    DIRF = "dirf"
    PGDAS = "pgdas"
    DEFIS = "defis"


class SituacaoDebitoEnum(StrEnum):
    """Situacao do debito."""

    ABERTO = "aberto"
    SUSPENSO = "suspenso"
    PARCELADO = "parcelado"
    PAGO = "pago"


class SituacaoProcessoEnum(StrEnum):
    """Situacao do processo."""

    ATIVO = "ativo"
    ENCERRADO = "encerrado"
    SUSPENSO = "suspenso"
    AGUARDANDO = "aguardando"


# ============== Request Schemas ==============


class ConsultaSituacaoFiscalRequest(BaseModel):
    """Request para consulta de situacao fiscal."""

    cpf_cnpj: str | None = Field(None, description="CPF ou CNPJ para consulta (opcional, usa o configurado)")

    @field_validator("cpf_cnpj")
    @classmethod
    def validar_documento(cls, v: str | None) -> str | None:
        """Remove formatacao do documento."""
        if v:
            return v.replace(".", "").replace("/", "").replace("-", "")
        return v


class ConsultaDebitosRequest(BaseModel):
    """Request para consulta de debitos."""

    situacao: SituacaoDebitoEnum | None = Field(None, description="Filtro por situacao do debito")
    competencia_inicio: str | None = Field(None, pattern=r"^\d{4}-\d{2}$", description="Competencia inicial (YYYY-MM)")
    competencia_fim: str | None = Field(None, pattern=r"^\d{4}-\d{2}$", description="Competencia final (YYYY-MM)")

    class Config:
        json_schema_extra = {
            "example": {"situacao": "aberto", "competencia_inicio": "2025-01", "competencia_fim": "2025-12"}
        }


class ConsultaDeclaracoesRequest(BaseModel):
    """Request para consulta de declaracoes."""

    tipo: TipoDeclaracaoEnum = Field(..., description="Tipo de declaracao")
    exercicio_inicio: int = Field(..., ge=2000, le=2100, description="Exercicio inicial")
    exercicio_fim: int | None = Field(None, ge=2000, le=2100, description="Exercicio final")

    class Config:
        json_schema_extra = {"example": {"tipo": "dctfweb", "exercicio_inicio": 2025, "exercicio_fim": 2026}}


class EmitirCertidaoRequest(BaseModel):
    """Request para emissao de certidao."""

    finalidade: str | None = Field(None, max_length=200, description="Finalidade da certidao")
    cpf_cnpj: str | None = Field(None, description="CPF ou CNPJ (opcional, usa o configurado)")

    @field_validator("cpf_cnpj")
    @classmethod
    def validar_documento(cls, v: str | None) -> str | None:
        """Remove formatacao do documento."""
        if v:
            return v.replace(".", "").replace("/", "").replace("-", "")
        return v

    class Config:
        json_schema_extra = {"example": {"finalidade": "Licitacao publica"}}


class ValidarCertidaoRequest(BaseModel):
    """Request para validacao de certidao."""

    numero: str = Field(..., min_length=1, max_length=50, description="Numero da certidao")
    codigo_controle: str = Field(..., min_length=1, max_length=50, description="Codigo de controle da certidao")

    class Config:
        json_schema_extra = {"example": {"numero": "123456789", "codigo_controle": "ABCD1234EFGH5678"}}


class ConsultaParcelamentosRequest(BaseModel):
    """Request para consulta de parcelamentos."""

    situacao: str | None = Field(None, description="Filtro por situacao (ativo, encerrado)")


class SimularParcelamentoRequest(BaseModel):
    """Request para simulacao de parcelamento."""

    debitos: list[str] = Field(..., min_length=1, description="Lista de codigos de debitos a parcelar")
    quantidade_parcelas: int = Field(..., ge=2, le=60, description="Quantidade de parcelas (2 a 60)")

    class Config:
        json_schema_extra = {"example": {"debitos": ["DEB001", "DEB002", "DEB003"], "quantidade_parcelas": 12}}


class ConsultaProcessosRequest(BaseModel):
    """Request para consulta de processos."""

    situacao: SituacaoProcessoEnum | None = Field(None, description="Filtro por situacao do processo")
    numero_processo: str | None = Field(None, description="Numero especifico do processo")


# ============== Response Schemas ==============


class PendenciaFiscalResponse(BaseModel):
    """Pendencia fiscal."""

    tipo: TipoPendenciaEnum
    descricao: str
    valor: str | None = None
    data_vencimento: str | None = None
    numero_processo: str | None = None
    exercicio: int | None = None
    periodo_apuracao: str | None = None


class DebitoFiscalResponse(BaseModel):
    """Debito fiscal."""

    codigo_receita: str
    descricao: str
    competencia: str
    valor_principal: str
    valor_multa: str
    valor_juros: str
    valor_total: str
    data_vencimento: str | None = None
    situacao: str
    numero_processo: str | None = None


class SituacaoFiscalResponse(BaseModel):
    """Response da consulta de situacao fiscal."""

    cpf_cnpj: str
    nome: str
    situacao: SituacaoFiscalEnum
    data_consulta: str
    pendencias: list[PendenciaFiscalResponse]
    debitos: list[DebitoFiscalResponse]
    declaracoes_omissas: list[str]
    certidao_disponivel: bool
    tipo_certidao_disponivel: TipoCertidaoEnum | None = None


class CertidaoResponse(BaseModel):
    """Response de emissao de certidao."""

    tipo: TipoCertidaoEnum
    numero: str
    data_emissao: str
    data_validade: str
    codigo_controle: str
    contribuinte_cpf_cnpj: str
    contribuinte_nome: str
    finalidade: str | None = None
    observacoes: str | None = None


class ValidacaoCertidaoResponse(BaseModel):
    """Response de validacao de certidao."""

    numero: str
    codigo_controle: str
    valida: bool
    data_validacao: str
    tipo_certidao: TipoCertidaoEnum | None = None
    data_emissao: str | None = None
    data_validade: str | None = None
    contribuinte: str | None = None
    mensagem: str


class DeclaracaoResponse(BaseModel):
    """Declaracao consultada."""

    tipo: TipoDeclaracaoEnum
    exercicio: int
    numero_recibo: str
    data_transmissao: str
    situacao: str
    retificadora: bool
    numero_recibo_anterior: str | None = None


class ParcelamentoResponse(BaseModel):
    """Parcelamento ativo."""

    numero: str
    tipo: str
    data_adesao: str
    valor_consolidado: str
    quantidade_parcelas: int
    parcelas_pagas: int
    parcelas_em_aberto: int
    valor_parcela: str
    situacao: str
    proxima_parcela: str | None = None
    data_vencimento_proxima: str | None = None


class SimulacaoParcelamentoResponse(BaseModel):
    """Response de simulacao de parcelamento."""

    debitos: list[str]
    quantidade_debitos: int
    valor_total_debitos: str
    quantidade_parcelas: int
    valor_primeira_parcela: str
    valor_demais_parcelas: str
    taxa_juros: str
    data_primeira_parcela: str
    observacoes: str | None = None


class ProcessoResponse(BaseModel):
    """Processo digital."""

    numero: str
    tipo: str
    assunto: str
    data_abertura: str
    situacao: SituacaoProcessoEnum
    ultima_movimentacao: str | None = None
    data_ultima_movimentacao: str | None = None
    responsavel: str | None = None


class StatusEcacResponse(BaseModel):
    """Response de status do e-CAC."""

    ambiente: str = Field(..., description="Ambiente configurado")
    url: str = Field(..., description="URL do e-CAC")
    cpf_cnpj: str = Field(..., description="CPF/CNPJ configurado")
    tipo_documento: str = Field(..., description="Tipo: CPF ou CNPJ")
    certificado_configurado: bool = Field(..., description="Se certificado esta configurado")
    certificado_valido: bool = Field(..., description="Se certificado e valido")
    servicos_disponiveis: list[str] = Field(..., description="Lista de servicos disponiveis")
