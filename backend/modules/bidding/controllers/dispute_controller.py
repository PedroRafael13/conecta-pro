"""
Controller de Disputas — Licitacoes
====================================
Endpoints para gerenciamento de disputas de pregao eletronico,
simulacoes de lances e monitoramento de sessoes.
Utiliza o agente Warrior para estrategias e simulacoes.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Body, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

from core.auth.dependencies import CurrentActiveUser
from modules.bidding.agents.warrior_agent import WarriorAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/disputes", tags=["Licitacoes - Disputas"])

# Instanciar agente Warrior
warrior_agent = WarriorAgent()


# ---- Schemas ----


class DisputeSimulationRequest(BaseModel):
    """Parametros para simulacao de disputa."""

    valor_referencia: float = Field(..., gt=0, description="Valor de referencia da licitacao")
    estrategia: str = Field(default="moderado", description="Estrategia: conservador, moderado, agressivo")
    piso_minimo: float | None = Field(None, description="Piso minimo para lances (0 = sem piso)")
    num_rodadas: int = Field(default=10, ge=1, le=50, description="Numero de rodadas da simulacao")
    concorrentes: int = Field(default=3, ge=1, le=10, description="Numero de concorrentes simulados")


class LanceRequest(BaseModel):
    """Dados para lance manual em disputa."""

    valor: float = Field(..., gt=0, description="Valor do lance")
    justificativa: str | None = Field(None, description="Justificativa do lance")


class DisputeStatusUpdate(BaseModel):
    """Atualizacao de status de disputa."""

    status: str = Field(..., description="Novo status (aguardando, em_disputa, encerrada, suspensa)")
    motivo: str | None = Field(None, description="Motivo da alteracao")


# ---- Cache/store temporario ----
_disputes_cache: dict[str, dict[str, Any]] = {}

VALID_STATUSES = {"aguardando", "em_disputa", "encerrada", "suspensa", "cancelada"}
VALID_ESTRATEGIAS = {"conservador", "moderado", "agressivo"}


# ---- Endpoints ----


@router.get("")
async def list_disputes(
    current_user: CurrentActiveUser,
    status_filter: str | None = Query(None, alias="status", description="Filtrar por status"),
    tender_id: str | None = Query(None, description="Filtrar por edital"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> dict[str, Any]:
    """Lista disputas de pregao eletronico."""
    try:
        results = list(_disputes_cache.values())

        if status_filter:
            results = [d for d in results if d.get("status") == status_filter]
        if tender_id:
            results = [d for d in results if d.get("tender_id") == tender_id]

        # Ordenar por data de criacao (mais recente primeiro)
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)

        # Paginacao
        total = len(results)
        start = (page - 1) * size
        end = start + size
        paginated = results[start:end]

        return {
            "items": paginated,
            "total": total,
            "page": page,
            "size": size,
        }
    except Exception as e:
        logger.error("Erro ao listar disputas: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar disputas: {str(e)}",
        )


@router.get("/{dispute_id}")
async def get_dispute(
    current_user: CurrentActiveUser,
    dispute_id: str = Path(..., description="ID da disputa"),
) -> dict[str, Any]:
    """Busca detalhes de uma disputa especifica."""
    dispute = _disputes_cache.get(dispute_id)
    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disputa nao encontrada: {dispute_id}",
        )
    return dispute


@router.post("/simulate", status_code=201)
async def simulate_dispute(current_user: CurrentActiveUser, request: DisputeSimulationRequest) -> dict[str, Any]:
    """
    Simula uma disputa de pregao eletronico usando o agente Warrior.

    Retorna a simulacao completa com rodadas, lances e resultado final.
    """
    if request.estrategia not in VALID_ESTRATEGIAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estrategia invalida: {request.estrategia}. Validas: {VALID_ESTRATEGIAS}",
        )

    try:
        piso = request.piso_minimo if request.piso_minimo else request.valor_referencia * 0.7

        result = await warrior_agent.run(
            valor_referencia=request.valor_referencia,
            estrategia=request.estrategia,
            piso_minimo=piso,
            num_rodadas=request.num_rodadas,
            concorrentes=request.concorrentes,
        )

        dispute_id = str(uuid4())
        now = datetime.utcnow().isoformat()

        dispute_record = {
            "id": dispute_id,
            "tipo": "simulacao",
            "status": "encerrada",
            "valor_referencia": request.valor_referencia,
            "estrategia": request.estrategia,
            "piso_minimo": piso,
            "num_rodadas": request.num_rodadas,
            "concorrentes": request.concorrentes,
            "resultado": result.data if result.success else None,
            "sucesso": result.success,
            "erro": result.error if not result.success else None,
            "created_at": now,
        }

        _disputes_cache[dispute_id] = dispute_record

        if result.success:
            return {
                "status": "success",
                "dispute_id": dispute_id,
                "simulacao": result.data,
            }
        return {
            "status": "error",
            "dispute_id": dispute_id,
            "message": result.error or "Erro na simulacao",
        }

    except Exception as e:
        logger.error("Erro na simulacao de disputa: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na simulacao de disputa: {str(e)}",
        )


@router.post("/{dispute_id}/lance", status_code=201)
async def register_lance(
    current_user: CurrentActiveUser,
    dispute_id: str = Path(..., description="ID da disputa"),
    request: LanceRequest = Body(...),
) -> dict[str, Any]:
    """Registra lance manual em uma disputa ativa."""
    dispute = _disputes_cache.get(dispute_id)
    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disputa nao encontrada: {dispute_id}",
        )

    if dispute.get("status") != "em_disputa":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Disputa nao esta em andamento. Status atual: {dispute.get('status')}",
        )

    lance_id = str(uuid4())
    now = datetime.utcnow().isoformat()

    lance = {
        "id": lance_id,
        "dispute_id": dispute_id,
        "valor": request.valor,
        "justificativa": request.justificativa,
        "tipo": "manual",
        "created_at": now,
    }

    # Adicionar lance ao historico da disputa
    if "lances" not in dispute:
        dispute["lances"] = []
    dispute["lances"].append(lance)
    dispute["ultimo_lance"] = now

    logger.info("Lance registrado: disputa=%s, valor=%.2f", dispute_id, request.valor)

    return {
        "status": "success",
        "lance": lance,
        "total_lances": len(dispute["lances"]),
    }


@router.patch("/{dispute_id}/status")
async def update_dispute_status(
    current_user: CurrentActiveUser,
    dispute_id: str = Path(..., description="ID da disputa"),
    request: DisputeStatusUpdate = Body(...),
) -> dict[str, Any]:
    """Atualiza status de uma disputa."""
    if request.status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status invalido: {request.status}. Validos: {VALID_STATUSES}",
        )

    dispute = _disputes_cache.get(dispute_id)
    if not dispute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disputa nao encontrada: {dispute_id}",
        )

    old_status = dispute.get("status")
    dispute["status"] = request.status
    dispute["motivo_status"] = request.motivo
    dispute["updated_at"] = datetime.utcnow().isoformat()

    logger.info(
        "Status da disputa %s atualizado: %s -> %s",
        dispute_id,
        old_status,
        request.status,
    )

    return {
        "status": "success",
        "dispute_id": dispute_id,
        "old_status": old_status,
        "new_status": request.status,
    }
