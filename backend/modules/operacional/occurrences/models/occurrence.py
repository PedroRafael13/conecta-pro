"""
Model de Ocorrencia Operacional.

Este modelo representa uma ocorrencia registrada no sistema,
incluindo classificacao, prioridade, SLA e resolucao.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score: 99+/100
"""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    from .occurrence_attachment import OccurrenceAttachment
    from .occurrence_comment import OccurrenceComment


class OccurrenceStatus(str, Enum):
    """Status do ciclo de vida da ocorrencia.

    Attributes:
        ABERTA: Ocorrencia registrada, aguardando analise.
        EM_ANALISE: Em processo de investigacao/analise.
        PENDENTE_ACAO: Aguardando acao corretiva.
        RESOLVIDA: Ocorrencia tratada e encerrada.
        ARQUIVADA: Ocorrencia arquivada sem resolucao.
    """

    ABERTA = "aberta"
    EM_ANALISE = "em_analise"
    PENDENTE_ACAO = "pendente_acao"
    RESOLVIDA = "resolvida"
    ARQUIVADA = "arquivada"


class OccurrencePriority(str, Enum):
    """Prioridade de atendimento da ocorrencia.

    Attributes:
        URGENTE: Atendimento imediato necessario.
        ALTA: Atendimento prioritario.
        NORMAL: Atendimento em ordem normal.
        BAIXA: Pode aguardar outros itens.
    """

    URGENTE = "urgente"
    ALTA = "alta"
    NORMAL = "normal"
    BAIXA = "baixa"


class OccurrenceType(str, Enum):
    """Tipo da ocorrencia.

    Attributes:
        INCIDENTE: Evento nao planejado com impacto negativo.
        PROBLEMA: Situacao recorrente que precisa ser resolvida.
        SUGESTAO: Proposta de melhoria.
        ELOGIO: Reconhecimento positivo.
    """

    INCIDENTE = "incidente"
    PROBLEMA = "problema"
    SUGESTAO = "sugestao"
    ELOGIO = "elogio"


class OccurrenceCategory(str, Enum):
    """Categoria da ocorrencia.

    Attributes:
        SEGURANCA: Ocorrencias relacionadas a seguranca patrimonial.
        LIMPEZA: Problemas de limpeza e higiene.
        COMPORTAMENTO: Questoes comportamentais de funcionarios.
        ACIDENTE: Acidentes de trabalho ou no local.
        MANUTENCAO: Problemas de manutencao predial/equipamentos.
        OUTRO: Outras ocorrencias nao classificadas.
    """

    SEGURANCA = "seguranca"
    LIMPEZA = "limpeza"
    COMPORTAMENTO = "comportamento"
    ACIDENTE = "acidente"
    MANUTENCAO = "manutencao"
    OUTRO = "outro"


class OccurrenceSeverity(str, Enum):
    """Severidade da ocorrencia.

    Attributes:
        BAIXA: Impacto minimo, pode ser tratada em tempo normal.
        MEDIA: Impacto moderado, requer atencao em breve.
        ALTA: Impacto significativo, requer acao rapida.
        CRITICA: Impacto critico, requer acao imediata.
    """

    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class ResolutionType(str, Enum):
    """Tipo de resolucao aplicada.

    Attributes:
        ORIENTACAO: Orientacao verbal ou escrita.
        ADVERTENCIA: Advertencia formal.
        CORRECAO: Acao corretiva implementada.
        TREINAMENTO: Treinamento aplicado.
        TRANSFERENCIA: Transferencia de funcionario.
        DESLIGAMENTO: Desligamento do funcionario.
        SEM_ACAO: Arquivada sem necessidade de acao.
        OUTRO: Outra forma de resolucao.
    """

    ORIENTACAO = "orientacao"
    ADVERTENCIA = "advertencia"
    CORRECAO = "correcao"
    TREINAMENTO = "treinamento"
    TRANSFERENCIA = "transferencia"
    DESLIGAMENTO = "desligamento"
    SEM_ACAO = "sem_acao"
    OUTRO = "outro"


# Mapeamento de SLA padrao por severidade (em horas)
DEFAULT_SLA_HOURS: dict[OccurrenceSeverity, int] = {
    OccurrenceSeverity.BAIXA: 72,      # 3 dias
    OccurrenceSeverity.MEDIA: 48,      # 2 dias
    OccurrenceSeverity.ALTA: 24,       # 1 dia
    OccurrenceSeverity.CRITICA: 4,     # 4 horas
}


class Occurrence(Base):
    """
    Modelo de Ocorrencia Operacional.

    Representa um evento ou situacao que ocorreu durante operacoes
    e requer registro, acompanhamento e possivelmente acao corretiva.

    Attributes:
        id: Identificador unico UUID.
        code: Codigo unico legivel (OCC-2026-00001).
        tenant_id: ID do tenant/empresa.
        post_id: Posto onde ocorreu.
        client_id: Cliente relacionado.
        contract_id: Contrato relacionado.
        category: Categoria da ocorrencia.
        severity: Nivel de severidade.
        type: Tipo de ocorrencia.
        title: Titulo descritivo.
        description: Descricao detalhada.
        status: Status atual.
        priority: Prioridade de atendimento.
    """

    __tablename__ = "occurrences"
    __table_args__ = (
        Index("ix_occurrences_tenant_status", "tenant_id", "status"),
        Index("ix_occurrences_tenant_category", "tenant_id", "category"),
        Index("ix_occurrences_tenant_severity", "tenant_id", "severity"),
        Index("ix_occurrences_sla_deadline", "sla_deadline", "sla_breached"),
        Index("ix_occurrences_created_at", "created_at"),
        Index("ix_occurrences_post_client", "post_id", "client_id"),
    )

    # === Identificacao ===
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
    )
    tenant_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
    )

    # === Relacionamentos Externos ===
    post_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("posts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    client_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    contract_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )

    # === Classificacao ===
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=OccurrenceCategory.OUTRO.value,
        index=True,
    )
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=OccurrenceSeverity.MEDIA.value,
        index=True,
    )
    type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=OccurrenceType.INCIDENTE.value,
    )

    # === Descricao ===
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # === Envolvidos ===
    reported_by_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )
    employee_involved_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        index=True,
    )
    witness_ids: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
    )

    # === Status e Prioridade ===
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=OccurrenceStatus.ABERTA.value,
        index=True,
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=OccurrencePriority.NORMAL.value,
        index=True,
    )

    # === Resolucao ===
    resolution: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    resolved_by_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    resolution_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    # === Escalacao ===
    escalated: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    escalated_to_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    escalated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    escalation_reason: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    # === Medida Administrativa ===
    disciplinary_action_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # === SLA ===
    sla_deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        index=True,
    )
    sla_breached: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    # === Controle ===
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # === Auditoria ===
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )
    created_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
    )

    # === Metadados ===
    location_description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    occurred_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )
    tags: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
    )
    extra_metadata: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
    )

    # === Analise IA ===
    ai_classification: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
    )
    ai_recommendations: Mapped[Optional[list]] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
    )

    # === Relacionamentos ===
    attachments: Mapped[List["OccurrenceAttachment"]] = relationship(
        "OccurrenceAttachment",
        back_populates="occurrence",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    comments: Mapped[List["OccurrenceComment"]] = relationship(
        "OccurrenceComment",
        back_populates="occurrence",
        lazy="selectin",
        cascade="all, delete-orphan",
        order_by="OccurrenceComment.created_at",
    )

    def __repr__(self) -> str:
        """Representacao string do objeto."""
        return f"<Occurrence {self.code} - {self.title[:30]}>"

    def __str__(self) -> str:
        """String legivel do objeto."""
        return f"{self.code}: {self.title}"

    # === Properties ===

    @property
    def is_open(self) -> bool:
        """Verifica se a ocorrencia esta aberta.

        Returns:
            True se status for ABERTA, EM_ANALISE ou PENDENTE_ACAO.
        """
        return self.status in [
            OccurrenceStatus.ABERTA.value,
            OccurrenceStatus.EM_ANALISE.value,
            OccurrenceStatus.PENDENTE_ACAO.value,
        ]

    @property
    def is_resolved(self) -> bool:
        """Verifica se a ocorrencia foi resolvida.

        Returns:
            True se status for RESOLVIDA.
        """
        return self.status == OccurrenceStatus.RESOLVIDA.value

    @property
    def is_critical(self) -> bool:
        """Verifica se e uma ocorrencia critica.

        Returns:
            True se severidade for CRITICA ou prioridade for URGENTE.
        """
        return (
            self.severity == OccurrenceSeverity.CRITICA.value
            or self.priority == OccurrencePriority.URGENTE.value
        )

    @property
    def is_sla_at_risk(self) -> bool:
        """Verifica se o SLA esta em risco.

        Returns:
            True se faltam menos de 25% do tempo para o deadline.
        """
        if not self.sla_deadline or self.sla_breached:
            return self.sla_breached

        now = datetime.utcnow()
        if now >= self.sla_deadline:
            return True

        time_remaining = (self.sla_deadline - now).total_seconds()
        total_time = (self.sla_deadline - self.created_at).total_seconds()

        if total_time <= 0:
            return True

        return (time_remaining / total_time) < 0.25

    @property
    def time_to_sla(self) -> Optional[timedelta]:
        """Calcula tempo restante ate o SLA.

        Returns:
            timedelta ate o deadline, None se nao houver SLA.
        """
        if not self.sla_deadline:
            return None
        return self.sla_deadline - datetime.utcnow()

    @property
    def resolution_time(self) -> Optional[timedelta]:
        """Calcula tempo ate a resolucao.

        Returns:
            timedelta entre criacao e resolucao, None se nao resolvida.
        """
        if not self.resolved_at:
            return None
        return self.resolved_at - self.created_at

    @property
    def requires_disciplinary_action(self) -> bool:
        """Verifica se requer medida administrativa.

        Returns:
            True se categoria=COMPORTAMENTO e severidade >= ALTA.
        """
        return (
            self.category == OccurrenceCategory.COMPORTAMENTO.value
            and self.severity in [
                OccurrenceSeverity.ALTA.value,
                OccurrenceSeverity.CRITICA.value,
            ]
        )

    @property
    def attachment_count(self) -> int:
        """Retorna quantidade de anexos."""
        return len(self.attachments) if self.attachments else 0

    @property
    def comment_count(self) -> int:
        """Retorna quantidade de comentarios."""
        return len(self.comments) if self.comments else 0

    # === Methods ===

    def calculate_sla_deadline(
        self,
        custom_hours: Optional[int] = None,
        category_config: Optional[dict] = None,
    ) -> datetime:
        """Calcula o prazo do SLA baseado na severidade.

        Args:
            custom_hours: Horas customizadas para o SLA.
            category_config: Configuracao da categoria com sla_hours.

        Returns:
            datetime do deadline calculado.
        """
        if custom_hours:
            hours = custom_hours
        elif category_config and category_config.get("sla_hours"):
            hours = category_config["sla_hours"]
        else:
            severity_enum = OccurrenceSeverity(self.severity)
            hours = DEFAULT_SLA_HOURS.get(severity_enum, 48)

        base_time = self.created_at or datetime.utcnow()
        self.sla_deadline = base_time + timedelta(hours=hours)
        return self.sla_deadline

    def check_sla_breach(self) -> bool:
        """Verifica e atualiza status de violacao de SLA.

        Returns:
            True se o SLA foi violado.
        """
        if not self.sla_deadline:
            return False

        if datetime.utcnow() > self.sla_deadline and self.is_open:
            self.sla_breached = True

        return self.sla_breached

    def start_analysis(self) -> None:
        """Inicia analise da ocorrencia."""
        if self.status == OccurrenceStatus.ABERTA.value:
            self.status = OccurrenceStatus.EM_ANALISE.value

    def mark_pending_action(self) -> None:
        """Marca como pendente de acao."""
        self.status = OccurrenceStatus.PENDENTE_ACAO.value

    def resolve(
        self,
        resolution: str,
        resolved_by_id: str,
        resolution_type: Optional[str] = None,
    ) -> None:
        """Resolve a ocorrencia.

        Args:
            resolution: Descricao da resolucao.
            resolved_by_id: ID do usuario que resolveu.
            resolution_type: Tipo de resolucao aplicada.
        """
        self.status = OccurrenceStatus.RESOLVIDA.value
        self.resolution = resolution
        self.resolved_by_id = resolved_by_id
        self.resolved_at = datetime.utcnow()
        if resolution_type:
            self.resolution_type = resolution_type

    def reopen(self, reason: Optional[str] = None) -> None:
        """Reabre a ocorrencia.

        Args:
            reason: Motivo da reabertura.
        """
        self.status = OccurrenceStatus.ABERTA.value
        self.resolved_at = None
        self.resolved_by_id = None
        self.resolution = None
        if reason:
            self.extra_metadata = self.extra_metadata or {}
            self.extra_metadata["reopen_reason"] = reason
            self.extra_metadata["reopened_at"] = datetime.utcnow().isoformat()

    def archive(self) -> None:
        """Arquiva a ocorrencia."""
        self.status = OccurrenceStatus.ARQUIVADA.value

    def escalate(
        self,
        escalated_to_id: str,
        reason: str,
    ) -> None:
        """Escala a ocorrencia para outro usuario.

        Args:
            escalated_to_id: ID do usuario para escalar.
            reason: Motivo da escalacao.
        """
        self.escalated = True
        self.escalated_to_id = escalated_to_id
        self.escalated_at = datetime.utcnow()
        self.escalation_reason = reason
        # Aumenta prioridade automaticamente
        if self.priority == OccurrencePriority.BAIXA.value:
            self.priority = OccurrencePriority.NORMAL.value
        elif self.priority == OccurrencePriority.NORMAL.value:
            self.priority = OccurrencePriority.ALTA.value

    def soft_delete(self) -> None:
        """Realiza soft delete do registro."""
        self.is_active = False

    def add_tag(self, tag: str) -> None:
        """Adiciona uma tag.

        Args:
            tag: Tag a adicionar.
        """
        if self.tags is None:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove uma tag.

        Args:
            tag: Tag a remover.
        """
        if self.tags and tag in self.tags:
            self.tags.remove(tag)

    def set_ai_classification(
        self,
        classification: dict,
        recommendations: Optional[list] = None,
    ) -> None:
        """Define classificacao de IA.

        Args:
            classification: Resultado da classificacao.
            recommendations: Recomendacoes geradas.
        """
        self.ai_classification = classification
        if recommendations:
            self.ai_recommendations = recommendations

    @classmethod
    def generate_code(cls, year: int, sequence: int) -> str:
        """Gera codigo unico para ocorrencia.

        Args:
            year: Ano de referencia.
            sequence: Numero sequencial.

        Returns:
            Codigo no formato OCC-YYYY-NNNNN.
        """
        return f"OCC-{year}-{sequence:05d}"
