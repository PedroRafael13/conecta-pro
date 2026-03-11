"""
DominioController — Endpoints para exportação Domínio TOTVS
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from ..agents.dominio_exporter import DominioExporterAgent

router = APIRouter(prefix="/empresas/dominio", tags=["Domínio TOTVS"])
agent = DominioExporterAgent()


class ExportarLancamentosRequest(BaseModel):
    empresa_slug: str
    periodo: str  # "YYYY-MM"
    lancamentos: list[dict] = []


class ExportarClientesRequest(BaseModel):
    empresa_slug: str
    clientes: list[dict] = []


class ExportarNfseRequest(BaseModel):
    empresa_slug: str
    periodo: str
    notas: list[dict] = []


@router.get("/plano-contas/{empresa_slug}")
def exportar_plano_contas(empresa_slug: str):
    return agent.gerar_plano_contas(empresa_slug)


@router.post("/lancamentos")
def exportar_lancamentos(req: ExportarLancamentosRequest):
    return agent.exportar_lancamentos(req.empresa_slug, req.periodo, req.lancamentos)


@router.post("/clientes")
def exportar_clientes(req: ExportarClientesRequest):
    return agent.exportar_clientes(req.empresa_slug, req.clientes)


@router.post("/nfse")
def exportar_nfse(req: ExportarNfseRequest):
    return agent.exportar_nfse_para_dominio(req.empresa_slug, req.periodo, req.notas)


@router.get("/download/plano-contas/{empresa_slug}", response_class=PlainTextResponse)
def download_plano_contas(empresa_slug: str):
    resultado = agent.gerar_plano_contas(empresa_slug)
    if not resultado.get("sucesso"):
        raise HTTPException(status_code=500, detail=resultado.get("erro"))
    return PlainTextResponse(
        content=resultado["conteudo"],
        headers={"Content-Disposition": f"attachment; filename={resultado['nome_arquivo']}"},
    )
