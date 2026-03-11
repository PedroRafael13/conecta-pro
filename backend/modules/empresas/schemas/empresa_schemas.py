"""Schemas Pydantic para o módulo de Empresas (Multi-CNPJ)."""

from datetime import date
from typing import Any
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
    numero_processo: str | None = None
    vara: str | None = None
    tribunal: str | None = None
    advogado: str | None = None
    data_solicitacao: date | None = None
    data_concessao: date | None = None
    data_validade: date | None = None
    status: LiminarStatusEnum | None = LiminarStatusEnum.A_SOLICITAR
    efeitos: dict[str, Any] | None = None
    fundamento_legal: str | None = None
    observacoes: str | None = None


class LiminarUpdate(BaseModel):
    tipo: LiminarTipoEnum | None = None
    descricao: str | None = None
    numero_processo: str | None = None
    vara: str | None = None
    tribunal: str | None = None
    advogado: str | None = None
    data_solicitacao: date | None = None
    data_concessao: date | None = None
    data_validade: date | None = None
    status: LiminarStatusEnum | None = None
    efeitos: dict[str, Any] | None = None
    fundamento_legal: str | None = None
    observacoes: str | None = None


class LiminarResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    tipo: str
    descricao: str
    numero_processo: str | None = None
    vara: str | None = None
    tribunal: str | None = None
    advogado: str | None = None
    data_solicitacao: date | None = None
    data_concessao: date | None = None
    data_validade: date | None = None
    status: str
    efeitos: dict[str, Any] | None = None
    fundamento_legal: str | None = None
    observacoes: str | None = None
    created_at: date | None = None
    updated_at: date | None = None


# ===================================================================
# EMPRESA SCHEMAS
# ===================================================================


class EmpresaCreate(BaseModel):
    slug: str
    razao_social: str
    nome_fantasia: str | None = None
    cnpj: str | None = None
    inscricao_municipal: str | None = None
    inscricao_estadual: str | None = None
    inscricao_suframa: str | None = None
    codigo_municipio_ibge: str | None = "1302603"
    regime_tributario: RegimeTributarioEnum
    anexo_simples: AnexoSimplesEnum | None = None
    data_opcao_simples: date | None = None
    data_desenquadramento_simples: date | None = None
    regime_futuro: RegimeTributarioEnum | None = None
    data_prevista_mudanca_regime: date | None = None
    certificado_a1_path: str | None = None
    certificado_a1_senha: str | None = None
    certificado_validade: date | None = None
    contador_software: str | None = None
    contador_email: str | None = None
    contador_nome: str | None = None
    tipos_servicos: list[str] | None = None
    nfse_ambiente: str | None = "homologacao"
    nfse_serie_rps: str | None = "1"
    nfse_numero_inicial: str | None = "1"
    status: EmpresaStatusEnum | None = EmpresaStatusEnum.ATIVA
    is_principal: bool | None = False
    observacoes: str | None = None


class EmpresaUpdate(BaseModel):
    slug: str | None = None
    razao_social: str | None = None
    nome_fantasia: str | None = None
    cnpj: str | None = None
    inscricao_municipal: str | None = None
    inscricao_estadual: str | None = None
    inscricao_suframa: str | None = None
    codigo_municipio_ibge: str | None = None
    regime_tributario: RegimeTributarioEnum | None = None
    anexo_simples: AnexoSimplesEnum | None = None
    data_opcao_simples: date | None = None
    data_desenquadramento_simples: date | None = None
    regime_futuro: RegimeTributarioEnum | None = None
    data_prevista_mudanca_regime: date | None = None
    certificado_a1_path: str | None = None
    certificado_a1_senha: str | None = None
    certificado_validade: date | None = None
    contador_software: str | None = None
    contador_email: str | None = None
    contador_nome: str | None = None
    tipos_servicos: list[str] | None = None
    nfse_ambiente: str | None = None
    nfse_serie_rps: str | None = None
    nfse_numero_inicial: str | None = None
    status: EmpresaStatusEnum | None = None
    is_principal: bool | None = None
    observacoes: str | None = None


class EmpresaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    slug: str
    razao_social: str
    nome_fantasia: str | None = None
    cnpj: str | None = None
    inscricao_municipal: str | None = None
    inscricao_estadual: str | None = None
    inscricao_suframa: str | None = None
    codigo_municipio_ibge: str | None = None
    regime_tributario: str
    anexo_simples: str | None = None
    data_opcao_simples: date | None = None
    data_desenquadramento_simples: date | None = None
    regime_futuro: str | None = None
    data_prevista_mudanca_regime: date | None = None
    certificado_a1_path: str | None = None
    certificado_validade: date | None = None
    contador_software: str | None = None
    contador_email: str | None = None
    contador_nome: str | None = None
    tipos_servicos: list[str] | None = None
    nfse_ambiente: str | None = None
    nfse_serie_rps: str | None = None
    nfse_numero_inicial: str | None = None
    status: str
    is_principal: bool
    observacoes: str | None = None
    created_at: date | None = None
    updated_at: date | None = None
    liminares: list[LiminarResponse] = []


class EmpresaListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    razao_social: str
    cnpj: str | None = None
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
