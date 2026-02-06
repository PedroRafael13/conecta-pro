"""
Sincronizadores de serviços estaduais (SEFAZ).

- NF-e: Notas fiscais eletrônicas
- CT-e: Conhecimento de transporte eletrônico
- MDF-e: Manifesto de documentos fiscais
- SPED: Arquivos fiscais SPED
"""

from .nfe_sync import NFeSynchronizer

__all__ = [
    "NFeSynchronizer",
]
