"""
Schemas Pydantic para compliance LGPD.

Modelos para requisições e respostas dos endpoints de proteção de dados.
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class DataRequestType(StrEnum):
    """Tipos de solicitação de dados LGPD."""

    ACCESS = "access"
    PORTABILITY = "portability"
    DELETION = "deletion"
    RECTIFICATION = "rectification"
    RESTRICTION = "restriction"


class DataRequestStatus(StrEnum):
    """Status da solicitação de dados."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class DataRequestCreate(BaseModel):
    """Schema para criar solicitação de dados."""

    request_type: DataRequestType = Field(..., description="Tipo de solicitação")
    description: str | None = Field(None, max_length=500, description="Descrição adicional da solicitação")

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Any, info) -> Any:
        """Valida descrição baseada no tipo de solicitação."""
        values = info.data
        request_type = values.get("request_type")

        # Descrição obrigatória para exclusão
        if request_type == DataRequestType.DELETION and not v:
            raise ValueError("Descrição obrigatória para solicitações de exclusão")

        return v

    class Config:
        """Pydantic config."""

        schema_extra = {
            "example": {"request_type": "access", "description": "Gostaria de acessar todos os meus dados pessoais"}
        }


class DataRequestResponse(BaseModel):
    """Schema de resposta para solicitação de dados."""

    success: bool
    message: str
    request_id: str | None = None
    request_type: str | None = None
    status: str | None = None
    created_at: str | None = None
    estimated_completion: str | None = None
    completion_date: str | None = None
    result_data: dict[str, Any] | None = None

    class Config:
        """Pydantic config."""

        schema_extra = {
            "example": {
                "success": True,
                "message": "Solicitação criada com sucesso",
                "request_id": "123e4567-e89b-12d3-a456-426614174000",
                "request_type": "access",
                "status": "pending",
                "estimated_completion": "2026-02-10T10:00:00Z",
            }
        }


class DataExportResponse(BaseModel):
    """Schema de resposta para exportação de dados."""

    success: bool
    message: str
    data: dict[str, Any] | None = None
    export_format: str = Field(default="json")
    export_date: str | None = None

    class Config:
        """Pydantic config."""

        schema_extra = {
            "example": {
                "success": True,
                "message": "Dados exportados com sucesso",
                "export_format": "json",
                "export_date": "2026-02-03T10:00:00Z",
                "data": {
                    "user_id": 123,
                    "data_categories": {
                        "basic_profile": {"name": "João", "email": "joao@example.com"},
                        "notification_preferences": [],
                        "notification_history": {"total_notifications": 50},
                        "registered_devices": [],
                    },
                },
            }
        }


class ConsentUpdateRequest(BaseModel):
    """Schema para atualizar consentimentos."""

    consent_type: str = Field(..., description="Tipo de consentimento (marketing, analytics, etc.)")
    granted: bool = Field(..., description="Se o consentimento foi concedido")
    purpose: str | None = Field(None, max_length=200, description="Finalidade específica do consentimento")

    class Config:
        """Pydantic config."""

        schema_extra = {
            "example": {
                "consent_type": "marketing",
                "granted": True,
                "purpose": "Recebimento de newsletters e promoções",
            }
        }


class ConsentResponse(BaseModel):
    """Schema de resposta para consentimentos."""

    success: bool
    message: str
    consent_id: str | None = None
    consent_type: str | None = None
    status: str | None = None
    granted_at: str | None = None
    expires_at: str | None = None

    class Config:
        """Pydantic config."""

        schema_extra = {
            "example": {
                "success": True,
                "message": "Consentimento atualizado com sucesso",
                "consent_id": "123e4567-e89b-12d3-a456-426614174000",
                "consent_type": "marketing",
                "status": "granted",
                "granted_at": "2026-02-03T10:00:00Z",
            }
        }


class PrivacySettingsResponse(BaseModel):
    """Schema para configurações de privacidade."""

    user_id: int
    notification_preferences: dict[str, Any]
    consent_records: list[dict[str, Any]]
    data_retention_policy: str
    last_updated: str | None = None

    class Config:
        """Pydantic config."""

        schema_extra = {
            "example": {
                "user_id": 123,
                "notification_preferences": {"marketing": True, "system": True, "newsletter": False},
                "consent_records": [{"type": "marketing", "granted": True, "date": "2026-02-03T10:00:00Z"}],
                "data_retention_policy": "Dados mantidos por 5 anos após inatividade da conta",
                "last_updated": "2026-02-03T10:00:00Z",
            }
        }


class AuditLogResponse(BaseModel):
    """Schema para logs de auditoria LGPD."""

    logs: list[dict[str, Any]]
    total_count: int
    page: int
    page_size: int

    class Config:
        """Pydantic config."""

        schema_extra = {
            "example": {
                "logs": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "timestamp": "2026-02-03T10:00:00Z",
                        "action": "data_export",
                        "user_id": 123,
                        "resource_type": "user_data",
                        "ip_address": "192.168.1.1",
                        "user_agent": "Mozilla/5.0...",
                        "success": True,
                    }
                ],
                "total_count": 1,
                "page": 1,
                "page_size": 50,
            }
        }


class DataDeletionConfirmation(BaseModel):
    """Schema para confirmação de exclusão de dados."""

    confirmation: str = Field(..., description="Confirmação exata: 'DELETE_MY_DATA'")
    reason: str | None = Field(None, max_length=200, description="Motivo da exclusão (opcional)")

    @field_validator("confirmation")
    @classmethod
    def validate_confirmation(cls, v):
        """Valida confirmação de exclusão."""
        if v != "DELETE_MY_DATA":
            raise ValueError("Confirmação deve ser exatamente 'DELETE_MY_DATA'")
        return v

    class Config:
        """Pydantic config."""

        schema_extra = {"example": {"confirmation": "DELETE_MY_DATA", "reason": "Não utilizo mais o serviço"}}
