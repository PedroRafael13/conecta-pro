"""
Módulo FISCAL/CONTÁBIL — Agregador
Unifica: empresas + fiscal + government_integrations + certidões

Routers re-exportados dos módulos de implementação.
API URLs inalteradas.
Data migração: 2026-03-11
"""

# --- Empresas (Multi-CNPJ) ---
# --- Certidões (CNDs) — movido de comercial/bidding ---
from modules.bidding import certificate_router as bidding_certificate_router
from modules.empresas.controllers.bookkeeper_controller import router as bookkeeper_router
from modules.empresas.controllers.dashboard_controller import router as empresas_dashboard_router
from modules.empresas.controllers.dominio_controller import router as dominio_router
from modules.empresas.controllers.empresa_controller import router as empresas_router
from modules.empresas.controllers.migrador_controller import router as migrador_router
from modules.empresas.controllers.obligations_controller import router as obrigacoes_router
from modules.empresas.controllers.statements_controller import router as statements_router

# --- Fiscal (NFS-e Multi-Empresa) ---
from modules.fiscal.controllers.nfse_multi_controller import router as nfse_multi_router

# --- Government Integrations ---
from modules.government_integrations import government_integrations_router

__all__ = [
    "empresas_router",
    "migrador_router",
    "obrigacoes_router",
    "empresas_dashboard_router",
    "dominio_router",
    "bookkeeper_router",
    "statements_router",
    "nfse_multi_router",
    "government_integrations_router",
    "bidding_certificate_router",
]
