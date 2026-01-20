"""
Package: security_lgpd
Description: Modulo de Seguranca e Compliance LGPD
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: LGPD - Lei Geral de Protecao de Dados (Lei 13.709/2018)
"""

from .encryption import (
    CryptoManager,
    CryptoConfig,
    EncryptionAlgorithm,
    KeyManager,
    KeyStatus,
    KeyPurpose,
    DataMasker,
    MaskingStrategy,
    MaskingLevel,
    PIICategory,
    get_crypto_manager,
    get_key_manager,
    get_data_masker,
    mask_cpf,
    mask_email,
    mask_phone,
)

from .compliance import (
    ConsentManager,
    ConsentPurpose,
    ConsentStatus,
    LegalBasis,
    DataErasureManager,
    ErasureStatus,
    PIAManager,
    RiskLevel,
    get_consent_manager,
    get_erasure_manager,
    get_pia_manager,
    requires_dpia,
)

from .audit import (
    AuditLogger,
    AuditAction,
    AuditSeverity,
    ResourceType,
    get_audit_logger,
    init_audit_logger,
    audit_action,
)

__all__ = [
    # Encryption
    "CryptoManager",
    "CryptoConfig",
    "EncryptionAlgorithm",
    "KeyManager",
    "KeyStatus",
    "KeyPurpose",
    "DataMasker",
    "MaskingStrategy",
    "MaskingLevel",
    "PIICategory",
    "get_crypto_manager",
    "get_key_manager",
    "get_data_masker",
    "mask_cpf",
    "mask_email",
    "mask_phone",
    # Compliance
    "ConsentManager",
    "ConsentPurpose",
    "ConsentStatus",
    "LegalBasis",
    "DataErasureManager",
    "ErasureStatus",
    "PIAManager",
    "RiskLevel",
    "get_consent_manager",
    "get_erasure_manager",
    "get_pia_manager",
    "requires_dpia",
    # Audit
    "AuditLogger",
    "AuditAction",
    "AuditSeverity",
    "ResourceType",
    "get_audit_logger",
    "init_audit_logger",
    "audit_action",
]

__version__ = "1.0.0"
__author__ = "Conecta PRO Team"
