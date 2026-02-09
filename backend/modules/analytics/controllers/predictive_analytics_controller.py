"""Controller para Predictive Analytics API."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from modules.analytics.ml.features.feature_store import FeatureStore
from modules.analytics.ml.registry.model_registry import ModelRegistry, ModelStage
from modules.analytics.models.churn.churn_predictor import ChurnPredictor, ChurnRiskLevel
from modules.analytics.models.forecasting.sales_forecaster import (
    ForecastGranularity,
    SalesForecaster,
)
from modules.analytics.models.fraud.fraud_detector import (
    AlertStatus,
    FraudDetector,
    FraudRiskLevel,
)
from modules.analytics.models.scoring.lead_scorer import LeadQuality, LeadScorer
from modules.analytics.monitoring.model_monitor import ModelMonitor

logger = logging.getLogger(__name__)

analytics_router = APIRouter(prefix="/analytics", tags=["Predictive Analytics"])


# ============== Schemas ==============


class ChurnPredictionRequest(BaseModel):
    """Request para predição de churn."""

    user_id: int


class ChurnPredictionResponse(BaseModel):
    """Response de predição de churn."""

    user_id: int
    churn_probability: float
    risk_level: str
    confidence: float
    contributing_factors: list[dict]
    retention_actions: list[dict]
    predicted_churn_date: str | None
    lifetime_value_at_risk: float


class ForecastRequest(BaseModel):
    """Request para forecast de vendas."""

    periods: int = Field(default=30, ge=1, le=365)
    granularity: str = Field(default="daily")
    entity_type: str = Field(default="revenue")


class ForecastResponse(BaseModel):
    """Response de forecast."""

    forecast_type: str
    granularity: str
    start_date: str
    end_date: str
    predictions: list[dict]
    total_forecast: float
    accuracy_metrics: dict
    insights: list[str]


class TransactionAnalysisRequest(BaseModel):
    """Request para análise de transação."""

    id: str | None = None
    user_id: int | None = None
    amount: float
    type: str | None = None
    hour: int | None = None
    device_id: str | None = None
    ip_address: str | None = None
    recent_transactions_count: int = 0


class FraudAlertResponse(BaseModel):
    """Response de análise de fraude."""

    transaction_id: str | None
    risk_score: float
    risk_level: str
    fraud_type: str
    confidence: float
    indicators: list[dict]
    recommended_actions: list[str]


class LeadScoreRequest(BaseModel):
    """Request para scoring de lead."""

    id: str | None = None
    title: str | None = None
    company_size: int = 0
    industry_fit: float = 0.5
    budget_range: float = 0
    decision_timeline: str | None = None
    website_visits: int = 0
    page_views: int = 0
    time_on_site: int = 0
    email_opens: int = 0
    email_clicks: int = 0
    content_downloads: int = 0
    demo_requests: int = 0
    form_submissions: int = 0


class LeadScoreResponse(BaseModel):
    """Response de lead scoring."""

    lead_id: str
    total_score: float
    quality: str
    conversion_probability: float
    stage: str
    factors: list[dict]
    insights: list[dict]
    next_best_action: str
    estimated_value: float
    time_to_conversion: int | None


class ModelHealthResponse(BaseModel):
    """Response de saúde do modelo."""

    model_name: str
    model_version: str
    status: str
    overall_score: float
    metrics: list[dict]
    predictions_last_hour: int
    avg_latency_ms: float
    error_rate: float
    recommendations: list[str]


# ============== Instances ==============

feature_store = FeatureStore()
model_registry = ModelRegistry()
churn_predictor = ChurnPredictor(feature_store, model_registry)
sales_forecaster = SalesForecaster(model_registry)
fraud_detector = FraudDetector(model_registry)
lead_scorer = LeadScorer(model_registry)
model_monitor = ModelMonitor(model_registry)


# ============== Churn Endpoints ==============


@analytics_router.post(
    "/churn/predict",
    response_model=ChurnPredictionResponse,
    summary="Predizer churn de usuário",
)
async def predict_churn(
    request: ChurnPredictionRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Prediz probabilidade de churn para um usuário específico.

    Retorna:
    - Probabilidade de churn (0-1)
    - Nível de risco
    - Fatores contribuintes
    - Ações de retenção recomendadas
    """
    try:
        prediction = await churn_predictor.predict(db, request.user_id)

        return ChurnPredictionResponse(
            user_id=prediction.user_id,
            churn_probability=prediction.churn_probability,
            risk_level=prediction.risk_level.value,
            confidence=prediction.confidence,
            contributing_factors=prediction.contributing_factors,
            retention_actions=[
                {
                    "type": a.action_type.value,
                    "priority": a.priority,
                    "description": a.description,
                    "expected_impact": a.expected_impact,
                }
                for a in prediction.retention_actions
            ],
            predicted_churn_date=(
                prediction.predicted_churn_date.isoformat() if prediction.predicted_churn_date else None
            ),
            lifetime_value_at_risk=prediction.lifetime_value_at_risk,
        )
    except Exception as e:
        logger.error(f"Erro na predição de churn: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get(
    "/churn/high-risk",
    summary="Listar usuários com alto risco de churn",
)
async def get_high_risk_users(
    limit: int = Query(default=50, le=200),
    min_risk: str = Query(default="high"),
    db: AsyncSession = Depends(get_db),
):
    """Lista usuários com alto risco de churn ordenados por probabilidade."""
    try:
        risk_level = ChurnRiskLevel(min_risk)
        predictions = await churn_predictor.get_high_risk_users(db, limit, risk_level)

        return {
            "total": len(predictions),
            "users": [
                {
                    "user_id": p.user_id,
                    "churn_probability": p.churn_probability,
                    "risk_level": p.risk_level.value,
                    "ltv_at_risk": p.lifetime_value_at_risk,
                }
                for p in predictions
            ],
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Nível de risco inválido")
    except Exception as e:
        logger.error(f"Erro ao buscar usuários de alto risco: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get(
    "/churn/analytics",
    summary="Analytics de churn",
)
async def get_churn_analytics(
    db: AsyncSession = Depends(get_db),
):
    """Obtém métricas agregadas de churn."""
    try:
        analytics = await churn_predictor.get_churn_analytics(db)

        return {
            "total_users": analytics.total_users,
            "at_risk_users": analytics.at_risk_users,
            "churn_rate_30d": analytics.churn_rate_30d,
            "churn_rate_90d": analytics.churn_rate_90d,
            "avg_churn_probability": analytics.avg_churn_probability,
            "ltv_at_risk": analytics.ltv_at_risk,
            "risk_distribution": analytics.risk_distribution,
            "top_churn_factors": analytics.top_churn_factors,
            "trend": analytics.trend,
        }
    except Exception as e:
        logger.error(f"Erro ao obter analytics de churn: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Forecast Endpoints ==============


@analytics_router.post(
    "/forecast/sales",
    response_model=ForecastResponse,
    summary="Previsão de vendas",
)
async def forecast_sales(
    request: ForecastRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Gera previsão de vendas/receita.

    Parâmetros:
    - periods: Número de períodos a prever
    - granularity: daily, weekly, monthly
    - entity_type: revenue, units, etc.
    """
    try:
        granularity = ForecastGranularity(request.granularity)
        forecast = await sales_forecaster.forecast(
            db,
            periods=request.periods,
            granularity=granularity,
            entity_type=request.entity_type,
        )

        return ForecastResponse(
            forecast_type=forecast.forecast_type,
            granularity=forecast.granularity.value,
            start_date=forecast.start_date.isoformat(),
            end_date=forecast.end_date.isoformat(),
            predictions=[
                {
                    "date": p.date.isoformat(),
                    "value": p.value,
                    "lower_bound": p.lower_bound,
                    "upper_bound": p.upper_bound,
                    "confidence": p.confidence,
                }
                for p in forecast.predictions
            ],
            total_forecast=forecast.total_forecast,
            accuracy_metrics=forecast.accuracy_metrics,
            insights=forecast.insights,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro no forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get(
    "/forecast/scenarios",
    summary="Cenários de previsão",
)
async def get_forecast_scenarios(
    periods: int = Query(default=30, le=90),
    db: AsyncSession = Depends(get_db),
):
    """Gera múltiplos cenários de previsão (pessimista, base, otimista)."""
    try:
        scenarios = await sales_forecaster.forecast_scenarios(db, periods)

        return {
            scenario_name: {
                "total_forecast": forecast.total_forecast,
                "insights": forecast.insights,
                "predictions_count": len(forecast.predictions),
            }
            for scenario_name, forecast in scenarios.items()
        }
    except Exception as e:
        logger.error(f"Erro nos cenários: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get(
    "/forecast/accuracy",
    summary="Relatório de acurácia do forecast",
)
async def get_forecast_accuracy(
    lookback_days: int = Query(default=90, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Obtém relatório de acurácia das previsões históricas."""
    try:
        report = await sales_forecaster.get_forecast_accuracy_report(db, lookback_days)
        return report
    except Exception as e:
        logger.error(f"Erro no relatório de acurácia: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Fraud Endpoints ==============


@analytics_router.post(
    "/fraud/analyze",
    response_model=FraudAlertResponse,
    summary="Analisar transação para fraude",
)
async def analyze_transaction(
    request: TransactionAnalysisRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Analisa uma transação em tempo real para detecção de fraude.

    Retorna:
    - Score de risco (0-100)
    - Nível de risco
    - Indicadores de fraude
    - Ações recomendadas
    """
    try:
        alert = await fraud_detector.analyze_transaction(db, request.dict())

        return FraudAlertResponse(
            transaction_id=alert.transaction_id,
            risk_score=alert.risk_score,
            risk_level=alert.risk_level.value,
            fraud_type=alert.fraud_type.value,
            confidence=alert.confidence,
            indicators=[
                {
                    "type": i.indicator_type,
                    "value": i.value,
                    "description": i.description,
                }
                for i in alert.indicators
            ],
            recommended_actions=alert.recommended_actions,
        )
    except Exception as e:
        logger.error(f"Erro na análise de fraude: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get(
    "/fraud/alerts",
    summary="Listar alertas de fraude",
)
async def get_fraud_alerts(
    min_risk: str | None = Query(default=None),
    acknowledged: bool | None = Query(default=None),
    limit: int = Query(default=50, le=200),
):
    """Lista alertas de fraude filtrados."""
    try:
        risk_level = FraudRiskLevel(min_risk) if min_risk else None
        alerts = fraud_detector.get_open_alerts(limit, risk_level or FraudRiskLevel.LOW)

        return {
            "total": len(alerts),
            "alerts": [
                {
                    "id": str(a.id),
                    "transaction_id": a.transaction_id,
                    "risk_score": a.risk_score,
                    "risk_level": a.risk_level.value,
                    "fraud_type": a.fraud_type.value,
                    "status": a.status.value,
                    "created_at": a.created_at.isoformat(),
                }
                for a in alerts
            ],
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Nível de risco inválido")


@analytics_router.put(
    "/fraud/alerts/{alert_id}/status",
    summary="Atualizar status de alerta",
)
async def update_alert_status(
    alert_id: str,
    new_status: str,
    notes: str | None = None,
):
    """Atualiza o status de um alerta de fraude."""
    try:
        status = AlertStatus(new_status)
        alert = fraud_detector.update_alert_status(alert_id, status, notes)

        if not alert:
            raise HTTPException(status_code=404, detail="Alerta não encontrado")

        return {"message": "Status atualizado", "new_status": status.value}
    except ValueError:
        raise HTTPException(status_code=400, detail="Status inválido")


@analytics_router.get(
    "/fraud/analytics",
    summary="Analytics de fraude",
)
async def get_fraud_analytics(
    db: AsyncSession = Depends(get_db),
):
    """Obtém métricas agregadas de fraude."""
    try:
        analytics = await fraud_detector.get_fraud_analytics(db)

        return {
            "period_start": analytics.period_start.isoformat(),
            "period_end": analytics.period_end.isoformat(),
            "total_transactions": analytics.total_transactions,
            "flagged_transactions": analytics.flagged_transactions,
            "confirmed_frauds": analytics.confirmed_frauds,
            "fraud_rate": analytics.fraud_rate,
            "detection_rate": analytics.detection_rate,
            "false_positive_rate": analytics.false_positive_rate,
            "total_amount_at_risk": analytics.total_amount_at_risk,
            "total_amount_prevented": analytics.total_amount_prevented,
            "alerts_by_type": analytics.alerts_by_type,
        }
    except Exception as e:
        logger.error(f"Erro ao obter analytics de fraude: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get(
    "/fraud/user/{user_id}/risk",
    summary="Perfil de risco de usuário",
)
async def get_user_risk_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Obtém perfil de risco de um usuário específico."""
    try:
        profile = await fraud_detector.get_user_risk_profile(db, user_id)
        return profile
    except Exception as e:
        logger.error(f"Erro ao obter perfil de risco: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Lead Scoring Endpoints ==============


@analytics_router.post(
    "/leads/score",
    response_model=LeadScoreResponse,
    summary="Calcular score de lead",
)
async def score_lead(
    request: LeadScoreRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Calcula score de um lead para priorização de vendas.

    Retorna:
    - Score total (0-100)
    - Qualidade (hot, warm, cold, etc.)
    - Probabilidade de conversão
    - Próxima melhor ação
    """
    try:
        score = await lead_scorer.score_lead(db, request.dict())

        return LeadScoreResponse(
            lead_id=score.lead_id,
            total_score=score.total_score,
            quality=score.quality.value,
            conversion_probability=score.conversion_probability,
            stage=score.stage.value,
            factors=[
                {
                    "name": f.name,
                    "value": f.value,
                    "impact": f.score_impact,
                    "category": f.category,
                }
                for f in score.factors
            ],
            insights=[
                {
                    "type": i.insight_type,
                    "title": i.title,
                    "description": i.description,
                    "action": i.action_recommended,
                }
                for i in score.insights
            ],
            next_best_action=score.next_best_action,
            estimated_value=score.estimated_value,
            time_to_conversion=score.time_to_conversion,
        )
    except Exception as e:
        logger.error(f"Erro no lead scoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get(
    "/leads/top",
    summary="Top leads por score",
)
async def get_top_leads(
    limit: int = Query(default=50, le=200),
    min_quality: str = Query(default="warm"),
    db: AsyncSession = Depends(get_db),
):
    """Lista os leads com melhor score."""
    try:
        quality = LeadQuality(min_quality)
        leads = await lead_scorer.get_top_leads(db, limit, quality)

        return {
            "total": len(leads),
            "leads": [
                {
                    "lead_id": lead.lead_id,
                    "score": lead.total_score,
                    "quality": lead.quality.value,
                    "conversion_probability": lead.conversion_probability,
                    "estimated_value": lead.estimated_value,
                    "next_action": lead.next_best_action,
                }
                for lead in leads
            ],
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Qualidade inválida")


@analytics_router.get(
    "/leads/analytics",
    summary="Analytics de lead scoring",
)
async def get_scoring_analytics(
    db: AsyncSession = Depends(get_db),
):
    """Obtém métricas agregadas de lead scoring."""
    try:
        analytics = await lead_scorer.get_scoring_analytics(db)

        return {
            "total_leads_scored": analytics.total_leads_scored,
            "average_score": analytics.average_score,
            "score_distribution": analytics.score_distribution,
            "quality_distribution": analytics.quality_distribution,
            "conversion_rate_by_score": analytics.conversion_rate_by_score,
            "top_scoring_factors": analytics.top_scoring_factors,
            "model_accuracy": analytics.model_accuracy,
            "pipeline_value": analytics.pipeline_value,
        }
    except Exception as e:
        logger.error(f"Erro ao obter analytics de scoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Model Management Endpoints ==============


@analytics_router.get(
    "/models",
    summary="Listar modelos registrados",
)
async def list_models():
    """Lista todos os modelos no registry."""
    models = model_registry.list_models()
    return {"total": len(models), "models": models}


@analytics_router.get(
    "/models/{model_name}/versions",
    summary="Listar versões de um modelo",
)
async def list_model_versions(
    model_name: str,
    stage: str | None = None,
):
    """Lista versões de um modelo específico."""
    try:
        model_stage = ModelStage(stage) if stage else None
        versions = model_registry.list_versions(model_name, model_stage)
        return {"model": model_name, "versions": versions}
    except ValueError:
        raise HTTPException(status_code=400, detail="Stage inválido")


@analytics_router.get(
    "/models/{model_name}/compare",
    summary="Comparar versões de modelo",
)
async def compare_model_versions(
    model_name: str,
    version1: str,
    version2: str,
):
    """Compara métricas entre duas versões de um modelo."""
    comparison = model_registry.compare_versions(model_name, version1, version2)
    if "error" in comparison:
        raise HTTPException(status_code=404, detail=comparison["error"])
    return comparison


@analytics_router.post(
    "/models/{model_name}/promote",
    summary="Promover modelo para produção",
)
async def promote_model(
    model_name: str,
    version: str,
    target_stage: str = "production",
):
    """Promove uma versão do modelo para um novo estágio."""
    try:
        stage = ModelStage(target_stage)
        success = model_registry.promote_model(model_name, version, stage)

        if not success:
            raise HTTPException(status_code=404, detail="Modelo não encontrado")

        return {"message": f"Modelo promovido para {target_stage}"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Stage inválido")


# ============== Monitoring Endpoints ==============


@analytics_router.get(
    "/monitoring/dashboard",
    summary="Dashboard de monitoramento",
)
async def get_monitoring_dashboard(
    db: AsyncSession = Depends(get_db),
):
    """Obtém dashboard de monitoramento de todos os modelos."""
    try:
        dashboard = await model_monitor.get_dashboard(db)

        return {
            "timestamp": dashboard.timestamp.isoformat(),
            "models_monitored": dashboard.models_monitored,
            "healthy_models": dashboard.healthy_models,
            "warning_models": dashboard.warning_models,
            "critical_models": dashboard.critical_models,
            "active_alerts": dashboard.active_alerts,
            "models_status": dashboard.models_status,
            "system_metrics": dashboard.system_metrics,
        }
    except Exception as e:
        logger.error(f"Erro no dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get(
    "/monitoring/models/{model_name}/health",
    response_model=ModelHealthResponse,
    summary="Saúde de um modelo específico",
)
async def get_model_health(
    model_name: str,
    db: AsyncSession = Depends(get_db),
):
    """Obtém status de saúde detalhado de um modelo."""
    try:
        health = await model_monitor.check_model_health(db, model_name)

        return ModelHealthResponse(
            model_name=health.model_name,
            model_version=health.model_version,
            status=health.status.value,
            overall_score=health.overall_score,
            metrics=[
                {
                    "name": m.name,
                    "value": m.value,
                    "baseline": m.baseline,
                    "is_healthy": m.is_healthy,
                    "trend": m.trend,
                }
                for m in health.metrics
            ],
            predictions_last_hour=health.predictions_last_hour,
            avg_latency_ms=health.avg_latency_ms,
            error_rate=health.error_rate,
            recommendations=health.recommendations,
        )
    except Exception as e:
        logger.error(f"Erro ao verificar saúde: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get(
    "/monitoring/alerts",
    summary="Listar alertas de monitoramento",
)
async def get_monitoring_alerts(
    model_name: str | None = None,
    acknowledged: bool | None = None,
):
    """Lista alertas de drift e degradação."""
    alerts = model_monitor.get_alerts(model_name, acknowledged=acknowledged)

    return {
        "total": len(alerts),
        "alerts": [
            {
                "id": str(a.id),
                "model_name": a.model_name,
                "drift_type": a.drift_type.value,
                "severity": a.severity.value,
                "drift_score": a.drift_score,
                "description": a.description,
                "created_at": a.created_at.isoformat(),
                "acknowledged": a.acknowledged,
            }
            for a in alerts
        ],
    }


@analytics_router.put(
    "/monitoring/alerts/{alert_id}/acknowledge",
    summary="Reconhecer alerta",
)
async def acknowledge_monitoring_alert(alert_id: str):
    """Reconhece um alerta de monitoramento."""
    success = model_monitor.acknowledge_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    return {"message": "Alerta reconhecido"}


# ============== Feature Store Endpoints ==============


@analytics_router.get(
    "/features/user/{user_id}",
    summary="Features de um usuário",
)
async def get_user_features(
    user_id: int,
    features: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Obtém features calculadas de um usuário."""
    try:
        include = features.split(",") if features else None
        user_features = await feature_store.get_user_features(db, user_id, include=include)
        return user_features
    except Exception as e:
        logger.error(f"Erro ao obter features: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@analytics_router.get(
    "/features/available",
    summary="Listar features disponíveis",
)
async def list_available_features():
    """Lista todas as features disponíveis no Feature Store."""
    features = feature_store.list_available_features()
    return {"total": len(features), "features": features}


@analytics_router.get(
    "/features/{feature_name}/metadata",
    summary="Metadados de uma feature",
)
async def get_feature_metadata(feature_name: str):
    """Obtém metadados de uma feature específica."""
    metadata = feature_store.get_feature_metadata(feature_name)
    if not metadata:
        raise HTTPException(status_code=404, detail="Feature não encontrada")
    return metadata
