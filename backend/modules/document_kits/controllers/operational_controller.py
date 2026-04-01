"""Controller de Integração Operacional - Document Kits."""

import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from modules.document_kits import scheduler as kit_scheduler
from modules.document_kits.services.kit_monthly_generator_service import KitMonthlyGeneratorService
from modules.document_kits.services.kit_operational_service import KitOperationalService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/document-kits-operational", tags=["Document Kits - Operational"])


async def get_operational_service(db: AsyncSession = Depends(get_db)) -> KitOperationalService:
    """Retorna instancia do Operational service."""
    return KitOperationalService(db)


async def get_generator_service(db: AsyncSession = Depends(get_db)) -> KitMonthlyGeneratorService:
    """Retorna instancia do Monthly Generator service."""
    return KitMonthlyGeneratorService(db)


# === Operational Integration Endpoints ===


@router.get("/employees", response_model=list[dict])
async def get_employees_by_condominium(
    condominium_id: str,
    current_user: CurrentActiveUser,
    start_date: str | None = Query(None, description="Data inicial (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="Data final (YYYY-MM-DD)"),
    include_inactive: bool = Query(False, description="Incluir funcionários inativos"),
    op_service: KitOperationalService = Depends(get_operational_service),
) -> list[dict]:
    """
    Busca todos os colaboradores alocados em um condomínio no período.

    Esta é a função PRINCIPAL para geração de kits mensais.

    Params:
        - condominium_id: UUID do condomínio
        - start_date: Data inicial (formato: YYYY-MM-DD, default = hoje)
        - end_date: Data final (formato: YYYY-MM-DD, default = hoje)
        - include_inactive: Incluir funcionários inativos (default = False)

    Returns:
        Lista de colaboradores com dados completos (employee, allocation, post)

    Example:
        GET /api/v1/document-kits-operational/employees?condominium_id=uuid&start_date=2026-01-01&end_date=2026-01-31
    """
    try:
        # Parse dates if provided
        start = date.fromisoformat(start_date) if start_date else None
        end = date.fromisoformat(end_date) if end_date else None

        # Fetch employees
        employees_data = await op_service.get_employees_by_condominium(
            condominium_id=condominium_id,
            start_date=start,
            end_date=end,
            include_inactive=include_inactive,
        )

        # Serialize to dict
        result = [emp.to_dict() for emp in employees_data]

        logger.info(
            "Fetched %d employees for condominium %s (period: %s to %s)",
            len(result),
            condominium_id,
            start_date or "today",
            end_date or "today",
        )

        return result

    except ValueError as e:
        logger.error("Validation error: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error("Error fetching employees: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/employees/month", response_model=list[dict])
async def get_employees_by_month(
    condominium_id: str,
    current_user: CurrentActiveUser,
    month: int = Query(..., ge=1, le=12, description="Mês (1-12)"),
    year: int = Query(..., ge=2020, le=2100, description="Ano (ex: 2026)"),
    include_inactive: bool = Query(False, description="Incluir funcionários inativos"),
    op_service: KitOperationalService = Depends(get_operational_service),
) -> list[dict]:
    """
    Busca colaboradores de um condomínio em um mês específico.

    Helper function para facilitar busca mensal.

    Params:
        - condominium_id: UUID do condomínio
        - month: Mês (1-12)
        - year: Ano (ex: 2026)
        - include_inactive: Incluir inativos

    Returns:
        Lista de colaboradores com dados completos

    Example:
        GET /api/v1/document-kits-operational/employees/month?condominium_id=uuid&month=1&year=2026
    """
    try:
        employees_data = await op_service.get_employees_by_month(
            condominium_id=condominium_id,
            month=month,
            year=year,
            include_inactive=include_inactive,
        )

        result = [emp.to_dict() for emp in employees_data]

        logger.info(
            "Fetched %d employees for condominium %s (month: %02d/%d)",
            len(result),
            condominium_id,
            month,
            year,
        )

        return result

    except ValueError as e:
        logger.error("Validation error: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error("Error fetching employees by month: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/condominiums", response_model=list[dict])
async def get_condominiums_with_employees(
    current_user: CurrentActiveUser,
    op_service: KitOperationalService = Depends(get_operational_service),
) -> list[dict]:
    """
    Busca TODOS os condomínios que possuem funcionários alocados atualmente.

    Útil para geração de kits mensais em lote.

    Returns:
        Lista de dicts com condomínio + contagem de funcionários:
        [
            {
                "condominium_id": "uuid",
                "condominium_name": "Ideal Flores da Cidade",
                "client_id": "uuid",
                "employee_count": 13,
                "post_count": 5
            },
            ...
        ]

    Example:
        GET /api/v1/document-kits-operational/condominiums
    """
    try:
        result = await op_service.get_condominiums_with_employees()

        logger.info("Fetched %d condominiums with active employees", len(result))

        return result

    except Exception as e:
        logger.error("Error fetching condominiums: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/validate", response_model=dict)
async def validate_condominium_has_employees(
    condominium_id: str,
    current_user: CurrentActiveUser,
    month: int | None = Query(None, ge=1, le=12, description="Mês (1-12)"),
    year: int | None = Query(None, ge=2020, le=2100, description="Ano"),
    op_service: KitOperationalService = Depends(get_operational_service),
) -> dict:
    """
    Valida se um condomínio possui funcionários no período.

    Params:
        - condominium_id: UUID do condomínio
        - month: Mês (opcional, default = mês atual)
        - year: Ano (opcional, default = ano atual)

    Returns:
        {
            "has_employees": bool,
            "employee_count": int,
            "period": "01/2026",
            "message": str
        }

    Example:
        GET /api/v1/document-kits-operational/validate?condominium_id=uuid&month=1&year=2026
    """
    try:
        result = await op_service.validate_condominium_has_employees(
            condominium_id=condominium_id,
            month=month,
            year=year,
        )

        logger.info(
            "Validation for condominium %s: %s employees in period %s",
            condominium_id,
            result["employee_count"],
            result["period"],
        )

        return result

    except ValueError as e:
        logger.error("Validation error: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error("Error validating condominium: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


# === Monthly Kit Generation Endpoints ===


@router.post("/generate/monthly", response_model=dict)
async def generate_monthly_kits(
    condominium_id: str,
    current_user: CurrentActiveUser,
    month: int = Query(..., ge=1, le=12, description="Mês (1-12)"),
    year: int = Query(..., ge=2020, le=2100, description="Ano"),
    created_by_id: str = Query(..., description="UUID do usuário que solicitou"),
    prazo_dias: int = Query(30, ge=1, le=180, description="Prazo em dias para entrega"),
    generator: KitMonthlyGeneratorService = Depends(get_generator_service),
) -> dict:
    """
    Gera kits mensais para TODOS os funcionários de um condomínio.

    Esta é a função PRINCIPAL de geração automática mensal.

    Params:
        - condominium_id: UUID do condomínio
        - month: Mês (1-12)
        - year: Ano
        - created_by_id: UUID do usuário que solicitou
        - prazo_dias: Prazo em dias para entrega (default: 30)

    Returns:
        {
            "success": bool,
            "condominium_id": str,
            "period": "01/2026",
            "template_kit_id": str,
            "employees_found": int,
            "assignments_created": int,
            "assignments_skipped": int,
            "assignments_failed": int,
            "details": [...]
        }

    Example:
        POST /api/v1/document-kits-operational/generate/monthly?condominium_id=uuid&month=1&year=2026&created_by_id=user-uuid
    """
    try:
        result = await generator.generate_monthly_kits(
            condominio_id=condominium_id,
            month=month,
            year=year,
            created_by_id=created_by_id,
            prazo_dias=prazo_dias,
        )

        logger.info(
            "Monthly kits generated for condominium %s: %s created, %s skipped, %s failed",
            condominium_id,
            result.get("assignments_created", 0),
            result.get("assignments_skipped", 0),
            result.get("assignments_failed", 0),
        )

        return result

    except Exception as e:
        logger.error("Error generating monthly kits: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/generate/batch", response_model=dict)
async def generate_kits_for_all_condominiums(
    current_user: CurrentActiveUser,
    month: int = Query(..., ge=1, le=12, description="Mês (1-12)"),
    year: int = Query(..., ge=2020, le=2100, description="Ano"),
    created_by_id: str = Query(..., description="UUID do usuário/sistema que solicitou"),
    generator: KitMonthlyGeneratorService = Depends(get_generator_service),
) -> dict:
    """
    Gera kits mensais para TODOS os condomínios que possuem funcionários.

    Esta função é ideal para execução em batch/scheduler no início de cada mês.

    Params:
        - month: Mês (1-12)
        - year: Ano
        - created_by_id: UUID do usuário/sistema que solicitou

    Returns:
        {
            "success": bool,
            "period": "01/2026",
            "condominiums_processed": int,
            "total_employees_found": int,
            "total_assignments_created": int,
            "total_assignments_skipped": int,
            "total_assignments_failed": int,
            "condominiums_details": [...]
        }

    Example:
        POST /api/v1/document-kits-operational/generate/batch?month=1&year=2026&created_by_id=system-uuid
    """
    try:
        result = await generator.generate_kits_for_all_condominiums(
            month=month,
            year=year,
            created_by_id=created_by_id,
        )

        logger.info(
            "Batch generation completed: %s condominiums, %s kits created",
            result.get("condominiums_processed", 0),
            result.get("total_assignments_created", 0),
        )

        return result

    except Exception as e:
        logger.error("Error in batch kit generation: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


# === Scheduler Management Endpoints ===


@router.get("/scheduler/status", response_model=dict)
def get_scheduler_status(current_user: CurrentActiveUser) -> dict:
    """
    Retorna status do scheduler de geração automática.

    Returns:
        {
            "running": bool,
            "jobs_count": int,
            "jobs": [...]
        }

    Example:
        GET /api/v1/document-kits-operational/scheduler/status
    """
    return kit_scheduler.get_scheduler_status()


@router.post("/scheduler/start", response_model=dict)
def start_scheduler(current_user: CurrentActiveUser) -> dict:
    """
    Inicia o scheduler de geração automática.

    Returns:
        {"message": "Scheduler iniciado com sucesso"}

    Example:
        POST /api/v1/document-kits-operational/scheduler/start
    """
    try:
        kit_scheduler.start_scheduler()
        return {"message": "Scheduler iniciado com sucesso"}
    except Exception as e:
        logger.error("Error starting scheduler: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/scheduler/stop", response_model=dict)
def stop_scheduler(current_user: CurrentActiveUser) -> dict:
    """
    Para o scheduler de geração automática.

    Returns:
        {"message": "Scheduler parado com sucesso"}

    Example:
        POST /api/v1/document-kits-operational/scheduler/stop
    """
    try:
        kit_scheduler.stop_scheduler()
        return {"message": "Scheduler parado com sucesso"}
    except Exception as e:
        logger.error("Error stopping scheduler: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
