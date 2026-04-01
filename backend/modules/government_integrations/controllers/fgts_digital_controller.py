"""
Controller REST para FGTS Digital.

Endpoints para operações do FGTS Digital.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from core.auth.dependencies import CurrentActiveUser

from ..schemas.common import StandardResponse
from ..schemas.fgts_digital import (
    CalcularFolhaRequest,
    ConsultarDebitosRequest,
    ConsultarExtratoRequest,
    GerarGuiaMensalRequest,
    ImportarESocialRequest,
    RescisaoRequest,
    SimularSaqueRequest,
)
from ..services.fgts_digital_service import (
    FGTSDigitalService,
    get_fgts_digital_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fgts-digital", tags=["FGTS Digital"])


def get_service() -> FGTSDigitalService:
    """Dependency para obter o service."""
    return get_fgts_digital_service()


@router.get(
    "/status",
    response_model=StandardResponse,
    summary="Status do FGTS Digital",
    description="Retorna o status da configuração do FGTS Digital",
)
async def get_status(
    current_user: CurrentActiveUser, service: FGTSDigitalService = Depends(get_service)
) -> StandardResponse:
    """Retorna status da configuração."""
    try:
        status_data = service.validar_status()

        return StandardResponse(success=True, message="Status FGTS Digital obtido", data=status_data)

    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.get(
    "/categorias",
    response_model=StandardResponse,
    summary="Lista categorias",
    description="Retorna a lista de categorias de trabalhadores",
)
async def listar_categorias(
    current_user: CurrentActiveUser, service: FGTSDigitalService = Depends(get_service)
) -> StandardResponse:
    """Lista categorias de trabalhadores."""
    try:
        categorias = service.listar_categorias()

        return StandardResponse(success=True, message="Categorias listadas", data=categorias)

    except Exception as e:
        logger.error(f"Erro ao listar categorias: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.get(
    "/modalidades-saque",
    response_model=StandardResponse,
    summary="Lista modalidades de saque",
    description="Retorna a lista de modalidades de saque",
)
async def listar_modalidades_saque(
    current_user: CurrentActiveUser, service: FGTSDigitalService = Depends(get_service)
) -> StandardResponse:
    """Lista modalidades de saque."""
    try:
        modalidades = service.listar_modalidades_saque()

        return StandardResponse(success=True, message="Modalidades listadas", data=modalidades)

    except Exception as e:
        logger.error(f"Erro ao listar modalidades: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/calcular-folha",
    response_model=StandardResponse,
    summary="Calcular FGTS da folha",
    description="Calcula o FGTS da folha de pagamento",
)
async def calcular_folha(
    current_user: CurrentActiveUser, request: CalcularFolhaRequest, service: FGTSDigitalService = Depends(get_service)
) -> StandardResponse:
    """Calcula FGTS da folha."""
    try:
        trabalhadores = [t.model_dump() for t in request.trabalhadores]

        resultado = service.calcular_folha(
            competencia=request.competencia,
            trabalhadores=trabalhadores,
        )

        return StandardResponse(success=True, message=f"FGTS calculado: R$ {resultado['total_fgts']}", data=resultado)

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro no cálculo: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/importar-esocial",
    response_model=StandardResponse,
    summary="Importar do eSocial",
    description="Importa dados do eSocial para cálculo do FGTS",
)
async def importar_esocial(
    current_user: CurrentActiveUser, request: ImportarESocialRequest, service: FGTSDigitalService = Depends(get_service)
) -> StandardResponse:
    """Importa dados do eSocial."""
    try:
        resultado = service.importar_esocial(
            competencia=request.competencia,
            eventos_s1200=request.eventos_s1200,
        )

        return StandardResponse(
            success=True, message=f"Importados {resultado['quantidade_importados']} trabalhadores", data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro na importação: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/guia-mensal",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Gerar guia mensal",
    description="Gera guia de recolhimento mensal (GRFGTS) com PIX",
)
async def gerar_guia_mensal(
    current_user: CurrentActiveUser, request: GerarGuiaMensalRequest, service: FGTSDigitalService = Depends(get_service)
) -> StandardResponse:
    """Gera guia mensal."""
    try:
        trabalhadores = [t.model_dump() for t in request.trabalhadores]

        resultado = service.gerar_guia_mensal(
            competencia=request.competencia,
            trabalhadores=trabalhadores,
            data_vencimento=request.data_vencimento,
        )

        return StandardResponse(
            success=True, message=f"GRFGTS gerada: R$ {resultado['guia']['valor_total']}", data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro na geração: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/guia-rescisoria",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Gerar guia rescisória",
    description="Gera guia de recolhimento rescisório (GRRF) com PIX",
)
async def gerar_guia_rescisoria(
    current_user: CurrentActiveUser, request: RescisaoRequest, service: FGTSDigitalService = Depends(get_service)
) -> StandardResponse:
    """Gera guia rescisória."""
    try:
        resultado = service.gerar_guia_rescisoria(request.model_dump())

        return StandardResponse(
            success=True, message=f"GRRF gerada: R$ {resultado['guia']['valor_total']}", data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro na geração: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/debitos", response_model=StandardResponse, summary="Consultar débitos", description="Consulta débitos de FGTS"
)
async def consultar_debitos(
    current_user: CurrentActiveUser,
    request: ConsultarDebitosRequest,
    service: FGTSDigitalService = Depends(get_service),
) -> StandardResponse:
    """Consulta débitos."""
    try:
        resultado = service.consultar_debitos(
            competencia_inicio=request.competencia_inicio,
            competencia_fim=request.competencia_fim,
        )

        return StandardResponse(success=True, message=f"Encontrados {resultado['quantidade']} débitos", data=resultado)

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro na consulta: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/extrato",
    response_model=StandardResponse,
    summary="Consultar extrato",
    description="Consulta extrato do FGTS de um trabalhador",
)
async def consultar_extrato(
    current_user: CurrentActiveUser,
    request: ConsultarExtratoRequest,
    service: FGTSDigitalService = Depends(get_service),
) -> StandardResponse:
    """Consulta extrato do trabalhador."""
    try:
        resultado = service.consultar_extrato(
            cpf=request.cpf,
            pis_pasep=request.pis_pasep,
        )

        return StandardResponse(success=True, message="Extrato consultado", data=resultado)

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro na consulta: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/simular-saque", response_model=StandardResponse, summary="Simular saque", description="Simula saque do FGTS"
)
async def simular_saque(
    current_user: CurrentActiveUser, request: SimularSaqueRequest, service: FGTSDigitalService = Depends(get_service)
) -> StandardResponse:
    """Simula saque do FGTS."""
    try:
        resultado = service.simular_saque(
            cpf=request.cpf,
            modalidade=request.modalidade.value,
            valor_solicitado=str(request.valor_solicitado) if request.valor_solicitado else None,
        )

        return StandardResponse(success=True, message="Simulação realizada", data=resultado)

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro na simulação: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")


@router.post(
    "/relatorio-mensal",
    response_model=StandardResponse,
    summary="Relatório mensal",
    description="Gera relatório mensal de FGTS",
)
async def gerar_relatorio_mensal(
    current_user: CurrentActiveUser, request: CalcularFolhaRequest, service: FGTSDigitalService = Depends(get_service)
) -> StandardResponse:
    """Gera relatório mensal."""
    try:
        trabalhadores = [t.model_dump() for t in request.trabalhadores]

        resultado = service.gerar_relatorio_mensal(
            competencia=request.competencia,
            trabalhadores=trabalhadores,
        )

        return StandardResponse(
            success=True, message=f"Relatório gerado: {resultado['resumo']['total_geral']}", data=resultado
        )

    except ValueError as e:
        logger.warning(f"Erro de validação: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Erro no relatório: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro: {str(e)}")
