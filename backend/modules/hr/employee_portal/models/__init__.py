"""Models do Portal do Funcionário."""

from modules.hr.employee_portal.models.employee_document import (
    DocumentStatus,
    DocumentType,
    EmployeeDocument,
)
from modules.hr.employee_portal.models.employee_notification import (
    EmployeeNotification,
    NotificationChannel,
    NotificationPriority,
    NotificationType,
)
from modules.hr.employee_portal.models.employee_preferences import (
    EmployeePreferences,
    LanguagePreference,
    ThemePreference,
)
from modules.hr.employee_portal.models.payslip import (
    PaySlip,
    PaySlipStatus,
    PaySlipType,
)
from modules.hr.employee_portal.models.vacation_request import (
    VacationPeriod,
    VacationRequest,
    VacationStatus,
    VacationType,
)

__all__ = [
    # PaySlip
    "PaySlip",
    "PaySlipStatus",
    "PaySlipType",
    # VacationRequest
    "VacationRequest",
    "VacationStatus",
    "VacationType",
    "VacationPeriod",
    # EmployeeDocument
    "EmployeeDocument",
    "DocumentType",
    "DocumentStatus",
    # EmployeeNotification
    "EmployeeNotification",
    "NotificationType",
    "NotificationPriority",
    "NotificationChannel",
    # EmployeePreferences
    "EmployeePreferences",
    "ThemePreference",
    "LanguagePreference",
]
