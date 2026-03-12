"""
Employee Portal Aggregator — Router principal do portal do funcionario.

Inclui todos os sub-routers sob o prefixo /portal.
"""

import logging

from fastapi import APIRouter

from .controllers import (
    my_data_router,
    my_documents_router,
    my_payslips_router,
    my_schedules_router,
    portal_auth_router,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/portal", tags=["Portal do Funcionario"])

# Auth e dashboard
router.include_router(portal_auth_router)

# Escalas
router.include_router(my_schedules_router)

# Contracheques
router.include_router(my_payslips_router)

# Documentos e assinatura digital
router.include_router(my_documents_router)

# Dados pessoais
router.include_router(my_data_router)
