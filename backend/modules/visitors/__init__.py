"""Módulo de Visitantes do ERP Conecta Mais.

Este módulo gerencia todo o ciclo de vida de visitantes:
- Cadastro e identificação de visitantes
- Autorizações de acesso (únicas, periódicas, recorrentes, permanentes)
- Logs de entrada e saída
- Agendamentos de visitas
- Análise de padrões com IA
"""

from modules.visitors.models import (
    Visitor,
    VisitorAuthorization,
    VisitorLog,
    VisitorSchedule,
    VisitorType,
    VisitorStatus,
    DocumentType,
    AuthorizationType,
    AuthorizationStatus,
    RecurrenceType,
    AccessType,
    AccessMethod,
    AccessPoint,
    DenialReason,
    ScheduleStatus,
    SchedulePriority,
)

from modules.visitors.services import (
    VisitorService,
    AuthorizationService,
    LogService,
    ScheduleService,
    VisitorAIService,
)

from modules.visitors.controllers import (
    visitor_router,
    authorization_router,
    log_router,
    schedule_router,
)

__all__ = [
    # Models
    "Visitor",
    "VisitorAuthorization",
    "VisitorLog",
    "VisitorSchedule",
    # Enums
    "VisitorType",
    "VisitorStatus",
    "DocumentType",
    "AuthorizationType",
    "AuthorizationStatus",
    "RecurrenceType",
    "AccessType",
    "AccessMethod",
    "AccessPoint",
    "DenialReason",
    "ScheduleStatus",
    "SchedulePriority",
    # Services
    "VisitorService",
    "AuthorizationService",
    "LogService",
    "ScheduleService",
    "VisitorAIService",
    # Routers
    "visitor_router",
    "authorization_router",
    "log_router",
    "schedule_router",
]
