"""
Package: sefaz
Description: Modulo de integracao com SEFAZ (NFe/NFCe/CTe)
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: Legislacao fiscal brasileira - Layout NFe 4.00
"""

from .sefaz_manager import (
    SEFAZManager,
    NotaFiscal,
    Produto,
    Destinatario,
    Pagamento,
    Transporte,
    DocumentType,
    DocumentStatus,
    Environment,
    SEFAZError,
    ValidationError,
    TransmissionError,
    XMLBuilder,
    get_sefaz_manager,
    init_sefaz_manager,
)

__all__ = [
    "SEFAZManager",
    "NotaFiscal",
    "Produto",
    "Destinatario",
    "Pagamento",
    "Transporte",
    "DocumentType",
    "DocumentStatus",
    "Environment",
    "SEFAZError",
    "ValidationError",
    "TransmissionError",
    "XMLBuilder",
    "get_sefaz_manager",
    "init_sefaz_manager",
]

__version__ = "1.0.0"
