"""Integracoes do modulo de licitacoes."""

from modules.bidding.integrations.bll.client import BLLClient
from modules.bidding.integrations.comprasnet.client import ComprasNetClient
from modules.bidding.integrations.ecompras_am.client import EComprasAMClient
from modules.bidding.integrations.licitacoes_e.client import LicitacoesEClient
from modules.bidding.integrations.pncp.client import PNCPClient
from modules.bidding.integrations.pncp.models import PNCPCompra, PNCPDocumento, PNCPItem, PNCPOrgao
from modules.bidding.integrations.pncp.parser import PNCPParser
from modules.bidding.integrations.portal_compras_publicas.client import PortalComprasPublicasClient

__all__ = [
    # PNCP
    "PNCPClient",
    "PNCPParser",
    "PNCPCompra",
    "PNCPOrgao",
    "PNCPItem",
    "PNCPDocumento",
    # ComprasNet (Compras.gov.br)
    "ComprasNetClient",
    # e-Compras AM
    "EComprasAMClient",
    # Licitacoes-e (Banco do Brasil)
    "LicitacoesEClient",
    # BLL Compras
    "BLLClient",
    # Portal de Compras Publicas
    "PortalComprasPublicasClient",
]
