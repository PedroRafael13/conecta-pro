"""
Controller de Reembolso — Departamento Pessoal.

Re-exporta endpoints de reembolso do módulo reimbursement.
"""

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reimbursements", tags=["DP - Reembolsos"])

# Re-export do router existente de reembolso
try:
    from modules.reimbursement.controllers.reimbursement_controller import (
        router as _reimbursement_router,
    )

    for route in _reimbursement_router.routes:
        router.routes.append(route)
    logger.info("Router de reembolso re-exportado para DP")
except ImportError:
    logger.info("Router de reembolso não disponível para re-export")
