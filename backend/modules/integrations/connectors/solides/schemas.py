"""
Schemas Pydantic para API Sólides (RH + DP)
Sprint 33: Integration Framework

Documentação API V1: https://app.solides.com/pt-BR/api/v1/
Documentação API V3: https://apigw.solides.com.br/management/
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ==================== ENUMS ====================

class SituacaoColaborador(str, Enum):
    """Situação do colaborador no Sólides."""
    ATIVO = "ativo"
    INATIVO = "inativo"
    FERIAS = "ferias"
    AFASTADO = "afastado"
    DEMITIDO = "demitido"


class TipoContrato(str, Enum):
    """Tipo de contrato de trabalho."""
    CLT = "CLT"
    PJ = "PJ"
    ESTAGIO = "Estagio"
    TEMPORARIO = "Temporario"
    TERCEIRIZADO = "Terceirizado"
    JOVEM_APRENDIZ = "Jovem Aprendiz"


class TipoOcorrencia(str, Enum):
    """Tipos de ocorrência no Sólides."""
    ADVERTENCIA_VERBAL = "advertencia_verbal"
    ADVERTENCIA_ESCRITA = "advertencia_escrita"
    SUSPENSAO = "suspensao"
    ELOGIO = "elogio"
    PROMOCAO = "promocao"
    MERITO = "merito"
    FEEDBACK = "feedback"
    ANOTACAO = "anotacao"
    TREINAMENTO = "treinamento"
    OUTRO = "outro"


class TipoAbsenteismo(str, Enum):
    """Tipos de absenteísmo."""
    FALTA = "falta"
    ATRASO = "atraso"
    SAIDA_ANTECIPADA = "saida_antecipada"
    ATESTADO_MEDICO = "atestado_medico"
    LICENCA_MATERNIDADE = "licenca_maternidade"
    LICENCA_PATERNIDADE = "licenca_paternidade"
    LICENCA_CASAMENTO = "licenca_casamento"
    LICENCA_LUTO = "licenca_luto"
    AFASTAMENTO_INSS = "afastamento_inss"
    FERIAS = "ferias"
    FOLGA = "folga"
    OUTRO = "outro"


class PerfilDISC(str, Enum):
    """Perfis DISC."""
    DOMINANCIA = "D"
    INFLUENCIA = "I"
    ESTABILIDADE = "S"
    CONFORMIDADE = "C"


class StatusVaga(str, Enum):
    """Status da vaga."""
    ABERTA = "aberta"
    EM_ANDAMENTO = "em_andamento"
    CONGELADA = "congelada"
    ENCERRADA = "encerrada"


class StatusCandidato(str, Enum):
    """Status do candidato."""
    NOVO = "novo"
    EM_ANALISE = "em_analise"
    APROVADO = "aprovado"
    REPROVADO = "reprovado"
    CONTRATADO = "contratado"


# ==================== ENDEREÇO ====================

class SolidesEndereco(BaseModel):
    """Endereço no Sólides."""
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    pais: Optional[str] = Field(default="Brasil")

    model_config = ConfigDict(extra="allow")


# ==================== UNIDADE ====================

class SolidesUnidade(BaseModel):
    """Unidade/filial no Sólides."""
    id: Optional[int] = None
    nome: str
    codigo: Optional[str] = None
    cnpj: Optional[str] = None
    endereco: Optional[SolidesEndereco] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    ativo: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")


# ==================== DEPARTAMENTO ====================

class SolidesDepartamento(BaseModel):
    """Departamento no Sólides."""
    id: Optional[int] = None
    nome: str
    codigo: Optional[str] = None
    departamento_pai_id: Optional[int] = None
    gestor_id: Optional[int] = None
    unidade_id: Optional[int] = None
    ativo: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")


# ==================== CARGO ====================

class SolidesCargo(BaseModel):
    """Cargo no Sólides."""
    id: Optional[int] = None
    nome: str
    codigo: Optional[str] = None
    descricao: Optional[str] = None
    departamento_id: Optional[int] = None
    cbo_id: Optional[int] = None
    cbo_codigo: Optional[str] = None
    nivel: Optional[str] = None  # junior, pleno, senior, etc.
    faixa_salarial_min: Optional[Decimal] = None
    faixa_salarial_max: Optional[Decimal] = None
    ativo: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")


# ==================== CBO ====================

class SolidesCBO(BaseModel):
    """Código Brasileiro de Ocupações."""
    id: Optional[int] = None
    codigo: str
    nome: str
    descricao: Optional[str] = None

    model_config = ConfigDict(extra="allow")


# ==================== COLABORADOR ====================

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
    unidade_id: Optional[int] = None
    unidade: Optional[SolidesUnidade] = None
    gestor_id: Optional[int] = None
    gestor_nome: Optional[str] = None

    # Contrato
    data_admissao: Optional[date] = None
    data_demissao: Optional[date] = None
    tipo_contrato: Optional[str] = None  # CLT, PJ, Estagio, etc.
    regime_trabalho: Optional[str] = None  # Presencial, Remoto, Hibrido
    jornada_trabalho: Optional[str] = None
    carga_horaria_semanal: Optional[int] = None
    salario: Optional[Decimal] = None

    # Dados DP
    ctps_numero: Optional[str] = None
    ctps_serie: Optional[str] = None
    ctps_uf: Optional[str] = None
    pis: Optional[str] = None
    titulo_eleitor: Optional[str] = None
    certificado_reservista: Optional[str] = None

    # Dependentes
    dependentes: Optional[List[Dict[str, Any]]] = None

    # Status
    situacao: Optional[str] = None  # ativo, inativo, ferias, afastado, demitido

    # Perfil comportamental
    perfil_disc: Optional[Dict[str, Any]] = None  # Resultados DISC
    perfil_profiler: Optional[Dict[str, Any]] = None  # Resultados Profiler

    # Metadados
    foto_url: Optional[str] = None
    dados_adicionais: Optional[Dict[str, Any]] = None
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
    unidade_id: Optional[int] = None
    data_admissao: Optional[date] = None
    tipo_contrato: str = Field(default="CLT")
    salario: Optional[Decimal] = None

    model_config = ConfigDict(extra="allow")


class SolidesColaboradorUpdate(BaseModel):
    """Schema para atualizar colaborador no Sólides."""
    nome: Optional[str] = Field(None, min_length=2, max_length=200)
    email: Optional[str] = Field(None, max_length=200)
    telefone: Optional[str] = None
    celular: Optional[str] = None
    cargo_id: Optional[int] = None
    departamento_id: Optional[int] = None
    unidade_id: Optional[int] = None
    situacao: Optional[str] = None
    salario: Optional[Decimal] = None
    data_demissao: Optional[date] = None
    motivo_demissao: Optional[str] = None

    model_config = ConfigDict(extra="allow")


# ==================== OCORRÊNCIAS ====================

class SolidesOcorrencia(BaseModel):
    """Ocorrência de colaborador no Sólides."""
    id: Optional[int] = None
    colaborador_id: int
    colaborador_nome: Optional[str] = None
    tipo: str  # advertencia_verbal, advertencia_escrita, elogio, promocao, etc.
    descricao: str
    data: date
    data_vigencia: Optional[date] = None  # Para suspensões

    # Detalhes específicos por tipo
    duracao_dias: Optional[int] = None  # Para suspensões
    valor_aumento: Optional[Decimal] = None  # Para promoções/méritos
    percentual_aumento: Optional[Decimal] = None
    novo_cargo_id: Optional[int] = None  # Para promoções
    novo_cargo_nome: Optional[str] = None

    # Responsável
    registrado_por_id: Optional[int] = None
    registrado_por_nome: Optional[str] = None

    # Arquivos anexos
    anexos: Optional[List[Dict[str, str]]] = None  # [{nome, url}]

    # Metadados
    observacoes: Optional[str] = None
    dados_adicionais: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")


class SolidesOcorrenciaCreate(BaseModel):
    """Schema para criar ocorrência no Sólides."""
    colaborador_id: int
    tipo: str
    descricao: str
    data: date
    data_vigencia: Optional[date] = None
    duracao_dias: Optional[int] = None
    valor_aumento: Optional[Decimal] = None
    percentual_aumento: Optional[Decimal] = None
    novo_cargo_id: Optional[int] = None
    observacoes: Optional[str] = None

    model_config = ConfigDict(extra="allow")


# ==================== ABSENTEÍSMOS ====================

class SolidesAbsenteismo(BaseModel):
    """Absenteísmo (falta, atraso, afastamento) no Sólides."""
    id: Optional[int] = None
    colaborador_id: int
    colaborador_nome: Optional[str] = None
    tipo: str  # falta, atraso, saida_antecipada, atestado, licenca, etc.
    motivo: Optional[str] = None
    data_inicio: date
    data_fim: Optional[date] = None
    horas: Optional[Decimal] = None  # Para atrasos/saídas antecipadas
    minutos_atraso: Optional[int] = None

    # Justificativa
    justificado: bool = False
    documento_anexo: Optional[str] = None  # URL do atestado/documento
    cid: Optional[str] = None  # Código CID (para atestados médicos)

    # Impacto
    desconto_em_folha: bool = True
    dias_descontados: Optional[int] = None

    # INSS (para afastamentos longos)
    numero_beneficio_inss: Optional[str] = None
    data_inicio_inss: Optional[date] = None
    data_fim_inss: Optional[date] = None

    # Responsável
    registrado_por_id: Optional[int] = None
    registrado_por_nome: Optional[str] = None

    # Metadados
    observacoes: Optional[str] = None
    dados_adicionais: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")


class SolidesAbsenteismoCreate(BaseModel):
    """Schema para criar absenteísmo no Sólides."""
    colaborador_id: int
    tipo: str
    motivo: Optional[str] = None
    data_inicio: date
    data_fim: Optional[date] = None
    horas: Optional[Decimal] = None
    justificado: bool = False
    documento_anexo: Optional[str] = None
    cid: Optional[str] = None
    desconto_em_folha: bool = True
    observacoes: Optional[str] = None

    model_config = ConfigDict(extra="allow")


# ==================== PASSAPORTE COMPORTAMENTAL ====================

class SolidesPerfilDISC(BaseModel):
    """Perfil DISC detalhado."""
    dominancia: Decimal = Field(alias="D")
    influencia: Decimal = Field(alias="I")
    estabilidade: Decimal = Field(alias="S")
    conformidade: Decimal = Field(alias="C")
    perfil_predominante: str
    perfil_secundario: Optional[str] = None

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class SolidesCompetencia(BaseModel):
    """Competência avaliada."""
    nome: str
    nivel: Decimal  # 0-100
    descricao: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class SolidesPassaporte(BaseModel):
    """Passaporte comportamental do Sólides (API V3)."""
    colaborador_id: int
    colaborador_nome: Optional[str] = None

    # Perfil DISC
    perfil_disc: Optional[SolidesPerfilDISC] = None
    perfil_predominante: Optional[str] = None  # D, I, S, C ou combinações
    perfis_secundarios: Optional[List[str]] = None

    # Intensidade
    intensidade: Optional[Decimal] = None  # 0-100

    # Competências mapeadas
    competencias: Optional[List[SolidesCompetencia]] = None

    # Pontos fortes e desenvolvimento
    pontos_fortes: Optional[List[str]] = None
    pontos_desenvolvimento: Optional[List[str]] = None

    # Estilo de trabalho
    estilo_comunicacao: Optional[str] = None
    estilo_lideranca: Optional[str] = None
    ambiente_ideal: Optional[str] = None
    motivadores: Optional[List[str]] = None
    desmotivadores: Optional[List[str]] = None

    # Compatibilidade
    compatibilidade_cargo: Optional[Decimal] = None  # 0-100
    compatibilidade_equipe: Optional[Decimal] = None

    # Relatório completo
    relatorio_url: Optional[str] = None
    relatorio_pdf_url: Optional[str] = None

    # Metadados
    data_avaliacao: Optional[datetime] = None
    versao_instrumento: Optional[str] = None
    dados_adicionais: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

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
    unidade_id: Optional[int] = None
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
    formacao: Optional[List[Dict[str, Any]]] = None  # [{instituicao, curso, nivel, conclusao}]
    experiencias: Optional[List[Dict[str, Any]]] = None  # [{empresa, cargo, periodo, descricao}]
    habilidades: Optional[List[str]] = None
    idiomas: Optional[List[Dict[str, Any]]] = None  # [{idioma, nivel}]

    # Status
    status: Optional[str] = None  # novo, em_analise, aprovado, reprovado, contratado

    # Perfil comportamental (se aplicado)
    perfil_disc: Optional[Dict[str, Any]] = None
    perfil_profiler: Optional[Dict[str, Any]] = None

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
    historico_etapas: Optional[List[Dict[str, Any]]] = None
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
    competencias: Optional[List[Dict[str, Any]]] = None  # [{competencia, nota, peso}]
    metas: Optional[List[Dict[str, Any]]] = None  # [{meta, resultado, percentual}]
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
    dimensoes: Optional[List[Dict[str, Any]]] = None  # [{dimensao, nota, respostas}]

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")


# ==================== WEBHOOKS ====================

class SolidesWebhookEvent(BaseModel):
    """Evento de webhook do Sólides."""
    event: str  # novo_colaborador, edicao_colaborador, demissao, etc.
    timestamp: datetime
    data: Dict[str, Any]
    empresa_id: Optional[int] = None
    versao: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class SolidesWebhookEventType(str, Enum):
    """Tipos de eventos de webhook suportados."""
    NOVO_COLABORADOR = "novo_colaborador"
    EDICAO_COLABORADOR = "edicao_colaborador"
    DEMISSAO_COLABORADOR = "demissao_colaborador"
    NOVA_OCORRENCIA = "nova_ocorrencia"
    NOVO_ABSENTEISMO = "novo_absenteismo"
    NOVA_RESPOSTA_PESQUISA = "nova_resposta_pesquisa"
    NOVO_CURRICULO = "novo_curriculo"
    NOVA_INSCRICAO = "nova_inscricao"
    MUDANCA_ETAPA = "mudanca_etapa"


# ==================== RESPONSES ====================

class SolidesPaginatedResponse(BaseModel):
    """Resposta paginada do Sólides."""
    data: List[Any] = Field(default_factory=list)
    total: Optional[int] = None
    page: Optional[int] = None
    per_page: Optional[int] = None
    total_pages: Optional[int] = None
    current_page: Optional[int] = None
    last_page: Optional[int] = None

    model_config = ConfigDict(extra="allow")


class SolidesSingleResponse(BaseModel):
    """Resposta de item único do Sólides."""
    data: Optional[Dict[str, Any]] = None
    success: bool = True
    message: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class SolidesErrorResponse(BaseModel):
    """Resposta de erro do Sólides."""
    error: Optional[str] = None
    message: Optional[str] = None
    code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    errors: Optional[Dict[str, List[str]]] = None  # Erros de validação

    model_config = ConfigDict(extra="allow")


# ==================== SYNC STATUS ====================

class SolidesSyncStatus(BaseModel):
    """Status de sincronização com Sólides."""
    connected: bool
    last_sync_at: Optional[datetime] = None
    last_full_sync_at: Optional[datetime] = None
    total_colaboradores: int = 0
    total_departamentos: int = 0
    total_cargos: int = 0
    pending_conflicts: int = 0
    last_error: Optional[str] = None
    api_version: str = "v1"

    model_config = ConfigDict(extra="allow")
