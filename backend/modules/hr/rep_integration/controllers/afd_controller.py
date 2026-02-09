"""Controller para gestão de arquivos AFD."""

import logging
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_user
from core.database import get_db
from modules.hr.rep_integration.repositories import AFDRecordRepository
from modules.hr.rep_integration.schemas import (
    AFDExportRequest,
    AFDExportResponse,
    AFDImportRequest,
    AFDImportResponse,
    AFDRecordFilter,
    AFDRecordList,
    AFDRecordResponse,
    AFDValidationResult,
)
from modules.hr.rep_integration.services import AFDService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/afd", tags=["AFD Records"])


@router.get("/records", response_model=AFDRecordList)
async def list_afd_records(
    device_id: UUID | None = None,
    condominio_id: UUID | None = None,
    record_type: str | None = None,
    pis_number: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    is_exported: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> AFDRecordList:
    """Lista registros AFD."""
    repo = AFDRecordRepository(db)

    filters = AFDRecordFilter(
        device_id=device_id,
        condominio_id=condominio_id,
        record_type=record_type,
        pis_number=pis_number,
        date_from=date_from,
        date_to=date_to,
        is_exported=is_exported,
    )

    records, total = await repo.list_records(filters, page, page_size)

    return AFDRecordList(
        items=records,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/records/{record_id}", response_model=AFDRecordResponse)
async def get_afd_record(
    record_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> AFDRecordResponse:
    """Obtém registro AFD por ID."""
    repo = AFDRecordRepository(db)
    record = await repo.get_by_id(record_id)

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro não encontrado",
        )

    return record


@router.post("/export", response_model=AFDExportResponse)
async def export_afd(
    request: AFDExportRequest,
    company_cnpj: str = Query(..., min_length=14, max_length=14),
    company_cei: str = Query(..., min_length=12, max_length=12),
    company_name: str = Query(..., min_length=1, max_length=150),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> AFDExportResponse:
    """Exporta arquivo AFD para um período."""
    afd_service = AFDService(db)

    try:
        result = await afd_service.export_afd(
            request=request,
            company_cnpj=company_cnpj,
            company_cei=company_cei,
            company_name=company_name,
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/export/{device_id}/download")
async def download_afd(
    device_id: UUID,
    start_date: date,
    end_date: date,
    company_cnpj: str = Query(..., min_length=14, max_length=14),
    company_cei: str = Query(..., min_length=12, max_length=12),
    company_name: str = Query(..., min_length=1, max_length=150),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
):
    """Baixa arquivo AFD."""
    afd_service = AFDService(db)

    request = AFDExportRequest(
        device_id=device_id,
        start_date=start_date,
        end_date=end_date,
    )

    result = await afd_service.export_afd(
        request=request,
        company_cnpj=company_cnpj,
        company_cei=company_cei,
        company_name=company_name,
    )

    if not result.success or not result.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum registro para exportar",
        )

    return FileResponse(
        path=result.file_path,
        filename=result.file_name,
        media_type="text/plain",
    )


@router.post("/validate", response_model=AFDValidationResult)
async def validate_afd(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> AFDValidationResult:
    """Valida arquivo AFD."""
    content = await file.read()
    content_str = content.decode("utf-8")

    afd_service = AFDService(db)
    return await afd_service.validate_afd_file(content_str)


@router.post("/import", response_model=AFDImportResponse)
async def import_afd(
    device_id: UUID,
    file: UploadFile = File(...),
    validate_only: bool = Query(False),
    skip_duplicates: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> AFDImportResponse:
    """Importa arquivo AFD."""
    content = await file.read()
    content_str = content.decode("utf-8")

    request = AFDImportRequest(
        device_id=device_id,
        file_content=content_str,
        validate_only=validate_only,
        skip_duplicates=skip_duplicates,
    )

    afd_service = AFDService(db)
    return await afd_service.import_afd_file(request)


@router.get("/statistics")
async def get_afd_statistics(
    device_id: UUID | None = None,
    condominio_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),  # pylint: disable=unused-argument
) -> dict:
    """Retorna estatísticas de registros AFD."""
    afd_service = AFDService(db)
    return await afd_service.get_afd_statistics(device_id, condominio_id)
