"""Modelo de Ocorrência."""

import enum
import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class OccurrenceType(str, enum.Enum):
    """Tipos de ocorrência."""

    RECLAMACAO = "reclamacao"
    SUGESTAO = "sugestao"
    ELOGIO = "elogio"
    INCIDENTE = "incidente"
    DENUNCIA = "denuncia"
    SOLICITACAO = "solicitacao"
    INFORMATIVO = "informativo"
    MANUTENCAO = "manutencao"
    SEGURANCA = "seguranca"
    BARULHO = "barulho"
    ANIMAL = "animal"
    VEICULO = "veiculo"
    AREA_COMUM = "area_comum"
    OUTRO = "outro"


class OccurrenceStatus(str, enum.Enum):
    """Status da ocorrência."""

    ABERTA = "aberta"
    EM_ANALISE = "em_analise"
    EM_ANDAMENTO = "em_andamento"
    AGUARDANDO_RESPOSTA = "aguardando_resposta"
    AGUARDANDO_TERCEIRO = "aguardando_terceiro"
    RESOLVIDA = "resolvida"
    ARQUIVADA = "arquivada"
    CANCELADA = "cancelada"
    REABERTA = "reaberta"


class OccurrencePriority(str, enum.Enum):
    """Prioridade da ocorrência."""

    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"
    CRITICA = "critica"


class ReporterType(str, enum.Enum):
    """Tipo de reportador."""

    MORADOR = "morador"
    FUNCIONARIO = "funcionario"
    VISITANTE = "visitante"
    PORTEIRO = "porteiro"
    SINDICO = "sindico"
    ADMINISTRADORA = "administradora"
    ANONIMO = "anonimo"
    SISTEMA = "sistema"


class Occurrence(Base):
    """Modelo de Ocorrência."""

    __tablename__ = "occurrences"

    # Identificação
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    occurrence_code: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False
    )

    # Classificação
    occurrence_type: Mapped[OccurrenceType] = mapped_column(
        Enum(OccurrenceType), nullable=False
    )
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("occurrence_categories.id"), nullable=True
    )
    priority: Mapped[OccurrencePriority] = mapped_column(
        Enum(OccurrencePriority), default=OccurrencePriority.MEDIA
    )
    status: Mapped[OccurrenceStatus] = mapped_column(
        Enum(OccurrenceStatus), default=OccurrenceStatus.ABERTA
    )

    # Conteúdo
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[Optional[list]] = mapped_column(JSONB, default=list)

    # Condomínio/Local
    condominium_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    condominium_name: Mapped[Optional[str]] = mapped_column(String(200))
    unit_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    unit_number: Mapped[Optional[str]] = mapped_column(String(20))
    block: Mapped[Optional[str]] = mapped_column(String(50))
    location: Mapped[Optional[str]] = mapped_column(String(200))
    location_details: Mapped[Optional[str]] = mapped_column(Text)

    # Reportador
    reporter_type: Mapped[ReporterType] = mapped_column(
        Enum(ReporterType), default=ReporterType.MORADOR
    )
    reporter_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    reporter_name: Mapped[Optional[str]] = mapped_column(String(200))
    reporter_email: Mapped[Optional[str]] = mapped_column(String(200))
    reporter_phone: Mapped[Optional[str]] = mapped_column(String(20))
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False)

    # Responsável
    assigned_to_id: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    assigned_to_name: Mapped[Optional[str]] = mapped_column(String(200))
    assigned_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    assigned_by_id: Mapped[Optional[str]] = mapped_column(String(50))
    assigned_by_name: Mapped[Optional[str]] = mapped_column(String(200))

    # SLA
    sla_response_hours: Mapped[Optional[int]] = mapped_column(Integer)
    sla_resolution_hours: Mapped[Optional[int]] = mapped_column(Integer)
    sla_response_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime)
    sla_resolution_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime)
    sla_response_met: Mapped[Optional[bool]] = mapped_column(Boolean)
    sla_resolution_met: Mapped[Optional[bool]] = mapped_column(Boolean)
    first_response_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Resolução
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    resolved_by_id: Mapped[Optional[str]] = mapped_column(String(50))
    resolved_by_name: Mapped[Optional[str]] = mapped_column(String(200))
    resolution_description: Mapped[Optional[str]] = mapped_column(Text)
    resolution_type: Mapped[Optional[str]] = mapped_column(String(50))

    # Avaliação
    satisfaction_rating: Mapped[Optional[int]] = mapped_column(Integer)
    satisfaction_comment: Mapped[Optional[str]] = mapped_column(Text)
    rated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Escalonamento
    is_escalated: Mapped[bool] = mapped_column(Boolean, default=False)
    escalated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    escalated_to_id: Mapped[Optional[str]] = mapped_column(String(50))
    escalated_to_name: Mapped[Optional[str]] = mapped_column(String(200))
    escalation_reason: Mapped[Optional[str]] = mapped_column(Text)
    escalation_level: Mapped[int] = mapped_column(Integer, default=0)

    # Recorrência
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_count: Mapped[int] = mapped_column(Integer, default=0)
    parent_occurrence_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("occurrences.id"), nullable=True
    )
    related_occurrence_ids: Mapped[Optional[list]] = mapped_column(JSONB, default=list)

    # Métricas
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    attachment_count: Mapped[int] = mapped_column(Integer, default=0)
    update_count: Mapped[int] = mapped_column(Integer, default=0)

    # IA
    ai_classification: Mapped[Optional[dict]] = mapped_column(JSONB)
    ai_priority_score: Mapped[Optional[float]] = mapped_column(Float)
    ai_sentiment: Mapped[Optional[str]] = mapped_column(String(20))
    ai_suggested_category_id: Mapped[Optional[str]] = mapped_column(String(50))
    ai_suggested_assignee_id: Mapped[Optional[str]] = mapped_column(String(50))

    # Metadados
    source: Mapped[Optional[str]] = mapped_column(String(50))
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, default=dict)

    # Histórico
    history: Mapped[Optional[list]] = mapped_column(JSONB, default=list)

    # Controle
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relacionamentos
    category: Mapped[Optional["OccurrenceCategory"]] = relationship(
        "OccurrenceCategory", back_populates="occurrences"
    )
    comments: Mapped[list["OccurrenceComment"]] = relationship(
        "OccurrenceComment", back_populates="occurrence", cascade="all, delete-orphan"
    )
    attachments: Mapped[list["OccurrenceAttachment"]] = relationship(
        "OccurrenceAttachment", back_populates="occurrence", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        """Inicializa a ocorrência."""
        super().__init__(**kwargs)
        if not self.occurrence_code:
            self.occurrence_code = self._generate_code()

    def _generate_code(self) -> str:
        """Gera código único para a ocorrência."""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        random_part = "".join(random.choices(string.digits, k=4))
        return f"OC-{timestamp}-{random_part}"

    # Métodos de Status
    def start_analysis(self, analyst_id: str = None, analyst_name: str = None) -> None:
        """Inicia análise da ocorrência."""
        self.status = OccurrenceStatus.EM_ANALISE
        if analyst_id:
            self.assigned_to_id = analyst_id
            self.assigned_to_name = analyst_name
            self.assigned_at = datetime.utcnow()
        self._add_history("status_change", "Ocorrência em análise")

    def start_progress(self) -> None:
        """Inicia andamento da ocorrência."""
        self.status = OccurrenceStatus.EM_ANDAMENTO
        self._add_history("status_change", "Ocorrência em andamento")

    def wait_response(self, reason: str = None) -> None:
        """Aguarda resposta do reportador."""
        self.status = OccurrenceStatus.AGUARDANDO_RESPOSTA
        self._add_history("status_change", f"Aguardando resposta: {reason or 'N/A'}")

    def wait_third_party(self, third_party: str = None) -> None:
        """Aguarda terceiro."""
        self.status = OccurrenceStatus.AGUARDANDO_TERCEIRO
        self._add_history("status_change", f"Aguardando terceiro: {third_party or 'N/A'}")

    def resolve(
        self,
        resolved_by_id: str,
        resolved_by_name: str,
        description: str = None,
        resolution_type: str = None,
    ) -> None:
        """Resolve a ocorrência."""
        self.status = OccurrenceStatus.RESOLVIDA
        self.resolved_at = datetime.utcnow()
        self.resolved_by_id = resolved_by_id
        self.resolved_by_name = resolved_by_name
        self.resolution_description = description
        self.resolution_type = resolution_type
        self.closed_at = datetime.utcnow()
        self._check_sla_resolution()
        self._add_history("resolved", f"Resolvida por {resolved_by_name}")

    def archive(self, reason: str = None) -> None:
        """Arquiva a ocorrência."""
        self.status = OccurrenceStatus.ARQUIVADA
        self.closed_at = datetime.utcnow()
        self._add_history("archived", f"Arquivada: {reason or 'N/A'}")

    def cancel(self, reason: str = None, cancelled_by: str = None) -> None:
        """Cancela a ocorrência."""
        self.status = OccurrenceStatus.CANCELADA
        self.closed_at = datetime.utcnow()
        self._add_history("cancelled", f"Cancelada por {cancelled_by}: {reason or 'N/A'}")

    def reopen(self, reason: str = None, reopened_by: str = None) -> None:
        """Reabre a ocorrência."""
        self.status = OccurrenceStatus.REABERTA
        self.closed_at = None
        self.resolved_at = None
        self.recurrence_count += 1
        self._add_history("reopened", f"Reaberta por {reopened_by}: {reason or 'N/A'}")

    # Métodos de Atribuição
    def assign(
        self,
        assignee_id: str,
        assignee_name: str,
        assigned_by_id: str = None,
        assigned_by_name: str = None,
    ) -> None:
        """Atribui responsável."""
        self.assigned_to_id = assignee_id
        self.assigned_to_name = assignee_name
        self.assigned_at = datetime.utcnow()
        self.assigned_by_id = assigned_by_id
        self.assigned_by_name = assigned_by_name
        self._add_history("assigned", f"Atribuída para {assignee_name}")

    def unassign(self) -> None:
        """Remove atribuição."""
        old_assignee = self.assigned_to_name
        self.assigned_to_id = None
        self.assigned_to_name = None
        self.assigned_at = None
        self._add_history("unassigned", f"Removida atribuição de {old_assignee}")

    # Métodos de Escalonamento
    def escalate(
        self, escalated_to_id: str, escalated_to_name: str, reason: str = None
    ) -> None:
        """Escalona a ocorrência."""
        self.is_escalated = True
        self.escalated_at = datetime.utcnow()
        self.escalated_to_id = escalated_to_id
        self.escalated_to_name = escalated_to_name
        self.escalation_reason = reason
        self.escalation_level += 1
        self._add_history("escalated", f"Escalonada para {escalated_to_name}: {reason or 'N/A'}")

    # Métodos de SLA
    def set_sla(self, response_hours: int, resolution_hours: int) -> None:
        """Define SLA."""
        now = datetime.utcnow()
        self.sla_response_hours = response_hours
        self.sla_resolution_hours = resolution_hours
        self.sla_response_deadline = now + timedelta(hours=response_hours)
        self.sla_resolution_deadline = now + timedelta(hours=resolution_hours)

    def register_first_response(self) -> None:
        """Registra primeira resposta."""
        if not self.first_response_at:
            self.first_response_at = datetime.utcnow()
            self._check_sla_response()

    def _check_sla_response(self) -> None:
        """Verifica SLA de resposta."""
        if self.sla_response_deadline and self.first_response_at:
            self.sla_response_met = self.first_response_at <= self.sla_response_deadline

    def _check_sla_resolution(self) -> None:
        """Verifica SLA de resolução."""
        if self.sla_resolution_deadline and self.resolved_at:
            self.sla_resolution_met = self.resolved_at <= self.sla_resolution_deadline

    # Métodos de Avaliação
    def rate(self, rating: int, comment: str = None) -> None:
        """Avalia a ocorrência."""
        if 1 <= rating <= 5:
            self.satisfaction_rating = rating
            self.satisfaction_comment = comment
            self.rated_at = datetime.utcnow()
            self._add_history("rated", f"Avaliada com nota {rating}")

    # Métodos de Contagem
    def increment_views(self) -> None:
        """Incrementa visualizações."""
        self.view_count += 1

    def increment_comments(self) -> None:
        """Incrementa comentários."""
        self.comment_count += 1

    def increment_attachments(self) -> None:
        """Incrementa anexos."""
        self.attachment_count += 1

    def increment_updates(self) -> None:
        """Incrementa atualizações."""
        self.update_count += 1

    # Métodos de Histórico
    def _add_history(self, action: str, description: str, user_id: str = None) -> None:
        """Adiciona entrada ao histórico."""
        if self.history is None:
            self.history = []
        self.history.append({
            "action": action,
            "description": description,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
        })

    # Properties
    @property
    def is_open(self) -> bool:
        """Verifica se está aberta."""
        return self.status in [
            OccurrenceStatus.ABERTA,
            OccurrenceStatus.EM_ANALISE,
            OccurrenceStatus.EM_ANDAMENTO,
            OccurrenceStatus.AGUARDANDO_RESPOSTA,
            OccurrenceStatus.AGUARDANDO_TERCEIRO,
            OccurrenceStatus.REABERTA,
        ]

    @property
    def is_closed(self) -> bool:
        """Verifica se está fechada."""
        return self.status in [
            OccurrenceStatus.RESOLVIDA,
            OccurrenceStatus.ARQUIVADA,
            OccurrenceStatus.CANCELADA,
        ]

    @property
    def is_overdue_response(self) -> bool:
        """Verifica se SLA de resposta está atrasado."""
        if not self.sla_response_deadline:
            return False
        if self.first_response_at:
            return self.first_response_at > self.sla_response_deadline
        return datetime.utcnow() > self.sla_response_deadline

    @property
    def is_overdue_resolution(self) -> bool:
        """Verifica se SLA de resolução está atrasado."""
        if not self.sla_resolution_deadline:
            return False
        if self.resolved_at:
            return self.resolved_at > self.sla_resolution_deadline
        if self.is_closed:
            return False
        return datetime.utcnow() > self.sla_resolution_deadline

    @property
    def resolution_time_hours(self) -> Optional[float]:
        """Calcula tempo de resolução em horas."""
        if not self.resolved_at:
            return None
        delta = self.resolved_at - self.created_at
        return delta.total_seconds() / 3600

    @property
    def response_time_hours(self) -> Optional[float]:
        """Calcula tempo de primeira resposta em horas."""
        if not self.first_response_at:
            return None
        delta = self.first_response_at - self.created_at
        return delta.total_seconds() / 3600

    @property
    def age_hours(self) -> float:
        """Calcula idade da ocorrência em horas."""
        end_time = self.closed_at or datetime.utcnow()
        delta = end_time - self.created_at
        return delta.total_seconds() / 3600

    @property
    def is_high_priority(self) -> bool:
        """Verifica se é alta prioridade."""
        high = [
            OccurrencePriority.ALTA,
            OccurrencePriority.URGENTE,
            OccurrencePriority.CRITICA,
        ]
        return self.priority in high
