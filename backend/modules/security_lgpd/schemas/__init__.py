"""Schemas Pydantic do modulo de seguranca LGPD."""

from modules.security_lgpd.schemas.encryption import (
    EncryptDataRequest,
    DecryptDataRequest,
    EncryptionResponse,
)
from modules.security_lgpd.schemas.masking import (
    MaskDataRequest,
    MaskingFormatResponse,
)
from modules.security_lgpd.schemas.consent import (
    ConsentRequest,
    ConsentResponse,
    ConsentListResponse,
)
from modules.security_lgpd.schemas.erasure import (
    ErasureRequestSchema,
    ErasureStatusResponse,
)
from modules.security_lgpd.schemas.pia import (
    PIARequest,
    PIAResponse,
)
from modules.security_lgpd.schemas.audit import (
    AuditLogRequest,
    AuditLogResponse,
    AuditLogListResponse,
)
from modules.security_lgpd.schemas.common import StandardResponse

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
