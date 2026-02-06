"""ChurnPredictor - Previsao de Churn de Clientes.

Sprint 34 - AI Predictions.
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID

# Note: Prediction and PredictionType used in type hints only

logger = logging.getLogger(__name__)


@dataclass
class ChurnFactors:
    """Fatores que influenciam o churn."""

    # Engajamento
    days_since_last_interaction: int = 0
    interaction_frequency: float = 0.0  # interacoes/mes
    support_tickets_count: int = 0
    unresolved_issues: int = 0

    # Financeiro
    payment_delays_count: int = 0
    avg_payment_delay_days: float = 0.0
    contract_value: float = 0.0
    value_trend: float = 0.0  # % mudanca no valor

    # Satisfacao
    nps_score: Optional[float] = None
    csat_score: Optional[float] = None
    complaints_count: int = 0

    # Contrato
    contract_age_months: int = 0
    days_until_renewal: Optional[int] = None
    renewal_count: int = 0

    # Uso
    feature_usage_rate: float = 0.0
    login_frequency: float = 0.0
    api_calls_trend: float = 0.0


@dataclass
class ChurnPrediction:
    """Resultado da previsao de churn."""

    churn_probability: float  # 0-1
    churn_risk_level: str  # low, medium, high, critical
    confidence: float  # 0-1
    main_factors: list  # fatores principais
    recommendations: list  # acoes recomendadas
    expected_churn_date: Optional[datetime] = None
    lifetime_value_at_risk: float = 0.0


class ChurnPredictor:
    """Preditor de churn de clientes."""

    # Pesos dos fatores (soma = 1.0)
    WEIGHTS = {
        "engagement": 0.25,
        "financial": 0.20,
        "satisfaction": 0.25,
        "contract": 0.15,
        "usage": 0.15,
    }

    # Thresholds de risco
    RISK_THRESHOLDS = {
        "low": 0.25,
        "medium": 0.50,
        "high": 0.75,
        "critical": 1.0,
    }

    def __init__(self, db_session: Any):
        """Inicializa o preditor.

        Args:
            db_session: Sessao do banco de dados.
        """
        self.db = db_session

    async def predict_churn(
        self,
        tenant_id: UUID,
        client_id: UUID,
        factors: Optional[ChurnFactors] = None,
    ) -> ChurnPrediction:
        """Preve probabilidade de churn para um cliente.

        Args:
            tenant_id: ID do tenant.
            client_id: ID do cliente.
            factors: Fatores de churn (opcional, busca se nao fornecido).

        Returns:
            Previsao de churn.
        """
        start_time = time.time()

        # Busca ou usa fatores fornecidos
        if factors is None:
            factors = await self._collect_factors(tenant_id, client_id)

        # Calcula scores por categoria
        engagement_score = self._calculate_engagement_score(factors)
        financial_score = self._calculate_financial_score(factors)
        satisfaction_score = self._calculate_satisfaction_score(factors)
        contract_score = self._calculate_contract_score(factors)
        usage_score = self._calculate_usage_score(factors)

        # Score ponderado
        weighted_score = (
            engagement_score * self.WEIGHTS["engagement"]
            + financial_score * self.WEIGHTS["financial"]
            + satisfaction_score * self.WEIGHTS["satisfaction"]
            + contract_score * self.WEIGHTS["contract"]
            + usage_score * self.WEIGHTS["usage"]
        )

        # Normaliza para 0-1
        churn_probability = min(max(weighted_score, 0.0), 1.0)

        # Determina nivel de risco
        risk_level = self._get_risk_level(churn_probability)

        # Calcula confianca baseado na quantidade de dados
        confidence = self._calculate_confidence(factors)

        # Identifica principais fatores
        main_factors = self._identify_main_factors(
            factors,
            {
                "engagement": engagement_score,
                "financial": financial_score,
                "satisfaction": satisfaction_score,
                "contract": contract_score,
                "usage": usage_score,
            },
        )

        # Gera recomendacoes
        recommendations = self._generate_recommendations(
            factors,
            risk_level,
            main_factors,
        )

        # Estima data de churn
        expected_churn_date = self._estimate_churn_date(
            factors,
            churn_probability,
        )

        # Calcula valor em risco
        ltv_at_risk = self._calculate_ltv_at_risk(
            factors,
            churn_probability,
        )

        processing_time = int((time.time() - start_time) * 1000)

        logger.info(
            "Churn prediction completed",
            extra={
                "client_id": str(client_id),
                "probability": churn_probability,
                "risk_level": risk_level,
                "processing_time_ms": processing_time,
            },
        )

        return ChurnPrediction(
            churn_probability=round(churn_probability, 4),
            churn_risk_level=risk_level,
            confidence=round(confidence, 4),
            main_factors=main_factors,
            recommendations=recommendations,
            expected_churn_date=expected_churn_date,
            lifetime_value_at_risk=round(ltv_at_risk, 2),
        )

    async def predict_churn_batch(
        self,
        tenant_id: UUID,
        client_ids: list[UUID],
    ) -> dict[UUID, ChurnPrediction]:
        """Preve churn para multiplos clientes.

        Args:
            tenant_id: ID do tenant.
            client_ids: Lista de IDs de clientes.

        Returns:
            Dicionario com previsoes por cliente.
        """
        results = {}
        for client_id in client_ids:
            try:
                prediction = await self.predict_churn(tenant_id, client_id)
                results[client_id] = prediction
            except Exception as e:
                logger.error(
                    "Churn prediction failed for client",
                    extra={"client_id": str(client_id), "error": str(e)},
                )
        return results

    async def _collect_factors(
        self,
        tenant_id: UUID,
        client_id: UUID,
    ) -> ChurnFactors:
        """Coleta fatores de churn do banco de dados.

        Args:
            tenant_id: ID do tenant.
            client_id: ID do cliente.

        Returns:
            Fatores de churn.
        """
        # Em producao, isso buscaria dados reais do banco
        # Aqui retornamos fatores simulados para demonstracao
        return ChurnFactors(
            days_since_last_interaction=15,
            interaction_frequency=2.5,
            support_tickets_count=3,
            unresolved_issues=1,
            payment_delays_count=0,
            avg_payment_delay_days=0,
            contract_value=5000.0,
            value_trend=-5.0,
            nps_score=7.0,
            csat_score=3.5,
            complaints_count=1,
            contract_age_months=18,
            days_until_renewal=45,
            renewal_count=1,
            feature_usage_rate=0.6,
            login_frequency=3.0,
            api_calls_trend=-10.0,
        )

    def _calculate_engagement_score(self, factors: ChurnFactors) -> float:
        """Calcula score de engajamento (0-1, maior = mais risco).

        Args:
            factors: Fatores de churn.

        Returns:
            Score de engajamento.
        """
        score = 0.0

        # Dias desde ultima interacao (max 90 dias = score 1)
        score += min(factors.days_since_last_interaction / 90, 1.0) * 0.4

        # Frequencia de interacao (inverso, menos interacao = mais risco)
        if factors.interaction_frequency < 1:
            score += 0.3
        elif factors.interaction_frequency < 3:
            score += 0.15

        # Tickets de suporte (muitos pode indicar frustacao)
        if factors.support_tickets_count > 5:
            score += 0.2
        elif factors.support_tickets_count > 2:
            score += 0.1

        # Issues nao resolvidos
        if factors.unresolved_issues > 0:
            score += min(factors.unresolved_issues * 0.1, 0.1)

        return min(score, 1.0)

    def _calculate_financial_score(self, factors: ChurnFactors) -> float:
        """Calcula score financeiro (0-1, maior = mais risco).

        Args:
            factors: Fatores de churn.

        Returns:
            Score financeiro.
        """
        score = 0.0

        # Atrasos de pagamento
        if factors.payment_delays_count > 3:
            score += 0.4
        elif factors.payment_delays_count > 0:
            score += 0.2

        # Media de dias de atraso
        if factors.avg_payment_delay_days > 30:
            score += 0.3
        elif factors.avg_payment_delay_days > 15:
            score += 0.15

        # Tendencia de valor (negativa = risco)
        if factors.value_trend < -20:
            score += 0.3
        elif factors.value_trend < -10:
            score += 0.15
        elif factors.value_trend < 0:
            score += 0.05

        return min(score, 1.0)

    def _calculate_satisfaction_score(self, factors: ChurnFactors) -> float:
        """Calcula score de satisfacao (0-1, maior = mais risco).

        Args:
            factors: Fatores de churn.

        Returns:
            Score de satisfacao.
        """
        score = 0.0

        # NPS (0-10, menor = mais risco)
        if factors.nps_score is not None:
            if factors.nps_score < 6:  # Detrator
                score += 0.4
            elif factors.nps_score < 8:  # Neutro
                score += 0.2

        # CSAT (1-5, menor = mais risco)
        if factors.csat_score is not None:
            if factors.csat_score < 3:
                score += 0.3
            elif factors.csat_score < 4:
                score += 0.15

        # Reclamacoes
        if factors.complaints_count > 3:
            score += 0.3
        elif factors.complaints_count > 0:
            score += 0.15

        return min(score, 1.0)

    def _calculate_contract_score(self, factors: ChurnFactors) -> float:
        """Calcula score de contrato (0-1, maior = mais risco).

        Args:
            factors: Fatores de churn.

        Returns:
            Score de contrato.
        """
        score = 0.0

        # Idade do contrato (novos tem mais risco)
        if factors.contract_age_months < 6:
            score += 0.3
        elif factors.contract_age_months < 12:
            score += 0.15

        # Dias ate renovacao (proximo = decisao iminente)
        if factors.days_until_renewal is not None:
            if factors.days_until_renewal < 30:
                score += 0.4
            elif factors.days_until_renewal < 60:
                score += 0.2
            elif factors.days_until_renewal < 90:
                score += 0.1

        # Numero de renovacoes (mais = cliente fiel)
        if factors.renewal_count == 0:
            score += 0.2
        elif factors.renewal_count == 1:
            score += 0.1

        return min(score, 1.0)

    def _calculate_usage_score(self, factors: ChurnFactors) -> float:
        """Calcula score de uso (0-1, maior = mais risco).

        Args:
            factors: Fatores de churn.

        Returns:
            Score de uso.
        """
        score = 0.0

        # Taxa de uso de features (menor = mais risco)
        if factors.feature_usage_rate < 0.3:
            score += 0.4
        elif factors.feature_usage_rate < 0.5:
            score += 0.2
        elif factors.feature_usage_rate < 0.7:
            score += 0.1

        # Frequencia de login (menor = mais risco)
        if factors.login_frequency < 1:
            score += 0.3
        elif factors.login_frequency < 3:
            score += 0.15

        # Tendencia de uso de API (negativa = menos uso)
        if factors.api_calls_trend < -30:
            score += 0.3
        elif factors.api_calls_trend < -10:
            score += 0.15
        elif factors.api_calls_trend < 0:
            score += 0.05

        return min(score, 1.0)

    def _get_risk_level(self, probability: float) -> str:
        """Determina nivel de risco.

        Args:
            probability: Probabilidade de churn.

        Returns:
            Nivel de risco.
        """
        if probability < self.RISK_THRESHOLDS["low"]:
            return "low"
        if probability < self.RISK_THRESHOLDS["medium"]:
            return "medium"
        if probability < self.RISK_THRESHOLDS["high"]:
            return "high"
        return "critical"

    def _calculate_confidence(self, factors: ChurnFactors) -> float:
        """Calcula confianca da previsao.

        Args:
            factors: Fatores disponíveis.

        Returns:
            Score de confianca (0-1).
        """
        # Quanto mais dados, maior a confianca
        data_points = 0
        total_points = 15

        # Conta dados disponíveis
        if factors.days_since_last_interaction > 0:
            data_points += 1
        if factors.interaction_frequency > 0:
            data_points += 1
        if factors.support_tickets_count >= 0:
            data_points += 1
        if factors.payment_delays_count >= 0:
            data_points += 1
        if factors.contract_value > 0:
            data_points += 1
        if factors.nps_score is not None:
            data_points += 2  # NPS vale mais
        if factors.csat_score is not None:
            data_points += 2
        if factors.contract_age_months > 0:
            data_points += 1
        if factors.days_until_renewal is not None:
            data_points += 1
        if factors.feature_usage_rate > 0:
            data_points += 1
        if factors.login_frequency > 0:
            data_points += 1

        return min(data_points / total_points, 1.0)

    def _identify_main_factors(
        self,
        factors: ChurnFactors,
        scores: dict,
    ) -> list[dict]:
        """Identifica principais fatores de risco.

        Args:
            factors: Fatores de churn.
            scores: Scores por categoria.

        Returns:
            Lista de fatores ordenados por impacto.
        """
        main_factors = []

        # Ordena categorias por score
        sorted_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        for category, score in sorted_categories[:3]:  # Top 3
            if score > 0.2:  # Só fatores significativos
                factor = {
                    "category": category,
                    "score": round(score, 2),
                    "impact": "high" if score > 0.5 else "medium",
                    "details": self._get_factor_details(category, factors),
                }
                main_factors.append(factor)

        return main_factors

    def _get_factor_details(self, category: str, factors: ChurnFactors) -> str:
        """Retorna detalhes de um fator.

        Args:
            category: Categoria do fator.
            factors: Fatores de churn.

        Returns:
            Descricao do fator.
        """
        details = {
            "engagement": f"Ultima interacao ha {factors.days_since_last_interaction} dias, "
            f"{factors.unresolved_issues} issues pendentes",
            "financial": f"{factors.payment_delays_count} atrasos de pagamento, "
            f"tendencia de valor: {factors.value_trend:+.1f}%",
            "satisfaction": f"NPS: {factors.nps_score or 'N/A'}, "
            f"CSAT: {factors.csat_score or 'N/A'}, "
            f"{factors.complaints_count} reclamacoes",
            "contract": f"Contrato ha {factors.contract_age_months} meses, "
            f"renovacao em {factors.days_until_renewal or 'N/A'} dias",
            "usage": f"Uso de features: {factors.feature_usage_rate*100:.0f}%, "
            f"logins/mes: {factors.login_frequency:.1f}",
        }
        return details.get(category, "")

    def _generate_recommendations(
        self,
        factors: ChurnFactors,
        risk_level: str,
        main_factors: list,
    ) -> list[dict]:
        """Gera recomendacoes de retencao.

        Args:
            factors: Fatores de churn.
            risk_level: Nivel de risco.
            main_factors: Principais fatores.

        Returns:
            Lista de recomendacoes.
        """
        recommendations = []

        # Recomendacoes baseadas em fatores
        for factor in main_factors:
            category = factor["category"]

            if category == "engagement":
                recommendations.append(
                    {
                        "action": "contact_customer",
                        "priority": "high",
                        "description": "Agendar ligacao de relacionamento com o cliente",
                        "expected_impact": "medium",
                    }
                )
                if factors.unresolved_issues > 0:
                    recommendations.append(
                        {
                            "action": "resolve_issues",
                            "priority": "high",
                            "description": f"Resolver {factors.unresolved_issues} issues pendentes",
                            "expected_impact": "high",
                        }
                    )

            elif category == "financial":
                if factors.payment_delays_count > 0:
                    recommendations.append(
                        {
                            "action": "payment_flexibility",
                            "priority": "medium",
                            "description": "Oferecer opcoes de pagamento mais flexíveis",
                            "expected_impact": "medium",
                        }
                    )
                if factors.value_trend < 0:
                    recommendations.append(
                        {
                            "action": "value_review",
                            "priority": "medium",
                            "description": "Revisar proposta de valor e benefícios",
                            "expected_impact": "medium",
                        }
                    )

            elif category == "satisfaction":
                if factors.nps_score and factors.nps_score < 7:
                    recommendations.append(
                        {
                            "action": "satisfaction_survey",
                            "priority": "high",
                            "description": "Realizar pesquisa de satisfacao detalhada",
                            "expected_impact": "medium",
                        }
                    )
                if factors.complaints_count > 0:
                    recommendations.append(
                        {
                            "action": "complaint_followup",
                            "priority": "high",
                            "description": "Fazer followup das reclamacoes anteriores",
                            "expected_impact": "high",
                        }
                    )

            elif category == "usage":
                if factors.feature_usage_rate < 0.5:
                    recommendations.append(
                        {
                            "action": "training_session",
                            "priority": "medium",
                            "description": "Oferecer treinamento sobre features nao utilizadas",
                            "expected_impact": "medium",
                        }
                    )

        # Recomendacao baseada em nivel de risco
        if risk_level == "critical":
            recommendations.insert(
                0,
                {
                    "action": "executive_intervention",
                    "priority": "critical",
                    "description": "Escalar para gerente de contas para intervencao imediata",
                    "expected_impact": "high",
                },
            )
        elif risk_level == "high":
            recommendations.insert(
                0,
                {
                    "action": "retention_offer",
                    "priority": "high",
                    "description": "Preparar oferta de retencao personalizada",
                    "expected_impact": "high",
                },
            )

        return recommendations[:5]  # Maximo 5 recomendacoes

    def _estimate_churn_date(
        self,
        factors: ChurnFactors,
        probability: float,
    ) -> Optional[datetime]:
        """Estima data provavel de churn.

        Args:
            factors: Fatores de churn.
            probability: Probabilidade de churn.

        Returns:
            Data estimada ou None.
        """
        if probability < 0.5:
            return None

        # Se tem data de renovacao, usa como referencia
        if factors.days_until_renewal is not None:
            return datetime.utcnow() + timedelta(days=factors.days_until_renewal)

        # Estima baseado na probabilidade
        # Alta probabilidade = churn mais proximo
        days_estimate = int((1 - probability) * 180)  # Max 6 meses
        return datetime.utcnow() + timedelta(days=max(days_estimate, 30))

    def _calculate_ltv_at_risk(
        self,
        factors: ChurnFactors,
        probability: float,
    ) -> float:
        """Calcula valor em risco.

        Args:
            factors: Fatores de churn.
            probability: Probabilidade de churn.

        Returns:
            Valor monetario em risco.
        """
        # Calcula LTV simples (valor mensal * meses estimados restantes)
        monthly_value = factors.contract_value / 12 if factors.contract_value else 0
        remaining_months = 24  # Estimativa de 2 anos de vida util

        ltv = monthly_value * remaining_months
        return ltv * probability
