"""
DataProfile Model - Perfil estatístico dos dados.

Armazena análises estatísticas e perfis de dados por entidade/campo.
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


class ProfileStatusEnum(StrEnum):
    """Status do perfil."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    OUTDATED = "outdated"


class DataTypeEnum(StrEnum):
    """Tipo de dado detectado."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    EMAIL = "email"
    PHONE = "phone"
    CPF = "cpf"
    CNPJ = "cnpj"
    CEP = "cep"
    URL = "url"
    UUID = "uuid"
    JSON = "json"
    ARRAY = "array"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    UNKNOWN = "unknown"


class DataProfile(Base):
    """Model de perfil de dados."""

    __tablename__ = "ai_data_profiles"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_code = Column(String(100), nullable=False)

    # Status
    status = Column(
        SQLEnum(ProfileStatusEnum, name="dq_profile_status_enum"), nullable=False, default=ProfileStatusEnum.PENDING
    )

    # Escopo
    entity_type = Column(String(100), nullable=False)
    field_name = Column(String(100), nullable=True)  # None = perfil da entidade
    is_entity_profile = Column(Boolean, default=False)

    # Tipo de dado
    detected_type = Column(SQLEnum(DataTypeEnum, name="dq_data_type_enum"), nullable=True)
    declared_type = Column(String(50), nullable=True)

    # Estatísticas gerais
    total_records = Column(Integer, default=0)
    sample_size = Column(Integer, default=0)
    null_count = Column(Integer, default=0)
    null_percentage = Column(Float, default=0.0)
    distinct_count = Column(Integer, default=0)
    distinct_percentage = Column(Float, default=0.0)
    duplicate_count = Column(Integer, default=0)

    # Completeness
    completeness_score = Column(Float, nullable=True)
    empty_count = Column(Integer, default=0)
    empty_percentage = Column(Float, default=0.0)

    # Estatísticas numéricas (para campos numéricos)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    mean_value = Column(Float, nullable=True)
    median_value = Column(Float, nullable=True)
    std_deviation = Column(Float, nullable=True)
    variance = Column(Float, nullable=True)
    sum_value = Column(Float, nullable=True)
    percentiles = Column(JSONB, default=dict)  # p25, p50, p75, p90, p95, p99

    # Estatísticas de string (para campos texto)
    min_length = Column(Integer, nullable=True)
    max_length = Column(Integer, nullable=True)
    avg_length = Column(Float, nullable=True)
    pattern_detected = Column(String(255), nullable=True)
    common_patterns = Column(JSONB, default=list)

    # Distribuição de valores
    value_distribution = Column(JSONB, default=dict)  # Top N valores com contagem
    frequency_distribution = Column(JSONB, default=dict)

    # Outliers
    outlier_count = Column(Integer, default=0)
    outlier_percentage = Column(Float, default=0.0)
    outliers = Column(JSONB, default=list)  # Sample de outliers

    # Qualidade
    quality_score = Column(Float, nullable=True)  # 0-100
    validity_score = Column(Float, nullable=True)
    consistency_score = Column(Float, nullable=True)

    # Issues detectados
    issues_summary = Column(JSONB, default=dict)
    common_issues = Column(JSONB, default=list)

    # Para campos de data/datetime
    date_range_start = Column(DateTime, nullable=True)
    date_range_end = Column(DateTime, nullable=True)
    future_dates_count = Column(Integer, default=0)
    invalid_dates_count = Column(Integer, default=0)

    # Para campos de referência
    orphan_count = Column(Integer, default=0)
    orphan_percentage = Column(Float, default=0.0)

    # Correlações (com outros campos)
    correlations = Column(JSONB, default=dict)

    # Recomendações
    recommendations = Column(JSONB, default=list)

    # Histórico
    previous_profile_id = Column(UUID(as_uuid=True), nullable=True)
    score_change = Column(Float, nullable=True)

    # Execução
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

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
        return f"<DataProfile(id={self.id}, entity={self.entity_type}, field={self.field_name})>"

    @property
    def is_completed(self) -> bool:
        """Verifica se o perfil está completo."""
        return self.status == ProfileStatusEnum.COMPLETED

    @property
    def is_outdated(self) -> bool:
        """Verifica se está desatualizado (mais de 7 dias)."""
        if not self.completed_at:
            return True
        age = (datetime.utcnow() - self.completed_at).days
        return age > 7

    @property
    def has_quality_issues(self) -> bool:
        """Verifica se tem problemas de qualidade."""
        if self.quality_score is not None and self.quality_score < 80:
            return True
        if self.null_percentage > 20:
            return True
        if self.outlier_percentage > 5:
            return True
        return False

    def start_profiling(self) -> None:
        """Inicia processo de profiling."""
        self.status = ProfileStatusEnum.PROCESSING
        self.started_at = datetime.utcnow()

    def complete_profiling(self) -> None:
        """Completa processo de profiling."""
        self.status = ProfileStatusEnum.COMPLETED
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.duration_ms = int((self.completed_at - self.started_at).total_seconds() * 1000)
        self._calculate_scores()

    def fail_profiling(self, error: str) -> None:
        """Marca falha no profiling."""
        self.status = ProfileStatusEnum.FAILED
        self.error_message = error
        self.completed_at = datetime.utcnow()

    def _calculate_scores(self) -> None:
        """Calcula scores de qualidade."""
        # Completeness score
        if self.total_records > 0:
            self.completeness_score = 100 - self.null_percentage

        # Quality score baseado em múltiplos fatores
        scores = []
        if self.completeness_score is not None:
            scores.append(self.completeness_score)
        if self.validity_score is not None:
            scores.append(self.validity_score)
        if self.consistency_score is not None:
            scores.append(self.consistency_score)

        # Penalidades
        penalty = 0
        if self.outlier_percentage > 5:
            penalty += 10
        if self.duplicate_count > 0 and self.total_records > 0:
            dup_rate = (self.duplicate_count / self.total_records) * 100
            if dup_rate > 5:
                penalty += 10

        if scores:
            self.quality_score = max(0, sum(scores) / len(scores) - penalty)

    def set_numeric_stats(
        self,
        min_val: float,
        max_val: float,
        mean: float,
        median: float,
        std: float,
        percentiles: dict[str, float] = None,
    ) -> None:
        """Define estatísticas numéricas."""
        self.min_value = min_val
        self.max_value = max_val
        self.mean_value = mean
        self.median_value = median
        self.std_deviation = std
        self.variance = std**2 if std else None
        if percentiles:
            self.percentiles = percentiles

    def set_string_stats(self, min_len: int, max_len: int, avg_len: float, patterns: list[str] = None) -> None:
        """Define estatísticas de string."""
        self.min_length = min_len
        self.max_length = max_len
        self.avg_length = avg_len
        if patterns:
            self.common_patterns = patterns

    def add_recommendation(self, recommendation: str, priority: str = "medium") -> None:
        """Adiciona recomendação."""
        if not self.recommendations:
            self.recommendations = []
        self.recommendations.append(
            {"text": recommendation, "priority": priority, "created_at": datetime.utcnow().isoformat()}
        )

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "profile_code": self.profile_code,
            "status": self.status.value,
            "entity_type": self.entity_type,
            "field_name": self.field_name,
            "detected_type": self.detected_type.value if self.detected_type else None,
            "total_records": self.total_records,
            "null_count": self.null_count,
            "null_percentage": self.null_percentage,
            "distinct_count": self.distinct_count,
            "completeness_score": self.completeness_score,
            "quality_score": self.quality_score,
            "outlier_count": self.outlier_count,
            "has_quality_issues": self.has_quality_issues,
            "is_outdated": self.is_outdated,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }

    def to_summary_dict(self) -> dict[str, Any]:
        """Converte para dicionário resumido."""
        return {
            "id": str(self.id),
            "entity_type": self.entity_type,
            "field_name": self.field_name,
            "quality_score": self.quality_score,
            "completeness_score": self.completeness_score,
            "total_records": self.total_records,
        }

    def to_stats_dict(self) -> dict[str, Any]:
        """Converte para dicionário de estatísticas."""
        stats = {
            "total_records": self.total_records,
            "null_count": self.null_count,
            "null_percentage": self.null_percentage,
            "distinct_count": self.distinct_count,
            "distinct_percentage": self.distinct_percentage,
            "duplicate_count": self.duplicate_count,
        }

        # Adiciona stats numéricas se disponíveis
        if self.detected_type in [DataTypeEnum.INTEGER, DataTypeEnum.FLOAT, DataTypeEnum.CURRENCY]:
            stats.update(
                {
                    "min": self.min_value,
                    "max": self.max_value,
                    "mean": self.mean_value,
                    "median": self.median_value,
                    "std": self.std_deviation,
                    "percentiles": self.percentiles,
                }
            )

        # Adiciona stats de string se disponíveis
        if self.detected_type == DataTypeEnum.STRING:
            stats.update(
                {
                    "min_length": self.min_length,
                    "max_length": self.max_length,
                    "avg_length": self.avg_length,
                    "patterns": self.common_patterns,
                }
            )

        return stats
