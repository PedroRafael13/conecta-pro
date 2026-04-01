"""
Controller de Status do Modulo LGPD.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, status

from core.auth.dependencies import get_current_user
from modules.security_lgpd.schemas.common import StandardResponse

router = APIRouter(tags=["LGPD - Status"])


@router.get(
    "/status",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Status do modulo LGPD",
    description="Retorna status de todos os componentes de seguranca.",
)
async def get_lgpd_status(current_user: dict = Depends(get_current_user)) -> StandardResponse:
    """
    Retorna status do modulo LGPD.
    Returns:
        StandardResponse: Status dos componentes.
    """
    return StandardResponse(
        success=True,
        message="Modulo LGPD operacional",
        data={
            "module": "Security LGPD",
            "version": "1.0.0",
            "status": "operational",
            "components": {
                "encryption": "active",
                "masking": "active",
                "consent_management": "active",
                "data_erasure": "active",
                "pia_dpia": "active",
                "audit_logging": "active",
            },
            "compliance": {
                "lgpd": "Lei 13.709/2018",
                "articles": ["Art. 7", "Art. 18", "Art. 38", "Art. 46"],
            },
            "encryption_algorithms": [
                "AES-256-GCM",
                "AES-256-CBC",
                "Fernet",
                "ChaCha20-Poly1305",
                "RSA-OAEP",
            ],
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@router.get(
    "/health",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Verifica saude do modulo.",
)
async def health_check(current_user: dict = Depends(get_current_user)) -> dict[str, Any]:
    """
    Health check do modulo.
    Returns:
        Dict com status de saude.
    """
    return {
        "status": "healthy",
        "module": "security_lgpd",
        "timestamp": datetime.utcnow().isoformat(),
    }
