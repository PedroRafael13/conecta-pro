"""
Controller de Contratos — Departamento Pessoal.

Endpoints CRUD para gestão de contratos de trabalho.
"""

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.people_management.hr.publishers import publish_contrato_criado
from modules.people_management.hr.schemas.contract import (
    ContractCreate,
    ContractResponse,
    ContractUpdate,
)
from modules.people_management.hr.services.contract_service import (
    ContractService,
    gerar_pdf_contrato,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contracts", tags=["DP - Contratos"])


@router.get(
    "",
    summary="Listar Contratos",
    description="Retorna lista paginada de todos os contratos de trabalho com paginação.",
)
async def list_contracts(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Any:
    """Lista todos os contratos com paginação."""
    service = ContractService(db)
    result = await service.list_all(page=page, page_size=page_size)
    # Serialize manually to avoid Pydantic errors with raw ORM objects
    if isinstance(result, dict) and "items" in result:
        result["items"] = [ContractResponse.model_validate(c).model_dump(mode="json") for c in result["items"]]
    elif isinstance(result, list):
        result = [ContractResponse.model_validate(c).model_dump(mode="json") for c in result]
    return result


@router.get(
    "/employee/{employee_id}",
    summary="Contratos por Funcionário",
    response_model=list[ContractResponse],
    description="Retorna lista paginada de todos os contratos de trabalho com paginação.",
)
async def list_employee_contracts(
    employee_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Lista todos os contratos de um funcionário (histórico)."""
    service = ContractService(db)
    return await service.list_by_employee(employee_id)


@router.get(
    "/employee/{employee_id}/current",
    summary="Contrato Vigente",
    response_model=ContractResponse,
    description="Retorna lista paginada de todos os contratos de trabalho com paginação.",
)
async def get_current_contract(
    employee_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna o contrato vigente de um funcionário."""
    service = ContractService(db)
    contract = await service.get_current_contract(employee_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Nenhum contrato vigente encontrado")
    return contract


@router.post(
    "",
    summary="Criar Contrato",
    response_model=ContractResponse,
    status_code=201,
    description="Retorna lista paginada de todos os contratos de trabalho com paginação.",
)
async def create_contract(
    data: ContractCreate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Cria um novo contrato de trabalho.

    Se houver contrato vigente, este será marcado como não atual.
    """
    service = ContractService(db)
    contract = await service.create_contract(data.model_dump())
    await db.commit()
    asyncio.create_task(
        publish_contrato_criado(
            funcionario_id=str(getattr(data, "employee_id", "") or ""),
            contract_id=str(getattr(contract, "id", "")),
            tipo_contrato=str(getattr(data, "contract_type", "") or getattr(data, "tipo_contrato", "")),
        )
    )
    return contract


@router.get(
    "/{contract_id}",
    summary="Buscar Contrato",
    response_model=ContractResponse,
    description="Retorna lista paginada de todos os contratos de trabalho com paginação.",
)
async def get_contract(
    contract_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna detalhes de um contrato."""
    service = ContractService(db)
    contract = await service.get_by_id(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    return contract


@router.patch(
    "/{contract_id}",
    summary="Atualizar Contrato",
    response_model=ContractResponse,
    description="Retorna lista paginada de todos os contratos de trabalho com paginação.",
)
async def update_contract(
    contract_id: str,
    data: ContractUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Atualiza dados de um contrato."""
    service = ContractService(db)
    contract = await service.update_contract(contract_id, data.model_dump(exclude_unset=True))
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    await db.commit()
    return contract


@router.post(
    "/{contract_id}/document",
    summary="Gerar Documento de Contrato",
    status_code=201,
    description="Retorna lista paginada de todos os contratos de trabalho com paginação.",
)
async def generate_contract_document(
    contract_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Gera documento de contrato de trabalho."""
    import uuid as _uuid

    try:
        _uuid.UUID(contract_id)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=422, detail="contract_id inválido: deve ser um UUID válido")

    service = ContractService(db)
    contract = await service.get_by_id(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")

    # Buscar nome do funcionário
    from modules.people_management.hr.services.employee_service import EmployeeService

    emp_service = EmployeeService(db)
    employee = await emp_service.get_by_id(contract.employee_id)
    employee_name = employee.nome if employee else "N/A"

    document = service.generate_contract_document(contract, employee_name)
    return document


@router.get(
    "/employee/{employee_id}/gerar-contrato-html",
    summary="Gerar HTML do Contrato de Trabalho",
    description="Renderiza o template HTML do contrato CLT com dados reais do funcionário e retorna para download.",
)
async def gerar_contrato_html(
    employee_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Renderiza contrato_trabalho.html com dados do funcionário e retorna como download."""
    import uuid as _uuid

    try:
        _uuid.UUID(employee_id)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=422, detail="employee_id inválido: deve ser UUID válido")

    from modules.people_management.hr.services.contract_generator_service import (
        ContractGeneratorService,
    )

    try:
        svc = ContractGeneratorService(db)
        result = await svc.gerar_contrato_trabalho_html(employee_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Erro ao gerar contrato HTML para %s: %s", employee_id, exc)
        raise HTTPException(status_code=500, detail=f"Erro ao gerar contrato: {exc}") from exc

    return Response(
        content=result["html_content"].encode("utf-8"),
        media_type="text/html",
        headers={
            "Content-Disposition": f'attachment; filename="{result["filename"]}"',
            "Cache-Control": "no-store",
        },
    )


@router.get(
    "/{contract_id}/pdf",
    summary="Download PDF do Contrato",
    description=("Gera e retorna o PDF do contrato de trabalho. Usa contract_templates para cláusulas customizadas."),
)
async def download_contrato_pdf(
    contract_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Gera PDF real do contrato usando reportlab + contract_templates."""
    try:
        pdf_bytes = await gerar_pdf_contrato(db, contract_id)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (f'attachment; filename="contrato_{contract_id[:8]}.pdf"'),
                "Cache-Control": "no-store",
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Erro ao gerar PDF contrato %s: %s", contract_id, exc)
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PDF: {exc}") from exc
