"""
Extratores SPED (Sistema Público de Escrituração Digital).

Inclui:
- SPED Fiscal (EFD-ICMS/IPI)
- SPED Contábil (ECD)
"""

from .sped_contabil_extractor import ExtratorSPEDContabil
from .sped_fiscal_extractor import ExtratorSPEDFiscal

__all__ = [
    "ExtratorSPEDFiscal",
    "ExtratorSPEDContabil",
]
