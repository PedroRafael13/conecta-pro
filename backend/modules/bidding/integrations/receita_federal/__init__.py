"""
Integracao com Receita Federal e TST
=====================================
Clients para consulta de certidoes:
- CND Federal (Receita Federal + PGFN)
- CNDT Trabalhista (TST)
"""

from modules.bidding.integrations.receita_federal.cnd_client import CNDFederalClient
from modules.bidding.integrations.receita_federal.cndt_client import CNDTTrabalhistaClient

__all__ = [
    "CNDFederalClient",
    "CNDTTrabalhistaClient",
]
