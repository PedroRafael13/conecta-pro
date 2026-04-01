"""FeatureStore Model - Store de Features para ML.

Sprint 34 - AI Predictions.
"""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import relationship

from core.models import Base


class FeatureStatus(StrEnum):
    """Status da feature."""

    DRAFT = "DRAFT"  # Rascunho
    ACTIVE = "ACTIVE"  # Ativa
    DEPRECATED = "DEPRECATED"  # Deprecada
    ARCHIVED = "ARCHIVED"  # Arquivada


class FeatureDataType(StrEnum):
    """Tipo de dado da feature."""

    NUMERIC = "NUMERIC"  # Numerico continuo
    INTEGER = "INTEGER"  # Inteiro
    CATEGORICAL = "CATEGORICAL"  # Categorico
    BOOLEAN = "BOOLEAN"  # Booleano
    TEXT = "TEXT"  # Texto
    DATE = "DATE"  # Data
    DATETIME = "DATETIME"  # Data e hora
    ARRAY = "ARRAY"  # Array
    EMBEDDING = "EMBEDDING"  # Embedding vetorial


class FeatureStore(Base):
    """Feature Store - Colecao de features para ML."""

    __tablename__ = "ai_feature_stores"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Identificacao
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    version = Column(String(50), nullable=False, default="1.0.0")

    # Status
    status = Column(
        Enum(FeatureStatus, name="featurestatus", create_type=True),
        nullable=False,
        default=FeatureStatus.DRAFT,
        index=True,
    )

    # Entidade base
    entity_type = Column(String(100), nullable=False, index=True)
    # Ex: "client", "lead", "contract", "employee"

    # Fonte de dados
    data_source = Column(String(200), nullable=True)
    # Ex: "postgres://...", "api://...", "file://..."
    source_query = Column(Text, nullable=True)  # Query SQL ou similar
    source_config = Column(JSONB, nullable=True)  # Configuracoes da fonte

    # Atualizacao
    refresh_frequency = Column(String(50), nullable=True)
    # Ex: "hourly", "daily", "weekly", "on_demand"
    last_refresh_at = Column(DateTime(timezone=True), nullable=True)
    next_refresh_at = Column(DateTime(timezone=True), nullable=True)
    refresh_status = Column(String(50), nullable=True)
    # Ex: "success", "failed", "running"

    # Metricas
    total_features = Column(Integer, default=0, nullable=False)
    total_entities = Column(Integer, default=0, nullable=False)
    storage_size_bytes = Column(Integer, nullable=True)

    # Qualidade
    data_quality_score = Column(Float, nullable=True)  # 0-100
    completeness_score = Column(Float, nullable=True)  # % de valores nao nulos
    freshness_score = Column(Float, nullable=True)  # Quao atualizado esta

    # Flags
    active = Column(Boolean, default=True, nullable=False)
    is_online = Column(Boolean, default=False, nullable=False)  # Servido em real-time
    is_cached = Column(Boolean, default=True, nullable=False)  # Cache habilitado

    # Tags
    tags = Column(ARRAY(String), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    features = relationship(
        "Feature",
        back_populates="feature_store",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<FeatureStore {self.name} ({self.entity_type})>"

    @property
    def is_ready(self) -> bool:
        """Verifica se esta pronta."""
        return self.status == FeatureStatus.ACTIVE and self.total_features > 0

    @property
    def needs_refresh(self) -> bool:
        """Verifica se precisa atualizar."""
        if not self.next_refresh_at:
            return False
        return datetime.utcnow() >= self.next_refresh_at

    def activate(self) -> None:
        """Ativa o feature store."""
        self.status = FeatureStatus.ACTIVE

    def deprecate(self) -> None:
        """Depreca o feature store."""
        self.status = FeatureStatus.DEPRECATED

    def archive(self) -> None:
        """Arquiva o feature store."""
        self.status = FeatureStatus.ARCHIVED
        self.active = False


class Feature(Base):
    """Feature individual no Feature Store."""

    __tablename__ = "ai_features"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Feature Store
    feature_store_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_feature_stores.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Identificacao
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Tipo de dado
    data_type = Column(
        Enum(FeatureDataType, name="featuredatatype", create_type=True),
        nullable=False,
    )

    # Status
    status = Column(
        Enum(FeatureStatus, name="featurestatus", create_type=True),
        nullable=False,
        default=FeatureStatus.ACTIVE,
    )

    # Transformacao
    source_column = Column(String(200), nullable=True)  # Coluna de origem
    transformation = Column(Text, nullable=True)  # Transformacao aplicada
    # Ex: "log(x)", "normalize(x)", "one_hot(x)"
    transformation_config = Column(JSONB, nullable=True)
    # Ex: {"method": "standard_scaler", "params": {"mean": 0, "std": 1}}

    # Estatisticas
    statistics = Column(JSONB, nullable=True)
    # Ex: {"min": 0, "max": 100, "mean": 50, "std": 15, "nulls": 5}

    # Validacao
    validation_rules = Column(JSONB, nullable=True)
    # Ex: {"min": 0, "max": 1000, "not_null": true}

    # Importancia
    importance_score = Column(Float, nullable=True)  # 0-1
    correlation_target = Column(Float, nullable=True)  # Correlacao com target

    # Metadados
    category = Column(String(100), nullable=True)
    # Ex: "demographic", "behavioral", "temporal", "aggregate"
    sensitivity = Column(String(50), nullable=True)
    # Ex: "public", "internal", "sensitive", "pii"

    # Flags
    active = Column(Boolean, default=True, nullable=False)
    is_computed = Column(Boolean, default=False, nullable=False)  # Calculada
    is_derived = Column(Boolean, default=False, nullable=False)  # Derivada de outras

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Audit
    created_by = Column(UUID(as_uuid=True), nullable=True)

    # Relationships
    feature_store = relationship(
        "FeatureStore",
        back_populates="features",
    )

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<Feature {self.name} ({self.data_type.value})>"

    @property
    def is_numeric(self) -> bool:
        """Verifica se e numerica."""
        return self.data_type in [FeatureDataType.NUMERIC, FeatureDataType.INTEGER]

    @property
    def is_categorical(self) -> bool:
        """Verifica se e categorica."""
        return self.data_type == FeatureDataType.CATEGORICAL

    def get_stats(self) -> dict:
        """Retorna estatisticas."""
        return self.statistics or {}

    def validate_value(self, value: any) -> bool:
        """Valida um valor contra as regras.

        Args:
            value: Valor a validar.

        Returns:
            True se valido.
        """
        if not self.validation_rules:
            return True

        rules = self.validation_rules

        # Not null
        if rules.get("not_null") and value is None:
            return False

        if value is None:
            return True

        # Min/max para numericos
        if self.is_numeric:
            if "min" in rules and value < rules["min"]:
                return False
            if "max" in rules and value > rules["max"]:
                return False

        # Valores permitidos para categoricos
        if self.is_categorical and "allowed_values" in rules:
            if value not in rules["allowed_values"]:
                return False

        return True
