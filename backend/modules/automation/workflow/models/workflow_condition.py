"""Workflow Condition Model - Condicoes para logica de fluxo.

Sprint 33 - Workflow Engine (Unificado).
"""

import enum
import re
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from core.models import Base


class ConditionType(str, enum.Enum):
    """Tipo de condicao."""

    SIMPLE = "SIMPLE"  # Comparacao simples
    COMPOUND = "COMPOUND"  # AND/OR de condicoes
    EXPRESSION = "EXPRESSION"  # Expressao customizada
    SCRIPT = "SCRIPT"  # Script Python
    FUNCTION = "FUNCTION"  # Funcao predefinida


class ConditionOperator(str, enum.Enum):
    """Operadores de comparacao."""

    # Igualdade
    EQUALS = "eq"
    NOT_EQUALS = "neq"

    # Comparacao numerica
    GREATER_THAN = "gt"
    GREATER_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_EQUAL = "lte"

    # String
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    MATCHES = "matches"  # Regex

    # Nulidade
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"

    # Colecao
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS_ANY = "contains_any"
    CONTAINS_ALL = "contains_all"

    # Tipo
    IS_TYPE = "is_type"

    # Data
    BEFORE = "before"
    AFTER = "after"
    BETWEEN = "between"


class LogicalOperator(str, enum.Enum):
    """Operadores logicos."""

    AND = "AND"
    OR = "OR"
    NOT = "NOT"


class WorkflowCondition(Base):
    """Condicao para controle de fluxo no workflow."""

    __tablename__ = "workflow_conditions"

    # Primary Key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    # Multi-tenant
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Identificacao
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Tipo
    condition_type = Column(
        Enum(ConditionType, name="conditiontype", create_type=True),
        nullable=False,
        default=ConditionType.SIMPLE,
    )

    # Condicao simples
    # Ex: {"field": "$.amount", "operator": "gt", "value": 1000}
    simple_condition = Column(JSONB, nullable=True)

    # Grupo de condicoes (para COMPOUND)
    # Ex: {"operator": "AND", "conditions": [...], "negate": false}
    condition_group = Column(JSONB, nullable=True)

    # Expressao (para EXPRESSION)
    expression = Column(Text, nullable=True)

    # Script (para SCRIPT)
    script = Column(Text, nullable=True)
    script_language = Column(String(20), default="python", nullable=True)

    # Funcao predefinida (para FUNCTION)
    function_name = Column(String(100), nullable=True)
    function_params = Column(JSONB, nullable=True)

    # Branches
    true_step_id = Column(UUID(as_uuid=True), nullable=True)
    false_step_id = Column(UUID(as_uuid=True), nullable=True)
    branches = Column(JSONB, nullable=True)  # valor -> step_id

    # Flags
    is_enabled = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<WorkflowCondition {self.name} ({self.condition_type.value})>"

    def evaluate(self, context: dict[str, Any]) -> bool:
        """Avalia condicao no contexto.

        Args:
            context: Contexto com variaveis.

        Returns:
            Resultado da avaliacao.
        """
        if self.condition_type == ConditionType.SIMPLE:
            return self._evaluate_simple(context)

        if self.condition_type == ConditionType.COMPOUND:
            return self._evaluate_compound(context)

        if self.condition_type == ConditionType.EXPRESSION:
            return self._evaluate_expression(context)

        if self.condition_type == ConditionType.FUNCTION:
            return self._evaluate_function(context)

        return True

    def _evaluate_simple(self, context: dict[str, Any]) -> bool:
        """Avalia condicao simples."""
        if not self.simple_condition:
            return True

        field = self.simple_condition.get("field", "")
        operator = self.simple_condition.get("operator", "eq")
        value = self.simple_condition.get("value")
        value_field = self.simple_condition.get("value_field", "")

        field_value = self._get_field_value(field, context)
        compare_value = (
            self._get_field_value(value_field, context)
            if value_field
            else value
        )

        return self._apply_operator(field_value, operator, compare_value)

    def _evaluate_compound(self, context: dict[str, Any]) -> bool:
        """Avalia grupo de condicoes."""
        if not self.condition_group:
            return True

        operator = self.condition_group.get("operator", "AND")
        conditions = self.condition_group.get("conditions", [])
        negate = self.condition_group.get("negate", False)

        if not conditions:
            return True

        results = []
        for cond in conditions:
            # Cada condicao pode ser simples ou grupo
            if "field" in cond:
                # Condicao simples
                field_value = self._get_field_value(cond.get("field", ""), context)
                compare_value = cond.get("value")
                result = self._apply_operator(
                    field_value,
                    cond.get("operator", "eq"),
                    compare_value,
                )
                results.append(result)
            elif "conditions" in cond:
                # Grupo aninhado
                sub_result = self._evaluate_nested_group(cond, context)
                results.append(sub_result)

        if operator == "AND":
            result = all(results)
        elif operator == "OR":
            result = any(results)
        else:
            result = results[0] if results else True

        return not result if negate else result

    def _evaluate_nested_group(
        self,
        group: dict[str, Any],
        context: dict[str, Any],
    ) -> bool:
        """Avalia grupo aninhado de condicoes."""
        operator = group.get("operator", "AND")
        conditions = group.get("conditions", [])
        negate = group.get("negate", False)

        if not conditions:
            return True

        results = []
        for cond in conditions:
            if "field" in cond:
                field_value = self._get_field_value(cond.get("field", ""), context)
                compare_value = cond.get("value")
                result = self._apply_operator(
                    field_value,
                    cond.get("operator", "eq"),
                    compare_value,
                )
                results.append(result)
            elif "conditions" in cond:
                sub_result = self._evaluate_nested_group(cond, context)
                results.append(sub_result)

        if operator == "AND":
            result = all(results)
        elif operator == "OR":
            result = any(results)
        else:
            result = results[0] if results else True

        return not result if negate else result

    def _evaluate_expression(self, context: dict[str, Any]) -> bool:
        """Avalia expressao string."""
        if not self.expression:
            return True

        try:
            safe_context = {
                "context": context,
                "data": context.get("data", {}),
                "input": context.get("input", {}),
                "output": context.get("output", {}),
            }
            result = eval(self.expression, {"__builtins__": {}}, safe_context)
            return bool(result)
        except Exception:
            return False

    def _evaluate_function(self, context: dict[str, Any]) -> bool:
        """Avalia funcao predefinida."""
        functions = {
            "is_business_hours": self._is_business_hours,
            "is_weekend": self._is_weekend,
            "has_permission": self._has_permission,
            "is_valid_document": self._is_valid_document,
        }

        func = functions.get(self.function_name or "")
        if func:
            params = self.function_params or {}
            return func(context, params)

        return True

    def _get_field_value(self, field_path: str, context: dict[str, Any]) -> Any:
        """Obtem valor de campo no contexto."""
        if not field_path:
            return None

        # Remove prefixo $. se presente
        if field_path.startswith("$."):
            field_path = field_path[2:]

        parts = field_path.split(".")
        value = context

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif isinstance(value, list):
                try:
                    idx = int(part)
                    value = value[idx]
                except (ValueError, IndexError):
                    return None
            else:
                return None

            if value is None:
                return None

        return value

    def _apply_operator(
        self,
        field_value: Any,
        operator: str,
        compare_value: Any,
    ) -> bool:
        """Aplica operador de comparacao."""
        # Nulidade
        if operator == "is_null":
            return field_value is None
        if operator == "is_not_null":
            return field_value is not None
        if operator == "is_empty":
            return not field_value
        if operator == "is_not_empty":
            return bool(field_value)

        # Se campo e None, nao pode comparar
        if field_value is None:
            return False

        # Igualdade
        if operator == "eq":
            return field_value == compare_value
        if operator == "neq":
            return field_value != compare_value

        # Numericos
        if operator == "gt":
            return field_value > compare_value
        if operator == "gte":
            return field_value >= compare_value
        if operator == "lt":
            return field_value < compare_value
        if operator == "lte":
            return field_value <= compare_value

        # String
        if operator == "contains":
            return str(compare_value) in str(field_value)
        if operator == "not_contains":
            return str(compare_value) not in str(field_value)
        if operator == "starts_with":
            return str(field_value).startswith(str(compare_value))
        if operator == "ends_with":
            return str(field_value).endswith(str(compare_value))
        if operator == "matches":
            return bool(re.match(str(compare_value), str(field_value)))

        # Colecao
        if operator == "in":
            return field_value in compare_value
        if operator == "not_in":
            return field_value not in compare_value

        return False

    def _is_business_hours(
        self,
        context: dict[str, Any],
        params: dict[str, Any],
    ) -> bool:
        """Verifica se esta em horario comercial."""
        now = datetime.now()
        start_hour = params.get("start_hour", 9)
        end_hour = params.get("end_hour", 18)
        return start_hour <= now.hour < end_hour and now.weekday() < 5

    def _is_weekend(
        self,
        context: dict[str, Any],
        params: dict[str, Any],
    ) -> bool:
        """Verifica se e final de semana."""
        return datetime.now().weekday() >= 5

    def _has_permission(
        self,
        context: dict[str, Any],
        params: dict[str, Any],
    ) -> bool:
        """Verifica se usuario tem permissao."""
        user = context.get("user", {})
        required_role = params.get("role", "")
        return user.get("role") == required_role

    def _is_valid_document(
        self,
        context: dict[str, Any],
        params: dict[str, Any],
    ) -> bool:
        """Verifica se documento e valido."""
        doc = context.get("document", {})
        return doc.get("status") == "valid"

    def get_next_step_id(self, context: dict[str, Any]) -> str | None:
        """Obtem proximo step baseado na avaliacao.

        Args:
            context: Contexto com variaveis.

        Returns:
            ID do proximo step.
        """
        result = self.evaluate(context)

        if self.branches:
            # Multi-branch
            result_key = str(result)
            return self.branches.get(result_key, str(self.false_step_id) if self.false_step_id else None)

        # Binary branch
        if result:
            return str(self.true_step_id) if self.true_step_id else None
        return str(self.false_step_id) if self.false_step_id else None


# Conditions builtin
BUILTIN_CONDITIONS = {
    "is_business_hours": {
        "name": "Horario Comercial",
        "condition_type": ConditionType.FUNCTION,
        "function_name": "is_business_hours",
        "function_params": {"start_hour": 9, "end_hour": 18},
    },
    "is_weekend": {
        "name": "Final de Semana",
        "condition_type": ConditionType.FUNCTION,
        "function_name": "is_weekend",
    },
    "amount_threshold": {
        "name": "Valor Acima do Limite",
        "condition_type": ConditionType.SIMPLE,
        "simple_condition": {
            "field": "$.amount",
            "operator": "gt",
            "value": 1000,
        },
    },
}
