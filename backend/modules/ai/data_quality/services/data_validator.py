"""
DataValidator Service - Sprint 48.

Serviço de validação de dados contra regras de qualidade.
"""

import re
import uuid
from typing import Any

from modules.ai.data_quality.models import (
    DataQualityIssue,
    DataQualityRule,
    IssueStatusEnum,
    IssueTypeEnum,
    RuleTypeEnum,
)


class DataValidator:
    """Serviço de validação de dados."""

    def __init__(self):
        self.validators = {
            RuleTypeEnum.NOT_NULL: self._validate_not_null,
            RuleTypeEnum.UNIQUE: self._validate_unique,
            RuleTypeEnum.FORMAT: self._validate_format,
            RuleTypeEnum.RANGE: self._validate_range,
            RuleTypeEnum.LENGTH: self._validate_length,
            RuleTypeEnum.ENUM: self._validate_enum,
            RuleTypeEnum.REGEX: self._validate_regex,
            RuleTypeEnum.CPF_VALID: self._validate_cpf,
            RuleTypeEnum.CNPJ_VALID: self._validate_cnpj,
            RuleTypeEnum.EMAIL_VALID: self._validate_email,
            RuleTypeEnum.PHONE_VALID: self._validate_phone,
        }

    def validate_record(
        self, data: dict[str, Any], rules: list[DataQualityRule], entity_type: str, entity_id: uuid.UUID = None
    ) -> tuple[bool, list[DataQualityIssue], dict[str, Any]]:
        """
        Valida registro contra regras.

        Returns:
            Tuple[is_valid, issues, fixed_data]
        """
        issues = []
        fixed_data = data.copy()
        is_valid = True

        for rule in rules:
            if rule.field_name:
                # Regra para campo específico
                field_value = data.get(rule.field_name)
                result = self._apply_rule(rule, field_value, data)

                if not result["valid"]:
                    is_valid = False
                    issue = self._create_issue(
                        rule=rule,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        field_name=rule.field_name,
                        current_value=str(field_value) if field_value else None,
                        error_message=result.get("message"),
                        suggested_value=result.get("suggested_value"),
                    )
                    issues.append(issue)

                    # Auto-fix se habilitado
                    if rule.auto_fix_enabled and result.get("fixed_value") is not None:
                        fixed_data[rule.field_name] = result["fixed_value"]
            else:
                # Regra para registro inteiro
                result = self._apply_rule(rule, data, data)
                if not result["valid"]:
                    is_valid = False
                    issue = self._create_issue(
                        rule=rule, entity_type=entity_type, entity_id=entity_id, error_message=result.get("message")
                    )
                    issues.append(issue)

        return is_valid, issues, fixed_data

    def _apply_rule(self, rule: DataQualityRule, value: Any, full_data: dict[str, Any]) -> dict[str, Any]:
        """Aplica regra de validação."""
        validator = self.validators.get(rule.rule_type)
        if validator:
            return validator(value, rule, full_data)
        return {"valid": True}

    def _validate_not_null(self, value: Any, rule: DataQualityRule, full_data: dict[str, Any]) -> dict[str, Any]:
        """Valida campo não nulo."""
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return {
                "valid": False,
                "message": rule.get_error_message() or f"Campo {rule.field_name} é obrigatório",
                "issue_type": IssueTypeEnum.MISSING_VALUE,
            }
        return {"valid": True}

    def _validate_unique(self, value: Any, rule: DataQualityRule, full_data: dict[str, Any]) -> dict[str, Any]:
        """Valida unicidade (placeholder - requer verificação no banco)."""
        # Esta validação real seria feita no nível do serviço/repositório
        return {"valid": True}

    def _validate_format(self, value: Any, rule: DataQualityRule, full_data: dict[str, Any]) -> dict[str, Any]:
        """Valida formato usando regex."""
        if value is None:
            return {"valid": True}

        pattern = rule.regex_pattern or rule.parameters.get("pattern")
        if pattern:
            if not re.match(pattern, str(value)):
                return {
                    "valid": False,
                    "message": f"Formato inválido para {rule.field_name}",
                    "issue_type": IssueTypeEnum.INVALID_FORMAT,
                }
        return {"valid": True}

    def _validate_range(self, value: Any, rule: DataQualityRule, full_data: dict[str, Any]) -> dict[str, Any]:
        """Valida valor dentro de range."""
        if value is None:
            return {"valid": True}

        try:
            num_value = float(value)
            if rule.min_value is not None and num_value < rule.min_value:
                return {
                    "valid": False,
                    "message": f"Valor abaixo do mínimo ({rule.min_value})",
                    "issue_type": IssueTypeEnum.OUT_OF_RANGE,
                    "suggested_value": rule.min_value,
                }
            if rule.max_value is not None and num_value > rule.max_value:
                return {
                    "valid": False,
                    "message": f"Valor acima do máximo ({rule.max_value})",
                    "issue_type": IssueTypeEnum.OUT_OF_RANGE,
                    "suggested_value": rule.max_value,
                }
        except (ValueError, TypeError):
            return {"valid": False, "message": "Valor não é numérico", "issue_type": IssueTypeEnum.TYPE_MISMATCH}
        return {"valid": True}

    def _validate_length(self, value: Any, rule: DataQualityRule, full_data: dict[str, Any]) -> dict[str, Any]:
        """Valida comprimento de string."""
        if value is None:
            return {"valid": True}

        str_value = str(value)
        length = len(str_value)

        if rule.min_length is not None and length < rule.min_length:
            return {
                "valid": False,
                "message": f"Comprimento mínimo é {rule.min_length} caracteres",
                "issue_type": IssueTypeEnum.INVALID_VALUE,
            }
        if rule.max_length is not None and length > rule.max_length:
            return {
                "valid": False,
                "message": f"Comprimento máximo é {rule.max_length} caracteres",
                "issue_type": IssueTypeEnum.INVALID_VALUE,
                "fixed_value": str_value[: rule.max_length] if rule.auto_fix_enabled else None,
            }
        return {"valid": True}

    def _validate_enum(self, value: Any, rule: DataQualityRule, full_data: dict[str, Any]) -> dict[str, Any]:
        """Valida valor em lista de permitidos."""
        if value is None:
            return {"valid": True}

        allowed = rule.allowed_values or []
        if str(value) not in [str(v) for v in allowed]:
            return {
                "valid": False,
                "message": f"Valor deve ser um de: {', '.join(map(str, allowed))}",
                "issue_type": IssueTypeEnum.INVALID_VALUE,
            }
        return {"valid": True}

    def _validate_regex(self, value: Any, rule: DataQualityRule, full_data: dict[str, Any]) -> dict[str, Any]:
        """Valida contra padrão regex."""
        if value is None or not rule.regex_pattern:
            return {"valid": True}

        if not re.match(rule.regex_pattern, str(value)):
            return {
                "valid": False,
                "message": rule.get_error_message() or "Valor não corresponde ao padrão esperado",
                "issue_type": IssueTypeEnum.INVALID_FORMAT,
            }
        return {"valid": True}

    def _validate_cpf(self, value: Any, rule: DataQualityRule, full_data: dict[str, Any]) -> dict[str, Any]:
        """Valida CPF brasileiro."""
        if value is None:
            return {"valid": True}

        cpf = re.sub(r"\D", "", str(value))

        if len(cpf) != 11:
            return {"valid": False, "message": "CPF deve ter 11 dígitos", "issue_type": IssueTypeEnum.INVALID_CHECKSUM}

        # Verifica CPFs inválidos conhecidos
        if cpf in [str(i) * 11 for i in range(10)]:
            return {"valid": False, "message": "CPF inválido", "issue_type": IssueTypeEnum.INVALID_CHECKSUM}

        # Calcula dígitos verificadores
        def calc_digit(cpf_part: str, weights: list[int]) -> int:
            total = sum(int(d) * w for d, w in zip(cpf_part, weights, strict=False))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder

        weights1 = [10, 9, 8, 7, 6, 5, 4, 3, 2]
        weights2 = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]

        digit1 = calc_digit(cpf[:9], weights1)
        digit2 = calc_digit(cpf[:10], weights2)

        if cpf[-2:] != f"{digit1}{digit2}":
            return {
                "valid": False,
                "message": "CPF com dígito verificador inválido",
                "issue_type": IssueTypeEnum.INVALID_CHECKSUM,
            }

        return {"valid": True}

    def _validate_cnpj(self, value: Any, rule: DataQualityRule, full_data: dict[str, Any]) -> dict[str, Any]:
        """Valida CNPJ brasileiro."""
        if value is None:
            return {"valid": True}

        cnpj = re.sub(r"\D", "", str(value))

        if len(cnpj) != 14:
            return {"valid": False, "message": "CNPJ deve ter 14 dígitos", "issue_type": IssueTypeEnum.INVALID_CHECKSUM}

        # Verifica CNPJs inválidos
        if cnpj in [str(i) * 14 for i in range(10)]:
            return {"valid": False, "message": "CNPJ inválido", "issue_type": IssueTypeEnum.INVALID_CHECKSUM}

        # Calcula dígitos verificadores
        def calc_digit(cnpj_part: str, weights: list[int]) -> int:
            total = sum(int(d) * w for d, w in zip(cnpj_part, weights, strict=False))
            remainder = total % 11
            return 0 if remainder < 2 else 11 - remainder

        weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        digit1 = calc_digit(cnpj[:12], weights1)
        digit2 = calc_digit(cnpj[:13], weights2)

        if cnpj[-2:] != f"{digit1}{digit2}":
            return {
                "valid": False,
                "message": "CNPJ com dígito verificador inválido",
                "issue_type": IssueTypeEnum.INVALID_CHECKSUM,
            }

        return {"valid": True}

    def _validate_email(self, value: Any, rule: DataQualityRule, full_data: dict[str, Any]) -> dict[str, Any]:
        """Valida email."""
        if value is None:
            return {"valid": True}

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, str(value)):
            return {"valid": False, "message": "Email em formato inválido", "issue_type": IssueTypeEnum.INVALID_FORMAT}
        return {"valid": True}

    def _validate_phone(self, value: Any, rule: DataQualityRule, full_data: dict[str, Any]) -> dict[str, Any]:
        """Valida telefone brasileiro."""
        if value is None:
            return {"valid": True}

        phone = re.sub(r"\D", "", str(value))

        if len(phone) < 10 or len(phone) > 11:
            return {
                "valid": False,
                "message": "Telefone deve ter 10 ou 11 dígitos",
                "issue_type": IssueTypeEnum.INVALID_FORMAT,
            }
        return {"valid": True}

    def _create_issue(
        self,
        rule: DataQualityRule,
        entity_type: str,
        entity_id: uuid.UUID = None,
        field_name: str = None,
        current_value: str = None,
        error_message: str = None,
        suggested_value: str = None,
    ) -> DataQualityIssue:
        """Cria issue de qualidade."""
        issue_code = f"DQ-{uuid.uuid4().hex[:8].upper()}"

        # Mapeia tipo de regra para tipo de issue
        issue_type_map = {
            RuleTypeEnum.NOT_NULL: IssueTypeEnum.MISSING_VALUE,
            RuleTypeEnum.UNIQUE: IssueTypeEnum.DUPLICATE_VALUE,
            RuleTypeEnum.FORMAT: IssueTypeEnum.INVALID_FORMAT,
            RuleTypeEnum.RANGE: IssueTypeEnum.OUT_OF_RANGE,
            RuleTypeEnum.LENGTH: IssueTypeEnum.INVALID_VALUE,
            RuleTypeEnum.ENUM: IssueTypeEnum.INVALID_VALUE,
            RuleTypeEnum.REGEX: IssueTypeEnum.INVALID_FORMAT,
            RuleTypeEnum.CPF_VALID: IssueTypeEnum.INVALID_CHECKSUM,
            RuleTypeEnum.CNPJ_VALID: IssueTypeEnum.INVALID_CHECKSUM,
            RuleTypeEnum.EMAIL_VALID: IssueTypeEnum.INVALID_FORMAT,
            RuleTypeEnum.PHONE_VALID: IssueTypeEnum.INVALID_FORMAT,
        }

        return DataQualityIssue(
            issue_code=issue_code,
            rule_id=rule.id,
            rule_code=rule.code,
            issue_type=issue_type_map.get(rule.rule_type, IssueTypeEnum.CUSTOM),
            severity=rule.severity,
            status=IssueStatusEnum.OPEN,
            entity_type=entity_type,
            entity_id=entity_id,
            field_name=field_name,
            current_value=current_value,
            suggested_value=str(suggested_value) if suggested_value else None,
            title=error_message or f"Violação da regra {rule.code}",
            description=rule.description,
            error_message=error_message,
            can_auto_fix=rule.auto_fix_enabled,
            confidence_score=1.0,
        )
