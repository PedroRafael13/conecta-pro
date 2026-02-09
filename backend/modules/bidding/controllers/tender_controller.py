"""
Controller de Editais - Licitacoes
==================================
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from core.database import get_db
from modules.bidding.schemas.tender import (
    TenderCreate,
    TenderListResponse,
    TenderResponse,
    TenderSearchParams,
    TenderUpdate,
)
from modules.bidding.services.pncp_service import PNCPService
from modules.bidding.services.tender_service import TenderService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tenders", tags=["Licitacoes - Editais"])


@router.get("/", response_model=TenderListResponse)
async def list_tenders(
    uf: str = Query(default="AM", max_length=2),
    municipio: str | None = None,
    modalidade: str | None = None,
    segmento: str | None = None,
    status: str | None = None,
    participando: bool | None = None,
    interesse: bool | None = None,
    valor_min: float | None = None,
    valor_max: float | None = None,
    termo_busca: str | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Lista editais com filtros e paginacao."""
    service = TenderService(db)
    params = TenderSearchParams(
        uf=uf,
        municipio=municipio,
        modalidade=modalidade,
        segmento=segmento,
        status=status,
        participando=participando,
        interesse=interesse,
        valor_min=valor_min,
        valor_max=valor_max,
        termo_busca=termo_busca,
        page=page,
        size=size,
    )
    return await service.list(params)


@router.get("/dashboard")
async def get_dashboard(uf: str = Query(default="AM", max_length=2), db: Session = Depends(get_db)):
    """Retorna dados para dashboard de editais."""
    service = TenderService(db)
    return await service.get_dashboard(uf)


@router.get("/abertos", response_model=list[TenderResponse])
async def list_abertos(uf: str = Query(default="AM", max_length=2), db: Session = Depends(get_db)):
    """Lista editais abertos para participacao."""
    service = TenderService(db)
    return await service.get_abertos(uf)


@router.get("/participando", response_model=list[TenderResponse])
async def list_participando(db: Session = Depends(get_db)):
    """Lista editais que estamos participando."""
    service = TenderService(db)
    return await service.get_participando()


@router.get("/segmento/{segmento}", response_model=list[TenderResponse])
async def list_por_segmento(segmento: str, uf: str = Query(default="AM", max_length=2), db: Session = Depends(get_db)):
    """Lista editais por segmento."""
    service = TenderService(db)
    return await service.get_por_segmento(segmento, uf)


@router.get("/{tender_id}", response_model=TenderResponse)
async def get_tender(tender_id: UUID, db: Session = Depends(get_db)):
    """Busca edital por ID."""
    service = TenderService(db)
    tender = await service.get(tender_id)
    if not tender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Edital nao encontrado")
    return tender


@router.post("/", response_model=TenderResponse, status_code=status.HTTP_201_CREATED)
async def create_tender(data: TenderCreate, db: Session = Depends(get_db)):
    """Cria novo edital."""
    service = TenderService(db)
    try:
        return await service.create(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{tender_id}", response_model=TenderResponse)
async def update_tender(tender_id: UUID, data: TenderUpdate, db: Session = Depends(get_db)):
    """Atualiza edital."""
    service = TenderService(db)
    tender = await service.update(tender_id, data)
    if not tender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Edital nao encontrado")
    return tender


@router.delete("/{tender_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tender(tender_id: UUID, db: Session = Depends(get_db)):
    """Remove edital."""
    service = TenderService(db)
    if not await service.delete(tender_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Edital nao encontrado")


@router.post("/{tender_id}/participar", response_model=TenderResponse)
async def marcar_participacao(
    tender_id: UUID, participando: bool = True, motivo: str | None = None, db: Session = Depends(get_db)
):
    """Marca participacao em edital."""
    service = TenderService(db)
    tender = await service.marcar_participacao(tender_id, participando, motivo)
    if not tender:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Edital nao encontrado")
    return tender


@router.post("/{tender_id}/status", response_model=TenderResponse)
async def alterar_status(tender_id: UUID, novo_status: str, db: Session = Depends(get_db)):
    """Altera status do edital."""
    service = TenderService(db)
    try:
        tender = await service.alterar_status(tender_id, novo_status)
        if not tender:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Edital nao encontrado")
        return tender
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{tender_id}/documentos")
async def get_documentos(tender_id: UUID, db: Session = Depends(get_db)):
    """Lista documentos do edital."""
    service = TenderService(db)
    return await service.get_documents(tender_id)


# Endpoints PNCP
@router.post("/sync-pncp")
async def sync_pncp(
    uf: str = Query(default="AM", max_length=2),
    dias: int = Query(default=30, ge=1, le=90),
    segmentos: list[str] | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Sincroniza editais do PNCP."""
    service = PNCPService(db)
    try:
        result = await service.sincronizar_editais(uf, dias, segmentos)
        return result
    finally:
        await service.close()


@router.get("/pncp/status")
async def pncp_status(db: Session = Depends(get_db)):
    """Verifica status da API PNCP."""
    service = PNCPService(db)
    try:
        return await service.verificar_disponibilidade()
    finally:
        await service.close()


@router.get("/pncp/buscar")
async def buscar_pncp(
    uf: str = Query(default="AM", max_length=2),
    modalidade: str | None = None,
    pagina: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
):
    """Busca editais diretamente no PNCP."""
    service = PNCPService(db)
    try:
        return await service.buscar_compras(uf=uf, modalidade=modalidade, pagina=pagina)
    finally:
        await service.close()
