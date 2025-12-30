"""Schemas Pydantic para DocumentSignature."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, EmailStr

from modules.ged.models.document_signature import (
    SignatureType,
    SignatureStatus,
    SignatureRole,
)


class DocumentSignatureBase(BaseModel):
    """Schema base de DocumentSignature."""

    signer_name: str = Field(..., min_length=1, max_length=255)
    signer_email: EmailStr
    signer_document: Optional[str] = Field(None, max_length=20)
    signer_phone: Optional[str] = Field(None, max_length=20)
    signer_role: SignatureRole = Field(default=SignatureRole.PARTE)
    signature_type: SignatureType = Field(default=SignatureType.ELETRONICA)
    order: int = Field(default=1, ge=1)
    is_sequential: bool = False
    deadline: Optional[datetime] = None
    metadata: Optional[dict] = None


class DocumentSignatureCreate(DocumentSignatureBase):
    """Schema para criar DocumentSignature."""

    document_id: str
    signer_id: Optional[str] = None
    created_by: str
    page_number: Optional[int] = Field(None, ge=1)
    position_x: Optional[int] = Field(None, ge=0)
    position_y: Optional[int] = Field(None, ge=0)
    width: Optional[int] = Field(None, ge=50)
    height: Optional[int] = Field(None, ge=20)


class DocumentSignatureUpdate(BaseModel):
    """Schema para atualizar DocumentSignature."""

    signer_name: Optional[str] = Field(None, min_length=1, max_length=255)
    signer_phone: Optional[str] = Field(None, max_length=20)
    signer_role: Optional[SignatureRole] = None
    order: Optional[int] = Field(None, ge=1)
    is_sequential: Optional[bool] = None
    deadline: Optional[datetime] = None
    page_number: Optional[int] = Field(None, ge=1)
    position_x: Optional[int] = Field(None, ge=0)
    position_y: Optional[int] = Field(None, ge=0)


class DocumentSignatureResponse(BaseModel):
    """Schema de resposta de DocumentSignature."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    signer_id: Optional[str]
    signer_name: str
    signer_email: str
    signer_document: Optional[str]
    signer_phone: Optional[str]
    signer_role: SignatureRole
    signature_type: SignatureType
    status: SignatureStatus
    order: int
    is_sequential: bool
    signature_token: Optional[str]
    token_expires_at: Optional[datetime]
    signature_hash: Optional[str]
    certificate_data: Optional[dict]
    page_number: Optional[int]
    position_x: Optional[int]
    position_y: Optional[int]
    width: Optional[int]
    height: Optional[int]
    ip_address: Optional[str]
    geolocation: Optional[dict]
    verification_code: Optional[str]
    is_verified: bool
    verified_at: Optional[datetime]
    verification_method: Optional[str]
    refusal_reason: Optional[str]
    notification_sent: bool
    notification_sent_at: Optional[datetime]
    reminder_count: int
    last_reminder_at: Optional[datetime]
    deadline: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    signed_at: Optional[datetime]
    refused_at: Optional[datetime]
    created_by: str

    # Computed
    is_pending: bool
    is_signed: bool
    is_refused: bool
    is_expired: bool
    is_token_valid: bool
    days_until_deadline: Optional[int]


class DocumentSignatureListResponse(BaseModel):
    """Schema de lista de DocumentSignatures."""

    items: List[DocumentSignatureResponse]
    total: int


class DocumentSignatureFilter(BaseModel):
    """Schema de filtro de DocumentSignatures."""

    document_id: Optional[str] = None
    signer_id: Optional[str] = None
    signer_email: Optional[str] = None
    signature_type: Optional[SignatureType] = None
    status: Optional[SignatureStatus] = None
    signer_role: Optional[SignatureRole] = None
    is_verified: Optional[bool] = None


class SignatureRequest(BaseModel):
    """Schema para assinar documento."""

    signature_data: str = Field(..., min_length=1)  # Base64 da assinatura
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    geolocation: Optional[dict] = None


class SignatureRefusalRequest(BaseModel):
    """Schema para recusar assinatura."""

    reason: str = Field(..., min_length=1, max_length=1000)


class SignatureVerifyRequest(BaseModel):
    """Schema para verificar assinatura."""

    token: str
    verification_code: Optional[str] = None


class SignatureBulkCreate(BaseModel):
    """Schema para criar múltiplas assinaturas."""

    document_id: str
    signers: List[DocumentSignatureCreate]
    send_notifications: bool = True


class SignatureReminderRequest(BaseModel):
    """Schema para enviar lembrete."""

    custom_message: Optional[str] = Field(None, max_length=500)


class SignatureStats(BaseModel):
    """Estatísticas de assinaturas."""

    total_signatures: int = 0
    pending: int = 0
    signed: int = 0
    refused: int = 0
    expired: int = 0
    by_type: dict = {}
    by_role: dict = {}
    avg_time_to_sign_hours: float = 0


class SignaturePositionRequest(BaseModel):
    """Schema para definir posição da assinatura."""

    page_number: int = Field(..., ge=1)
    position_x: int = Field(..., ge=0)
    position_y: int = Field(..., ge=0)
    width: int = Field(default=200, ge=50)
    height: int = Field(default=50, ge=20)
