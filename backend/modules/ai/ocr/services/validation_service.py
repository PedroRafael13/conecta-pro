"""ValidationService - Servico de validacao de dados extraidos.

Sprint 39 - Document OCR.

Valida dados extraidos:
- CPF/CNPJ (digito verificador)
- Datas
- Valores monetarios
- Cross-validation (totais vs itens)
"""

import logging
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from modules.ai.ocr.models.extracted_field import FieldType, FieldValidationStatus
from modules.ai.ocr.models.validation_result import ValidationStatus, ValidationAction

logger = logging.getLogger(__name__)


class ValidationService:
    """Servico de validacao de dados extraidos."""

    def __init__(
        self,
        enable_external_validation: bool = False,
        enable_auto_correction: bool = True,
        strict_mode: bool = False,
    ):
        """Inicializa o servico.

        Args:
            enable_external_validation: Habilita validacao externa (APIs)
            enable_auto_correction: Habilita correcao automatica
            strict_mode: Modo estrito (falha em warnings)
        """
        self.enable_external_validation = enable_external_validation
        self.enable_auto_correction = enable_auto_correction
        self.strict_mode = strict_mode

    def validate_fields(
        self,
        fields: List[Dict[str, Any]],
        document_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Valida lista de campos extraidos.

        Args:
            fields: Lista de campos
            document_type: Tipo de documento (para validacoes especificas)

        Returns:
            Resultado da validacao
        """
        result = {
            "validation_id": str(uuid.uuid4()),
            "status": ValidationStatus.PENDING.value,
            "total_fields": len(fields),
            "valid_fields": 0,
            "invalid_fields": 0,
            "warning_fields": 0,
            "field_results": [],
            "errors": [],
            "warnings": [],
            "auto_corrections": [],
        }

        for field in fields:
            field_result = self._validate_field(field)
            result["field_results"].append(field_result)

            status = field_result.get("status")
            if status == FieldValidationStatus.VALID.value:
                result["valid_fields"] += 1
            elif status == FieldValidationStatus.INVALID.value:
                result["invalid_fields"] += 1
                result["errors"].extend(field_result.get("errors", []))
            elif status == FieldValidationStatus.WARNING.value:
                result["warning_fields"] += 1
                result["warnings"].extend(field_result.get("warnings", []))

            # Correcoes automaticas
            if field_result.get("auto_corrections"):
                result["auto_corrections"].extend(field_result["auto_corrections"])

        # Cross-validation (se aplicavel)
        cross_results = self._cross_validate(fields, document_type)
        result["cross_validation_results"] = cross_results
        result["errors"].extend([r for r in cross_results if r.get("status") == "failed"])

        # Determina status geral
        if result["invalid_fields"] > 0:
            result["status"] = ValidationStatus.FAILED.value
        elif result["warning_fields"] > 0 and self.strict_mode:
            result["status"] = ValidationStatus.PARTIAL.value
        else:
            result["status"] = ValidationStatus.PASSED.value

        # Calcula scores
        result["overall_score"] = self._calculate_score(result)
        result["needs_review"] = self._needs_review(result)

        return result

    def _validate_field(self, field: Dict[str, Any]) -> Dict[str, Any]:
        """Valida um campo individual.

        Args:
            field: Campo a validar

        Returns:
            Resultado da validacao do campo
        """
        field_type = FieldType(field.get("field_type", "text"))
        value = field.get("normalized_value") or field.get("extracted_value", "")

        result = {
            "field_id": field.get("field_id"),
            "field_name": field.get("field_name"),
            "status": FieldValidationStatus.PENDING.value,
            "rules_applied": [],
            "rules_passed": [],
            "rules_failed": [],
            "errors": [],
            "warnings": [],
            "auto_corrections": [],
        }

        # Validacao por tipo
        if field_type == FieldType.CPF:
            self._validate_cpf(value, result)

        elif field_type == FieldType.CNPJ:
            self._validate_cnpj(value, result)

        elif field_type == FieldType.EMAIL:
            self._validate_email(value, result)

        elif field_type == FieldType.PHONE:
            self._validate_phone(value, result)

        elif field_type == FieldType.CEP:
            self._validate_cep(value, result)

        elif field_type == FieldType.DATE:
            self._validate_date(value, result)

        elif field_type == FieldType.CURRENCY:
            self._validate_currency(value, result)

        elif field_type == FieldType.NF_KEY:
            self._validate_nf_key(value, result)

        else:
            # Validacao generica
            self._validate_generic(value, result)

        # Determina status final
        if result["rules_failed"]:
            result["status"] = FieldValidationStatus.INVALID.value
        elif result["warnings"]:
            result["status"] = FieldValidationStatus.WARNING.value
        else:
            result["status"] = FieldValidationStatus.VALID.value

        return result

    def _validate_cpf(
        self,
        value: str,
        result: Dict[str, Any],
    ) -> None:
        """Valida CPF.

        Args:
            value: Valor do CPF (apenas digitos)
            result: Resultado para atualizar
        """
        result["rules_applied"].append("cpf_format")
        result["rules_applied"].append("cpf_checksum")

        # Remove caracteres nao numericos
        cpf = re.sub(r"\D", "", value)

        # Formato
        if len(cpf) != 11:
            result["rules_failed"].append("cpf_format")
            result["errors"].append({
                "field": result["field_name"],
                "code": "INVALID_CPF_FORMAT",
                "message": f"CPF deve ter 11 digitos, encontrado: {len(cpf)}",
            })
            return

        result["rules_passed"].append("cpf_format")

        # Verifica digitos repetidos
        if cpf == cpf[0] * 11:
            result["rules_failed"].append("cpf_checksum")
            result["errors"].append({
                "field": result["field_name"],
                "code": "INVALID_CPF",
                "message": "CPF invalido (digitos repetidos)",
            })
            return

        # Calcula digito verificador
        if not self._cpf_checksum(cpf):
            result["rules_failed"].append("cpf_checksum")
            result["errors"].append({
                "field": result["field_name"],
                "code": "INVALID_CPF_CHECKSUM",
                "message": "Digito verificador do CPF invalido",
            })
            return

        result["rules_passed"].append("cpf_checksum")

    def _cpf_checksum(self, cpf: str) -> bool:
        """Verifica checksum do CPF.

        Args:
            cpf: CPF apenas digitos

        Returns:
            True se valido
        """
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

    def _validate_cnpj(
        self,
        value: str,
        result: Dict[str, Any],
    ) -> None:
        """Valida CNPJ.

        Args:
            value: Valor do CNPJ (apenas digitos)
            result: Resultado para atualizar
        """
        result["rules_applied"].append("cnpj_format")
        result["rules_applied"].append("cnpj_checksum")

        # Remove caracteres nao numericos
        cnpj = re.sub(r"\D", "", value)

        # Formato
        if len(cnpj) != 14:
            result["rules_failed"].append("cnpj_format")
            result["errors"].append({
                "field": result["field_name"],
                "code": "INVALID_CNPJ_FORMAT",
                "message": f"CNPJ deve ter 14 digitos, encontrado: {len(cnpj)}",
            })
            return

        result["rules_passed"].append("cnpj_format")

        # Verifica digitos repetidos
        if cnpj == cnpj[0] * 14:
            result["rules_failed"].append("cnpj_checksum")
            result["errors"].append({
                "field": result["field_name"],
                "code": "INVALID_CNPJ",
                "message": "CNPJ invalido (digitos repetidos)",
            })
            return

        # Calcula digito verificador
        if not self._cnpj_checksum(cnpj):
            result["rules_failed"].append("cnpj_checksum")
            result["errors"].append({
                "field": result["field_name"],
                "code": "INVALID_CNPJ_CHECKSUM",
                "message": "Digito verificador do CNPJ invalido",
            })
            return

        result["rules_passed"].append("cnpj_checksum")

    def _cnpj_checksum(self, cnpj: str) -> bool:
        """Verifica checksum do CNPJ.

        Args:
            cnpj: CNPJ apenas digitos

        Returns:
            True se valido
        """
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

    def _validate_email(
        self,
        value: str,
        result: Dict[str, Any],
    ) -> None:
        """Valida email.

        Args:
            value: Valor do email
            result: Resultado para atualizar
        """
        result["rules_applied"].append("email_format")

        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(pattern, value):
            result["rules_failed"].append("email_format")
            result["errors"].append({
                "field": result["field_name"],
                "code": "INVALID_EMAIL_FORMAT",
                "message": "Formato de email invalido",
            })
            return

        result["rules_passed"].append("email_format")

    def _validate_phone(
        self,
        value: str,
        result: Dict[str, Any],
    ) -> None:
        """Valida telefone.

        Args:
            value: Valor do telefone
            result: Resultado para atualizar
        """
        result["rules_applied"].append("phone_format")

        # Remove caracteres nao numericos
        phone = re.sub(r"\D", "", value)

        if len(phone) < 10 or len(phone) > 13:
            result["rules_failed"].append("phone_format")
            result["errors"].append({
                "field": result["field_name"],
                "code": "INVALID_PHONE_FORMAT",
                "message": f"Telefone deve ter 10-13 digitos, encontrado: {len(phone)}",
            })
            return

        result["rules_passed"].append("phone_format")

    def _validate_cep(
        self,
        value: str,
        result: Dict[str, Any],
    ) -> None:
        """Valida CEP.

        Args:
            value: Valor do CEP
            result: Resultado para atualizar
        """
        result["rules_applied"].append("cep_format")

        # Remove caracteres nao numericos
        cep = re.sub(r"\D", "", value)

        if len(cep) != 8:
            result["rules_failed"].append("cep_format")
            result["errors"].append({
                "field": result["field_name"],
                "code": "INVALID_CEP_FORMAT",
                "message": f"CEP deve ter 8 digitos, encontrado: {len(cep)}",
            })
            return

        result["rules_passed"].append("cep_format")

    def _validate_date(
        self,
        value: str,
        result: Dict[str, Any],
    ) -> None:
        """Valida data.

        Args:
            value: Valor da data
            result: Resultado para atualizar
        """
        result["rules_applied"].append("date_format")
        result["rules_applied"].append("date_valid")

        # Tenta parsear a data
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%d.%m.%Y",
        ]

        parsed_date = None
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(value, fmt)
                break
            except ValueError:
                continue

        if not parsed_date:
            result["rules_failed"].append("date_format")
            result["errors"].append({
                "field": result["field_name"],
                "code": "INVALID_DATE_FORMAT",
                "message": f"Formato de data invalido: {value}",
            })
            return

        result["rules_passed"].append("date_format")

        # Verifica se data eh razoavel (nao muito no passado ou futuro)
        today = datetime.now()
        min_date = datetime(1900, 1, 1)
        max_date = datetime(today.year + 50, 12, 31)

        if parsed_date < min_date or parsed_date > max_date:
            result["warnings"].append({
                "field": result["field_name"],
                "code": "DATE_OUT_OF_RANGE",
                "message": f"Data fora do intervalo esperado: {value}",
            })
        else:
            result["rules_passed"].append("date_valid")

    def _validate_currency(
        self,
        value: str,
        result: Dict[str, Any],
    ) -> None:
        """Valida valor monetario.

        Args:
            value: Valor monetario
            result: Resultado para atualizar
        """
        result["rules_applied"].append("currency_format")

        try:
            # Converte para float
            amount = float(value.replace(",", ".").replace(" ", ""))

            if amount < 0:
                result["warnings"].append({
                    "field": result["field_name"],
                    "code": "NEGATIVE_CURRENCY",
                    "message": "Valor monetario negativo",
                })

            result["rules_passed"].append("currency_format")

        except ValueError:
            result["rules_failed"].append("currency_format")
            result["errors"].append({
                "field": result["field_name"],
                "code": "INVALID_CURRENCY_FORMAT",
                "message": f"Formato de valor invalido: {value}",
            })

    def _validate_nf_key(
        self,
        value: str,
        result: Dict[str, Any],
    ) -> None:
        """Valida chave de acesso NFe.

        Args:
            value: Chave de acesso
            result: Resultado para atualizar
        """
        result["rules_applied"].append("nf_key_format")
        result["rules_applied"].append("nf_key_checksum")

        # Remove caracteres nao numericos
        key = re.sub(r"\D", "", value)

        if len(key) != 44:
            result["rules_failed"].append("nf_key_format")
            result["errors"].append({
                "field": result["field_name"],
                "code": "INVALID_NF_KEY_FORMAT",
                "message": f"Chave NFe deve ter 44 digitos, encontrado: {len(key)}",
            })
            return

        result["rules_passed"].append("nf_key_format")

        # Verifica digito verificador (modulo 11)
        if not self._nf_key_checksum(key):
            result["rules_failed"].append("nf_key_checksum")
            result["errors"].append({
                "field": result["field_name"],
                "code": "INVALID_NF_KEY_CHECKSUM",
                "message": "Digito verificador da chave NFe invalido",
            })
            return

        result["rules_passed"].append("nf_key_checksum")

    def _nf_key_checksum(self, key: str) -> bool:
        """Verifica checksum da chave NFe.

        Args:
            key: Chave apenas digitos (44)

        Returns:
            True se valido
        """
        # Modulo 11 com pesos 2-9
        pesos = [2, 3, 4, 5, 6, 7, 8, 9]
        soma = 0

        for i, digit in enumerate(reversed(key[:43])):
            peso = pesos[i % len(pesos)]
            soma += int(digit) * peso

        resto = soma % 11
        dv_calc = 0 if resto < 2 else 11 - resto

        return int(key[43]) == dv_calc

    def _validate_generic(
        self,
        value: str,
        result: Dict[str, Any],
    ) -> None:
        """Validacao generica.

        Args:
            value: Valor a validar
            result: Resultado para atualizar
        """
        result["rules_applied"].append("not_empty")

        if not value or not value.strip():
            result["warnings"].append({
                "field": result["field_name"],
                "code": "EMPTY_VALUE",
                "message": "Campo vazio",
            })
        else:
            result["rules_passed"].append("not_empty")

    def _cross_validate(
        self,
        fields: List[Dict[str, Any]],
        document_type: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Cross-validation entre campos.

        Args:
            fields: Lista de campos
            document_type: Tipo de documento

        Returns:
            Resultados de cross-validation
        """
        results = []

        # Agrupa campos por nome
        fields_by_name = {}
        for field in fields:
            name = field.get("field_name", "").lower()
            fields_by_name[name] = field

        # Validacao de totais (se aplicavel)
        total_field = None
        item_values = []

        for name, field in fields_by_name.items():
            if "total" in name and field.get("field_type") == "currency":
                total_field = field
            elif "item" in name or "valor" in name:
                if field.get("field_type") == "currency":
                    try:
                        value = float(field.get("normalized_value", "0").replace(",", "."))
                        item_values.append(value)
                    except ValueError:
                        pass

        if total_field and item_values:
            try:
                total_value = float(total_field.get("normalized_value", "0").replace(",", "."))
                calculated_sum = sum(item_values)

                # Tolerancia de 0.01 para erros de arredondamento
                if abs(total_value - calculated_sum) > 0.01:
                    results.append({
                        "type": "sum_check",
                        "status": "failed",
                        "expected": total_value,
                        "calculated": calculated_sum,
                        "difference": abs(total_value - calculated_sum),
                        "message": f"Soma dos itens ({calculated_sum:.2f}) difere do total ({total_value:.2f})",
                    })
                else:
                    results.append({
                        "type": "sum_check",
                        "status": "passed",
                        "expected": total_value,
                        "calculated": calculated_sum,
                    })
            except ValueError:
                pass

        return results

    def _calculate_score(self, result: Dict[str, Any]) -> float:
        """Calcula score de validacao.

        Args:
            result: Resultado da validacao

        Returns:
            Score 0-1
        """
        total = result.get("total_fields", 0)
        if total == 0:
            return 1.0

        valid = result.get("valid_fields", 0)
        warnings = result.get("warning_fields", 0)

        # Valid = 1.0, Warning = 0.5, Invalid = 0.0
        score = (valid + warnings * 0.5) / total
        return round(score, 2)

    def _needs_review(self, result: Dict[str, Any]) -> bool:
        """Determina se precisa revisao.

        Args:
            result: Resultado da validacao

        Returns:
            True se precisa revisao
        """
        # Precisa revisao se:
        # - Tem campos invalidos
        # - Score abaixo de 0.8
        # - Tem warnings criticos

        if result.get("invalid_fields", 0) > 0:
            return True

        if result.get("overall_score", 1.0) < 0.8:
            return True

        # Cross-validation falhou
        cross_results = result.get("cross_validation_results", [])
        if any(r.get("status") == "failed" for r in cross_results):
            return True

        return False
