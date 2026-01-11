"""
Schemas Pydantic para integrações governamentais.
"""

from .common import StandardResponse
from .receita_federal import (
    ConsultaCNPJRequest,
    ConsultaCPFRequest,
    ValidateDocumentRequest,
)
from .fgts_inss import CalculoFGTSRequest, CalculoINSSRequest
from .esocial import ESocialEventRequest
from .sefaz import NFERequest

__all__ = [
    # Common
    "StandardResponse",
    # Receita Federal
    "ValidateDocumentRequest",
    "ConsultaCPFRequest",
    "ConsultaCNPJRequest",
    # FGTS/INSS
    "CalculoFGTSRequest",
    "CalculoINSSRequest",
    # eSocial
    "ESocialEventRequest",
    # SEFAZ
    "NFERequest",
]
