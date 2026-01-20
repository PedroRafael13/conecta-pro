"""
Package: encryption
Description: Modulo de criptografia e protecao de dados para compliance LGPD.
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: LGPD Art. 46 - Seguranca e Sigilo de Dados
"""

from .crypto_manager import (
    CryptoManager,
    CryptoConfig,
    CryptoError,
    EncryptionError,
    DecryptionError,
    EncryptionAlgorithm,
    EncryptionResult,
    get_crypto_manager,
)

from .key_management import (
    KeyManager,
    KeyStatus,
    KeyPurpose,
    KeyAlgorithm,
    KeyMetadata,
    ManagedKey,
    KeyManagementError,
    KeyNotFoundError,
    KeyExpiredError,
    KeyRotationError,
    KeyDerivationService,
    EncryptedFileKeyStore,
    InMemoryKeyStore,
    get_key_manager,
    init_key_manager,
    generate_master_key,
    create_key_manager,
)

from .data_masking import (
    DataMasker,
    MaskingConfig,
    MaskingStrategy,
    MaskingLevel,
    MaskingRule,
    MaskingError,
    PIICategory,
    PIIFieldRegistry,
    get_data_masker,
    get_pii_registry,
    register_pii_fields,
    mask_cpf,
    mask_email,
    mask_phone,
    mask_pii_in_text,
    init_default_pii_registry,
)

__all__ = [
    # Crypto Manager
    "CryptoManager",
    "CryptoConfig",
    "CryptoError",
    "EncryptionError",
    "DecryptionError",
    "EncryptionAlgorithm",
    "EncryptionResult",
    "get_crypto_manager",
    # Key Management
    "KeyManager",
    "KeyStatus",
    "KeyPurpose",
    "KeyAlgorithm",
    "KeyMetadata",
    "ManagedKey",
    "KeyManagementError",
    "KeyNotFoundError",
    "KeyExpiredError",
    "KeyRotationError",
    "KeyDerivationService",
    "EncryptedFileKeyStore",
    "InMemoryKeyStore",
    "get_key_manager",
    "init_key_manager",
    "generate_master_key",
    "create_key_manager",
    # Data Masking
    "DataMasker",
    "MaskingConfig",
    "MaskingStrategy",
    "MaskingLevel",
    "MaskingRule",
    "MaskingError",
    "PIICategory",
    "PIIFieldRegistry",
    "get_data_masker",
    "get_pii_registry",
    "register_pii_fields",
    "mask_cpf",
    "mask_email",
    "mask_phone",
    "mask_pii_in_text",
    "init_default_pii_registry",
]

__version__ = "1.0.0"
__author__ = "Conecta PRO Team"
