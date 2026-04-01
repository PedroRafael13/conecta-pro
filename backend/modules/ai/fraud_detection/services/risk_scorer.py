"""
Risk Scorer Service - Sprint 45

Servico para calculo de scores de risco de entidades.
"""

import logging
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from modules.ai.fraud_detection.models.fraud_alert import AlertStatus, FraudAlert
from modules.ai.fraud_detection.models.risk_profile import (
    EntityType,
    RiskLevel,
    RiskProfile,
)

logger = logging.getLogger(__name__)


class RiskScorer:
    """Calculador de scores de risco."""

    # Pesos dos componentes
    COMPONENT_WEIGHTS = {
        "behavior": 0.20,
        "transaction": 0.25,
        "velocity": 0.15,
        "identity": 0.15,
        "network": 0.10,
        "historical": 0.15,
    }

    # Fatores de risco e seus pesos
    RISK_FACTORS = {
        # Comportamentais
        "new_device": 10,
        "new_location": 8,
        "unusual_time": 5,
        "high_velocity": 15,
        "unusual_amount": 12,
        # Identidade
        "unverified_identity": 20,
        "multiple_accounts": 15,
        "suspicious_email": 10,
        "vpn_detected": 8,
        # Transacionais
        "high_risk_recipient": 20,
        "structuring_pattern": 25,
        "round_amounts": 5,
        "rapid_withdrawals": 18,
        # Historico
        "previous_fraud": 40,
        "previous_chargeback": 25,
        "account_suspended": 30,
        "linked_to_fraud": 35,
        # Rede
        "blacklisted_ip": 30,
        "tor_exit_node": 25,
        "proxy_detected": 15,
        "known_fraud_device": 40,
    }

    # Indicadores de confianca e seus bonus
    TRUST_INDICATORS = {
        "verified_identity": -15,
        "long_account_age": -10,
        "consistent_behavior": -8,
        "good_transaction_history": -12,
        "2fa_enabled": -10,
        "verified_phone": -5,
        "verified_address": -5,
        "premium_account": -8,
    }

    def __init__(self, db: Session):
        """Inicializa o scorer."""
        self.db = db

    async def calculate_risk_score(
        self,
        entity_type: EntityType,
        entity_id: UUID,
        context: dict[str, Any] | None = None,
        recalculate: bool = True,
    ) -> dict[str, Any]:
        """
        Calcula score de risco para uma entidade.

        Args:
            entity_type: Tipo da entidade
            entity_id: ID da entidade
            context: Contexto adicional
            recalculate: Se deve recalcular mesmo que tenha cache

        Returns:
            Score de risco e detalhes
        """
        result = {
            "entity_type": entity_type.value,
            "entity_id": str(entity_id),
            "risk_level": RiskLevel.LOW.value,
            "risk_score": 0.0,
            "previous_score": None,
            "score_change": 0.0,
            "component_scores": {},
            "risk_factors": [],
            "trust_indicators": [],
            "recommendations": [],
            "calculated_at": datetime.utcnow().isoformat(),
        }

        try:
            # Obter ou criar perfil
            profile = await self._get_or_create_profile(entity_type, entity_id)
            result["previous_score"] = profile.risk_score

            if not recalculate and profile.last_calculated_at:
                # Usar score em cache se recente (< 1 hora)
                cache_age = datetime.utcnow() - profile.last_calculated_at
                if cache_age < timedelta(hours=1):
                    result["risk_score"] = profile.risk_score
                    result["risk_level"] = profile.risk_level.value
                    result["component_scores"] = {
                        "behavior": profile.behavior_score,
                        "transaction": profile.transaction_score,
                        "velocity": profile.velocity_score,
                        "identity": profile.identity_score,
                        "network": profile.network_score,
                        "historical": profile.historical_score,
                    }
                    return result

            # Calcular componentes
            behavior_score = await self._calculate_behavior_score(profile, context)
            transaction_score = await self._calculate_transaction_score(profile, context)
            velocity_score = await self._calculate_velocity_score(profile, context)
            identity_score = await self._calculate_identity_score(profile, context)
            network_score = await self._calculate_network_score(profile, context)
            historical_score = await self._calculate_historical_score(entity_type, entity_id)

            result["component_scores"] = {
                "behavior": behavior_score,
                "transaction": transaction_score,
                "velocity": velocity_score,
                "identity": identity_score,
                "network": network_score,
                "historical": historical_score,
            }

            # Calcular score ponderado
            weighted_score = (
                behavior_score * self.COMPONENT_WEIGHTS["behavior"]
                + transaction_score * self.COMPONENT_WEIGHTS["transaction"]
                + velocity_score * self.COMPONENT_WEIGHTS["velocity"]
                + identity_score * self.COMPONENT_WEIGHTS["identity"]
                + network_score * self.COMPONENT_WEIGHTS["network"]
                + historical_score * self.COMPONENT_WEIGHTS["historical"]
            )

            # Aplicar fatores de risco
            risk_factors = await self._identify_risk_factors(profile, context)
            risk_adjustment = sum(self.RISK_FACTORS.get(f["factor"], 0) for f in risk_factors)
            result["risk_factors"] = risk_factors

            # Aplicar indicadores de confianca
            trust_indicators = await self._identify_trust_indicators(profile)
            trust_adjustment = sum(self.TRUST_INDICATORS.get(t["indicator"], 0) for t in trust_indicators)
            result["trust_indicators"] = trust_indicators

            # Score final
            final_score = weighted_score + risk_adjustment + trust_adjustment
            final_score = max(0, min(100, final_score))  # Limitar 0-100

            result["risk_score"] = round(final_score, 2)
            result["score_change"] = round(final_score - (result["previous_score"] or 0), 2)

            # Determinar nivel de risco
            result["risk_level"] = self._determine_risk_level(final_score).value

            # Gerar recomendacoes
            result["recommendations"] = await self._generate_recommendations(result["risk_level"], risk_factors)

            # Atualizar perfil
            await self._update_profile(profile, result)

            logger.info(
                f"Score calculado para {entity_type.value}:{entity_id} - "
                f"Score: {final_score:.2f}, Level: {result['risk_level']}"
            )

        except Exception as e:
            logger.error(f"Erro ao calcular score de risco: {e}")
            result["error"] = str(e)

        return result

    async def batch_calculate_scores(
        self,
        entity_type: EntityType,
        entity_ids: list[UUID],
    ) -> list[dict[str, Any]]:
        """Calcula scores para multiplas entidades."""
        results = []
        for entity_id in entity_ids:
            result = await self.calculate_risk_score(entity_type, entity_id)
            results.append(result)
        return results

    async def get_risk_summary(
        self,
        entity_type: EntityType | None = None,
    ) -> dict[str, Any]:
        """Obtem resumo de distribuicao de risco."""
        query = self.db.query(RiskProfile)

        if entity_type:
            query = query.filter(RiskProfile.entity_type == entity_type)

        profiles = query.all()

        distribution = {
            "minimal": 0,
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0,
            "blocked": 0,
        }

        for profile in profiles:
            level = profile.risk_level.value
            if level in distribution:
                distribution[level] += 1
            if profile.is_blocked:
                distribution["blocked"] += 1

        total = len(profiles)
        avg_score = sum(p.risk_score for p in profiles) / total if total > 0 else 0

        return {
            "total_profiles": total,
            "average_score": round(avg_score, 2),
            "distribution": distribution,
            "high_risk_count": distribution["high"] + distribution["critical"],
            "blocked_count": distribution["blocked"],
        }

    async def _calculate_behavior_score(
        self,
        profile: RiskProfile,
        context: dict[str, Any] | None,
    ) -> float:
        """Calcula score comportamental."""
        score = profile.behavior_score or 20  # Base

        # Ajustes baseados em comportamento
        if context:
            if context.get("is_new_device"):
                score += 15
            if context.get("is_new_location"):
                score += 10
            if context.get("is_unusual_time"):
                score += 8

        # Penalizar inconsistencias
        if profile.total_alerts > 5:
            score += min(20, profile.total_alerts * 2)

        return min(100, max(0, score))

    async def _calculate_transaction_score(
        self,
        profile: RiskProfile,
        context: dict[str, Any] | None,
    ) -> float:
        """Calcula score transacional."""
        score = profile.transaction_score or 15

        # Baseado em historico
        if profile.total_transactions > 0:
            # Mais transacoes = mais dados = mais confiavel
            if profile.total_transactions > 100:
                score -= 5
            elif profile.total_transactions < 5:
                score += 10

        # Valor medio
        avg_value = profile.avg_transaction_value or 0
        if avg_value > 10000:  # Alto valor
            score += 15
        elif avg_value > 5000:
            score += 8

        if context:
            current_amount = context.get("amount", 0)
            if avg_value > 0 and current_amount > avg_value * 5:
                score += 20  # 5x o valor medio

        return min(100, max(0, score))

    async def _calculate_velocity_score(
        self,
        profile: RiskProfile,
        context: dict[str, Any] | None,
    ) -> float:
        """Calcula score de velocidade."""
        score = profile.velocity_score or 10

        # Transacoes hoje
        if profile.transactions_today:
            if profile.transactions_today > 20:
                score += 30
            elif profile.transactions_today > 10:
                score += 15
            elif profile.transactions_today > 5:
                score += 5

        # Logins hoje
        if profile.logins_today:
            if profile.logins_today > 10:
                score += 25
            elif profile.logins_today > 5:
                score += 10

        return min(100, max(0, score))

    async def _calculate_identity_score(
        self,
        profile: RiskProfile,
        context: dict[str, Any] | None,
    ) -> float:
        """Calcula score de identidade."""
        score = 50 if not profile.identity_verified else 10

        # Nivel de verificacao
        if profile.verification_level >= 3:
            score -= 20
        elif profile.verification_level >= 2:
            score -= 10
        elif profile.verification_level == 0:
            score += 20

        # Idade da conta
        if profile.created_at:
            age_days = (datetime.utcnow() - profile.created_at).days
            if age_days > 365:
                score -= 10
            elif age_days < 7:
                score += 20
            elif age_days < 30:
                score += 10

        return min(100, max(0, score))

    async def _calculate_network_score(
        self,
        profile: RiskProfile,
        context: dict[str, Any] | None,
    ) -> float:
        """Calcula score de rede (IP, dispositivo)."""
        score = profile.network_score or 20

        known_devices = profile.known_devices or []
        known_ips = profile.known_ips or []

        if context:
            device_id = context.get("device_id")
            ip_address = context.get("ip_address")

            if device_id and device_id not in known_devices:
                score += 15
            if ip_address and ip_address not in known_ips:
                score += 10

            # VPN/Proxy
            if context.get("vpn_detected"):
                score += 15
            if context.get("proxy_detected"):
                score += 12

        return min(100, max(0, score))

    async def _calculate_historical_score(
        self,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> float:
        """Calcula score baseado em historico de alertas."""
        score = 10  # Base

        # Contar alertas confirmados
        confirmed_frauds = (
            self.db.query(func.count(FraudAlert.id))
            .filter(
                FraudAlert.entity_type == entity_type.value,
                FraudAlert.entity_id == entity_id,
                FraudAlert.status == AlertStatus.CONFIRMED,
            )
            .scalar()
            or 0
        )

        if confirmed_frauds > 0:
            score += min(50, confirmed_frauds * 20)

        # Alertas recentes
        recent_alerts = (
            self.db.query(func.count(FraudAlert.id))
            .filter(
                FraudAlert.entity_type == entity_type.value,
                FraudAlert.entity_id == entity_id,
                FraudAlert.created_at >= datetime.utcnow() - timedelta(days=30),
            )
            .scalar()
            or 0
        )

        if recent_alerts > 0:
            score += min(30, recent_alerts * 5)

        return min(100, max(0, score))

    async def _identify_risk_factors(
        self,
        profile: RiskProfile,
        context: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        """Identifica fatores de risco presentes."""
        factors = []

        # Do perfil
        existing_factors = profile.risk_factors or []
        for f in existing_factors:
            if isinstance(f, dict):
                factors.append(f)
            else:
                factors.append({"factor": f, "weight": self.RISK_FACTORS.get(f, 5)})

        # Do contexto
        if context:
            if context.get("is_new_device"):
                factors.append({"factor": "new_device", "weight": 10})
            if context.get("is_new_location"):
                factors.append({"factor": "new_location", "weight": 8})
            if context.get("unusual_time"):
                factors.append({"factor": "unusual_time", "weight": 5})
            if context.get("vpn_detected"):
                factors.append({"factor": "vpn_detected", "weight": 8})

        # Do historico
        if not profile.identity_verified:
            factors.append({"factor": "unverified_identity", "weight": 20})
        if profile.confirmed_frauds > 0:
            factors.append({"factor": "previous_fraud", "weight": 40})

        return factors

    async def _identify_trust_indicators(
        self,
        profile: RiskProfile,
    ) -> list[dict[str, Any]]:
        """Identifica indicadores de confianca."""
        indicators = []

        existing = profile.trust_indicators or []
        for i in existing:
            if isinstance(i, dict):
                indicators.append(i)
            else:
                indicators.append({"indicator": i, "weight": self.TRUST_INDICATORS.get(i, -5)})

        if profile.identity_verified:
            indicators.append({"indicator": "verified_identity", "weight": -15})

        if profile.verification_level >= 2:
            indicators.append({"indicator": "2fa_enabled", "weight": -10})

        # Idade da conta
        if profile.created_at:
            age_days = (datetime.utcnow() - profile.created_at).days
            if age_days > 180:
                indicators.append({"indicator": "long_account_age", "weight": -10})

        # Historico limpo
        if profile.total_alerts == 0 and profile.total_transactions > 10:
            indicators.append({"indicator": "good_transaction_history", "weight": -12})

        return indicators

    def _determine_risk_level(self, score: float) -> RiskLevel:
        """Determina nivel de risco baseado no score."""
        if score >= 80:
            return RiskLevel.CRITICAL
        elif score >= 60:
            return RiskLevel.HIGH
        elif score >= 40:
            return RiskLevel.MEDIUM
        elif score >= 20:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL

    async def _generate_recommendations(
        self,
        risk_level: str,
        risk_factors: list[dict[str, Any]],
    ) -> list[str]:
        """Gera recomendacoes baseadas no risco."""
        recommendations = []

        if risk_level in ["critical", "high"]:
            recommendations.append("Verificacao adicional de identidade recomendada")
            recommendations.append("Considerar revisao manual de transacoes")
            recommendations.append("Ativar monitoramento intensivo")

        if risk_level == "critical":
            recommendations.append("Considerar bloqueio preventivo")
            recommendations.append("Escalar para equipe de seguranca")

        # Baseado em fatores
        factor_names = [f.get("factor", "") for f in risk_factors]

        if "unverified_identity" in factor_names:
            recommendations.append("Solicitar verificacao de identidade")

        if "new_device" in factor_names or "new_location" in factor_names:
            recommendations.append("Confirmar dispositivo/localizacao com usuario")

        if "previous_fraud" in factor_names:
            recommendations.append("Revisar historico de fraudes anteriores")

        if "high_velocity" in factor_names:
            recommendations.append("Implementar limite de velocidade temporario")

        return recommendations

    async def _get_or_create_profile(
        self,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> RiskProfile:
        """Obtem ou cria perfil de risco."""
        profile = (
            self.db.query(RiskProfile)
            .filter(
                RiskProfile.entity_type == entity_type,
                RiskProfile.entity_id == entity_id,
            )
            .first()
        )

        if not profile:
            profile = RiskProfile(
                entity_type=entity_type,
                entity_id=entity_id,
            )
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)

        return profile

    async def _update_profile(
        self,
        profile: RiskProfile,
        result: dict[str, Any],
    ) -> None:
        """Atualiza perfil com novos scores."""
        try:
            profile.risk_score = result["risk_score"]
            profile.risk_score_change = result["score_change"]
            profile.risk_level = RiskLevel(result["risk_level"])

            scores = result.get("component_scores", {})
            profile.behavior_score = scores.get("behavior", profile.behavior_score)
            profile.transaction_score = scores.get("transaction", profile.transaction_score)
            profile.velocity_score = scores.get("velocity", profile.velocity_score)
            profile.identity_score = scores.get("identity", profile.identity_score)
            profile.network_score = scores.get("network", profile.network_score)
            profile.historical_score = scores.get("historical", profile.historical_score)

            profile.risk_factors = result.get("risk_factors", [])
            profile.trust_indicators = result.get("trust_indicators", [])

            profile.last_calculated_at = datetime.utcnow()

            self.db.commit()

        except Exception as e:
            logger.error(f"Erro ao atualizar perfil: {e}")
            self.db.rollback()
