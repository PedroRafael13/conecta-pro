"""Schemas Pydantic para o módulo de Empresas (Multi-CNPJ)."""

from datetime import date
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from modules.empresas.models.empresa import (
    AnexoSimplesEnum,
    EmpresaStatusEnum,
    LiminarStatusEnum,
    LiminarTipoEnum,
    RegimeTributarioEnum,
)


# ===================================================================
# LIMINAR SCHEMAS
# ===================================================================


class LiminarCreate(BaseModel):
    tipo: LiminarTipoEnum
    descricao: str
    numero_processo: Optional[str] = None
    vara: Optional[str] = None
    tribunal: Optional[str] = None
    advogado: Optional[str] = None
    data_solicitacao: Optional[date] = None
    data_concessao: Optional[date] = None
    data_validade: Optional[date] = None
    status: Optional[LiminarStatusEnum] = LiminarStatusEnum.A_SOLICITAR
    efeitos: Optional[Dict[str, Any]] = None
    fundamento_legal: Optional[str] = None
    observacoes: Optional[str] = None


class LiminarUpdate(BaseModel):
    tipo: Optional[LiminarTipoEnum] = None
    descricao: Optional[str] = None
    numero_processo: Optional[str] = None
    vara: Optional[str] = None
    tribunal: Optional[str] = None
    advogado: Optional[str] = None
    data_solicitacao: Optional[date] = None
    data_concessao: Optional[date] = None
    data_validade: Optional[date] = None
    status: Optional[LiminarStatusEnum] = None
    efeitos: Optional[Dict[str, Any]] = None
    fundamento_legal: Optional[str] = None
    observacoes: Optional[str] = None


class LiminarResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    tipo: str
    descricao: str
    numero_processo: Optional[str] = None
    vara: Optional[str] = None
    tribunal: Optional[str] = None
    advogado: Optional[str] = None
    data_solicitacao: Optional[date] = None
    data_concessao: Optional[date] = None
    data_validade: Optional[date] = None
    status: str
    efeitos: Optional[Dict[str, Any]] = None
    fundamento_legal: Optional[str] = None
    observacoes: Optional[str] = None
    created_at: Optional[date] = None
    updated_at: Optional[date] = None


# ===================================================================
# EMPRESA SCHEMAS
# ===================================================================


class EmpresaCreate(BaseModel):
    slug: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    cnpj: Optional[str] = None
    inscricao_municipal: Optional[str] = None
    inscricao_estadual: Optional[str] = None
    inscricao_suframa: Optional[str] = None
    codigo_municipio_ibge: Optional[str] = "1302603"
    regime_tributario: RegimeTributarioEnum
    anexo_simples: Optional[AnexoSimplesEnum] = None
    data_opcao_simples: Optional[date] = None
    data_desenquadramento_simples: Optional[date] = None
    regime_futuro: Optional[RegimeTributarioEnum] = None
    data_prevista_mudanca_regime: Optional[date] = None
    certificado_a1_path: Optional[str] = None
    certificado_a1_senha: Optional[str] = None
    certificado_validade: Optional[date] = None
    contador_software: Optional[str] = None
    contador_email: Optional[str] = None
    contador_nome: Optional[str] = None
    tipos_servicos: Optional[List[str]] = None
    nfse_ambiente: Optional[str] = "homologacao"
    nfse_serie_rps: Optional[str] = "1"
    nfse_numero_inicial: Optional[str] = "1"
    status: Optional[EmpresaStatusEnum] = EmpresaStatusEnum.ATIVA
    is_principal: Optional[bool] = False
    observacoes: Optional[str] = None


class EmpresaUpdate(BaseModel):
    slug: Optional[str] = None
    razao_social: Optional[str] = None
    nome_fantasia: Optional[str] = None
    cnpj: Optional[str] = None
    inscricao_municipal: Optional[str] = None
    inscricao_estadual: Optional[str] = None
    inscricao_suframa: Optional[str] = None
    codigo_municipio_ibge: Optional[str] = None
    regime_tributario: Optional[RegimeTributarioEnum] = None
    anexo_simples: Optional[AnexoSimplesEnum] = None
    data_opcao_simples: Optional[date] = None
    data_desenquadramento_simples: Optional[date] = None
    regime_futuro: Optional[RegimeTributarioEnum] = None
    data_prevista_mudanca_regime: Optional[date] = None
    certificado_a1_path: Optional[str] = None
    certificado_a1_senha: Optional[str] = None
    certificado_validade: Optional[date] = None
    contador_software: Optional[str] = None
    contador_email: Optional[str] = None
    contador_nome: Optional[str] = None
    tipos_servicos: Optional[List[str]] = None
    nfse_ambiente: Optional[str] = None
    nfse_serie_rps: Optional[str] = None
    nfse_numero_inicial: Optional[str] = None
    status: Optional[EmpresaStatusEnum] = None
    is_principal: Optional[bool] = None
    observacoes: Optional[str] = None


class EmpresaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    slug: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    cnpj: Optional[str] = None
    inscricao_municipal: Optional[str] = None
    inscricao_estadual: Optional[str] = None
    inscricao_suframa: Optional[str] = None
    codigo_municipio_ibge: Optional[str] = None
    regime_tributario: str
    anexo_simples: Optional[str] = None
    data_opcao_simples: Optional[date] = None
    data_desenquadramento_simples: Optional[date] = None
    regime_futuro: Optional[str] = None
    data_prevista_mudanca_regime: Optional[date] = None
    certificado_a1_path: Optional[str] = None
    certificado_validade: Optional[date] = None
    contador_software: Optional[str] = None
    contador_email: Optional[str] = None
    contador_nome: Optional[str] = None
    tipos_servicos: Optional[List[str]] = None
    nfse_ambiente: Optional[str] = None
    nfse_serie_rps: Optional[str] = None
    nfse_numero_inicial: Optional[str] = None
    status: str
    is_principal: bool
    observacoes: Optional[str] = None
    created_at: Optional[date] = None
    updated_at: Optional[date] = None
    liminares: List[LiminarResponse] = []


class EmpresaListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    razao_social: str
    cnpj: Optional[str] = None
    regime_tributario: str
    status: str
    is_principal: bool


# ===================================================================
# AI / SIMULAÇÃO SCHEMAS
# ===================================================================


class SugestaoEmpresaFaturamento(BaseModel):
    empresa_id: UUID
    slug: str
    razao_social: str
    motivo: str
    carga_tributaria_estimada: float
    economia_potencial: float


class SimulacaoRegime(BaseModel):
    empresa_id: UUID
    regime_atual: str
    regime_simulado: str
    faturamento_anual: float
    impostos_regime_atual: float
    impostos_regime_simulado: float
    economia_anual: float
    recomendacao: str
