"""
DataQualityIssue Model - Problemas de qualidade encontrados.

Registra issues de qualidade detectados em dados.
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
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.database import Base


class IssueSeverityEnum(StrEnum):
    """Severidade do issue."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IssueStatusEnum(StrEnum):
    """Status do issue."""

    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    FIXED = "fixed"
    IGNORED = "ignored"
    FALSE_POSITIVE = "false_positive"
    WONT_FIX = "wont_fix"


class IssueTypeEnum(StrEnum):
    """Tipo de issue."""

    # Completeness
    MISSING_VALUE = "missing_value"
    INCOMPLETE_RECORD = "incomplete_record"

    # Accuracy
    INVALID_VALUE = "invalid_value"
    OUT_OF_RANGE = "out_of_range"
    INVALID_FORMAT = "invalid_format"
    INVALID_CHECKSUM = "invalid_checksum"

    # Consistency
    INCONSISTENT_DATA = "inconsistent_data"
    CROSS_FIELD_MISMATCH = "cross_field_mismatch"
    REFERENTIAL_INTEGRITY = "referential_integrity"

    # Uniqueness
    DUPLICATE_VALUE = "duplicate_value"
    DUPLICATE_RECORD = "duplicate_record"

    # Validity
    CONSTRAINT_VIOLATION = "constraint_violation"
    BUSINESS_RULE_VIOLATION = "business_rule_violation"
    TYPE_MISMATCH = "type_mismatch"

    # Timeliness
    OUTDATED_DATA = "outdated_data"
    STALE_RECORD = "stale_record"

    # Standardization
    NON_STANDARD_FORMAT = "non_standard_format"
    ENCODING_ISSUE = "encoding_issue"

    # Other
    CUSTOM = "custom"


class DataQualityIssue(Base):
    """Model de issue de qualidade de dados."""

    __tablename__ = "ai_data_quality_issues"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    issue_code = Column(String(50), nullable=False)

    # Referência ao check
    check_id = Column(UUID(as_uuid=True), ForeignKey("ai_data_quality_checks.id"), nullable=True)

    # Referência à regra
    rule_id = Column(UUID(as_uuid=True), ForeignKey("ai_data_quality_rules.id"), nullable=True)
    rule_code = Column(String(100), nullable=True)

    # Tipo e severidade
    issue_type = Column(SQLEnum(IssueTypeEnum, name="dq_issue_type_enum"), nullable=False)
    severity = Column(
        SQLEnum(IssueSeverityEnum, name="dq_issue_severity_enum"), nullable=False, default=IssueSeverityEnum.MEDIUM
    )
    status = Column(SQLEnum(IssueStatusEnum, name="dq_issue_status_enum"), nullable=False, default=IssueStatusEnum.OPEN)

    # Localização do problema
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    entity_code = Column(String(100), nullable=True)
    field_name = Column(String(100), nullable=True)
    field_path = Column(String(255), nullable=True)  # Para campos aninhados

    # Valores
    current_value = Column(Text, nullable=True)
    expected_value = Column(Text, nullable=True)
    suggested_value = Column(Text, nullable=True)

    # Descrição
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    # Contexto
    context = Column(JSONB, default=dict)  # Dados adicionais do contexto
    related_records = Column(JSONB, default=list)  # Registros relacionados (para duplicatas)

    # Scoring
    confidence_score = Column(Float, default=1.0)  # Confiança na detecção
    impact_score = Column(Float, nullable=True)  # Impacto estimado

    # Auto-fix
    can_auto_fix = Column(Boolean, default=False)
    auto_fix_attempted = Column(Boolean, default=False)
    auto_fix_success = Column(Boolean, nullable=True)
    fix_applied_at = Column(DateTime, nullable=True)
    fix_applied_by = Column(UUID(as_uuid=True), nullable=True)
    fix_details = Column(JSONB, default=dict)

    # Resolução manual
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(UUID(as_uuid=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    resolution_type = Column(String(50), nullable=True)  # fixed, ignored, false_positive

    # Recorrência
    occurrence_count = Column(Integer, default=1)
    first_detected_at = Column(DateTime, default=datetime.utcnow)
    last_detected_at = Column(DateTime, default=datetime.utcnow)
    is_recurring = Column(Boolean, default=False)

    # Agrupamento
    group_id = Column(UUID(as_uuid=True), nullable=True)  # Para agrupar issues similares
    is_group_leader = Column(Boolean, default=False)

    # Ownership
    assigned_to = Column(UUID(as_uuid=True), nullable=True)
    organization_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Metadados
    tags = Column(JSONB, default=list)
    extra_metadata = Column(JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<DataQualityIssue(id={self.id}, type={self.issue_type}, status={self.status})>"

    @property
    def is_open(self) -> bool:
        """Verifica se o issue está aberto."""
        return self.status in [IssueStatusEnum.OPEN, IssueStatusEnum.ACKNOWLEDGED, IssueStatusEnum.IN_PROGRESS]

    @property
    def is_resolved(self) -> bool:
        """Verifica se foi resolvido."""
        return self.status in [
            IssueStatusEnum.FIXED,
            IssueStatusEnum.IGNORED,
            IssueStatusEnum.FALSE_POSITIVE,
            IssueStatusEnum.WONT_FIX,
        ]

    @property
    def age_hours(self) -> float:
        """Idade do issue em horas."""
        delta = datetime.utcnow() - self.created_at
        return delta.total_seconds() / 3600

    def acknowledge(self, user_id: uuid.UUID = None) -> None:
        """Reconhece o issue."""
        self.status = IssueStatusEnum.ACKNOWLEDGED
        if user_id:
            self.assigned_to = user_id

    def start_fix(self, user_id: uuid.UUID = None) -> None:
        """Inicia correção."""
        self.status = IssueStatusEnum.IN_PROGRESS
        if user_id:
            self.assigned_to = user_id

    def mark_fixed(self, user_id: uuid.UUID = None, notes: str = None, auto: bool = False) -> None:
        """Marca como corrigido."""
        self.status = IssueStatusEnum.FIXED
        self.resolved_at = datetime.utcnow()
        self.resolved_by = user_id
        self.resolution_notes = notes
        self.resolution_type = "auto_fixed" if auto else "manual_fixed"
        if auto:
            self.auto_fix_success = True
            self.fix_applied_at = datetime.utcnow()

    def mark_ignored(self, user_id: uuid.UUID = None, notes: str = None) -> None:
        """Marca como ignorado."""
        self.status = IssueStatusEnum.IGNORED
        self.resolved_at = datetime.utcnow()
        self.resolved_by = user_id
        self.resolution_notes = notes
        self.resolution_type = "ignored"

    def mark_false_positive(self, user_id: uuid.UUID = None, notes: str = None) -> None:
        """Marca como falso positivo."""
        self.status = IssueStatusEnum.FALSE_POSITIVE
        self.resolved_at = datetime.utcnow()
        self.resolved_by = user_id
        self.resolution_notes = notes
        self.resolution_type = "false_positive"

    def increment_occurrence(self) -> None:
        """Incrementa contagem de ocorrências."""
        self.occurrence_count += 1
        self.last_detected_at = datetime.utcnow()
        self.is_recurring = True

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "issue_code": self.issue_code,
            "issue_type": self.issue_type.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "entity_type": self.entity_type,
            "entity_id": str(self.entity_id) if self.entity_id else None,
            "field_name": self.field_name,
            "title": self.title,
            "description": self.description,
            "current_value": self.current_value,
            "suggested_value": self.suggested_value,
            "can_auto_fix": self.can_auto_fix,
            "occurrence_count": self.occurrence_count,
            "is_open": self.is_open,
            "created_at": self.created_at.isoformat(),
        }

    def to_summary_dict(self) -> dict[str, Any]:
        """Converte para dicionário resumido."""
        return {
            "id": str(self.id),
            "issue_type": self.issue_type.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "title": self.title,
            "is_open": self.is_open,
        }
