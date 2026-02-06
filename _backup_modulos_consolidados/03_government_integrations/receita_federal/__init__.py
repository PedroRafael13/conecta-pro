"""
Package: receita_federal
Description: Modulo de integracao com Receita Federal (CNPJ/CPF/Certidoes)
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: Legislacao fiscal brasileira
"""

from .receita_federal import (
    ReceitaFederalService,
    DocumentValidator,
    ConsultaCNPJ,
    ConsultaCPF,
    Certidao,
    SituacaoCadastral,
    TipoCertidao,
    ReceitaFederalError,
    DocumentoInvalidoError,
    ConsultaError,
    get_receita_service,
    init_receita_service,
    validar_cpf,
    validar_cnpj,
    formatar_cpf,
    formatar_cnpj,
)

__all__ = [
    "ReceitaFederalService",
    "DocumentValidator",
    "ConsultaCNPJ",
    "ConsultaCPF",
    "Certidao",
    "SituacaoCadastral",
    "TipoCertidao",
    "ReceitaFederalError",
    "DocumentoInvalidoError",
    "ConsultaError",
    "get_receita_service",
    "init_receita_service",
    "validar_cpf",
    "validar_cnpj",
    "formatar_cpf",
    "formatar_cnpj",
]

__version__ = "1.0.0"
