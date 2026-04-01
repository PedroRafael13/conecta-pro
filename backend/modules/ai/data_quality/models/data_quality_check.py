"""
DataQualityCheck Model - Verificações de qualidade executadas.

Registra execuções de verificação de qualidade de dados.
"""

import uuid
from datetime import datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.database import Base


class CheckStatusEnum(StrEnum):
    """Status da verificação."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


class CheckScopeEnum(StrEnum):
    """Escopo da verificação."""

    FULL = "full"
    INCREMENTAL = "incremental"
    SAMPLE = "sample"
    SINGLE_RECORD = "single_record"
    BATCH = "batch"


class CheckTriggerEnum(StrEnum):
    """Gatilho da verificação."""

    MANUAL = "manual"
    SCHEDULED = "scheduled"
    ON_INSERT = "on_insert"
    ON_UPDATE = "on_update"
    ON_IMPORT = "on_import"
    API = "api"
    WEBHOOK = "webhook"


class DataQualityCheck(Base):
    """Model de verificação de qualidade de dados."""

    __tablename__ = "ai_data_quality_checks"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    check_number = Column(Integer, nullable=False)
    name = Column(String(255), nullable=True)

    # Status
    status = Column(
        SQLEnum(CheckStatusEnum, name="dq_check_status_enum"), nullable=False, default=CheckStatusEnum.PENDING
    )
    progress = Column(Float, default=0.0)  # 0-100

    # Escopo
    scope = Column(SQLEnum(CheckScopeEnum, name="dq_check_scope_enum"), nullable=False, default=CheckScopeEnum.FULL)
    entity_type = Column(String(100), nullable=False)
    entity_ids = Column(JSONB, default=list)  # IDs específicos se aplicável

    # Gatilho
    trigger = Column(
        SQLEnum(CheckTriggerEnum, name="dq_check_trigger_enum"), nullable=False, default=CheckTriggerEnum.MANUAL
    )
    triggered_by = Column(UUID(as_uuid=True), nullable=True)

    # Regras aplicadas
    rule_ids = Column(JSONB, default=list)  # IDs das regras
    rules_applied = Column(Integer, default=0)
    rules_passed = Column(Integer, default=0)
    rules_failed = Column(Integer, default=0)

    # Configuração
    parameters = Column(JSONB, default=dict)
    sample_size = Column(Integer, nullable=True)
    sample_percentage = Column(Float, nullable=True)

    # Resultados
    records_checked = Column(Integer, default=0)
    records_valid = Column(Integer, default=0)
    records_invalid = Column(Integer, default=0)
    records_fixed = Column(Integer, default=0)
    records_skipped = Column(Integer, default=0)

    # Issues
    issues_found = Column(Integer, default=0)
    issues_critical = Column(Integer, default=0)
    issues_high = Column(Integer, default=0)
    issues_medium = Column(Integer, default=0)
    issues_low = Column(Integer, default=0)

    # Scores
    overall_score = Column(Float, nullable=True)  # 0-100
    completeness_score = Column(Float, nullable=True)
    accuracy_score = Column(Float, nullable=True)
    consistency_score = Column(Float, nullable=True)
    validity_score = Column(Float, nullable=True)
    uniqueness_score = Column(Float, nullable=True)

    # Tempo
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, default=0)

    # Erros
    error_message = Column(Text, nullable=True)
    error_details = Column(JSONB, default=dict)

    # Resultado detalhado
    results_summary = Column(JSONB, default=dict)
    field_scores = Column(JSONB, default=dict)  # Score por campo
    rule_results = Column(JSONB, default=dict)  # Resultado por regra

    # Auto-fix
    auto_fix_enabled = Column(Boolean, default=False)
    fixes_applied = Column(Integer, default=0)
    fixes_failed = Column(Integer, default=0)

    # Comparação com check anterior
    previous_check_id = Column(UUID(as_uuid=True), nullable=True)
    score_change = Column(Float, nullable=True)
    issues_change = Column(Integer, nullable=True)

    # Ownership
    organization_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Metadados
    extra_metadata = Column(JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<DataQualityCheck(id={self.id}, status={self.status}, score={self.overall_score})>"

    @property
    def is_running(self) -> bool:
        """Verifica se está em execução."""
        return self.status in [CheckStatusEnum.PENDING, CheckStatusEnum.RUNNING]

    @property
    def is_completed(self) -> bool:
        """Verifica se foi completado."""
        return self.status == CheckStatusEnum.COMPLETED

    @property
    def pass_rate(self) -> float:
        """Taxa de registros válidos."""
        total = self.records_valid + self.records_invalid
        if total == 0:
            return 0.0
        return (self.records_valid / total) * 100

    @property
    def fix_rate(self) -> float:
        """Taxa de correções bem-sucedidas."""
        if self.records_invalid == 0:
            return 0.0
        return (self.records_fixed / self.records_invalid) * 100

    def start(self) -> None:
        """Inicia a verificação."""
        self.status = CheckStatusEnum.RUNNING
        self.started_at = datetime.utcnow()
        self.progress = 0.0

    def complete(self, success: bool = True) -> None:
        """Completa a verificação."""
        self.status = CheckStatusEnum.COMPLETED if success else CheckStatusEnum.FAILED
        self.completed_at = datetime.utcnow()
        self.progress = 100.0
        if self.started_at:
            self.duration_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)
        self._calculate_scores()

    def update_progress(self, progress: float, records_processed: int = None) -> None:
        """Atualiza progresso."""
        self.progress = min(100.0, max(0.0, progress))
        if records_processed is not None:
            self.records_checked = records_processed

    def add_issue(self, severity: str) -> None:
        """Adiciona issue encontrado."""
        self.issues_found += 1
        if severity == "critical":
            self.issues_critical += 1
        elif severity == "high":
            self.issues_high += 1
        elif severity == "medium":
            self.issues_medium += 1
        else:
            self.issues_low += 1

    def _calculate_scores(self) -> None:
        """Calcula scores de qualidade."""
        scores = []
        if self.completeness_score is not None:
            scores.append(self.completeness_score)
        if self.accuracy_score is not None:
            scores.append(self.accuracy_score)
        if self.consistency_score is not None:
            scores.append(self.consistency_score)
        if self.validity_score is not None:
            scores.append(self.validity_score)
        if self.uniqueness_score is not None:
            scores.append(self.uniqueness_score)

        if scores:
            self.overall_score = sum(scores) / len(scores)
        elif self.records_checked > 0:
            self.overall_score = self.pass_rate

    def set_error(self, message: str, details: dict = None) -> None:
        """Define erro da verificação."""
        self.status = CheckStatusEnum.FAILED
        self.error_message = message
        self.error_details = details or {}
        self.completed_at = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "check_number": self.check_number,
            "status": self.status.value,
            "scope": self.scope.value,
            "entity_type": self.entity_type,
            "progress": self.progress,
            "records_checked": self.records_checked,
            "records_valid": self.records_valid,
            "records_invalid": self.records_invalid,
            "issues_found": self.issues_found,
            "overall_score": self.overall_score,
            "pass_rate": self.pass_rate,
            "duration_ms": self.duration_ms,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    def to_summary_dict(self) -> dict[str, Any]:
        """Converte para dicionário resumido."""
        return {
            "id": str(self.id),
            "status": self.status.value,
            "overall_score": self.overall_score,
            "issues_found": self.issues_found,
            "pass_rate": self.pass_rate,
        }
