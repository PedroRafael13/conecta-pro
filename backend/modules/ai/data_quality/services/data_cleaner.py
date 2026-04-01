"""
DataCleaner Service - Sprint 48.

Serviço de limpeza e padronização de dados.
"""

import re
import unicodedata
from typing import Any


class DataCleaner:
    """Serviço de limpeza e padronização de dados."""

    def __init__(self):
        self.cleaners = {
            "trim": self._trim,
            "uppercase": self._uppercase,
            "lowercase": self._lowercase,
            "normalize": self._normalize,
            "remove_special": self._remove_special_chars,
            "cpf_format": self._format_cpf,
            "cnpj_format": self._format_cnpj,
            "phone_format": self._format_phone,
            "cep_format": self._format_cep,
            "email_format": self._format_email,
            "remove_duplicates_spaces": self._remove_duplicate_spaces,
            "capitalize": self._capitalize,
            "title_case": self._title_case,
        }

    def clean_record(
        self, data: dict[str, Any], field_operations: dict[str, list[str]] = None, default_operations: list[str] = None
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """
        Limpa e padroniza registro.

        Args:
            data: Dados do registro
            field_operations: Operações por campo
            default_operations: Operações padrão para todos

        Returns:
            Tuple[cleaned_data, changes]
        """
        cleaned_data = data.copy()
        changes = []

        default_ops = default_operations or ["trim", "remove_duplicates_spaces"]

        for field, value in data.items():
            if value is None:
                continue

            operations = field_operations.get(field, default_ops) if field_operations else default_ops
            new_value = value

            for op in operations:
                cleaner = self.cleaners.get(op)
                if cleaner:
                    result = cleaner(new_value)
                    if result != new_value:
                        changes.append(
                            {"field": field, "operation": op, "original": str(new_value), "cleaned": str(result)}
                        )
                        new_value = result

            cleaned_data[field] = new_value

        return cleaned_data, changes

    def clean_value(self, value: Any, operations: list[str]) -> Any:
        """Limpa valor individual."""
        if value is None:
            return None

        result = value
        for op in operations:
            cleaner = self.cleaners.get(op)
            if cleaner:
                result = cleaner(result)
        return result

    def _trim(self, value: Any) -> Any:
        """Remove espaços no início e fim."""
        if isinstance(value, str):
            return value.strip()
        return value

    def _uppercase(self, value: Any) -> Any:
        """Converte para maiúsculas."""
        if isinstance(value, str):
            return value.upper()
        return value

    def _lowercase(self, value: Any) -> Any:
        """Converte para minúsculas."""
        if isinstance(value, str):
            return value.lower()
        return value

    def _normalize(self, value: Any) -> Any:
        """Normaliza caracteres Unicode."""
        if isinstance(value, str):
            # Remove acentos
            nfkd = unicodedata.normalize("NFKD", value)
            return "".join(c for c in nfkd if not unicodedata.combining(c))
        return value

    def _remove_special_chars(self, value: Any) -> Any:
        """Remove caracteres especiais."""
        if isinstance(value, str):
            return re.sub(r"[^\w\s@.\-]", "", value)
        return value

    def _remove_duplicate_spaces(self, value: Any) -> Any:
        """Remove espaços duplicados."""
        if isinstance(value, str):
            return re.sub(r"\s+", " ", value).strip()
        return value

    def _capitalize(self, value: Any) -> Any:
        """Capitaliza primeira letra."""
        if isinstance(value, str):
            return value.capitalize()
        return value

    def _title_case(self, value: Any) -> Any:
        """Converte para Title Case."""
        if isinstance(value, str):
            # Palavras que devem ficar em minúsculas
            exceptions = ["de", "da", "do", "das", "dos", "e", "em", "para", "com"]
            words = value.lower().split()
            result = []
            for i, word in enumerate(words):
                if i == 0 or word not in exceptions:
                    result.append(word.capitalize())
                else:
                    result.append(word)
            return " ".join(result)
        return value

    def _format_cpf(self, value: Any) -> Any:
        """Formata CPF."""
        if value is None:
            return None
        digits = re.sub(r"\D", "", str(value))
        if len(digits) == 11:
            return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
        return value

    def _format_cnpj(self, value: Any) -> Any:
        """Formata CNPJ."""
        if value is None:
            return None
        digits = re.sub(r"\D", "", str(value))
        if len(digits) == 14:
            return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"
        return value

    def _format_phone(self, value: Any) -> Any:
        """Formata telefone brasileiro."""
        if value is None:
            return None
        digits = re.sub(r"\D", "", str(value))
        if len(digits) == 11:
            return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
        elif len(digits) == 10:
            return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
        return value

    def _format_cep(self, value: Any) -> Any:
        """Formata CEP."""
        if value is None:
            return None
        digits = re.sub(r"\D", "", str(value))
        if len(digits) == 8:
            return f"{digits[:5]}-{digits[5:]}"
        return value

    def _format_email(self, value: Any) -> Any:
        """Normaliza email."""
        if isinstance(value, str):
            return value.lower().strip()
        return value

    def suggest_cleaning_operations(self, field_name: str, sample_values: list[Any]) -> list[str]:
        """Sugere operações de limpeza para campo."""
        suggestions = ["trim"]
        field_lower = field_name.lower()

        # Por tipo de campo
        if "email" in field_lower:
            suggestions.extend(["email_format", "lowercase"])
        elif "cpf" in field_lower:
            suggestions.append("cpf_format")
        elif "cnpj" in field_lower:
            suggestions.append("cnpj_format")
        elif "phone" in field_lower or "telefone" in field_lower:
            suggestions.append("phone_format")
        elif "cep" in field_lower:
            suggestions.append("cep_format")
        elif "name" in field_lower or "nome" in field_lower:
            suggestions.extend(["title_case", "remove_duplicates_spaces"])

        # Análise de sample
        has_extra_spaces = any(isinstance(v, str) and "  " in v for v in sample_values if v)
        if has_extra_spaces:
            suggestions.append("remove_duplicates_spaces")

        return list(dict.fromkeys(suggestions))  # Remove duplicatas mantendo ordem
