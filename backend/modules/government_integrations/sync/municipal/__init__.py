"""
Sincronizadores de serviços municipais.

- NFS-e Manaus: Notas fiscais de serviço (padrão Manaus/AM)
- NFS-e Nacional: Padrão nacional (ABRASF)
"""

from .nfse_manaus_sync import NFSeManausSynchronizer

__all__ = [
    "NFSeManausSynchronizer",
]
