"""
Controller para status e health check das integrações governamentais.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, status

from core.config.credentials import (
    get_government_credentials,
    is_certificate_configured,
)

from ..schemas.common import StandardResponse

router = APIRouter(tags=["Status"])


@router.get(
    "/status",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Status das integracoes governamentais",
    description="Retorna status de todas as integracoes.",
)
async def get_government_status() -> StandardResponse:
    """
    Retorna status das integrações governamentais.

    Returns:
        StandardResponse: Status dos serviços.
    """
    # Verifica credenciais
    creds = get_government_credentials()
    cert_configured = is_certificate_configured()
    cert_path = creds.certificate.path

    return StandardResponse(
        success=True,
        message="Integracoes governamentais operacionais",
        data={
            "module": "Government Integrations",
            "version": "1.0.0",
            "status": "operational",
            "credentials": {
                "certificate": {
                    "configured": cert_configured,
                    "path": cert_path if cert_configured else None,
                    "status": "ready" if cert_configured else "not_configured",
                },
                "govbr": {
                    "configured": creds.govbr.is_configured,
                    "status": "ready" if creds.govbr.is_configured else "not_configured",
                },
            },
            "services": {
                "receita_federal": {
                    "status": "active",
                    "endpoints": ["consulta_cpf", "consulta_cnpj", "certidoes"],
                },
                "esocial": {
                    "status": "active" if cert_configured else "awaiting_certificate",
                    "eventos": ["S-2200", "S-2299", "S-2220"],
                    "ambiente": "producao" if creds.esocial_environment == "1" else "homologacao",
                },
                "sefaz": {
                    "status": "active" if cert_configured else "awaiting_certificate",
                    "layout": "4.00",
                    "documentos": ["NFe", "NFCe"],
                    "ambiente": "producao" if creds.sefaz_environment == "1" else "homologacao",
                },
                "fgts_inss": {
                    "status": "active",
                    "tabela_inss": "2026",
                    "aliquota_fgts": "8%",
                },
            },
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
async def health_check() -> dict[str, Any]:
    """
    Health check do módulo.

    Returns:
        Dict com status de saúde.
    """
    return {
        "status": "healthy",
        "module": "government_integrations",
        "timestamp": datetime.utcnow().isoformat(),
    }
