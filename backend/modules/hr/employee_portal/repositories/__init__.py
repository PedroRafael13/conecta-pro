"""Repositories do Portal do Funcionário."""

from modules.hr.employee_portal.repositories.document_repository import (
    DocumentRepository,
)
from modules.hr.employee_portal.repositories.notification_repository import (
    NotificationRepository,
)
from modules.hr.employee_portal.repositories.payslip_repository import (
    PaySlipRepository,
)
from modules.hr.employee_portal.repositories.preferences_repository import (
    PreferencesRepository,
)
from modules.hr.employee_portal.repositories.vacation_repository import (
    VacationPeriodRepository,
    VacationRequestRepository,
)

__all__ = [
    "PaySlipRepository",
    "VacationPeriodRepository",
    "VacationRequestRepository",
    "DocumentRepository",
    "NotificationRepository",
    "PreferencesRepository",
]
