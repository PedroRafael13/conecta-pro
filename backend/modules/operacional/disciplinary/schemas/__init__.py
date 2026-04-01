"""
Schemas Pydantic do modulo de Medidas Administrativas.
"""

from .disciplinary_schemas import (
    ApproveRequest,
    # DisciplinaryAction
    DisciplinaryActionBase,
    DisciplinaryActionCreate,
    DisciplinaryActionDetailResponse,
    DisciplinaryActionListResponse,
    DisciplinaryActionResponse,
    DisciplinaryActionStatus,
    # Enums
    DisciplinaryActionType,
    DisciplinaryActionUpdate,
    DisciplinaryFilter,
    DisciplinaryStats,
    GenerateDocumentRequest,
    GenerateDocumentResponse,
    LegalComplianceRequest,
    LegalComplianceResponse,
    ProportionalityCheckRequest,
    ProportionalityCheckResponse,
    ReasonCategory,
    # AI Advisor
    RecommendationRequest,
    RecommendationResponse,
    RefuseSignRequest,
    RejectRequest,
    # Signature
    SignatureBase,
    SignatureCreate,
    SignatureResponse,
    SignatureVerifyRequest,
    SignatureVerifyResponse,
    SignerType,
    SignRequest,
    # Workflow
    SubmitForApprovalRequest,
    # Template
    TemplateBase,
    TemplateCreate,
    TemplateListResponse,
    TemplateResponse,
    TemplateUpdate,
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
