"""
DataQualityRule Model - Regras de validação de dados.

Define regras para validação, padronização e qualidade de dados.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.database import Base


class RuleTypeEnum(str, Enum):
    """Tipos de regra de qualidade."""

    # Validação
    NOT_NULL = "not_null"
    UNIQUE = "unique"
    FORMAT = "format"
    RANGE = "range"
    LENGTH = "length"
    ENUM = "enum"
    REGEX = "regex"

    # Referencial
    FOREIGN_KEY = "foreign_key"
    CROSS_FIELD = "cross_field"
    CONDITIONAL = "conditional"

    # Padronização
    UPPERCASE = "uppercase"
    LOWERCASE = "lowercase"
    TRIM = "trim"
    NORMALIZE = "normalize"
    PHONE_FORMAT = "phone_format"
    CPF_FORMAT = "cpf_format"
    CNPJ_FORMAT = "cnpj_format"
    CEP_FORMAT = "cep_format"
    EMAIL_FORMAT = "email_format"
    DATE_FORMAT = "date_format"

    # Limpeza
    REMOVE_DUPLICATES = "remove_duplicates"
    FILL_MISSING = "fill_missing"
    OUTLIER_DETECTION = "outlier_detection"

    # Validação de negócio
    CPF_VALID = "cpf_valid"
    CNPJ_VALID = "cnpj_valid"
    EMAIL_VALID = "email_valid"
    PHONE_VALID = "phone_valid"

    # Custom
    CUSTOM = "custom"


class RuleSeverityEnum(str, Enum):
    """Severidade da violação."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RuleStatusEnum(str, Enum):
    """Status da regra."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    DEPRECATED = "deprecated"


class RuleCategoryEnum(str, Enum):
    """Categoria da regra."""

    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    CONSISTENCY = "consistency"
    VALIDITY = "validity"
    UNIQUENESS = "uniqueness"
    TIMELINESS = "timeliness"
    STANDARDIZATION = "standardization"


class DataQualityRule(Base):
    """Model de regra de qualidade de dados."""

    __tablename__ = "ai_data_quality_rules"

    # Identificação
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(100), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Tipo e categoria
    rule_type = Column(
        SQLEnum(RuleTypeEnum, name="dq_rule_type_enum"),
        nullable=False
    )
    category = Column(
        SQLEnum(RuleCategoryEnum, name="dq_rule_category_enum"),
        nullable=False,
        default=RuleCategoryEnum.VALIDITY
    )
    severity = Column(
        SQLEnum(RuleSeverityEnum, name="dq_rule_severity_enum"),
        nullable=False,
        default=RuleSeverityEnum.MEDIUM
    )
    status = Column(
        SQLEnum(RuleStatusEnum, name="dq_rule_status_enum"),
        nullable=False,
        default=RuleStatusEnum.ACTIVE
    )

    # Escopo
    entity_type = Column(String(100), nullable=False)  # Ex: "lead", "client", "contact"
    field_name = Column(String(100), nullable=True)  # Campo específico ou None para entidade
    applies_to_all = Column(Boolean, default=False)

    # Configuração da regra
    condition = Column(Text, nullable=True)  # Expressão ou SQL
    parameters = Column(JSONB, default=dict)  # Parâmetros da regra
    threshold = Column(Float, nullable=True)  # Limiar para violação

    # Para regex
    regex_pattern = Column(String(500), nullable=True)

    # Para range
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)

    # Para length
    min_length = Column(Integer, nullable=True)
    max_length = Column(Integer, nullable=True)

    # Para enum
    allowed_values = Column(JSONB, default=list)

    # Para foreign key
    reference_table = Column(String(100), nullable=True)
    reference_field = Column(String(100), nullable=True)

    # Para cross-field
    related_fields = Column(JSONB, default=list)
    cross_field_condition = Column(Text, nullable=True)

    # Ação em caso de violação
    action_on_violation = Column(String(50), default="flag")  # flag, reject, fix, warn
    auto_fix_enabled = Column(Boolean, default=False)
    fix_function = Column(String(100), nullable=True)  # Função de correção
    fix_value = Column(String(500), nullable=True)  # Valor padrão para correção

    # Mensagens
    error_message = Column(String(500), nullable=True)
    error_message_template = Column(String(500), nullable=True)
    suggestion = Column(String(500), nullable=True)

    # Prioridade e ordenação
    priority = Column(Integer, default=50)  # 1-100
    execution_order = Column(Integer, default=0)

    # Agrupamento
    rule_group = Column(String(100), nullable=True)
    tags = Column(JSONB, default=list)

    # Métricas
    total_checks = Column(Integer, default=0)
    total_violations = Column(Integer, default=0)
    last_violation_at = Column(DateTime, nullable=True)
    violation_rate = Column(Float, default=0.0)

    # Sistema
    is_system = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False)

    # Ownership
    created_by = Column(UUID(as_uuid=True), nullable=True)
    organization_id = Column(UUID(as_uuid=True), nullable=True, index=True)

    # Metadados
    extra_metadata = Column(JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<DataQualityRule(id={self.id}, code={self.code}, type={self.rule_type})>"

    @property
    def is_validation_rule(self) -> bool:
        """Verifica se é regra de validação."""
        validation_types = [
            RuleTypeEnum.NOT_NULL, RuleTypeEnum.UNIQUE, RuleTypeEnum.FORMAT,
            RuleTypeEnum.RANGE, RuleTypeEnum.LENGTH, RuleTypeEnum.ENUM,
            RuleTypeEnum.REGEX, RuleTypeEnum.CPF_VALID, RuleTypeEnum.CNPJ_VALID,
            RuleTypeEnum.EMAIL_VALID, RuleTypeEnum.PHONE_VALID
        ]
        return self.rule_type in validation_types

    @property
    def is_standardization_rule(self) -> bool:
        """Verifica se é regra de padronização."""
        std_types = [
            RuleTypeEnum.UPPERCASE, RuleTypeEnum.LOWERCASE, RuleTypeEnum.TRIM,
            RuleTypeEnum.NORMALIZE, RuleTypeEnum.PHONE_FORMAT, RuleTypeEnum.CPF_FORMAT,
            RuleTypeEnum.CNPJ_FORMAT, RuleTypeEnum.CEP_FORMAT, RuleTypeEnum.EMAIL_FORMAT,
            RuleTypeEnum.DATE_FORMAT
        ]
        return self.rule_type in std_types

    def increment_check(self, violated: bool = False) -> None:
        """Incrementa contadores de verificação."""
        self.total_checks += 1
        if violated:
            self.total_violations += 1
            self.last_violation_at = datetime.utcnow()
        self._update_violation_rate()

    def _update_violation_rate(self) -> None:
        """Atualiza taxa de violação."""
        if self.total_checks > 0:
            self.violation_rate = (self.total_violations / self.total_checks) * 100

    def get_error_message(self, context: Dict[str, Any] = None) -> str:
        """Retorna mensagem de erro formatada."""
        if self.error_message_template and context:
            try:
                return self.error_message_template.format(**context)
            except KeyError:
                pass
        return self.error_message or f"Violação da regra {self.code}"

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": str(self.id),
            "code": self.code,
            "name": self.name,
            "rule_type": self.rule_type.value,
            "category": self.category.value,
            "severity": self.severity.value,
            "status": self.status.value,
            "entity_type": self.entity_type,
            "field_name": self.field_name,
            "violation_rate": self.violation_rate,
            "total_checks": self.total_checks,
            "is_active": self.is_active,
        }
