"""
StatementsController — DRE, Balanço Patrimonial e DFC
"""

from fastapi import APIRouter
from pydantic import BaseModel

from core.auth.dependencies import CurrentActiveUser

from ..agents.financial_statements import FinancialStatementsAgent

router = APIRouter(prefix="/empresas/demonstrativos", tags=["Demonstrativos Financeiros"])
agent = FinancialStatementsAgent()


class DRERequest(BaseModel):
    empresa_slug: str
    periodo: str
    dados: dict
    regime: str = "lucro_real"


class BalancoRequest(BaseModel):
    empresa_slug: str
    data_base: str
    dados: dict


class DFCRequest(BaseModel):
    empresa_slug: str
    periodo: str
    dados: dict


class ConsolidadoRequest(BaseModel):
    periodo: str
    empresas: list[dict]


@router.post("/dre")
def gerar_dre(current_user: CurrentActiveUser, req: DRERequest):
    return agent.gerar_dre(req.empresa_slug, req.periodo, req.dados, req.regime)


@router.post("/balanco")
def gerar_balanco(current_user: CurrentActiveUser, req: BalancoRequest):
    return agent.gerar_balanco_sintetico(req.empresa_slug, req.data_base, req.dados)


@router.post("/dfc")
def gerar_dfc(current_user: CurrentActiveUser, req: DFCRequest):
    return agent.gerar_dfc_indireto(req.empresa_slug, req.periodo, req.dados)


@router.post("/consolidado-grupo")
def consolidado_grupo(current_user: CurrentActiveUser, req: ConsolidadoRequest):
    return agent.gerar_consolidado_grupo(req.periodo, req.empresas)
