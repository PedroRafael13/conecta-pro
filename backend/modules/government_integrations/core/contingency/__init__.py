"""
Sistema de Contingência para Integrações Governamentais.

Implementa:
- Matriz de contingência por UF
- Comutação automática de endpoints
- Testes periódicos de disponibilidade
"""

from .availability_checker import (
    ResultadoVerificacao,
    VerificadorDisponibilidade,
)
from .endpoint_switcher import (
    ComutadorEndpoints,
    StatusEndpoint,
)
from .uf_matrix import (
    ENDPOINTS_CENTRALIZADOS,
    MATRIZ_CONTINGENCIA_CTE,
    MATRIZ_CONTINGENCIA_MDFE,
    MATRIZ_CONTINGENCIA_NFE,
    EndpointConfig,
    MatrizContingencia,
    TipoContingencia,
)

__all__ = [
    # Matrix
    "MatrizContingencia",
    "EndpointConfig",
    "TipoContingencia",
    "MATRIZ_CONTINGENCIA_NFE",
    "MATRIZ_CONTINGENCIA_CTE",
    "MATRIZ_CONTINGENCIA_MDFE",
    "ENDPOINTS_CENTRALIZADOS",
    # Switcher
    "ComutadorEndpoints",
    "StatusEndpoint",
    # Checker
    "VerificadorDisponibilidade",
    "ResultadoVerificacao",
]
