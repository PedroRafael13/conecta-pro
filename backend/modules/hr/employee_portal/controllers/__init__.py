"""Controllers do Portal do Funcionário."""

from fastapi import APIRouter

from modules.hr.employee_portal.controllers.payslip_controller import (
    router as payslip_router,
)
from modules.hr.employee_portal.controllers.vacation_controller import (
    router as vacation_router,
)
from modules.hr.employee_portal.controllers.document_controller import (
    router as document_router,
)
from modules.hr.employee_portal.controllers.notification_controller import (
    router as notification_router,
)
from modules.hr.employee_portal.controllers.preferences_controller import (
    router as preferences_router,
)

router = APIRouter(prefix="/portal", tags=["Employee Portal"])

router.include_router(payslip_router)
router.include_router(vacation_router)
router.include_router(document_router)
router.include_router(notification_router)
router.include_router(preferences_router)

__all__ = ["router"]
