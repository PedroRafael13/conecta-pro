"""
DTOs para integracao com PNCP
=============================
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class PNCPOrgao(BaseModel):
    """Orgao/Entidade do PNCP."""

    cnpj: str
    razao_social: str
    nome_unidade: str | None = None
    uf: str = "AM"
    municipio: str | None = None
    codigo_ibge: str | None = None
    esfera: str | None = None  # federal, estadual, municipal


class PNCPItem(BaseModel):
    """Item de compra do PNCP."""

    numero_item: int
    descricao: str
    quantidade: Decimal
    unidade_medida: str
    valor_unitario_estimado: Decimal | None = None
    valor_total_estimado: Decimal | None = None
    situacao: str | None = None
    codigo_material_servico: str | None = None
    tipo_beneficio: str | None = None  # ME/EPP, ampla, etc


class PNCPDocumento(BaseModel):
    """Documento/Anexo do PNCP."""

    titulo: str
    tipo: str  # edital, anexo, ata, etc
    url: str
    data_publicacao: datetime | None = None
    tamanho_bytes: int | None = None
    hash_arquivo: str | None = None


class PNCPCompra(BaseModel):
    """Compra do PNCP."""

    # Identificacao
    numero_compra: str
    ano_compra: int
    sequencial_compra: int
    numero_controle_pncp: str | None = None

    # Orgao
    orgao: PNCPOrgao

    # Modalidade e tipo
    modalidade_id: int | None = None
    modalidade_nome: str | None = None
    modo_disputa_id: int | None = None
    modo_disputa_nome: str | None = None
    tipo_contratacao: str | None = None
    tipo_instrumento_convocatorio: str | None = None

    # Objeto
    objeto: str
    objeto_resumido: str | None = None
    informacao_complementar: str | None = None

    # Valores
    valor_estimado_total: Decimal | None = None
    valor_homologado_total: Decimal | None = None

    # Datas
    data_publicacao_pncp: datetime | None = None
    data_abertura_proposta: datetime | None = None
    data_encerramento_proposta: datetime | None = None
    data_resultado: datetime | None = None

    # Status
    situacao_compra_id: int | None = None
    situacao_compra_nome: str | None = None

    # Links
    link_sistema_origem: str | None = None
    link_pncp: str | None = None

    # Itens e documentos
    itens: list[PNCPItem] = Field(default_factory=list)
    documentos: list[PNCPDocumento] = Field(default_factory=list)

    # Informacoes adicionais
    srp: bool = False  # Sistema de Registro de Precos
    processo_administrativo: str | None = None
    justificativa: str | None = None


class PNCPContrato(BaseModel):
    """Contrato do PNCP."""

    numero_contrato: str
    ano_contrato: int
    sequencial_contrato: int

    # Orgao
    cnpj_orgao: str
    nome_orgao: str

    # Fornecedor
    cnpj_fornecedor: str
    nome_fornecedor: str

    # Valores
    valor_inicial: Decimal
    valor_global: Decimal | None = None

    # Vigencia
    data_assinatura: date | None = None
    data_publicacao: date | None = None
    data_vigencia_inicio: date | None = None
    data_vigencia_fim: date | None = None

    # Objeto
    objeto: str

    # Links
    link_pncp: str | None = None


class PNCPResponse(BaseModel):
    """Resposta padrao da API PNCP."""

    sucesso: bool = True
    total_registros: int = 0
    pagina_atual: int = 1
    total_paginas: int = 1
    compras: list[PNCPCompra] = Field(default_factory=list)
    erro: str | None = None


class PNCPSearchParams(BaseModel):
    """Parametros de busca no PNCP."""

    uf: str = "AM"
    data_inicial: date | None = None
    data_final: date | None = None
    modalidade: str | None = None
    situacao: str | None = None
    cnpj_orgao: str | None = None
    objeto: str | None = None
    valor_minimo: Decimal | None = None
    valor_maximo: Decimal | None = None
    pagina: int = 1
    tamanho_pagina: int = 20
