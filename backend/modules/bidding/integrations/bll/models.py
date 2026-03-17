"""
DTOs para integracao com BLL Compras
=====================================
Modelos Pydantic para tipagem das respostas do portal BLL Compras.
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OportunidadeBLL(BaseModel):
    """Oportunidade de licitacao no portal BLL Compras."""

    # Identificacao
    licitacao_id: str
    numero_processo: str | None = None
    numero_edital: str | None = None

    # Orgao
    orgao_nome: str = ""
    orgao_cnpj: str | None = None
    uf: str = ""
    municipio: str | None = None

    # Objeto e modalidade
    objeto: str = ""
    modalidade: str | None = None
    tipo_contratacao: str | None = None

    # Valores
    valor_estimado: Decimal | None = None
    valor_homologado: Decimal | None = None

    # Datas
    data_publicacao: datetime | None = None
    data_abertura: datetime | None = None
    data_encerramento: datetime | None = None
    data_resultado: datetime | None = None

    # Links
    url_edital: str | None = None
    url_processo: str | None = None

    # Status
    situacao: str | None = None
    ativo: bool = True


class FiltrosBuscaBLL(BaseModel):
    """Parametros de busca no portal BLL Compras."""

    uf: str = "AM"
    modalidade: str | None = None
    data_inicial: date | None = None
    data_final: date | None = None
    texto_objeto: str | None = None
    orgao: str | None = None
    pagina: int = 1
    tamanho_pagina: int = 20


class DetalheLicitacaoBLL(BaseModel):
    """Detalhes completos de uma licitacao no BLL Compras."""

    # Dados basicos
    licitacao_id: str
    numero_processo: str | None = None
    numero_edital: str | None = None
    objeto: str = ""
    modalidade: str | None = None

    # Orgao
    orgao_nome: str = ""
    orgao_cnpj: str | None = None
    orgao_endereco: str | None = None
    uf: str = ""
    municipio: str | None = None

    # Valores
    valor_estimado: Decimal | None = None
    valor_homologado: Decimal | None = None

    # Datas
    data_publicacao: datetime | None = None
    data_abertura: datetime | None = None
    data_encerramento: datetime | None = None

    # Documentos e anexos
    documentos: list[dict] = Field(default_factory=list)
    itens: list[dict] = Field(default_factory=list)

    # Links
    url_edital: str | None = None
    url_ata: str | None = None

    # Status
    situacao: str | None = None
    resultado: str | None = None


class ResultadoBuscaBLL(BaseModel):
    """Resultado de busca no BLL Compras."""

    sucesso: bool = True
    total_registros: int = 0
    pagina_atual: int = 1
    oportunidades: list[OportunidadeBLL] = Field(default_factory=list)
    erro: str | None = None
