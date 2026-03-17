"""
DTOs para integracao com e-Compras AM
======================================
Modelos Pydantic para tipagem das respostas do portal
e-Compras do Estado do Amazonas.
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OportunidadeEComprasAM(BaseModel):
    """Oportunidade de licitacao no portal e-Compras AM."""

    # Identificacao
    edital_id: str | None = None
    numero_edital: str | None = None
    numero_processo: str | None = None

    # Orgao
    orgao_nome: str = ""
    orgao_cnpj: str | None = None
    secretaria: str | None = None
    uf: str = "AM"
    municipio: str = "Manaus"

    # Objeto e modalidade
    objeto: str = ""
    modalidade: str | None = None
    tipo_contratacao: str | None = None

    # Valores
    valor_estimado: Decimal | None = None
    valor_referencia: Decimal | None = None

    # Datas
    data_publicacao: datetime | None = None
    data_abertura: datetime | None = None
    data_encerramento: datetime | None = None
    data_resultado: datetime | None = None

    # Links
    url_edital: str | None = None
    url_portal: str | None = None

    # Status
    situacao: str | None = None
    fase: str | None = None
    ativo: bool = True


class FiltrosBuscaEComprasAM(BaseModel):
    """Parametros de busca no portal e-Compras AM."""

    data_inicial: date | None = None
    data_final: date | None = None
    texto_objeto: str | None = None
    modalidade: str | None = None
    secretaria: str | None = None
    orgao: str | None = None
    pagina: int = 1
    tamanho_pagina: int = 20


class DetalheLicitacaoEComprasAM(BaseModel):
    """Detalhes completos de uma licitacao no e-Compras AM."""

    # Dados basicos
    edital_id: str | None = None
    numero_edital: str | None = None
    numero_processo: str | None = None
    objeto: str = ""
    modalidade: str | None = None

    # Orgao
    orgao_nome: str = ""
    orgao_cnpj: str | None = None
    secretaria: str | None = None
    uf: str = "AM"
    municipio: str = "Manaus"

    # Valores
    valor_estimado: Decimal | None = None
    valor_referencia: Decimal | None = None
    valor_homologado: Decimal | None = None

    # Datas
    data_publicacao: datetime | None = None
    data_abertura: datetime | None = None
    data_encerramento: datetime | None = None
    data_homologacao: datetime | None = None

    # Itens
    itens: list[dict] = Field(default_factory=list)
    total_itens: int = 0

    # Documentos e anexos
    documentos: list[dict] = Field(default_factory=list)

    # Status
    situacao: str | None = None
    resultado: str | None = None

    # Comissao de licitacao
    comissao: str | None = None
    pregoeiro: str | None = None


class ResultadoBuscaEComprasAM(BaseModel):
    """Resultado de busca no e-Compras AM."""

    sucesso: bool = True
    total_registros: int = 0
    pagina_atual: int = 1
    oportunidades: list[OportunidadeEComprasAM] = Field(default_factory=list)
    erro: str | None = None
