"""Models do Portal do Funcionário."""

from modules.hr.employee_portal.models.payslip import (
    PaySlip,
    PaySlipStatus,
    PaySlipType,
)
from modules.hr.employee_portal.models.vacation_request import (
    VacationRequest,
    VacationStatus,
    VacationType,
    VacationPeriod,
)
from modules.hr.employee_portal.models.employee_document import (
    EmployeeDocument,
    DocumentType,
    DocumentStatus,
)
from modules.hr.employee_portal.models.employee_notification import (
    EmployeeNotification,
    NotificationType,
    NotificationPriority,
    NotificationChannel,
)
from modules.hr.employee_portal.models.employee_preferences import (
    EmployeePreferences,
    ThemePreference,
    LanguagePreference,
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
