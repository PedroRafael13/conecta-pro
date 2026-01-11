"""
DTOs para integracao com PNCP
=============================
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


class PNCPOrgao(BaseModel):
    """Orgao/Entidade do PNCP."""
    cnpj: str
    razao_social: str
    nome_unidade: Optional[str] = None
    uf: str = "AM"
    municipio: Optional[str] = None
    codigo_ibge: Optional[str] = None
    esfera: Optional[str] = None  # federal, estadual, municipal


class PNCPItem(BaseModel):
    """Item de compra do PNCP."""
    numero_item: int
    descricao: str
    quantidade: Decimal
    unidade_medida: str
    valor_unitario_estimado: Optional[Decimal] = None
    valor_total_estimado: Optional[Decimal] = None
    situacao: Optional[str] = None
    codigo_material_servico: Optional[str] = None
    tipo_beneficio: Optional[str] = None  # ME/EPP, ampla, etc


class PNCPDocumento(BaseModel):
    """Documento/Anexo do PNCP."""
    titulo: str
    tipo: str  # edital, anexo, ata, etc
    url: str
    data_publicacao: Optional[datetime] = None
    tamanho_bytes: Optional[int] = None
    hash_arquivo: Optional[str] = None


class PNCPCompra(BaseModel):
    """Compra do PNCP."""
    # Identificacao
    numero_compra: str
    ano_compra: int
    sequencial_compra: int
    numero_controle_pncp: Optional[str] = None

    # Orgao
    orgao: PNCPOrgao

    # Modalidade e tipo
    modalidade_id: Optional[int] = None
    modalidade_nome: Optional[str] = None
    modo_disputa_id: Optional[int] = None
    modo_disputa_nome: Optional[str] = None
    tipo_contratacao: Optional[str] = None
    tipo_instrumento_convocatorio: Optional[str] = None

    # Objeto
    objeto: str
    objeto_resumido: Optional[str] = None
    informacao_complementar: Optional[str] = None

    # Valores
    valor_estimado_total: Optional[Decimal] = None
    valor_homologado_total: Optional[Decimal] = None

    # Datas
    data_publicacao_pncp: Optional[datetime] = None
    data_abertura_proposta: Optional[datetime] = None
    data_encerramento_proposta: Optional[datetime] = None
    data_resultado: Optional[datetime] = None

    # Status
    situacao_compra_id: Optional[int] = None
    situacao_compra_nome: Optional[str] = None

    # Links
    link_sistema_origem: Optional[str] = None
    link_pncp: Optional[str] = None

    # Itens e documentos
    itens: List[PNCPItem] = Field(default_factory=list)
    documentos: List[PNCPDocumento] = Field(default_factory=list)

    # Informacoes adicionais
    srp: bool = False  # Sistema de Registro de Precos
    processo_administrativo: Optional[str] = None
    justificativa: Optional[str] = None


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
    valor_global: Optional[Decimal] = None

    # Vigencia
    data_assinatura: Optional[date] = None
    data_publicacao: Optional[date] = None
    data_vigencia_inicio: Optional[date] = None
    data_vigencia_fim: Optional[date] = None

    # Objeto
    objeto: str

    # Links
    link_pncp: Optional[str] = None


class PNCPResponse(BaseModel):
    """Resposta padrao da API PNCP."""
    sucesso: bool = True
    total_registros: int = 0
    pagina_atual: int = 1
    total_paginas: int = 1
    compras: List[PNCPCompra] = Field(default_factory=list)
    erro: Optional[str] = None


class PNCPSearchParams(BaseModel):
    """Parametros de busca no PNCP."""
    uf: str = "AM"
    data_inicial: Optional[date] = None
    data_final: Optional[date] = None
    modalidade: Optional[str] = None
    situacao: Optional[str] = None
    cnpj_orgao: Optional[str] = None
    objeto: Optional[str] = None
    valor_minimo: Optional[Decimal] = None
    valor_maximo: Optional[Decimal] = None
    pagina: int = 1
    tamanho_pagina: int = 20
