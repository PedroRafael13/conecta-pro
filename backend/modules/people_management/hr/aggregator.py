"""
Aggregator — Departamento Pessoal (DP/HR).

Router principal que inclui todos os sub-routers do módulo DP.
Montado sob o prefixo /hr no FastAPI.
"""

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/hr", tags=["Departamento Pessoal"])

# Importar e incluir todos os sub-routers
try:
    from modules.people_management.hr.controllers.employee_controller import (
        router as employee_router,
    )

    router.include_router(employee_router)
    logger.debug("DP: employee_router incluído")
except ImportError as e:
    logger.warning("DP: falha ao incluir employee_router: %s", e)

try:
    from modules.people_management.hr.controllers.admission_controller import (
        router as admission_router,
    )

    router.include_router(admission_router)
    logger.debug("DP: admission_router incluído")
except ImportError as e:
    logger.warning("DP: falha ao incluir admission_router: %s", e)

try:
    from modules.people_management.hr.controllers.termination_controller import (
        router as termination_router,
    )

    router.include_router(termination_router)
    logger.debug("DP: termination_router incluído")
except ImportError as e:
    logger.warning("DP: falha ao incluir termination_router: %s", e)

try:
    from modules.people_management.hr.controllers.benefits_controller import (
        router as benefits_router,
    )

    router.include_router(benefits_router)
    logger.debug("DP: benefits_router incluído")
except ImportError as e:
    logger.warning("DP: falha ao incluir benefits_router: %s", e)

try:
    from modules.people_management.hr.controllers.contract_controller import (
        router as contract_router,
    )

    router.include_router(contract_router)
    logger.debug("DP: contract_router incluído")
except ImportError as e:
    logger.warning("DP: falha ao incluir contract_router: %s", e)

try:
    from modules.people_management.hr.controllers.vacation_controller import (
        router as vacation_router,
    )

    router.include_router(vacation_router)
    logger.debug("DP: vacation_router incluído")
except ImportError as e:
    logger.warning("DP: falha ao incluir vacation_router: %s", e)

try:
    from modules.people_management.hr.controllers.discipline_controller import (
        router as discipline_router,
    )

    router.include_router(discipline_router)
    logger.debug("DP: discipline_router incluído")
except ImportError as e:
    logger.warning("DP: falha ao incluir discipline_router: %s", e)

try:
    from modules.people_management.hr.controllers.time_tracking_controller import (
        router as time_tracking_router,
    )

    router.include_router(time_tracking_router)
    logger.debug("DP: time_tracking_router incluído")
except ImportError as e:
    logger.warning("DP: falha ao incluir time_tracking_router: %s", e)

try:
    from modules.people_management.hr.controllers.payroll_controller import (
        router as payroll_router,
    )

    router.include_router(payroll_router)
    logger.debug("DP: payroll_router incluído")
except ImportError as e:
    logger.warning("DP: falha ao incluir payroll_router: %s", e)

try:
    from modules.people_management.hr.controllers.reimbursement_controller import (
        router as reimbursement_router,
    )

    router.include_router(reimbursement_router)
    logger.debug("DP: reimbursement_router incluído")
except ImportError as e:
    logger.warning("DP: falha ao incluir reimbursement_router: %s", e)

logger.info("Módulo Departamento Pessoal (DP) carregado — aggregator montado em /hr")
