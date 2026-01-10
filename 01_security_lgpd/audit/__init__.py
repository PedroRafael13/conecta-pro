"""
Package: audit
Description: Modulo de auditoria e logging para compliance LGPD.
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: LGPD Art. 37, 49 - Registro de Operacoes
"""

from .audit_logger import (
    AuditLogger,
    AuditEntry,
    AuditContext,
    AuditAction,
    AuditSeverity,
    ResourceType,
    AuditStoreInterface,
    InMemoryAuditStore,
    AuditLogModel,
    AuditMiddleware,
    get_audit_logger,
    init_audit_logger,
    audit_action,
)

__all__ = [
    "AuditLogger",
    "AuditEntry",
    "AuditContext",
    "AuditAction",
    "AuditSeverity",
    "ResourceType",
    "AuditStoreInterface",
    "InMemoryAuditStore",
    "AuditLogModel",
    "AuditMiddleware",
    "get_audit_logger",
    "init_audit_logger",
    "audit_action",
]

__version__ = "1.0.0"
__author__ = "Conecta PRO Team"
