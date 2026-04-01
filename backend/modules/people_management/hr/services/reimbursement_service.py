"""
Serviço de Reembolso — Departamento Pessoal.

Re-exporta funcionalidades do módulo reimbursement existente.
"""

import logging

logger = logging.getLogger(__name__)

# Re-export do serviço existente
try:
    from modules.reimbursement.services.reimbursement_service import (
        ReimbursementService,
    )
except ImportError:
    logger.info("Módulo reimbursement não disponível para re-export")

    class ReimbursementService:  # type: ignore[no-redef]
        """Stub para quando o módulo de reembolso não está disponível."""

        def __init__(self, db=None):
            self.db = db

        async def list_requests(self, **kwargs):
            """Lista solicitações de reembolso (stub)."""
            return {"items": [], "total": 0, "message": "Módulo não disponível"}


__all__ = ["ReimbursementService"]
