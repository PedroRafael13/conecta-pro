"""
Controller de Admissão — Departamento Pessoal.

Endpoints para o workflow de admissão de novos colaboradores.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.people_management.hr.models.admission import AdmissionStatus
from modules.people_management.hr.schemas.admission import (
    AdmissionProcessCreate,
    AdmissionProcessResponse,
    AdmissionProcessUpdate,
)
from modules.people_management.hr.services.admission_service import AdmissionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admissions", tags=["DP - Admissões"])


@router.get("")
async def list_admissions(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    status: AdmissionStatus | None = Query(None, description="Filtro por status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Any:
    """Lista processos de admissão com filtro e paginação."""
    service = AdmissionService(db)
    return await service.list_admissions(status=status, page=page, page_size=page_size)


@router.post("", response_model=AdmissionProcessResponse, status_code=201)
async def create_admission(
    data: AdmissionProcessCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Cria um novo processo de admissão."""
    service = AdmissionService(db)
    admission = await service.create_admission(data.model_dump(), created_by_id=current_user.id)
    await db.commit()
    return admission


@router.get("/checklist")
async def get_document_checklist(
    include_security: bool = Query(True, description="Incluir documentos de vigilância"),
) -> Any:
    """Retorna checklist padrão de documentos para admissão."""
    service = AdmissionService(db=None)  # type: ignore[arg-type]
    return service.generate_document_checklist(include_security=include_security)


@router.get("/{admission_id}", response_model=AdmissionProcessResponse)
async def get_admission(
    admission_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna detalhes de um processo de admissão."""
    service = AdmissionService(db)
    admission = await service.get_by_id(admission_id)
    if not admission:
        raise HTTPException(status_code=404, detail="Admissão não encontrada")
    return admission


@router.patch("/{admission_id}", response_model=AdmissionProcessResponse)
async def update_admission(
    admission_id: str,
    data: AdmissionProcessUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Atualiza dados de um processo de admissão."""
    service = AdmissionService(db)
    update_data = data.model_dump(exclude_unset=True)
    new_status = update_data.pop("status", None)

    if new_status:
        admission = await service.update_status(admission_id, new_status, data=update_data)
    else:
        admission = await service.get_by_id(admission_id)
        if admission:
            for key, value in update_data.items():
                if hasattr(admission, key) and value is not None:
                    setattr(admission, key, value)
            await db.flush()
            await db.refresh(admission)

    if not admission:
        raise HTTPException(status_code=404, detail="Admissão não encontrada")
    await db.commit()
    return admission


@router.post("/{admission_id}/complete")
async def complete_admission(
    admission_id: str,
    employee_data: dict,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Conclui o processo de admissão e cria o registro de Employee."""
    service = AdmissionService(db)
    try:
        result = await service.complete_admission(admission_id, employee_data)
        await db.commit()
        return {
            "message": "Admissão concluída com sucesso",
            "admission_id": str(result["admission"].id),
            "employee_id": str(result["employee"].id),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
