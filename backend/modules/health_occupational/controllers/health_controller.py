"""
Controller Health - Status e Health Check do Modulo
====================================================

Endpoints para verificacao de status do modulo Saude Ocupacional.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, status

from core.auth.dependencies import CurrentActiveUser
from modules.health_occupational.schemas.common import StandardResponse

router = APIRouter(tags=["Health - Status do Modulo"])


@router.get(
    "/status",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Status do modulo Saude Ocupacional",
    description="Retorna status de todos os componentes.",
)
async def get_health_status(current_user: CurrentActiveUser) -> StandardResponse:
    """
    Retorna status do modulo de saude ocupacional.

    Returns:
        StandardResponse: Status dos componentes.
    """
    return StandardResponse(
        success=True,
        message="Modulo Saude Ocupacional operacional",
        data={
            "module": "Health Occupational",
            "version": "2.0.0",
            "status": "operational",
            "architecture": "modular",
            "components": {
                "pcmso": {
                    "status": "active",
                    "description": "Exames Medicos Ocupacionais e ASO",
                    "compliance": "NR-7",
                },
                "ppra_pgr": {
                    "status": "active",
                    "description": "Mapeamento de Riscos Ocupacionais",
                    "compliance": "NR-9",
                },
                "epi_management": {
                    "status": "active",
                    "description": "Gestao de Equipamentos de Protecao",
                    "compliance": "NR-6",
                },
            },
            "compliance": {
                "nr4": "SESMT - Servicos Especializados em Engenharia de Seguranca e Medicina do Trabalho",
                "nr6": "EPI - Equipamento de Protecao Individual",
                "nr7": "PCMSO - Programa de Controle Medico de Saude Ocupacional",
                "nr9": "PPRA/PGR - Programa de Prevencao de Riscos Ambientais",
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
async def health_check(current_user: CurrentActiveUser) -> dict[str, Any]:
    """
    Health check do modulo.

    Returns:
        Dict com status de saude.
    """
    return {
        "status": "healthy",
        "module": "health_occupational",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get(
    "/info",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Informacoes do modulo",
)
async def get_module_info(current_user: CurrentActiveUser) -> dict[str, Any]:
    """
    Retorna informacoes detalhadas do modulo.

    Returns:
        Dict com informacoes do modulo.
    """
    return {
        "name": "Health Occupational",
        "version": "2.0.0",
        "description": "Modulo de Saude Ocupacional do Conecta PRO",
        "author": "Conecta PRO Team",
        "compliance": ["NR-4", "NR-6", "NR-7", "NR-9"],
        "features": [
            "Agendamento de exames medicos ocupacionais",
            "Emissao de ASO (Atestado de Saude Ocupacional)",
            "Controle de vencimentos de ASO",
            "Mapeamento de riscos ocupacionais (PPRA/PGR)",
            "Calculo de nivel de risco por setor/funcao",
            "Cadastro e gestao de EPIs",
            "Controle de entregas de EPI (Ficha de EPI)",
            "Gestao de estoque de EPIs",
            "Recomendacao automatica de EPIs por risco",
        ],
        "endpoints": {
            "pcmso": "/api/v1/health-occupational/pcmso",
            "ppra": "/api/v1/health-occupational/ppra",
            "epi": "/api/v1/health-occupational/epi",
        },
    }
