"""
DTOs para integracao com Licitacoes-e (Banco do Brasil)
========================================================
Modelos Pydantic para tipagem das respostas do portal
Licitacoes-e, plataforma de licitacoes eletronicas do BB.
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OportunidadeLicitacoesE(BaseModel):
    """Oportunidade de licitacao no portal Licitacoes-e."""

    # Identificacao
    licitacao_id: str | None = None
    numero_licitacao: str | None = None
    numero_processo: str | None = None

    # Orgao / Entidade
    entidade_nome: str = ""
    entidade_cnpj: str | None = None
    uf: str = ""
    municipio: str | None = None

    # Objeto e modalidade
    objeto: str = ""
    modalidade: str | None = None
    tipo: str | None = None  # bens, servicos, obras

    # Valores
    valor_estimado: Decimal | None = None
    valor_lance_minimo: Decimal | None = None

    # Datas
    data_publicacao: datetime | None = None
    data_inicio_disputa: datetime | None = None
    data_fim_disputa: datetime | None = None
    data_abertura_propostas: datetime | None = None
    data_encerramento_propostas: datetime | None = None

    # Links
    url_edital: str | None = None
    url_portal: str | None = None

    # Status
    situacao: str | None = None
    fase_atual: str | None = None
    ativo: bool = True

    # Segmento
    segmento: str | None = None
    segmento_codigo: str | None = None


class FiltrosBuscaLicitacoesE(BaseModel):
    """Parametros de busca no portal Licitacoes-e."""

    uf: str = "AM"
    segmento: str | None = None  # todos, bens, servicos, obras, saude, ti
    data_inicial: date | None = None
    data_final: date | None = None
    texto_objeto: str | None = None
    entidade: str | None = None
    pagina: int = 1
    tamanho_pagina: int = 20


class DetalheLicitacaoLicitacoesE(BaseModel):
    """Detalhes completos de uma licitacao no Licitacoes-e."""

    # Dados basicos
    licitacao_id: str | None = None
    numero_licitacao: str | None = None
    numero_processo: str | None = None
    objeto: str = ""
    modalidade: str | None = None
    tipo: str | None = None

    # Entidade
    entidade_nome: str = ""
    entidade_cnpj: str | None = None
    uf: str = ""
    municipio: str | None = None
    endereco_entidade: str | None = None

    # Valores
    valor_estimado: Decimal | None = None
    valor_lance_minimo: Decimal | None = None
    valor_homologado: Decimal | None = None

    # Datas
    data_publicacao: datetime | None = None
    data_inicio_disputa: datetime | None = None
    data_fim_disputa: datetime | None = None
    data_resultado: datetime | None = None
    data_homologacao: datetime | None = None

    # Itens
    itens: list[dict] = Field(default_factory=list)
    lotes: list[dict] = Field(default_factory=list)
    total_itens: int = 0

    # Documentos e anexos
    documentos: list[dict] = Field(default_factory=list)

    # Status
    situacao: str | None = None
    fase_atual: str | None = None
    resultado: str | None = None

    # Pregoeiro / Comissao
    pregoeiro: str | None = None
    telefone_contato: str | None = None
    email_contato: str | None = None


class ResultadoBuscaLicitacoesE(BaseModel):
    """Resultado de busca no Licitacoes-e."""

    sucesso: bool = True
    total_registros: int = 0
    pagina_atual: int = 1
    oportunidades: list[OportunidadeLicitacoesE] = Field(default_factory=list)
    erro: str | None = None
