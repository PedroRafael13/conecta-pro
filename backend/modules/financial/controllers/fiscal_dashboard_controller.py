"""Dashboard Fiscal-Financeiro — Conecta PRO"""

from datetime import datetime

from fastapi import APIRouter, HTTPException

from core.auth.dependencies import CurrentActiveUser

router = APIRouter(prefix="/fiscal-dashboard", tags=["Dashboard Fiscal"])


@router.get("/{mes}/{ano}", summary="Dashboard fiscal-financeiro completo")
async def get_dashboard(mes: int, ano: int, _: CurrentActiveUser):
    """
    Retorna dashboard integrado: DRE + notas + fluxo + estoque.
    Base para declaração Lucro Real / Receita Federal.
    """
    from modules.financial.services.fiscal_dashboard_service import get_dashboard_fiscal

    try:
        return get_dashboard_fiscal(mes, ano)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/atual", summary="Dashboard do mês atual")
async def get_dashboard_atual(_: CurrentActiveUser):
    from modules.financial.services.fiscal_dashboard_service import get_dashboard_fiscal

    now = datetime.now()
    try:
        return get_dashboard_fiscal(now.month, now.year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
