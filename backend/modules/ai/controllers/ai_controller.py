"""AI Controller - Endpoints REST para IA.

Sprint 34 - AI Predictions.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from core.auth.dependencies import CurrentActiveUser
from core.database.session import get_db
from modules.ai.models.anomaly_log import AnomalySeverity, AnomalyStatus
from modules.ai.models.ml_model import ModelStatus, ModelType
from modules.ai.models.prediction import PredictionStatus, PredictionType
from modules.ai.models.recommendation import RecommendationType
from modules.ai.repositories.ai_repository import AIRepository
from modules.ai.schemas.ai_schemas import (
    AnomalyCreate,
    AnomalyResponse,
    ChurnPredictionRequest,
    ChurnPredictionResponse,
    FeatureStoreCreate,
    FeatureStoreResponse,
    ForecastRequest,
    ForecastResponse,
    MLModelCreate,
    MLModelResponse,
    MLModelUpdate,
    ModelStatsResponse,
    PredictionCreate,
    PredictionFeedback,
    PredictionListResponse,
    PredictionResponse,
    PredictionStatsResponse,
    RecommendationListResponse,
    RecommendationRequest,
    RecommendationResponse,
    TrainingJobCreate,
    TrainingJobResponse,
)
from modules.ai.services.anomaly_detector import AnomalyDetector
from modules.ai.services.churn_predictor import ChurnFactors, ChurnPredictor
from modules.ai.services.forecast_service import ForecastService
from modules.ai.services.prediction_service import PredictionService
from modules.ai.services.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Predictions"])


# ============ Prediction Endpoints ============


@router.post(
    "/predictions",
    response_model=PredictionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria nova previsao",
)
async def create_prediction(
    data: PredictionCreate,
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
) -> PredictionResponse:
    """Cria uma nova previsao."""
    service = PredictionService(db)

    prediction = await service.create_prediction(
        tenant_id=current_user.tenant_id,
        prediction_type=data.prediction_type,
        entity_type=data.entity_type,
        entity_id=data.entity_id,
        model_id=data.model_id,
        features=data.features,
        valid_days=data.valid_days,
        requested_by=current_user.id,
        tags=data.tags,
    )

    return PredictionResponse.model_validate(prediction)


@router.get(
    "/predictions",
    response_model=PredictionListResponse,
    summary="Lista previsoes",
)
async def list_predictions(
    prediction_type: PredictionType | None = None,
    status_filter: PredictionStatus | None = Query(None, alias="status"),
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
) -> PredictionListResponse:
    """Lista previsoes com filtros."""
    repo = AIRepository(db)

    skip = (page - 1) * page_size
    items, total = await repo.list_predictions(
        tenant_id=current_user.tenant_id,
        prediction_type=prediction_type,
        status=status_filter,
        entity_type=entity_type,
        entity_id=entity_id,
        skip=skip,
        limit=page_size,
    )

    return PredictionListResponse(
        items=[PredictionResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/predictions/{prediction_id}",
    response_model=PredictionResponse,
    summary="Busca previsao por ID",
)
async def get_prediction(
    prediction_id: UUID,
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
) -> PredictionResponse:
    """Busca previsao por ID."""
    repo = AIRepository(db)

    prediction = await repo.get_prediction(prediction_id, current_user.tenant_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Previsao nao encontrada",
        )

    return PredictionResponse.model_validate(prediction)


@router.post(
    "/predictions/{prediction_id}/feedback",
    response_model=PredictionResponse,
    summary="Adiciona feedback a previsao",
)
async def add_prediction_feedback(
    prediction_id: UUID,
    data: PredictionFeedback,
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
) -> PredictionResponse:
    """Adiciona feedback real a uma previsao."""
    service = PredictionService(db)
    repo = AIRepository(db)

    prediction = await repo.get_prediction(prediction_id, current_user.tenant_id)
    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Previsao nao encontrada",
        )

    updated = await service.add_feedback(
        prediction=prediction,
        actual_value=data.actual_value,
        actual_label=data.actual_label,
        user_id=current_user.id,
        notes=data.notes,
    )

    return PredictionResponse.model_validate(updated)


@router.get(
    "/predictions/stats/summary",
    response_model=PredictionStatsResponse,
    summary="Estatisticas de previsoes",
)
async def get_prediction_stats(
    days: int = Query(30, ge=1, le=365),
    prediction_type: PredictionType | None = None,
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
) -> PredictionStatsResponse:
    """Retorna estatisticas de previsoes."""
    service = PredictionService(db)

    stats = await service.get_prediction_stats(
        tenant_id=current_user.tenant_id,
        days=days,
        prediction_type=prediction_type,
    )

    return PredictionStatsResponse(**stats)


# ============ Churn Prediction Endpoints ============


@router.post(
    "/churn/predict",
    response_model=ChurnPredictionResponse,
    summary="Preve churn de cliente",
)
async def predict_churn(
    data: ChurnPredictionRequest,
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
) -> ChurnPredictionResponse:
    """Preve probabilidade de churn para um cliente."""
    predictor = ChurnPredictor(db)

    # Monta fatores se fornecidos
    factors = None
    if any(
        [
            data.days_since_last_interaction,
            data.interaction_frequency,
            data.nps_score,
            data.contract_value,
        ]
    ):
        factors = ChurnFactors(
            days_since_last_interaction=data.days_since_last_interaction or 0,
            interaction_frequency=data.interaction_frequency or 0,
            support_tickets_count=data.support_tickets_count or 0,
            payment_delays_count=data.payment_delays_count or 0,
            nps_score=data.nps_score,
            csat_score=data.csat_score,
            contract_value=data.contract_value or 0,
            contract_age_months=data.contract_age_months or 0,
            days_until_renewal=data.days_until_renewal,
            feature_usage_rate=data.feature_usage_rate or 0,
        )

    result = await predictor.predict_churn(
        tenant_id=current_user.tenant_id,
        client_id=data.client_id,
        factors=factors,
    )

    return ChurnPredictionResponse(
        client_id=data.client_id,
        churn_probability=result.churn_probability,
        churn_risk_level=result.churn_risk_level,
        confidence=result.confidence,
        main_factors=result.main_factors,
        recommendations=result.recommendations,
        expected_churn_date=result.expected_churn_date,
        lifetime_value_at_risk=result.lifetime_value_at_risk,
    )


# ============ Forecast Endpoints ============


@router.post(
    "/forecast",
    response_model=ForecastResponse,
    summary="Gera forecast",
)
async def generate_forecast(
    data: ForecastRequest,
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
) -> ForecastResponse:
    """Gera forecast de receita, despesa ou demanda."""
    service = ForecastService(db)

    if data.forecast_type == "revenue":
        result = await service.forecast_revenue(
            tenant_id=current_user.tenant_id,
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            periods=data.periods,
            period_type=data.period_type,
            confidence_level=data.confidence_level,
        )
    elif data.forecast_type == "expense":
        result = await service.forecast_expense(
            tenant_id=current_user.tenant_id,
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            periods=data.periods,
            period_type=data.period_type,
            confidence_level=data.confidence_level,
        )
    else:  # demand
        result = await service.forecast_demand(
            tenant_id=current_user.tenant_id,
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            periods=data.periods,
            period_type=data.period_type,
            confidence_level=data.confidence_level,
        )

    return ForecastResponse(
        period_start=result.period_start,
        period_end=result.period_end,
        total_value=result.total_value,
        avg_value=result.avg_value,
        min_value=result.min_value,
        max_value=result.max_value,
        trend=result.trend,
        confidence=result.confidence,
        scenarios=result.scenarios,
        forecasts=[
            {
                "date": f.date.isoformat(),
                "value": f.value,
                "lower_bound": f.lower_bound,
                "upper_bound": f.upper_bound,
                "confidence": f.confidence,
                "trend": f.trend,
                "seasonality_factor": f.seasonality_factor,
            }
            for f in result.forecasts
        ],
    )


# ============ Anomaly Detection Endpoints ============


@router.post(
    "/anomalies/detect",
    response_model=AnomalyResponse,
    summary="Detecta anomalia",
)
async def detect_anomaly(
    data: AnomalyCreate,
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
) -> AnomalyResponse:
    """Detecta anomalia em um valor."""
    detector = AnomalyDetector(db)

    result = await detector.detect_anomaly(
        tenant_id=current_user.tenant_id,
        entity_type=data.entity_type,
        entity_id=data.entity_id,
        field=data.field,
        value=data.value,
        historical_values=data.historical_values,
        context=data.context,
    )

    return AnomalyResponse(
        is_anomaly=result.is_anomaly,
        anomaly_type=result.anomaly_type,
        severity=result.severity,
        anomaly_score=result.anomaly_score,
        confidence=result.confidence,
        observed_value=result.observed_value,
        expected_value=result.expected_value,
        expected_range=result.expected_range,
        deviation_score=result.deviation_score,
        explanation=result.explanation,
        contributing_factors=result.contributing_factors,
    )


@router.get(
    "/anomalies",
    summary="Lista anomalias",
)
async def list_anomalies(
    entity_type: str | None = None,
    severity: AnomalySeverity | None = None,
    status_filter: AnomalyStatus | None = Query(None, alias="status"),
    days: int = Query(30, ge=1, le=365),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
):
    """Lista anomalias detectadas."""
    repo = AIRepository(db)

    skip = (page - 1) * page_size
    items, total = await repo.list_anomalies(
        tenant_id=current_user.tenant_id,
        entity_type=entity_type,
        severity=severity,
        status=status_filter,
        days=days,
        skip=skip,
        limit=page_size,
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


# ============ Recommendation Endpoints ============


@router.post(
    "/recommendations",
    response_model=RecommendationListResponse,
    summary="Gera recomendacoes",
)
async def get_recommendations(
    data: RecommendationRequest,
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
) -> RecommendationListResponse:
    """Gera recomendacoes para uma entidade."""
    engine = RecommendationEngine(db)

    result = await engine.get_recommendations(
        tenant_id=current_user.tenant_id,
        target_entity_type=data.target_entity_type,
        target_entity_id=data.target_entity_id,
        recommendation_type=data.recommendation_type,
        limit=data.limit,
        context=data.context,
        algorithm=data.algorithm,
    )

    # Busca recomendacoes salvas
    repo = AIRepository(db)
    saved_recs, _ = await repo.list_recommendations(
        tenant_id=current_user.tenant_id,
        target_entity_type=data.target_entity_type,
        target_entity_id=data.target_entity_id,
        recommendation_type=data.recommendation_type,
        only_valid=True,
        limit=data.limit,
    )

    return RecommendationListResponse(
        recommendations=[RecommendationResponse.model_validate(r) for r in saved_recs],
        algorithm=result.algorithm,
        total_candidates=result.total_candidates,
        processing_time_ms=result.processing_time_ms,
    )


@router.get(
    "/recommendations/{entity_type}/{entity_id}",
    summary="Lista recomendacoes para entidade",
)
async def list_recommendations_for_entity(
    entity_type: str,
    entity_id: UUID,
    recommendation_type: RecommendationType | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
):
    """Lista recomendacoes para uma entidade."""
    repo = AIRepository(db)

    skip = (page - 1) * page_size
    items, total = await repo.list_recommendations(
        tenant_id=current_user.tenant_id,
        target_entity_type=entity_type,
        target_entity_id=entity_id,
        recommendation_type=recommendation_type,
        only_valid=True,
        skip=skip,
        limit=page_size,
    )

    return {
        "items": [RecommendationResponse.model_validate(r) for r in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post(
    "/recommendations/{recommendation_id}/interaction",
    summary="Registra interacao com recomendacao",
)
async def record_recommendation_interaction(
    recommendation_id: UUID,
    interaction_type: str = Query(..., description="shown, clicked, accepted, rejected"),
    feedback: str | None = None,
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
):
    """Registra interacao com recomendacao."""
    engine = RecommendationEngine(db)

    result = await engine.record_interaction(
        recommendation_id=recommendation_id,
        interaction_type=interaction_type,
        feedback=feedback,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recomendacao nao encontrada",
        )

    return {"status": "ok", "new_status": result.status.value}


# ============ ML Model Endpoints ============


@router.post(
    "/models",
    response_model=MLModelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria modelo",
)
async def create_model(
    data: MLModelCreate,
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
) -> MLModelResponse:
    """Cria novo modelo de ML."""
    from modules.ai.models.ml_model import MLModel

    repo = AIRepository(db)

    # Verifica se slug ja existe
    existing = await repo.get_model_by_slug(current_user.tenant_id, data.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ja existe um modelo com este slug",
        )

    model = MLModel(
        tenant_id=current_user.tenant_id,
        name=data.name,
        slug=data.slug,
        description=data.description,
        model_type=data.model_type,
        algorithm=data.algorithm,
        framework=data.framework,
        hyperparameters=data.hyperparameters,
        input_features=data.input_features,
        target_variable=data.target_variable,
        prediction_threshold=data.prediction_threshold,
        confidence_threshold=data.confidence_threshold,
        tags=data.tags,
        created_by=current_user.id,
    )

    created = await repo.create_model(model)
    return MLModelResponse.model_validate(created)


@router.get(
    "/models",
    summary="Lista modelos",
)
async def list_models(
    model_type: ModelType | None = None,
    status_filter: ModelStatus | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
):
    """Lista modelos de ML."""
    repo = AIRepository(db)

    skip = (page - 1) * page_size
    items, total = await repo.list_models(
        tenant_id=current_user.tenant_id,
        model_type=model_type,
        status=status_filter,
        skip=skip,
        limit=page_size,
    )

    return {
        "items": [MLModelResponse.model_validate(m) for m in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get(
    "/models/{model_id}",
    response_model=MLModelResponse,
    summary="Busca modelo por ID",
)
async def get_model(
    model_id: UUID,
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
) -> MLModelResponse:
    """Busca modelo por ID."""
    repo = AIRepository(db)

    model = await repo.get_model(model_id, current_user.tenant_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo nao encontrado",
        )

    return MLModelResponse.model_validate(model)


@router.patch(
    "/models/{model_id}",
    response_model=MLModelResponse,
    summary="Atualiza modelo",
)
async def update_model(
    model_id: UUID,
    data: MLModelUpdate,
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
) -> MLModelResponse:
    """Atualiza modelo."""
    repo = AIRepository(db)

    model = await repo.get_model(model_id, current_user.tenant_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo nao encontrado",
        )

    # Atualiza campos
    if data.name is not None:
        model.name = data.name
    if data.description is not None:
        model.description = data.description
    if data.hyperparameters is not None:
        model.hyperparameters = data.hyperparameters
    if data.prediction_threshold is not None:
        model.prediction_threshold = data.prediction_threshold
    if data.confidence_threshold is not None:
        model.confidence_threshold = data.confidence_threshold
    if data.auto_retrain is not None:
        model.auto_retrain = data.auto_retrain
    if data.tags is not None:
        model.tags = data.tags

    model.updated_by = current_user.id

    updated = await repo.update_model(model)
    return MLModelResponse.model_validate(updated)


@router.post(
    "/models/{model_id}/deploy",
    response_model=MLModelResponse,
    summary="Faz deploy do modelo",
)
async def deploy_model(
    model_id: UUID,
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
) -> MLModelResponse:
    """Faz deploy de um modelo."""
    repo = AIRepository(db)

    model = await repo.get_model(model_id, current_user.tenant_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo nao encontrado",
        )

    if model.status != ModelStatus.READY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Modelo precisa estar pronto para deploy",
        )

    model.deploy()
    updated = await repo.update_model(model)

    return MLModelResponse.model_validate(updated)


@router.get(
    "/models/{model_id}/stats",
    response_model=ModelStatsResponse,
    summary="Estatisticas do modelo",
)
async def get_model_stats(
    model_id: UUID,
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
) -> ModelStatsResponse:
    """Retorna estatisticas do modelo."""
    repo = AIRepository(db)

    stats = await repo.get_model_stats(current_user.tenant_id, model_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo nao encontrado",
        )

    return ModelStatsResponse(**stats)


# ============ Training Job Endpoints ============


@router.post(
    "/training-jobs",
    response_model=TrainingJobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria job de treinamento",
)
async def create_training_job(
    data: TrainingJobCreate,
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
) -> TrainingJobResponse:
    """Cria job de treinamento."""
    from modules.ai.models.training_job import TrainingJob

    repo = AIRepository(db)

    # Verifica se modelo existe
    model = await repo.get_model(data.model_id, current_user.tenant_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modelo nao encontrado",
        )

    job = TrainingJob(
        tenant_id=current_user.tenant_id,
        model_id=data.model_id,
        name=data.name,
        description=data.description,
        config=data.config,
        hyperparameters=data.hyperparameters,
        feature_store_id=data.feature_store_id,
        validation_split=data.validation_split,
        test_split=data.test_split,
        cv_folds=data.cv_folds,
        timeout_seconds=data.timeout_seconds,
        created_by=current_user.id,
    )

    created = await repo.create_training_job(job)
    return TrainingJobResponse.model_validate(created)


@router.get(
    "/training-jobs",
    summary="Lista jobs de treinamento",
)
async def list_training_jobs(
    model_id: UUID | None = None,
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
):
    """Lista jobs de treinamento."""
    repo = AIRepository(db)

    skip = (page - 1) * page_size
    items, total = await repo.list_training_jobs(
        tenant_id=current_user.tenant_id,
        model_id=model_id,
        status=status_filter,
        skip=skip,
        limit=page_size,
    )

    return {
        "items": [TrainingJobResponse.model_validate(j) for j in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get(
    "/training-jobs/{job_id}",
    response_model=TrainingJobResponse,
    summary="Busca job por ID",
)
async def get_training_job(
    job_id: UUID,
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
) -> TrainingJobResponse:
    """Busca job de treinamento por ID."""
    repo = AIRepository(db)

    job = await repo.get_training_job(job_id, current_user.tenant_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job nao encontrado",
        )

    return TrainingJobResponse.model_validate(job)


@router.post(
    "/training-jobs/{job_id}/cancel",
    response_model=TrainingJobResponse,
    summary="Cancela job",
)
async def cancel_training_job(
    job_id: UUID,
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
) -> TrainingJobResponse:
    """Cancela job de treinamento."""
    repo = AIRepository(db)

    job = await repo.get_training_job(job_id, current_user.tenant_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job nao encontrado",
        )

    if not job.is_running:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job nao esta em execucao",
        )

    job.cancel(str(current_user.id))
    updated = await repo.update_training_job(job)

    return TrainingJobResponse.model_validate(updated)


# ============ Feature Store Endpoints ============


@router.post(
    "/feature-stores",
    response_model=FeatureStoreResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cria feature store",
)
async def create_feature_store(
    data: FeatureStoreCreate,
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
) -> FeatureStoreResponse:
    """Cria feature store."""
    from modules.ai.models.feature_store import FeatureStore

    repo = AIRepository(db)

    store = FeatureStore(
        tenant_id=current_user.tenant_id,
        name=data.name,
        slug=data.slug,
        description=data.description,
        entity_type=data.entity_type,
        data_source=data.data_source,
        refresh_frequency=data.refresh_frequency,
        tags=data.tags,
        created_by=current_user.id,
    )

    created = await repo.create_feature_store(store)
    return FeatureStoreResponse.model_validate(created)


@router.get(
    "/feature-stores",
    summary="Lista feature stores",
)
async def list_feature_stores(
    entity_type: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
):
    """Lista feature stores."""
    repo = AIRepository(db)

    skip = (page - 1) * page_size
    items, total = await repo.list_feature_stores(
        tenant_id=current_user.tenant_id,
        entity_type=entity_type,
        skip=skip,
        limit=page_size,
    )

    return {
        "items": [FeatureStoreResponse.model_validate(s) for s in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get(
    "/feature-stores/{store_id}",
    response_model=FeatureStoreResponse,
    summary="Busca feature store por ID",
)
async def get_feature_store(
    store_id: UUID,
    current_user: CurrentActiveUser = ...,  # Required
    db=Depends(get_db),
) -> FeatureStoreResponse:
    """Busca feature store por ID."""
    repo = AIRepository(db)

    store = await repo.get_feature_store(store_id, current_user.tenant_id)
    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feature store nao encontrado",
        )

    return FeatureStoreResponse.model_validate(store)
