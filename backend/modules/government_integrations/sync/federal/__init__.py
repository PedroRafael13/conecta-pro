"""
Sincronizadores de serviços federais.

- eSocial: Eventos trabalhistas e previdenciários
- Receita Federal: e-CAC, certidões, Simples Nacional
- FGTS Digital: Guias e informações FGTS
- INSS: Contribuições previdenciárias
"""

from .esocial_sync import ESocialSynchronizer
from .receita_sync import ReceitaFederalSynchronizer

__all__ = [
    "ESocialSynchronizer",
    "ReceitaFederalSynchronizer",
]
