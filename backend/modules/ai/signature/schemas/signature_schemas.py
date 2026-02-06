"""Signature Recognition Schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ============== Enums ==============

class SignatureTypeEnum(str):
    """Signature type enumeration."""

    HANDWRITTEN = "handwritten"
    DIGITAL = "digital"
    ELECTRONIC = "electronic"
    BIOMETRIC = "biometric"
    SCANNED = "scanned"
    DRAWN = "drawn"


class SignatureStatusEnum(str):
    """Signature status enumeration."""

    PENDING = "pending"
    EXTRACTED = "extracted"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REVOKED = "revoked"


# ============== Request Schemas ==============

class SignatureUploadRequest(BaseModel):
    """Request for uploading a signature."""

    owner_id: Optional[UUID] = None
    owner_type: Optional[str] = Field(None, max_length=50)
    owner_name: Optional[str] = Field(None, max_length=255)
    owner_document: Optional[str] = Field(None, max_length=50)
    signature_type: str = Field(default="handwritten")
    source: str = Field(default="upload")
    image_data: Optional[str] = Field(None, description="Base64 encoded image")
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class SignatureExtractRequest(BaseModel):
    """Request for extracting signatures from image."""

    image_data: str = Field(..., description="Base64 encoded image")
    region: Optional[Dict[str, int]] = Field(
        None, description="Region {x, y, width, height}"
    )
    method: str = Field(default="auto", description="auto, contour, edge, template")
    min_confidence: float = Field(default=0.5, ge=0, le=1)
    max_signatures: int = Field(default=10, ge=1, le=50)


class SignatureCompareRequest(BaseModel):
    """Request for comparing two signatures."""

    signature1_id: Optional[UUID] = None
    signature1_data: Optional[Dict[str, Any]] = None
    signature2_id: Optional[UUID] = None
    signature2_data: Optional[Dict[str, Any]] = None
    template_id: Optional[UUID] = None
    mode: str = Field(default="normal", description="strict, normal, relaxed")
    custom_threshold: Optional[float] = Field(None, ge=0, le=1)


class SignatureValidateRequest(BaseModel):
    """Request for validating a signature."""

    signature_id: Optional[UUID] = None
    signature_data: Optional[Dict[str, Any]] = None
    template_id: Optional[UUID] = None
    context: Optional[Dict[str, Any]] = Field(
        None, description="Validation context (purpose, document_type, etc.)"
    )
    strict_mode: bool = Field(default=False)


class TemplateCreateRequest(BaseModel):
    """Request for creating a signature template."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    code: Optional[str] = Field(None, max_length=50)
    owner_id: UUID
    owner_type: str = Field(..., max_length=50)
    owner_name: Optional[str] = Field(None, max_length=255)
    owner_document: Optional[str] = Field(None, max_length=50)
    template_type: str = Field(default="personal")
    matching_mode: str = Field(default="normal")
    similarity_threshold: float = Field(default=0.75, ge=0, le=1)
    min_samples_required: int = Field(default=3, ge=1, le=10)
    allowed_document_types: Optional[List[str]] = None
    allowed_purposes: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class TemplateAddSampleRequest(BaseModel):
    """Request for adding sample to template."""

    signature_id: Optional[UUID] = None
    image_data: Optional[str] = Field(None, description="Base64 encoded image")


class SignatureRequestCreate(BaseModel):
    """Request for creating a signature request."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: str = Field(default="normal")
    purpose: str = Field(default="approval")
    document_id: Optional[UUID] = None
    document_name: Optional[str] = Field(None, max_length=255)
    signer_id: Optional[UUID] = None
    signer_type: Optional[str] = Field(None, max_length=50)
    signer_name: str = Field(..., min_length=1, max_length=255)
    signer_email: Optional[str] = Field(None, max_length=255)
    signer_phone: Optional[str] = Field(None, max_length=20)
    template_id: Optional[UUID] = None
    signature_page: Optional[int] = None
    signature_position: Optional[Dict[str, int]] = None
    due_date: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    reminder_frequency: str = Field(default="none")
    requires_authentication: bool = Field(default=False)
    metadata: Optional[Dict[str, Any]] = None


class SignatureSubmitRequest(BaseModel):
    """Request for submitting a signature."""

    image_data: str = Field(..., description="Base64 encoded signature image")
    biometric_data: Optional[Dict[str, Any]] = None
    device_info: Optional[str] = None
    location: Optional[Dict[str, Any]] = None


# ============== Response Schemas ==============

class BoundingBoxResponse(BaseModel):
    """Bounding box response."""

    x: int
    y: int
    width: int
    height: int


class ExtractedSignatureResponse(BaseModel):
    """Extracted signature response."""

    id: str
    bounding_box: Optional[BoundingBoxResponse] = None
    confidence: float
    quality_score: float
    contrast_score: float
    clarity_score: float
    completeness_score: float
    width: int
    height: int
    stroke_count: int
    extraction_method: str
    has_image: bool
    has_features: bool


class ExtractionResultResponse(BaseModel):
    """Extraction result response."""

    success: bool
    signatures: List[ExtractedSignatureResponse]
    total_found: int
    processing_time_ms: int
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]


class FeatureScoreResponse(BaseModel):
    """Feature score response."""

    feature_name: str
    score: float
    weight: float
    weighted_score: float
    details: Dict[str, Any]


class ComparisonResultResponse(BaseModel):
    """Comparison result response."""

    is_match: bool
    similarity_score: float
    confidence: float
    threshold_used: float
    feature_scores: List[FeatureScoreResponse]
    method_used: str
    anomalies: List[str]
    warnings: List[str]
    processing_time_ms: int
    metadata: Dict[str, Any]


class QualityCheckResponse(BaseModel):
    """Quality check response."""

    passed: bool
    quality_score: float
    issues: List[str]
    recommendations: List[str]
    details: Dict[str, Any]


class FraudAnalysisResponse(BaseModel):
    """Fraud analysis response."""

    is_suspicious: bool
    risk_level: str
    fraud_indicators: List[str]
    confidence: float
    analysis_details: Dict[str, Any]


class ValidationResultResponse(BaseModel):
    """Validation result response."""

    id: str
    is_valid: bool
    is_authentic: bool
    overall_score: float
    confidence: float
    status: str
    quality_check: Optional[QualityCheckResponse] = None
    comparison_result: Optional[ComparisonResultResponse] = None
    fraud_analysis: Optional[FraudAnalysisResponse] = None
    errors: List[str]
    warnings: List[str]
    processing_time_ms: int


class SignatureResponse(BaseModel):
    """Signature response."""

    id: UUID
    tenant_id: UUID
    owner_id: Optional[UUID] = None
    owner_name: Optional[str] = None
    signature_type: Optional[str] = None
    signature_format: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None
    quality_score: Optional[float] = None
    is_verified: bool
    is_valid: bool
    width: Optional[int] = None
    height: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class TemplateResponse(BaseModel):
    """Template response."""

    id: UUID
    tenant_id: UUID
    name: str
    owner_id: UUID
    owner_name: Optional[str] = None
    template_type: Optional[str] = None
    status: Optional[str] = None
    matching_mode: Optional[str] = None
    sample_count: int
    min_samples_required: int
    similarity_threshold: float
    is_valid: bool
    has_enough_samples: bool
    success_rate: Optional[float] = None
    total_verifications: int
    created_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class VerificationResponse(BaseModel):
    """Verification response."""

    id: UUID
    tenant_id: UUID
    signature_id: UUID
    template_id: Optional[UUID] = None
    status: Optional[str] = None
    result: Optional[str] = None
    risk_level: Optional[str] = None
    method: Optional[str] = None
    overall_score: Optional[float] = None
    similarity_score: Optional[float] = None
    confidence: Optional[float] = None
    passed_threshold: Optional[bool] = None
    is_match: bool
    requires_manual_review: bool
    processing_time_ms: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class SignatureRequestResponse(BaseModel):
    """Signature request response."""

    id: UUID
    tenant_id: UUID
    title: str
    status: Optional[str] = None
    priority: Optional[str] = None
    purpose: Optional[str] = None
    signer_name: str
    signer_email: Optional[str] = None
    document_name: Optional[str] = None
    due_date: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_pending: bool
    is_signed: bool
    is_expired: bool
    is_overdue: bool
    signed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class SignedDocumentResponse(BaseModel):
    """Signed document response."""

    id: UUID
    tenant_id: UUID
    title: str
    reference_code: Optional[str] = None
    status: Optional[str] = None
    integrity_status: Optional[str] = None
    total_signatures_required: int
    total_signatures_collected: int
    signatures_remaining: int
    completion_percentage: float
    is_complete: bool
    is_valid: bool
    verification_code: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class SignatureStatsResponse(BaseModel):
    """Signature statistics response."""

    total_signatures: int
    verified_signatures: int
    pending_signatures: int
    rejected_signatures: int
    total_templates: int
    active_templates: int
    total_verifications: int
    successful_verifications: int
    failed_verifications: int
    average_match_score: Optional[float] = None
    pending_requests: int
    completed_requests: int
    signed_documents: int


# ============== List Response ==============

class SignatureListResponse(BaseModel):
    """Paginated signature list response."""

    items: List[SignatureResponse]
    total: int
    page: int
    size: int
    pages: int


class TemplateListResponse(BaseModel):
    """Paginated template list response."""

    items: List[TemplateResponse]
    total: int
    page: int
    size: int
    pages: int


class RequestListResponse(BaseModel):
    """Paginated request list response."""

    items: List[SignatureRequestResponse]
    total: int
    page: int
    size: int
    pages: int
