"""
DuplicateRecord Model - Registros duplicados detectados.

Gerencia detecção e resolução de duplicatas.
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


class DuplicateStatusEnum(StrEnum):
    """Status do grupo de duplicatas."""

    DETECTED = "detected"
    REVIEWING = "reviewing"
    CONFIRMED = "confirmed"
    MERGED = "merged"
    REJECTED = "rejected"
    AUTO_MERGED = "auto_merged"


class DuplicateTypeEnum(StrEnum):
    """Tipo de duplicata."""

    EXACT = "exact"  # Duplicata exata
    FUZZY = "fuzzy"  # Duplicata por similaridade
    PARTIAL = "partial"  # Alguns campos iguais
    PHONETIC = "phonetic"  # Similaridade fonética
    SEMANTIC = "semantic"  # Similaridade semântica


class MergeStrategyEnum(StrEnum):
    """Estratégia de merge."""

    KEEP_FIRST = "keep_first"  # Manter primeiro registro
    KEEP_LAST = "keep_last"  # Manter último registro
    KEEP_MOST_COMPLETE = "keep_most_complete"  # Manter mais completo
    KEEP_MOST_RECENT = "keep_most_recent"  # Manter mais recente
    MERGE_FIELDS = "merge_fields"  # Combinar campos
    MANUAL = "manual"  # Decisão manual


class DuplicateRecord(Base):
    """Model de registro duplicado."""

    __tablename__ = "ai_duplicate_records"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Grupo de duplicatas

    # Status
    status = Column(
        SQLEnum(DuplicateStatusEnum, name="dq_duplicate_status_enum"),
        nullable=False,
        default=DuplicateStatusEnum.DETECTED,
    )
    duplicate_type = Column(
        SQLEnum(DuplicateTypeEnum, name="dq_duplicate_type_enum"), nullable=False, default=DuplicateTypeEnum.FUZZY
    )

    # Entidade
    entity_type = Column(String(100), nullable=False)

    # Registros do grupo
    record_ids = Column(JSONB, nullable=False)  # Lista de IDs dos registros
    record_count = Column(Integer, default=2)
    master_record_id = Column(UUID(as_uuid=True), nullable=True)  # Registro master escolhido

    # Campos de match
    matching_fields = Column(JSONB, default=list)  # Campos que matcharam
    matching_values = Column(JSONB, default=dict)  # Valores dos campos

    # Scores
    similarity_score = Column(Float, nullable=False)  # 0-100
    confidence_score = Column(Float, default=0.0)
    field_scores = Column(JSONB, default=dict)  # Score por campo

    # Detalhes da comparação
    comparison_details = Column(JSONB, default=dict)
    field_comparisons = Column(JSONB, default=list)

    # Merge
    merge_strategy = Column(SQLEnum(MergeStrategyEnum, name="dq_merge_strategy_enum"), nullable=True)
    merged_record_id = Column(UUID(as_uuid=True), nullable=True)
    merged_at = Column(DateTime, nullable=True)
    merged_by = Column(UUID(as_uuid=True), nullable=True)
    merge_log = Column(JSONB, default=dict)

    # Campos conflitantes
    conflicting_fields = Column(JSONB, default=list)
    conflict_resolutions = Column(JSONB, default=dict)

    # Auto-merge
    can_auto_merge = Column(Boolean, default=False)
    auto_merge_blocked_reason = Column(String(255), nullable=True)

    # Referência ao check que detectou
    check_id = Column(UUID(as_uuid=True), ForeignKey("ai_data_quality_checks.id"), nullable=True)

    # Review
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(UUID(as_uuid=True), nullable=True)
    review_notes = Column(Text, nullable=True)

    # Rejection
    rejection_reason = Column(String(255), nullable=True)

    # Ownership
    organization_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Metadados
    extra_metadata = Column(JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<DuplicateRecord(id={self.id}, group={self.group_id}, score={self.similarity_score})>"

    @property
    def is_pending(self) -> bool:
        """Verifica se está pendente de resolução."""
        return self.status in [
            DuplicateStatusEnum.DETECTED,
            DuplicateStatusEnum.REVIEWING,
            DuplicateStatusEnum.CONFIRMED,
        ]

    @property
    def is_resolved(self) -> bool:
        """Verifica se foi resolvido."""
        return self.status in [
            DuplicateStatusEnum.MERGED,
            DuplicateStatusEnum.REJECTED,
            DuplicateStatusEnum.AUTO_MERGED,
        ]

    @property
    def has_conflicts(self) -> bool:
        """Verifica se tem conflitos."""
        return bool(self.conflicting_fields)

    def add_record(self, record_id: uuid.UUID) -> None:
        """Adiciona registro ao grupo."""
        if not self.record_ids:
            self.record_ids = []
        if str(record_id) not in [str(r) for r in self.record_ids]:
            self.record_ids.append(str(record_id))
            self.record_count = len(self.record_ids)

    def set_master(self, record_id: uuid.UUID) -> None:
        """Define registro master."""
        self.master_record_id = record_id

    def start_review(self, user_id: uuid.UUID = None) -> None:
        """Inicia revisão."""
        self.status = DuplicateStatusEnum.REVIEWING
        if user_id:
            self.reviewed_by = user_id

    def confirm(self, user_id: uuid.UUID = None) -> None:
        """Confirma duplicata."""
        self.status = DuplicateStatusEnum.CONFIRMED
        self.reviewed_at = datetime.utcnow()
        if user_id:
            self.reviewed_by = user_id

    def merge(
        self,
        master_id: uuid.UUID,
        merged_id: uuid.UUID,
        strategy: MergeStrategyEnum,
        user_id: uuid.UUID = None,
        auto: bool = False,
    ) -> None:
        """Realiza merge."""
        self.status = DuplicateStatusEnum.AUTO_MERGED if auto else DuplicateStatusEnum.MERGED
        self.master_record_id = master_id
        self.merged_record_id = merged_id
        self.merge_strategy = strategy
        self.merged_at = datetime.utcnow()
        self.merged_by = user_id

    def reject(self, reason: str, user_id: uuid.UUID = None) -> None:
        """Rejeita como não duplicata."""
        self.status = DuplicateStatusEnum.REJECTED
        self.rejection_reason = reason
        self.reviewed_at = datetime.utcnow()
        if user_id:
            self.reviewed_by = user_id

    def add_field_comparison(self, field: str, value1: Any, value2: Any, score: float, is_match: bool) -> None:
        """Adiciona comparação de campo."""
        if not self.field_comparisons:
            self.field_comparisons = []
        self.field_comparisons.append(
            {
                "field": field,
                "value1": str(value1) if value1 else None,
                "value2": str(value2) if value2 else None,
                "score": score,
                "is_match": is_match,
            }
        )
        if not self.field_scores:
            self.field_scores = {}
        self.field_scores[field] = score

        if is_match:
            if not self.matching_fields:
                self.matching_fields = []
            if field not in self.matching_fields:
                self.matching_fields.append(field)
        elif value1 != value2:
            if not self.conflicting_fields:
                self.conflicting_fields = []
            if field not in self.conflicting_fields:
                self.conflicting_fields.append(field)

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "group_id": str(self.group_id),
            "status": self.status.value,
            "duplicate_type": self.duplicate_type.value,
            "entity_type": self.entity_type,
            "record_ids": self.record_ids,
            "record_count": self.record_count,
            "master_record_id": str(self.master_record_id) if self.master_record_id else None,
            "similarity_score": self.similarity_score,
            "confidence_score": self.confidence_score,
            "matching_fields": self.matching_fields,
            "conflicting_fields": self.conflicting_fields,
            "can_auto_merge": self.can_auto_merge,
            "is_pending": self.is_pending,
            "created_at": self.created_at.isoformat(),
        }

    def to_summary_dict(self) -> dict[str, Any]:
        """Converte para dicionário resumido."""
        return {
            "id": str(self.id),
            "group_id": str(self.group_id),
            "status": self.status.value,
            "record_count": self.record_count,
            "similarity_score": self.similarity_score,
            "is_pending": self.is_pending,
        }
