"""
Fraud Detector Service - AI Fraud Detection

Motor principal de deteccao de fraudes.
"""

import logging
import time
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from modules.ai.fraud_detection.models.fraud_alert import (
    AlertSeverity,
    FraudAlert,
    FraudCategory,
)
from modules.ai.fraud_detection.models.risk_profile import (
    EntityType,
    RiskLevel,
    RiskProfile,
)
from modules.ai.fraud_detection.repositories.fraud_repository import FraudRepository

logger = logging.getLogger(__name__)


class FraudDetector:
    """
    Motor de deteccao de fraudes.

    Avalia transacoes e eventos contra regras e padroes
    para identificar atividades fraudulentas.
    """

    def __init__(self, db: Session):
        """Inicializa detector."""
        self.db = db
        self.repository = FraudRepository(db)

    def check_transaction(
        self,
        transaction_id: UUID,
        transaction_type: str,
        amount: float,
        payer_id: UUID,
        payer_type: str,
        payee_id: UUID | None = None,
        payee_type: str | None = None,
        ip_address: str | None = None,
        device_id: str | None = None,
        location: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Verifica transacao para fraude.

        Args:
            transaction_id: ID da transacao
            transaction_type: Tipo (payment, transfer, etc)
            amount: Valor
            payer_id: ID do pagador
            payer_type: Tipo do pagador
            payee_id: ID do recebedor
            payee_type: Tipo do recebedor
            ip_address: IP de origem
            device_id: ID do dispositivo
            location: Localizacao
            metadata: Dados adicionais

        Returns:
            Dict com decisao e detalhes
        """
        start_time = time.time()
        logger.info(f"Verificando transacao {transaction_id}")

        # Preparar dados
        data = {
            "transaction_id": str(transaction_id),
            "transaction_type": transaction_type,
            "amount": amount,
            "payer_id": str(payer_id),
            "payer_type": payer_type,
            "payee_id": str(payee_id) if payee_id else None,
            "payee_type": payee_type,
            "ip_address": ip_address,
            "device_id": device_id,
            "location": location,
            **(metadata or {}),
        }

        # Resultados
        matched_rules = []
        matched_patterns = []
        alerts_generated = []
        total_risk_score = 0
        decision_reasons = []
        recommendations = []
        required_actions = []

        # 1. Buscar perfil de risco do pagador
        profile = self.repository.get_or_create_profile(
            EntityType(payer_type) if payer_type in [e.value for e in EntityType] else EntityType.USER,
            payer_id,
        )

        # Verificar se esta bloqueado
        if profile.is_blocked:
            return {
                "transaction_id": transaction_id,
                "is_allowed": False,
                "risk_score": 100,
                "risk_level": RiskLevel.BLOCKED,
                "decision": "block",
                "decision_reasons": ["Entidade bloqueada"],
                "matched_rules": [],
                "matched_patterns": [],
                "alerts_generated": [],
                "recommendations": ["Verificar motivo do bloqueio"],
                "required_actions": ["Desbloquear entidade se apropriado"],
                "processing_time_ms": int((time.time() - start_time) * 1000),
            }

        # Adicionar score do perfil
        total_risk_score += profile.risk_score * 0.3

        # 2. Avaliar regras
        rules = self.repository.get_active_rules(
            applies_to=transaction_type,
        )

        for rule in rules:
            matched, score, reasons = rule.evaluate(data)
            if matched:
                matched_rules.append(rule.code)
                total_risk_score += score
                decision_reasons.extend(reasons)

                # Registrar trigger
                rule.increment_trigger()

                logger.info(f"Regra {rule.code} acionada")

        # 3. Verificar padroes
        patterns = self.repository.get_active_patterns(
            category="financial",
        )

        for pattern in patterns:
            matched, confidence, indicators = pattern.match(
                {
                    "indicators": self._extract_indicators(data, profile),
                }
            )
            if matched:
                matched_patterns.append(pattern.code)
                total_risk_score += pattern.risk_score * confidence * 0.5
                decision_reasons.append(f"Padrao detectado: {pattern.name}")

                logger.info(f"Padrao {pattern.code} detectado")

        # 4. Verificar limites
        if profile.transaction_limit_daily:
            if amount > profile.transaction_limit_daily:
                total_risk_score += 20
                decision_reasons.append("Valor excede limite diario")
                required_actions.append("Aprovar manualmente")

        # 5. Verificar valor atipico
        if profile.avg_transaction_value > 0:
            if amount > profile.avg_transaction_value * 5:
                total_risk_score += 15
                decision_reasons.append("Valor muito acima da media")

        # 6. Normalizar score
        risk_score = min(100, total_risk_score)

        # 7. Determinar nivel e decisao
        risk_level, decision = self._determine_decision(risk_score, matched_rules, matched_patterns)

        # 8. Gerar alertas se necessario
        if decision in ("review", "block"):
            alert = self._create_transaction_alert(
                transaction_id=transaction_id,
                transaction_type=transaction_type,
                amount=amount,
                entity_type=payer_type,
                entity_id=payer_id,
                risk_score=risk_score,
                matched_rules=matched_rules,
                matched_patterns=matched_patterns,
                decision_reasons=decision_reasons,
                ip_address=ip_address,
                location=location,
            )
            if alert:
                alerts_generated.append(alert.id)

        # 9. Atualizar perfil
        profile.record_transaction(amount, suspicious=(decision != "approve"))
        self.db.commit()

        # 10. Gerar recomendacoes
        if risk_score >= 50:
            recommendations.append("Verificar identidade do pagador")
        if matched_patterns:
            recommendations.append("Investigar padrao de fraude detectado")

        processing_time = int((time.time() - start_time) * 1000)

        logger.info(
            f"Transacao {transaction_id} verificada: {decision} (score: {risk_score:.1f}, tempo: {processing_time}ms)"
        )

        return {
            "transaction_id": transaction_id,
            "is_allowed": decision == "approve",
            "risk_score": risk_score,
            "risk_level": risk_level,
            "decision": decision,
            "decision_reasons": decision_reasons,
            "matched_rules": matched_rules,
            "matched_patterns": matched_patterns,
            "alerts_generated": alerts_generated,
            "recommendations": recommendations,
            "required_actions": required_actions,
            "processing_time_ms": processing_time,
        }

    def check_access(
        self,
        user_id: UUID,
        ip_address: str,
        action: str,
        session_id: str | None = None,
        device_id: str | None = None,
        user_agent: str | None = None,
        location: str | None = None,
        geo_coordinates: dict[str, float] | None = None,
        resource: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Verifica acesso para fraude.

        Args:
            user_id: ID do usuario
            ip_address: IP de origem
            action: Acao (login, password_reset, etc)
            session_id: ID da sessao
            device_id: ID do dispositivo
            user_agent: User agent
            location: Localizacao
            geo_coordinates: Coordenadas
            resource: Recurso acessado
            metadata: Dados adicionais

        Returns:
            Dict com decisao e detalhes
        """
        start_time = time.time()
        logger.info(f"Verificando acesso de {user_id}: {action}")

        # Buscar ou criar perfil
        profile = self.repository.get_or_create_profile(
            EntityType.USER,
            user_id,
        )

        # Resultados
        anomalies = []
        risk_factors = []
        alerts_generated = []
        total_risk_score = profile.risk_score * 0.2

        # Verificar se bloqueado
        if profile.is_blocked:
            return {
                "user_id": user_id,
                "is_allowed": False,
                "risk_score": 100,
                "risk_level": RiskLevel.BLOCKED,
                "decision": "block",
                "challenge_type": None,
                "anomalies_detected": ["Usuario bloqueado"],
                "risk_factors": [],
                "is_new_device": False,
                "is_new_location": False,
                "is_unusual_time": False,
                "alerts_generated": [],
                "processing_time_ms": int((time.time() - start_time) * 1000),
            }

        # Verificar dispositivo novo
        is_new_device = False
        if device_id and device_id not in (profile.known_devices or []):
            is_new_device = True
            anomalies.append("new_device")
            risk_factors.append("Dispositivo desconhecido")
            total_risk_score += 15

        # Verificar IP novo
        if ip_address and ip_address not in (profile.known_ips or []):
            anomalies.append("new_ip")
            risk_factors.append("IP desconhecido")
            total_risk_score += 10

        # Verificar localizacao nova
        is_new_location = False
        if location and location not in (profile.known_locations or []):
            is_new_location = True
            anomalies.append("new_location")
            risk_factors.append("Localizacao nova")
            total_risk_score += 20

        # Verificar horario atipico
        is_unusual_time = False
        current_hour = datetime.utcnow().hour
        typical_hours = profile.typical_hours or {}
        if typical_hours:
            usual_hours = [h for h, count in typical_hours.items() if count > 5]
            if str(current_hour) not in usual_hours:
                is_unusual_time = True
                anomalies.append("unusual_time")
                risk_factors.append("Horario atipico")
                total_risk_score += 10

        # Verificar falhas recentes
        if profile.failed_logins > 3:
            anomalies.append("multiple_failures")
            risk_factors.append(f"{profile.failed_logins} falhas de login recentes")
            total_risk_score += min(profile.failed_logins * 5, 30)

        # Avaliar regras de acesso
        rules = self.repository.get_active_rules(
            category="access",
        )

        for rule in rules:
            data = {
                "action": action,
                "ip_address": ip_address,
                "device_id": device_id,
                "is_new_device": is_new_device,
                "is_new_location": is_new_location,
                "failed_logins": profile.failed_logins,
            }
            matched, score, reasons = rule.evaluate(data)
            if matched:
                total_risk_score += score
                risk_factors.extend(reasons)
                rule.increment_trigger()

        # Normalizar score
        risk_score = min(100, total_risk_score)

        # Determinar decisao
        if risk_score >= 80:
            decision = "block"
            challenge_type = None
        elif risk_score >= 50:
            decision = "challenge"
            challenge_type = "mfa" if action == "login" else "captcha"
        elif risk_score >= 30:
            decision = "challenge"
            challenge_type = "captcha"
        else:
            decision = "allow"
            challenge_type = None

        # Determinar nivel
        if risk_score >= 80:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 60:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 40:
            risk_level = RiskLevel.MEDIUM
        elif risk_score >= 20:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.MINIMAL

        # Gerar alerta se necessario
        if decision in ("challenge", "block"):
            alert = self._create_access_alert(
                user_id=user_id,
                action=action,
                risk_score=risk_score,
                anomalies=anomalies,
                risk_factors=risk_factors,
                ip_address=ip_address,
                device_id=device_id,
                location=location,
            )
            if alert:
                alerts_generated.append(alert.id)

        # Registrar login no perfil
        profile.record_login(
            ip=ip_address,
            device=device_id or "unknown",
            location=location,
            success=(decision == "allow"),
        )
        self.db.commit()

        processing_time = int((time.time() - start_time) * 1000)

        logger.info(f"Acesso de {user_id} verificado: {decision} (score: {risk_score:.1f}, tempo: {processing_time}ms)")

        return {
            "user_id": user_id,
            "is_allowed": decision == "allow",
            "risk_score": risk_score,
            "risk_level": risk_level,
            "decision": decision,
            "challenge_type": challenge_type,
            "anomalies_detected": anomalies,
            "risk_factors": risk_factors,
            "is_new_device": is_new_device,
            "is_new_location": is_new_location,
            "is_unusual_time": is_unusual_time,
            "alerts_generated": alerts_generated,
            "processing_time_ms": processing_time,
        }

    def _determine_decision(
        self,
        risk_score: float,
        matched_rules: list[str],
        matched_patterns: list[str],
    ) -> tuple[RiskLevel, str]:
        """Determina nivel de risco e decisao."""
        if risk_score >= 80 or len(matched_patterns) >= 2:
            return RiskLevel.CRITICAL, "block"
        elif risk_score >= 60:
            return RiskLevel.HIGH, "review"
        elif risk_score >= 40 or matched_rules:
            return RiskLevel.MEDIUM, "review"
        elif risk_score >= 20:
            return RiskLevel.LOW, "approve"
        else:
            return RiskLevel.MINIMAL, "approve"

    def _extract_indicators(
        self,
        data: dict[str, Any],
        profile: RiskProfile,
    ) -> list[str]:
        """Extrai indicadores dos dados."""
        indicators = []

        # Valor alto
        if data.get("amount", 0) > 10000:
            indicators.append("high_value_transaction")

        # Multiplas transacoes
        if profile.total_transactions > 50:
            indicators.append("high_transaction_volume")

        # IP desconhecido
        if data.get("ip_address") and data["ip_address"] not in (profile.known_ips or []):
            indicators.append("unknown_ip")

        # Dispositivo desconhecido
        if data.get("device_id") and data["device_id"] not in (profile.known_devices or []):
            indicators.append("unknown_device")

        # Perfil de alto risco
        if profile.is_high_risk:
            indicators.append("high_risk_profile")

        return indicators

    def _create_transaction_alert(
        self,
        transaction_id: UUID,
        transaction_type: str,
        amount: float,
        entity_type: str,
        entity_id: UUID,
        risk_score: float,
        matched_rules: list[str],
        matched_patterns: list[str],
        decision_reasons: list[str],
        ip_address: str | None = None,
        location: str | None = None,
    ) -> FraudAlert | None:
        """Cria alerta de transacao."""
        # Determinar severidade
        if risk_score >= 80:
            severity = AlertSeverity.CRITICAL
        elif risk_score >= 60:
            severity = AlertSeverity.HIGH
        elif risk_score >= 40:
            severity = AlertSeverity.MEDIUM
        else:
            severity = AlertSeverity.LOW

        alert_data = {
            "category": FraudCategory.TRANSACTION,
            "severity": severity,
            "title": f"Transacao suspeita: {transaction_type}",
            "description": "; ".join(decision_reasons),
            "entity_type": entity_type,
            "entity_id": entity_id,
            "transaction_id": transaction_id,
            "transaction_type": transaction_type,
            "transaction_value": amount,
            "risk_score": risk_score,
            "indicators": matched_rules + matched_patterns,
            "evidence": [{"type": "rules", "matched": matched_rules}],
            "ip_address": ip_address,
            "location": location,
            "potential_loss": amount,
            "requires_immediate_action": severity in (AlertSeverity.HIGH, AlertSeverity.CRITICAL),
        }

        return self.repository.create_alert(alert_data)

    def _create_access_alert(
        self,
        user_id: UUID,
        action: str,
        risk_score: float,
        anomalies: list[str],
        risk_factors: list[str],
        ip_address: str | None = None,
        device_id: str | None = None,
        location: str | None = None,
    ) -> FraudAlert | None:
        """Cria alerta de acesso."""
        if risk_score >= 70:
            severity = AlertSeverity.HIGH
        elif risk_score >= 50:
            severity = AlertSeverity.MEDIUM
        else:
            severity = AlertSeverity.LOW

        alert_data = {
            "category": FraudCategory.ACCESS,
            "severity": severity,
            "title": f"Acesso suspeito: {action}",
            "description": "; ".join(risk_factors),
            "entity_type": "user",
            "entity_id": user_id,
            "risk_score": risk_score,
            "indicators": anomalies,
            "ip_address": ip_address,
            "device_id": device_id,
            "location": location,
            "requires_immediate_action": severity == AlertSeverity.HIGH,
        }

        return self.repository.create_alert(alert_data)
