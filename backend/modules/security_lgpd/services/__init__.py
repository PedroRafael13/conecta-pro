"""
Services do módulo de Segurança LGPD - Consolidado
=================================================

Módulo unificado com implementações avançadas de:
- Criptografia (AES-256-GCM, RSA, Fernet, ChaCha20)
- Mascaramento de PII
- Gestão de Consentimentos
- Exclusão de Dados (Right to be Forgotten)
- Auditoria com hash chain
- Privacy Impact Assessment

Compliance: LGPD (Lei 13.709/2018)
"""

# Criptografia
from modules.security_lgpd.services.crypto_service import (
    CryptoService,
    CryptoConfig,
    EncryptionAlgorithm,
    EncryptionResult,
    KeyType,
    CryptoError,
    EncryptionError,
    DecryptionError,
    KeyGenerationError,
    get_crypto_service,
)

# Auditoria
from modules.security_lgpd.services.audit_service import (
    AuditService,
    AuditAction,
    AuditSeverity,
    ResourceType,
    AuditContext,
    AuditEntry,
    AuditStoreInterface,
    InMemoryAuditStore,
    audit_action,
    get_audit_service,
    init_audit_service,
)

# Mascaramento
from modules.security_lgpd.services.masking_service import (
    MaskingService,
    MaskingStrategy,
    PIICategory,
    MaskingLevel,
    MaskingRule,
    MaskingConfig,
    get_masking_service,
    mask_cpf,
    mask_email,
    mask_phone,
    mask_pii_in_text,
)

# Consentimento
from modules.security_lgpd.services.consent_service import ConsentService

# Exclusão
from modules.security_lgpd.services.erasure_service import (
    ErasureService,
    ErasureStatus,
    ErasureMethod,
    RetentionReason,
    ErasureScope,
    ErasureError,
    DataLocation,
    ErasureResult,
    ErasureRequest,
    get_erasure_service,
)

# PIA (Privacy Impact Assessment)
from modules.security_lgpd.services.pia_service import PIAService

# Compatibilidade - alias para EncryptionService
EncryptionService = CryptoService

__all__ = [
    # Criptografia
    "CryptoService",
    "CryptoConfig",
    "EncryptionAlgorithm",
    "EncryptionResult",
    "KeyType",
    "CryptoError",
    "EncryptionError",
    "DecryptionError",
    "KeyGenerationError",
    "get_crypto_service",
    "EncryptionService",  # Alias
    # Auditoria
    "AuditService",
    "AuditAction",
    "AuditSeverity",
    "ResourceType",
    "AuditContext",
    "AuditEntry",
    "AuditStoreInterface",
    "InMemoryAuditStore",
    "audit_action",
    "get_audit_service",
    "init_audit_service",
    # Mascaramento
    "MaskingService",
    "MaskingStrategy",
    "PIICategory",
    "MaskingLevel",
    "MaskingRule",
    "MaskingConfig",
    "get_masking_service",
    "mask_cpf",
    "mask_email",
    "mask_phone",
    "mask_pii_in_text",
    # Consentimento
    "ConsentService",
    # Exclusão
    "ErasureService",
    "ErasureStatus",
    "ErasureMethod",
    "RetentionReason",
    "ErasureScope",
    "ErasureError",
    "DataLocation",
    "ErasureResult",
    "ErasureRequest",
    "get_erasure_service",
    # PIA
    "PIAService",
]
