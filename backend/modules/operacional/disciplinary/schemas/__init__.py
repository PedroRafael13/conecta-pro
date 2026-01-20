"""
Schemas Pydantic do modulo de Medidas Administrativas.
"""

from .disciplinary_schemas import (
    # Enums
    DisciplinaryActionType,
    DisciplinaryActionStatus,
    ReasonCategory,
    SignerType,
    # DisciplinaryAction
    DisciplinaryActionBase,
    DisciplinaryActionCreate,
    DisciplinaryActionUpdate,
    DisciplinaryActionResponse,
    DisciplinaryActionListResponse,
    DisciplinaryActionDetailResponse,
    DisciplinaryFilter,
    DisciplinaryStats,
    # Workflow
    SubmitForApprovalRequest,
    ApproveRequest,
    RejectRequest,
    SignRequest,
    RefuseSignRequest,
    GenerateDocumentRequest,
    GenerateDocumentResponse,
    # Template
    TemplateBase,
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateListResponse,
    # Signature
    SignatureBase,
    SignatureCreate,
    SignatureResponse,
    SignatureVerifyRequest,
    SignatureVerifyResponse,
    # AI Advisor
    RecommendationRequest,
    RecommendationResponse,
    LegalComplianceRequest,
    LegalComplianceResponse,
    ProportionalityCheckRequest,
    ProportionalityCheckResponse,
)

__all__ = [
    # Enums
    "DisciplinaryActionType",
    "DisciplinaryActionStatus",
    "ReasonCategory",
    "SignerType",
    # DisciplinaryAction
    "DisciplinaryActionBase",
    "DisciplinaryActionCreate",
    "DisciplinaryActionUpdate",
    "DisciplinaryActionResponse",
    "DisciplinaryActionListResponse",
    "DisciplinaryActionDetailResponse",
    "DisciplinaryFilter",
    "DisciplinaryStats",
    # Workflow
    "SubmitForApprovalRequest",
    "ApproveRequest",
    "RejectRequest",
    "SignRequest",
    "RefuseSignRequest",
    "GenerateDocumentRequest",
    "GenerateDocumentResponse",
    # Template
    "TemplateBase",
    "TemplateCreate",
    "TemplateUpdate",
    "TemplateResponse",
    "TemplateListResponse",
    # Signature
    "SignatureBase",
    "SignatureCreate",
    "SignatureResponse",
    "SignatureVerifyRequest",
    "SignatureVerifyResponse",
    # AI Advisor
    "RecommendationRequest",
    "RecommendationResponse",
    "LegalComplianceRequest",
    "LegalComplianceResponse",
    "ProportionalityCheckRequest",
    "ProportionalityCheckResponse",
]
