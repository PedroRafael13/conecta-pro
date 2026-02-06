"""
Sistema de Contingência para Integrações Governamentais.

Implementa:
- Matriz de contingência por UF
- Comutação automática de endpoints
- Testes periódicos de disponibilidade
"""

from .uf_matrix import (
    MatrizContingencia,
    EndpointConfig,
    TipoContingencia,
    MATRIZ_CONTINGENCIA_NFE,
    MATRIZ_CONTINGENCIA_CTE,
    MATRIZ_CONTINGENCIA_MDFE,
    ENDPOINTS_CENTRALIZADOS,
)
from .endpoint_switcher import (
    ComutadorEndpoints,
    StatusEndpoint,
)
from .availability_checker import (
    VerificadorDisponibilidade,
    ResultadoVerificacao,
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
