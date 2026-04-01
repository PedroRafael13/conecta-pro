"""Schemas Pydantic para DocumentSignature."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from modules.ged.models.document_signature import (
    SignatureRole,
    SignatureStatus,
    SignatureType,
)


class DocumentSignatureBase(BaseModel):
    """Schema base de DocumentSignature."""

    signer_name: str = Field(..., min_length=1, max_length=255)
    signer_email: EmailStr
    signer_document: str | None = Field(None, max_length=20)
    signer_phone: str | None = Field(None, max_length=20)
    signer_role: SignatureRole = Field(default=SignatureRole.PARTE)
    signature_type: SignatureType = Field(default=SignatureType.ELETRONICA)
    order: int = Field(default=1, ge=1)
    is_sequential: bool = False
    deadline: datetime | None = None
    metadata: dict | None = None


class DocumentSignatureCreate(DocumentSignatureBase):
    """Schema para criar DocumentSignature."""

    document_id: str
    signer_id: str | None = None
    created_by: str
    page_number: int | None = Field(None, ge=1)
    position_x: int | None = Field(None, ge=0)
    position_y: int | None = Field(None, ge=0)
    width: int | None = Field(None, ge=50)
    height: int | None = Field(None, ge=20)


class DocumentSignatureUpdate(BaseModel):
    """Schema para atualizar DocumentSignature."""

    signer_name: str | None = Field(None, min_length=1, max_length=255)
    signer_phone: str | None = Field(None, max_length=20)
    signer_role: SignatureRole | None = None
    order: int | None = Field(None, ge=1)
    is_sequential: bool | None = None
    deadline: datetime | None = None
    page_number: int | None = Field(None, ge=1)
    position_x: int | None = Field(None, ge=0)
    position_y: int | None = Field(None, ge=0)


class DocumentSignatureResponse(BaseModel):
    """Schema de resposta de DocumentSignature."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    signer_id: str | None
    signer_name: str
    signer_email: str
    signer_document: str | None
    signer_phone: str | None
    signer_role: SignatureRole
    signature_type: SignatureType
    status: SignatureStatus
    order: int
    is_sequential: bool
    signature_token: str | None
    token_expires_at: datetime | None
    signature_hash: str | None
    certificate_data: dict | None
    page_number: int | None
    position_x: int | None
    position_y: int | None
    width: int | None
    height: int | None
    ip_address: str | None
    geolocation: dict | None
    verification_code: str | None
    is_verified: bool
    verified_at: datetime | None
    verification_method: str | None
    refusal_reason: str | None
    notification_sent: bool
    notification_sent_at: datetime | None
    reminder_count: int
    last_reminder_at: datetime | None
    deadline: datetime | None
    created_at: datetime
    updated_at: datetime
    signed_at: datetime | None
    refused_at: datetime | None
    created_by: str

    # Computed
    is_pending: bool
    is_signed: bool
    is_refused: bool
    is_expired: bool
    is_token_valid: bool
    days_until_deadline: int | None


class DocumentSignatureListResponse(BaseModel):
    """Schema de lista de DocumentSignatures."""

    items: list[DocumentSignatureResponse]
    total: int


class DocumentSignatureFilter(BaseModel):
    """Schema de filtro de DocumentSignatures."""

    document_id: str | None = None
    signer_id: str | None = None
    signer_email: str | None = None
    signature_type: SignatureType | None = None
    status: SignatureStatus | None = None
    signer_role: SignatureRole | None = None
    is_verified: bool | None = None


class SignatureRequest(BaseModel):
    """Schema para assinar documento."""

    signature_data: str = Field(..., min_length=1)  # Base64 da assinatura
    ip_address: str | None = None
    user_agent: str | None = None
    geolocation: dict | None = None


class SignatureRefusalRequest(BaseModel):
    """Schema para recusar assinatura."""

    reason: str = Field(..., min_length=1, max_length=1000)


class SignatureVerifyRequest(BaseModel):
    """Schema para verificar assinatura."""

    token: str
    verification_code: str | None = None


class SignatureBulkCreate(BaseModel):
    """Schema para criar múltiplas assinaturas."""

    document_id: str
    signers: list[DocumentSignatureCreate]
    send_notifications: bool = True


class SignatureReminderRequest(BaseModel):
    """Schema para enviar lembrete."""

    custom_message: str | None = Field(None, max_length=500)


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
