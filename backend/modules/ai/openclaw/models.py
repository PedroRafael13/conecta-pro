"""
Modelos OpenClaw — memoria episodica, padroes aprendidos e knowledge base.

Registra intervencoes, aprende padroes de resolucao e mantem
conhecimento sobre componentes do sistema.
"""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import BaseModel


class InterventionStatus(StrEnum):
    RECEIVED = "received"
    DIAGNOSING = "diagnosing"
    ACTING = "acting"
    RESOLVED = "resolved"
    FAILED = "failed"
    ESCALATED = "escalated"


class InterventionSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class Intervention(BaseModel):
    """Registro de intervenção automática do OpenClaw."""

    __tablename__ = "openclaw_interventions"

    # Alerta que disparou a intervenção
    alert_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    alert_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    severity: Mapped[InterventionSeverity] = mapped_column(
        Enum(InterventionSeverity, values_callable=lambda e: [x.value for x in e], create_type=False),
        nullable=False,
        default=InterventionSeverity.WARNING,
    )
    status: Mapped[InterventionStatus] = mapped_column(
        Enum(InterventionStatus, values_callable=lambda e: [x.value for x in e], create_type=False),
        nullable=False,
        default=InterventionStatus.RECEIVED,
    )

    # Diagnóstico gerado
    diagnosis: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Ações executadas (lista de steps)
    actions_taken: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Resultado
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Tempo de resposta em segundos
    response_time_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Payload original do Alertmanager
    raw_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Notificação enviada
    telegram_sent: Mapped[bool] = mapped_column(default=False)
    telegram_message_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Campos de aprendizado (preenchidos pos-resolucao)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    learned_pattern: Mapped[str | None] = mapped_column(Text, nullable=True)
    prevention_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    used_cached_solution: Mapped[bool] = mapped_column(default=False)

    # Proteção contra falsos positivos
    false_positive: Mapped[bool] = mapped_column(default=False)
    false_positive_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Validação humana
    human_validated: Mapped[bool] = mapped_column(default=False)
    human_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    validated_by: Mapped[str | None] = mapped_column(String(200), nullable=True)


class AgentPattern(BaseModel):
    """Padrao aprendido pelo OpenClaw a partir de intervencoes repetidas."""

    __tablename__ = "openclaw_patterns"

    pattern_name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    alert_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    trigger_conditions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    frequency: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    auto_action: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    diagnosis_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    avg_resolve_time_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Validação humana
    human_validated: Mapped[bool] = mapped_column(default=False)
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    validated_by: Mapped[str | None] = mapped_column(String(200), nullable=True)


class AgentKnowledgeBase(BaseModel):
    """Conhecimento sobre componentes do sistema monitorado."""

    __tablename__ = "openclaw_knowledge_base"

    component: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    known_issues: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    dependencies: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    peak_hours: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    criticality_level: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    runbook: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    last_incident_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
