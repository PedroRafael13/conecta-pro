"""
Módulo de sincronização de dados governamentais.

Fornece sincronizadores para extração e atualização de dados de:
- Serviços federais (eSocial, Receita Federal, FGTS, INSS)
- Serviços estaduais (NF-e, CT-e, MDF-e, SPED)
- Serviços municipais (NFS-e)
"""

from .base_sync import BaseSynchronizer, SyncConfig, SyncResult, SyncStatus
from .sync_manager import SyncManager, ServicoGov

# Federal
from .federal.esocial_sync import ESocialSynchronizer
from .federal.receita_sync import ReceitaFederalSynchronizer

# Estadual
from .estadual.nfe_sync import NFeSynchronizer

# Municipal
from .municipal.nfse_manaus_sync import NFSeManausSynchronizer

__all__ = [
    # Base
    "BaseSynchronizer",
    "SyncConfig",
    "SyncResult",
    "SyncStatus",
    "SyncManager",
    "ServicoGov",
    # Federal
    "ESocialSynchronizer",
    "ReceitaFederalSynchronizer",
    # Estadual
    "NFeSynchronizer",
    # Municipal
    "NFSeManausSynchronizer",
]
