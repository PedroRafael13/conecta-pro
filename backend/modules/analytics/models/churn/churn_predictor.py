"""Modelo de predição de churn de clientes."""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from modules.analytics.ml.features.feature_store import FeatureStore
from modules.analytics.ml.registry.model_registry import (
    ModelFramework,
    ModelMetrics,
    ModelRegistry,
    ModelStage,
    ModelType,
)
from modules.analytics.ml.training.training_pipeline import (
    DataSplit,
    TrainingConfig,
    TrainingPipeline,
)

logger = logging.getLogger(__name__)


class ChurnRiskLevel(Enum):
    """Níveis de risco de churn."""

    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RetentionActionType(Enum):
    """Tipos de ações de retenção."""

    DISCOUNT = "discount"
    PERSONALIZED_OFFER = "personalized_offer"
    ENGAGEMENT_CAMPAIGN = "engagement_campaign"
    SUPPORT_OUTREACH = "support_outreach"
    LOYALTY_REWARD = "loyalty_reward"
    FEATURE_EDUCATION = "feature_education"
    SURVEY = "survey"
    VIP_UPGRADE = "vip_upgrade"


@dataclass
class RetentionAction:
    """Ação de retenção sugerida."""

    action_type: RetentionActionType
    priority: int  # 1-5
    description: str
    expected_impact: float  # 0-1
    cost_estimate: float
    target_segment: str
    recommended_timing: str


@dataclass
class ChurnPrediction:
    """Resultado da predição de churn."""

    id: UUID
    user_id: int
    churn_probability: float
    risk_level: ChurnRiskLevel
    confidence: float
    contributing_factors: list[dict[str, Any]]
    retention_actions: list[RetentionAction]
    predicted_churn_date: Optional[datetime] = None
    lifetime_value_at_risk: float = 0.0
    model_version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ChurnAnalytics:
    """Analytics agregadas de churn."""

    total_users: int
    at_risk_users: int
    churn_rate_30d: float
    churn_rate_90d: float
    avg_churn_probability: float
    ltv_at_risk: float
    risk_distribution: dict[str, int]
    top_churn_factors: list[dict[str, Any]]
    trend: str  # improving, stable, worsening
    period_start: datetime
    period_end: datetime


class ChurnPredictor:
    """
    Sistema de predição de churn.

    Funcionalidades:
    - Predição de probabilidade de churn
    - Classificação de risco
    - Identificação de fatores contribuintes
    - Recomendação de ações de retenção
    - Analytics de churn em tempo real
    """

    # Features usadas para predição
    CHURN_FEATURES = [
        "tenure_days",
        "total_spent",
        "avg_order_value",
        "order_frequency",
        "last_activity_days",
        "login_frequency",
        "session_duration_avg",
        "pages_per_session",
        "notification_response_rate",
        "transaction_count_30d",
        "transaction_value_30d",
        "refund_rate",
    ]

    # Thresholds de risco
    RISK_THRESHOLDS = {
        ChurnRiskLevel.VERY_LOW: 0.1,
        ChurnRiskLevel.LOW: 0.25,
        ChurnRiskLevel.MEDIUM: 0.5,
        ChurnRiskLevel.HIGH: 0.75,
        ChurnRiskLevel.CRITICAL: 1.0,
    }

    def __init__(
        self,
        feature_store: Optional[FeatureStore] = None,
        model_registry: Optional[ModelRegistry] = None,
    ) -> None:
        """
        Inicializa o preditor de churn.

        Args:
            feature_store: Store de features
            model_registry: Registry de modelos
        """
        self.feature_store = feature_store or FeatureStore()
        self.model_registry = model_registry or ModelRegistry()
        self.training_pipeline = TrainingPipeline(self.model_registry)
        self._model = None
        self._model_version = None

    async def predict(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> ChurnPrediction:
        """
        Prediz probabilidade de churn para um usuário.

        Args:
            db: Sessão do banco
            user_id: ID do usuário

        Returns:
            ChurnPrediction com análise completa
        """
        logger.info(f"Predizendo churn para usuário {user_id}")

        # Obter features do usuário
        features = await self._get_user_features(db, user_id)

        # Carregar modelo
        model = self._load_model()

        # Fazer predição
        if model:
            X = pd.DataFrame([features])
            churn_prob = model.predict_proba(X)[0][1]
            confidence = self._calculate_confidence(model, X)
        else:
            # Modelo baseado em regras se ML não disponível
            churn_prob = self._rule_based_prediction(features)
            confidence = 0.7

        # Classificar risco
        risk_level = self._classify_risk(churn_prob)

        # Identificar fatores contribuintes
        contributing_factors = self._identify_contributing_factors(
            features, model
        )

        # Gerar ações de retenção
        retention_actions = self._generate_retention_actions(
            risk_level, contributing_factors, features
        )

        # Estimar data de churn
        predicted_churn_date = self._estimate_churn_date(
            churn_prob, features.get("last_activity_days", 0)
        )

        # Calcular LTV em risco
        ltv_at_risk = self._calculate_ltv_at_risk(
            churn_prob, features.get("total_spent", 0)
        )

        return ChurnPrediction(
            id=uuid4(),
            user_id=user_id,
            churn_probability=round(churn_prob, 4),
            risk_level=risk_level,
            confidence=round(confidence, 4),
            contributing_factors=contributing_factors,
            retention_actions=retention_actions,
            predicted_churn_date=predicted_churn_date,
            lifetime_value_at_risk=round(ltv_at_risk, 2),
            model_version=self._model_version or "rules_v1",
        )

    async def predict_batch(
        self,
        db: AsyncSession,
        user_ids: list[int],
    ) -> list[ChurnPrediction]:
        """
        Prediz churn para múltiplos usuários.

        Args:
            db: Sessão do banco
            user_ids: Lista de IDs

        Returns:
            Lista de predições
        """
        predictions = []
        for user_id in user_ids:
            try:
                pred = await self.predict(db, user_id)
                predictions.append(pred)
            except Exception as e:
                logger.error(f"Erro na predição para user {user_id}: {e}")
        return predictions

    async def get_high_risk_users(
        self,
        db: AsyncSession,
        limit: int = 100,
        min_risk_level: ChurnRiskLevel = ChurnRiskLevel.HIGH,
    ) -> list[ChurnPrediction]:
        """
        Obtém usuários com alto risco de churn.

        Args:
            db: Sessão do banco
            limit: Máximo de usuários
            min_risk_level: Risco mínimo

        Returns:
            Lista de predições de alto risco
        """
        # Em produção, isso viria de cache ou batch prediction
        # Simulação para desenvolvimento
        all_user_ids = await self._get_active_user_ids(db, limit * 2)

        predictions = await self.predict_batch(db, all_user_ids)

        # Filtrar por risco
        risk_order = list(ChurnRiskLevel)
        min_index = risk_order.index(min_risk_level)

        high_risk = [
            p for p in predictions
            if risk_order.index(p.risk_level) >= min_index
        ]

        # Ordenar por probabilidade
        high_risk.sort(key=lambda x: x.churn_probability, reverse=True)

        return high_risk[:limit]

    async def get_churn_analytics(
        self,
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> ChurnAnalytics:
        """
        Obtém analytics agregadas de churn.

        Args:
            db: Sessão do banco
            start_date: Data inicial
            end_date: Data final

        Returns:
            ChurnAnalytics com métricas agregadas
        """
        end_date = end_date or datetime.utcnow()
        start_date = start_date or (end_date - timedelta(days=30))

        # Em produção, viria de tabelas agregadas
        # Simulação para desenvolvimento
        total_users = 1000
        predictions = await self._get_sample_predictions(db, 200)

        risk_distribution = {level.value: 0 for level in ChurnRiskLevel}
        for pred in predictions:
            risk_distribution[pred.risk_level.value] += 1

        at_risk = risk_distribution[ChurnRiskLevel.HIGH.value] + \
                  risk_distribution[ChurnRiskLevel.CRITICAL.value]

        avg_prob = np.mean([p.churn_probability for p in predictions])
        ltv_at_risk = sum(p.lifetime_value_at_risk for p in predictions)

        # Identificar top fatores
        all_factors = []
        for pred in predictions:
            all_factors.extend(pred.contributing_factors)

        factor_counts = {}
        for f in all_factors:
            name = f.get("factor", "unknown")
            factor_counts[name] = factor_counts.get(name, 0) + 1

        top_factors = [
            {"factor": k, "count": v, "percentage": v / len(predictions) * 100}
            for k, v in sorted(
                factor_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        ]

        return ChurnAnalytics(
            total_users=total_users,
            at_risk_users=at_risk,
            churn_rate_30d=round(at_risk / total_users * 100, 2),
            churn_rate_90d=round(at_risk / total_users * 100 * 1.5, 2),
            avg_churn_probability=round(avg_prob, 4),
            ltv_at_risk=round(ltv_at_risk, 2),
            risk_distribution=risk_distribution,
            top_churn_factors=top_factors,
            trend=self._calculate_trend(predictions),
            period_start=start_date,
            period_end=end_date,
        )

    async def train_model(
        self,
        db: AsyncSession,
        training_data: Optional[pd.DataFrame] = None,
        version: str = "1.0.0",
    ) -> dict[str, Any]:
        """
        Treina ou re-treina o modelo de churn.

        Args:
            db: Sessão do banco
            training_data: Dados de treinamento (se None, gera sintético)
            version: Versão do modelo

        Returns:
            Resultado do treinamento
        """
        logger.info("Iniciando treinamento do modelo de churn")

        # Obter ou gerar dados de treinamento
        if training_data is None:
            training_data = await self._generate_training_data(db)

        # Configurar treinamento
        config = TrainingConfig(
            model_name="churn_predictor",
            model_type=ModelType.CLASSIFICATION,
            framework=ModelFramework.SKLEARN,
            target_column="churned",
            feature_columns=self.CHURN_FEATURES,
            test_size=0.2,
            val_size=0.1,
            cv_folds=5,
            metrics=["accuracy", "precision", "recall", "f1_score", "auc_roc"],
        )

        # Preparar dados
        data = self.training_pipeline.prepare_data(training_data, config)

        # Treinar múltiplos modelos
        models = [
            ("logistic", LogisticRegression(max_iter=1000)),
            ("random_forest", RandomForestClassifier(n_estimators=100)),
            ("gradient_boosting", GradientBoostingClassifier(n_estimators=100)),
        ]

        results = self.training_pipeline.train_with_automl(
            training_data, config, models, version
        )

        # Promover melhor modelo para produção
        if results and results[0].status == "success":
            best = results[0]
            self.model_registry.promote_model(
                name="churn_predictor",
                version=version,
                target_stage=ModelStage.PRODUCTION,
            )

            self._model = None  # Forçar reload
            self._model_version = version

        return {
            "status": "success" if results else "failed",
            "best_model": results[0].model_name if results else None,
            "metrics": results[0].metrics.to_dict() if results else {},
            "version": version,
            "training_samples": len(training_data),
        }

    async def _get_user_features(
        self,
        db: AsyncSession,
        user_id: int,
    ) -> dict[str, Any]:
        """Obtém features de um usuário."""
        # Usar Feature Store
        user_features = await self.feature_store.get_user_features(
            db, user_id, include=self.CHURN_FEATURES[:6]
        )

        engagement_features = await self.feature_store.get_engagement_features(
            db, user_id, include=self.CHURN_FEATURES[6:9]
        )

        transaction_features = await self.feature_store.get_transaction_features(
            db, user_id, include=self.CHURN_FEATURES[9:]
        )

        # Combinar features
        features = {}
        for f in self.CHURN_FEATURES:
            if f in user_features:
                features[f] = user_features[f]
            elif f in engagement_features:
                features[f] = engagement_features[f]
            elif f in transaction_features:
                features[f] = transaction_features[f]
            else:
                features[f] = 0  # Default

        return features

    def _load_model(self) -> Optional[Any]:
        """Carrega modelo de produção."""
        if self._model is None:
            self._model = self.model_registry.get_production_model("churn_predictor")
            if self._model:
                version = self.model_registry.get_model_version(
                    "churn_predictor",
                    stage=ModelStage.PRODUCTION
                )
                self._model_version = version.version if version else None

        return self._model

    def _rule_based_prediction(self, features: dict) -> float:
        """Predição baseada em regras quando não há modelo ML."""
        score = 0.0

        # Inatividade aumenta risco
        last_activity = features.get("last_activity_days", 0)
        if last_activity > 30:
            score += 0.3
        elif last_activity > 14:
            score += 0.15

        # Baixa frequência de login
        login_freq = features.get("login_frequency", 0)
        if login_freq < 2:
            score += 0.2
        elif login_freq < 5:
            score += 0.1

        # Queda em transações
        tx_count = features.get("transaction_count_30d", 0)
        if tx_count == 0:
            score += 0.25
        elif tx_count < 2:
            score += 0.1

        # Taxa de reembolso alta
        refund_rate = features.get("refund_rate", 0)
        if refund_rate > 0.1:
            score += 0.15

        # Baixo engagement
        notification_rate = features.get("notification_response_rate", 0)
        if notification_rate < 0.2:
            score += 0.1

        return min(score, 0.95)

    def _calculate_confidence(self, model: Any, X: pd.DataFrame) -> float:
        """Calcula confiança da predição."""
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X)[0]
            # Confiança é quão longe de 0.5 está
            return abs(proba[1] - 0.5) * 2
        return 0.7

    def _classify_risk(self, probability: float) -> ChurnRiskLevel:
        """Classifica nível de risco baseado na probabilidade."""
        for level, threshold in self.RISK_THRESHOLDS.items():
            if probability <= threshold:
                return level
        return ChurnRiskLevel.CRITICAL

    def _identify_contributing_factors(
        self,
        features: dict,
        model: Any,
    ) -> list[dict[str, Any]]:
        """Identifica fatores que contribuem para o risco."""
        factors = []

        # Feature importance do modelo
        if model and hasattr(model, "feature_importances_"):
            importances = dict(zip(
                self.CHURN_FEATURES,
                model.feature_importances_
            ))
            sorted_features = sorted(
                importances.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

            for feature, importance in sorted_features:
                value = features.get(feature, 0)
                factors.append({
                    "factor": feature,
                    "value": value,
                    "importance": round(importance, 4),
                    "direction": self._get_factor_direction(feature, value),
                })
        else:
            # Análise baseada em regras
            if features.get("last_activity_days", 0) > 14:
                factors.append({
                    "factor": "last_activity_days",
                    "value": features["last_activity_days"],
                    "importance": 0.25,
                    "direction": "negative",
                    "insight": "Inatividade prolongada",
                })

            if features.get("login_frequency", 0) < 5:
                factors.append({
                    "factor": "login_frequency",
                    "value": features["login_frequency"],
                    "importance": 0.2,
                    "direction": "negative",
                    "insight": "Baixa frequência de acesso",
                })

            if features.get("transaction_count_30d", 0) < 2:
                factors.append({
                    "factor": "transaction_count_30d",
                    "value": features["transaction_count_30d"],
                    "importance": 0.2,
                    "direction": "negative",
                    "insight": "Poucas transações recentes",
                })

        return factors

    def _get_factor_direction(self, feature: str, value: float) -> str:
        """Determina se o valor do fator contribui positiva ou negativamente."""
        negative_thresholds = {
            "last_activity_days": 14,
            "login_frequency": 5,
            "transaction_count_30d": 2,
            "notification_response_rate": 0.3,
            "session_duration_avg": 120,
        }

        if feature in negative_thresholds:
            return "negative" if value > negative_thresholds[feature] else "positive"
        return "neutral"

    def _generate_retention_actions(
        self,
        risk_level: ChurnRiskLevel,
        factors: list[dict],
        features: dict,
    ) -> list[RetentionAction]:
        """Gera ações de retenção personalizadas."""
        actions = []

        # Ações baseadas no nível de risco
        if risk_level in [ChurnRiskLevel.CRITICAL, ChurnRiskLevel.HIGH]:
            actions.append(RetentionAction(
                action_type=RetentionActionType.PERSONALIZED_OFFER,
                priority=1,
                description="Oferta personalizada com desconto de 30%",
                expected_impact=0.35,
                cost_estimate=50.0,
                target_segment="high_risk",
                recommended_timing="imediato",
            ))

            actions.append(RetentionAction(
                action_type=RetentionActionType.SUPPORT_OUTREACH,
                priority=2,
                description="Contato proativo do suporte",
                expected_impact=0.25,
                cost_estimate=20.0,
                target_segment="high_risk",
                recommended_timing="dentro de 24h",
            ))

        if risk_level == ChurnRiskLevel.MEDIUM:
            actions.append(RetentionAction(
                action_type=RetentionActionType.ENGAGEMENT_CAMPAIGN,
                priority=1,
                description="Campanha de re-engajamento por email",
                expected_impact=0.2,
                cost_estimate=5.0,
                target_segment="medium_risk",
                recommended_timing="próximos 3 dias",
            ))

        # Ações baseadas em fatores específicos
        for factor in factors:
            if factor["factor"] == "last_activity_days" and factor.get("direction") == "negative":
                actions.append(RetentionAction(
                    action_type=RetentionActionType.FEATURE_EDUCATION,
                    priority=3,
                    description="Email destacando novos recursos",
                    expected_impact=0.15,
                    cost_estimate=2.0,
                    target_segment="inactive",
                    recommended_timing="próxima semana",
                ))

            if factor["factor"] == "notification_response_rate" and factor.get("direction") == "negative":
                actions.append(RetentionAction(
                    action_type=RetentionActionType.SURVEY,
                    priority=4,
                    description="Pesquisa de preferências de comunicação",
                    expected_impact=0.1,
                    cost_estimate=1.0,
                    target_segment="low_engagement",
                    recommended_timing="próximos 7 dias",
                ))

        # LTV alto merece ação premium
        if features.get("total_spent", 0) > 5000:
            actions.append(RetentionAction(
                action_type=RetentionActionType.VIP_UPGRADE,
                priority=1,
                description="Upgrade para programa VIP",
                expected_impact=0.4,
                cost_estimate=100.0,
                target_segment="high_value",
                recommended_timing="imediato",
            ))

        # Ordenar por prioridade
        actions.sort(key=lambda x: x.priority)

        return actions[:5]  # Máximo 5 ações

    def _estimate_churn_date(
        self,
        probability: float,
        last_activity_days: int,
    ) -> Optional[datetime]:
        """Estima data provável de churn."""
        if probability < 0.3:
            return None

        # Quanto maior a probabilidade e inatividade, mais próximo
        base_days = 90 - (probability * 60) - (last_activity_days * 0.5)
        days_to_churn = max(7, int(base_days))

        return datetime.utcnow() + timedelta(days=days_to_churn)

    def _calculate_ltv_at_risk(
        self,
        probability: float,
        total_spent: float,
    ) -> float:
        """Calcula valor em risco de churn."""
        # Estimar LTV futuro baseado em gasto atual
        estimated_future_ltv = total_spent * 1.5
        return probability * estimated_future_ltv

    async def _get_active_user_ids(
        self,
        db: AsyncSession,
        limit: int,
    ) -> list[int]:
        """Obtém IDs de usuários ativos."""
        # Em produção, query real
        # Simulação para desenvolvimento
        return list(range(1, min(limit + 1, 201)))

    async def _get_sample_predictions(
        self,
        db: AsyncSession,
        sample_size: int,
    ) -> list[ChurnPrediction]:
        """Obtém sample de predições para analytics."""
        user_ids = await self._get_active_user_ids(db, sample_size)
        return await self.predict_batch(db, user_ids[:sample_size])

    async def _generate_training_data(
        self,
        db: AsyncSession,
        n_samples: int = 1000,
    ) -> pd.DataFrame:
        """Gera dados sintéticos para treinamento."""
        np.random.seed(42)

        data = {
            "user_id": range(1, n_samples + 1),
            "churned": np.random.binomial(1, 0.2, n_samples),
        }

        for feature in self.CHURN_FEATURES:
            if feature == "tenure_days":
                data[feature] = np.random.randint(30, 730, n_samples)
            elif feature == "total_spent":
                data[feature] = np.random.uniform(100, 10000, n_samples)
            elif feature == "avg_order_value":
                data[feature] = np.random.uniform(50, 500, n_samples)
            elif feature == "order_frequency":
                data[feature] = np.random.randint(1, 50, n_samples)
            elif feature == "last_activity_days":
                data[feature] = np.random.randint(0, 60, n_samples)
            elif feature == "login_frequency":
                data[feature] = np.random.randint(0, 30, n_samples)
            elif feature == "session_duration_avg":
                data[feature] = np.random.uniform(60, 1800, n_samples)
            elif feature == "pages_per_session":
                data[feature] = np.random.uniform(1, 20, n_samples)
            elif feature == "notification_response_rate":
                data[feature] = np.random.uniform(0.1, 0.9, n_samples)
            elif feature == "transaction_count_30d":
                data[feature] = np.random.randint(0, 20, n_samples)
            elif feature == "transaction_value_30d":
                data[feature] = np.random.uniform(0, 5000, n_samples)
            elif feature == "refund_rate":
                data[feature] = np.random.uniform(0, 0.2, n_samples)

        df = pd.DataFrame(data)

        # Ajustar churn baseado em features (correlação)
        mask = (
            (df["last_activity_days"] > 30) &
            (df["login_frequency"] < 5) &
            (df["transaction_count_30d"] < 2)
        )
        df.loc[mask, "churned"] = np.random.binomial(1, 0.7, mask.sum())

        return df

    def _calculate_trend(self, predictions: list[ChurnPrediction]) -> str:
        """Calcula tendência de churn."""
        if not predictions:
            return "stable"

        # Dividir em duas metades
        mid = len(predictions) // 2
        first_half = predictions[:mid]
        second_half = predictions[mid:]

        avg_first = np.mean([p.churn_probability for p in first_half])
        avg_second = np.mean([p.churn_probability for p in second_half])

        diff = avg_second - avg_first

        if diff > 0.05:
            return "worsening"
        elif diff < -0.05:
            return "improving"
        return "stable"
