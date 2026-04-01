"""
Portal do Funcionario - Conecta PRO
===================================
Self-service para funcionarios com acesso a contracheques,
ferias, documentos e preferencias pessoais.

Funcionalidades:
- Contracheques: Visualizacao e contestacao
- Ferias: Solicitacao e acompanhamento
- Documentos: Assinatura digital e download
- Notificacoes: Central de comunicados
- Preferencias: Configuracoes pessoais
"""

from modules.hr.employee_portal.controllers import router as portal_router
from modules.hr.employee_portal.models import (
    EmployeeDocument,
    EmployeeNotification,
    EmployeePreferences,
    PaySlip,
    PaySlipStatus,
    PaySlipType,
    VacationPeriod,
    VacationRequest,
    VacationStatus,
    VacationType,
)
from modules.hr.employee_portal.services import (
    DocumentService,
    PaySlipService,
    PortalNotificationService,
    PreferencesService,
    VacationService,
)

__all__ = [
    # Router
    "portal_router",
    # Models
    "PaySlip",
    "PaySlipStatus",
    "PaySlipType",
    "VacationRequest",
    "VacationStatus",
    "VacationType",
    "VacationPeriod",
    "EmployeeDocument",
    "EmployeeNotification",
    "EmployeePreferences",
    # Services
    "PaySlipService",
    "VacationService",
    "DocumentService",
    "PortalNotificationService",
    "PreferencesService",
]
