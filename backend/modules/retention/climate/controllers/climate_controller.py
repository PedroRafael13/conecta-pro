"""
Controller (endpoints) para Pesquisa de Clima Operacional.

Define endpoints REST para gestao de pesquisas de clima,
coleta de respostas e visualizacao de resultados.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import CurrentActiveUser
from core.database import get_db
from core.logging import logger
from modules.retention.climate.models.climate_models import AlertSeverity, EntityType
from modules.retention.climate.repositories.climate_repository import (
    ClimateAlertRepository,
    ClimateSurveyRepository,
)
from modules.retention.climate.schemas.climate_schemas import (
    AlertListResponse,
    AlertResolve,
    AlertResponse,
    CalculationRequest,
    CalculationResult,
    ClimateByEquipe,
    ClimateByEmpresa,
    ClimateByPosto,
    ClimateDashboard,
    ClimateScoreListResponse,
    ClimateScoreResponse,
    ClimateTrend,
    QuestionSchema,
    ResponseConfirmation,
    ResponseCreate,
    SurveyActiveResponse,
    SurveyCreate,
    SurveyListResponse,
    SurveyResponse,
    SurveyUpdate,
)
from modules.retention.climate.services.climate_service import ClimateService

router = APIRouter(
    prefix="/retention/climate",
    tags=["Retention - Climate Survey"],
)


# =============================================================================
# Dependency
# =============================================================================


async def get_climate_service(db: AsyncSession = Depends(get_db)) -> ClimateService:
    """Obtem instancia do ClimateService."""
    return ClimateService(db)


# =============================================================================
# Survey Endpoints
# =============================================================================


@router.get(
    "/surveys",
    response_model=SurveyListResponse,
    summary="Lista pesquisas de clima",
    description="Retorna lista paginada de pesquisas de clima.",
)
async def list_surveys(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Pagina atual"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por pagina"),
    empresa_id: Optional[str] = Query(None, description="Filtrar por empresa"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status"),
) -> SurveyListResponse:
    """Lista pesquisas de clima com filtros e paginacao."""
    repo = ClimateSurveyRepository(db)

    surveys, total = await repo.list(
        empresa_id=empresa_id,
        ativo=ativo,
        page=page,
        page_size=page_size,
    )

    total_pages = (total + page_size - 1) // page_size

    logger.debug(f"Listadas {len(surveys)} pesquisas de clima")

    return SurveyListResponse(
        items=[SurveyResponse.model_validate(s) for s in surveys],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post(
    "/surveys",
    response_model=SurveyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria pesquisa de clima",
    description="Cria uma nova pesquisa de clima organizacional.",
)
async def create_survey(
    data: SurveyCreate,
    current_user: CurrentActiveUser,
    service: ClimateService = Depends(get_climate_service),
) -> SurveyResponse:
    """Cria nova pesquisa de clima."""
    survey = await service.criar_pesquisa(data, created_by=current_user.id)

    logger.info(f"Pesquisa de clima criada por {current_user.email}: {survey.id}")

    return SurveyResponse.model_validate(survey)


@router.get(
    "/surveys/ativa",
    response_model=SurveyActiveResponse,
    summary="Obtem pesquisa ativa",
    description="Retorna a pesquisa de clima ativa para responder.",
)
async def get_active_survey(
    current_user: CurrentActiveUser,
    service: ClimateService = Depends(get_climate_service),
    empresa_id: Optional[str] = Query(None, description="ID da empresa"),
) -> SurveyActiveResponse:
    """Busca pesquisa ativa para responder."""
    survey = await service.get_pesquisa_ativa(empresa_id)

    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma pesquisa de clima ativa no momento",
        )

    # Converter perguntas para schema
    perguntas = [
        QuestionSchema(**p) if isinstance(p, dict) else p for p in survey.perguntas
    ]

    # Tempo estimado: 30 segundos por pergunta
    tempo_estimado = max(3, len(perguntas) * 0.5)

    return SurveyActiveResponse(
        id=survey.id,
        nome=survey.nome,
        descricao=survey.descricao,
        perguntas=perguntas,
        total_perguntas=len(perguntas),
        tempo_estimado_minutos=int(tempo_estimado),
    )


@router.get(
    "/surveys/perguntas-padrao",
    response_model=List[QuestionSchema],
    summary="Lista perguntas padrao",
    description="Retorna as perguntas padrao do sistema.",
)
async def get_default_questions(
    current_user: CurrentActiveUser,
    service: ClimateService = Depends(get_climate_service),
) -> List[QuestionSchema]:
    """Retorna perguntas padrao do sistema."""
    return await service.get_perguntas_padrao()


@router.get(
    "/surveys/{survey_id}",
    response_model=SurveyResponse,
    summary="Obtem pesquisa por ID",
)
async def get_survey(
    survey_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> SurveyResponse:
    """Busca pesquisa por ID."""
    repo = ClimateSurveyRepository(db)
    survey = await repo.get_by_id(survey_id)

    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pesquisa nao encontrada",
        )

    return SurveyResponse.model_validate(survey)


@router.patch(
    "/surveys/{survey_id}",
    response_model=SurveyResponse,
    summary="Atualiza pesquisa",
)
async def update_survey(
    survey_id: str,
    data: SurveyUpdate,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> SurveyResponse:
    """Atualiza uma pesquisa de clima."""
    repo = ClimateSurveyRepository(db)
    survey = await repo.update(survey_id, data)

    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pesquisa nao encontrada",
        )

    logger.info(f"Pesquisa atualizada por {current_user.email}: {survey.id}")

    return SurveyResponse.model_validate(survey)


@router.delete(
    "/surveys/{survey_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Desativa pesquisa",
)
async def delete_survey(
    survey_id: str,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Desativa uma pesquisa (soft delete)."""
    repo = ClimateSurveyRepository(db)
    deleted = await repo.delete(survey_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pesquisa nao encontrada",
        )

    logger.info(f"Pesquisa desativada por {current_user.email}: {survey_id}")


# =============================================================================
# Response Endpoints
# =============================================================================


@router.post(
    "/respond",
    response_model=ResponseConfirmation,
    status_code=status.HTTP_201_CREATED,
    summary="Responde pesquisa de clima",
    description="Registra resposta anonima de pesquisa de clima.",
)
async def respond_survey(
    data: ResponseCreate,
    request: Request,
    service: ClimateService = Depends(get_climate_service),
) -> ResponseConfirmation:
    """
    Registra resposta de pesquisa de clima.

    A resposta e anonimizada - o ID do funcionario e convertido em hash.
    """
    try:
        # Obter IP e User-Agent para hash
        ip = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")

        result = await service.responder_pesquisa(data, ip=ip, user_agent=user_agent)

        logger.info(f"Resposta de clima registrada: score={result.score}")

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# =============================================================================
# Results Endpoints
# =============================================================================


@router.get(
    "/results/posto/{posto_id}",
    response_model=ClimateByPosto,
    summary="Resultados por posto",
    description="Retorna resultados de clima de um posto especifico.",
)
async def get_results_by_posto(
    posto_id: str,
    current_user: CurrentActiveUser,
    service: ClimateService = Depends(get_climate_service),
    periodo: Optional[str] = Query(
        None,
        pattern=r"^\d{4}-\d{2}$",
        description="Periodo YYYY-MM (default: atual)",
    ),
) -> ClimateByPosto:
    """Retorna resultados de clima de um posto."""
    result = await service.get_results_by_posto(posto_id, periodo)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nenhum resultado encontrado para o posto no periodo",
        )

    return result


@router.get(
    "/results/equipe/{equipe_id}",
    response_model=ClimateByEquipe,
    summary="Resultados por equipe",
    description="Retorna resultados de clima de uma equipe especifica.",
)
async def get_results_by_equipe(
    equipe_id: str,
    current_user: CurrentActiveUser,
    service: ClimateService = Depends(get_climate_service),
    periodo: Optional[str] = Query(
        None,
        pattern=r"^\d{4}-\d{2}$",
        description="Periodo YYYY-MM (default: atual)",
    ),
) -> ClimateByEquipe:
    """Retorna resultados de clima de uma equipe."""
    result = await service.get_results_by_equipe(equipe_id, periodo)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum resultado encontrado para a equipe no periodo",
        )

    return result


@router.get(
    "/results/empresa",
    response_model=ClimateByEmpresa,
    summary="Resultados da empresa",
    description="Retorna resultados de clima consolidados da empresa.",
)
async def get_results_empresa(
    current_user: CurrentActiveUser,
    service: ClimateService = Depends(get_climate_service),
    empresa_id: Optional[str] = Query(None, description="ID da empresa"),
    periodo: Optional[str] = Query(
        None,
        pattern=r"^\d{4}-\d{2}$",
        description="Periodo YYYY-MM (default: atual)",
    ),
) -> ClimateByEmpresa:
    """Retorna resultados consolidados da empresa."""
    # Usar empresa_id do usuario se nao fornecido
    empresa = empresa_id or getattr(current_user, "empresa_id", None)

    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="empresa_id e obrigatorio",
        )

    result = await service.get_results_empresa(empresa, periodo)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum resultado encontrado para a empresa no periodo",
        )

    return result


# =============================================================================
# Trends Endpoints
# =============================================================================


@router.get(
    "/trends/{entidade_tipo}/{entidade_id}",
    response_model=ClimateTrend,
    summary="Tendencia de clima",
    description="Retorna evolucao historica do clima de uma entidade.",
)
async def get_trends(
    entidade_tipo: EntityType,
    entidade_id: str,
    current_user: CurrentActiveUser,
    service: ClimateService = Depends(get_climate_service),
    periodos: int = Query(6, ge=2, le=24, description="Quantidade de periodos"),
) -> ClimateTrend:
    """Retorna tendencia historica de clima."""
    return await service.get_tendencias(entidade_tipo, entidade_id, periodos)


# =============================================================================
# Dashboard Endpoints
# =============================================================================


@router.get(
    "/dashboard",
    response_model=ClimateDashboard,
    summary="Dashboard de clima",
    description="Retorna visao geral do clima organizacional.",
)
async def get_dashboard(
    current_user: CurrentActiveUser,
    service: ClimateService = Depends(get_climate_service),
    empresa_id: Optional[str] = Query(None, description="Filtrar por empresa"),
) -> ClimateDashboard:
    """Retorna dashboard geral de clima."""
    return await service.get_dashboard(empresa_id)


# =============================================================================
# Alerts Endpoints
# =============================================================================


@router.get(
    "/alerts",
    response_model=AlertListResponse,
    summary="Lista alertas de clima",
    description="Retorna alertas ativos de clima organizacional.",
)
async def list_alerts(
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
    empresa_id: Optional[str] = Query(None, description="Filtrar por empresa"),
    severidade: Optional[AlertSeverity] = Query(None, description="Filtrar por severidade"),
    limit: int = Query(50, ge=1, le=200, description="Limite de resultados"),
) -> AlertListResponse:
    """Lista alertas ativos."""
    repo = ClimateAlertRepository(db)

    alerts = await repo.list_active(empresa_id, severidade, limit)
    counts = await repo.count_by_severidade(empresa_id)

    return AlertListResponse(
        items=[AlertResponse.model_validate(a) for a in alerts],
        total=len(alerts),
        total_criticos=counts.get(AlertSeverity.CRITICA.value, 0),
        total_altos=counts.get(AlertSeverity.ALTA.value, 0),
        total_medios=counts.get(AlertSeverity.MEDIA.value, 0),
        total_baixos=counts.get(AlertSeverity.BAIXA.value, 0),
    )


@router.post(
    "/alerts/{alert_id}/resolve",
    response_model=AlertResponse,
    summary="Resolve alerta",
    description="Marca um alerta como resolvido.",
)
async def resolve_alert(
    alert_id: str,
    data: AlertResolve,
    current_user: CurrentActiveUser,
    db: AsyncSession = Depends(get_db),
) -> AlertResponse:
    """Resolve um alerta de clima."""
    repo = ClimateAlertRepository(db)

    alert = await repo.resolve(
        alert_id,
        resolvido_por=current_user.id,
        notas_resolucao=data.notas_resolucao,
    )

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta nao encontrado",
        )

    logger.info(f"Alerta resolvido por {current_user.email}: {alert_id}")

    return AlertResponse.model_validate(alert)


# =============================================================================
# Calculation Endpoints
# =============================================================================


@router.post(
    "/calculate",
    response_model=CalculationResult,
    summary="Calcula scores do periodo",
    description="Executa calculo de scores agregados para um periodo.",
)
async def calculate_scores(
    data: CalculationRequest,
    current_user: CurrentActiveUser,
    service: ClimateService = Depends(get_climate_service),
) -> CalculationResult:
    """
    Executa calculo de scores para um periodo.

    Este endpoint pode ser chamado manualmente ou por um job agendado.
    """
    logger.info(
        f"Calculo de scores iniciado por {current_user.email} para periodo {data.periodo}"
    )

    result = await service.calcular_scores_periodo(
        periodo=data.periodo,
        empresa_id=data.empresa_id,
        recalcular=data.recalcular,
    )

    return result


@router.post(
    "/check-alerts",
    response_model=dict,
    summary="Verifica quedas e gera alertas",
    description="Detecta quedas significativas e gera alertas.",
)
async def check_alerts(
    current_user: CurrentActiveUser,
    service: ClimateService = Depends(get_climate_service),
    empresa_id: Optional[str] = Query(None, description="Filtrar por empresa"),
) -> dict:
    """Verifica quedas e gera alertas."""
    alertas = await service.verificar_quedas(empresa_id)

    return {
        "success": True,
        "alertas_gerados": len(alertas),
        "message": f"{len(alertas)} alertas gerados",
    }


# =============================================================================
# Health Check
# =============================================================================


@router.get(
    "/health",
    response_model=dict,
    summary="Health check do modulo",
    include_in_schema=False,
)
async def health_check() -> dict:
    """Health check do modulo de clima."""
    return {
        "status": "healthy",
        "module": "climate",
        "timestamp": datetime.now().isoformat(),
    }
