"""
Service para integrações com Receita Federal.
"""

import logging
from datetime import date
from typing import Any

# Imports relativos do módulo pai
from modules.government_integrations.utils import (
    formatar_cnpj,
    formatar_cpf,
    validar_cnpj,
    validar_cpf,
)

logger = logging.getLogger(__name__)


class ReceitaFederalApiService:
    """Service para operações com Receita Federal."""

    @staticmethod
    def validar_documento(documento: str, tipo: str) -> dict[str, Any]:
        """
        Valida CPF ou CNPJ.

        Args:
            documento: Número do documento (apenas dígitos).
            tipo: Tipo do documento ('cpf' ou 'cnpj').

        Returns:
            Dict com resultado da validação.
        """
        is_valid: bool
        documento_formatado: str

        if tipo == "cpf":
            is_valid = validar_cpf(documento)
            documento_formatado = formatar_cpf(documento) if is_valid else documento
        else:
            is_valid = validar_cnpj(documento)
            documento_formatado = formatar_cnpj(documento) if is_valid else documento

        return {
            "documento": documento_formatado,
            "tipo": tipo,
            "valido": is_valid,
        }

    @staticmethod
    def consultar_cpf(cpf: str, data_nascimento: date) -> dict[str, Any]:
        """
        Consulta CPF na Receita Federal.

        Args:
            cpf: Número do CPF (apenas dígitos).
            data_nascimento: Data de nascimento do titular.

        Returns:
            Dict com dados do CPF.

        Raises:
            ValueError: Se CPF inválido.
        """
        cpf_limpo = "".join(c for c in cpf if c.isdigit())

        if not validar_cpf(cpf_limpo):
            raise ValueError("CPF invalido")

        # Receita Federal não tem API pública para consulta de CPF
        return {
            "cpf": formatar_cpf(cpf_limpo),
            "status": "indisponivel",
            "fonte": "nao_consultado",
            "aviso": "Receita Federal não tem API pública. Consultar via e-CAC ou Gov.br.",
        }

    @staticmethod
    def consultar_cnpj(cnpj: str) -> dict[str, Any]:
        """
        Consulta CNPJ na Receita Federal.

        Args:
            cnpj: Número do CNPJ.

        Returns:
            Dict com dados do CNPJ.

        Raises:
            ValueError: Se CNPJ inválido.
        """
        cnpj_limpo = "".join(c for c in cnpj if c.isdigit())

        if not validar_cnpj(cnpj_limpo):
            raise ValueError("CNPJ invalido")

        # Receita Federal não tem API pública para consulta de CNPJ
        return {
            "cnpj": formatar_cnpj(cnpj_limpo),
            "status": "indisponivel",
            "fonte": "nao_consultado",
            "aviso": "Receita Federal não tem API pública. Consultar via e-CAC ou Gov.br.",
        }
