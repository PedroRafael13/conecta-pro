"""
Controller de Feriados — CCT 2026.

Endpoints para consulta de feriados Manaus/AM.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Query

from core.auth.dependencies import CurrentActiveUser
from modules.cct.models.holidays import (
    FERIADOS_MANAUS_2026,
    get_feriados_mes,
    is_feriado,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feriados", tags=["CCT — Feriados"])


@router.get("")
async def get_feriados(
    current_user: CurrentActiveUser,
) -> Any:
    """Retorna todos os 16 feriados de Manaus/AM 2026."""
    return {
        "total": len(FERIADOS_MANAUS_2026),
        "ano": 2026,
        "municipio": "Manaus/AM",
        "feriados": [
            {
                "data": f.data.isoformat(),
                "nome": f.nome,
                "tipo": f.tipo,
                "dia_semana": f.data.strftime("%A"),
            }
            for f in FERIADOS_MANAUS_2026
        ],
    }


@router.get("/mes/{mes}")
async def get_feriados_por_mes(
    mes: int,
    current_user: CurrentActiveUser,
) -> Any:
    """Retorna feriados de um mes especifico."""
    if mes < 1 or mes > 12:
        return {"error": "Mes deve ser entre 1 e 12"}

    feriados = get_feriados_mes(mes)
    return {
        "mes": mes,
        "total": len(feriados),
        "feriados": [
            {
                "data": f.data.isoformat(),
                "nome": f.nome,
                "tipo": f.tipo,
            }
            for f in feriados
        ],
    }


@router.get("/verificar")
async def verificar_feriado(
    current_user: CurrentActiveUser,
    data: str = Query(..., description="Data no formato YYYY-MM-DD"),
) -> Any:
    """Verifica se uma data especifica e feriado."""
    try:
        dt = datetime.strptime(data, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Formato de data invalido. Use YYYY-MM-DD"}

    feriado = is_feriado(dt)
    return {
        "data": data,
        "eh_feriado": feriado is not None,
        "feriado": (
            {
                "nome": feriado.nome,
                "tipo": feriado.tipo,
            }
            if feriado
            else None
        ),
    }
