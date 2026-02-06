"""
Extratores de NFS-e (Nota Fiscal de Serviço Eletrônica).

Inclui:
- NFS-e Nacional: Sistema nacional unificado
- NFS-e Manaus: Sistema municipal de Manaus
"""

from .manaus_extractor import ExtratorNFSeManaus
from .nfse_nacional_extractor import ExtratorNFSeNacional

__all__ = [
    "ExtratorNFSeManaus",
    "ExtratorNFSeNacional",
]
