"""Compliance Manager para LGPD - Sprint 03."""

from modules.notifications.compliance.lgpd_manager import (
    LGPDComplianceManager,
    ConsentRecord,
    ConsentType,
    ConsentStatus,
    DataProcessingRequest,
    DataExportResult,
    ComplianceAuditLog,
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
