"""Compliance Manager para LGPD - Sprint 03."""

from modules.notifications.compliance.lgpd_manager import (
    ComplianceAuditLog,
    ConsentRecord,
    ConsentStatus,
    ConsentType,
    DataExportResult,
    DataProcessingRequest,
    LGPDComplianceManager,
)

__all__ = [
    "LGPDComplianceManager",
    "ConsentRecord",
    "ConsentType",
    "ConsentStatus",
    "DataProcessingRequest",
    "DataExportResult",
    "ComplianceAuditLog",
]
