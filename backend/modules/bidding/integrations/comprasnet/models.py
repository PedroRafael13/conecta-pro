"""
DTOs para integracao com ComprasNet / Compras.gov.br
=====================================================
Modelos Pydantic para tipagem das respostas do portal
ComprasNet (Compras.gov.br) do Governo Federal.
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OportunidadeComprasNet(BaseModel):
    """Oportunidade de licitacao no portal ComprasNet."""

    # Identificacao
    numero_pregao: str | None = None
    codigo_uasg: str | None = None
    numero_processo: str | None = None

    # Orgao / UASG
    orgao_nome: str = ""
    nome_uasg: str | None = None
    orgao_cnpj: str | None = None
    uf: str = ""
    municipio: str | None = None

    # Objeto e modalidade
    objeto: str = ""
    modalidade: str = "Pregao Eletronico"
    tipo_licitacao: str | None = None
    criterio_julgamento: str | None = None

    # Valores
    valor_estimado: Decimal | None = None
    valor_homologado: Decimal | None = None

    # Datas
    data_publicacao: datetime | None = None
    data_abertura: datetime | None = None
    data_encerramento: datetime | None = None
    data_resultado: datetime | None = None

    # Links e referencias
    url_edital: str | None = None
    url_ata: str | None = None
    link_sistema_origem: str | None = None

    # Status
    situacao: str | None = None
    fase_atual: str | None = None
    srp: bool = False  # Sistema de Registro de Precos


class FiltrosBuscaComprasNet(BaseModel):
    """Parametros de busca no portal ComprasNet."""

    uf: str = "AM"
    codigo_uasg: str | None = None
    data_inicial: date | None = None
    data_final: date | None = None
    texto_objeto: str | None = None
    modalidade: str | None = None
    situacao: str | None = None
    pagina: int = 1
    tamanho_pagina: int = 20


class DetalheLicitacaoComprasNet(BaseModel):
    """Detalhes completos de uma licitacao no ComprasNet."""

    # Dados basicos
    numero_pregao: str | None = None
    codigo_uasg: str | None = None
    numero_processo: str | None = None
    objeto: str = ""
    modalidade: str = "Pregao Eletronico"

    # Orgao
    orgao_nome: str = ""
    nome_uasg: str | None = None
    orgao_cnpj: str | None = None
    uf: str = ""
    municipio: str | None = None

    # Valores
    valor_estimado: Decimal | None = None
    valor_homologado: Decimal | None = None

    # Datas
    data_publicacao: datetime | None = None
    data_abertura: datetime | None = None
    data_encerramento: datetime | None = None
    data_sessao: datetime | None = None
    data_homologacao: datetime | None = None

    # Itens
    itens: list[dict] = Field(default_factory=list)
    total_itens: int = 0

    # Documentos e ata
    documentos: list[dict] = Field(default_factory=list)
    ata_sessao: str | None = None

    # Status
    situacao: str | None = None
    fase_atual: str | None = None
    resultado: str | None = None

    # Sistema de Registro de Precos
    srp: bool = False
    ata_registro_precos: str | None = None


class ResultadoBuscaComprasNet(BaseModel):
    """Resultado de busca no ComprasNet."""

    sucesso: bool = True
    total_registros: int = 0
    pagina_atual: int = 1
    oportunidades: list[OportunidadeComprasNet] = Field(default_factory=list)
    erro: str | None = None
