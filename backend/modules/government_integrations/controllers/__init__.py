"""
Controllers para integrações governamentais.

Sprint 33: Adicionado suporte a certificados digitais A1.
Sprint 34: Adicionado NFS-e Manaus (Prefeitura de Manaus - ABRASF 2.04)
"""

from fastapi import APIRouter

from .receita_federal_controller import router as receita_federal_router
from .fgts_inss_controller import router as fgts_inss_router
from .esocial_controller import router as esocial_router
from .sefaz_controller import router as sefaz_router
from .status_controller import router as status_router
from .certificate_controller import router as certificate_router
from .nfse_manaus_controller import router as nfse_manaus_router

# Router principal que agrega todos os sub-routers
router = APIRouter(prefix="/government", tags=["Government - Integracoes Governamentais"])

# Inclui sub-routers
router.include_router(receita_federal_router)
router.include_router(fgts_inss_router)
router.include_router(esocial_router)
router.include_router(sefaz_router)
router.include_router(status_router)
router.include_router(certificate_router)
router.include_router(nfse_manaus_router)

__all__ = [
    "router",
    "receita_federal_router",
    "fgts_inss_router",
    "esocial_router",
    "sefaz_router",
    "status_router",
    "certificate_router",
    "nfse_manaus_router",
]
