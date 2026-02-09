"""RecommendationEngine - Motor de Recomendacoes IA.

Sprint 34 - AI Predictions.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from modules.ai.models.recommendation import (
    Recommendation,
    RecommendationStatus,
    RecommendationType,
)

logger = logging.getLogger(__name__)


@dataclass
class RecommendationItem:
    """Item de recomendacao."""

    entity_type: str
    entity_id: UUID
    entity_name: str
    relevance_score: float  # 0-1
    confidence: float  # 0-1
    reason: str
    expected_value: float
    features: dict


@dataclass
class RecommendationResult:
    """Resultado do motor de recomendacao."""

    recommendations: list[RecommendationItem]
    algorithm: str
    total_candidates: int
    processing_time_ms: int
    context_used: dict


class RecommendationEngine:
    """Motor de recomendacoes baseado em IA."""

    # Algoritmos disponiveis
    ALGORITHMS = [
        "collaborative_filtering",
        "content_based",
        "hybrid",
        "popularity",
        "rule_based",
    ]

    def __init__(self, db_session: Any):
        """Inicializa o motor.

        Args:
            db_session: Sessao do banco de dados.
        """
        self.db = db_session

    async def get_recommendations(
        self,
        tenant_id: UUID,
        target_entity_type: str,
        target_entity_id: UUID,
        recommendation_type: RecommendationType,
        limit: int = 5,
        context: dict | None = None,
        algorithm: str = "hybrid",
    ) -> RecommendationResult:
        """Gera recomendacoes para uma entidade.

        Args:
            tenant_id: ID do tenant.
            target_entity_type: Tipo da entidade alvo.
            target_entity_id: ID da entidade alvo.
            recommendation_type: Tipo de recomendacao.
            limit: Numero maximo de recomendacoes.
            context: Contexto adicional.
            algorithm: Algoritmo a usar.

        Returns:
            Resultado com recomendacoes.
        """
        import time

        start_time = time.time()

        # Coleta features da entidade alvo
        target_features = await self._get_entity_features(tenant_id, target_entity_type, target_entity_id)

        # Gera candidatos baseado no tipo
        candidates = await self._generate_candidates(
            tenant_id,
            target_entity_type,
            target_entity_id,
            recommendation_type,
            context,
        )

        # Pontua candidatos
        scored_candidates = self._score_candidates(
            candidates,
            target_features,
            algorithm,
            context,
        )

        # Ordena e limita
        sorted_candidates = sorted(
            scored_candidates,
            key=lambda x: x.relevance_score,
            reverse=True,
        )[:limit]

        # Salva recomendacoes no banco
        await self._save_recommendations(
            tenant_id,
            target_entity_type,
            target_entity_id,
            recommendation_type,
            sorted_candidates,
            algorithm,
        )

        processing_time = int((time.time() - start_time) * 1000)

        logger.info(
            "Recommendations generated",
            extra={
                "target": f"{target_entity_type}:{target_entity_id}",
                "type": recommendation_type.value,
                "count": len(sorted_candidates),
                "algorithm": algorithm,
                "processing_time_ms": processing_time,
            },
        )

        return RecommendationResult(
            recommendations=sorted_candidates,
            algorithm=algorithm,
            total_candidates=len(candidates),
            processing_time_ms=processing_time,
            context_used=context or {},
        )

    async def get_upsell_recommendations(
        self,
        tenant_id: UUID,
        client_id: UUID,
        current_products: list[UUID],
        limit: int = 3,
    ) -> RecommendationResult:
        """Gera recomendacoes de upsell para cliente.

        Args:
            tenant_id: ID do tenant.
            client_id: ID do cliente.
            current_products: Produtos atuais do cliente.
            limit: Numero de recomendacoes.

        Returns:
            Recomendacoes de upsell.
        """
        context = {
            "current_products": [str(p) for p in current_products],
            "recommendation_goal": "upsell",
        }

        return await self.get_recommendations(
            tenant_id=tenant_id,
            target_entity_type="client",
            target_entity_id=client_id,
            recommendation_type=RecommendationType.UPSELL,
            limit=limit,
            context=context,
            algorithm="content_based",
        )

    async def get_cross_sell_recommendations(
        self,
        tenant_id: UUID,
        client_id: UUID,
        current_products: list[UUID],
        limit: int = 3,
    ) -> RecommendationResult:
        """Gera recomendacoes de cross-sell para cliente.

        Args:
            tenant_id: ID do tenant.
            client_id: ID do cliente.
            current_products: Produtos atuais do cliente.
            limit: Numero de recomendacoes.

        Returns:
            Recomendacoes de cross-sell.
        """
        context = {
            "current_products": [str(p) for p in current_products],
            "recommendation_goal": "cross_sell",
        }

        return await self.get_recommendations(
            tenant_id=tenant_id,
            target_entity_type="client",
            target_entity_id=client_id,
            recommendation_type=RecommendationType.CROSS_SELL,
            limit=limit,
            context=context,
            algorithm="collaborative_filtering",
        )

    async def get_retention_actions(
        self,
        tenant_id: UUID,
        client_id: UUID,
        churn_probability: float,
        limit: int = 3,
    ) -> RecommendationResult:
        """Gera recomendacoes de acoes de retencao.

        Args:
            tenant_id: ID do tenant.
            client_id: ID do cliente.
            churn_probability: Probabilidade de churn.
            limit: Numero de recomendacoes.

        Returns:
            Acoes recomendadas.
        """
        context = {
            "churn_probability": churn_probability,
            "recommendation_goal": "retention",
        }

        return await self.get_recommendations(
            tenant_id=tenant_id,
            target_entity_type="client",
            target_entity_id=client_id,
            recommendation_type=RecommendationType.RETENTION,
            limit=limit,
            context=context,
            algorithm="rule_based",
        )

    async def get_next_best_action(
        self,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID,
        current_state: dict,
        limit: int = 1,
    ) -> RecommendationResult:
        """Recomenda proxima melhor acao.

        Args:
            tenant_id: ID do tenant.
            entity_type: Tipo da entidade.
            entity_id: ID da entidade.
            current_state: Estado atual.
            limit: Numero de acoes.

        Returns:
            Acoes recomendadas.
        """
        context = {
            "current_state": current_state,
            "recommendation_goal": "next_action",
        }

        return await self.get_recommendations(
            tenant_id=tenant_id,
            target_entity_type=entity_type,
            target_entity_id=entity_id,
            recommendation_type=RecommendationType.NEXT_BEST_ACTION,
            limit=limit,
            context=context,
            algorithm="hybrid",
        )

    async def _get_entity_features(
        self,
        tenant_id: UUID,
        entity_type: str,
        entity_id: UUID,
    ) -> dict:
        """Busca features de uma entidade.

        Args:
            tenant_id: ID do tenant.
            entity_type: Tipo da entidade.
            entity_id: ID da entidade.

        Returns:
            Features da entidade.
        """
        # Em producao, buscaria do feature store ou banco
        # Aqui retorna features simuladas
        return {
            "entity_type": entity_type,
            "entity_id": str(entity_id),
            "segment": "premium",
            "tenure_months": 24,
            "contract_value": 5000.0,
            "products_count": 3,
            "satisfaction_score": 8.0,
            "engagement_level": "high",
            "last_interaction_days": 7,
        }

    async def _generate_candidates(
        self,
        tenant_id: UUID,
        target_entity_type: str,
        target_entity_id: UUID,
        recommendation_type: RecommendationType,
        context: dict | None,
    ) -> list[dict]:
        """Gera candidatos para recomendacao.

        Args:
            tenant_id: ID do tenant.
            target_entity_type: Tipo da entidade alvo.
            target_entity_id: ID da entidade alvo.
            recommendation_type: Tipo de recomendacao.
            context: Contexto adicional.

        Returns:
            Lista de candidatos.
        """
        # Em producao, buscaria candidatos reais do banco
        # Aqui gera candidatos simulados
        candidates = []

        if recommendation_type == RecommendationType.UPSELL:
            candidates = [
                {
                    "entity_type": "service",
                    "entity_id": "serv-001",
                    "name": "Plano Premium",
                    "category": "upgrade",
                    "price": 500.0,
                    "features": ["24/7 support", "priority response"],
                },
                {
                    "entity_type": "service",
                    "entity_id": "serv-002",
                    "name": "Monitoramento Avancado",
                    "category": "addon",
                    "price": 200.0,
                    "features": ["AI detection", "alerts"],
                },
                {
                    "entity_type": "service",
                    "entity_id": "serv-003",
                    "name": "Backup Redundante",
                    "category": "addon",
                    "price": 150.0,
                    "features": ["cloud backup", "recovery"],
                },
            ]

        elif recommendation_type == RecommendationType.CROSS_SELL:
            candidates = [
                {
                    "entity_type": "product",
                    "entity_id": "prod-001",
                    "name": "Camera IP HD",
                    "category": "equipment",
                    "price": 800.0,
                    "features": ["1080p", "night vision"],
                },
                {
                    "entity_type": "product",
                    "entity_id": "prod-002",
                    "name": "Sensor de Presenca",
                    "category": "equipment",
                    "price": 150.0,
                    "features": ["wireless", "pet immune"],
                },
            ]

        elif recommendation_type == RecommendationType.RETENTION:
            candidates = [
                {
                    "entity_type": "action",
                    "entity_id": "act-001",
                    "name": "Oferecer Desconto",
                    "category": "discount",
                    "expected_impact": 0.3,
                    "features": ["10% off", "3 months"],
                },
                {
                    "entity_type": "action",
                    "entity_id": "act-002",
                    "name": "Ligacao de Relacionamento",
                    "category": "engagement",
                    "expected_impact": 0.2,
                    "features": ["personal call", "feedback"],
                },
                {
                    "entity_type": "action",
                    "entity_id": "act-003",
                    "name": "Upgrade Gratuito",
                    "category": "benefit",
                    "expected_impact": 0.4,
                    "features": ["free upgrade", "1 month"],
                },
            ]

        elif recommendation_type == RecommendationType.NEXT_BEST_ACTION:
            candidates = [
                {
                    "entity_type": "action",
                    "entity_id": "nba-001",
                    "name": "Enviar Proposta",
                    "category": "sales",
                    "expected_impact": 0.5,
                    "features": ["proposal", "follow_up"],
                },
                {
                    "entity_type": "action",
                    "entity_id": "nba-002",
                    "name": "Agendar Demo",
                    "category": "sales",
                    "expected_impact": 0.4,
                    "features": ["demo", "technical"],
                },
            ]

        else:
            candidates = [
                {
                    "entity_type": "insight",
                    "entity_id": "ins-001",
                    "name": "Revisar Contrato",
                    "category": "insight",
                    "expected_impact": 0.3,
                    "features": ["contract", "review"],
                },
            ]

        return candidates

    def _score_candidates(
        self,
        candidates: list[dict],
        target_features: dict,
        algorithm: str,
        context: dict | None,
    ) -> list[RecommendationItem]:
        """Pontua candidatos.

        Args:
            candidates: Lista de candidatos.
            target_features: Features do alvo.
            algorithm: Algoritmo a usar.
            context: Contexto adicional.

        Returns:
            Lista de itens pontuados.
        """
        scored = []

        for candidate in candidates:
            # Calcula score baseado no algoritmo
            if algorithm == "collaborative_filtering":
                score = self._collaborative_score(candidate, target_features)
            elif algorithm == "content_based":
                score = self._content_based_score(candidate, target_features)
            elif algorithm == "rule_based":
                score = self._rule_based_score(candidate, target_features, context)
            elif algorithm == "popularity":
                score = self._popularity_score(candidate)
            else:  # hybrid
                score = (
                    self._collaborative_score(candidate, target_features) * 0.4
                    + self._content_based_score(candidate, target_features) * 0.4
                    + self._popularity_score(candidate) * 0.2
                )

            # Ajusta score pelo contexto
            if context:
                score = self._adjust_by_context(score, candidate, context)

            # Gera razao
            reason = self._generate_reason(candidate, target_features, score)

            # Calcula valor esperado
            expected_value = self._calculate_expected_value(candidate, score)

            scored.append(
                RecommendationItem(
                    entity_type=candidate["entity_type"],
                    entity_id=(UUID(candidate["entity_id"]) if "-" in candidate["entity_id"] else UUID(int=0)),
                    entity_name=candidate["name"],
                    relevance_score=round(min(score, 1.0), 4),
                    confidence=round(0.7 + score * 0.2, 4),
                    reason=reason,
                    expected_value=round(expected_value, 2),
                    features={
                        "category": candidate.get("category", ""),
                        "features": candidate.get("features", []),
                    },
                )
            )

        return scored

    def _collaborative_score(self, candidate: dict, target_features: dict) -> float:
        """Calcula score por filtragem colaborativa.

        Args:
            candidate: Candidato.
            target_features: Features do alvo.

        Returns:
            Score.
        """
        # Simulacao - em producao usaria matriz de usuarios/itens
        base_score = 0.5

        # Bonus por segmento
        if target_features.get("segment") == "premium":
            base_score += 0.2

        # Bonus por engajamento
        if target_features.get("engagement_level") == "high":
            base_score += 0.15

        return min(base_score, 1.0)

    def _content_based_score(self, candidate: dict, target_features: dict) -> float:
        """Calcula score baseado em conteudo.

        Args:
            candidate: Candidato.
            target_features: Features do alvo.

        Returns:
            Score.
        """
        base_score = 0.5

        # Bonus por categoria compativel
        candidate_category = candidate.get("category", "")
        if candidate_category in ["upgrade", "addon"]:
            base_score += 0.2

        # Bonus por satisfacao alta
        if target_features.get("satisfaction_score", 0) >= 7:
            base_score += 0.15

        return min(base_score, 1.0)

    def _rule_based_score(
        self,
        candidate: dict,
        target_features: dict,
        context: dict | None,
    ) -> float:
        """Calcula score baseado em regras.

        Args:
            candidate: Candidato.
            target_features: Features do alvo.
            context: Contexto.

        Returns:
            Score.
        """
        base_score = 0.5

        # Regras para retencao
        if context and context.get("recommendation_goal") == "retention":
            churn_prob = context.get("churn_probability", 0)
            expected_impact = candidate.get("expected_impact", 0)

            # Quanto maior o risco de churn, maior o score para acoes de alto impacto
            base_score = churn_prob * expected_impact * 2

        return min(base_score, 1.0)

    def _popularity_score(self, candidate: dict) -> float:
        """Calcula score por popularidade.

        Args:
            candidate: Candidato.

        Returns:
            Score.
        """
        # Simulacao - em producao usaria dados reais de popularidade
        return 0.6

    def _adjust_by_context(
        self,
        score: float,
        candidate: dict,
        context: dict,
    ) -> float:
        """Ajusta score pelo contexto.

        Args:
            score: Score base.
            candidate: Candidato.
            context: Contexto.

        Returns:
            Score ajustado.
        """
        # Penaliza produtos ja comprados
        current_products = context.get("current_products", [])
        if candidate.get("entity_id") in current_products:
            score *= 0.1

        return score

    def _generate_reason(
        self,
        candidate: dict,
        target_features: dict,
        score: float,
    ) -> str:
        """Gera razao da recomendacao.

        Args:
            candidate: Candidato.
            target_features: Features do alvo.
            score: Score calculado.

        Returns:
            Razao em texto.
        """
        reasons = []

        if target_features.get("segment") == "premium":
            reasons.append("clientes premium semelhantes adquiriram")

        if target_features.get("satisfaction_score", 0) >= 7:
            reasons.append("alta satisfacao indica boa receptividade")

        if candidate.get("category") == "upgrade":
            reasons.append("upgrade complementa servicos atuais")

        if not reasons:
            reasons.append("recomendado com base no perfil do cliente")

        return "; ".join(reasons)

    def _calculate_expected_value(self, candidate: dict, score: float) -> float:
        """Calcula valor esperado da recomendacao.

        Args:
            candidate: Candidato.
            score: Score de relevancia.

        Returns:
            Valor esperado.
        """
        price = candidate.get("price", 0)
        expected_impact = candidate.get("expected_impact", 0.5)

        # Valor esperado = preco * probabilidade de aceite * impacto
        return price * score * (1 + expected_impact)

    async def _save_recommendations(
        self,
        tenant_id: UUID,
        target_entity_type: str,
        target_entity_id: UUID,
        recommendation_type: RecommendationType,
        recommendations: list[RecommendationItem],
        algorithm: str,
    ) -> list[Recommendation]:
        """Salva recomendacoes no banco.

        Args:
            tenant_id: ID do tenant.
            target_entity_type: Tipo da entidade alvo.
            target_entity_id: ID da entidade alvo.
            recommendation_type: Tipo de recomendacao.
            recommendations: Recomendacoes geradas.
            algorithm: Algoritmo usado.

        Returns:
            Recomendacoes salvas.
        """
        saved = []

        for i, rec in enumerate(recommendations):
            recommendation = Recommendation(
                tenant_id=tenant_id,
                recommendation_type=recommendation_type,
                status=RecommendationStatus.PENDING,
                target_entity_type=target_entity_type,
                target_entity_id=target_entity_id,
                recommended_entity_type=rec.entity_type,
                recommended_entity_id=rec.entity_id,
                recommended_entity_name=rec.entity_name,
                title=f"Recomendacao: {rec.entity_name}",
                description=rec.reason,
                reason=rec.reason,
                relevance_score=rec.relevance_score,
                confidence_score=rec.confidence,
                priority_score=(len(recommendations) - i) * 10,
                expected_value=rec.expected_value,
                rank_position=i + 1,
                total_recommendations=len(recommendations),
                algorithm=algorithm,
                item_features=rec.features,
                valid_from=datetime.utcnow(),
                valid_until=datetime.utcnow() + timedelta(days=7),
            )

            self.db.add(recommendation)
            saved.append(recommendation)

        await self.db.commit()

        return saved

    async def record_interaction(
        self,
        recommendation_id: UUID,
        interaction_type: str,  # shown, clicked, accepted, rejected
        feedback: str | None = None,
    ) -> Recommendation | None:
        """Registra interacao com recomendacao.

        Args:
            recommendation_id: ID da recomendacao.
            interaction_type: Tipo de interacao.
            feedback: Feedback opcional.

        Returns:
            Recomendacao atualizada.
        """
        recommendation = await self.db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()

        if not recommendation:
            return None

        if interaction_type == "shown":
            recommendation.mark_shown()
        elif interaction_type == "clicked":
            recommendation.mark_clicked()
        elif interaction_type == "accepted":
            recommendation.accept()
        elif interaction_type == "rejected":
            recommendation.reject(feedback=feedback)

        await self.db.commit()
        await self.db.refresh(recommendation)

        logger.info(
            "Recommendation interaction recorded",
            extra={
                "recommendation_id": str(recommendation_id),
                "interaction": interaction_type,
            },
        )

        return recommendation

    async def record_conversion(
        self,
        recommendation_id: UUID,
        conversion_value: float,
        conversion_entity_id: UUID | None = None,
    ) -> Recommendation | None:
        """Registra conversao de recomendacao.

        Args:
            recommendation_id: ID da recomendacao.
            conversion_value: Valor da conversao.
            conversion_entity_id: ID da entidade gerada.

        Returns:
            Recomendacao atualizada.
        """
        recommendation = await self.db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()

        if not recommendation:
            return None

        recommendation.convert(
            value=conversion_value,
            entity_id=str(conversion_entity_id) if conversion_entity_id else None,
        )

        await self.db.commit()
        await self.db.refresh(recommendation)

        logger.info(
            "Recommendation conversion recorded",
            extra={
                "recommendation_id": str(recommendation_id),
                "value": conversion_value,
            },
        )

        return recommendation
