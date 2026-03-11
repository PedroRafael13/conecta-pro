"""
BookkeeperController — Endpoints escrituração contábil automática
"""

from fastapi import APIRouter
from pydantic import BaseModel

from ..agents.bookkeeper_auto import BookkeeperAutoAgent

router = APIRouter(prefix="/empresas/contabilidade", tags=["Escrituração Contábil"])
agent = BookkeeperAutoAgent()


class LancamentosFolhaRequest(BaseModel):
    empresa_slug: str
    competencia: str
    funcionarios: list[dict] = []


class LancamentosImpostosRequest(BaseModel):
    empresa_slug: str
    competencia: str
    impostos: dict = {}
    regime: str = "lucro_real"


class ResumoContabilRequest(BaseModel):
    empresa_slug: str
    periodo: str
    receitas: float = 0
    custos_folha: float = 0
    impostos: float = 0
    despesas_admin: float = 0


@router.post("/lancamentos/folha")
def lancamentos_folha(req: LancamentosFolhaRequest):
    return agent.gerar_lancamentos_folha(req.empresa_slug, req.competencia, req.funcionarios)


@router.post("/lancamentos/impostos")
def lancamentos_impostos(req: LancamentosImpostosRequest):
    return agent.gerar_lancamentos_impostos(req.empresa_slug, req.competencia, req.impostos, req.regime)


@router.post("/resumo-mensal")
def resumo_mensal(req: ResumoContabilRequest):
    return agent.resumo_contabil_mensal(
        req.empresa_slug, req.periodo, req.receitas, req.custos_folha, req.impostos, req.despesas_admin
    )
