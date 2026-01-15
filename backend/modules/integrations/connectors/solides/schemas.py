"""
Schemas Pydantic para API Sólides
Sprint 33: Integration Framework

Baseado na documentação: https://developers.solides.com.br/
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict


# ==================== COLABORADORES ====================

class SolidesEndereco(BaseModel):
    """Endereço no Sólides."""
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    pais: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class SolidesDepartamento(BaseModel):
    """Departamento no Sólides."""
    id: Optional[int] = None
    nome: str
    codigo: Optional[str] = None
    departamento_pai_id: Optional[int] = None
    gestor_id: Optional[int] = None
    ativo: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")


class SolidesCargo(BaseModel):
    """Cargo no Sólides."""
    id: Optional[int] = None
    nome: str
    codigo: Optional[str] = None
    descricao: Optional[str] = None
    departamento_id: Optional[int] = None
    nivel: Optional[str] = None  # junior, pleno, senior, etc.
    faixa_salarial_min: Optional[Decimal] = None
    faixa_salarial_max: Optional[Decimal] = None
    ativo: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")


class SolidesColaborador(BaseModel):
    """Colaborador no Sólides."""
    id: Optional[int] = None
    nome: str
    email: Optional[str] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
    data_nascimento: Optional[date] = None
    sexo: Optional[str] = None  # M, F, O
    estado_civil: Optional[str] = None
    telefone: Optional[str] = None
    celular: Optional[str] = None

    # Endereço
    endereco: Optional[SolidesEndereco] = None

    # Dados profissionais
    matricula: Optional[str] = None
    cargo_id: Optional[int] = None
    cargo: Optional[SolidesCargo] = None
    departamento_id: Optional[int] = None
    departamento: Optional[SolidesDepartamento] = None
    gestor_id: Optional[int] = None
    gestor_nome: Optional[str] = None

    # Contrato
    data_admissao: Optional[date] = None
    data_demissao: Optional[date] = None
    tipo_contrato: Optional[str] = None  # CLT, PJ, Estagio, etc.
    regime_trabalho: Optional[str] = None  # Presencial, Remoto, Hibrido
    jornada_trabalho: Optional[str] = None
    salario: Optional[Decimal] = None

    # Status
    situacao: Optional[str] = None  # ativo, inativo, ferias, afastado, demitido

    # Perfil comportamental
    perfil_disc: Optional[dict] = None  # Resultados DISC
    perfil_profiler: Optional[dict] = None  # Resultados Profiler

    # Metadados
    foto_url: Optional[str] = None
    dados_adicionais: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")


class SolidesColaboradorCreate(BaseModel):
    """Schema para criar colaborador no Sólides."""
    nome: str = Field(..., min_length=2, max_length=200)
    email: str = Field(..., max_length=200)
    cpf: Optional[str] = None
    data_nascimento: Optional[date] = None
    telefone: Optional[str] = None
    celular: Optional[str] = None
    cargo_id: Optional[int] = None
    departamento_id: Optional[int] = None
    data_admissao: Optional[date] = None
    tipo_contrato: str = Field(default="CLT")

    model_config = ConfigDict(extra="allow")


# ==================== RECRUTAMENTO ====================

class SolidesVaga(BaseModel):
    """Vaga de emprego no Sólides."""
    id: Optional[int] = None
    titulo: str
    codigo: Optional[str] = None
    descricao: Optional[str] = None
    requisitos: Optional[str] = None
    beneficios: Optional[str] = None

    # Localização
    cargo_id: Optional[int] = None
    departamento_id: Optional[int] = None
    local_trabalho: Optional[str] = None
    regime_trabalho: Optional[str] = None

    # Faixa salarial
    salario_min: Optional[Decimal] = None
    salario_max: Optional[Decimal] = None
    esconder_salario: bool = True

    # Status
    status: Optional[str] = None  # aberta, em_andamento, congelada, encerrada
    quantidade_vagas: int = 1
    vagas_preenchidas: int = 0

    # Datas
    data_abertura: Optional[date] = None
    data_encerramento: Optional[date] = None

    # Responsável
    recrutador_id: Optional[int] = None
    gestor_id: Optional[int] = None

    # Metadados
    url_inscricao: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")


class SolidesCandidato(BaseModel):
    """Candidato no Sólides."""
    id: Optional[int] = None
    nome: str
    email: Optional[str] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    celular: Optional[str] = None

    # Dados pessoais
    data_nascimento: Optional[date] = None
    sexo: Optional[str] = None
    estado_civil: Optional[str] = None
    endereco: Optional[SolidesEndereco] = None

    # Dados profissionais
    cargo_pretendido: Optional[str] = None
    pretensao_salarial: Optional[Decimal] = None
    disponibilidade: Optional[str] = None

    # Currículo
    curriculo_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    # Formação
    formacao: Optional[List[dict]] = None  # [{instituicao, curso, nivel, conclusao}]
    experiencias: Optional[List[dict]] = None  # [{empresa, cargo, periodo, descricao}]
    habilidades: Optional[List[str]] = None
    idiomas: Optional[List[dict]] = None  # [{idioma, nivel}]

    # Status
    status: Optional[str] = None  # novo, em_analise, aprovado, reprovado, contratado

    # Perfil comportamental (se aplicado)
    perfil_disc: Optional[dict] = None
    perfil_profiler: Optional[dict] = None

    # Metadados
    fonte: Optional[str] = None  # linkedin, indeed, indicacao, site
    tags: Optional[List[str]] = None
    notas: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")


class SolidesInscricao(BaseModel):
    """Inscrição de candidato em vaga."""
    id: Optional[int] = None
    vaga_id: int
    candidato_id: int
    vaga: Optional[SolidesVaga] = None
    candidato: Optional[SolidesCandidato] = None

    # Status no processo
    etapa: Optional[str] = None  # triagem, entrevista_rh, entrevista_tecnica, proposta
    status: Optional[str] = None  # em_andamento, aprovado, reprovado, desistencia

    # Avaliações
    nota_triagem: Optional[Decimal] = None
    nota_entrevista: Optional[Decimal] = None
    nota_tecnica: Optional[Decimal] = None
    nota_final: Optional[Decimal] = None

    # Histórico
    historico_etapas: Optional[List[dict]] = None
    feedback: Optional[str] = None

    # Datas
    data_inscricao: Optional[datetime] = None
    data_ultima_etapa: Optional[datetime] = None
    data_conclusao: Optional[datetime] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")


# ==================== AVALIAÇÕES ====================

class SolidesAvaliacao(BaseModel):
    """Avaliação de desempenho no Sólides."""
    id: Optional[int] = None
    titulo: str
    tipo: Optional[str] = None  # autoavaliacao, gestor, 360, pares

    # Período
    ciclo: Optional[str] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None

    # Avaliado
    colaborador_id: Optional[int] = None
    colaborador_nome: Optional[str] = None

    # Avaliador
    avaliador_id: Optional[int] = None
    avaliador_nome: Optional[str] = None

    # Resultados
    status: Optional[str] = None  # pendente, em_andamento, concluida
    nota_final: Optional[Decimal] = None
    competencias: Optional[List[dict]] = None  # [{competencia, nota, peso}]
    metas: Optional[List[dict]] = None  # [{meta, resultado, percentual}]
    pontos_fortes: Optional[str] = None
    pontos_desenvolvimento: Optional[str] = None

    # Feedback
    feedback_gestor: Optional[str] = None
    feedback_colaborador: Optional[str] = None
    plano_desenvolvimento: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")


# ==================== PESQUISA DE CLIMA ====================

class SolidesPesquisaClima(BaseModel):
    """Pesquisa de clima organizacional."""
    id: Optional[int] = None
    titulo: str
    descricao: Optional[str] = None

    # Período
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None

    # Configuração
    anonima: bool = True
    departamentos: Optional[List[int]] = None  # IDs dos departamentos

    # Status
    status: Optional[str] = None  # rascunho, ativa, encerrada
    total_convidados: int = 0
    total_respostas: int = 0
    taxa_adesao: Optional[Decimal] = None

    # Resultados agregados
    nota_geral: Optional[Decimal] = None
    enps: Optional[int] = None  # Employee Net Promoter Score
    dimensoes: Optional[List[dict]] = None  # [{dimensao, nota, respostas}]

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")


# ==================== RESPONSES ====================

class SolidesPaginatedResponse(BaseModel):
    """Resposta paginada do Sólides."""
    data: List[Any] = Field(default_factory=list)
    total: Optional[int] = None
    page: Optional[int] = None
    per_page: Optional[int] = None
    total_pages: Optional[int] = None

    model_config = ConfigDict(extra="allow")


class SolidesSingleResponse(BaseModel):
    """Resposta de item único do Sólides."""
    data: Optional[dict] = None
    success: bool = True
    message: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class SolidesErrorResponse(BaseModel):
    """Resposta de erro do Sólides."""
    error: Optional[str] = None
    message: Optional[str] = None
    code: Optional[str] = None
    details: Optional[dict] = None

    model_config = ConfigDict(extra="allow")
