"""
Schemas para FGTS Digital.

Pydantic models para validação de entrada/saída da API.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class TipoRecolhimentoEnum(str, Enum):
    """Tipo de recolhimento FGTS."""
    MENSAL = "1"
    RESCISORIO = "2"
    RECURSAL = "3"
    INFORME_COMPETENCIA = "4"


class ModalidadeSaqueEnum(str, Enum):
    """Modalidade de saque FGTS."""
    RESCISAO = "01"
    APOSENTADORIA = "04"
    FALECIMENTO = "23"
    SAQUE_ANIVERSARIO = "98"
    CALAMIDADE = "99"


class SituacaoGuiaEnum(str, Enum):
    """Situação da guia FGTS."""
    GERADA = "gerada"
    PAGA = "paga"
    VENCIDA = "vencida"
    CANCELADA = "cancelada"


class CategoriaTrabalhadoEnum(str, Enum):
    """Categoria do trabalhador."""
    EMPREGADO_GERAL = "101"
    DOMESTICO = "104"
    APRENDIZ = "103"
    TEMPORARIO = "106"
    DIRETOR_FGTS = "721"


# ============== Schemas de Entrada ==============

class TrabalhadorRequest(BaseModel):
    """Dados do trabalhador."""
    cpf: str = Field(
        ...,
        min_length=11,
        max_length=14,
        description="CPF do trabalhador"
    )
    nome: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nome do trabalhador"
    )
    pis_pasep: str = Field(
        ...,
        min_length=11,
        max_length=11,
        description="Número PIS/PASEP"
    )
    data_admissao: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Data de admissão (YYYY-MM-DD)"
    )
    categoria: CategoriaTrabalhadoEnum = Field(
        default=CategoriaTrabalhadoEnum.EMPREGADO_GERAL,
        description="Categoria do trabalhador"
    )
    remuneracao: Decimal = Field(
        ...,
        gt=0,
        description="Remuneração do mês"
    )
    base_fgts: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Base de cálculo FGTS (se diferente da remuneração)"
    )
    valor_13_salario: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Valor do 13º salário"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "cpf": "12345678901",
                "nome": "João da Silva",
                "pis_pasep": "12345678901",
                "data_admissao": "2020-01-15",
                "categoria": "101",
                "remuneracao": "5000.00"
            }
        }


class CalcularFolhaRequest(BaseModel):
    """Request para calcular FGTS da folha."""
    competencia: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}$",
        description="Competência (YYYY-MM)"
    )
    trabalhadores: List[TrabalhadorRequest] = Field(
        ...,
        min_length=1,
        description="Lista de trabalhadores"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "competencia": "2026-01",
                "trabalhadores": [
                    {
                        "cpf": "12345678901",
                        "nome": "João da Silva",
                        "pis_pasep": "12345678901",
                        "data_admissao": "2020-01-15",
                        "remuneracao": "5000.00"
                    }
                ]
            }
        }


class ImportarESocialRequest(BaseModel):
    """Request para importar dados do eSocial."""
    competencia: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}$",
        description="Competência (YYYY-MM)"
    )
    eventos_s1200: List[Dict[str, Any]] = Field(
        ...,
        min_length=1,
        description="Eventos S-1200 do eSocial"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "competencia": "2026-01",
                "eventos_s1200": [
                    {
                        "cpf": "12345678901",
                        "nome": "João da Silva",
                        "pis_pasep": "12345678901",
                        "data_admissao": "2020-01-15",
                        "categoria": "101",
                        "remuneracao_total": "5000.00",
                        "base_fgts": "5000.00"
                    }
                ]
            }
        }


class GerarGuiaMensalRequest(BaseModel):
    """Request para gerar guia mensal."""
    competencia: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}$",
        description="Competência (YYYY-MM)"
    )
    trabalhadores: List[TrabalhadorRequest] = Field(
        ...,
        min_length=1,
        description="Lista de trabalhadores"
    )
    data_vencimento: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Data de vencimento (YYYY-MM-DD)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "competencia": "2026-01",
                "trabalhadores": [
                    {
                        "cpf": "12345678901",
                        "nome": "João da Silva",
                        "pis_pasep": "12345678901",
                        "data_admissao": "2020-01-15",
                        "remuneracao": "5000.00"
                    }
                ],
                "data_vencimento": "2026-02-20"
            }
        }


class RescisaoRequest(BaseModel):
    """Request para rescisão."""
    cpf: str = Field(
        ...,
        min_length=11,
        max_length=14,
        description="CPF do trabalhador"
    )
    nome: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nome do trabalhador"
    )
    pis_pasep: str = Field(
        ...,
        min_length=11,
        max_length=11,
        description="Número PIS/PASEP"
    )
    data_admissao: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Data de admissão"
    )
    data_desligamento: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Data de desligamento"
    )
    motivo_desligamento: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Motivo do desligamento"
    )
    aviso_previo: str = Field(
        ...,
        pattern=r"^(trabalhado|indenizado|ausencia)$",
        description="Tipo de aviso prévio"
    )
    remuneracao: Decimal = Field(
        ...,
        gt=0,
        description="Remuneração"
    )
    saldo_fgts: Decimal = Field(
        ...,
        ge=0,
        description="Saldo FGTS acumulado"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "cpf": "12345678901",
                "nome": "João da Silva",
                "pis_pasep": "12345678901",
                "data_admissao": "2020-01-15",
                "data_desligamento": "2026-01-31",
                "motivo_desligamento": "Pedido de demissão",
                "aviso_previo": "trabalhado",
                "remuneracao": "5000.00",
                "saldo_fgts": "15000.00"
            }
        }


class ConsultarDebitosRequest(BaseModel):
    """Request para consultar débitos."""
    competencia_inicio: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}$",
        description="Competência inicial"
    )
    competencia_fim: Optional[str] = Field(
        None,
        pattern=r"^\d{4}-\d{2}$",
        description="Competência final"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "competencia_inicio": "2025-01",
                "competencia_fim": "2025-12"
            }
        }


class ConsultarExtratoRequest(BaseModel):
    """Request para consultar extrato."""
    cpf: str = Field(
        ...,
        min_length=11,
        max_length=14,
        description="CPF do trabalhador"
    )
    pis_pasep: str = Field(
        ...,
        min_length=11,
        max_length=11,
        description="Número PIS/PASEP"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "cpf": "12345678901",
                "pis_pasep": "12345678901"
            }
        }


class SimularSaqueRequest(BaseModel):
    """Request para simular saque."""
    cpf: str = Field(
        ...,
        min_length=11,
        max_length=14,
        description="CPF do trabalhador"
    )
    modalidade: ModalidadeSaqueEnum = Field(
        ...,
        description="Modalidade de saque"
    )
    valor_solicitado: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Valor solicitado"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "cpf": "12345678901",
                "modalidade": "01",
                "valor_solicitado": "5000.00"
            }
        }


# ============== Schemas de Resposta ==============

class TrabalhadorFGTSResponse(BaseModel):
    """Trabalhador com FGTS calculado."""
    cpf: str
    nome: str
    pis_pasep: str
    categoria: str
    remuneracao: str
    fgts_mensal: str
    fgts_13: str
    fgts_total: str


class CalculoFolhaResponse(BaseModel):
    """Response do cálculo da folha."""
    competencia: str
    quantidade_trabalhadores: int
    total_remuneracao: str
    total_fgts: str
    trabalhadores: List[Dict[str, str]]


class GRFGTSResponse(BaseModel):
    """Response da guia GRFGTS."""
    numero: str
    competencia: str
    data_geracao: str
    data_vencimento: str
    valor_principal: str
    valor_atualizacao: str
    valor_multa: str
    valor_juros: str
    valor_total: str
    chave_pix: Optional[str] = None
    codigo_pix: Optional[str] = None
    qrcode_pix: Optional[str] = None
    situacao: str


class GuiaRescisoriaResponse(BaseModel):
    """Response da guia rescisória."""
    numero: str
    cpf_trabalhador: str
    nome_trabalhador: str
    data_desligamento: str
    valor_deposito_mes: str
    valor_deposito_aviso: str
    valor_deposito_13: str
    valor_multa_rescisoria: str
    valor_total: str
    codigo_pix: Optional[str] = None
    qrcode_pix: Optional[str] = None
    data_vencimento: Optional[str] = None
    situacao: str


class DebitoFGTSResponse(BaseModel):
    """Débito de FGTS."""
    competencia: str
    tipo: str
    valor_principal: str
    valor_atualizacao: str
    valor_multa: str
    valor_juros: str
    valor_total: str
    data_vencimento: Optional[str] = None


class ExtratoFGTSResponse(BaseModel):
    """Extrato do FGTS."""
    cpf: str
    pis_pasep: str
    saldo_total: str
    mensagem: str


class SimulacaoSaqueResponse(BaseModel):
    """Response da simulação de saque."""
    cpf: str
    modalidade: str
    valor_solicitado: Optional[str] = None
    status: str
    mensagem: str


class RelatorioMensalResponse(BaseModel):
    """Relatório mensal de FGTS."""
    cnpj: str
    razao_social: str
    competencia: str
    data_geracao: str
    resumo: Dict[str, Any]
    detalhamento: List[TrabalhadorFGTSResponse]


class CategoriaResponse(BaseModel):
    """Categoria de trabalhador."""
    codigo: str
    descricao: str


class CategoriasResponse(BaseModel):
    """Lista de categorias."""
    categorias: List[CategoriaResponse]


class ModalidadeSaqueResponse(BaseModel):
    """Modalidade de saque."""
    codigo: str
    descricao: str


class ModalidadesSaqueResponse(BaseModel):
    """Lista de modalidades de saque."""
    modalidades: List[ModalidadeSaqueResponse]


class StatusFGTSResponse(BaseModel):
    """Status do FGTS Digital."""
    cnpj: str
    razao_social: str
    ambiente: str
    portal_url: str
    aliquota_fgts: str
    aliquota_multa: str
    operacoes_disponiveis: List[str]
