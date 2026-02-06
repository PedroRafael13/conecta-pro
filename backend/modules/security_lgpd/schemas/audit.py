"""
Schemas de auditoria do modulo de seguranca LGPD.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AuditLogRequest(BaseModel):
    """Request para registro de auditoria.

    Attributes:
        action: Acao executada.
        resource_type: Tipo de recurso afetado.
        resource_id: ID do recurso.
        user_id: ID do usuario executor.
        details: Detalhes adicionais.
        severity: Severidade do evento.
    """

    action: str = Field(
        ...,
        description="Acao executada",
        pattern=r"^(create|read|update|delete|export|consent|login|logout|encrypt|decrypt|mask|erasure)$",
    )
    resource_type: str = Field(
        ...,
        description="Tipo de recurso",
        pattern=r"^(user|document|consent|data|system|audit)$",
    )
    resource_id: str = Field(..., description="ID do recurso")
    user_id: str = Field(..., description="ID do usuario")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Detalhes adicionais",
    )
    severity: str = Field(
        default="info",
        description="Severidade",
        pattern=r"^(debug|info|warning|error|critical)$",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "action": "read",
                "resource_type": "document",
                "resource_id": "doc-123",
                "user_id": "user-456",
                "details": {"ip": "192.168.1.1"},
                "severity": "info",
            }
        }
    }


class AuditLogResponse(BaseModel):
    """Response de registro de auditoria."""

    log_id: str = Field(..., description="ID do log")
    action: str = Field(..., description="Acao executada")
    resource_type: str = Field(..., description="Tipo de recurso")
    timestamp: datetime = Field(..., description="Timestamp do evento")


class AuditLogListResponse(BaseModel):
    """Response com lista de logs de auditoria."""

    logs: List[Dict[str, Any]] = Field(..., description="Lista de logs")
    total: int = Field(..., description="Total de logs")
    limit: int = Field(..., description="Limite aplicado")
    offset: int = Field(..., description="Offset aplicado")
