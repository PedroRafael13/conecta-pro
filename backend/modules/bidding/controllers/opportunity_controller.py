"""
Controller de Oportunidades — Licitacoes
=========================================
Endpoints para gerenciamento de oportunidades de licitacao
detectadas pelo agente Scout e consolidadas de multiplos portais.
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status

from modules.bidding.agents.scout_agent import ScoutAgent, ScoutSearchParams
from modules.bidding.schemas.opportunity import ScoutRequest
from modules.bidding.services.opportunity_service import OpportunityFilters, OpportunityService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/opportunities", tags=["Licitacoes - Oportunidades"])

# Instanciar service e agente
opportunity_service = OpportunityService()
scout_agent = ScoutAgent()


@router.get("")
async def list_opportunities(
    portal: str | None = Query(None, description="Filtrar por portal (pncp, comprasnet, bll, etc.)"),
    uf: str | None = Query(None, description="Filtrar por UF"),
    modalidade: str | None = Query(None, description="Filtrar por modalidade"),
    valor_minimo: float | None = Query(None, description="Valor minimo estimado"),
    valor_maximo: float | None = Query(None, description="Valor maximo estimado"),
    status_filter: str | None = Query(None, alias="status", description="Filtrar por status"),
    segmento: str | None = Query(None, description="Filtrar por segmento"),
    page: int = Query(1, ge=1, description="Pagina"),
    size: int = Query(20, ge=1, le=100, description="Itens por pagina"),
) -> dict[str, Any]:
    """Lista oportunidades de licitacao com filtros."""
    try:
        filters = OpportunityFilters(
            portal=portal,
            uf=uf,
            modalidade=modalidade,
            valor_minimo=valor_minimo,
            valor_maximo=valor_maximo,
            status=status_filter,
            segmento=segmento,
            page=page,
            size=size,
        )
        opportunities = await opportunity_service.list_opportunities(filters)
        return {
            "items": opportunities,
            "total": len(opportunities),
            "page": page,
            "size": size,
        }
    except Exception as e:
        logger.error("Erro ao listar oportunidades: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar oportunidades: {str(e)}",
        )


@router.get("/statistics")
async def get_statistics() -> dict[str, Any]:
    """Retorna estatisticas das oportunidades."""
    try:
        stats = await opportunity_service.get_statistics()
        return {
            "status": "success",
            "statistics": stats,
        }
    except Exception as e:
        logger.error("Erro ao obter estatisticas: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter estatisticas: {str(e)}",
        )


@router.get("/{opportunity_id}")
async def get_opportunity(opportunity_id: str) -> dict[str, Any]:
    """Busca oportunidade por ID."""
    try:
        opportunity = await opportunity_service.get_opportunity(opportunity_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Oportunidade nao encontrada: {opportunity_id}",
            )
        return opportunity
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao buscar oportunidade %s: %s", opportunity_id, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar oportunidade: {str(e)}",
        )


@router.post("/search")
async def search_opportunities(request: ScoutRequest) -> dict[str, Any]:
    """
    Busca oportunidades nos portais via agente Scout.

    Dispara busca em tempo real nos portais configurados e
    retorna oportunidades encontradas.
    """
    try:
        search_params = ScoutSearchParams(
            keywords=request.keywords or ["vigilancia", "seguranca patrimonial", "portaria"],
            ufs=[request.uf] if request.uf else ["AM"],
            modalidades=[request.modalidade] if request.modalidade else None,
            valor_minimo=request.valor_min,
            valor_maximo=request.valor_max,
            portais=(
                request.portais
                if hasattr(request, "portais") and request.portais
                else ["pncp", "comprasnet", "licitacoes_e", "ecompras_am"]
            ),
        )

        result = await scout_agent.run(search_params=search_params)
        if not result.success:
            return {
                "status": "error",
                "message": result.error or "Erro na busca",
                "opportunities": [],
                "total": 0,
            }

        opportunities = result.data if isinstance(result.data, list) else result.data.get("opportunities", [])

        # Salvar oportunidades encontradas no service
        saved = []
        for opp_data in opportunities:
            saved_opp = await opportunity_service.create_from_scout(opp_data)
            saved.append(saved_opp)

        return {
            "status": "success",
            "opportunities": saved,
            "total": len(saved),
            "portais_consultados": search_params.portais or [],
        }

    except Exception as e:
        logger.error("Erro na busca de oportunidades: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na busca de oportunidades: {str(e)}",
        )
