"""
Modelo de Template de Extracao.

Define templates para extracao estruturada de dados de documentos,
com regras, campos e padroes reutilizaveis.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Pattern
import re
from uuid import uuid4


class TemplateCategory(str, Enum):
    """Categorias de templates."""

    FINANCIAL = "financial"
    PERSONAL = "personal"
    BUSINESS = "business"
    GOVERNMENT = "government"
    HEALTHCARE = "healthcare"
    LEGAL = "legal"
    EDUCATION = "education"
    OTHER = "other"


class TemplateStatus(str, Enum):
    """Status do template."""

    DRAFT = "draft"
    ACTIVE = "active"
    TESTING = "testing"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class RuleType(str, Enum):
    """Tipos de regras de extracao."""

    REGEX = "regex"
    KEYWORD_ANCHOR = "keyword_anchor"
    POSITION = "position"
    TABLE_CELL = "table_cell"
    AFTER_LABEL = "after_label"
    BETWEEN_LABELS = "between_labels"
    LINE_MATCH = "line_match"
    NLP_ENTITY = "nlp_entity"
    BARCODE = "barcode"
    CUSTOM = "custom"


class PostProcessor(str, Enum):
    """Pos-processadores disponiveis."""

    STRIP = "strip"
    UPPERCASE = "uppercase"
    LOWERCASE = "lowercase"
    REMOVE_SPACES = "remove_spaces"
    DIGITS_ONLY = "digits_only"
    LETTERS_ONLY = "letters_only"
    FORMAT_CPF = "format_cpf"
    FORMAT_CNPJ = "format_cnpj"
    FORMAT_PHONE = "format_phone"
    FORMAT_DATE = "format_date"
    FORMAT_CURRENCY = "format_currency"
    REMOVE_SPECIAL = "remove_special"
    NORMALIZE_UNICODE = "normalize_unicode"
    CUSTOM = "custom"


@dataclass
class TemplateRule:
    """
    Regra de extracao de campo.

    Attributes:
        rule_type: Tipo da regra
        pattern: Padrao regex ou texto
        anchor: Texto ancora
        group: Grupo de captura regex
        position: Posicao no documento
        fallback_rules: Regras alternativas
        post_processors: Pos-processadores
    """

    rule_type: RuleType = RuleType.REGEX
    pattern: Optional[str] = None
    anchor: Optional[str] = None
    anchor_position: str = "before"  # before, after, above, below
    anchor_offset: int = 0  # Offset em linhas/caracteres

    # Para regex
    group: int = 0  # Grupo de captura
    flags: int = re.IGNORECASE | re.MULTILINE

    # Para posicao
    page: Optional[int] = None
    x_min: Optional[int] = None
    x_max: Optional[int] = None
    y_min: Optional[int] = None
    y_max: Optional[int] = None

    # Para tabela
    row: Optional[int] = None
    column: Optional[int] = None
    header: Optional[str] = None

    # Fallback
    fallback_rules: List["TemplateRule"] = field(default_factory=list)

    # Pos-processamento
    post_processors: List[PostProcessor] = field(default_factory=list)

    # Validacao
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_chars: Optional[str] = None
    validation_regex: Optional[str] = None

    def compile_pattern(self) -> Optional[Pattern]:
        """Compila padrao regex."""
        if self.pattern:
            try:
                return re.compile(self.pattern, self.flags)
            except re.error:
                return None
        return None

    def apply_post_processors(self, value: str) -> str:
        """Aplica pos-processadores ao valor."""
        result = value

        for processor in self.post_processors:
            if processor == PostProcessor.STRIP:
                result = result.strip()
            elif processor == PostProcessor.UPPERCASE:
                result = result.upper()
            elif processor == PostProcessor.LOWERCASE:
                result = result.lower()
            elif processor == PostProcessor.REMOVE_SPACES:
                result = result.replace(" ", "")
            elif processor == PostProcessor.DIGITS_ONLY:
                result = "".join(filter(str.isdigit, result))
            elif processor == PostProcessor.LETTERS_ONLY:
                result = "".join(filter(str.isalpha, result))
            elif processor == PostProcessor.REMOVE_SPECIAL:
                result = re.sub(r"[^a-zA-Z0-9\s]", "", result)

        return result

    def validate_value(self, value: str) -> bool:
        """Valida valor extraido."""
        if self.min_length and len(value) < self.min_length:
            return False
        if self.max_length and len(value) > self.max_length:
            return False
        if self.allowed_chars:
            if not all(c in self.allowed_chars for c in value):
                return False
        if self.validation_regex:
            if not re.match(self.validation_regex, value):
                return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "rule_type": self.rule_type.value,
            "pattern": self.pattern,
            "anchor": self.anchor,
            "anchor_position": self.anchor_position,
            "group": self.group,
            "post_processors": [p.value for p in self.post_processors],
        }


@dataclass
class TemplateField:
    """
    Definicao de campo no template.

    Attributes:
        name: Nome do campo
        label: Label para exibicao
        field_type: Tipo do campo
        rules: Regras de extracao
        required: Se e obrigatorio
        default_value: Valor padrao
        description: Descricao do campo
    """

    name: str = ""
    label: Optional[str] = None
    field_type: str = "text"  # text, number, date, currency, cpf, cnpj, etc
    group: Optional[str] = None  # Agrupamento logico

    # Regras
    rules: List[TemplateRule] = field(default_factory=list)
    primary_rule: Optional[TemplateRule] = None

    # Configuracoes
    required: bool = False
    default_value: Optional[str] = None
    description: Optional[str] = None

    # Validacao
    min_confidence: float = 0.5
    validators: List[str] = field(default_factory=list)

    # Formatacao
    format_pattern: Optional[str] = None
    display_format: Optional[str] = None

    # Dependencias
    depends_on: Optional[str] = None
    conditional_rules: Dict[str, List[TemplateRule]] = field(default_factory=dict)

    # Metadados
    order: int = 0
    is_key_field: bool = False  # Campo chave para identificacao
    is_searchable: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Inicializa campos derivados."""
        if not self.label:
            self.label = self.name.replace("_", " ").title()
        if self.rules and not self.primary_rule:
            self.primary_rule = self.rules[0]

    def get_rules_for_condition(self, condition: str) -> List[TemplateRule]:
        """Obtem regras para uma condicao."""
        if condition in self.conditional_rules:
            return self.conditional_rules[condition]
        return self.rules

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "name": self.name,
            "label": self.label,
            "field_type": self.field_type,
            "group": self.group,
            "rules": [r.to_dict() for r in self.rules],
            "required": self.required,
            "default_value": self.default_value,
            "description": self.description,
            "min_confidence": self.min_confidence,
            "order": self.order,
            "is_key_field": self.is_key_field,
        }


@dataclass
class ExtractionTemplate:
    """
    Template completo de extracao.

    Attributes:
        id: Identificador unico
        tenant_id: ID do tenant
        name: Nome do template
        document_type: Tipo de documento
        category: Categoria
        fields: Campos a extrair
        detection_rules: Regras de deteccao do tipo
        version: Versao do template
        is_active: Se esta ativo
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    tenant_id: Optional[str] = None  # None = template global
    name: str = ""
    description: Optional[str] = None
    document_type: str = ""
    category: TemplateCategory = TemplateCategory.OTHER
    status: TemplateStatus = TemplateStatus.DRAFT

    # Campos
    fields: List[TemplateField] = field(default_factory=list)
    field_groups: Dict[str, List[str]] = field(default_factory=dict)

    # Deteccao
    detection_rules: List[TemplateRule] = field(default_factory=list)
    detection_keywords: List[str] = field(default_factory=list)
    detection_patterns: List[str] = field(default_factory=list)
    min_detection_score: float = 0.7

    # Configuracoes
    language: str = "pt"
    preprocessing: Dict[str, Any] = field(default_factory=dict)
    ocr_config: Dict[str, Any] = field(default_factory=dict)

    # Versionamento
    version: int = 1
    parent_version_id: Optional[str] = None
    changelog: List[str] = field(default_factory=list)

    # Estatisticas
    usage_count: int = 0
    success_count: int = 0
    avg_confidence: float = 0.0
    avg_processing_time_ms: int = 0

    # Metadados
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_official: bool = False
    is_public: bool = False

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None

    def get_field(self, name: str) -> Optional[TemplateField]:
        """Obtem campo por nome."""
        for fld in self.fields:
            if fld.name == name:
                return fld
        return None

    def get_required_fields(self) -> List[TemplateField]:
        """Obtem campos obrigatorios."""
        return [f for f in self.fields if f.required]

    def get_key_fields(self) -> List[TemplateField]:
        """Obtem campos chave."""
        return [f for f in self.fields if f.is_key_field]

    def get_fields_by_group(self, group: str) -> List[TemplateField]:
        """Obtem campos de um grupo."""
        return [f for f in self.fields if f.group == group]

    def add_field(self, field_: TemplateField) -> None:
        """Adiciona campo ao template."""
        field_.order = len(self.fields)
        self.fields.append(field_)
        self.updated_at = datetime.utcnow()

    def remove_field(self, name: str) -> bool:
        """Remove campo do template."""
        for i, fld in enumerate(self.fields):
            if fld.name == name:
                self.fields.pop(i)
                self.updated_at = datetime.utcnow()
                return True
        return False

    def activate(self) -> None:
        """Ativa o template."""
        self.status = TemplateStatus.ACTIVE
        self.published_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def deprecate(self) -> None:
        """Deprecia o template."""
        self.status = TemplateStatus.DEPRECATED
        self.updated_at = datetime.utcnow()

    def clone(self, new_name: Optional[str] = None) -> "ExtractionTemplate":
        """Clona o template."""
        import copy

        cloned = copy.deepcopy(self)
        cloned.id = str(uuid4())
        cloned.name = new_name or f"{self.name} (Copy)"
        cloned.status = TemplateStatus.DRAFT
        cloned.parent_version_id = self.id
        cloned.version = 1
        cloned.usage_count = 0
        cloned.success_count = 0
        cloned.created_at = datetime.utcnow()
        cloned.updated_at = datetime.utcnow()
        cloned.published_at = None
        return cloned

    def increment_version(self) -> None:
        """Incrementa versao do template."""
        self.version += 1
        self.updated_at = datetime.utcnow()

    def update_statistics(
        self, success: bool, confidence: float, processing_time_ms: int
    ) -> None:
        """Atualiza estatisticas de uso."""
        self.usage_count += 1
        if success:
            self.success_count += 1

        # Media movel de confianca
        if self.usage_count == 1:
            self.avg_confidence = confidence
            self.avg_processing_time_ms = processing_time_ms
        else:
            alpha = 0.1  # Fator de suavizacao
            self.avg_confidence = (
                alpha * confidence + (1 - alpha) * self.avg_confidence
            )
            self.avg_processing_time_ms = int(
                alpha * processing_time_ms + (1 - alpha) * self.avg_processing_time_ms
            )

    @property
    def success_rate(self) -> float:
        """Taxa de sucesso."""
        if self.usage_count == 0:
            return 0.0
        return self.success_count / self.usage_count

    def validate(self) -> List[str]:
        """Valida template."""
        errors = []

        if not self.name:
            errors.append("Nome do template e obrigatorio")
        if not self.document_type:
            errors.append("Tipo de documento e obrigatorio")
        if not self.fields:
            errors.append("Template deve ter pelo menos um campo")
        if not self.detection_rules and not self.detection_keywords:
            errors.append("Template deve ter regras de deteccao")

        # Validar campos
        field_names = set()
        for fld in self.fields:
            if not fld.name:
                errors.append("Campo sem nome encontrado")
            elif fld.name in field_names:
                errors.append(f"Campo duplicado: {fld.name}")
            else:
                field_names.add(fld.name)

            if not fld.rules:
                errors.append(f"Campo {fld.name} sem regras de extracao")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionario."""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "description": self.description,
            "document_type": self.document_type,
            "category": self.category.value,
            "status": self.status.value,
            "fields": [f.to_dict() for f in self.fields],
            "detection_keywords": self.detection_keywords,
            "version": self.version,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "avg_confidence": self.avg_confidence,
            "is_official": self.is_official,
            "is_public": self.is_public,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
