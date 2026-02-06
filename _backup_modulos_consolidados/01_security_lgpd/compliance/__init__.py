"""
Package: compliance
Description: Modulo de compliance LGPD com gestao de consentimentos,
             exclusao de dados e avaliacao de impacto.
Author: Claude AI + Human Developer
Date: 2026-01-10
Quality Score Target: 99+/100
Compliance: LGPD - Lei Geral de Protecao de Dados
"""

from .consent_manager import (
    ConsentManager,
    ConsentManagerConfig,
    ConsentRecord,
    ConsentPurpose,
    ConsentStatus,
    LegalBasis,
    ConsentError,
    ConsentNotFoundError,
    ConsentExpiredError,
    ConsentDeniedError,
    ConsentStoreInterface,
    InMemoryConsentStore,
    ConsentModel,
    ConsentHistoryModel,
    get_consent_manager,
    init_consent_manager,
    require_consent,
)

from .data_erasure import (
    DataErasureManager,
    DataDiscoveryService,
    ErasureExecutor,
    ErasureRequest,
    ErasureResult,
    ErasureStatus,
    ErasureMethod,
    RetentionReason,
    DataLocation,
    ErasureError,
    ErasureBlockedError,
    ErasureNotFoundError,
    DataMapRegistry,
    DataMapEntry,
    ErasureRequestModel,
    get_data_map,
    register_data_table,
    get_erasure_manager,
    init_erasure_manager,
    init_default_data_map,
)

from .privacy_impact import (
    PIAManager,
    PrivacyImpactAssessment,
    DataProcessingActivity,
    RiskAssessment,
    MitigationMeasure,
    RiskLevel,
    RiskCategory,
    ProcessingType,
    AssessmentStatus,
    PIAError,
    PIATemplate,
    PIAModel,
    get_pia_manager,
    init_pia_manager,
    requires_dpia,
)

__all__ = [
    # Consent Manager
    "ConsentManager",
    "ConsentManagerConfig",
    "ConsentRecord",
    "ConsentPurpose",
    "ConsentStatus",
    "LegalBasis",
    "ConsentError",
    "ConsentNotFoundError",
    "ConsentExpiredError",
    "ConsentDeniedError",
    "ConsentStoreInterface",
    "InMemoryConsentStore",
    "ConsentModel",
    "ConsentHistoryModel",
    "get_consent_manager",
    "init_consent_manager",
    "require_consent",
    # Data Erasure
    "DataErasureManager",
    "DataDiscoveryService",
    "ErasureExecutor",
    "ErasureRequest",
    "ErasureResult",
    "ErasureStatus",
    "ErasureMethod",
    "RetentionReason",
    "DataLocation",
    "ErasureError",
    "ErasureBlockedError",
    "ErasureNotFoundError",
    "DataMapRegistry",
    "DataMapEntry",
    "ErasureRequestModel",
    "get_data_map",
    "register_data_table",
    "get_erasure_manager",
    "init_erasure_manager",
    "init_default_data_map",
    # Privacy Impact Assessment
    "PIAManager",
    "PrivacyImpactAssessment",
    "DataProcessingActivity",
    "RiskAssessment",
    "MitigationMeasure",
    "RiskLevel",
    "RiskCategory",
    "ProcessingType",
    "AssessmentStatus",
    "PIAError",
    "PIATemplate",
    "PIAModel",
    "get_pia_manager",
    "init_pia_manager",
    "requires_dpia",
]

__version__ = "1.0.0"
__author__ = "Conecta PRO Team"
