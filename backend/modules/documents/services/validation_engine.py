"""
Validation Engine Service.

Motor de validacao de dados extraidos com suporte a
validadores builtin e customizados.
"""

import logging
import re
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from ..models.extracted_field import ExtractedField, FieldType
from ..models.validation_result import (
    BUILTIN_VALIDATORS,
    FieldValidationResult,
    ValidationResult,
    ValidationRule,
    ValidationSeverity,
    ValidationStatus,
    ValidationType,
)

logger = logging.getLogger(__name__)


@dataclass
class ValidationConfig:
    """Configuracao do motor de validacao."""

    # Comportamento
    stop_on_first_error: bool = False
    validate_required: bool = True
    auto_correct: bool = True

    # Limites
    max_errors_per_field: int = 5
    timeout_seconds: int = 30

    # Correcoes automaticas
    corrections: dict[str, bool] = field(
        default_factory=lambda: {
            "trim_whitespace": True,
            "normalize_unicode": True,
            "fix_encoding": True,
            "format_cpf": True,
            "format_cnpj": True,
            "format_phone": True,
            "format_date": True,
        }
    )


class ValidationEngine:
    """
    Motor de validacao de dados.

    Valida campos extraidos usando regras configuradas,
    validadores builtin e customizados.
    """

    # Mapeamento de FieldType para ValidationType
    FIELD_VALIDATORS: dict[FieldType, ValidationType] = {
        FieldType.CPF: ValidationType.CPF,
        FieldType.CNPJ: ValidationType.CNPJ,
        FieldType.EMAIL: ValidationType.EMAIL,
        FieldType.PHONE: ValidationType.PHONE,
        FieldType.ZIP_CODE: ValidationType.CEP,
        FieldType.DATE: ValidationType.DATE,
        FieldType.NFE_KEY: ValidationType.NFE_KEY,
        FieldType.BOLETO_LINE: ValidationType.BOLETO_LINE,
    }

    def __init__(self, config: ValidationConfig | None = None):
        """
        Inicializa motor de validacao.

        Args:
            config: Configuracao do motor
        """
        self.config = config or ValidationConfig()
        self._custom_validators: dict[str, Callable] = {}
        self._rules_by_field: dict[str, list[ValidationRule]] = {}

    async def validate(
        self,
        fields: list[ExtractedField],
        rules: list[ValidationRule] | None = None,
        document_id: str | None = None,
    ) -> ValidationResult:
        """
        Valida lista de campos extraidos.

        Args:
            fields: Campos a validar
            rules: Regras adicionais de validacao
            document_id: ID do documento

        Returns:
            Resultado da validacao
        """
        start_time = time.time()

        result = ValidationResult(
            document_id=document_id or "",
            total_fields=len(fields),
        )

        # Indexar regras por campo
        rules_map: dict[str, list[ValidationRule]] = {}
        if rules:
            for rule in rules:
                if rule.is_active:
                    field_name = rule.field_name
                    if field_name not in rules_map:
                        rules_map[field_name] = []
                    rules_map[field_name].append(rule)

        # Validar cada campo
        for val_field in fields:
            field_result = await self._validate_field(
                val_field,
                rules_map.get(val_field.field_name, []),
            )
            result.add_field_result(field_result)

            if self.config.stop_on_first_error and field_result.status == ValidationStatus.FAILED:
                break

        # Cross-field validations
        if rules:
            cross_rules = [r for r in rules if r.validation_type == ValidationType.CROSS_FIELD]
            for rule in cross_rules:
                self._validate_cross_field(result, fields, rule)

        # Finalizar
        result.total_validation_time_ms = int((time.time() - start_time) * 1000)
        result.finalize()

        return result

    async def _validate_field(
        self,
        field: ExtractedField,
        rules: list[ValidationRule],
    ) -> FieldValidationResult:
        """Valida um campo individual."""
        result = FieldValidationResult(
            field_name=field.field_name,
            value=field.raw_value,
            validated_value=field.normalized_value or field.raw_value,
        )

        start_time = time.time()

        # Validacao obrigatoria
        if self.config.validate_required and field.is_required:
            if not field.raw_value or not field.raw_value.strip():
                result.add_error("Campo obrigatorio nao preenchido", "required")
                result.validation_time_ms = int((time.time() - start_time) * 1000)
                return result

        # Validacao por tipo
        type_validator = self.FIELD_VALIDATORS.get(field.field_type)
        if type_validator and type_validator in BUILTIN_VALIDATORS:
            validator = BUILTIN_VALIDATORS[type_validator]
            value = field.normalized_value or field.raw_value
            if value:
                value_str = str(value)
                if not validator(value_str):
                    result.add_error(
                        f"Valor invalido para {field.field_type.value}",
                        f"type_{field.field_type.value}",
                    )
                else:
                    result.mark_passed(f"type_{field.field_type.value}")

        # Aplicar regras customizadas
        for rule in rules:
            self._apply_rule(result, field, rule)
            if self.config.stop_on_first_error and result.status == ValidationStatus.FAILED:
                break

        # Auto-correcoes
        if self.config.auto_correct:
            self._apply_corrections(result, field)

        # Atualizar status
        if not result.errors:
            result.status = ValidationStatus.PASSED
            result.is_valid = True

        result.validation_time_ms = int((time.time() - start_time) * 1000)

        return result

    def _apply_rule(
        self,
        result: FieldValidationResult,
        field: ExtractedField,
        rule: ValidationRule,
    ) -> None:
        """Aplica uma regra de validacao."""
        value = str(field.normalized_value or field.raw_value or "")

        try:
            passed = False

            if rule.validation_type == ValidationType.REQUIRED:
                passed = bool(value.strip())

            elif rule.validation_type == ValidationType.FORMAT:
                if rule.pattern:
                    passed = bool(re.match(rule.pattern, value))

            elif rule.validation_type == ValidationType.REGEX:
                if rule.pattern:
                    passed = bool(re.search(rule.pattern, value))

            elif rule.validation_type == ValidationType.LENGTH:
                length = len(value)
                min_len = rule.min_length or 0
                max_len = rule.max_length or float("inf")
                passed = min_len <= length <= max_len

            elif rule.validation_type == ValidationType.RANGE:
                try:
                    num_value = float(value.replace(",", "."))
                    min_val = rule.min_value if rule.min_value is not None else float("-inf")
                    max_val = rule.max_value if rule.max_value is not None else float("inf")
                    passed = min_val <= num_value <= max_val
                except ValueError:
                    passed = False

            elif rule.validation_type in BUILTIN_VALIDATORS:
                validator = BUILTIN_VALIDATORS[rule.validation_type]
                passed = validator(value)

            elif rule.validation_type == ValidationType.CUSTOM:
                if rule.custom_validator:
                    passed = rule.custom_validator(value, field, rule.params)
                elif rule.name in self._custom_validators:
                    passed = self._custom_validators[rule.name](value, field, rule.params)
                else:
                    logger.warning(f"Validador customizado nao encontrado: {rule.name}")
                    passed = True

            # Registrar resultado
            if passed:
                result.mark_passed(rule.name)
            else:
                message = rule.format_error_message(value)
                if rule.severity == ValidationSeverity.ERROR:
                    result.add_error(message, rule.name)
                elif rule.severity == ValidationSeverity.WARNING:
                    result.add_warning(message)

                if rule.suggestion:
                    result.add_suggestion(rule.suggestion)

        except Exception as e:
            logger.error(f"Erro ao aplicar regra {rule.name}: {e}")
            result.add_error(f"Erro na validacao: {str(e)}", rule.name)

        result.metadata["rules_executed"] = result.metadata.get("rules_executed", 0) + 1

    def _validate_cross_field(
        self,
        result: ValidationResult,
        fields: list[ExtractedField],
        rule: ValidationRule,
    ) -> None:
        """Valida regra cross-field."""
        # Obter campos envolvidos
        field_values = {}
        for cf_field in fields:
            if cf_field.field_name in rule.field_names:
                field_values[cf_field.field_name] = cf_field.normalized_value or cf_field.raw_value

        # Verificar se todos os campos existem
        if len(field_values) != len(rule.field_names):
            result.add_cross_field_result(
                rule.field_names,
                rule.name,
                False,
                "Campos necessarios nao encontrados",
            )
            return

        # Aplicar validador cross-field
        try:
            if rule.custom_validator:
                passed = rule.custom_validator(field_values, rule.params)
            else:
                # Validacao padrao: verificar consistencia
                passed = self._default_cross_validation(field_values, rule)

            message = "OK" if passed else rule.error_message
            result.add_cross_field_result(rule.field_names, rule.name, passed, message)

        except Exception as e:
            logger.error(f"Erro na validacao cross-field: {e}")
            result.add_cross_field_result(
                rule.field_names,
                rule.name,
                False,
                f"Erro: {str(e)}",
            )

    def _default_cross_validation(
        self,
        field_values: dict[str, Any],
        rule: ValidationRule,
    ) -> bool:
        """Validacao cross-field padrao."""
        validation_type = rule.params.get("type", "not_empty")

        if validation_type == "not_empty":
            # Todos devem ter valor
            return all(v for v in field_values.values())

        elif validation_type == "one_required":
            # Pelo menos um deve ter valor
            return any(v for v in field_values.values())

        elif validation_type == "equal":
            # Todos devem ser iguais
            values = list(field_values.values())
            return all(v == values[0] for v in values)

        elif validation_type == "sum":
            # Soma deve ser igual a valor esperado
            try:
                total = sum(Decimal(str(v)) for v in field_values.values() if v)
                expected = Decimal(str(rule.params.get("expected", 0)))
                return total == expected
            except (ValueError, TypeError):
                return False

        elif validation_type == "date_order":
            # Datas devem estar em ordem
            try:
                dates = []
                for v in field_values.values():
                    if isinstance(v, (date, datetime)):
                        dates.append(v)
                    elif isinstance(v, str):
                        dates.append(datetime.strptime(v, "%d/%m/%Y").date())
                return dates == sorted(dates)
            except (ValueError, TypeError):
                return False

        return True

    def _apply_corrections(
        self,
        result: FieldValidationResult,
        field: ExtractedField,
    ) -> None:
        """Aplica correcoes automaticas."""
        value = result.validated_value
        if not value:
            return

        original = value
        corrected = str(value)

        # Trim whitespace
        if self.config.corrections.get("trim_whitespace"):
            corrected = corrected.strip()
            corrected = re.sub(r"\s+", " ", corrected)

        # Correcoes por tipo
        if field.field_type == FieldType.CPF and self.config.corrections.get("format_cpf"):
            digits = "".join(filter(str.isdigit, corrected))
            if len(digits) == 11:
                corrected = f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"

        elif field.field_type == FieldType.CNPJ and self.config.corrections.get("format_cnpj"):
            digits = "".join(filter(str.isdigit, corrected))
            if len(digits) == 14:
                corrected = f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"

        elif field.field_type == FieldType.PHONE and self.config.corrections.get("format_phone"):
            digits = "".join(filter(str.isdigit, corrected))
            if len(digits) == 11:
                corrected = f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
            elif len(digits) == 10:
                corrected = f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"

        elif field.field_type == FieldType.DATE and self.config.corrections.get("format_date"):
            # Tentar normalizar formato de data
            patterns = [
                (r"(\d{2})/(\d{2})/(\d{4})", r"\1/\2/\3"),
                (r"(\d{2})-(\d{2})-(\d{4})", r"\1/\2/\3"),
                (r"(\d{4})-(\d{2})-(\d{2})", r"\3/\2/\1"),
            ]
            for pattern, replacement in patterns:
                match = re.match(pattern, corrected)
                if match:
                    corrected = re.sub(pattern, replacement, corrected)
                    break

        # Aplicar correcao se houve mudanca
        if corrected != original:
            result.apply_correction(corrected, "auto_format")

    def register_validator(
        self,
        name: str,
        validator: Callable[[str, ExtractedField, dict], bool],
    ) -> None:
        """
        Registra validador customizado.

        Args:
            name: Nome do validador
            validator: Funcao de validacao
        """
        self._custom_validators[name] = validator

    def add_field_rules(self, field_name: str, rules: list[ValidationRule]) -> None:
        """
        Adiciona regras para um campo.

        Args:
            field_name: Nome do campo
            rules: Regras de validacao
        """
        if field_name not in self._rules_by_field:
            self._rules_by_field[field_name] = []
        self._rules_by_field[field_name].extend(rules)

    def create_rule(
        self,
        name: str,
        field_name: str,
        validation_type: ValidationType,
        error_message: str,
        **kwargs,
    ) -> ValidationRule:
        """
        Cria uma regra de validacao.

        Args:
            name: Nome da regra
            field_name: Campo alvo
            validation_type: Tipo de validacao
            error_message: Mensagem de erro
            **kwargs: Parametros adicionais

        Returns:
            Regra criada
        """
        return ValidationRule(
            name=name,
            field_name=field_name,
            validation_type=validation_type,
            error_message=error_message,
            pattern=kwargs.get("pattern"),
            min_length=kwargs.get("min_length"),
            max_length=kwargs.get("max_length"),
            min_value=kwargs.get("min_value"),
            max_value=kwargs.get("max_value"),
            severity=kwargs.get("severity", ValidationSeverity.ERROR),
            suggestion=kwargs.get("suggestion"),
            params=kwargs.get("params", {}),
        )

    def validate_single(
        self,
        value: str,
        validation_type: ValidationType,
    ) -> bool:
        """
        Valida um valor unico.

        Args:
            value: Valor a validar
            validation_type: Tipo de validacao

        Returns:
            True se valido
        """
        if validation_type in BUILTIN_VALIDATORS:
            return BUILTIN_VALIDATORS[validation_type](value)
        return False

    def get_supported_validations(self) -> list[str]:
        """Retorna validacoes suportadas."""
        builtin = [v.value for v in ValidationType]
        custom = list(self._custom_validators.keys())
        return builtin + custom


# Validadores builtin adicionais
def validate_nfe_key(value: str) -> bool:
    """Valida chave de acesso NFe."""
    digits = "".join(filter(str.isdigit, value))
    if len(digits) != 44:
        return False

    # Validar digito verificador
    weights = [2, 3, 4, 5, 6, 7, 8, 9] * 6
    total = sum(int(d) * w for d, w in zip(reversed(digits[:43]), weights, strict=False))
    remainder = total % 11
    dv = 0 if remainder < 2 else 11 - remainder

    return int(digits[43]) == dv


def validate_boleto_line(value: str) -> bool:
    """Valida linha digitavel de boleto."""
    digits = "".join(filter(str.isdigit, value))
    if len(digits) not in [47, 48]:
        return False
    return True


def validate_date_br(value: str) -> bool:
    """Valida data no formato brasileiro."""
    pattern = r"^(\d{2})/(\d{2})/(\d{4})$"
    match = re.match(pattern, value)
    if not match:
        return False

    day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))

    if month < 1 or month > 12:
        return False
    if day < 1 or day > 31:
        return False
    if year < 1900 or year > 2100:
        return False

    # Verificar dias do mes
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        days_in_month[1] = 29

    return day <= days_in_month[month - 1]


# Adicionar validadores extras ao dicionario
BUILTIN_VALIDATORS[ValidationType.NFE_KEY] = validate_nfe_key
BUILTIN_VALIDATORS[ValidationType.BOLETO_LINE] = validate_boleto_line
BUILTIN_VALIDATORS[ValidationType.DATE] = validate_date_br
