"""Repositories do modulo de seguranca LGPD."""

from modules.security_lgpd.repositories.audit_repository import AuditRepository
from modules.security_lgpd.repositories.consent_repository import ConsentRepository
from modules.security_lgpd.repositories.erasure_repository import ErasureRepository
from modules.security_lgpd.repositories.pia_repository import PIARepository

__all__ = [
    "ConsentRepository",
    "ErasureRepository",
    "AuditRepository",
    "PIARepository",
]
