"""
Condition Evaluator - Avalia condicoes de workflow.

Processa expressoes condicionais, operadores logicos e funcoes.
"""

import logging
import re
from datetime import datetime
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional

from modules._deprecated_workflows_dataclass.models.condition import (
    BUILTIN_CONDITIONS,
    Condition,
    ConditionGroup,
    ConditionOperator,
    ConditionType,
    LogicalOperator,
    SimpleCondition,
)

logger = logging.getLogger(__name__)


class ExpressionParser:
    """Parser de expressoes condicionais."""

    # Operadores suportados
    OPERATORS = {
        "==": ConditionOperator.EQUALS,
        "!=": ConditionOperator.NOT_EQUALS,
        ">": ConditionOperator.GREATER_THAN,
        ">=": ConditionOperator.GREATER_EQUAL,
        "<": ConditionOperator.LESS_THAN,
        "<=": ConditionOperator.LESS_EQUAL,
        "contains": ConditionOperator.CONTAINS,
        "not contains": ConditionOperator.NOT_CONTAINS,
        "starts with": ConditionOperator.STARTS_WITH,
        "ends with": ConditionOperator.ENDS_WITH,
        "matches": ConditionOperator.MATCHES,
        "in": ConditionOperator.IN,
        "not in": ConditionOperator.NOT_IN,
        "is null": ConditionOperator.IS_NULL,
        "is not null": ConditionOperator.IS_NOT_NULL,
        "is empty": ConditionOperator.IS_EMPTY,
        "is not empty": ConditionOperator.IS_NOT_EMPTY,
    }

    def parse(self, expression: str) -> Optional[SimpleCondition]:
        """
        Parseia expressao para SimpleCondition.

        Formatos suportados:
        - field == value
        - field > 100
        - field contains "text"
        - field is null
        """
        if not expression:
            return None

        expression = expression.strip()

        # Tenta cada operador
        for op_str, op_enum in sorted(
            self.OPERATORS.items(),
            key=lambda x: len(x[0]),
            reverse=True,
        ):
            if op_str in expression:
                parts = expression.split(op_str, 1)
                if len(parts) == 2:
                    field = parts[0].strip()
                    value_str = parts[1].strip()

                    # Converte valor
                    value = self._parse_value(value_str)

                    return SimpleCondition(
                        field=field,
                        operator=op_enum,
                        value=value,
                    )

        return None

    def _parse_value(self, value_str: str) -> Any:
        """Parseia valor da expressao."""
        if not value_str:
            return None

        # String entre aspas
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]

        # Booleanos
        if value_str.lower() == "true":
            return True
        if value_str.lower() == "false":
            return False
        if value_str.lower() in ("null", "none"):
            return None

        # Numeros
        try:
            if "." in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass

        # Lista
        if value_str.startswith("[") and value_str.endswith("]"):
            items = value_str[1:-1].split(",")
            return [self._parse_value(item.strip()) for item in items]

        # Referencia a campo
        if value_str.startswith("$"):
            return value_str  # Sera resolvido em runtime

        return value_str


class ConditionEvaluator:
    """
    Avaliador de condicoes.

    Avalia expressoes condicionais no contexto de execucao.
    """

    def __init__(self):
        self._parser = ExpressionParser()
        self._custom_functions: Dict[str, Callable] = {}
        self._register_builtin_functions()

    def _register_builtin_functions(self) -> None:
        """Registra funcoes builtin."""
        self._custom_functions = {
            "is_business_hours": self._fn_is_business_hours,
            "is_weekend": self._fn_is_weekend,
            "is_holiday": self._fn_is_holiday,
            "has_role": self._fn_has_role,
            "has_permission": self._fn_has_permission,
            "date_diff_days": self._fn_date_diff_days,
            "list_contains": self._fn_list_contains,
            "regex_match": self._fn_regex_match,
            "between": self._fn_between,
        }

    def register_function(
        self,
        name: str,
        func: Callable[[Dict[str, Any], Dict[str, Any]], bool],
    ) -> None:
        """Registra funcao customizada."""
        self._custom_functions[name] = func

    def evaluate(
        self,
        condition: Condition,
        context: Dict[str, Any],
    ) -> bool:
        """
        Avalia condicao no contexto.

        Args:
            condition: Condicao a avaliar
            context: Contexto com variaveis

        Returns:
            Resultado da avaliacao
        """
        try:
            if condition.condition_type == ConditionType.SIMPLE:
                return self._evaluate_simple(condition, context)

            elif condition.condition_type == ConditionType.COMPOUND:
                return self._evaluate_compound(condition, context)

            elif condition.condition_type == ConditionType.EXPRESSION:
                return self._evaluate_expression(condition, context)

            elif condition.condition_type == ConditionType.FUNCTION:
                return self._evaluate_function(condition, context)

            elif condition.condition_type == ConditionType.SCRIPT:
                return self._evaluate_script(condition, context)

            return True

        except Exception as e:
            logger.error(f"Erro ao avaliar condicao {condition.id}: {e}")
            return False

    def _evaluate_simple(
        self,
        condition: Condition,
        context: Dict[str, Any],
    ) -> bool:
        """Avalia condicao simples."""
        if not condition.simple_condition:
            return True

        return condition.simple_condition.evaluate(context)

    def _evaluate_compound(
        self,
        condition: Condition,
        context: Dict[str, Any],
    ) -> bool:
        """Avalia grupo de condicoes."""
        if not condition.condition_group:
            return True

        return condition.condition_group.evaluate(context)

    def _evaluate_expression(
        self,
        condition: Condition,
        context: Dict[str, Any],
    ) -> bool:
        """Avalia expressao string."""
        if not condition.expression:
            return True

        # Tenta parsear como condicao simples
        simple = self._parser.parse(condition.expression)
        if simple:
            # Resolve referencias de campo
            if isinstance(simple.value, str) and simple.value.startswith("$"):
                simple.value = self._resolve_path(simple.value, context)

            return simple.evaluate(context)

        # Avalia expressao complexa
        return self._evaluate_complex_expression(condition.expression, context)

    def _evaluate_complex_expression(
        self,
        expression: str,
        context: Dict[str, Any],
    ) -> bool:
        """Avalia expressao complexa."""
        try:
            # Substitui referencias de campo
            resolved = self._resolve_references(expression, context)

            # Ambiente seguro
            safe_globals = {
                "__builtins__": {},
                "True": True,
                "False": False,
                "None": None,
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "min": min,
                "max": max,
                "sum": sum,
                "abs": abs,
            }

            safe_locals = {
                "context": context,
                "data": context.get("data", {}),
                "input": context.get("input", {}),
                "output": context.get("output", {}),
            }

            result = eval(resolved, safe_globals, safe_locals)
            return bool(result)

        except Exception as e:
            logger.error(f"Erro ao avaliar expressao '{expression}': {e}")
            return False

    def _evaluate_function(
        self,
        condition: Condition,
        context: Dict[str, Any],
    ) -> bool:
        """Avalia funcao predefinida."""
        func = self._custom_functions.get(condition.function_name)
        if not func:
            logger.warning(f"Funcao nao encontrada: {condition.function_name}")
            return True

        return func(context, condition.function_params)

    def _evaluate_script(
        self,
        condition: Condition,
        context: Dict[str, Any],
    ) -> bool:
        """Avalia script Python."""
        if not condition.script:
            return True

        try:
            # Ambiente restrito
            safe_globals = {
                "__builtins__": {
                    "True": True,
                    "False": False,
                    "None": None,
                    "len": len,
                    "str": str,
                    "int": int,
                    "float": float,
                    "bool": bool,
                    "list": list,
                    "dict": dict,
                    "range": range,
                    "enumerate": enumerate,
                    "zip": zip,
                    "map": map,
                    "filter": filter,
                    "sorted": sorted,
                    "min": min,
                    "max": max,
                    "sum": sum,
                    "any": any,
                    "all": all,
                },
                "datetime": datetime,
                "Decimal": Decimal,
            }

            safe_locals = {"context": context, "result": True}

            exec(condition.script, safe_globals, safe_locals)
            return bool(safe_locals.get("result", True))

        except Exception as e:
            logger.error(f"Erro ao executar script: {e}")
            return False

    def _resolve_path(self, path: str, context: Dict[str, Any]) -> Any:
        """Resolve path de variavel."""
        if not path or not path.startswith("$"):
            return path

        path = path[1:]  # Remove $
        if path.startswith("."):
            path = path[1:]

        parts = path.split(".")
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

    def _resolve_references(self, expression: str, context: Dict[str, Any]) -> str:
        """Substitui referencias no formato $field.path."""
        pattern = r'\$([a-zA-Z_][a-zA-Z0-9_.]*)'

        def replacer(match):
            path = match.group(1)
            value = self._resolve_path(f"$.{path}", context)
            if isinstance(value, str):
                return f'"{value}"'
            return str(value)

        return re.sub(pattern, replacer, expression)

    # Funcoes builtin

    def _fn_is_business_hours(
        self,
        context: Dict[str, Any],
        params: Dict[str, Any],
    ) -> bool:
        """Verifica horario comercial."""
        now = datetime.now()
        start = params.get("start_hour", 9)
        end = params.get("end_hour", 18)
        return start <= now.hour < end and now.weekday() < 5

    def _fn_is_weekend(
        self,
        context: Dict[str, Any],
        params: Dict[str, Any],
    ) -> bool:
        """Verifica final de semana."""
        return datetime.now().weekday() >= 5

    def _fn_is_holiday(
        self,
        context: Dict[str, Any],
        params: Dict[str, Any],
    ) -> bool:
        """Verifica feriado (simplificado)."""
        # Em producao, consultar API de feriados
        holidays = params.get("holidays", [])
        today = datetime.now().strftime("%m-%d")
        return today in holidays

    def _fn_has_role(
        self,
        context: Dict[str, Any],
        params: Dict[str, Any],
    ) -> bool:
        """Verifica role do usuario."""
        user = context.get("user", {})
        required_role = params.get("role", "")
        user_roles = user.get("roles", [user.get("role", "")])
        return required_role in user_roles

    def _fn_has_permission(
        self,
        context: Dict[str, Any],
        params: Dict[str, Any],
    ) -> bool:
        """Verifica permissao do usuario."""
        user = context.get("user", {})
        required = params.get("permission", "")
        permissions = user.get("permissions", [])
        return required in permissions

    def _fn_date_diff_days(
        self,
        context: Dict[str, Any],
        params: Dict[str, Any],
    ) -> bool:
        """Verifica diferenca de dias."""
        date_field = params.get("field", "")
        max_days = params.get("max_days", 30)
        operator = params.get("operator", "<=")

        date_value = self._resolve_path(date_field, context)
        if not date_value:
            return False

        if isinstance(date_value, str):
            try:
                date_value = datetime.fromisoformat(date_value)
            except ValueError:
                return False

        diff = (datetime.now() - date_value).days

        if operator == "<=":
            return diff <= max_days
        elif operator == ">=":
            return diff >= max_days
        elif operator == "==":
            return diff == max_days
        elif operator == "<":
            return diff < max_days
        elif operator == ">":
            return diff > max_days

        return False

    def _fn_list_contains(
        self,
        context: Dict[str, Any],
        params: Dict[str, Any],
    ) -> bool:
        """Verifica se lista contem valor."""
        list_field = params.get("list_field", "")
        value = params.get("value", "")

        list_value = self._resolve_path(list_field, context)
        if not isinstance(list_value, list):
            return False

        # Resolve valor se for referencia
        if isinstance(value, str) and value.startswith("$"):
            value = self._resolve_path(value, context)

        return value in list_value

    def _fn_regex_match(
        self,
        context: Dict[str, Any],
        params: Dict[str, Any],
    ) -> bool:
        """Verifica match de regex."""
        field = params.get("field", "")
        pattern = params.get("pattern", "")

        value = self._resolve_path(field, context)
        if not value or not pattern:
            return False

        return bool(re.match(pattern, str(value)))

    def _fn_between(
        self,
        context: Dict[str, Any],
        params: Dict[str, Any],
    ) -> bool:
        """Verifica se valor esta entre limites."""
        field = params.get("field", "")
        min_val = params.get("min")
        max_val = params.get("max")

        value = self._resolve_path(field, context)
        if value is None:
            return False

        try:
            return min_val <= value <= max_val
        except TypeError:
            return False

    def get_next_step(
        self,
        condition: Condition,
        context: Dict[str, Any],
    ) -> str:
        """
        Determina proximo step baseado na avaliacao.

        Args:
            condition: Condicao com branches
            context: Contexto de execucao

        Returns:
            ID do proximo step
        """
        result = self.evaluate(condition, context)

        # Multi-branch
        if condition.branches:
            result_key = str(result)
            return condition.branches.get(result_key, condition.false_step_id)

        # Binary branch
        return condition.true_step_id if result else condition.false_step_id

    def validate_condition(self, condition: Condition) -> List[str]:
        """Valida condicao."""
        errors = []

        if condition.condition_type == ConditionType.EXPRESSION:
            if not condition.expression:
                errors.append("Expressao obrigatoria")

        if condition.condition_type == ConditionType.FUNCTION:
            if not condition.function_name:
                errors.append("Nome da funcao obrigatorio")
            if condition.function_name not in self._custom_functions:
                errors.append(f"Funcao '{condition.function_name}' nao encontrada")

        if condition.condition_type == ConditionType.SCRIPT:
            if not condition.script:
                errors.append("Script obrigatorio")

        return errors
