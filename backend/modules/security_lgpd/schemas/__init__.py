"""Schemas Pydantic do modulo de seguranca LGPD."""

from modules.security_lgpd.schemas.audit import (
    AuditLogListResponse,
    AuditLogRequest,
    AuditLogResponse,
)
from modules.security_lgpd.schemas.common import StandardResponse
from modules.security_lgpd.schemas.consent import (
    ConsentListResponse,
    ConsentRequest,
    ConsentResponse,
)
from modules.security_lgpd.schemas.encryption import (
    DecryptDataRequest,
    EncryptDataRequest,
    EncryptionResponse,
)
from modules.security_lgpd.schemas.erasure import (
    ErasureRequestSchema,
    ErasureStatusResponse,
)
from modules.security_lgpd.schemas.masking import (
    MaskDataRequest,
    MaskingFormatResponse,
)
from modules.security_lgpd.schemas.pia import (
    PIARequest,
    PIAResponse,
)

__all__ = [
    # Encryption
    "EncryptDataRequest",
    "DecryptDataRequest",
    "EncryptionResponse",
    # Masking
    "MaskDataRequest",
    "MaskingFormatResponse",
    # Consent
    "ConsentRequest",
    "ConsentResponse",
    "ConsentListResponse",
    # Erasure
    "ErasureRequestSchema",
    "ErasureStatusResponse",
    # PIA
    "PIARequest",
    "PIAResponse",
    # Audit
    "AuditLogRequest",
    "AuditLogResponse",
    "AuditLogListResponse",
    # Common
    "StandardResponse",
]
