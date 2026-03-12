"""
Operations Aggregator — Router que re-exporta routers do modulo operacional.

Parte da categoria People Management.
Monta todos os sub-routers sob o prefixo /operations.
"""

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/operations", tags=["People Management - Operations"])

# Re-exportar routers do operacional
try:
    from modules.operacional.controllers import (
        allocation_router,
        dashboard_router,
        employee_router,
        post_router,
        scale_router,
        scale_template_router,
        shift_router,
        substitution_router,
        time_bank_router,
    )

    router.include_router(post_router, prefix="/postos", tags=["Operations - Postos"])
    router.include_router(scale_router, prefix="/escalas", tags=["Operations - Escalas"])
    router.include_router(scale_template_router, tags=["Operations - Templates"])
    router.include_router(shift_router, prefix="/turnos", tags=["Operations - Turnos"])
    router.include_router(allocation_router, prefix="/alocacoes", tags=["Operations - Alocacoes"])
    router.include_router(substitution_router, prefix="/substituicoes", tags=["Operations - Substituicoes"])
    router.include_router(time_bank_router, prefix="/banco-horas", tags=["Operations - Banco de Horas"])
    router.include_router(dashboard_router, tags=["Operations - Dashboard"])
    router.include_router(employee_router, tags=["Operations - Employees"])

except ImportError as e:
    logger.warning("Routers do operacional nao disponiveis: %s", e)

# Sub-modulos opcionais
try:
    from modules.operacional import ai_router

    router.include_router(ai_router, tags=["Operations - AI"])
except ImportError:
    pass

try:
    from modules.operacional import occurrence_router

    router.include_router(occurrence_router, prefix="/ocorrencias", tags=["Operations - Ocorrencias"])
except ImportError:
    pass

try:
    from modules.operacional import disciplinary_router

    router.include_router(
        disciplinary_router,
        prefix="/medidas-administrativas",
        tags=["Operations - Disciplinar"],
    )
except ImportError:
    pass

try:
    from modules.operacional import communication_router

    router.include_router(communication_router, tags=["Operations - Comunicacao"])
except ImportError:
    pass

try:
    from modules.operacional import vacation_router

    router.include_router(vacation_router, tags=["Operations - Ferias"])
except ImportError:
    pass

try:
    from modules.operacional import inspection_round_router

    router.include_router(inspection_round_router, prefix="/rondas", tags=["Operations - Rondas"])
except ImportError:
    pass
