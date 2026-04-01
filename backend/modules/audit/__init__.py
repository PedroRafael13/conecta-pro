"""
Module: audit
Description: Modulo de Auditoria e Compliance

DEPRECATED: Use 'modules.gestao' instead for router imports.
Deprecation date: 2026-03-11. Removal target: 2026-05-11.

Estrutura modular:
- models/: Modelos SQLAlchemy para persistencia
- schemas/: Schemas Pydantic para validacao
- services/: Logica de negocio
- controllers/: Endpoints FastAPI
- repositories/: Acesso a dados
"""

import warnings

warnings.warn(
    "Importing from 'modules.audit' is deprecated. "
    "Use 'modules.gestao' for router access. "
    "This module will be removed after 2026-05-11.",
    DeprecationWarning,
    stacklevel=2,
)

from fastapi import APIRouter  # noqa: E402

# Importa router do controller
from modules.audit.controllers import router as audit_controller_router  # noqa: E402

# Cria router principal do modulo
audit_router = APIRouter(prefix="/audit", tags=["Audit - Auditoria e Compliance"])

# Inclui o sub-router
audit_router.include_router(audit_controller_router)

# Exporta tambem o router antigo para compatibilidade
router = audit_router

# Re-export models principais
from modules.audit.models import (  # noqa: E402
    # AccessHistory
    AccessHistory,
    AccessResult,
    AccessType,
    AuditAction,
    AuditCategory,
    # AuditLog
    AuditLog,
    AuditResult,
    AuditSeverity,
    CheckResult,
    CheckStatus,
    CheckType,
    # ComplianceCheck
    ComplianceCheck,
    ComplianceFramework,
    # ComplianceRule
    ComplianceRule,
    DataCategory,
    # DataRetention
    DataRetention,
    DeviceType,
    RetentionAction,
    RetentionPeriod,
    RetentionStatus,
    RiskLevel,
    RuleCategory,
    RuleSeverity,
    RuleStatus,
)

# Re-export repositories
from modules.audit.repositories import AuditRepository  # noqa: E402

# Re-export schemas principais
from modules.audit.schemas import (  # noqa: E402
    # AccessHistory
    AccessHistoryCreate,
    AccessHistoryFilter,
    AccessHistoryList,
    AccessHistoryResponse,
    AccessHistoryStats,
    # Dashboard
    AuditDashboard,
    # AuditLog
    AuditLogCreate,
    AuditLogFilter,
    AuditLogList,
    AuditLogResponse,
    AuditLogStats,
    # ComplianceCheck
    ComplianceCheckCreate,
    ComplianceCheckList,
    ComplianceCheckResponse,
    ComplianceCheckUpdate,
    ComplianceOverview,
    # ComplianceRule
    ComplianceRuleCreate,
    ComplianceRuleList,
    ComplianceRuleResponse,
    ComplianceRuleUpdate,
    # DataRetention
    DataRetentionCreate,
    DataRetentionExecution,
    DataRetentionList,
    DataRetentionResponse,
    DataRetentionUpdate,
    SecurityOverview,
)

# Re-export services
from modules.audit.services import AuditService  # noqa: E402

__all__ = [
    # Router principal
    "audit_router",
    "router",
    # Sub-routers
    "audit_controller_router",
    # Models - AuditLog
    "AuditLog",
    "AuditAction",
    "AuditCategory",
    "AuditSeverity",
    "AuditResult",
    # Models - ComplianceRule
    "ComplianceRule",
    "ComplianceFramework",
    "RuleCategory",
    "RuleSeverity",
    "RuleStatus",
    # Models - ComplianceCheck
    "ComplianceCheck",
    "CheckStatus",
    "CheckResult",
    "CheckType",
    # Models - DataRetention
    "DataRetention",
    "RetentionPeriod",
    "RetentionAction",
    "RetentionStatus",
    "DataCategory",
    # Models - AccessHistory
    "AccessHistory",
    "AccessType",
    "AccessResult",
    "DeviceType",
    "RiskLevel",
    # Services
    "AuditService",
    # Repositories
    "AuditRepository",
    # Schemas - AuditLog
    "AuditLogCreate",
    "AuditLogResponse",
    "AuditLogList",
    "AuditLogFilter",
    "AuditLogStats",
    # Schemas - ComplianceRule
    "ComplianceRuleCreate",
    "ComplianceRuleUpdate",
    "ComplianceRuleResponse",
    "ComplianceRuleList",
    # Schemas - ComplianceCheck
    "ComplianceCheckCreate",
    "ComplianceCheckUpdate",
    "ComplianceCheckResponse",
    "ComplianceCheckList",
    # Schemas - DataRetention
    "DataRetentionCreate",
    "DataRetentionUpdate",
    "DataRetentionResponse",
    "DataRetentionList",
    "DataRetentionExecution",
    # Schemas - AccessHistory
    "AccessHistoryCreate",
    "AccessHistoryResponse",
    "AccessHistoryList",
    "AccessHistoryFilter",
    "AccessHistoryStats",
    # Schemas - Dashboard
    "AuditDashboard",
    "ComplianceOverview",
    "SecurityOverview",
]

__version__ = "1.0.0"
