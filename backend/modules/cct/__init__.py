"""
Modulo CCT 2026 — SINDECOMPRESTS/SINDICOND-AM.

Convencao Coletiva de Trabalho aplicavel a Conecta Mais Patrimonial.
Vigencia: 01/01/2026 a 31/12/2026 — Registro MTE: AM000613/2025.

Sub-modulos:
- models: Tabela salarial, adicionais, beneficios, feriados
- schemas: Pydantic schemas para API
- services: Logica de validacao e calculo
- controllers: Endpoints REST
- validators: Regras de compliance CCT
"""

from fastapi import APIRouter

router = APIRouter(prefix="/cct", tags=["CCT 2026 — SINDECOMPRESTS/SINDICOND-AM"])


def register_routers() -> None:
    """Registra sub-routers do modulo CCT."""
    import logging

    _logger = logging.getLogger(__name__)

    try:
        from .controllers.salary_controller import router as salary_router

        router.include_router(salary_router)
        _logger.debug("CCT: salary_router incluido")
    except ImportError as exc:
        _logger.warning("CCT: falha ao incluir salary_router: %s", exc)

    try:
        from .controllers.benefits_controller import router as benefits_router

        router.include_router(benefits_router)
        _logger.debug("CCT: benefits_router incluido")
    except ImportError as exc:
        _logger.warning("CCT: falha ao incluir benefits_router: %s", exc)

    try:
        from .controllers.schedule_controller import router as schedule_router

        router.include_router(schedule_router)
        _logger.debug("CCT: schedule_router incluido")
    except ImportError as exc:
        _logger.warning("CCT: falha ao incluir schedule_router: %s", exc)

    try:
        from .controllers.compliance_controller import router as compliance_router

        router.include_router(compliance_router)
        _logger.debug("CCT: compliance_router incluido")
    except ImportError as exc:
        _logger.warning("CCT: falha ao incluir compliance_router: %s", exc)

    try:
        from .controllers.termination_controller import router as termination_router

        router.include_router(termination_router)
        _logger.debug("CCT: termination_router incluido")
    except ImportError as exc:
        _logger.warning("CCT: falha ao incluir termination_router: %s", exc)

    try:
        from .controllers.holidays_controller import router as holidays_router

        router.include_router(holidays_router)
        _logger.debug("CCT: holidays_router incluido")
    except ImportError as exc:
        _logger.warning("CCT: falha ao incluir holidays_router: %s", exc)


register_routers()
