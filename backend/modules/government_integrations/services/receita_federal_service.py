"""
Service para integrações com Receita Federal.
"""

import logging
import sys
from datetime import date
from typing import Dict, Any



# Imports relativos do módulo pai
from modules.government_integrations.utils import (
    get_receita_service,
    validar_cpf,
    validar_cnpj,
    formatar_cpf,
    formatar_cnpj,
)

logger = logging.getLogger(__name__)


class ReceitaFederalApiService:
    """Service para operações com Receita Federal."""

    @staticmethod
    def validar_documento(documento: str, tipo: str) -> Dict[str, Any]:
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
    def consultar_cpf(cpf: str, data_nascimento: date) -> Dict[str, Any]:
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

        receita_service = get_receita_service()
        resultado = receita_service.consultar_cpf(
            cpf=cpf_limpo,
            data_nascimento=data_nascimento,
        )

        return {
            "cpf": formatar_cpf(cpf_limpo),
            "situacao": resultado.get("situacao"),
            "nome": resultado.get("nome"),
            "data_inscricao": resultado.get("data_inscricao"),
            "digito_verificador": resultado.get("digito_verificador"),
        }

    @staticmethod
    def consultar_cnpj(cnpj: str) -> Dict[str, Any]:
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

        receita_service = get_receita_service()
        resultado = receita_service.consultar_cnpj(cnpj=cnpj_limpo)

        return {
            "cnpj": formatar_cnpj(cnpj_limpo),
            "razao_social": resultado.get("razao_social"),
            "nome_fantasia": resultado.get("nome_fantasia"),
            "situacao_cadastral": resultado.get("situacao_cadastral"),
            "data_situacao": resultado.get("data_situacao"),
            "cnae_principal": resultado.get("cnae_principal"),
            "endereco": resultado.get("endereco"),
            "porte": resultado.get("porte"),
            "natureza_juridica": resultado.get("natureza_juridica"),
        }
