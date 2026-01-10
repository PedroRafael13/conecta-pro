"""
modules/fase5/cct_compliance/__init__.py - CCT Compliance Module
================================================================
Compliance automatico com CCT SINDCOND 2026
"""

from .service import CCTComplianceService
from .models import (
    CargoSINDCOND,
    SalarioBase,
    Beneficio,
    JornadaTrabalho,
    ValidacaoCCT
)
from .enums import (
    TipoCargo,
    TipoJornada,
    TipoBeneficio,
    StatusValidacao
)

__all__ = [
    "CCTComplianceService",
    "CargoSINDCOND",
    "SalarioBase",
    "Beneficio",
    "JornadaTrabalho",
    "ValidacaoCCT",
    "TipoCargo",
    "TipoJornada",
    "TipoBeneficio",
    "StatusValidacao"
]
