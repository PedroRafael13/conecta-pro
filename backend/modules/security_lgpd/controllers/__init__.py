"""Controllers do modulo de seguranca LGPD."""

from modules.security_lgpd.controllers.encryption_controller import router as encryption_router
from modules.security_lgpd.controllers.masking_controller import router as masking_router
from modules.security_lgpd.controllers.consent_controller import router as consent_router
from modules.security_lgpd.controllers.erasure_controller import router as erasure_router
from modules.security_lgpd.controllers.pia_controller import router as pia_router
from modules.security_lgpd.controllers.audit_controller import router as audit_router
from modules.security_lgpd.controllers.status_controller import router as status_router

__all__ = [
    "encryption_router",
    "masking_router",
    "consent_router",
    "erasure_router",
    "pia_router",
    "audit_router",
    "status_router",
]
