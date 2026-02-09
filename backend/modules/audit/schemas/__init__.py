"""
Schemas do módulo de Auditoria e Compliance
Sprint 33: Auditoria e Compliance
"""

from modules.audit.schemas.audit_schemas import (
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

__all__ = [
    # AuditLog
    "AuditLogCreate",
    "AuditLogResponse",
    "AuditLogList",
    "AuditLogFilter",
    "AuditLogStats",
    # ComplianceRule
    "ComplianceRuleCreate",
    "ComplianceRuleUpdate",
    "ComplianceRuleResponse",
    "ComplianceRuleList",
    # ComplianceCheck
    "ComplianceCheckCreate",
    "ComplianceCheckUpdate",
    "ComplianceCheckResponse",
    "ComplianceCheckList",
    # DataRetention
    "DataRetentionCreate",
    "DataRetentionUpdate",
    "DataRetentionResponse",
    "DataRetentionList",
    "DataRetentionExecution",
    # AccessHistory
    "AccessHistoryCreate",
    "AccessHistoryResponse",
    "AccessHistoryList",
    "AccessHistoryFilter",
    "AccessHistoryStats",
    # Dashboard
    "AuditDashboard",
    "ComplianceOverview",
    "SecurityOverview",
]
