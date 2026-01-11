"""
Service de Mascaramento de Dados LGPD.
"""

import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class MaskingService:
    """Service para operacoes de mascaramento de dados PII.

    Encapsula a logica de mascaramento de dados pessoais
    identificaveis (PII) conforme LGPD.
    """

    def __init__(self):
        """Inicializa o service."""
        pass

    def _mask_cpf(self, cpf: str, level: str = "partial") -> str:
        """Mascara CPF brasileiro."""
        cpf_clean = re.sub(r"[^\d]", "", cpf)
        if len(cpf_clean) != 11:
            return "*" * len(cpf)

        if level == "full":
            return "***.***.***-**"
        # partial
        return f"{cpf_clean[:3]}.***.***-{cpf_clean[-2:]}"

    def _mask_cnpj(self, cnpj: str, level: str = "partial") -> str:
        """Mascara CNPJ brasileiro."""
        cnpj_clean = re.sub(r"[^\d]", "", cnpj)
        if len(cnpj_clean) != 14:
            return "*" * len(cnpj)

        if level == "full":
            return "**.***.***/****.***"
        # partial
        return f"{cnpj_clean[:2]}.***.***/{cnpj_clean[8:12]}-**"

    def _mask_email(self, email: str, level: str = "partial") -> str:
        """Mascara endereco de email."""
        if "@" not in email:
            return "*" * len(email)

        local, domain = email.rsplit("@", 1)

        if level == "full":
            return f"{'*' * len(local)}@{'*' * len(domain)}"
        # partial
        if len(local) <= 2:
            masked_local = "*" * len(local)
        else:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
        return f"{masked_local}@{domain}"

    def _mask_phone(self, phone: str, level: str = "partial") -> str:
        """Mascara numero de telefone."""
        phone_clean = re.sub(r"[^\d]", "", phone)

        if level == "full":
            return "*" * len(phone_clean)
        # partial
        if len(phone_clean) >= 4:
            return phone_clean[:2] + "*" * (len(phone_clean) - 4) + phone_clean[-2:]
        return "*" * len(phone_clean)

    def _mask_card(self, card: str, level: str = "partial") -> str:
        """Mascara numero de cartao de credito."""
        card_clean = re.sub(r"[^\d]", "", card)

        if level == "full":
            return "**** **** **** ****"
        # partial - mostra apenas ultimos 4 digitos
        return f"**** **** **** {card_clean[-4:]}" if len(card_clean) >= 4 else "*" * len(card_clean)

    def _mask_name(self, name: str, level: str = "partial") -> str:
        """Mascara nome pessoal."""
        if level == "full":
            return "*" * len(name)
        # partial - mostra primeira letra de cada palavra
        words = name.split()
        masked_words = []
        for word in words:
            if len(word) > 1:
                masked_words.append(word[0] + "*" * (len(word) - 1))
            else:
                masked_words.append("*")
        return " ".join(masked_words)

    def _mask_generic(self, data: str, level: str = "partial") -> str:
        """Mascaramento generico."""
        if level == "full":
            return "*" * len(data)
        # partial - mostra 20% inicio e fim
        visible = max(1, len(data) // 5)
        return data[:visible] + "*" * (len(data) - 2 * visible) + data[-visible:]

    def mask(
        self,
        data: str,
        category: str,
        level: str = "partial",
    ) -> Dict[str, Any]:
        """Mascara dados PII.

        Args:
            data: Dado a mascarar.
            category: Categoria do dado (cpf, email, phone, etc).
            level: Nivel de mascaramento (partial, full).

        Returns:
            Dict com dado mascarado.
        """
        masked: str

        mask_functions = {
            "cpf": self._mask_cpf,
            "cnpj": self._mask_cnpj,
            "email": self._mask_email,
            "phone": self._mask_phone,
            "card": self._mask_card,
            "name": self._mask_name,
            "generic": self._mask_generic,
        }

        mask_func = mask_functions.get(category.lower(), self._mask_generic)
        masked = mask_func(data, level)

        logger.info("Dado mascarado: categoria=%s, nivel=%s", category, level)

        return {
            "original_length": len(data),
            "masked": masked,
            "category": category,
            "level": level,
        }

    def get_formats(self) -> Dict[str, List[Dict[str, str]]]:
        """Retorna formatos de mascaramento disponiveis.

        Returns:
            Dict com categorias e niveis disponiveis.
        """
        return {
            "categories": [
                {"id": "cpf", "description": "CPF brasileiro"},
                {"id": "cnpj", "description": "CNPJ brasileiro"},
                {"id": "email", "description": "Endereco de email"},
                {"id": "phone", "description": "Telefone"},
                {"id": "card", "description": "Cartao de credito"},
                {"id": "name", "description": "Nome pessoal"},
                {"id": "address", "description": "Endereco"},
                {"id": "generic", "description": "Texto generico"},
            ],
            "levels": [
                {"id": "partial", "description": "Mascaramento parcial"},
                {"id": "full", "description": "Mascaramento completo"},
            ],
        }
