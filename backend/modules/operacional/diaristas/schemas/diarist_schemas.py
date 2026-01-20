"""Schemas Pydantic para Diaristas."""

from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from modules.operacional.diaristas.models.diarist import (
    DiaristType,
    AssignmentType,
    RecurrenceType,
    PaymentMethod,
    Weekday,
)


# === Diarist Schemas ===


class DiaristBase(BaseModel):
    """Schema base de Diarista."""

    nome: str = Field(..., min_length=2, max_length=200)
    nome_social: Optional[str] = Field(None, max_length=200)
    cpf: str = Field(..., min_length=11, max_length=14)
    rg: Optional[str] = Field(None, max_length=20)
    data_nascimento: Optional[date] = None
    genero: Optional[str] = Field(None, max_length=20)
    nacionalidade: Optional[str] = Field("Brasileira", max_length=50)
    estado_civil: Optional[str] = Field(None, max_length=30)

    email: Optional[str] = Field(None, max_length=255)
    telefone: Optional[str] = Field(None, max_length=20)
    celular: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    contato_emergencia: Optional[str] = Field(None, max_length=200)
    telefone_emergencia: Optional[str] = Field(None, max_length=20)

    cep: Optional[str] = Field(None, max_length=10)
    logradouro: Optional[str] = Field(None, max_length=255)
    numero: Optional[str] = Field(None, max_length=20)
    complemento: Optional[str] = Field(None, max_length=100)
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)

    tipo: DiaristType = Field(default=DiaristType.LIMPEZA)
    especialidades: Optional[List[str]] = Field(default_factory=list)
    experiencia_anos: Optional[int] = Field(0, ge=0)
    certificacoes: Optional[List[dict]] = Field(default_factory=list)
    referencias: Optional[List[dict]] = Field(default_factory=list)

    dias_disponiveis: Optional[List[Weekday]] = Field(default_factory=list)
    horario_inicio: Optional[time] = Field(default=time(8, 0))
    horario_fim: Optional[time] = Field(default=time(17, 0))
    carga_horaria_max: Optional[int] = Field(8, ge=1, le=12)
    aceita_hora_extra: Optional[bool] = True
    distancia_max_km: Optional[int] = Field(30, ge=0)
    regioes_atendimento: Optional[List[str]] = Field(default_factory=list)

    valor_diaria: Decimal = Field(..., ge=0)
    valor_hora_extra: Optional[Decimal] = Field(Decimal("25.00"), ge=0)
    valor_adicional_noturno: Optional[Decimal] = Field(Decimal("30.00"), ge=0)
    valor_adicional_feriado: Optional[Decimal] = Field(Decimal("50.00"), ge=0)
    forma_pagamento_preferida: Optional[PaymentMethod] = PaymentMethod.PIX

    banco: Optional[str] = Field(None, max_length=100)
    agencia: Optional[str] = Field(None, max_length=20)
    conta: Optional[str] = Field(None, max_length=30)
    tipo_conta: Optional[str] = Field(None, max_length=20)
    pix_chave: Optional[str] = Field(None, max_length=100)
    pix_tipo: Optional[str] = Field(None, max_length=20)

    tags: Optional[List[str]] = Field(default_factory=list)
    observacoes: Optional[str] = None


class DiaristCreate(DiaristBase):
    """Schema de criacao de Diarista."""

    condominio_id: UUID
    codigo: Optional[str] = Field(None, max_length=50)
    documentos: Optional[List[dict]] = Field(default_factory=list)
    foto_url: Optional[str] = Field(None, max_length=500)


class DiaristUpdate(BaseModel):
    """Schema de atualizacao de Diarista."""

    nome: Optional[str] = Field(None, min_length=2, max_length=200)
    nome_social: Optional[str] = Field(None, max_length=200)
    data_nascimento: Optional[date] = None
    genero: Optional[str] = Field(None, max_length=20)
    estado_civil: Optional[str] = Field(None, max_length=30)

    email: Optional[str] = Field(None, max_length=255)
    telefone: Optional[str] = Field(None, max_length=20)
    celular: Optional[str] = Field(None, max_length=20)
    whatsapp: Optional[str] = Field(None, max_length=20)
    contato_emergencia: Optional[str] = Field(None, max_length=200)
    telefone_emergencia: Optional[str] = Field(None, max_length=20)

    cep: Optional[str] = Field(None, max_length=10)
    logradouro: Optional[str] = Field(None, max_length=255)
    numero: Optional[str] = Field(None, max_length=20)
    complemento: Optional[str] = Field(None, max_length=100)
    bairro: Optional[str] = Field(None, max_length=100)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)

    tipo: Optional[DiaristType] = None
    especialidades: Optional[List[str]] = None
    experiencia_anos: Optional[int] = Field(None, ge=0)
    certificacoes: Optional[List[dict]] = None
    referencias: Optional[List[dict]] = None

    dias_disponiveis: Optional[List[Weekday]] = None
    horario_inicio: Optional[time] = None
    horario_fim: Optional[time] = None
    carga_horaria_max: Optional[int] = Field(None, ge=1, le=12)
    aceita_hora_extra: Optional[bool] = None
    distancia_max_km: Optional[int] = Field(None, ge=0)
    regioes_atendimento: Optional[List[str]] = None

    valor_diaria: Optional[Decimal] = Field(None, ge=0)
    valor_hora_extra: Optional[Decimal] = Field(None, ge=0)
    valor_adicional_noturno: Optional[Decimal] = Field(None, ge=0)
    valor_adicional_feriado: Optional[Decimal] = Field(None, ge=0)
    forma_pagamento_preferida: Optional[PaymentMethod] = None

    banco: Optional[str] = Field(None, max_length=100)
    agencia: Optional[str] = Field(None, max_length=20)
    conta: Optional[str] = Field(None, max_length=30)
    tipo_conta: Optional[str] = Field(None, max_length=20)
    pix_chave: Optional[str] = Field(None, max_length=100)
    pix_tipo: Optional[str] = Field(None, max_length=20)

    documentos: Optional[List[dict]] = None
    foto_url: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = None
    observacoes: Optional[str] = None


class DiaristResponse(BaseModel):
    """Schema de resposta de Diarista."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    codigo: str
    nome: str
    nome_social: Optional[str] = None
    cpf: str
    rg: Optional[str] = None
    data_nascimento: Optional[date] = None
    genero: Optional[str] = None
    nacionalidade: Optional[str] = None
    estado_civil: Optional[str] = None

    email: Optional[str] = None
    telefone: Optional[str] = None
    celular: Optional[str] = None
    whatsapp: Optional[str] = None

    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None

    tipo: str
    especialidades: List[str] = []
    experiencia_anos: int = 0

    dias_disponiveis: List[str] = []
    horario_inicio: Optional[time] = None
    horario_fim: Optional[time] = None
    carga_horaria_max: int = 8
    aceita_hora_extra: bool = True

    valor_diaria: Decimal
    valor_hora_extra: Optional[Decimal] = None
    forma_pagamento_preferida: Optional[str] = None

    status: str
    is_blocked: bool = False
    data_admissao: Optional[date] = None

    total_diarias: int = 0
    total_horas: Decimal = Decimal("0")
    total_recebido: Decimal = Decimal("0")
    media_avaliacao: Decimal = Decimal("0")
    total_avaliacoes: int = 0
    taxa_comparecimento: Decimal = Decimal("100")
    taxa_pontualidade: Decimal = Decimal("100")
    ultima_diaria: Optional[date] = None
    proxima_diaria: Optional[date] = None

    score_confiabilidade: Decimal = Decimal("50")
    score_qualidade: Decimal = Decimal("50")

    tags: List[str] = []
    foto_url: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None


class DiaristListResponse(BaseModel):
    """Schema de lista de diaristas."""

    items: List[DiaristResponse]
    total: int
    page: int
    page_size: int
    pages: int


class DiaristStatsResponse(BaseModel):
    """Schema de estatisticas de diaristas."""

    total: int = 0
    ativos: int = 0
    inativos: int = 0
    bloqueados: int = 0
    por_tipo: dict = {}
    media_avaliacao_geral: float = 0.0
    total_diarias_mes: int = 0
    total_valor_mes: float = 0.0


# === Assignment Schemas ===


class DiaristAssignmentBase(BaseModel):
    """Schema base de Alocacao."""

    diarist_id: UUID
    tipo: AssignmentType = AssignmentType.AVULSO
    servico_tipo: str = Field(..., max_length=50)
    servico_descricao: Optional[str] = None
    local_servico: Optional[str] = Field(None, max_length=200)
    unidade_id: Optional[UUID] = None
    area_comum: Optional[str] = Field(None, max_length=100)

    data_inicio: date
    data_fim: Optional[date] = None
    horario_inicio: Optional[time] = Field(default=time(8, 0))
    horario_fim: Optional[time] = Field(default=time(17, 0))
    carga_horaria: Optional[int] = Field(8, ge=1, le=12)

    recorrencia: RecurrenceType = RecurrenceType.NENHUMA
    dias_semana: Optional[List[Weekday]] = Field(default_factory=list)
    intervalo_dias: Optional[int] = Field(None, ge=1)
    total_ocorrencias: Optional[int] = Field(None, ge=1)

    valor_acordado: Decimal = Field(..., ge=0)
    valor_adicional: Optional[Decimal] = Field(Decimal("0"), ge=0)
    desconto: Optional[Decimal] = Field(Decimal("0"), ge=0)
    forma_pagamento: Optional[PaymentMethod] = None

    contratante_nome: Optional[str] = Field(None, max_length=200)
    instrucoes: Optional[str] = None
    observacoes: Optional[str] = None
    materiais_necessarios: Optional[List[str]] = Field(default_factory=list)


class DiaristAssignmentCreate(DiaristAssignmentBase):
    """Schema de criacao de Alocacao."""

    condominio_id: UUID


class DiaristAssignmentUpdate(BaseModel):
    """Schema de atualizacao de Alocacao."""

    servico_descricao: Optional[str] = None
    local_servico: Optional[str] = Field(None, max_length=200)
    unidade_id: Optional[UUID] = None
    area_comum: Optional[str] = Field(None, max_length=100)

    data_fim: Optional[date] = None
    horario_inicio: Optional[time] = None
    horario_fim: Optional[time] = None
    carga_horaria: Optional[int] = Field(None, ge=1, le=12)

    valor_adicional: Optional[Decimal] = Field(None, ge=0)
    desconto: Optional[Decimal] = Field(None, ge=0)

    instrucoes: Optional[str] = None
    observacoes: Optional[str] = None
    materiais_necessarios: Optional[List[str]] = None


class DiaristAssignmentResponse(BaseModel):
    """Schema de resposta de Alocacao."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    diarist_id: UUID
    tipo: str
    status: str

    servico_tipo: str
    servico_descricao: Optional[str] = None
    local_servico: Optional[str] = None
    unidade_id: Optional[UUID] = None
    area_comum: Optional[str] = None

    data_inicio: date
    data_fim: Optional[date] = None
    horario_inicio: Optional[time] = None
    horario_fim: Optional[time] = None
    carga_horaria: int = 8

    recorrencia: str
    dias_semana: List[str] = []
    total_ocorrencias: Optional[int] = None
    ocorrencias_realizadas: int = 0

    valor_acordado: Decimal
    valor_adicional: Decimal = Decimal("0")
    desconto: Decimal = Decimal("0")
    valor_total: Optional[Decimal] = None
    forma_pagamento: Optional[str] = None

    contratante_nome: Optional[str] = None
    aprovado_at: Optional[datetime] = None

    instrucoes: Optional[str] = None
    observacoes: Optional[str] = None
    materiais_necessarios: List[str] = []

    created_at: datetime
    updated_at: Optional[datetime] = None


# === Schedule Schemas ===


class DiaristScheduleBase(BaseModel):
    """Schema base de Agenda."""

    diarist_id: UUID
    assignment_id: Optional[UUID] = None
    data: date
    horario_inicio_previsto: time
    horario_fim_previsto: time
    carga_horaria_prevista: Optional[int] = Field(8, ge=1, le=12)

    servico_tipo: Optional[str] = Field(None, max_length=50)
    servico_descricao: Optional[str] = None
    local_servico: Optional[str] = Field(None, max_length=200)
    tarefas: Optional[List[str]] = Field(default_factory=list)

    is_feriado: Optional[bool] = False
    is_fim_semana: Optional[bool] = False

    valor_base: Optional[Decimal] = Field(None, ge=0)
    observacoes: Optional[str] = None


class DiaristScheduleCreate(DiaristScheduleBase):
    """Schema de criacao de Agenda."""

    condominio_id: UUID


class DiaristScheduleUpdate(BaseModel):
    """Schema de atualizacao de Agenda."""

    horario_inicio_previsto: Optional[time] = None
    horario_fim_previsto: Optional[time] = None
    carga_horaria_prevista: Optional[int] = Field(None, ge=1, le=12)

    servico_descricao: Optional[str] = None
    local_servico: Optional[str] = Field(None, max_length=200)
    tarefas: Optional[List[str]] = None

    valor_base: Optional[Decimal] = Field(None, ge=0)
    valor_adicional: Optional[Decimal] = Field(None, ge=0)
    valor_desconto: Optional[Decimal] = Field(None, ge=0)
    observacoes: Optional[str] = None


class DiaristScheduleResponse(BaseModel):
    """Schema de resposta de Agenda."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    diarist_id: UUID
    assignment_id: Optional[UUID] = None

    data: date
    horario_inicio_previsto: time
    horario_fim_previsto: time
    carga_horaria_prevista: int = 8

    checkin_at: Optional[datetime] = None
    checkout_at: Optional[datetime] = None
    horas_trabalhadas: Decimal = Decimal("0")
    horas_extras: Decimal = Decimal("0")

    status: str
    is_feriado: bool = False
    is_fim_semana: bool = False

    servico_tipo: Optional[str] = None
    servico_descricao: Optional[str] = None
    local_servico: Optional[str] = None
    tarefas: List[str] = []
    tarefas_concluidas: List[str] = []

    avaliacao_nota: Optional[int] = None
    avaliacao_comentario: Optional[str] = None

    valor_base: Optional[Decimal] = None
    valor_hora_extra: Decimal = Decimal("0")
    valor_adicional: Decimal = Decimal("0")
    valor_desconto: Decimal = Decimal("0")
    valor_total: Optional[Decimal] = None

    observacoes: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None


class CheckinRequest(BaseModel):
    """Schema de check-in."""

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    foto_url: Optional[str] = Field(None, max_length=500)


class CheckoutRequest(BaseModel):
    """Schema de check-out."""

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    foto_url: Optional[str] = Field(None, max_length=500)
    tarefas_concluidas: Optional[List[str]] = Field(default_factory=list)
    ocorrencias: Optional[List[dict]] = Field(default_factory=list)
    materiais_usados: Optional[List[dict]] = Field(default_factory=list)


# === Payment Schemas ===


class DiaristPaymentBase(BaseModel):
    """Schema base de Pagamento."""

    diarist_id: UUID
    assignment_id: Optional[UUID] = None

    periodo_inicio: date
    periodo_fim: date
    competencia: Optional[str] = Field(None, max_length=7)

    valor_diarias: Decimal = Field(..., ge=0)
    quantidade_diarias: Optional[int] = Field(0, ge=0)
    valor_horas_extras: Optional[Decimal] = Field(Decimal("0"), ge=0)
    quantidade_horas_extras: Optional[Decimal] = Field(Decimal("0"), ge=0)
    valor_adicional: Optional[Decimal] = Field(Decimal("0"), ge=0)
    descricao_adicional: Optional[str] = None
    valor_desconto: Optional[Decimal] = Field(Decimal("0"), ge=0)
    descricao_desconto: Optional[str] = None

    inss_retido: Optional[Decimal] = Field(Decimal("0"), ge=0)
    iss_retido: Optional[Decimal] = Field(Decimal("0"), ge=0)
    irrf_retido: Optional[Decimal] = Field(Decimal("0"), ge=0)
    outras_retencoes: Optional[Decimal] = Field(Decimal("0"), ge=0)

    forma_pagamento: Optional[PaymentMethod] = None
    data_vencimento: Optional[date] = None
    observacoes: Optional[str] = None

    schedules_ids: Optional[List[UUID]] = Field(default_factory=list)


class DiaristPaymentCreate(DiaristPaymentBase):
    """Schema de criacao de Pagamento."""

    condominio_id: UUID


class DiaristPaymentUpdate(BaseModel):
    """Schema de atualizacao de Pagamento."""

    valor_adicional: Optional[Decimal] = Field(None, ge=0)
    descricao_adicional: Optional[str] = None
    valor_desconto: Optional[Decimal] = Field(None, ge=0)
    descricao_desconto: Optional[str] = None

    inss_retido: Optional[Decimal] = Field(None, ge=0)
    iss_retido: Optional[Decimal] = Field(None, ge=0)
    irrf_retido: Optional[Decimal] = Field(None, ge=0)
    outras_retencoes: Optional[Decimal] = Field(None, ge=0)

    data_vencimento: Optional[date] = None
    observacoes: Optional[str] = None


class DiaristPaymentResponse(BaseModel):
    """Schema de resposta de Pagamento."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    diarist_id: UUID
    assignment_id: Optional[UUID] = None

    periodo_inicio: date
    periodo_fim: date
    competencia: Optional[str] = None

    valor_diarias: Decimal
    quantidade_diarias: int = 0
    valor_horas_extras: Decimal = Decimal("0")
    quantidade_horas_extras: Decimal = Decimal("0")
    valor_adicional: Decimal = Decimal("0")
    valor_desconto: Decimal = Decimal("0")
    valor_bruto: Optional[Decimal] = None
    valor_liquido: Optional[Decimal] = None

    inss_retido: Decimal = Decimal("0")
    iss_retido: Decimal = Decimal("0")
    irrf_retido: Decimal = Decimal("0")
    outras_retencoes: Decimal = Decimal("0")

    status: str
    forma_pagamento: Optional[str] = None
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None
    comprovante_url: Optional[str] = None

    aprovado_at: Optional[datetime] = None
    observacoes: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None


# === Evaluation Schemas ===


class DiaristEvaluationBase(BaseModel):
    """Schema base de Avaliacao."""

    diarist_id: UUID
    schedule_id: Optional[UUID] = None

    avaliador_nome: Optional[str] = Field(None, max_length=200)
    avaliador_tipo: Optional[str] = Field(None, max_length=50)

    nota_geral: int = Field(..., ge=1, le=5)
    nota_pontualidade: Optional[int] = Field(None, ge=1, le=5)
    nota_qualidade: Optional[int] = Field(None, ge=1, le=5)
    nota_profissionalismo: Optional[int] = Field(None, ge=1, le=5)
    nota_comunicacao: Optional[int] = Field(None, ge=1, le=5)
    nota_cuidado: Optional[int] = Field(None, ge=1, le=5)

    comentario: Optional[str] = None
    pontos_positivos: Optional[List[str]] = Field(default_factory=list)
    pontos_melhorar: Optional[List[str]] = Field(default_factory=list)

    recomendaria: Optional[bool] = True
    contrataria_novamente: Optional[bool] = True

    servico_tipo: Optional[str] = Field(None, max_length=50)
    data_servico: Optional[date] = None

    is_anonima: Optional[bool] = False


class DiaristEvaluationCreate(DiaristEvaluationBase):
    """Schema de criacao de Avaliacao."""

    condominio_id: UUID
    avaliador_id: UUID


class DiaristEvaluationResponse(BaseModel):
    """Schema de resposta de Avaliacao."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    diarist_id: UUID
    schedule_id: Optional[UUID] = None

    avaliador_nome: Optional[str] = None
    avaliador_tipo: Optional[str] = None

    nota_geral: int
    nota_pontualidade: Optional[int] = None
    nota_qualidade: Optional[int] = None
    nota_profissionalismo: Optional[int] = None
    nota_comunicacao: Optional[int] = None
    nota_cuidado: Optional[int] = None

    comentario: Optional[str] = None
    pontos_positivos: List[str] = []
    pontos_melhorar: List[str] = []

    recomendaria: bool = True
    contrataria_novamente: bool = True

    servico_tipo: Optional[str] = None
    data_servico: Optional[date] = None

    is_publicada: bool = True
    is_anonima: bool = False

    resposta: Optional[str] = None
    resposta_at: Optional[datetime] = None

    created_at: datetime


# === AI Schemas ===


class DiaristSuggestionResponse(BaseModel):
    """Schema de sugestao de diarista."""

    diarist_id: str
    diarist_nome: str
    diarist_tipo: str
    score: float
    motivo: str
    disponivel: bool
    valor_diaria: float
    media_avaliacao: float
    total_diarias: int


class DiaristAvailabilityResponse(BaseModel):
    """Schema de disponibilidade."""

    diarist_id: str
    diarist_nome: str
    data: date
    horario_inicio: time
    horario_fim: time
    disponivel: bool
    motivo: Optional[str] = None


class DiaristPerformanceResponse(BaseModel):
    """Schema de performance."""

    diarist_id: str
    diarist_nome: str
    periodo: str
    total_diarias: int
    total_horas: float
    taxa_comparecimento: float
    taxa_pontualidade: float
    media_avaliacao: float
    total_recebido: float
    tendencia: str
    recomendacoes: List[str]


class ScheduleOptimizationResponse(BaseModel):
    """Schema de otimizacao de agenda."""

    data: date
    sugestoes: List[dict]
    conflitos: List[dict]
    recomendacoes: List[str]
