"""
Controller de Reembolso — Departamento Pessoal.

Re-exporta endpoints de reembolso do módulo reimbursement.
"""

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reimbursements", tags=["DP - Reembolsos"])

# Re-export do router existente de reembolso
# IMPORTANTE: usar include_router (NÃO append) para preservar prefixos
try:
    from modules.reimbursement.controllers.reimbursement_controller import (
        router as _reimbursement_router,
    )

    router.include_router(_reimbursement_router)
    logger.info("Router de reembolso re-exportado para DP")
except ImportError:
    logger.info("Router de reembolso não disponível para re-export")
