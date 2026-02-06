"""
Schemas para NFS-e Manaus.

Pydantic models para validação de entrada/saída da API.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class NaturezaOperacaoEnum(str, Enum):
    """Natureza da operação."""
    TRIBUTACAO_MUNICIPIO = "1"
    TRIBUTACAO_FORA_MUNICIPIO = "2"
    ISENCAO = "3"
    IMUNE = "4"
    EXIGIBILIDADE_SUSPENSA_JUDICIAL = "5"
    EXIGIBILIDADE_SUSPENSA_ADM = "6"
    EXPORTACAO = "7"


class CodigoCancelamentoEnum(str, Enum):
    """Código do motivo de cancelamento."""
    ERRO_EMISSAO = "1"
    SERVICO_NAO_PRESTADO = "2"
    ERRO_PREENCHIMENTO = "3"
    DUPLICIDADE = "4"


class NFSeStatusEnum(str, Enum):
    """Status da NFS-e."""
    PENDENTE = "pendente"
    PROCESSANDO = "processando"
    AUTORIZADA = "autorizada"
    CANCELADA = "cancelada"
    SUBSTITUIDA = "substituida"
    ERRO = "erro"
    SIMULADO = "simulado"


# ============== Schemas de Entrada ==============

class TomadorRequest(BaseModel):
    """Dados do tomador do serviço."""
    cpf_cnpj: str = Field(
        ...,
        min_length=11,
        max_length=18,  # Aceita formato com pontuação: 12.345.678/0001-34
        description="CPF (11 dígitos) ou CNPJ (14 dígitos) do tomador"
    )
    razao_social: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Nome ou razão social do tomador"
    )
    endereco: str = Field(
        ...,
        min_length=1,
        max_length=125,
        description="Logradouro"
    )
    numero: str = Field(
        default="S/N",
        max_length=10,
        description="Número do endereço"
    )
    complemento: Optional[str] = Field(
        None,
        max_length=60,
        description="Complemento do endereço"
    )
    bairro: str = Field(
        ...,
        min_length=1,
        max_length=60,
        description="Bairro"
    )
    cidade: str = Field(
        default="Manaus",
        max_length=60,
        description="Cidade"
    )
    uf: str = Field(
        default="AM",
        min_length=2,
        max_length=2,
        description="Estado (UF)"
    )
    cep: str = Field(
        ...,
        min_length=8,
        max_length=10,  # Aceita formato com hífen: 69000-000
        description="CEP (8 dígitos, sem hífen)"
    )
    email: Optional[str] = Field(
        None,
        max_length=80,
        description="Email do tomador"
    )
    telefone: Optional[str] = Field(
        None,
        max_length=20,
        description="Telefone do tomador"
    )
    inscricao_municipal: Optional[str] = Field(
        None,
        max_length=15,
        description="Inscrição municipal do tomador (se houver)"
    )

    @field_validator("cpf_cnpj")
    @classmethod
    def validar_cpf_cnpj(cls, v: str) -> str:
        """Remove formatação e valida tamanho."""
        doc = v.replace(".", "").replace("-", "").replace("/", "")
        if len(doc) not in [11, 14]:
            raise ValueError("CPF deve ter 11 dígitos ou CNPJ 14 dígitos")
        return doc

    @field_validator("cep")
    @classmethod
    def validar_cep(cls, v: str) -> str:
        """Remove formatação do CEP."""
        cep = v.replace("-", "").replace(".", "")
        if len(cep) != 8:
            raise ValueError("CEP deve ter 8 dígitos")
        return cep


class ServicoRequest(BaseModel):
    """Dados do serviço prestado."""
    codigo_servico: str = Field(
        default="11.02",
        description="Código do serviço (Lista LC 116). Ex: 11.02 para vigilância"
    )
    discriminacao: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Descrição detalhada do serviço prestado"
    )
    valor_servicos: Decimal = Field(
        ...,
        gt=0,
        description="Valor total dos serviços"
    )
    valor_deducoes: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Valor de deduções permitidas"
    )
    aliquota_iss: Decimal = Field(
        default=Decimal("0.05"),
        ge=0,
        le=1,
        description="Alíquota do ISS (0.05 = 5%)"
    )
    iss_retido: bool = Field(
        default=False,
        description="Se o ISS será retido pelo tomador"
    )
    codigo_cnae: Optional[str] = Field(
        None,
        max_length=7,
        description="Código CNAE da atividade"
    )


class EmitirNFSeRequest(BaseModel):
    """Request para emissão de NFS-e."""
    tomador: TomadorRequest
    servico: ServicoRequest
    competencia: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}$",
        description="Competência no formato YYYY-MM (default: mês atual)"
    )
    natureza_operacao: NaturezaOperacaoEnum = Field(
        default=NaturezaOperacaoEnum.TRIBUTACAO_MUNICIPIO,
        description="Natureza da operação fiscal"
    )
    optante_simples: bool = Field(
        default=True,
        description="Se é optante do Simples Nacional"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "tomador": {
                    "cpf_cnpj": "12345678901234",
                    "razao_social": "Empresa Cliente LTDA",
                    "endereco": "Av. Eduardo Ribeiro",
                    "numero": "1000",
                    "bairro": "Centro",
                    "cidade": "Manaus",
                    "uf": "AM",
                    "cep": "69010001",
                    "email": "contato@empresa.com.br"
                },
                "servico": {
                    "codigo_servico": "11.02",
                    "discriminacao": "Serviços de vigilância patrimonial armada conforme contrato 001/2026, período de janeiro/2026",
                    "valor_servicos": "15000.00",
                    "aliquota_iss": "0.05",
                    "iss_retido": False
                },
                "competencia": "2026-01",
                "natureza_operacao": "1",
                "optante_simples": True
            }
        }


class ConsultarNFSeRpsRequest(BaseModel):
    """Request para consulta de NFS-e por RPS."""
    numero_rps: str = Field(
        ...,
        description="Número do RPS"
    )
    serie: str = Field(
        default="RPS",
        description="Série do RPS"
    )
    tipo: str = Field(
        default="1",
        description="Tipo do RPS (1=RPS)"
    )


class ConsultarNFSeNumeroRequest(BaseModel):
    """Request para consulta de NFS-e por número."""
    numero_nfse: str = Field(
        ...,
        description="Número da NFS-e"
    )


class CancelarNFSeRequest(BaseModel):
    """Request para cancelamento de NFS-e."""
    numero_nfse: str = Field(
        ...,
        description="Número da NFS-e a cancelar"
    )
    codigo_cancelamento: CodigoCancelamentoEnum = Field(
        default=CodigoCancelamentoEnum.ERRO_EMISSAO,
        description="Código do motivo do cancelamento"
    )
    motivo: Optional[str] = Field(
        None,
        max_length=255,
        description="Descrição do motivo do cancelamento"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "numero_nfse": "123456",
                "codigo_cancelamento": "1",
                "motivo": "Erro no valor do serviço"
            }
        }


class SubstituirNFSeRequest(BaseModel):
    """Request para substituição de NFS-e."""
    numero_nfse_substituida: str = Field(
        ...,
        description="Número da NFS-e a ser substituída"
    )
    tomador: TomadorRequest
    servico: ServicoRequest


# ============== Schemas de Saída ==============

class NFSeResponse(BaseModel):
    """Response padrão de NFS-e."""
    numero_nfse: Optional[str] = Field(None, description="Número da NFS-e")
    numero_rps: Optional[str] = Field(None, description="Número do RPS")
    numero_lote: Optional[str] = Field(None, description="Número do lote")
    codigo_verificacao: Optional[str] = Field(None, description="Código de verificação")
    protocolo: Optional[str] = Field(None, description="Protocolo de recebimento")
    status: NFSeStatusEnum = Field(..., description="Status da operação")
    mensagem: Optional[str] = Field(None, description="Mensagem de retorno")
    data_emissao: Optional[datetime] = Field(None, description="Data/hora da emissão")
    xml_envio: Optional[str] = Field(None, description="XML enviado")


class EmitirNFSeResponse(NFSeResponse):
    """Response para emissão de NFS-e."""
    valor_servicos: Optional[Decimal] = Field(None, description="Valor dos serviços")
    valor_iss: Optional[Decimal] = Field(None, description="Valor do ISS")
    tomador_cpf_cnpj: Optional[str] = Field(None, description="CPF/CNPJ do tomador")

    class Config:
        json_schema_extra = {
            "example": {
                "numero_nfse": "123456",
                "numero_rps": "1737000000",
                "numero_lote": "1737000001",
                "codigo_verificacao": "ABCD1234",
                "protocolo": "123456789",
                "status": "autorizada",
                "mensagem": None,
                "data_emissao": "2026-01-16T10:30:00",
                "valor_servicos": "15000.00",
                "valor_iss": "750.00",
                "tomador_cpf_cnpj": "12345678901234"
            }
        }


class ConsultarNFSeResponse(BaseModel):
    """Response para consulta de NFS-e."""
    numero_nfse: Optional[str] = None
    numero_rps: Optional[str] = None
    status: NFSeStatusEnum
    data_emissao: Optional[datetime] = None
    codigo_verificacao: Optional[str] = None
    valor_servicos: Optional[Decimal] = None
    valor_iss: Optional[Decimal] = None
    tomador: Optional[Dict[str, Any]] = None
    prestador: Optional[Dict[str, Any]] = None
    servico: Optional[Dict[str, Any]] = None
    mensagem: Optional[str] = None


class CancelarNFSeResponse(BaseModel):
    """Response para cancelamento de NFS-e."""
    numero_nfse: str
    status: NFSeStatusEnum
    data_cancelamento: Optional[datetime] = None
    protocolo: Optional[str] = None
    mensagem: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "numero_nfse": "123456",
                "status": "cancelada",
                "data_cancelamento": "2026-01-16T11:00:00",
                "protocolo": "987654321",
                "mensagem": None
            }
        }


class ValidarConexaoResponse(BaseModel):
    """Response para validação de conexão."""
    ambiente: str
    cnpj: str
    url_base: str
    conexao_http: bool
    http_status: Optional[int] = None
    certificado_configurado: bool
    certificado_valido: Optional[bool] = None
    certificado_expira: Optional[str] = None
    mensagem: Optional[str] = None


class LoteNFSeResponse(BaseModel):
    """Response para consulta de lote."""
    numero_lote: str
    situacao: str
    quantidade_rps: Optional[int] = None
    notas_processadas: Optional[List[NFSeResponse]] = None
    erros: Optional[List[Dict[str, Any]]] = None
