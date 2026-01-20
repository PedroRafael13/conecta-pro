"""
Schemas para MDF-e (Manifesto Eletronico de Documentos Fiscais).

Pydantic models para validacao de entrada/saida da API.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field


class ModalTransporteEnum(str, Enum):
    """Modal de transporte."""
    RODOVIARIO = "1"
    AEREO = "2"
    AQUAVIARIO = "3"
    FERROVIARIO = "4"


class TipoEmitenteEnum(str, Enum):
    """Tipo de emitente do MDF-e."""
    TRANSPORTADORA = "1"  # Prestador de servico de transporte
    CARGA_PROPRIA = "2"   # Transportador de carga propria
    CTC = "3"             # Correios


class TipoCarroceriaEnum(str, Enum):
    """Tipo de carroceria."""
    NAO_APLICAVEL = "00"
    ABERTA = "01"
    FECHADA_BAU = "02"
    GRANELEIRA = "03"
    PORTA_CONTAINER = "04"
    SIDER = "05"


class TipoRodadoEnum(str, Enum):
    """Tipo de rodado do veiculo."""
    TRUCK = "01"
    TOCO = "02"
    CAVALO_MECANICO = "03"
    VAN = "04"
    UTILITARIO = "05"
    OUTROS = "06"


class SituacaoMDFeEnum(str, Enum):
    """Situacao do MDF-e."""
    EM_DIGITACAO = "em_digitacao"
    ASSINADO = "assinado"
    AUTORIZADO = "autorizado"
    CANCELADO = "cancelado"
    ENCERRADO = "encerrado"
    REJEITADO = "rejeitado"


# ============== Schemas de Entrada ==============

class CondutorRequest(BaseModel):
    """Dados do condutor."""
    cpf: str = Field(..., min_length=11, max_length=11)
    nome: str = Field(..., min_length=1, max_length=60)

    class Config:
        json_schema_extra = {
            "example": {
                "cpf": "12345678901",
                "nome": "Joao Silva"
            }
        }


class VeiculoRequest(BaseModel):
    """Dados do veiculo de tracao."""
    placa: str = Field(..., min_length=7, max_length=7)
    renavam: Optional[str] = Field(None, max_length=11)
    uf: str = Field(..., min_length=2, max_length=2)
    tara: Decimal = Field(default=Decimal("0"), ge=0, description="Peso do veiculo vazio (kg)")
    capacidade_kg: Decimal = Field(default=Decimal("0"), ge=0)
    capacidade_m3: Decimal = Field(default=Decimal("0"), ge=0)
    tipo_rodado: TipoRodadoEnum = Field(default=TipoRodadoEnum.TRUCK)
    tipo_carroceria: TipoCarroceriaEnum = Field(default=TipoCarroceriaEnum.FECHADA_BAU)
    proprietario_cnpj_cpf: Optional[str] = Field(None, max_length=14)
    proprietario_nome: Optional[str] = Field(None, max_length=60)
    proprietario_ie: Optional[str] = Field(None, max_length=14)
    proprietario_uf: Optional[str] = Field(None, max_length=2)

    class Config:
        json_schema_extra = {
            "example": {
                "placa": "ABC1234",
                "uf": "AM",
                "tara": "8000",
                "capacidade_kg": "30000",
                "tipo_rodado": "03",
                "tipo_carroceria": "02"
            }
        }


class ReboqueRequest(BaseModel):
    """Dados do reboque/semi-reboque."""
    placa: str = Field(..., min_length=7, max_length=7)
    renavam: Optional[str] = Field(None, max_length=11)
    uf: str = Field(default="", max_length=2)
    tara: Decimal = Field(default=Decimal("0"), ge=0)
    capacidade_kg: Decimal = Field(default=Decimal("0"), ge=0)
    capacidade_m3: Decimal = Field(default=Decimal("0"), ge=0)
    tipo_carroceria: TipoCarroceriaEnum = Field(default=TipoCarroceriaEnum.FECHADA_BAU)

    class Config:
        json_schema_extra = {
            "example": {
                "placa": "XYZ9876",
                "uf": "AM",
                "tara": "5000",
                "capacidade_kg": "25000"
            }
        }


class DocumentoVinculadoRequest(BaseModel):
    """Documento fiscal vinculado ao MDF-e."""
    tipo: str = Field(..., pattern="^(NFe|CTe)$", description="Tipo: NFe ou CTe")
    chave: str = Field(..., min_length=44, max_length=44)
    segundo_codigo_barras: Optional[str] = Field(None, max_length=44)

    class Config:
        json_schema_extra = {
            "example": {
                "tipo": "NFe",
                "chave": "35260100000000000000550010000000011000000011"
            }
        }


class MunicipioRequest(BaseModel):
    """Municipio de carregamento/descarregamento."""
    codigo_ibge: str = Field(..., min_length=7, max_length=7)
    nome: str = Field(..., max_length=60)
    documentos: Optional[List[DocumentoVinculadoRequest]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "codigo_ibge": "1302603",
                "nome": "MANAUS",
                "documentos": []
            }
        }


class PercursoRequest(BaseModel):
    """UF de percurso."""
    uf: str = Field(..., min_length=2, max_length=2)


class CriarMDFeRequest(BaseModel):
    """Request para criar MDF-e."""
    numero: int = Field(..., gt=0)
    serie: int = Field(default=1, ge=1)
    modal: ModalTransporteEnum = Field(default=ModalTransporteEnum.RODOVIARIO)
    tipo_emitente: TipoEmitenteEnum = Field(default=TipoEmitenteEnum.TRANSPORTADORA)
    uf_inicio: str = Field(..., min_length=2, max_length=2)
    uf_fim: str = Field(..., min_length=2, max_length=2)
    percurso: Optional[List[PercursoRequest]] = None
    data_inicio_viagem: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")

    # Municipios
    municipios_carregamento: Optional[List[MunicipioRequest]] = None
    municipios_descarregamento: Optional[List[MunicipioRequest]] = None

    # Totais
    valor_total_carga: Decimal = Field(default=Decimal("0"), ge=0)
    peso_bruto_total: Decimal = Field(default=Decimal("0"), ge=0)

    # Veiculo e condutores
    veiculo_tracao: Optional[VeiculoRequest] = None
    reboques: Optional[List[ReboqueRequest]] = None
    condutores: Optional[List[CondutorRequest]] = None

    # CIOT
    ciot: Optional[str] = Field(None, max_length=12)
    ciot_cnpj_cpf: Optional[str] = Field(None, max_length=14)

    # Seguro
    seguradora_cnpj: Optional[str] = Field(None, max_length=14)
    seguradora_nome: Optional[str] = Field(None, max_length=60)
    numero_apolice: Optional[str] = Field(None, max_length=20)
    numero_averbacao: Optional[str] = Field(None, max_length=40)

    class Config:
        json_schema_extra = {
            "example": {
                "numero": 1,
                "serie": 1,
                "modal": "1",
                "tipo_emitente": "1",
                "uf_inicio": "AM",
                "uf_fim": "SP",
                "valor_total_carga": "50000.00",
                "peso_bruto_total": "15000.0000"
            }
        }


class GerarXMLRequest(BaseModel):
    """Request para gerar XML do MDF-e."""
    mdfe_id: str = Field(..., description="ID do MDF-e")

    class Config:
        json_schema_extra = {
            "example": {
                "mdfe_id": "mdfe_001"
            }
        }


class EncerrarMDFeRequest(BaseModel):
    """Request para encerrar MDF-e."""
    chave: str = Field(..., min_length=44, max_length=44)
    protocolo_autorizacao: str = Field(..., min_length=1)
    data_encerramento: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")
    uf_encerramento: str = Field(..., min_length=2, max_length=2)
    codigo_municipio: str = Field(..., min_length=7, max_length=7)

    class Config:
        json_schema_extra = {
            "example": {
                "chave": "35260100000000000000580010000000011000000011",
                "protocolo_autorizacao": "135260000000001",
                "uf_encerramento": "SP",
                "codigo_municipio": "3550308"
            }
        }


class IncluirCondutorRequest(BaseModel):
    """Request para incluir condutor em MDF-e autorizado."""
    chave: str = Field(..., min_length=44, max_length=44)
    condutor: CondutorRequest

    class Config:
        json_schema_extra = {
            "example": {
                "chave": "35260100000000000000580010000000011000000011",
                "condutor": {
                    "cpf": "12345678901",
                    "nome": "Joao Silva"
                }
            }
        }


# ============== Schemas de Resposta ==============

class CondutorResponse(BaseModel):
    """Condutor cadastrado."""
    cpf: str
    nome: str


class VeiculoResponse(BaseModel):
    """Veiculo cadastrado."""
    placa: str
    uf: str
    tara: str
    capacidade_kg: str
    tipo_rodado: str
    tipo_carroceria: str


class MDFeResponse(BaseModel):
    """MDF-e criado."""
    numero: int
    serie: int
    chave: Optional[str]
    modal: str
    tipo_emitente: str
    uf_inicio: str
    uf_fim: str
    situacao: str
    data_emissao: str
    valor_total_carga: str
    peso_bruto_total: str
    quantidade_cte: int
    quantidade_nfe: int


class XMLResponse(BaseModel):
    """XML gerado."""
    numero: int
    xml: str
    hash_md5: Optional[str] = None


class EncerrarMDFeResponse(BaseModel):
    """Resultado do encerramento."""
    chave: str
    tipo_evento: str
    descricao: str
    status: str
    protocolo: Optional[str]
    data_encerramento: str


class IncluirCondutorResponse(BaseModel):
    """Resultado da inclusao de condutor."""
    chave: str
    tipo_evento: str
    descricao: str
    condutor_cpf: str
    condutor_nome: str
    status: str


class StatusServicoResponse(BaseModel):
    """Status do servico SEFAZ."""
    servico: str
    url: str
    ambiente: str
    status: str
    mensagem: str


class MDFeNaoEncerradoResponse(BaseModel):
    """MDF-e nao encerrado."""
    chave: str
    numero: int
    serie: int
    data_emissao: str
    situacao: str


class ModalResponse(BaseModel):
    """Modal de transporte."""
    codigo: str
    descricao: str


class TipoEmitenteResponse(BaseModel):
    """Tipo de emitente."""
    codigo: str
    descricao: str


class TipoCarroceriaResponse(BaseModel):
    """Tipo de carroceria."""
    codigo: str
    descricao: str


class StatusMDFeResponse(BaseModel):
    """Status do modulo MDF-e."""
    cnpj: str
    razao_social: str
    inscricao_estadual: str
    uf: str
    ambiente: str
    versao_layout: str
    operacoes_disponiveis: List[str]
