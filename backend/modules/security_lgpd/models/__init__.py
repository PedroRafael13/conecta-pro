"""Models do modulo de seguranca LGPD."""

from modules.security_lgpd.models.audit_log import AuditAction, AuditLog, AuditSeverity
from modules.security_lgpd.models.consent import Consent, ConsentPurpose, ConsentStatus
from modules.security_lgpd.models.erasure_request import ErasureRequest, ErasureScope, ErasureStatus
from modules.security_lgpd.models.pia_assessment import PIAAssessment, RiskLevel

__all__ = [
    # Consent
    "Consent",
    "ConsentStatus",
    "ConsentPurpose",
    # Erasure
    "ErasureRequest",
    "ErasureStatus",
    "ErasureScope",
    # Audit
    "AuditLog",
    "AuditAction",
    "AuditSeverity",
    # PIA
    "PIAAssessment",
    "RiskLevel",
]
