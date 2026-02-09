"""
Modelo de Resultado de Validacao.

Define estruturas para validacao de dados extraidos,
incluindo regras, resultados e estatisticas.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


class ValidationType(StrEnum):
    """Tipos de validacao."""

    # Formato
    FORMAT = "format"
    REGEX = "regex"
    LENGTH = "length"
    RANGE = "range"

    # Documento
    CPF = "cpf"
    CNPJ = "cnpj"
    EMAIL = "email"
    PHONE = "phone"
    DATE = "date"
    CEP = "cep"

    # Financeiro
    BANK_ACCOUNT = "bank_account"
    BOLETO_LINE = "boleto_line"
    NFE_KEY = "nfe_key"

    # Negocio
    REQUIRED = "required"
    UNIQUE = "unique"
    REFERENCE = "reference"
    CROSS_FIELD = "cross_field"
    BUSINESS_RULE = "business_rule"

    # Consistencia
    CONSISTENCY = "consistency"
    CHECKSUM = "checksum"
    LUHN = "luhn"

    # Externo
    EXTERNAL_API = "external_api"
    DATABASE = "database"

    # Customizado
    CUSTOM = "custom"


class ValidationSeverity(StrEnum):
    """Severidade da validacao."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationStatus(StrEnum):
    """Status da validacao."""

    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class ValidationRule:
    """
    Regra de validacao.

    Attributes:
        id: Identificador unico
        name: Nome da regra
        validation_type: Tipo de validacao
        field_name: Campo a validar
        params: Parametros da validacao
        error_message: Mensagem de erro
        severity: Severidade
        is_active: Se esta ativa
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str | None = None
    validation_type: ValidationType = ValidationType.FORMAT
    field_name: str = ""
    field_names: list[str] = field(default_factory=list)  # Para cross-field

    # Parametros
    params: dict[str, Any] = field(default_factory=dict)
    pattern: str | None = None
    min_value: Any | None = None
    max_value: Any | None = None
    min_length: int | None = None
    max_length: int | None = None
    allowed_values: list[Any] = field(default_factory=list)
    reference_field: str | None = None

    # Mensagens
    error_message: str = "Validacao falhou"
    error_message_template: str | None = None
    suggestion: str | None = None

    # Configuracoes
    severity: ValidationSeverity = ValidationSeverity.ERROR
    is_active: bool = True
    stop_on_failure: bool = False
    order: int = 0

    # Funcao customizada
    custom_validator: Callable | None = None

    def format_error_message(self, value: Any, **kwargs: Any) -> str:
        """Formata mensagem de erro."""
        if self.error_message_template:
            try:
                return self.error_message_template.format(
                    value=value,
                    field=self.field_name,
                    **self.params,
                    **kwargs,
                )
            except (KeyError, ValueError):
                pass
        return self.error_message

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionario."""
        return {
            "id": self.id,
            "name": self.name,
            "validation_type": self.validation_type.value,
            "field_name": self.field_name,
            "params": self.params,
            "error_message": self.error_message,
            "severity": self.severity.value,
            "is_active": self.is_active,
        }


@dataclass
class FieldValidationResult:
    """Resultado de validacao de um campo."""

    field_name: str = ""
    status: ValidationStatus = ValidationStatus.PENDING
    is_valid: bool = True
    value: Any = None
    validated_value: Any = None

    # Resultados
    rules_passed: list[str] = field(default_factory=list)
    rules_failed: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    # Correcoes
    auto_corrected: bool = False
    original_value: Any | None = None
    correction_applied: str | None = None

    # Metadados
    validation_time_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_error(self, message: str, rule_name: str | None = None) -> None:
        """Adiciona erro."""
        self.errors.append(message)
        self.is_valid = False
        self.status = ValidationStatus.FAILED
        if rule_name:
            self.rules_failed.append(rule_name)

    def add_warning(self, message: str) -> None:
        """Adiciona aviso."""
        self.warnings.append(message)

    def add_suggestion(self, suggestion: str) -> None:
        """Adiciona sugestao."""
        self.suggestions.append(suggestion)

    def mark_passed(self, rule_name: str) -> None:
        """Marca regra como passou."""
        self.rules_passed.append(rule_name)

    def apply_correction(self, corrected_value: Any, correction_type: str) -> None:
        """Aplica correcao automatica."""
        if not self.auto_corrected:
            self.original_value = self.value
        self.validated_value = corrected_value
        self.auto_corrected = True
        self.correction_applied = correction_type

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionario."""
        return {
            "field_name": self.field_name,
            "status": self.status.value,
            "is_valid": self.is_valid,
            "value": str(self.value) if self.value else None,
            "validated_value": str(self.validated_value) if self.validated_value else None,
            "errors": self.errors,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "auto_corrected": self.auto_corrected,
            "original_value": str(self.original_value) if self.original_value else None,
            "rules_passed": len(self.rules_passed),
            "rules_failed": len(self.rules_failed),
        }


@dataclass
class ValidationResult:
    """
    Resultado completo da validacao do documento.

    Attributes:
        id: Identificador unico
        document_id: ID do documento
        status: Status geral
        is_valid: Se documento e valido
        field_results: Resultados por campo
        summary: Resumo da validacao
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    document_id: str = ""
    template_id: str | None = None

    # Status
    status: ValidationStatus = ValidationStatus.PENDING
    is_valid: bool = True
    overall_score: float = 0.0

    # Resultados por campo
    field_results: dict[str, FieldValidationResult] = field(default_factory=dict)

    # Contadores
    total_fields: int = 0
    fields_validated: int = 0
    fields_passed: int = 0
    fields_failed: int = 0
    fields_with_warnings: int = 0
    fields_auto_corrected: int = 0

    # Erros e avisos globais
    global_errors: list[str] = field(default_factory=list)
    global_warnings: list[str] = field(default_factory=list)

    # Cross-field validations
    cross_field_results: list[dict[str, Any]] = field(default_factory=list)

    # Performance
    total_validation_time_ms: int = 0
    rules_executed: int = 0

    # Metadados
    validated_by: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_field_result(self, result: FieldValidationResult) -> None:
        """Adiciona resultado de campo."""
        self.field_results[result.field_name] = result
        self.fields_validated += 1

        if result.is_valid:
            self.fields_passed += 1
        else:
            self.fields_failed += 1
            self.is_valid = False

        if result.warnings:
            self.fields_with_warnings += 1

        if result.auto_corrected:
            self.fields_auto_corrected += 1

        self._update_score()

    def add_global_error(self, error: str) -> None:
        """Adiciona erro global."""
        self.global_errors.append(error)
        self.is_valid = False
        self.status = ValidationStatus.FAILED

    def add_global_warning(self, warning: str) -> None:
        """Adiciona aviso global."""
        self.global_warnings.append(warning)

    def add_cross_field_result(
        self,
        fields: list[str],
        rule_name: str,
        passed: bool,
        message: str,
    ) -> None:
        """Adiciona resultado de validacao cross-field."""
        self.cross_field_results.append(
            {
                "fields": fields,
                "rule": rule_name,
                "passed": passed,
                "message": message,
            }
        )
        if not passed:
            self.is_valid = False

    def _update_score(self) -> None:
        """Atualiza score geral."""
        if self.fields_validated == 0:
            self.overall_score = 0.0
        else:
            self.overall_score = self.fields_passed / self.fields_validated

    def finalize(self) -> None:
        """Finaliza validacao."""
        self.total_fields = len(self.field_results)

        if self.fields_failed > 0 or self.global_errors:
            self.status = ValidationStatus.FAILED
            self.is_valid = False
        else:
            self.status = ValidationStatus.PASSED
            self.is_valid = True

        self._update_score()

    def get_errors(self) -> list[str]:
        """Obtem todos os erros."""
        errors = list(self.global_errors)
        for result in self.field_results.values():
            errors.extend(result.errors)
        return errors

    def get_warnings(self) -> list[str]:
        """Obtem todos os avisos."""
        warnings = list(self.global_warnings)
        for result in self.field_results.values():
            warnings.extend(result.warnings)
        return warnings

    def get_suggestions(self) -> list[str]:
        """Obtem todas as sugestoes."""
        suggestions = []
        for result in self.field_results.values():
            suggestions.extend(result.suggestions)
        return suggestions

    def get_corrected_data(self) -> dict[str, Any]:
        """Obtem dados corrigidos."""
        data = {}
        for field_name, result in self.field_results.items():
            if result.auto_corrected:
                data[field_name] = result.validated_value
            else:
                data[field_name] = result.value
        return data

    def get_summary(self) -> dict[str, Any]:
        """Obtem resumo da validacao."""
        return {
            "status": self.status.value,
            "is_valid": self.is_valid,
            "overall_score": round(self.overall_score * 100, 1),
            "total_fields": self.total_fields,
            "fields_passed": self.fields_passed,
            "fields_failed": self.fields_failed,
            "fields_with_warnings": self.fields_with_warnings,
            "fields_auto_corrected": self.fields_auto_corrected,
            "total_errors": len(self.get_errors()),
            "total_warnings": len(self.get_warnings()),
            "validation_time_ms": self.total_validation_time_ms,
        }

    def to_dict(self) -> dict[str, Any]:
        """Converte para dicionario."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "template_id": self.template_id,
            "summary": self.get_summary(),
            "field_results": {k: v.to_dict() for k, v in self.field_results.items()},
            "global_errors": self.global_errors,
            "global_warnings": self.global_warnings,
            "cross_field_results": self.cross_field_results,
            "created_at": self.created_at.isoformat(),
        }


# Validadores builtin
def validate_cpf(value: str) -> bool:
    """Valida CPF."""
    cpf = "".join(filter(str.isdigit, value))
    if len(cpf) != 11:
        return False
    if cpf == cpf[0] * 11:
        return False

    # Primeiro digito
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    d1 = 0 if resto < 2 else 11 - resto
    if int(cpf[9]) != d1:
        return False

    # Segundo digito
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    d2 = 0 if resto < 2 else 11 - resto
    return int(cpf[10]) == d2


def validate_cnpj(value: str) -> bool:
    """Valida CNPJ."""
    cnpj = "".join(filter(str.isdigit, value))
    if len(cnpj) != 14:
        return False
    if cnpj == cnpj[0] * 14:
        return False

    # Primeiro digito
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
    resto = soma % 11
    d1 = 0 if resto < 2 else 11 - resto
    if int(cnpj[12]) != d1:
        return False

    # Segundo digito
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
    resto = soma % 11
    d2 = 0 if resto < 2 else 11 - resto
    return int(cnpj[13]) == d2


def validate_email(value: str) -> bool:
    """Valida email."""
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, value))


def validate_phone_br(value: str) -> bool:
    """Valida telefone brasileiro."""
    digits = "".join(filter(str.isdigit, value))
    return len(digits) in [10, 11]


def validate_cep(value: str) -> bool:
    """Valida CEP."""
    cep = "".join(filter(str.isdigit, value))
    return len(cep) == 8


BUILTIN_VALIDATORS: dict[ValidationType, Callable[[str], bool]] = {
    ValidationType.CPF: validate_cpf,
    ValidationType.CNPJ: validate_cnpj,
    ValidationType.EMAIL: validate_email,
    ValidationType.PHONE: validate_phone_br,
    ValidationType.CEP: validate_cep,
}
