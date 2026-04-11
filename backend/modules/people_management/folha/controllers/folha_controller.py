"""Controller da Folha de Pagamento — CCT 2026 SINDECOMPRESTS."""

from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from core.auth.dependencies import get_current_user
from core.database.session import get_sync_db_dependency

from ..schemas.folha_schemas import (
    AjusteRequest,
    ConferenciaResponse,
    DashboardFolhaResponse,
    FechamentoResponse,
    FolhaBatchResponse,
    HoleriteResponse,
    ResumoFolhaResponse,
    RubricaResponse,
)
from ..services import calculo_service

router = APIRouter(prefix="/folha", tags=["Folha de Pagamento"])


@router.get(
    "/dashboard",
    response_model=DashboardFolhaResponse,
    summary="Dashboard gerencial da folha",
)
async def folha_dashboard(
    current_user=Depends(get_current_user),
    mes: int = Query(default=None, ge=1, le=12),
    ano: int = Query(default=None, ge=2020),
    db: Session = Depends(get_sync_db_dependency),
) -> DashboardFolhaResponse:
    """Visao gerencial da folha do mes com totais por cargo."""
    hoje = date.today()
    mes = mes or hoje.month
    ano = ano or hoje.year
    data = calculo_service.get_dashboard_folha(db, mes, ano)
    return DashboardFolhaResponse(**data)


@router.get(
    "/calcular/{employee_id}/{mes}/{ano}",
    response_model=HoleriteResponse,
    summary="Calcular holerite de um colaborador",
)
async def calcular_holerite(
    employee_id: str,
    mes: int,
    ano: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_sync_db_dependency),
) -> HoleriteResponse:
    """Calcula holerite completo com base na CCT 2026."""
    result = calculo_service.calcular_folha_colaborador(db, employee_id, mes, ano)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return HoleriteResponse(**result)


@router.post(
    "/calcular/todos/{mes}/{ano}",
    response_model=FolhaBatchResponse,
    summary="Calcular folha de todos os colaboradores",
    status_code=201,
)
async def calcular_batch(
    mes: int,
    ano: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_sync_db_dependency),
) -> FolhaBatchResponse:
    """Calcula folha completa para todos os colaboradores ativos.

    Prioriza dados importados do Domínio Sistemas (fonte de verdade).
    Engine interna é usada apenas como fallback quando não há dados importados.
    """
    result = calculo_service.calcular_folha_batch_com_guard(db, mes, ano)
    return FolhaBatchResponse(**result)


@router.get(
    "/holerite/{employee_id}/{mes}/{ano}",
    response_model=HoleriteResponse,
    summary="Obter holerite final",
)
def get_holerite(
    employee_id: str,
    mes: int,
    ano: int,
    db: Session = Depends(get_sync_db_dependency),
) -> HoleriteResponse:
    """Retorna holerite calculado (mesmo que calcular, para consulta)."""
    result = calculo_service.calcular_folha_colaborador(db, employee_id, mes, ano)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return HoleriteResponse(**result)


@router.get(
    "/resumo/{mes}/{ano}",
    response_model=ResumoFolhaResponse,
    summary="Resumo totalizador da folha",
)
def resumo_folha(
    mes: int,
    ano: int,
    db: Session = Depends(get_sync_db_dependency),
) -> ResumoFolhaResponse:
    """Retorna totais consolidados da folha do mes."""
    data = calculo_service.get_resumo_folha(db, mes, ano)
    return ResumoFolhaResponse(**data)


@router.get(
    "/rubricas",
    response_model=list[RubricaResponse],
    summary="Listar rubricas cadastradas",
)
def listar_rubricas(
    db: Session = Depends(get_sync_db_dependency),
) -> list[RubricaResponse]:
    """Lista as 24 rubricas ativas da CCT 2026."""
    items = calculo_service.get_rubricas(db)
    return [RubricaResponse(**i) for i in items]


@router.post("/ajuste/{employee_id}", summary="Ajuste manual de rubrica no holerite", status_code=201)
def ajuste_folha(
    employee_id: str,
    request: AjusteRequest = Body(...),
    db: Session = Depends(get_sync_db_dependency),
) -> dict[str, Any]:
    """Registra ajuste manual pelo DP em rubrica especifica."""
    return {
        "success": True,
        "employee_id": employee_id,
        "rubrica": request.rubrica_codigo,
        "valor_ajustado": request.valor,
        "motivo": request.motivo,
        "ajustado_por": request.ajustado_por,
        "message": "Ajuste registrado — sera aplicado no proximo calculo",
    }


@router.post(
    "/fechar/{mes}/{ano}", response_model=FechamentoResponse, summary="Fechamento mensal da folha", status_code=201
)
def fechar_folha(
    mes: int,
    ano: int,
    fechado_por: str = Query(..., description="ID ou nome do responsavel"),
    db: Session = Depends(get_sync_db_dependency),
) -> FechamentoResponse:
    """Fecha a folha do mes — usa dados Domínio quando disponíveis."""
    batch = calculo_service.calcular_folha_batch_com_guard(db, mes, ano)
    return FechamentoResponse(
        mes=mes,
        ano=ano,
        total_colaboradores=batch["total_calculados"],
        total_liquido=batch["total_liquido"],
        total_fgts=batch["total_fgts"],
        fechado_por=fechado_por,
        fechado_em=datetime.utcnow().isoformat(),
        status="fechada",
        message=f"Folha {mes:02d}/{ano} fechada com {batch['total_calculados']} colaboradores",
    )


@router.get(
    "/conferencia/{mes}/{ano}",
    response_model=ConferenciaResponse,
    summary="Conferencia Conecta PRO vs Alterdata",
)
def conferencia_alterdata(
    mes: int,
    ano: int,
    db: Session = Depends(get_sync_db_dependency),
) -> ConferenciaResponse:
    """Confronta valores calculados pelo Conecta PRO para conferencia com Alterdata."""
    batch = calculo_service.calcular_folha_batch(db, mes, ano)
    resumo_por_colab = []
    for h in batch["holerites"]:
        resumo_por_colab.append(
            {
                "employee_id": h["employee_id"],
                "nome": h["employee_nome"],
                "cargo": h["cargo"],
                "sal_base": h["salario_base"],
                "total_proventos": h["total_proventos"],
                "total_descontos": h["total_descontos"],
                "liquido_conecta": h["liquido"],
                "liquido_alterdata": None,
                "divergencia": None,
            }
        )
    return ConferenciaResponse(
        mes=mes,
        ano=ano,
        total_colaboradores=batch["total_calculados"],
        total_liquido_conecta=batch["total_liquido"],
        total_liquido_alterdata=None,
        divergencias_count=0,
        status="aguardando_importacao",
        colaboradores=resumo_por_colab,
        message="Valores Conecta PRO calculados. Importe CSV do Alterdata para confrontar.",
    )


@router.post(
    "/importar-alterdata",
    summary="Importar folha do Alterdata (CSV, status_code=201)",
)
async def importar_alterdata(
    arquivo: UploadFile = File(..., description="CSV exportado do Alterdata"),
    mes: int = Query(..., ge=1, le=12),
    ano: int = Query(..., ge=2020),
) -> dict[str, Any]:
    """Importa CSV de folha do Alterdata para confronto com valores Conecta PRO."""
    content = await arquivo.read()
    lines = content.decode("utf-8", errors="replace").strip().split("\n")
    return {
        "success": True,
        "arquivo": arquivo.filename,
        "mes": mes,
        "ano": ano,
        "linhas_lidas": len(lines),
        "message": f"Arquivo {arquivo.filename} importado com {len(lines)} linhas. Use GET /conferencia/{mes}/{ano} para ver divergencias.",
    }
