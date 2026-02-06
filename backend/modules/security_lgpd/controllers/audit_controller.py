"""
Controller de Auditoria LGPD.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from modules.security_lgpd.schemas.audit import AuditLogRequest
from modules.security_lgpd.schemas.common import StandardResponse
from modules.security_lgpd.services.audit_service import AuditService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit", tags=["LGPD - Auditoria"])


@router.post(
    "/log",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registra evento de auditoria",
    description="Registra evento na trilha de auditoria com hash chain.",
)
async def create_audit_log(request: AuditLogRequest) -> StandardResponse:
    """
    Registra evento de auditoria.

    Args:
        request: Dados do evento.

    Returns:
        StandardResponse: Confirmacao do registro.
    """
    try:
        service = AuditService()
        result = service.log_event(
            action=request.action,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            user_id=request.user_id,
            details=request.details,
            severity=request.severity,
        )

        return StandardResponse(
            success=True,
            message="Evento registrado na trilha de auditoria",
            data=result,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dados invalidos: {str(e)}",
        )
    except Exception as e:
        logger.error("Erro ao registrar auditoria: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao registrar evento",
        )


@router.get(
    "/logs",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista eventos de auditoria",
    description="Retorna eventos de auditoria com filtros.",
)
async def list_audit_logs(
    resource_type: Optional[str] = Query(None, description="Tipo de recurso"),
    user_id: Optional[str] = Query(None, description="ID do usuario"),
    start_date: Optional[datetime] = Query(None, description="Data inicial"),
    end_date: Optional[datetime] = Query(None, description="Data final"),
    limit: int = Query(100, ge=1, le=1000, description="Limite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginacao"),
) -> StandardResponse:
    """
    Lista eventos de auditoria.

    Args:
        resource_type: Filtro por tipo de recurso.
        user_id: Filtro por usuario.
        start_date: Data inicial.
        end_date: Data final.
        limit: Limite de resultados.
        offset: Offset para paginacao.

    Returns:
        StandardResponse: Lista de eventos.
    """
    try:
        service = AuditService()
        result = service.query_logs(
            resource_type=resource_type,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

        return StandardResponse(
            success=True,
            message=f"Encontrados {result['total']} eventos",
            data=result,
        )

    except Exception as e:
        logger.error("Erro ao listar auditoria: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar eventos",
        )


@router.get(
    "/actions/list",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista acoes de auditoria",
    description="Retorna acoes de auditoria disponiveis.",
)
async def list_actions() -> StandardResponse:
    """
    Lista acoes de auditoria disponiveis.

    Returns:
        StandardResponse: Lista de acoes.
    """
    service = AuditService()
    actions = service.get_actions()

    return StandardResponse(
        success=True,
        message="Acoes de auditoria disponiveis",
        data={"actions": actions},
    )


@router.get(
    "/resource-types/list",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista tipos de recurso",
    description="Retorna tipos de recurso auditados.",
)
async def list_resource_types() -> StandardResponse:
    """
    Lista tipos de recurso auditados.

    Returns:
        StandardResponse: Lista de tipos de recurso.
    """
    service = AuditService()
    types = service.get_resource_types()

    return StandardResponse(
        success=True,
        message="Tipos de recurso disponiveis",
        data={"resource_types": types},
    )
