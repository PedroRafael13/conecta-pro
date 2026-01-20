"""AIRepository - Repositorio para operacoes de IA.

Sprint 34 - AI Predictions.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from modules.ai.models.anomaly_log import AnomalyLog, AnomalySeverity, AnomalyStatus
from modules.ai.models.feature_store import Feature, FeatureStore
from modules.ai.models.ml_model import MLModel, ModelStatus, ModelType
from modules.ai.models.prediction import Prediction, PredictionStatus, PredictionType
from modules.ai.models.prediction_log import PredictionLog
from modules.ai.models.recommendation import Recommendation, RecommendationStatus, RecommendationType
from modules.ai.models.training_job import TrainingJob, TrainingStatus

logger = logging.getLogger(__name__)


class AIRepository:
    """Repositorio para operacoes de IA."""

    def __init__(self, db: Session):
        """Inicializa o repositorio.

        Args:
            db: Sessao do banco.
        """
        self.db = db

    # ============ Prediction Methods ============

    async def create_prediction(self, prediction: Prediction) -> Prediction:
        """Cria previsao.

        Args:
            prediction: Previsao a criar.

        Returns:
            Previsao criada.
        """
        self.db.add(prediction)
        await self.db.commit()
        await self.db.refresh(prediction)
        return prediction

    async def get_prediction(
        self,
        prediction_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> Optional[Prediction]:
        """Busca previsao por ID.

        Args:
            prediction_id: ID da previsao.
            tenant_id: ID do tenant.

        Returns:
            Previsao ou None.
        """
        query = self.db.query(Prediction).filter(Prediction.id == prediction_id)
        if tenant_id:
            query = query.filter(Prediction.tenant_id == tenant_id)
        return await query.first()

    async def list_predictions(
        self,
        tenant_id: UUID,
        prediction_type: Optional[PredictionType] = None,
        status: Optional[PredictionStatus] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        model_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Prediction], int]:
        """Lista previsoes com filtros.

        Args:
            tenant_id: ID do tenant.
            prediction_type: Filtro por tipo.
            status: Filtro por status.
            entity_type: Filtro por tipo de entidade.
            entity_id: Filtro por ID de entidade.
            model_id: Filtro por modelo.
            skip: Offset.
            limit: Limite.

        Returns:
            Tupla com lista e total.
        """
        query = self.db.query(Prediction).filter(Prediction.tenant_id == tenant_id)

        if prediction_type:
            query = query.filter(Prediction.prediction_type == prediction_type)
        if status:
            query = query.filter(Prediction.status == status)
        if entity_type:
            query = query.filter(Prediction.entity_type == entity_type)
        if entity_id:
            query = query.filter(Prediction.entity_id == entity_id)
        if model_id:
            query = query.filter(Prediction.model_id == model_id)

        total = await query.count()
        items = await query.order_by(Prediction.created_at.desc()).offset(skip).limit(limit).all()

        return items, total

    async def update_prediction(self, prediction: Prediction) -> Prediction:
        """Atualiza previsao.

        Args:
            prediction: Previsao a atualizar.

        Returns:
            Previsao atualizada.
        """
        await self.db.commit()
        await self.db.refresh(prediction)
        return prediction

    # ============ ML Model Methods ============

    async def create_model(self, model: MLModel) -> MLModel:
        """Cria modelo.

        Args:
            model: Modelo a criar.

        Returns:
            Modelo criado.
        """
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return model

    async def get_model(
        self,
        model_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> Optional[MLModel]:
        """Busca modelo por ID.

        Args:
            model_id: ID do modelo.
            tenant_id: ID do tenant.

        Returns:
            Modelo ou None.
        """
        query = self.db.query(MLModel).filter(MLModel.id == model_id)
        if tenant_id:
            query = query.filter(MLModel.tenant_id == tenant_id)
        return await query.first()

    async def get_model_by_slug(
        self,
        tenant_id: UUID,
        slug: str,
    ) -> Optional[MLModel]:
        """Busca modelo por slug.

        Args:
            tenant_id: ID do tenant.
            slug: Slug do modelo.

        Returns:
            Modelo ou None.
        """
        return await (
            self.db.query(MLModel)
            .filter(MLModel.tenant_id == tenant_id)
            .filter(MLModel.slug == slug)
            .first()
        )

    async def list_models(
        self,
        tenant_id: UUID,
        model_type: Optional[ModelType] = None,
        status: Optional[ModelStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[MLModel], int]:
        """Lista modelos com filtros.

        Args:
            tenant_id: ID do tenant.
            model_type: Filtro por tipo.
            status: Filtro por status.
            skip: Offset.
            limit: Limite.

        Returns:
            Tupla com lista e total.
        """
        query = self.db.query(MLModel).filter(MLModel.tenant_id == tenant_id)

        if model_type:
            query = query.filter(MLModel.model_type == model_type)
        if status:
            query = query.filter(MLModel.status == status)

        total = await query.count()
        items = await query.order_by(MLModel.created_at.desc()).offset(skip).limit(limit).all()

        return items, total

    async def get_default_model(
        self,
        tenant_id: UUID,
        model_type: ModelType,
    ) -> Optional[MLModel]:
        """Busca modelo default para um tipo.

        Args:
            tenant_id: ID do tenant.
            model_type: Tipo de modelo.

        Returns:
            Modelo ou None.
        """
        return await (
            self.db.query(MLModel)
            .filter(MLModel.tenant_id == tenant_id)
            .filter(MLModel.model_type == model_type)
            .filter(MLModel.is_default == True)  # noqa: E712
            .filter(MLModel.status == ModelStatus.DEPLOYED)
            .first()
        )

    async def update_model(self, model: MLModel) -> MLModel:
        """Atualiza modelo.

        Args:
            model: Modelo a atualizar.

        Returns:
            Modelo atualizado.
        """
        await self.db.commit()
        await self.db.refresh(model)
        return model

    # ============ Feature Store Methods ============

    async def create_feature_store(self, store: FeatureStore) -> FeatureStore:
        """Cria feature store.

        Args:
            store: Feature store a criar.

        Returns:
            Feature store criado.
        """
        self.db.add(store)
        await self.db.commit()
        await self.db.refresh(store)
        return store

    async def get_feature_store(
        self,
        store_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> Optional[FeatureStore]:
        """Busca feature store por ID.

        Args:
            store_id: ID do store.
            tenant_id: ID do tenant.

        Returns:
            Feature store ou None.
        """
        query = self.db.query(FeatureStore).filter(FeatureStore.id == store_id)
        if tenant_id:
            query = query.filter(FeatureStore.tenant_id == tenant_id)
        return await query.first()

    async def list_feature_stores(
        self,
        tenant_id: UUID,
        entity_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[FeatureStore], int]:
        """Lista feature stores.

        Args:
            tenant_id: ID do tenant.
            entity_type: Filtro por tipo de entidade.
            skip: Offset.
            limit: Limite.

        Returns:
            Tupla com lista e total.
        """
        query = self.db.query(FeatureStore).filter(FeatureStore.tenant_id == tenant_id)

        if entity_type:
            query = query.filter(FeatureStore.entity_type == entity_type)

        total = await query.count()
        items = await query.order_by(FeatureStore.created_at.desc()).offset(skip).limit(limit).all()

        return items, total

    # ============ Training Job Methods ============

    async def create_training_job(self, job: TrainingJob) -> TrainingJob:
        """Cria job de treinamento.

        Args:
            job: Job a criar.

        Returns:
            Job criado.
        """
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def get_training_job(
        self,
        job_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> Optional[TrainingJob]:
        """Busca job por ID.

        Args:
            job_id: ID do job.
            tenant_id: ID do tenant.

        Returns:
            Job ou None.
        """
        query = self.db.query(TrainingJob).filter(TrainingJob.id == job_id)
        if tenant_id:
            query = query.filter(TrainingJob.tenant_id == tenant_id)
        return await query.first()

    async def list_training_jobs(
        self,
        tenant_id: UUID,
        model_id: Optional[UUID] = None,
        status: Optional[TrainingStatus] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[TrainingJob], int]:
        """Lista jobs de treinamento.

        Args:
            tenant_id: ID do tenant.
            model_id: Filtro por modelo.
            status: Filtro por status.
            skip: Offset.
            limit: Limite.

        Returns:
            Tupla com lista e total.
        """
        query = self.db.query(TrainingJob).filter(TrainingJob.tenant_id == tenant_id)

        if model_id:
            query = query.filter(TrainingJob.model_id == model_id)
        if status:
            query = query.filter(TrainingJob.status == status)

        total = await query.count()
        items = await query.order_by(TrainingJob.created_at.desc()).offset(skip).limit(limit).all()

        return items, total

    async def update_training_job(self, job: TrainingJob) -> TrainingJob:
        """Atualiza job.

        Args:
            job: Job a atualizar.

        Returns:
            Job atualizado.
        """
        await self.db.commit()
        await self.db.refresh(job)
        return job

    # ============ Anomaly Methods ============

    async def create_anomaly(self, anomaly: AnomalyLog) -> AnomalyLog:
        """Cria log de anomalia.

        Args:
            anomaly: Anomalia a criar.

        Returns:
            Anomalia criada.
        """
        self.db.add(anomaly)
        await self.db.commit()
        await self.db.refresh(anomaly)
        return anomaly

    async def get_anomaly(
        self,
        anomaly_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> Optional[AnomalyLog]:
        """Busca anomalia por ID.

        Args:
            anomaly_id: ID da anomalia.
            tenant_id: ID do tenant.

        Returns:
            Anomalia ou None.
        """
        query = self.db.query(AnomalyLog).filter(AnomalyLog.id == anomaly_id)
        if tenant_id:
            query = query.filter(AnomalyLog.tenant_id == tenant_id)
        return await query.first()

    async def list_anomalies(
        self,
        tenant_id: UUID,
        entity_type: Optional[str] = None,
        severity: Optional[AnomalySeverity] = None,
        status: Optional[AnomalyStatus] = None,
        days: int = 30,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[AnomalyLog], int]:
        """Lista anomalias.

        Args:
            tenant_id: ID do tenant.
            entity_type: Filtro por tipo de entidade.
            severity: Filtro por severidade.
            status: Filtro por status.
            days: Dias de historico.
            skip: Offset.
            limit: Limite.

        Returns:
            Tupla com lista e total.
        """
        since = datetime.utcnow() - timedelta(days=days)
        query = (
            self.db.query(AnomalyLog)
            .filter(AnomalyLog.tenant_id == tenant_id)
            .filter(AnomalyLog.detected_at >= since)
        )

        if entity_type:
            query = query.filter(AnomalyLog.entity_type == entity_type)
        if severity:
            query = query.filter(AnomalyLog.severity == severity)
        if status:
            query = query.filter(AnomalyLog.status == status)

        total = await query.count()
        items = await query.order_by(AnomalyLog.detected_at.desc()).offset(skip).limit(limit).all()

        return items, total

    async def update_anomaly(self, anomaly: AnomalyLog) -> AnomalyLog:
        """Atualiza anomalia.

        Args:
            anomaly: Anomalia a atualizar.

        Returns:
            Anomalia atualizada.
        """
        await self.db.commit()
        await self.db.refresh(anomaly)
        return anomaly

    # ============ Recommendation Methods ============

    async def create_recommendation(self, rec: Recommendation) -> Recommendation:
        """Cria recomendacao.

        Args:
            rec: Recomendacao a criar.

        Returns:
            Recomendacao criada.
        """
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def get_recommendation(
        self,
        rec_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> Optional[Recommendation]:
        """Busca recomendacao por ID.

        Args:
            rec_id: ID da recomendacao.
            tenant_id: ID do tenant.

        Returns:
            Recomendacao ou None.
        """
        query = self.db.query(Recommendation).filter(Recommendation.id == rec_id)
        if tenant_id:
            query = query.filter(Recommendation.tenant_id == tenant_id)
        return await query.first()

    async def list_recommendations(
        self,
        tenant_id: UUID,
        target_entity_type: Optional[str] = None,
        target_entity_id: Optional[UUID] = None,
        recommendation_type: Optional[RecommendationType] = None,
        status: Optional[RecommendationStatus] = None,
        only_valid: bool = True,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Recommendation], int]:
        """Lista recomendacoes.

        Args:
            tenant_id: ID do tenant.
            target_entity_type: Filtro por tipo alvo.
            target_entity_id: Filtro por ID alvo.
            recommendation_type: Filtro por tipo.
            status: Filtro por status.
            only_valid: Apenas validas.
            skip: Offset.
            limit: Limite.

        Returns:
            Tupla com lista e total.
        """
        query = self.db.query(Recommendation).filter(Recommendation.tenant_id == tenant_id)

        if target_entity_type:
            query = query.filter(Recommendation.target_entity_type == target_entity_type)
        if target_entity_id:
            query = query.filter(Recommendation.target_entity_id == target_entity_id)
        if recommendation_type:
            query = query.filter(Recommendation.recommendation_type == recommendation_type)
        if status:
            query = query.filter(Recommendation.status == status)

        if only_valid:
            now = datetime.utcnow()
            query = query.filter(
                or_(
                    Recommendation.valid_until.is_(None),
                    Recommendation.valid_until >= now,
                )
            )

        total = await query.count()
        items = (
            await query.order_by(Recommendation.relevance_score.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return items, total

    async def update_recommendation(self, rec: Recommendation) -> Recommendation:
        """Atualiza recomendacao.

        Args:
            rec: Recomendacao a atualizar.

        Returns:
            Recomendacao atualizada.
        """
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    # ============ Stats Methods ============

    async def get_prediction_stats(
        self,
        tenant_id: UUID,
        days: int = 30,
    ) -> dict:
        """Retorna estatisticas de previsoes.

        Args:
            tenant_id: ID do tenant.
            days: Dias para analisar.

        Returns:
            Estatisticas.
        """
        since = datetime.utcnow() - timedelta(days=days)

        # Total e por status
        total = await (
            self.db.query(func.count(Prediction.id))
            .filter(Prediction.tenant_id == tenant_id)
            .filter(Prediction.created_at >= since)
            .scalar()
        )

        completed = await (
            self.db.query(func.count(Prediction.id))
            .filter(Prediction.tenant_id == tenant_id)
            .filter(Prediction.created_at >= since)
            .filter(Prediction.status == PredictionStatus.COMPLETED)
            .scalar()
        )

        failed = await (
            self.db.query(func.count(Prediction.id))
            .filter(Prediction.tenant_id == tenant_id)
            .filter(Prediction.created_at >= since)
            .filter(Prediction.status == PredictionStatus.FAILED)
            .scalar()
        )

        # Tempo medio de processamento
        avg_time = await (
            self.db.query(func.avg(Prediction.processing_time_ms))
            .filter(Prediction.tenant_id == tenant_id)
            .filter(Prediction.created_at >= since)
            .filter(Prediction.processing_time_ms.isnot(None))
            .scalar()
        )

        return {
            "period_days": days,
            "total": total or 0,
            "completed": completed or 0,
            "failed": failed or 0,
            "success_rate": ((completed or 0) / total * 100) if total else 0,
            "avg_processing_time_ms": avg_time,
        }

    async def get_model_stats(
        self,
        tenant_id: UUID,
        model_id: UUID,
    ) -> dict:
        """Retorna estatisticas de modelo.

        Args:
            tenant_id: ID do tenant.
            model_id: ID do modelo.

        Returns:
            Estatisticas.
        """
        model = await self.get_model(model_id, tenant_id)
        if not model:
            return {}

        return {
            "model_id": str(model.id),
            "model_name": model.name,
            "total_predictions": model.total_predictions,
            "success_rate": model.success_rate,
            "avg_prediction_time_ms": model.avg_prediction_time_ms,
            "drift_score": model.drift_score,
            "drift_detected": model.drift_detected,
            "needs_retraining": model.needs_retraining,
        }
