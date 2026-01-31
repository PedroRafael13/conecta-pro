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
    cpf: str = Field(..., min_length=11, max_length=14)
    rg: Optional[str] = Field(None, max_length=20)
    data_nascimento: Optional[date] = None

    email: Optional[str] = Field(None, max_length=255)
    telefone: Optional[str] = Field(None, max_length=20)
    telefone_emergencia: Optional[str] = Field(None, max_length=20)
    foto_url: Optional[str] = Field(None, max_length=500)

    endereco: Optional[str] = Field(None, max_length=500)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, max_length=10)

    tipos_servico: Optional[List[str]] = Field(default_factory=list)
    especialidades: Optional[List[str]] = Field(default_factory=list)
    experiencia_anos: Optional[int] = Field(0, ge=0)
    referencias: Optional[dict] = Field(default_factory=dict)
    documentos: Optional[dict] = Field(default_factory=dict)

    dias_disponiveis: Optional[List[str]] = Field(default_factory=list)
    hora_inicio_disponivel: Optional[time] = Field(default=time(8, 0))
    hora_fim_disponivel: Optional[time] = Field(default=time(17, 0))
    aceita_hora_extra: Optional[bool] = True

    valor_hora: Optional[Decimal] = Field(None, ge=0)
    valor_diaria: Decimal = Field(..., ge=0)
    valor_hora_extra: Optional[Decimal] = Field(Decimal("25.00"), ge=0)

    banco: Optional[str] = Field(None, max_length=100)
    agencia: Optional[str] = Field(None, max_length=20)
    conta: Optional[str] = Field(None, max_length=30)
    tipo_conta: Optional[str] = Field(None, max_length=20)
    pix: Optional[str] = Field(None, max_length=100)


class DiaristCreate(DiaristBase):
    """Schema de criacao de Diarista."""

    pass


class DiaristUpdate(BaseModel):
    """Schema de atualizacao de Diarista."""

    nome: Optional[str] = Field(None, min_length=2, max_length=200)
    data_nascimento: Optional[date] = None

    email: Optional[str] = Field(None, max_length=255)
    telefone: Optional[str] = Field(None, max_length=20)
    telefone_emergencia: Optional[str] = Field(None, max_length=20)
    foto_url: Optional[str] = Field(None, max_length=500)

    endereco: Optional[str] = Field(None, max_length=500)
    cidade: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None, max_length=2)
    cep: Optional[str] = Field(None, max_length=10)

    tipos_servico: Optional[List[str]] = None
    especialidades: Optional[List[str]] = None
    experiencia_anos: Optional[int] = Field(None, ge=0)
    referencias: Optional[dict] = None
    documentos: Optional[dict] = None

    dias_disponiveis: Optional[List[str]] = None
    hora_inicio_disponivel: Optional[time] = None
    hora_fim_disponivel: Optional[time] = None
    aceita_hora_extra: Optional[bool] = None

    valor_hora: Optional[Decimal] = Field(None, ge=0)
    valor_diaria: Optional[Decimal] = Field(None, ge=0)
    valor_hora_extra: Optional[Decimal] = Field(None, ge=0)

    banco: Optional[str] = Field(None, max_length=100)
    agencia: Optional[str] = Field(None, max_length=20)
    conta: Optional[str] = Field(None, max_length=30)
    tipo_conta: Optional[str] = Field(None, max_length=20)
    pix: Optional[str] = Field(None, max_length=100)


class DiaristResponse(BaseModel):
    """Schema de resposta de Diarista."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    ativo: bool = True

    nome: str
    cpf: str
    rg: Optional[str] = None
    data_nascimento: Optional[date] = None

    telefone: Optional[str] = None
    telefone_emergencia: Optional[str] = None
    email: Optional[str] = None
    foto_url: Optional[str] = None

    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None

    tipos_servico: List[str] = []
    especialidades: List[str] = []
    experiencia_anos: int = 0
    referencias: dict = {}
    documentos: dict = {}

    dias_disponiveis: List[str] = []
    hora_inicio_disponivel: Optional[time] = None
    hora_fim_disponivel: Optional[time] = None
    aceita_hora_extra: bool = True

    valor_hora: Optional[Decimal] = None
    valor_diaria: Decimal
    valor_hora_extra: Optional[Decimal] = None

    banco: Optional[str] = None
    agencia: Optional[str] = None
    conta: Optional[str] = None
    tipo_conta: Optional[str] = None
    pix: Optional[str] = None

    status: str

    avaliacao_media: Decimal = Decimal("0")
    total_avaliacoes: int = 0
    total_servicos: int = 0


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
    """Schema base de Agenda. Campos alinhados com tabela diarist_schedules."""

    diarist_id: UUID
    assignment_id: Optional[UUID] = None
    condominio_id: Optional[UUID] = None
    unidade_id: Optional[UUID] = None
    data_trabalho: date
    hora_inicio: Optional[time] = time(8, 0)
    hora_fim: Optional[time] = time(17, 0)
    valor_previsto: Optional[Decimal] = Field(None, ge=0)
    tarefas: Optional[List[str]] = Field(default_factory=list)
    observacoes: Optional[str] = None


class DiaristScheduleCreate(DiaristScheduleBase):
    """Schema de criacao de Agenda."""

    condominio_id: UUID


class DiaristScheduleUpdate(BaseModel):
    """Schema de atualizacao de Agenda."""

    hora_inicio: Optional[time] = None
    hora_fim: Optional[time] = None

    servico_descricao: Optional[str] = None
    local_servico: Optional[str] = Field(None, max_length=200)
    tarefas: Optional[List[str]] = None

    valor_base: Optional[Decimal] = Field(None, ge=0)
    valor_adicional: Optional[Decimal] = Field(None, ge=0)
    valor_desconto: Optional[Decimal] = Field(None, ge=0)
    observacoes: Optional[str] = None


class DiaristScheduleResponse(BaseModel):
    """Schema de resposta de Agenda.

    Alinhado com colunas reais: data_trabalho, hora_inicio, hora_fim,
    checkin_real, checkout_real, valor_previsto, valor_final.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    condominio_id: UUID
    diarist_id: UUID
    assignment_id: Optional[UUID] = None

    # Campos reais do banco
    data_trabalho: date
    hora_inicio: Optional[time] = None
    hora_fim: Optional[time] = None

    checkin_real: Optional[datetime] = None
    checkout_real: Optional[datetime] = None

    status: str

    # Financeiro
    valor_previsto: Optional[Decimal] = None
    valor_final: Optional[Decimal] = None

    # Tarefas
    tarefas: Optional[List[str]] = []
    observacoes: Optional[str] = None

    created_at: datetime
    updated_at: Optional[datetime] = None


class CheckinRequest(BaseModel):
    """Schema de check-in."""

    schedule_id: UUID
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    foto_url: Optional[str] = Field(None, max_length=500)


class CheckoutRequest(BaseModel):
    """Schema de check-out."""

    schedule_id: UUID
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


# === Batch Schedule Schemas ===


class BatchScheduleItem(BaseModel):
    """Item individual para escala em lote."""

    diarist_id: UUID
    horario_inicio: str = Field(default="08:00", max_length=5)
    horario_fim: str = Field(default="17:00", max_length=5)
    servico_tipo: str = Field(default="limpeza", max_length=50)
    servico_descricao: Optional[str] = None
    local_servico: Optional[str] = Field(None, max_length=200)
    observacoes: Optional[str] = None


class BatchScheduleCreate(BaseModel):
    """Schema para criacao de escala em lote."""

    condominio_id: UUID
    data: date
    items: List[BatchScheduleItem] = Field(..., min_length=1)


class BatchScheduleResponse(BaseModel):
    """Schema de resposta de escala em lote."""

    total_criados: int = 0
    total_erros: int = 0
    erros: List[str] = []
    schedules: List[DiaristScheduleResponse] = []


# === Payroll (Fechamento de Folha) Schemas ===


class PayrollDiaristItem(BaseModel):
    """Item de diarista no relatorio de folha."""

    model_config = ConfigDict(from_attributes=True)

    diarist_id: str
    diarist_nome: str
    cpf: str
    quantidade_diarias: int = 0
    total_horas: Decimal = Decimal("0")
    valor_diaria: Decimal = Decimal("0")
    valor_bruto: Decimal = Decimal("0")
    inss_retido: Decimal = Decimal("0")
    valor_liquido: Decimal = Decimal("0")
    pix: Optional[str] = None
    banco: Optional[str] = None
    agencia: Optional[str] = None
    conta: Optional[str] = None


class PayrollReportResponse(BaseModel):
    """Schema de resposta do relatorio de folha."""

    competencia: str  # YYYY-MM
    periodo_inicio: date
    periodo_fim: date
    total_diaristas: int = 0
    total_diarias: int = 0
    valor_bruto_total: Decimal = Decimal("0")
    inss_total: Decimal = Decimal("0")
    valor_liquido_total: Decimal = Decimal("0")
    items: List[PayrollDiaristItem] = []


class PayrollGenerateRequest(BaseModel):
    """Schema para gerar pagamentos do fechamento."""

    condominio_id: UUID
    competencia: str = Field(..., min_length=7, max_length=7)  # YYYY-MM
    diarist_ids: Optional[List[UUID]] = None  # filtro opcional
    forma_pagamento: Optional[str] = Field(None, max_length=30)
