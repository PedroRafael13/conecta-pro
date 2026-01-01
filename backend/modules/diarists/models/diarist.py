"""Models de Diaristas."""

from datetime import datetime, date, time
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Date,
    Time,
    ForeignKey,
    Text,
    Integer,
    Numeric,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship

from core.models.base import Base


class DiaristType(str, Enum):
    """Tipos de diarista."""

    LIMPEZA = "limpeza"
    FAXINA = "faxina"
    JARDINAGEM = "jardinagem"
    MANUTENCAO = "manutencao"
    COZINHA = "cozinha"
    PASSADEIRA = "passadeira"
    CUIDADOR = "cuidador"
    BABA = "baba"
    MOTORISTA = "motorista"
    OUTRO = "outro"


class DiaristStatus(str, Enum):
    """Status do diarista."""

    ATIVO = "ativo"
    INATIVO = "inativo"
    SUSPENSO = "suspenso"
    BLOQUEADO = "bloqueado"
    FERIAS = "ferias"
    AFASTADO = "afastado"
    DESLIGADO = "desligado"


class DocumentType(str, Enum):
    """Tipos de documento."""

    CPF = "cpf"
    RG = "rg"
    CNH = "cnh"
    CTPS = "ctps"
    PIS = "pis"
    TITULO_ELEITOR = "titulo_eleitor"
    RESERVISTA = "reservista"
    PASSAPORTE = "passaporte"


class AssignmentType(str, Enum):
    """Tipos de alocacao."""

    AVULSO = "avulso"
    RECORRENTE = "recorrente"
    TEMPORARIO = "temporario"
    SUBSTITUICAO = "substituicao"
    EMERGENCIAL = "emergencial"


class AssignmentStatus(str, Enum):
    """Status da alocacao."""

    RASCUNHO = "rascunho"
    AGENDADO = "agendado"
    CONFIRMADO = "confirmado"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"
    SUSPENSO = "suspenso"
    EXPIRADO = "expirado"


class RecurrenceType(str, Enum):
    """Tipos de recorrencia."""

    DIARIA = "diaria"
    SEMANAL = "semanal"
    QUINZENAL = "quinzenal"
    MENSAL = "mensal"
    CUSTOMIZADA = "customizada"
    NENHUMA = "nenhuma"


class ScheduleStatus(str, Enum):
    """Status da agenda."""

    AGENDADO = "agendado"
    CONFIRMADO = "confirmado"
    EM_ANDAMENTO = "em_andamento"
    CONCLUIDO = "concluido"
    FALTA = "falta"
    ATRASO = "atraso"
    CANCELADO = "cancelado"
    REAGENDADO = "reagendado"


class PaymentStatus(str, Enum):
    """Status do pagamento."""

    PENDENTE = "pendente"
    APROVADO = "aprovado"
    PAGO = "pago"
    CANCELADO = "cancelado"
    ESTORNADO = "estornado"
    PARCIAL = "parcial"


class PaymentMethod(str, Enum):
    """Metodos de pagamento."""

    DINHEIRO = "dinheiro"
    PIX = "pix"
    TRANSFERENCIA = "transferencia"
    DEPOSITO = "deposito"
    CHEQUE = "cheque"
    CARTAO = "cartao"


class Weekday(str, Enum):
    """Dias da semana."""

    SEGUNDA = "segunda"
    TERCA = "terca"
    QUARTA = "quarta"
    QUINTA = "quinta"
    SEXTA = "sexta"
    SABADO = "sabado"
    DOMINGO = "domingo"


class Diarist(Base):
    """Model de Diarista."""

    __tablename__ = "diarists"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )

    # Dados pessoais
    codigo = Column(String(50), nullable=False, index=True)
    nome = Column(String(200), nullable=False)
    nome_social = Column(String(200))
    cpf = Column(String(14), nullable=False, index=True)
    rg = Column(String(20))
    data_nascimento = Column(Date)
    genero = Column(String(20))
    nacionalidade = Column(String(50), default="Brasileira")
    estado_civil = Column(String(30))

    # Contato
    email = Column(String(255))
    telefone = Column(String(20))
    celular = Column(String(20))
    whatsapp = Column(String(20))
    contato_emergencia = Column(String(200))
    telefone_emergencia = Column(String(20))

    # Endereco
    cep = Column(String(10))
    logradouro = Column(String(255))
    numero = Column(String(20))
    complemento = Column(String(100))
    bairro = Column(String(100))
    cidade = Column(String(100))
    estado = Column(String(2))

    # Profissional
    tipo = Column(String(50), nullable=False, default=DiaristType.LIMPEZA.value)
    especialidades = Column(JSONB, default=list)
    experiencia_anos = Column(Integer, default=0)
    certificacoes = Column(JSONB, default=list)
    referencias = Column(JSONB, default=list)

    # Disponibilidade
    dias_disponiveis = Column(JSONB, default=list)  # Lista de Weekday
    horario_inicio = Column(Time, default=time(8, 0))
    horario_fim = Column(Time, default=time(17, 0))
    carga_horaria_max = Column(Integer, default=8)
    aceita_hora_extra = Column(Boolean, default=True)
    distancia_max_km = Column(Integer, default=30)
    regioes_atendimento = Column(JSONB, default=list)

    # Financeiro
    valor_diaria = Column(Numeric(10, 2), nullable=False, default=150.00)
    valor_hora_extra = Column(Numeric(10, 2), default=25.00)
    valor_adicional_noturno = Column(Numeric(10, 2), default=30.00)
    valor_adicional_feriado = Column(Numeric(10, 2), default=50.00)
    forma_pagamento_preferida = Column(
        String(30), default=PaymentMethod.PIX.value
    )

    # Dados bancarios
    banco = Column(String(100))
    agencia = Column(String(20))
    conta = Column(String(30))
    tipo_conta = Column(String(20))
    pix_chave = Column(String(100))
    pix_tipo = Column(String(20))

    # Documentos
    documentos = Column(JSONB, default=list)
    foto_url = Column(String(500))
    contrato_url = Column(String(500))
    exame_admissional_url = Column(String(500))
    data_exame_admissional = Column(Date)

    # Status
    status = Column(
        String(30), nullable=False, default=DiaristStatus.ATIVO.value, index=True
    )
    motivo_status = Column(Text)
    data_admissao = Column(Date, default=date.today)
    data_desligamento = Column(Date)
    motivo_desligamento = Column(Text)

    # Bloqueio
    is_blocked = Column(Boolean, default=False)
    blocked_reason = Column(Text)
    blocked_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    blocked_at = Column(DateTime)

    # Metricas
    total_diarias = Column(Integer, default=0)
    total_horas = Column(Numeric(10, 2), default=0)
    total_recebido = Column(Numeric(12, 2), default=0)
    media_avaliacao = Column(Numeric(3, 2), default=0)
    total_avaliacoes = Column(Integer, default=0)
    taxa_comparecimento = Column(Numeric(5, 2), default=100)
    taxa_pontualidade = Column(Numeric(5, 2), default=100)
    ultima_diaria = Column(Date)
    proxima_diaria = Column(Date)

    # IA
    score_confiabilidade = Column(Numeric(5, 2), default=50)
    score_qualidade = Column(Numeric(5, 2), default=50)
    perfil_ia = Column(JSONB, default=dict)
    recomendacoes_ia = Column(JSONB, default=list)

    # Metadata
    tags = Column(JSONB, default=list)
    observacoes = Column(Text)
    metadata = Column(JSONB, default=dict)

    # Auditoria
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    assignments = relationship("DiaristAssignment", back_populates="diarist")
    schedules = relationship("DiaristSchedule", back_populates="diarist")
    payments = relationship("DiaristPayment", back_populates="diarist")
    evaluations = relationship("DiaristEvaluation", back_populates="diarist")

    __table_args__ = (
        Index("ix_diarists_cpf_condominio", "cpf", "condominio_id", unique=True),
        Index("ix_diarists_codigo_condominio", "codigo", "condominio_id", unique=True),
    )

    @property
    def is_ativo(self) -> bool:
        """Verifica se diarista esta ativo."""
        return self.status == DiaristStatus.ATIVO.value and not self.is_blocked

    @property
    def is_disponivel(self) -> bool:
        """Verifica se diarista esta disponivel."""
        return self.is_ativo and self.status not in [
            DiaristStatus.FERIAS.value,
            DiaristStatus.AFASTADO.value,
        ]

    @property
    def idade(self) -> Optional[int]:
        """Calcula idade."""
        if not self.data_nascimento:
            return None
        today = date.today()
        return (
            today.year
            - self.data_nascimento.year
            - (
                (today.month, today.day)
                < (self.data_nascimento.month, self.data_nascimento.day)
            )
        )

    @property
    def endereco_completo(self) -> str:
        """Retorna endereco completo."""
        parts = []
        if self.logradouro:
            parts.append(self.logradouro)
        if self.numero:
            parts.append(self.numero)
        if self.complemento:
            parts.append(self.complemento)
        if self.bairro:
            parts.append(self.bairro)
        if self.cidade:
            parts.append(self.cidade)
        if self.estado:
            parts.append(self.estado)
        return ", ".join(parts)

    def ativar(self) -> None:
        """Ativa diarista."""
        self.status = DiaristStatus.ATIVO.value
        self.is_blocked = False
        self.blocked_reason = None
        self.blocked_by = None
        self.blocked_at = None

    def inativar(self, motivo: Optional[str] = None) -> None:
        """Inativa diarista."""
        self.status = DiaristStatus.INATIVO.value
        self.motivo_status = motivo

    def suspender(self, motivo: str) -> None:
        """Suspende diarista."""
        self.status = DiaristStatus.SUSPENSO.value
        self.motivo_status = motivo

    def bloquear(self, motivo: str, blocked_by: str) -> None:
        """Bloqueia diarista."""
        self.is_blocked = True
        self.blocked_reason = motivo
        self.blocked_by = UUID(blocked_by)
        self.blocked_at = datetime.utcnow()
        self.status = DiaristStatus.BLOQUEADO.value

    def desbloquear(self) -> None:
        """Desbloqueia diarista."""
        self.is_blocked = False
        self.blocked_reason = None
        self.blocked_by = None
        self.blocked_at = None
        self.status = DiaristStatus.ATIVO.value

    def iniciar_ferias(self) -> None:
        """Inicia periodo de ferias."""
        self.status = DiaristStatus.FERIAS.value

    def afastar(self, motivo: str) -> None:
        """Afasta diarista."""
        self.status = DiaristStatus.AFASTADO.value
        self.motivo_status = motivo

    def desligar(self, motivo: str) -> None:
        """Desliga diarista."""
        self.status = DiaristStatus.DESLIGADO.value
        self.motivo_desligamento = motivo
        self.data_desligamento = date.today()

    def atualizar_metricas(
        self,
        diarias: int = 0,
        horas: float = 0,
        valor: float = 0,
    ) -> None:
        """Atualiza metricas."""
        self.total_diarias += diarias
        self.total_horas = float(self.total_horas or 0) + horas
        self.total_recebido = float(self.total_recebido or 0) + valor
        self.ultima_diaria = date.today()

    def atualizar_avaliacao(self, nota: float) -> None:
        """Atualiza media de avaliacao."""
        total = self.total_avaliacoes or 0
        media = float(self.media_avaliacao or 0)
        nova_media = ((media * total) + nota) / (total + 1)
        self.media_avaliacao = round(nova_media, 2)
        self.total_avaliacoes = total + 1


class DiaristAssignment(Base):
    """Model de Alocacao de Diarista."""

    __tablename__ = "diarist_assignments"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )
    diarist_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("diarists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Tipo e status
    tipo = Column(
        String(30), nullable=False, default=AssignmentType.AVULSO.value, index=True
    )
    status = Column(
        String(30), nullable=False, default=AssignmentStatus.RASCUNHO.value, index=True
    )

    # Servico
    servico_tipo = Column(String(50), nullable=False)
    servico_descricao = Column(Text)
    local_servico = Column(String(200))
    unidade_id = Column(PG_UUID(as_uuid=True))
    area_comum = Column(String(100))

    # Periodo
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date)
    horario_inicio = Column(Time, default=time(8, 0))
    horario_fim = Column(Time, default=time(17, 0))
    carga_horaria = Column(Integer, default=8)

    # Recorrencia
    recorrencia = Column(
        String(30), nullable=False, default=RecurrenceType.NENHUMA.value
    )
    dias_semana = Column(JSONB, default=list)
    intervalo_dias = Column(Integer)
    total_ocorrencias = Column(Integer)
    ocorrencias_realizadas = Column(Integer, default=0)

    # Financeiro
    valor_acordado = Column(Numeric(10, 2), nullable=False)
    valor_adicional = Column(Numeric(10, 2), default=0)
    desconto = Column(Numeric(10, 2), default=0)
    valor_total = Column(Numeric(10, 2))
    forma_pagamento = Column(String(30))

    # Responsavel
    contratante_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    contratante_nome = Column(String(200))
    aprovador_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    aprovado_at = Column(DateTime)

    # Substituicao
    substitui_assignment_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("diarist_assignments.id")
    )
    motivo_substituicao = Column(Text)

    # Cancelamento
    cancelado_por = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    cancelado_at = Column(DateTime)
    motivo_cancelamento = Column(Text)

    # Observacoes
    instrucoes = Column(Text)
    observacoes = Column(Text)
    materiais_necessarios = Column(JSONB, default=list)

    # Metadata
    metadata = Column(JSONB, default=dict)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    diarist = relationship("Diarist", back_populates="assignments")
    schedules = relationship("DiaristSchedule", back_populates="assignment")
    payments = relationship("DiaristPayment", back_populates="assignment")

    __table_args__ = (
        Index("ix_diarist_assignments_periodo", "data_inicio", "data_fim"),
    )

    @property
    def is_ativo(self) -> bool:
        """Verifica se alocacao esta ativa."""
        return self.status in [
            AssignmentStatus.AGENDADO.value,
            AssignmentStatus.CONFIRMADO.value,
            AssignmentStatus.EM_ANDAMENTO.value,
        ]

    @property
    def is_recorrente(self) -> bool:
        """Verifica se e recorrente."""
        return self.recorrencia != RecurrenceType.NENHUMA.value

    @property
    def dias_restantes(self) -> Optional[int]:
        """Calcula dias restantes."""
        if not self.data_fim:
            return None
        return (self.data_fim - date.today()).days

    def confirmar(self) -> None:
        """Confirma alocacao."""
        self.status = AssignmentStatus.CONFIRMADO.value

    def iniciar(self) -> None:
        """Inicia alocacao."""
        self.status = AssignmentStatus.EM_ANDAMENTO.value

    def concluir(self) -> None:
        """Conclui alocacao."""
        self.status = AssignmentStatus.CONCLUIDO.value

    def cancelar(self, motivo: str, cancelado_por: str) -> None:
        """Cancela alocacao."""
        self.status = AssignmentStatus.CANCELADO.value
        self.motivo_cancelamento = motivo
        self.cancelado_por = UUID(cancelado_por)
        self.cancelado_at = datetime.utcnow()

    def suspender(self) -> None:
        """Suspende alocacao."""
        self.status = AssignmentStatus.SUSPENSO.value

    def aprovar(self, aprovador_id: str) -> None:
        """Aprova alocacao."""
        self.aprovador_id = UUID(aprovador_id)
        self.aprovado_at = datetime.utcnow()
        self.status = AssignmentStatus.AGENDADO.value

    def calcular_valor_total(self) -> None:
        """Calcula valor total."""
        base = float(self.valor_acordado or 0)
        adicional = float(self.valor_adicional or 0)
        desconto = float(self.desconto or 0)
        self.valor_total = base + adicional - desconto


class DiaristSchedule(Base):
    """Model de Agenda de Diarista."""

    __tablename__ = "diarist_schedules"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )
    diarist_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("diarists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assignment_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("diarist_assignments.id", ondelete="CASCADE"),
        index=True,
    )

    # Data e horario
    data = Column(Date, nullable=False, index=True)
    horario_inicio_previsto = Column(Time, nullable=False)
    horario_fim_previsto = Column(Time, nullable=False)
    carga_horaria_prevista = Column(Integer, default=8)

    # Check-in/out
    checkin_at = Column(DateTime)
    checkout_at = Column(DateTime)
    checkin_latitude = Column(Numeric(10, 8))
    checkin_longitude = Column(Numeric(11, 8))
    checkout_latitude = Column(Numeric(10, 8))
    checkout_longitude = Column(Numeric(11, 8))
    checkin_foto_url = Column(String(500))
    checkout_foto_url = Column(String(500))

    # Horas
    horas_trabalhadas = Column(Numeric(5, 2), default=0)
    horas_extras = Column(Numeric(5, 2), default=0)
    horas_noturnas = Column(Numeric(5, 2), default=0)
    intervalo_minutos = Column(Integer, default=60)

    # Status
    status = Column(
        String(30), nullable=False, default=ScheduleStatus.AGENDADO.value, index=True
    )
    motivo_status = Column(Text)
    is_feriado = Column(Boolean, default=False)
    is_fim_semana = Column(Boolean, default=False)

    # Servico
    servico_tipo = Column(String(50))
    servico_descricao = Column(Text)
    local_servico = Column(String(200))
    tarefas = Column(JSONB, default=list)
    tarefas_concluidas = Column(JSONB, default=list)

    # Avaliacao rapida
    avaliacao_nota = Column(Integer)  # 1-5
    avaliacao_comentario = Column(Text)
    avaliado_por = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    avaliado_at = Column(DateTime)

    # Ocorrencias
    ocorrencias = Column(JSONB, default=list)
    materiais_usados = Column(JSONB, default=list)

    # Financeiro
    valor_base = Column(Numeric(10, 2))
    valor_hora_extra = Column(Numeric(10, 2), default=0)
    valor_adicional = Column(Numeric(10, 2), default=0)
    valor_desconto = Column(Numeric(10, 2), default=0)
    valor_total = Column(Numeric(10, 2))

    # Confirmacao
    confirmado_por = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    confirmado_at = Column(DateTime)

    # Reagendamento
    reagendado_de = Column(PG_UUID(as_uuid=True), ForeignKey("diarist_schedules.id"))
    reagendado_para = Column(Date)
    motivo_reagendamento = Column(Text)

    # Metadata
    observacoes = Column(Text)
    metadata = Column(JSONB, default=dict)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    diarist = relationship("Diarist", back_populates="schedules")
    assignment = relationship("DiaristAssignment", back_populates="schedules")

    __table_args__ = (
        Index("ix_diarist_schedules_data_diarist", "data", "diarist_id"),
    )

    @property
    def is_confirmado(self) -> bool:
        """Verifica se esta confirmado."""
        return self.status == ScheduleStatus.CONFIRMADO.value

    @property
    def is_concluido(self) -> bool:
        """Verifica se esta concluido."""
        return self.status == ScheduleStatus.CONCLUIDO.value

    @property
    def teve_checkin(self) -> bool:
        """Verifica se teve check-in."""
        return self.checkin_at is not None

    @property
    def teve_checkout(self) -> bool:
        """Verifica se teve check-out."""
        return self.checkout_at is not None

    @property
    def duracao_minutos(self) -> Optional[int]:
        """Calcula duracao em minutos."""
        if not self.checkin_at or not self.checkout_at:
            return None
        delta = self.checkout_at - self.checkin_at
        return int(delta.total_seconds() / 60)

    def confirmar(self) -> None:
        """Confirma agenda."""
        self.status = ScheduleStatus.CONFIRMADO.value

    def fazer_checkin(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        foto_url: Optional[str] = None,
    ) -> None:
        """Registra check-in."""
        self.checkin_at = datetime.utcnow()
        self.checkin_latitude = latitude
        self.checkin_longitude = longitude
        self.checkin_foto_url = foto_url
        self.status = ScheduleStatus.EM_ANDAMENTO.value

    def fazer_checkout(
        self,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        foto_url: Optional[str] = None,
    ) -> None:
        """Registra check-out."""
        self.checkout_at = datetime.utcnow()
        self.checkout_latitude = latitude
        self.checkout_longitude = longitude
        self.checkout_foto_url = foto_url
        self.calcular_horas()
        self.status = ScheduleStatus.CONCLUIDO.value

    def calcular_horas(self) -> None:
        """Calcula horas trabalhadas."""
        if not self.checkin_at or not self.checkout_at:
            return

        delta = self.checkout_at - self.checkin_at
        total_minutos = delta.total_seconds() / 60
        total_minutos -= self.intervalo_minutos or 60

        horas = total_minutos / 60
        carga = self.carga_horaria_prevista or 8

        self.horas_trabalhadas = min(horas, carga)
        self.horas_extras = max(0, horas - carga)

    def marcar_falta(self, motivo: Optional[str] = None) -> None:
        """Marca como falta."""
        self.status = ScheduleStatus.FALTA.value
        self.motivo_status = motivo

    def marcar_atraso(self) -> None:
        """Marca como atraso."""
        self.status = ScheduleStatus.ATRASO.value

    def cancelar(self, motivo: Optional[str] = None) -> None:
        """Cancela agenda."""
        self.status = ScheduleStatus.CANCELADO.value
        self.motivo_status = motivo

    def reagendar(self, nova_data: date, motivo: Optional[str] = None) -> None:
        """Reagenda para outra data."""
        self.reagendado_para = nova_data
        self.motivo_reagendamento = motivo
        self.status = ScheduleStatus.REAGENDADO.value

    def avaliar(self, nota: int, comentario: str, avaliador_id: str) -> None:
        """Registra avaliacao."""
        self.avaliacao_nota = nota
        self.avaliacao_comentario = comentario
        self.avaliado_por = UUID(avaliador_id)
        self.avaliado_at = datetime.utcnow()

    def calcular_valor(self) -> None:
        """Calcula valor total."""
        base = float(self.valor_base or 0)
        extra = float(self.valor_hora_extra or 0) * float(self.horas_extras or 0)
        adicional = float(self.valor_adicional or 0)
        desconto = float(self.valor_desconto or 0)
        self.valor_total = base + extra + adicional - desconto


class DiaristPayment(Base):
    """Model de Pagamento de Diarista."""

    __tablename__ = "diarist_payments"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )
    diarist_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("diarists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assignment_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("diarist_assignments.id", ondelete="SET NULL"),
        index=True,
    )

    # Periodo
    periodo_inicio = Column(Date, nullable=False)
    periodo_fim = Column(Date, nullable=False)
    competencia = Column(String(7))  # YYYY-MM

    # Valores
    valor_diarias = Column(Numeric(10, 2), nullable=False, default=0)
    quantidade_diarias = Column(Integer, default=0)
    valor_horas_extras = Column(Numeric(10, 2), default=0)
    quantidade_horas_extras = Column(Numeric(5, 2), default=0)
    valor_adicional = Column(Numeric(10, 2), default=0)
    descricao_adicional = Column(Text)
    valor_desconto = Column(Numeric(10, 2), default=0)
    descricao_desconto = Column(Text)
    valor_bruto = Column(Numeric(10, 2))
    valor_liquido = Column(Numeric(10, 2))

    # Impostos/Retencoes
    inss_retido = Column(Numeric(10, 2), default=0)
    iss_retido = Column(Numeric(10, 2), default=0)
    irrf_retido = Column(Numeric(10, 2), default=0)
    outras_retencoes = Column(Numeric(10, 2), default=0)

    # Pagamento
    status = Column(
        String(30), nullable=False, default=PaymentStatus.PENDENTE.value, index=True
    )
    forma_pagamento = Column(String(30))
    data_vencimento = Column(Date)
    data_pagamento = Column(Date)
    comprovante_url = Column(String(500))
    numero_documento = Column(String(100))
    observacoes_pagamento = Column(Text)

    # Aprovacao
    aprovado_por = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    aprovado_at = Column(DateTime)
    motivo_rejeicao = Column(Text)

    # Estorno
    estornado_por = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    estornado_at = Column(DateTime)
    motivo_estorno = Column(Text)

    # Schedules incluidos
    schedules_ids = Column(JSONB, default=list)

    # Metadata
    observacoes = Column(Text)
    metadata = Column(JSONB, default=dict)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    diarist = relationship("Diarist", back_populates="payments")
    assignment = relationship("DiaristAssignment", back_populates="payments")

    @property
    def is_pago(self) -> bool:
        """Verifica se esta pago."""
        return self.status == PaymentStatus.PAGO.value

    @property
    def is_vencido(self) -> bool:
        """Verifica se esta vencido."""
        if not self.data_vencimento:
            return False
        return (
            date.today() > self.data_vencimento
            and self.status == PaymentStatus.PENDENTE.value
        )

    @property
    def total_retencoes(self) -> float:
        """Calcula total de retencoes."""
        return (
            float(self.inss_retido or 0)
            + float(self.iss_retido or 0)
            + float(self.irrf_retido or 0)
            + float(self.outras_retencoes or 0)
        )

    def calcular_valores(self) -> None:
        """Calcula valores bruto e liquido."""
        diarias = float(self.valor_diarias or 0)
        extras = float(self.valor_horas_extras or 0)
        adicional = float(self.valor_adicional or 0)
        desconto = float(self.valor_desconto or 0)

        self.valor_bruto = diarias + extras + adicional - desconto
        self.valor_liquido = self.valor_bruto - self.total_retencoes

    def aprovar(self, aprovador_id: str) -> None:
        """Aprova pagamento."""
        self.status = PaymentStatus.APROVADO.value
        self.aprovado_por = UUID(aprovador_id)
        self.aprovado_at = datetime.utcnow()

    def rejeitar(self, motivo: str) -> None:
        """Rejeita pagamento."""
        self.status = PaymentStatus.CANCELADO.value
        self.motivo_rejeicao = motivo

    def pagar(
        self,
        data_pagamento: Optional[date] = None,
        comprovante_url: Optional[str] = None,
    ) -> None:
        """Registra pagamento."""
        self.status = PaymentStatus.PAGO.value
        self.data_pagamento = data_pagamento or date.today()
        if comprovante_url:
            self.comprovante_url = comprovante_url

    def estornar(self, motivo: str, estornado_por: str) -> None:
        """Estorna pagamento."""
        self.status = PaymentStatus.ESTORNADO.value
        self.motivo_estorno = motivo
        self.estornado_por = UUID(estornado_por)
        self.estornado_at = datetime.utcnow()


class DiaristEvaluation(Base):
    """Model de Avaliacao de Diarista."""

    __tablename__ = "diarist_evaluations"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    condominio_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("condominios.id"),
        nullable=False,
        index=True,
    )
    diarist_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("diarists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    schedule_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("diarist_schedules.id", ondelete="SET NULL"),
        index=True,
    )

    # Avaliador
    avaliador_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    avaliador_nome = Column(String(200))
    avaliador_tipo = Column(String(50))  # morador, sindico, administrador

    # Notas (1-5)
    nota_geral = Column(Integer, nullable=False)
    nota_pontualidade = Column(Integer)
    nota_qualidade = Column(Integer)
    nota_profissionalismo = Column(Integer)
    nota_comunicacao = Column(Integer)
    nota_cuidado = Column(Integer)

    # Comentarios
    comentario = Column(Text)
    pontos_positivos = Column(JSONB, default=list)
    pontos_melhorar = Column(JSONB, default=list)

    # Recomendacao
    recomendaria = Column(Boolean, default=True)
    contrataria_novamente = Column(Boolean, default=True)

    # Servico avaliado
    servico_tipo = Column(String(50))
    data_servico = Column(Date)

    # Status
    is_publicada = Column(Boolean, default=True)
    is_anonima = Column(Boolean, default=False)

    # Resposta do diarista
    resposta = Column(Text)
    resposta_at = Column(DateTime)

    # Metadata
    metadata = Column(JSONB, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    diarist = relationship("Diarist", back_populates="evaluations")

    @property
    def media_notas(self) -> float:
        """Calcula media das notas."""
        notas = [
            n
            for n in [
                self.nota_geral,
                self.nota_pontualidade,
                self.nota_qualidade,
                self.nota_profissionalismo,
                self.nota_comunicacao,
                self.nota_cuidado,
            ]
            if n is not None
        ]
        if not notas:
            return 0.0
        return round(sum(notas) / len(notas), 2)

    def responder(self, resposta: str) -> None:
        """Registra resposta do diarista."""
        self.resposta = resposta
        self.resposta_at = datetime.utcnow()

    def ocultar(self) -> None:
        """Oculta avaliacao."""
        self.is_publicada = False

    def publicar(self) -> None:
        """Publica avaliacao."""
        self.is_publicada = True
