"""
Intelligence Hub Controller - API REST da Central de IA

Endpoints para interagir com a Central de Inteligência Artificial do Conecta PRO
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from ..cross_module_analytics import CrossModuleAnalytics
from ..insight_distributor import Insight, InsightDistributor, InsightPriority, InsightType
from ..module_integration_manager import ModuleIntegrationManager
from ..predictive_orchestra import PredictionPriority, PredictionRequest, PredictiveOrchestra

# Importar componentes da Central de IA
from ..unified_ai_engine import AIInput, PredictionContext, UnifiedAIEngine

logger = logging.getLogger(__name__)

# Instâncias globais dos componentes (em produção, usaria dependency injection)
ai_engine = UnifiedAIEngine()
analytics = CrossModuleAnalytics()
orchestra = PredictiveOrchestra()
distributor = InsightDistributor()
integration_manager = ModuleIntegrationManager()

# Router
router = APIRouter(prefix="/intelligence-hub", tags=["Intelligence Hub - Central IA"])


# =============================================================================
# SCHEMAS PYDANTIC
# =============================================================================


class AIRequestSchema(BaseModel):
    module_name: str = Field(..., description="Nome do módulo")
    data_type: str = Field(..., description="Tipo de dados")
    data: dict[str, Any] = Field(..., description="Dados para análise")
    context: str = Field(default="real_time", description="Contexto da predição")
    user_id: str | None = Field(None, description="ID do usuário")
    tenant_id: str = Field(..., description="ID do tenant")


class PredictionRequestSchema(BaseModel):
    module_name: str = Field(..., description="Nome do módulo")
    data_type: str = Field(..., description="Tipo de dados")
    data: dict[str, Any] = Field(..., description="Dados para predição")
    priority: str = Field(default="normal", description="Prioridade (low, normal, high, critical, emergency)")
    tenant_id: str = Field(..., description="ID do tenant")
    user_id: str | None = Field(None, description="ID do usuário")
    deadline: str | None = Field(None, description="Deadline ISO format")


class InsightSchema(BaseModel):
    type: str = Field(..., description="Tipo do insight")
    priority: str = Field(..., description="Prioridade")
    source_module: str = Field(..., description="Módulo de origem")
    title: str = Field(..., description="Título")
    content: str = Field(..., description="Conteúdo")
    data: dict[str, Any] = Field(..., description="Dados do insight")
    tenant_id: str = Field(..., description="ID do tenant")
    target_modules: list[str] = Field(default=[], description="Módulos alvo")
    target_users: list[str] = Field(default=[], description="Usuários alvo")


class ModuleHealthResponse(BaseModel):
    module: str
    status: str
    last_check: str
    response_time: float
    details: dict[str, Any]


# =============================================================================
# ENDPOINTS DA CENTRAL DE IA
# =============================================================================


@router.get("/health", summary="Health Check da Central de IA")
async def health_check():
    """Verifica saúde geral da Central de IA"""
    try:
        # Verificar todos os componentes
        ai_health = await ai_engine.health_check()
        analytics_health = await analytics.health_check()
        orchestra_health = await orchestra.health_check()
        distributor_health = await distributor.health_check()
        integration_health = await integration_manager.health_check()

        overall_status = "healthy"
        components = {
            "ai_engine": ai_health,
            "analytics": analytics_health,
            "orchestra": orchestra_health,
            "distributor": distributor_health,
            "integration_manager": integration_health,
        }

        return {"status": overall_status, "timestamp": datetime.now().isoformat(), "components": components}
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/predict", summary="Fazer Predição com IA")
async def make_ai_prediction(request: AIRequestSchema):
    """Faz uma predição usando o motor central de IA"""
    try:
        # Converter para AIInput
        ai_input = AIInput(
            module_name=request.module_name,
            data_type=request.data_type,
            data=request.data,
            context=PredictionContext(request.context),
            timestamp=datetime.now(),
            user_id=request.user_id,
            tenant_id=request.tenant_id,
        )

        # Processar com IA
        result = await ai_engine.process_ai_request(ai_input)

        return {
            "prediction": result.prediction,
            "confidence": result.confidence,
            "model_used": result.model_used,
            "processing_time": result.processing_time,
            "insights": result.insights,
            "recommendations": result.recommendations,
            "metadata": result.metadata,
        }

    except Exception as e:
        logger.error(f"Erro na predição: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predictions/submit", summary="Submeter Predição para Fila")
async def submit_prediction(request: PredictionRequestSchema):
    """Submete uma predição para a fila do orquestrador"""
    try:
        # Converter prioridade
        priority_map = {
            "low": PredictionPriority.LOW,
            "normal": PredictionPriority.NORMAL,
            "high": PredictionPriority.HIGH,
            "critical": PredictionPriority.CRITICAL,
            "emergency": PredictionPriority.EMERGENCY,
        }

        priority = priority_map.get(request.priority, PredictionPriority.NORMAL)

        # Criar requisição
        pred_request = PredictionRequest(
            id=str(uuid.uuid4()),
            module_name=request.module_name,
            data_type=request.data_type,
            data=request.data,
            priority=priority,
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            deadline=datetime.fromisoformat(request.deadline) if request.deadline else None,
        )

        # Submeter
        prediction_id = await orchestra.submit_prediction(pred_request)

        return {
            "prediction_id": prediction_id,
            "status": "submitted",
            "priority": request.priority,
            "estimated_completion": "Será processado conforme a fila",
        }

    except Exception as e:
        logger.error(f"Erro ao submeter predição: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions/{prediction_id}/status", summary="Status de Predição")
async def get_prediction_status(prediction_id: str):
    """Obtém status de uma predição específica"""
    try:
        status = await orchestra.get_prediction_status(prediction_id)

        if not status:
            raise HTTPException(status_code=404, detail="Predição não encontrada")

        return status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/correlations", summary="Análises Cross-Module")
async def get_module_correlations(tenant_id: str, timeframe_days: int = 30):
    """Obtém correlações entre módulos"""
    try:
        correlations = await analytics.analyze_all_correlations(tenant_id, timeframe_days)

        # Serializar correlações
        correlation_data = []
        for corr in correlations:
            correlation_data.append(
                {
                    "module_a": corr.module_a,
                    "module_b": corr.module_b,
                    "correlation_type": corr.correlation_type.value,
                    "strength": corr.strength,
                    "confidence": corr.confidence,
                    "insights": corr.insights,
                    "impact_areas": corr.impact_areas,
                    "timestamp": corr.timestamp.isoformat(),
                }
            )

        return {
            "tenant_id": tenant_id,
            "timeframe_days": timeframe_days,
            "total_correlations": len(correlation_data),
            "correlations": correlation_data,
            "generated_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Erro nas análises de correlação: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/insights", summary="Insights Integrados")
async def get_integrated_insights(tenant_id: str):
    """Obtém insights integrados cross-module"""
    try:
        insights = await analytics.generate_integrated_insights(tenant_id)
        return insights

    except Exception as e:
        logger.error(f"Erro ao gerar insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/insights/distribute", summary="Distribuir Insight")
async def distribute_insight(insight_data: InsightSchema):
    """Distribui um insight para módulos e usuários relevantes"""
    try:
        # Converter para Insight
        insight = Insight(
            id=str(uuid.uuid4()),
            type=InsightType(insight_data.type),
            priority=InsightPriority[insight_data.priority.upper()],
            source_module=insight_data.source_module,
            title=insight_data.title,
            content=insight_data.content,
            data=insight_data.data,
            tenant_id=insight_data.tenant_id,
            target_modules=insight_data.target_modules,
            target_users=insight_data.target_users,
        )

        # Distribuir
        result = await distributor.distribute_insight(insight)

        return result

    except Exception as e:
        logger.error(f"Erro na distribuição de insight: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/modules/health", summary="Saúde dos Módulos")
async def get_modules_health():
    """Obtém saúde de todos os módulos integrados"""
    try:
        health = await integration_manager.get_all_modules_health()
        return health

    except Exception as e:
        logger.error(f"Erro ao obter saúde dos módulos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/modules/{module_name}/health", summary="Saúde de Módulo Específico")
async def get_module_health(module_name: str):
    """Obtém saúde de um módulo específico"""
    try:
        health = await integration_manager.get_module_health(module_name)
        return health

    except Exception as e:
        logger.error(f"Erro ao obter saúde do módulo {module_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/modules/discover", summary="Auto-descobrir Módulos")
async def discover_modules(background_tasks: BackgroundTasks):
    """Executa auto-descoberta de módulos"""
    try:
        # Executar em background para não bloquear
        background_tasks.add_task(integration_manager.auto_discover_modules)

        return {"message": "Auto-descoberta iniciada", "status": "running", "timestamp": datetime.now().isoformat()}

    except Exception as e:
        logger.error(f"Erro na auto-descoberta: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/status", summary="Status da Fila de Predições")
async def get_queue_status():
    """Obtém status da fila de predições"""
    try:
        status = await orchestra.get_queue_status()
        return status

    except Exception as e:
        logger.error(f"Erro ao obter status da fila: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", summary="Estatísticas da Central IA")
async def get_intelligence_hub_stats():
    """Obtém estatísticas gerais da Central de IA"""
    try:
        # Coletar estatísticas de todos os componentes
        orchestra_stats = await orchestra.get_queue_status()
        integration_stats = await integration_manager.get_integration_stats()

        return {
            "timestamp": datetime.now().isoformat(),
            "orchestra": orchestra_stats,
            "integration": integration_stats,
            "modules_monitored": len(integration_manager.modules),
            "version": "1.0.0",
        }

    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# INICIALIZAÇÃO DOS COMPONENTES
# =============================================================================


@router.on_event("startup")
async def startup_intelligence_hub():
    """Inicializa componentes da Central de IA"""
    try:
        logger.info("Iniciando Central de IA...")

        # Iniciar orquestrador
        await orchestra.start()

        # Iniciar gerenciador de integração
        await integration_manager.start()

        logger.info("Central de IA iniciada com sucesso!")

    except Exception as e:
        logger.error(f"Erro na inicialização da Central de IA: {e}")


@router.on_event("shutdown")
async def shutdown_intelligence_hub():
    """Para componentes da Central de IA"""
    try:
        logger.info("Parando Central de IA...")

        # Parar orquestrador
        await orchestra.stop()

        # Parar gerenciador de integração
        await integration_manager.stop()

        logger.info("Central de IA parada com sucesso!")

    except Exception as e:
        logger.error(f"Erro ao parar Central de IA: {e}")
