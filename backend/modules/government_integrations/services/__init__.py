"""
Services para integrações governamentais.
"""

from .receita_federal_service import ReceitaFederalApiService
from .fgts_inss_service import FGTSINSSService
from .esocial_service import ESocialService
from .sefaz_service import SEFAZService

__all__ = [
    "ReceitaFederalApiService",
    "FGTSINSSService",
    "ESocialService",
    "SEFAZService",
]
