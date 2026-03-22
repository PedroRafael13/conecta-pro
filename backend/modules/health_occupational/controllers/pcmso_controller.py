"""
Controller PCMSO (NR-7) - Programa de Controle Medico de Saude Ocupacional
==========================================================================

Endpoints REST para exames medicos ocupacionais e ASO.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from core.database.session import get_sync_db_dependency
from modules.health_occupational.schemas.common import StandardResponse
from modules.health_occupational.schemas.pcmso import (
    ASORequest,
    ASOResponse,
    MedicalExamRequest,
    MedicalExamResponse,
    MedicalExamUpdateRequest,
)
from modules.health_occupational.services.pcmso_service import PCMSOService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pcmso", tags=["PCMSO - Exames Medicos (NR-7)"])


# Dependency para obter o service com DB session
def get_pcmso_service(db: Session = Depends(get_sync_db_dependency)) -> PCMSOService:
    """Retorna instancia do PCMSOService com DB session."""
    return PCMSOService(db=db)


# ==============================================================================
# Medical Exam Endpoints
# ==============================================================================


@router.post(
    "/exames/agendar",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agenda exame medico ocupacional",
    description="Agenda exame medico (admissional, periodico, demissional, etc).",
)
async def schedule_medical_exam(
    request: MedicalExamRequest,
    service: PCMSOService = Depends(get_pcmso_service),
) -> StandardResponse:
    """
    Agenda exame medico ocupacional.

    Args:
        request: Dados do agendamento.
        service: Service de PCMSO.

    Returns:
        StandardResponse: Confirmacao do agendamento.

    Raises:
        HTTPException: Se falhar o agendamento.
    """
    try:
        exam = service.schedule_exam(request)

        logger.info(
            "Exame agendado: funcionario=%s, tipo=%s, data=%s",
            request.funcionario_id,
            request.tipo_exame,
            request.data_agendamento,
        )

        return StandardResponse(
            success=True,
            message="Exame medico agendado com sucesso",
            data={
                "exame_id": str(exam.id),
                "funcionario_id": str(request.funcionario_id),
                "tipo_exame": request.tipo_exame,
                "data_agendamento": request.data_agendamento.isoformat(),
                "status": exam.status,
                "exames_complementares": request.exames_complementares,
            },
        )

    except ValueError as e:
        logger.warning("Erro de validacao no agendamento: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro de validacao: {str(e)}",
        )
    except Exception as e:
        logger.error("Erro ao agendar exame: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao agendar exame",
        )


@router.get(
    "/exames/{exame_id}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Busca exame por ID",
)
async def get_exam(
    exame_id: UUID = Path(..., description="ID do exame"),
    service: PCMSOService = Depends(get_pcmso_service),
) -> StandardResponse:
    """Busca exame medico por ID."""
    try:
        exam = service.get_exam(exame_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exame nao encontrado",
            )

        return StandardResponse(
            success=True,
            message="Exame encontrado",
            data=MedicalExamResponse.model_validate(exam).model_dump(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao buscar exame: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao buscar exame",
        )


@router.patch(
    "/exames/{exame_id}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualiza exame medico",
)
async def update_exam(
    exame_id: UUID,
    request: MedicalExamUpdateRequest,
    service: PCMSOService = Depends(get_pcmso_service),
) -> StandardResponse:
    """Atualiza dados de exame medico."""
    try:
        exam = service.update_exam(exame_id, request)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exame nao encontrado",
            )

        return StandardResponse(
            success=True,
            message="Exame atualizado com sucesso",
            data={"exame_id": str(exam.id)},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao atualizar exame: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar exame",
        )


@router.get(
    "/exames/funcionario/{funcionario_id}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista exames do funcionario",
    description="Retorna historico de exames de um funcionario.",
)
async def list_employee_exams(
    funcionario_id: UUID = Path(..., description="UUID do funcionario"),
    status_filter: str | None = Query(None, description="Filtrar por status"),
    tipo_filter: str | None = Query(None, description="Filtrar por tipo"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    service: PCMSOService = Depends(get_pcmso_service),
) -> StandardResponse:
    """Lista exames de um funcionario."""
    try:
        result = service.list_employee_exams(
            funcionario_id=funcionario_id,
            status_filter=status_filter,
            tipo_filter=tipo_filter,
            page=page,
            size=size,
        )

        return StandardResponse(
            success=True,
            message=f"Encontrados {result['total']} exames",
            data={
                "funcionario_id": str(funcionario_id),
                "exames": [MedicalExamResponse.model_validate(e).model_dump() for e in result["items"]],
                "total": result["total"],
                "page": result["page"],
                "size": result["size"],
            },
        )

    except Exception as e:
        logger.error("Erro ao listar exames: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar exames",
        )


@router.post(
    "/exames/{exame_id}/confirmar",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirma agendamento de exame",
)
async def confirm_exam(
    exame_id: UUID,
    service: PCMSOService = Depends(get_pcmso_service),
) -> StandardResponse:
    """Confirma agendamento de exame."""
    try:
        exam = service.confirm_exam(exame_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exame nao encontrado",
            )

        return StandardResponse(
            success=True,
            message="Exame confirmado",
            data={"exame_id": str(exam.id), "status": exam.status},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao confirmar exame: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno",
        )


@router.post(
    "/exames/{exame_id}/realizar",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Marca exame como realizado",
)
async def complete_exam(
    exame_id: UUID,
    service: PCMSOService = Depends(get_pcmso_service),
) -> StandardResponse:
    """Marca exame como realizado."""
    try:
        exam = service.complete_exam(exame_id)
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exame nao encontrado",
            )

        return StandardResponse(
            success=True,
            message="Exame marcado como realizado",
            data={
                "exame_id": str(exam.id),
                "status": exam.status,
                "data_realizacao": exam.data_realizacao.isoformat() if exam.data_realizacao else None,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao completar exame: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno",
        )


# ==============================================================================
# ASO Endpoints
# ==============================================================================


@router.post(
    "/aso/emitir",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Emite ASO (Atestado de Saude Ocupacional)",
    description="Emite ASO apos realizacao do exame medico.",
)
async def emit_aso(
    request: ASORequest,
    service: PCMSOService = Depends(get_pcmso_service),
) -> StandardResponse:
    """
    Emite ASO (Atestado de Saude Ocupacional).

    Args:
        request: Dados do ASO.
        service: Service de PCMSO.

    Returns:
        StandardResponse: ASO emitido.

    Raises:
        HTTPException: Se falhar a emissao.
    """
    try:
        aso = service.emit_aso(request)

        logger.info(
            "ASO emitido: numero=%s, exame=%s, resultado=%s",
            aso.numero_aso,
            request.exame_id,
            request.resultado,
        )

        return StandardResponse(
            success=True,
            message="ASO emitido com sucesso",
            data={
                "aso_id": str(aso.id),
                "numero_aso": aso.numero_aso,
                "exame_id": str(request.exame_id),
                "resultado": request.resultado,
                "restricoes": request.restricoes,
                "validade": f"{request.validade_dias} dias",
                "data_vencimento": aso.data_vencimento.isoformat(),
                "medico": request.medico_responsavel,
                "crm": request.crm,
                "data_emissao": aso.data_emissao.isoformat(),
            },
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro de validacao: {str(e)}",
        )
    except Exception as e:
        logger.error("Erro ao emitir ASO: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao emitir ASO",
        )


@router.get(
    "/aso/{aso_id}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Busca ASO por ID",
)
async def get_aso(
    aso_id: UUID,
    service: PCMSOService = Depends(get_pcmso_service),
) -> StandardResponse:
    """Busca ASO por ID."""
    try:
        aso = service.get_aso(aso_id)
        if not aso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ASO nao encontrado",
            )

        return StandardResponse(
            success=True,
            message="ASO encontrado",
            data=ASOResponse.model_validate(aso).model_dump(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao buscar ASO: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno",
        )


@router.get(
    "/vencimentos",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Lista ASOs a vencer",
    description="Retorna ASOs com vencimento proximo.",
)
async def list_expiring_asos(
    dias: int = Query(30, ge=1, le=180, description="Dias para vencimento"),
    service: PCMSOService = Depends(get_pcmso_service),
) -> StandardResponse:
    """Lista ASOs com vencimento proximo."""
    try:
        expiring = service.list_expiring_asos(days=dias)

        return StandardResponse(
            success=True,
            message=f"Encontrados {len(expiring)} ASOs a vencer em {dias} dias",
            data={
                "dias_antecedencia": dias,
                "asos_vencendo": expiring,
                "total": len(expiring),
            },
        )

    except Exception as e:
        logger.error("Erro ao listar ASOs a vencer: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar ASOs",
        )


@router.post(
    "/aso/{aso_id}/assinar",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Registra assinatura do funcionario no ASO",
)
async def sign_aso(
    aso_id: UUID,
    service: PCMSOService = Depends(get_pcmso_service),
) -> StandardResponse:
    """Registra assinatura do funcionario no ASO."""
    try:
        from modules.health_occupational.schemas.pcmso import ASOUpdateRequest

        aso = service.update_aso(aso_id, ASOUpdateRequest(assinatura_funcionario=True))
        if not aso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ASO nao encontrado",
            )

        return StandardResponse(
            success=True,
            message="Assinatura registrada",
            data={
                "aso_id": str(aso.id),
                "assinatura_funcionario": aso.assinatura_funcionario,
                "data_assinatura": aso.data_assinatura_funcionario.isoformat()
                if aso.data_assinatura_funcionario
                else None,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Erro ao registrar assinatura: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno",
        )


# ==============================================================================
# Statistics Endpoint
# ==============================================================================


@router.get(
    "/estatisticas",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Estatisticas do PCMSO",
)
async def get_statistics(
    service: PCMSOService = Depends(get_pcmso_service),
) -> StandardResponse:
    """Retorna estatisticas do PCMSO."""
    try:
        stats = service.get_statistics()

        return StandardResponse(
            success=True,
            message="Estatisticas do PCMSO",
            data=stats,
        )

    except Exception as e:
        logger.error("Erro ao obter estatisticas: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno",
        )
