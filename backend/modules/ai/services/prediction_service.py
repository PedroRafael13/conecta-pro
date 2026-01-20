"""PredictionService - Servico Principal de Previsoes.

Sprint 34 - AI Predictions.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID

from modules.ai.models.ml_model import MLModel, ModelStatus
from modules.ai.models.prediction import Prediction, PredictionStatus, PredictionType

logger = logging.getLogger(__name__)


class PredictionService:
    """Servico principal para gerenciar previsoes."""

    def __init__(self, db_session: Any):
        """Inicializa o servico.

        Args:
            db_session: Sessao do banco de dados.
        """
        self.db = db_session

    async def create_prediction(
        self,
        tenant_id: UUID,
        prediction_type: PredictionType,
        entity_type: str,
        entity_id: UUID,
        model_id: Optional[UUID] = None,
        features: Optional[dict] = None,
        valid_days: int = 30,
        requested_by: Optional[UUID] = None,
        tags: Optional[list] = None,
    ) -> Prediction:
        """Cria uma nova previsao.

        Args:
            tenant_id: ID do tenant.
            prediction_type: Tipo de previsao.
            entity_type: Tipo da entidade.
            entity_id: ID da entidade.
            model_id: ID do modelo a usar.
            features: Features de entrada.
            valid_days: Dias de validade.
            requested_by: ID do usuario solicitante.
            tags: Tags para categorizar.

        Returns:
            Previsao criada.
        """
        prediction = Prediction(
            tenant_id=tenant_id,
            prediction_type=prediction_type,
            entity_type=entity_type,
            entity_id=entity_id,
            model_id=model_id,
            features_used=features,
            valid_from=datetime.utcnow(),
            valid_until=datetime.utcnow() + timedelta(days=valid_days),
            requested_by=requested_by,
            tags=tags or [],
        )

        self.db.add(prediction)
        await self.db.commit()
        await self.db.refresh(prediction)

        logger.info(
            "Prediction created",
            extra={
                "prediction_id": str(prediction.id),
                "type": prediction_type.value,
                "entity": f"{entity_type}:{entity_id}",
            },
        )

        return prediction

    async def get_prediction(
        self,
        prediction_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> Optional[Prediction]:
        """Busca uma previsao por ID.

        Args:
            prediction_id: ID da previsao.
            tenant_id: ID do tenant (para validacao).

        Returns:
            Previsao ou None.
        """
        query = self.db.query(Prediction).filter(Prediction.id == prediction_id)
        if tenant_id:
            query = query.filter(Prediction.tenant_id == tenant_id)
        return await query.first()

    async def get_predictions_for_entity(
        self,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID,
        prediction_type: Optional[PredictionType] = None,
        only_valid: bool = True,
        limit: int = 10,
    ) -> list[Prediction]:
        """Busca previsoes para uma entidade.

        Args:
            tenant_id: ID do tenant.
            entity_type: Tipo da entidade.
            entity_id: ID da entidade.
            prediction_type: Filtrar por tipo.
            only_valid: Apenas previsoes validas.
            limit: Limite de resultados.

        Returns:
            Lista de previsoes.
        """
        query = (
            self.db.query(Prediction)
            .filter(Prediction.tenant_id == tenant_id)
            .filter(Prediction.entity_type == entity_type)
            .filter(Prediction.entity_id == entity_id)
            .filter(Prediction.status == PredictionStatus.COMPLETED)
        )

        if prediction_type:
            query = query.filter(Prediction.prediction_type == prediction_type)

        if only_valid:
            now = datetime.utcnow()
            query = query.filter(
                Prediction.valid_from <= now,
                Prediction.valid_until >= now,
            )

        query = query.order_by(Prediction.created_at.desc()).limit(limit)
        return await query.all()

    async def complete_prediction(
        self,
        prediction: Prediction,
        value: Optional[float] = None,
        label: Optional[str] = None,
        confidence: Optional[float] = None,
        probabilities: Optional[dict] = None,
        explanation: Optional[str] = None,
        feature_importance: Optional[dict] = None,
        processing_time_ms: Optional[int] = None,
    ) -> Prediction:
        """Completa uma previsao com resultados.

        Args:
            prediction: Previsao a completar.
            value: Valor previsto.
            label: Label prevista.
            confidence: Score de confianca.
            probabilities: Probabilidades.
            explanation: Explicacao.
            feature_importance: Importancia das features.
            processing_time_ms: Tempo de processamento.

        Returns:
            Previsao atualizada.
        """
        prediction.complete(
            value=value,
            label=label,
            confidence=confidence,
            probabilities=probabilities,
            processing_time_ms=processing_time_ms,
        )
        prediction.explanation = explanation
        prediction.feature_importance = feature_importance

        await self.db.commit()
        await self.db.refresh(prediction)

        # Atualiza metricas do modelo
        if prediction.model_id:
            model = await self.db.query(MLModel).filter(MLModel.id == prediction.model_id).first()
            if model:
                model.record_prediction(True, processing_time_ms)
                await self.db.commit()

        logger.info(
            "Prediction completed",
            extra={
                "prediction_id": str(prediction.id),
                "confidence": confidence,
                "processing_time_ms": processing_time_ms,
            },
        )

        return prediction

    async def fail_prediction(
        self,
        prediction: Prediction,
        error_message: str,
    ) -> Prediction:
        """Marca previsao como falha.

        Args:
            prediction: Previsao.
            error_message: Mensagem de erro.

        Returns:
            Previsao atualizada.
        """
        prediction.fail(error_message)
        await self.db.commit()

        # Atualiza metricas do modelo
        if prediction.model_id:
            model = await self.db.query(MLModel).filter(MLModel.id == prediction.model_id).first()
            if model:
                model.record_prediction(False)
                await self.db.commit()

        logger.error(
            "Prediction failed",
            extra={
                "prediction_id": str(prediction.id),
                "error": error_message,
            },
        )

        return prediction

    async def add_feedback(
        self,
        prediction: Prediction,
        actual_value: Optional[float] = None,
        actual_label: Optional[str] = None,
        user_id: Optional[UUID] = None,
        notes: Optional[str] = None,
    ) -> Prediction:
        """Adiciona feedback a uma previsao.

        Args:
            prediction: Previsao.
            actual_value: Valor real.
            actual_label: Label real.
            user_id: ID do usuario.
            notes: Notas.

        Returns:
            Previsao atualizada.
        """
        prediction.add_feedback(
            actual_value=actual_value,
            actual_label=actual_label,
            user_id=str(user_id) if user_id else None,
            notes=notes,
        )
        await self.db.commit()
        await self.db.refresh(prediction)

        logger.info(
            "Feedback added to prediction",
            extra={
                "prediction_id": str(prediction.id),
                "is_correct": prediction.is_correct,
                "absolute_error": prediction.absolute_error,
            },
        )

        return prediction

    async def get_model_for_prediction(
        self,
        tenant_id: UUID,
        prediction_type: PredictionType,
    ) -> Optional[MLModel]:
        """Busca modelo para um tipo de previsao.

        Args:
            tenant_id: ID do tenant.
            prediction_type: Tipo de previsao.

        Returns:
            Modelo ou None.
        """
        # Mapeia tipo de previsao para tipo de modelo
        type_mapping = {
            PredictionType.CHURN: "churn",
            PredictionType.REVENUE_FORECAST: "revenue",
            PredictionType.EXPENSE_FORECAST: "expense",
            PredictionType.DEMAND_FORECAST: "demand",
            PredictionType.LEAD_SCORING: "lead_scoring",
            PredictionType.CREDIT_RISK: "credit_risk",
            PredictionType.ANOMALY: "anomaly",
        }

        slug = type_mapping.get(prediction_type, prediction_type.value.lower())

        # Busca modelo default para o tipo
        model = await (
            self.db.query(MLModel)
            .filter(MLModel.tenant_id == tenant_id)
            .filter(MLModel.slug.ilike(f"%{slug}%"))
            .filter(MLModel.status == ModelStatus.DEPLOYED)
            .filter(MLModel.is_default == True)  # noqa: E712
            .first()
        )

        if not model:
            # Busca qualquer modelo deployed para o tipo
            model = await (
                self.db.query(MLModel)
                .filter(MLModel.tenant_id == tenant_id)
                .filter(MLModel.slug.ilike(f"%{slug}%"))
                .filter(MLModel.status == ModelStatus.DEPLOYED)
                .order_by(MLModel.deployed_at.desc())
                .first()
            )

        return model

    async def get_prediction_stats(
        self,
        tenant_id: UUID,
        days: int = 30,
        prediction_type: Optional[PredictionType] = None,
    ) -> dict:
        """Retorna estatisticas de previsoes.

        Args:
            tenant_id: ID do tenant.
            days: Dias para analisar.
            prediction_type: Filtrar por tipo.

        Returns:
            Dicionario com estatisticas.
        """
        since = datetime.utcnow() - timedelta(days=days)

        query = (
            self.db.query(Prediction)
            .filter(Prediction.tenant_id == tenant_id)
            .filter(Prediction.created_at >= since)
        )

        if prediction_type:
            query = query.filter(Prediction.prediction_type == prediction_type)

        predictions = await query.all()

        total = len(predictions)
        completed = len([p for p in predictions if p.status == PredictionStatus.COMPLETED])
        failed = len([p for p in predictions if p.status == PredictionStatus.FAILED])
        with_feedback = len([p for p in predictions if p.has_feedback])

        # Calcula metricas de qualidade
        correct_predictions = [p for p in predictions if p.is_correct is True]
        incorrect_predictions = [p for p in predictions if p.is_correct is False]

        accuracy = 0.0
        if correct_predictions or incorrect_predictions:
            accuracy = len(correct_predictions) / (
                len(correct_predictions) + len(incorrect_predictions)
            )

        # Calcula erro medio
        errors = [p.percentage_error for p in predictions if p.percentage_error is not None]
        avg_error = sum(errors) / len(errors) if errors else None

        # Tempo medio de processamento
        times = [p.processing_time_ms for p in predictions if p.processing_time_ms]
        avg_time = sum(times) / len(times) if times else None

        return {
            "period_days": days,
            "total_predictions": total,
            "completed": completed,
            "failed": failed,
            "success_rate": (completed / total * 100) if total else 0,
            "with_feedback": with_feedback,
            "feedback_rate": (with_feedback / completed * 100) if completed else 0,
            "accuracy": accuracy * 100,
            "avg_percentage_error": avg_error,
            "avg_processing_time_ms": avg_time,
            "by_type": self._group_by_type(predictions),
        }

    def _group_by_type(self, predictions: list[Prediction]) -> dict:
        """Agrupa previsoes por tipo.

        Args:
            predictions: Lista de previsoes.

        Returns:
            Dicionario agrupado.
        """
        result = {}
        for pred in predictions:
            type_name = pred.prediction_type.value
            if type_name not in result:
                result[type_name] = {"count": 0, "completed": 0, "failed": 0}
            result[type_name]["count"] += 1
            if pred.status == PredictionStatus.COMPLETED:
                result[type_name]["completed"] += 1
            elif pred.status == PredictionStatus.FAILED:
                result[type_name]["failed"] += 1
        return result

    async def expire_old_predictions(
        self,
        tenant_id: Optional[UUID] = None,
    ) -> int:
        """Expira previsoes antigas.

        Args:
            tenant_id: ID do tenant (None = todos).

        Returns:
            Numero de previsoes expiradas.
        """
        now = datetime.utcnow()
        query = (
            self.db.query(Prediction)
            .filter(Prediction.valid_until < now)
            .filter(Prediction.status == PredictionStatus.COMPLETED)
            .filter(Prediction.active == True)  # noqa: E712
        )

        if tenant_id:
            query = query.filter(Prediction.tenant_id == tenant_id)

        predictions = await query.all()
        for pred in predictions:
            pred.expire()

        await self.db.commit()

        logger.info(
            "Expired old predictions",
            extra={"count": len(predictions)},
        )

        return len(predictions)
