"""Signature Recognition Schemas."""

from modules.ai.signature.schemas.signature_schemas import (
    # Request Schemas
    SignatureUploadRequest,
    SignatureExtractRequest,
    SignatureCompareRequest,
    SignatureValidateRequest,
    TemplateCreateRequest,
    TemplateAddSampleRequest,
    SignatureRequestCreate,
    SignatureSubmitRequest,
    # Response Schemas
    BoundingBoxResponse,
    ExtractedSignatureResponse,
    ExtractionResultResponse,
    FeatureScoreResponse,
    ComparisonResultResponse,
    QualityCheckResponse,
    FraudAnalysisResponse,
    ValidationResultResponse,
    SignatureResponse,
    TemplateResponse,
    VerificationResponse,
    SignatureRequestResponse,
    SignedDocumentResponse,
    SignatureStatsResponse,
    # List Responses
    SignatureListResponse,
    TemplateListResponse,
    RequestListResponse,
)

__all__ = [
    # Request Schemas
    "SignatureUploadRequest",
    "SignatureExtractRequest",
    "SignatureCompareRequest",
    "SignatureValidateRequest",
    "TemplateCreateRequest",
    "TemplateAddSampleRequest",
    "SignatureRequestCreate",
    "SignatureSubmitRequest",
    # Response Schemas
    "BoundingBoxResponse",
    "ExtractedSignatureResponse",
    "ExtractionResultResponse",
    "FeatureScoreResponse",
    "ComparisonResultResponse",
    "QualityCheckResponse",
    "FraudAnalysisResponse",
    "ValidationResultResponse",
    "SignatureResponse",
    "TemplateResponse",
    "VerificationResponse",
    "SignatureRequestResponse",
    "SignedDocumentResponse",
    "SignatureStatsResponse",
    # List Responses
    "SignatureListResponse",
    "TemplateListResponse",
    "RequestListResponse",
]
