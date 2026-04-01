"""
Schemas Pydantic para API Sólides (RH + DP)
Sprint 33: Integration Framework

Documentação API V1: https://app.solides.com/pt-BR/api/v1/
Documentação API V3: https://apigw.solides.com.br/management/
"""

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ==================== ENUMS ====================


class SituacaoColaborador(StrEnum):
    """Situação do colaborador no Sólides."""

    ATIVO = "ativo"
    INATIVO = "inativo"
    FERIAS = "ferias"
    AFASTADO = "afastado"
    DEMITIDO = "demitido"


class TipoContrato(StrEnum):
    """Tipo de contrato de trabalho."""

    CLT = "CLT"
    PJ = "PJ"
    ESTAGIO = "Estagio"
    TEMPORARIO = "Temporario"
    TERCEIRIZADO = "Terceirizado"
    JOVEM_APRENDIZ = "Jovem Aprendiz"


class TipoOcorrencia(StrEnum):
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


class TipoAbsenteismo(StrEnum):
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


class PerfilDISC(StrEnum):
    """Perfis DISC."""

    DOMINANCIA = "D"
    INFLUENCIA = "I"
    ESTABILIDADE = "S"
    CONFORMIDADE = "C"


class StatusVaga(StrEnum):
    """Status da vaga."""

    ABERTA = "aberta"
    EM_ANDAMENTO = "em_andamento"
    CONGELADA = "congelada"
    ENCERRADA = "encerrada"


class StatusCandidato(StrEnum):
    """Status do candidato."""

    NOVO = "novo"
    EM_ANALISE = "em_analise"
    APROVADO = "aprovado"
    REPROVADO = "reprovado"
    CONTRATADO = "contratado"


# ==================== ENDEREÇO ====================


class SolidesEndereco(BaseModel):
    """Endereço no Sólides."""

    logradouro: str | None = None
    numero: str | None = None
    complemento: str | None = None
    bairro: str | None = None
    cidade: str | None = None
    estado: str | None = None
    cep: str | None = None
    pais: str | None = Field(default="Brasil")

    model_config = ConfigDict(extra="allow")


# ==================== UNIDADE ====================


class SolidesUnidade(BaseModel):
    """Unidade/filial no Sólides."""

    id: int | None = None
    nome: str
    codigo: str | None = None
    cnpj: str | None = None
    endereco: SolidesEndereco | None = None
    telefone: str | None = None
    email: str | None = None
    ativo: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(extra="allow")


# ==================== DEPARTAMENTO ====================


class SolidesDepartamento(BaseModel):
    """Departamento no Sólides."""

    id: int | None = None
    nome: str
    codigo: str | None = None
    departamento_pai_id: int | None = None
    gestor_id: int | None = None
    unidade_id: int | None = None
    ativo: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(extra="allow")


# ==================== CARGO ====================


class SolidesCargo(BaseModel):
    """Cargo no Sólides."""

    id: int | None = None
    nome: str
    codigo: str | None = None
    descricao: str | None = None
    departamento_id: int | None = None
    cbo_id: int | None = None
    cbo_codigo: str | None = None
    nivel: str | None = None  # junior, pleno, senior, etc.
    faixa_salarial_min: Decimal | None = None
    faixa_salarial_max: Decimal | None = None
    ativo: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(extra="allow")


# ==================== CBO ====================


class SolidesCBO(BaseModel):
    """Código Brasileiro de Ocupações."""

    id: int | None = None
    codigo: str
    nome: str
    descricao: str | None = None

    model_config = ConfigDict(extra="allow")


# ==================== COLABORADOR ====================


class SolidesColaborador(BaseModel):
    """Colaborador no Sólides."""

    id: int | None = None
    nome: str
    email: str | None = None
    cpf: str | None = None
    rg: str | None = None
    data_nascimento: date | None = None
    sexo: str | None = None  # M, F, O
    estado_civil: str | None = None
    telefone: str | None = None
    celular: str | None = None

    # Endereço
    endereco: SolidesEndereco | None = None

    # Dados profissionais
    matricula: str | None = None
    cargo_id: int | None = None
    cargo: SolidesCargo | None = None
    departamento_id: int | None = None
    departamento: SolidesDepartamento | None = None
    unidade_id: int | None = None
    unidade: SolidesUnidade | None = None
    gestor_id: int | None = None
    gestor_nome: str | None = None

    # Contrato
    data_admissao: date | None = None
    data_demissao: date | None = None
    tipo_contrato: str | None = None  # CLT, PJ, Estagio, etc.
    regime_trabalho: str | None = None  # Presencial, Remoto, Hibrido
    jornada_trabalho: str | None = None
    carga_horaria_semanal: int | None = None
    salario: Decimal | None = None

    # Dados DP
    ctps_numero: str | None = None
    ctps_serie: str | None = None
    ctps_uf: str | None = None
    pis: str | None = None
    titulo_eleitor: str | None = None
    certificado_reservista: str | None = None

    # Dependentes
    dependentes: list[dict[str, Any]] | None = None

    # Status
    situacao: str | None = None  # ativo, inativo, ferias, afastado, demitido

    # Perfil comportamental
    perfil_disc: dict[str, Any] | None = None  # Resultados DISC
    perfil_profiler: dict[str, Any] | None = None  # Resultados Profiler

    # Metadados
    foto_url: str | None = None
    dados_adicionais: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(extra="allow")


class SolidesColaboradorCreate(BaseModel):
    """Schema para criar colaborador no Sólides."""

    nome: str = Field(..., min_length=2, max_length=200)
    email: str = Field(..., max_length=200)
    cpf: str | None = None
    data_nascimento: date | None = None
    telefone: str | None = None
    celular: str | None = None
    cargo_id: int | None = None
    departamento_id: int | None = None
    unidade_id: int | None = None
    data_admissao: date | None = None
    tipo_contrato: str = Field(default="CLT")
    salario: Decimal | None = None

    model_config = ConfigDict(extra="allow")


class SolidesColaboradorUpdate(BaseModel):
    """Schema para atualizar colaborador no Sólides."""

    nome: str | None = Field(None, min_length=2, max_length=200)
    email: str | None = Field(None, max_length=200)
    telefone: str | None = None
    celular: str | None = None
    cargo_id: int | None = None
    departamento_id: int | None = None
    unidade_id: int | None = None
    situacao: str | None = None
    salario: Decimal | None = None
    data_demissao: date | None = None
    motivo_demissao: str | None = None

    model_config = ConfigDict(extra="allow")


# ==================== OCORRÊNCIAS ====================


class SolidesOcorrencia(BaseModel):
    """Ocorrência de colaborador no Sólides."""

    id: int | None = None
    colaborador_id: int
    colaborador_nome: str | None = None
    tipo: str  # advertencia_verbal, advertencia_escrita, elogio, promocao, etc.
    descricao: str
    data: date
    data_vigencia: date | None = None  # Para suspensões

    # Detalhes específicos por tipo
    duracao_dias: int | None = None  # Para suspensões
    valor_aumento: Decimal | None = None  # Para promoções/méritos
    percentual_aumento: Decimal | None = None
    novo_cargo_id: int | None = None  # Para promoções
    novo_cargo_nome: str | None = None

    # Responsável
    registrado_por_id: int | None = None
    registrado_por_nome: str | None = None

    # Arquivos anexos
    anexos: list[dict[str, str]] | None = None  # [{nome, url}]

    # Metadados
    observacoes: str | None = None
    dados_adicionais: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(extra="allow")


class SolidesOcorrenciaCreate(BaseModel):
    """Schema para criar ocorrência no Sólides."""

    colaborador_id: int
    tipo: str
    descricao: str
    data: date
    data_vigencia: date | None = None
    duracao_dias: int | None = None
    valor_aumento: Decimal | None = None
    percentual_aumento: Decimal | None = None
    novo_cargo_id: int | None = None
    observacoes: str | None = None

    model_config = ConfigDict(extra="allow")


# ==================== ABSENTEÍSMOS ====================


class SolidesAbsenteismo(BaseModel):
    """Absenteísmo (falta, atraso, afastamento) no Sólides."""

    id: int | None = None
    colaborador_id: int
    colaborador_nome: str | None = None
    tipo: str  # falta, atraso, saida_antecipada, atestado, licenca, etc.
    motivo: str | None = None
    data_inicio: date
    data_fim: date | None = None
    horas: Decimal | None = None  # Para atrasos/saídas antecipadas
    minutos_atraso: int | None = None

    # Justificativa
    justificado: bool = False
    documento_anexo: str | None = None  # URL do atestado/documento
    cid: str | None = None  # Código CID (para atestados médicos)

    # Impacto
    desconto_em_folha: bool = True
    dias_descontados: int | None = None

    # INSS (para afastamentos longos)
    numero_beneficio_inss: str | None = None
    data_inicio_inss: date | None = None
    data_fim_inss: date | None = None

    # Responsável
    registrado_por_id: int | None = None
    registrado_por_nome: str | None = None

    # Metadados
    observacoes: str | None = None
    dados_adicionais: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(extra="allow")


class SolidesAbsenteismoCreate(BaseModel):
    """Schema para criar absenteísmo no Sólides."""

    colaborador_id: int
    tipo: str
    motivo: str | None = None
    data_inicio: date
    data_fim: date | None = None
    horas: Decimal | None = None
    justificado: bool = False
    documento_anexo: str | None = None
    cid: str | None = None
    desconto_em_folha: bool = True
    observacoes: str | None = None

    model_config = ConfigDict(extra="allow")


# ==================== PASSAPORTE COMPORTAMENTAL ====================


class SolidesPerfilDISC(BaseModel):
    """Perfil DISC detalhado."""

    dominancia: Decimal = Field(alias="D")
    influencia: Decimal = Field(alias="I")
    estabilidade: Decimal = Field(alias="S")
    conformidade: Decimal = Field(alias="C")
    perfil_predominante: str
    perfil_secundario: str | None = None

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class SolidesCompetencia(BaseModel):
    """Competência avaliada."""

    nome: str
    nivel: Decimal  # 0-100
    descricao: str | None = None

    model_config = ConfigDict(extra="allow")


class SolidesPassaporte(BaseModel):
    """Passaporte comportamental do Sólides (API V3)."""

    colaborador_id: int
    colaborador_nome: str | None = None

    # Perfil DISC
    perfil_disc: SolidesPerfilDISC | None = None
    perfil_predominante: str | None = None  # D, I, S, C ou combinações
    perfis_secundarios: list[str] | None = None

    # Intensidade
    intensidade: Decimal | None = None  # 0-100

    # Competências mapeadas
    competencias: list[SolidesCompetencia] | None = None

    # Pontos fortes e desenvolvimento
    pontos_fortes: list[str] | None = None
    pontos_desenvolvimento: list[str] | None = None

    # Estilo de trabalho
    estilo_comunicacao: str | None = None
    estilo_lideranca: str | None = None
    ambiente_ideal: str | None = None
    motivadores: list[str] | None = None
    desmotivadores: list[str] | None = None

    # Compatibilidade
    compatibilidade_cargo: Decimal | None = None  # 0-100
    compatibilidade_equipe: Decimal | None = None

    # Relatório completo
    relatorio_url: str | None = None
    relatorio_pdf_url: str | None = None

    # Metadados
    data_avaliacao: datetime | None = None
    versao_instrumento: str | None = None
    dados_adicionais: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(extra="allow")


# ==================== RECRUTAMENTO ====================


class SolidesVaga(BaseModel):
    """Vaga de emprego no Sólides."""

    id: int | None = None
    titulo: str
    codigo: str | None = None
    descricao: str | None = None
    requisitos: str | None = None
    beneficios: str | None = None

    # Localização
    cargo_id: int | None = None
    departamento_id: int | None = None
    unidade_id: int | None = None
    local_trabalho: str | None = None
    regime_trabalho: str | None = None

    # Faixa salarial
    salario_min: Decimal | None = None
    salario_max: Decimal | None = None
    esconder_salario: bool = True

    # Status
    status: str | None = None  # aberta, em_andamento, congelada, encerrada
    quantidade_vagas: int = 1
    vagas_preenchidas: int = 0

    # Datas
    data_abertura: date | None = None
    data_encerramento: date | None = None

    # Responsável
    recrutador_id: int | None = None
    gestor_id: int | None = None

    # Metadados
    url_inscricao: str | None = None
    tags: list[str] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(extra="allow")


class SolidesCandidato(BaseModel):
    """Candidato no Sólides."""

    id: int | None = None
    nome: str
    email: str | None = None
    cpf: str | None = None
    telefone: str | None = None
    celular: str | None = None

    # Dados pessoais
    data_nascimento: date | None = None
    sexo: str | None = None
    estado_civil: str | None = None
    endereco: SolidesEndereco | None = None

    # Dados profissionais
    cargo_pretendido: str | None = None
    pretensao_salarial: Decimal | None = None
    disponibilidade: str | None = None

    # Currículo
    curriculo_url: str | None = None
    linkedin_url: str | None = None
    portfolio_url: str | None = None

    # Formação
    formacao: list[dict[str, Any]] | None = None  # [{instituicao, curso, nivel, conclusao}]
    experiencias: list[dict[str, Any]] | None = None  # [{empresa, cargo, periodo, descricao}]
    habilidades: list[str] | None = None
    idiomas: list[dict[str, Any]] | None = None  # [{idioma, nivel}]

    # Status
    status: str | None = None  # novo, em_analise, aprovado, reprovado, contratado

    # Perfil comportamental (se aplicado)
    perfil_disc: dict[str, Any] | None = None
    perfil_profiler: dict[str, Any] | None = None

    # Metadados
    fonte: str | None = None  # linkedin, indeed, indicacao, site
    tags: list[str] | None = None
    notas: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(extra="allow")


class SolidesInscricao(BaseModel):
    """Inscrição de candidato em vaga."""

    id: int | None = None
    vaga_id: int
    candidato_id: int
    vaga: SolidesVaga | None = None
    candidato: SolidesCandidato | None = None

    # Status no processo
    etapa: str | None = None  # triagem, entrevista_rh, entrevista_tecnica, proposta
    status: str | None = None  # em_andamento, aprovado, reprovado, desistencia

    # Avaliações
    nota_triagem: Decimal | None = None
    nota_entrevista: Decimal | None = None
    nota_tecnica: Decimal | None = None
    nota_final: Decimal | None = None

    # Histórico
    historico_etapas: list[dict[str, Any]] | None = None
    feedback: str | None = None

    # Datas
    data_inscricao: datetime | None = None
    data_ultima_etapa: datetime | None = None
    data_conclusao: datetime | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(extra="allow")


# ==================== AVALIAÇÕES ====================


class SolidesAvaliacao(BaseModel):
    """Avaliação de desempenho no Sólides."""

    id: int | None = None
    titulo: str
    tipo: str | None = None  # autoavaliacao, gestor, 360, pares

    # Período
    ciclo: str | None = None
    data_inicio: date | None = None
    data_fim: date | None = None

    # Avaliado
    colaborador_id: int | None = None
    colaborador_nome: str | None = None

    # Avaliador
    avaliador_id: int | None = None
    avaliador_nome: str | None = None

    # Resultados
    status: str | None = None  # pendente, em_andamento, concluida
    nota_final: Decimal | None = None
    competencias: list[dict[str, Any]] | None = None  # [{competencia, nota, peso}]
    metas: list[dict[str, Any]] | None = None  # [{meta, resultado, percentual}]
    pontos_fortes: str | None = None
    pontos_desenvolvimento: str | None = None

    # Feedback
    feedback_gestor: str | None = None
    feedback_colaborador: str | None = None
    plano_desenvolvimento: str | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(extra="allow")


# ==================== PESQUISA DE CLIMA ====================


class SolidesPesquisaClima(BaseModel):
    """Pesquisa de clima organizacional."""

    id: int | None = None
    titulo: str
    descricao: str | None = None

    # Período
    data_inicio: date | None = None
    data_fim: date | None = None

    # Configuração
    anonima: bool = True
    departamentos: list[int] | None = None  # IDs dos departamentos

    # Status
    status: str | None = None  # rascunho, ativa, encerrada
    total_convidados: int = 0
    total_respostas: int = 0
    taxa_adesao: Decimal | None = None

    # Resultados agregados
    nota_geral: Decimal | None = None
    enps: int | None = None  # Employee Net Promoter Score
    dimensoes: list[dict[str, Any]] | None = None  # [{dimensao, nota, respostas}]

    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(extra="allow")


# ==================== WEBHOOKS ====================


class SolidesWebhookEvent(BaseModel):
    """Evento de webhook do Sólides."""

    event: str  # novo_colaborador, edicao_colaborador, demissao, etc.
    timestamp: datetime
    data: dict[str, Any]
    empresa_id: int | None = None
    versao: str | None = None

    model_config = ConfigDict(extra="allow")


class SolidesWebhookEventType(StrEnum):
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

    data: list[Any] = Field(default_factory=list)
    total: int | None = None
    page: int | None = None
    per_page: int | None = None
    total_pages: int | None = None
    current_page: int | None = None
    last_page: int | None = None

    model_config = ConfigDict(extra="allow")


class SolidesSingleResponse(BaseModel):
    """Resposta de item único do Sólides."""

    data: dict[str, Any] | None = None
    success: bool = True
    message: str | None = None

    model_config = ConfigDict(extra="allow")


class SolidesErrorResponse(BaseModel):
    """Resposta de erro do Sólides."""

    error: str | None = None
    message: str | None = None
    code: str | None = None
    details: dict[str, Any] | None = None
    errors: dict[str, list[str]] | None = None  # Erros de validação

    model_config = ConfigDict(extra="allow")


# ==================== SYNC STATUS ====================


class SolidesSyncStatus(BaseModel):
    """Status de sincronização com Sólides."""

    connected: bool
    last_sync_at: datetime | None = None
    last_full_sync_at: datetime | None = None
    total_colaboradores: int = 0
    total_departamentos: int = 0
    total_cargos: int = 0
    pending_conflicts: int = 0
    last_error: str | None = None
    api_version: str = "v1"

    model_config = ConfigDict(extra="allow")
