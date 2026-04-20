"""Controller FastAPI — FASE 4 BLOCO 3 / T2 (§27, §28).

Expõe KitBuilderService via 2 endpoints:
- GET /kits/completude/{condominio_id}?mes_ref=MM.YYYY
- GET /kits/lote?mes_ref=MM.YYYY

§27: contrato de API (fonte única da verdade)
§28: documentação desta implementação

§13.1 Chesterton: KitBuilderService usado como está, sem alteração.
BUG 7 (CPRO 9): auth via Depends(get_current_user) OBRIGATÓRIA em ambos endpoints.
§28.6: usa get_sync_db_dependency (sync) pois KitBuilderService usa Session síncrona.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.auth.dependencies import get_current_user
from core.database.session import get_sync_db_dependency
from modules.gedeon.schemas.kit_completude import CompletudeKitResponse
from modules.gedeon.services.kit_builder_service import KitBuilderService

router = APIRouter(prefix="/gedeon", tags=["GEDEON — Kits"])

MES_REF_QUERY = Query(
    ...,
    description="Mês de referência no formato MM.YYYY (ex: 03.2026)",
    regex=r"^(0[1-9]|1[0-2])\.\d{4}$",
    examples=["03.2026"],
)


@router.get(
    "/kits/completude/{condominio_id}",
    response_model=CompletudeKitResponse,
    summary="Completude do kit documental de 1 condomínio",
    description="Retorna docs presentes, faltantes e métricas conforme §27.4.",
)
def get_completude_kit(
    condominio_id: UUID,
    mes_ref: str = MES_REF_QUERY,
    db: Session = Depends(get_sync_db_dependency),
    current_user=Depends(get_current_user),
) -> CompletudeKitResponse:
    """GET /api/v1/gedeon/kits/completude/{condominio_id}?mes_ref=MM.YYYY"""
    service = KitBuilderService(db)
    try:
        kit = service.build_completude(condominio_id, mes_ref)
    except ValueError as exc:
        msg = str(exc)
        if "mes_ref" in msg.lower():
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=404, detail=msg)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao montar completude do kit",
        )
    return CompletudeKitResponse.from_dataclass(kit)


@router.get(
    "/kits/lote",
    response_model=list[CompletudeKitResponse],
    summary="Completude em lote de todos os condomínios ativos",
    description="Retorna array de CompletudeKit (1 por condomínio ativo).",
)
def get_completude_lote(
    mes_ref: str = MES_REF_QUERY,
    db: Session = Depends(get_sync_db_dependency),
    current_user=Depends(get_current_user),
) -> list[CompletudeKitResponse]:
    """GET /api/v1/gedeon/kits/lote?mes_ref=MM.YYYY"""
    service = KitBuilderService(db)
    try:
        kits = service.build_lote_condominios(mes_ref)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao montar completude em lote",
        )
    return [CompletudeKitResponse.from_dataclass(k) for k in kits]
