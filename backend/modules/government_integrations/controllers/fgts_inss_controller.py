"""
Controller para cálculos de FGTS e INSS.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db

# Imports relativos do módulo pai
from modules.government_integrations.utils import CalculoError

from ..schemas.common import StandardResponse
from ..schemas.fgts_inss import CalculoFGTSRequest, CalculoINSSRequest
from ..services.fgts_inss_service import FGTSINSSService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["FGTS/INSS"])


@router.post(
    "/fgts/calcular",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Calcula FGTS",
    description="Calcula valor de FGTS (8% ou rescisorio com multa 40%).",
)
async def calculate_fgts(current_user: CurrentActiveUser, request: CalculoFGTSRequest) -> StandardResponse:
    """
    Calcula FGTS.

    Args:
        request: Dados para cálculo.

    Returns:
        StandardResponse: Cálculo detalhado do FGTS.
    """
    try:
        resultado = FGTSINSSService.calcular_fgts(
            salario_base=request.salario_base,
            mes_referencia=request.mes_referencia,
            tipo_recolhimento=request.tipo_recolhimento,
            rescisao=request.rescisao,
        )

        return StandardResponse(
            success=True,
            message="FGTS calculado com sucesso",
            data=resultado,
        )

    except CalculoError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro no calculo: {str(e)}",
        )
    except Exception as e:
        logger.error("Erro ao calcular FGTS: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao calcular FGTS",
        )


@router.post(
    "/inss/calcular",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Calcula INSS",
    description="Calcula INSS com tabela progressiva 2026.",
)
async def calculate_inss(current_user: CurrentActiveUser, request: CalculoINSSRequest) -> StandardResponse:
    """
    Calcula INSS com tabela progressiva.

    Args:
        request: Dados para cálculo.

    Returns:
        StandardResponse: Cálculo detalhado do INSS.
    """
    try:
        resultado = FGTSINSSService.calcular_inss(
            salario_bruto=request.salario_bruto,
            categoria=request.categoria,
            mes_referencia=request.mes_referencia,
        )

        return StandardResponse(
            success=True,
            message="INSS calculado com sucesso",
            data=resultado,
        )

    except Exception as e:
        logger.error("Erro ao calcular INSS: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao calcular INSS",
        )


@router.get(
    "/inss/tabela",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Tabela INSS vigente",
    description="Retorna tabela progressiva do INSS 2026.",
)
async def get_inss_table(current_user: CurrentActiveUser) -> StandardResponse:
    """
    Retorna tabela INSS vigente.

    Returns:
        StandardResponse: Tabela progressiva.
    """
    return StandardResponse(
        success=True,
        message="Tabela INSS 2026",
        data=FGTSINSSService.get_tabela_inss(),
    )


@router.get(
    "/fgts/guias",
    status_code=status.HTTP_200_OK,
    summary="Listar guias FGTS",
    description="Lista guias de recolhimento FGTS (GRF) armazenadas no GED.",
)
async def listar_guias_fgts(
    current_user: CurrentActiveUser,
    mes_ref: str | None = Query(None, description="Filtro por mês (ex: 03.2026 ou 2026-03)"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Lista guias GRF_FGTS do GED."""
    from modules.people_management.ged.models.document_kit import GedDocumentKit
    from modules.people_management.ged.models.kit_document import KitDocument

    query = (
        select(KitDocument, GedDocumentKit.reference_month)
        .join(GedDocumentKit, KitDocument.kit_id == GedDocumentKit.id)
        .where(KitDocument.document_type == "grf_fgts")
        .order_by(GedDocumentKit.reference_month.desc())
    )
    result = await db.execute(query)
    rows = result.all()

    items = []
    for doc, ref_month in rows:
        mes_str = ref_month.strftime("%m.%Y") if ref_month else None
        if mes_ref and mes_ref not in (mes_str or ""):
            continue
        items.append(
            {
                "id": str(doc.id),
                "mes_ref": mes_str,
                "tipo": doc.document_type,
                "nome": doc.document_name,
                "arquivo_pdf": doc.file_path,
                "status": "disponivel" if doc.file_path else "pendente",
                "criado_em": doc.created_at.isoformat() if doc.created_at else None,
            }
        )

    return {"total": len(items), "items": items}


@router.get(
    "/inss/guias",
    status_code=status.HTTP_200_OK,
    summary="Listar guias INSS",
    description="Lista guias de recolhimento INSS (GPS) armazenadas no GED.",
)
async def listar_guias_inss(
    current_user: CurrentActiveUser,
    mes_ref: str | None = Query(None, description="Filtro por mês (ex: 03.2026 ou 2026-03)"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Lista guias GPS_INSS do GED."""
    from modules.people_management.ged.models.document_kit import GedDocumentKit
    from modules.people_management.ged.models.kit_document import KitDocument

    query = (
        select(KitDocument, GedDocumentKit.reference_month)
        .join(GedDocumentKit, KitDocument.kit_id == GedDocumentKit.id)
        .where(KitDocument.document_type == "gps_inss")
        .order_by(GedDocumentKit.reference_month.desc())
    )
    result = await db.execute(query)
    rows = result.all()

    items = []
    for doc, ref_month in rows:
        mes_str = ref_month.strftime("%m.%Y") if ref_month else None
        if mes_ref and mes_ref not in (mes_str or ""):
            continue
        items.append(
            {
                "id": str(doc.id),
                "mes_ref": mes_str,
                "nome": doc.document_name,
                "arquivo_pdf": doc.file_path,
                "status": "disponivel" if doc.file_path else "pendente",
                "criado_em": doc.created_at.isoformat() if doc.created_at else None,
            }
        )

    return {"total": len(items), "items": items}
