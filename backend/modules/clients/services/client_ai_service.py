"""
Client AI Service - Inteligência Artificial para Clientes
Sprint 30: Cadastro de Clientes/Condomínios
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from modules.clients.models.client import Client, ClientType, ClientStatus, ClientSegment
from modules.clients.models.condominium import Condominium, CondominiumStatus
from modules.clients.models.unit import Unit
from modules.clients.models.client_contract import ClientContract, ServiceStatus

logger = logging.getLogger(__name__)


class ClientAIService:
    """
    Serviço de IA para análise e insights de clientes.

    Funcionalidades:
    - Análise de perfil do cliente
    - Segmentação automática
    - Predição de churn (risco de perda)
    - Recomendações de upsell/cross-sell
    - Insights de condomínios
    - Score de saúde do relacionamento
    """

    def __init__(self, db: Session):
        self.db = db

    def analyze_client_profile(self, client_id: UUID) -> Dict[str, Any]:
        """
        Analisa o perfil completo de um cliente.

        Returns:
            Dict com análise do perfil, scores e recomendações.
        """
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return {"error": "Cliente não encontrado"}

        # Calcular scores
        health_score = self._calculate_health_score(client)
        engagement_score = self._calculate_engagement_score(client)
        value_score = self._calculate_value_score(client)
        risk_level = self._assess_risk_level(client)

        # Identificar padrões
        patterns = self._identify_patterns(client)

        # Gerar recomendações
        recommendations = self._generate_recommendations(client, health_score, risk_level)

        return {
            "client_id": str(client.id),
            "client_code": client.code,
            "client_name": client.display_name,
            "scores": {
                "health_score": health_score,
                "engagement_score": engagement_score,
                "value_score": value_score,
                "overall_score": round((health_score + engagement_score + value_score) / 3, 1)
            },
            "risk_assessment": {
                "level": risk_level,
                "factors": self._get_risk_factors(client),
                "probability": self._calculate_churn_probability(client)
            },
            "patterns": patterns,
            "recommendations": recommendations,
            "analysis_date": datetime.utcnow().isoformat()
        }

    def suggest_segmentation(self, client_id: UUID) -> Dict[str, Any]:
        """
        Sugere segmentação automática para o cliente.

        Returns:
            Dict com segmento sugerido e justificativa.
        """
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return {"error": "Cliente não encontrado"}

        # Calcular score de valor
        value_score = self._calculate_value_score(client)

        # Determinar segmento baseado em critérios
        suggested_segment = self._determine_segment(client, value_score)

        # Justificativa
        justification = self._get_segmentation_justification(client, suggested_segment)

        return {
            "client_id": str(client.id),
            "current_segment": client.segment.value if client.segment else None,
            "suggested_segment": suggested_segment.value,
            "confidence": self._calculate_segment_confidence(client, suggested_segment),
            "justification": justification,
            "criteria": {
                "revenue": float(client.total_revenue or 0),
                "contracts": client.active_contracts,
                "relationship_days": self._get_relationship_days(client),
                "is_vip": client.is_vip
            }
        }

    def predict_churn_risk(self, client_id: UUID) -> Dict[str, Any]:
        """
        Prediz risco de churn (perda do cliente).

        Returns:
            Dict com probabilidade de churn e fatores de risco.
        """
        client = self.db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return {"error": "Cliente não encontrado"}

        probability = self._calculate_churn_probability(client)
        risk_factors = self._get_risk_factors(client)
        retention_actions = self._suggest_retention_actions(client, probability)

        return {
            "client_id": str(client.id),
            "churn_probability": probability,
            "risk_level": self._probability_to_level(probability),
            "risk_factors": risk_factors,
            "positive_factors": self._get_positive_factors(client),
            "retention_actions": retention_actions,
            "estimated_revenue_at_risk": float(client.total_revenue or 0) * (probability / 100),
            "prediction_date": datetime.utcnow().isoformat()
        }

    def recommend_services(self, client_id: UUID) -> Dict[str, Any]:
        """
        Recomenda serviços para upsell/cross-sell.

        Returns:
            Dict com serviços recomendados e justificativa.
        """
        client = (
            self.db.query(Client)
            .filter(Client.id == client_id)
            .first()
        )
        if not client:
            return {"error": "Cliente não encontrado"}

        # Obter serviços atuais
        current_services = (
            self.db.query(ClientContract)
            .filter(ClientContract.client_id == client_id)
            .filter(ClientContract.status == ServiceStatus.ATIVO)
            .all()
        )

        current_types = {s.service_type for s in current_services}

        # Gerar recomendações
        recommendations = self._generate_service_recommendations(client, current_types)

        return {
            "client_id": str(client.id),
            "current_services": [s.service_type.value for s in current_services],
            "recommendations": recommendations,
            "potential_revenue_increase": sum(r["estimated_value"] for r in recommendations),
            "recommendation_date": datetime.utcnow().isoformat()
        }

    def analyze_condominium_health(self, condominium_id: UUID) -> Dict[str, Any]:
        """
        Analisa a saúde de um condomínio.

        Returns:
            Dict com métricas de saúde do condomínio.
        """
        condominium = (
            self.db.query(Condominium)
            .filter(Condominium.id == condominium_id)
            .first()
        )
        if not condominium:
            return {"error": "Condomínio não encontrado"}

        # Obter unidades
        units = (
            self.db.query(Unit)
            .filter(Unit.condominium_id == condominium_id)
            .all()
        )

        # Calcular métricas
        occupancy_rate = condominium.occupancy_rate
        defaulter_rate = self._calculate_defaulter_rate(units)
        security_score = self._calculate_security_score(condominium)
        infrastructure_score = self._calculate_infrastructure_score(condominium)

        # Score geral
        health_score = self._calculate_condominium_health_score(
            occupancy_rate, defaulter_rate, security_score, infrastructure_score
        )

        # Alertas e recomendações
        alerts = self._get_condominium_alerts(condominium, units, defaulter_rate)
        recommendations = self._get_condominium_recommendations(
            condominium, health_score, defaulter_rate
        )

        return {
            "condominium_id": str(condominium.id),
            "condominium_name": condominium.name,
            "health_score": health_score,
            "metrics": {
                "occupancy_rate": occupancy_rate,
                "defaulter_rate": defaulter_rate,
                "security_score": security_score,
                "infrastructure_score": infrastructure_score
            },
            "unit_stats": {
                "total": condominium.total_units,
                "occupied": len([u for u in units if u.is_occupied]),
                "defaulters": len([u for u in units if u.is_defaulter])
            },
            "alerts": alerts,
            "recommendations": recommendations,
            "analysis_date": datetime.utcnow().isoformat()
        }

    def get_dashboard_insights(self) -> Dict[str, Any]:
        """
        Gera insights para o dashboard gerencial.

        Returns:
            Dict com insights consolidados.
        """
        # Métricas gerais
        total_clients = self.db.query(func.count(Client.id)).scalar() or 0
        active_clients = (
            self.db.query(func.count(Client.id))
            .filter(Client.status == ClientStatus.ATIVO)
            .scalar() or 0
        )
        defaulter_clients = (
            self.db.query(func.count(Client.id))
            .filter(Client.is_defaulter.is_(True))
            .scalar() or 0
        )

        # Clientes em risco
        at_risk_clients = self._get_clients_at_risk()

        # Contratos expirando
        expiring_contracts = self._get_expiring_contracts()

        # Tendências
        trends = self._calculate_trends()

        # Alertas críticos
        critical_alerts = self._get_critical_alerts()

        return {
            "overview": {
                "total_clients": total_clients,
                "active_clients": active_clients,
                "defaulter_clients": defaulter_clients,
                "defaulter_rate": (
                    (defaulter_clients / total_clients * 100) if total_clients > 0 else 0
                )
            },
            "clients_at_risk": at_risk_clients,
            "expiring_contracts": expiring_contracts,
            "trends": trends,
            "critical_alerts": critical_alerts,
            "generated_at": datetime.utcnow().isoformat()
        }

    # =========================================================================
    # MÉTODOS PRIVADOS - CÁLCULOS
    # =========================================================================

    def _calculate_health_score(self, client: Client) -> int:
        """Calcula score de saúde do cliente (0-100)."""
        score = 100

        # Status
        if client.status == ClientStatus.INADIMPLENTE:
            score -= 40
        elif client.status == ClientStatus.SUSPENSO:
            score -= 30
        elif client.status == ClientStatus.BLOQUEADO:
            score -= 50
        elif client.status != ClientStatus.ATIVO:
            score -= 20

        # Inadimplência
        if client.is_defaulter:
            days = client.days_as_defaulter or 0
            if days > 90:
                score -= 25
            elif days > 60:
                score -= 15
            elif days > 30:
                score -= 10

        # Contratos ativos
        if client.active_contracts == 0:
            score -= 15
        elif client.active_contracts >= 3:
            score += 5

        # Satisfação
        if client.satisfaction_score:
            if client.satisfaction_score >= 4.5:
                score += 10
            elif client.satisfaction_score < 3:
                score -= 10

        # VIP
        if client.is_vip:
            score += 5

        return max(0, min(100, score))

    def _calculate_engagement_score(self, client: Client) -> int:
        """Calcula score de engajamento (0-100)."""
        score = 50

        # Contratos
        if client.active_contracts >= 3:
            score += 20
        elif client.active_contracts >= 1:
            score += 10

        # Integrações ativas
        if client.guardian_enabled:
            score += 10
        if client.plus_enabled:
            score += 10

        # Tempo de relacionamento
        days = self._get_relationship_days(client)
        if days > 730:  # 2+ anos
            score += 15
        elif days > 365:  # 1+ ano
            score += 10
        elif days > 180:  # 6+ meses
            score += 5

        # NPS
        if client.nps_score:
            if client.nps_score >= 9:
                score += 10
            elif client.nps_score >= 7:
                score += 5
            elif client.nps_score <= 6:
                score -= 10

        return max(0, min(100, score))

    def _calculate_value_score(self, client: Client) -> int:
        """Calcula score de valor do cliente (0-100)."""
        score = 0

        # Receita total
        revenue = float(client.total_revenue or 0)
        if revenue >= 100000:
            score += 40
        elif revenue >= 50000:
            score += 30
        elif revenue >= 20000:
            score += 20
        elif revenue >= 5000:
            score += 10

        # Ticket médio
        avg_ticket = float(client.average_ticket or 0)
        if avg_ticket >= 5000:
            score += 20
        elif avg_ticket >= 2000:
            score += 15
        elif avg_ticket >= 1000:
            score += 10

        # Contratos
        if client.total_contracts >= 5:
            score += 20
        elif client.total_contracts >= 3:
            score += 15
        elif client.total_contracts >= 1:
            score += 10

        # VIP
        if client.is_vip:
            score += 10

        # Segmento
        if client.segment == ClientSegment.ENTERPRISE:
            score += 10
        elif client.segment == ClientSegment.GRANDE:
            score += 5

        return max(0, min(100, score))

    def _assess_risk_level(self, client: Client) -> str:
        """Avalia nível de risco do cliente."""
        probability = self._calculate_churn_probability(client)
        return self._probability_to_level(probability)

    def _calculate_churn_probability(self, client: Client) -> float:
        """Calcula probabilidade de churn (0-100)."""
        probability = 10.0  # Base

        # Status negativo
        if client.status == ClientStatus.INADIMPLENTE:
            probability += 35
        elif client.status == ClientStatus.SUSPENSO:
            probability += 25
        elif client.status == ClientStatus.BLOQUEADO:
            probability += 45

        # Inadimplência
        if client.is_defaulter:
            days = client.days_as_defaulter or 0
            if days > 90:
                probability += 30
            elif days > 60:
                probability += 20
            elif days > 30:
                probability += 10

        # Sem contratos ativos
        if client.active_contracts == 0:
            probability += 20

        # Satisfação baixa
        if client.satisfaction_score and client.satisfaction_score < 3:
            probability += 15

        # NPS detrator
        if client.nps_score and client.nps_score <= 6:
            probability += 10

        # Fatores positivos (reduzem probabilidade)
        if client.is_vip:
            probability -= 10

        if client.satisfaction_score and client.satisfaction_score >= 4.5:
            probability -= 10

        days = self._get_relationship_days(client)
        if days > 730:
            probability -= 15
        elif days > 365:
            probability -= 10

        return max(0.0, min(100.0, probability))

    def _probability_to_level(self, probability: float) -> str:
        """Converte probabilidade em nível de risco."""
        if probability >= 70:
            return "critico"
        elif probability >= 50:
            return "alto"
        elif probability >= 30:
            return "medio"
        return "baixo"

    def _get_relationship_days(self, client: Client) -> int:
        """Retorna dias de relacionamento."""
        start = client.first_contract_date or client.acquisition_date or client.created_at.date()
        return (date.today() - start).days

    def _determine_segment(self, client: Client, _value_score: int) -> ClientSegment:
        """Determina segmento sugerido."""
        revenue = float(client.total_revenue or 0)

        if revenue >= 100000 or client.active_contracts >= 5:
            return ClientSegment.ENTERPRISE
        elif revenue >= 50000 or client.active_contracts >= 3:
            return ClientSegment.GRANDE
        elif revenue >= 20000 or client.active_contracts >= 2:
            return ClientSegment.MEDIO
        return ClientSegment.PEQUENO

    def _calculate_segment_confidence(
        self, client: Client, _segment: ClientSegment
    ) -> float:
        """Calcula confiança na segmentação."""
        confidence = 70.0

        # Dados completos aumentam confiança
        if client.total_revenue and client.total_revenue > 0:
            confidence += 10
        if client.active_contracts > 0:
            confidence += 10
        if client.first_contract_date:
            confidence += 5
        if client.satisfaction_score:
            confidence += 5

        return min(100.0, confidence)

    def _calculate_defaulter_rate(self, units: List[Unit]) -> float:
        """Calcula taxa de inadimplência das unidades."""
        if not units:
            return 0.0
        defaulters = len([u for u in units if u.is_defaulter])
        return (defaulters / len(units)) * 100

    def _calculate_security_score(self, condominium: Condominium) -> int:
        """Calcula score de segurança do condomínio."""
        score = 0
        if condominium.has_24h_security:
            score += 30
        if condominium.has_cctv:
            score += 25
        if condominium.has_access_control:
            score += 25
        if condominium.has_electric_fence:
            score += 10
        if condominium.has_alarm:
            score += 10
        return min(100, score)

    def _calculate_infrastructure_score(self, condominium: Condominium) -> int:
        """Calcula score de infraestrutura."""
        score = 50
        if condominium.total_elevators and condominium.total_elevators > 0:
            score += 10
        if condominium.has_pool:
            score += 10
        if condominium.has_gym:
            score += 10
        if condominium.has_party_room:
            score += 10
        if condominium.guardian_enabled:
            score += 5
        if condominium.plus_enabled:
            score += 5
        return min(100, score)

    def _calculate_condominium_health_score(
        self,
        occupancy_rate: float,
        defaulter_rate: float,
        security_score: int,
        infrastructure_score: int
    ) -> int:
        """Calcula score de saúde do condomínio."""
        # Pesos: ocupação 30%, inadimplência 30%, segurança 25%, infraestrutura 15%
        occupancy_component = (occupancy_rate / 100) * 30
        defaulter_component = ((100 - defaulter_rate) / 100) * 30
        security_component = (security_score / 100) * 25
        infra_component = (infrastructure_score / 100) * 15

        return int(occupancy_component + defaulter_component + security_component + infra_component)

    # =========================================================================
    # MÉTODOS PRIVADOS - INSIGHTS E RECOMENDAÇÕES
    # =========================================================================

    def _get_risk_factors(self, client: Client) -> List[str]:
        """Identifica fatores de risco."""
        factors = []

        if client.status == ClientStatus.INADIMPLENTE:
            factors.append("Cliente inadimplente")
        if client.status == ClientStatus.SUSPENSO:
            factors.append("Cliente suspenso")
        if client.is_defaulter:
            days = client.days_as_defaulter or 0
            factors.append(f"Inadimplente há {days} dias")
        if client.active_contracts == 0:
            factors.append("Sem contratos ativos")
        if client.satisfaction_score and client.satisfaction_score < 3:
            factors.append("Satisfação baixa")
        if client.nps_score and client.nps_score <= 6:
            factors.append("NPS detrator")

        return factors

    def _get_positive_factors(self, client: Client) -> List[str]:
        """Identifica fatores positivos."""
        factors = []

        if client.is_vip:
            factors.append("Cliente VIP")
        if client.satisfaction_score and client.satisfaction_score >= 4.5:
            factors.append("Alta satisfação")
        if client.nps_score and client.nps_score >= 9:
            factors.append("NPS promotor")
        if client.active_contracts >= 3:
            factors.append("Múltiplos contratos ativos")

        days = self._get_relationship_days(client)
        if days > 730:
            factors.append("Cliente há mais de 2 anos")
        elif days > 365:
            factors.append("Cliente há mais de 1 ano")

        return factors

    def _identify_patterns(self, client: Client) -> List[str]:
        """Identifica padrões de comportamento."""
        patterns = []

        if client.type == ClientType.CONDOMINIO and client.active_contracts >= 2:
            patterns.append("Condomínio com múltiplos serviços")

        if client.guardian_enabled and client.plus_enabled:
            patterns.append("Uso integrado Guardian + Plus")

        if client.is_vip and client.satisfaction_score and client.satisfaction_score >= 4:
            patterns.append("Cliente premium satisfeito")

        return patterns

    def _generate_recommendations(
        self,
        client: Client,
        health_score: int,
        risk_level: str
    ) -> List[Dict[str, str]]:
        """Gera recomendações para o cliente."""
        recommendations = []

        if risk_level in ("critico", "alto"):
            recommendations.append({
                "type": "urgent",
                "action": "Agendar reunião de retenção",
                "reason": f"Cliente com risco {risk_level} de churn"
            })

        if client.is_defaulter:
            recommendations.append({
                "type": "financial",
                "action": "Propor acordo de renegociação",
                "reason": "Cliente inadimplente"
            })

        if health_score < 50:
            recommendations.append({
                "type": "relationship",
                "action": "Plano de recuperação de relacionamento",
                "reason": "Score de saúde baixo"
            })

        if not client.guardian_enabled and client.type == ClientType.CONDOMINIO:
            recommendations.append({
                "type": "upsell",
                "action": "Apresentar Conecta Guardian",
                "reason": "Condomínio sem integração de segurança"
            })

        if not client.plus_enabled and client.type == ClientType.CONDOMINIO:
            recommendations.append({
                "type": "upsell",
                "action": "Apresentar Conecta Plus",
                "reason": "Condomínio sem gestão condominial"
            })

        return recommendations

    def _suggest_retention_actions(
        self,
        client: Client,
        probability: float
    ) -> List[Dict[str, Any]]:
        """Sugere ações de retenção."""
        actions = []

        if probability >= 50:
            actions.append({
                "action": "Contato urgente do gerente de contas",
                "priority": "alta",
                "deadline_days": 3
            })

        if client.is_defaulter:
            actions.append({
                "action": "Proposta de renegociação de débito",
                "priority": "alta",
                "deadline_days": 7
            })

        if client.satisfaction_score and client.satisfaction_score < 3:
            actions.append({
                "action": "Pesquisa de satisfação detalhada",
                "priority": "media",
                "deadline_days": 14
            })

        if probability >= 30:
            actions.append({
                "action": "Oferta de benefícios de fidelidade",
                "priority": "media",
                "deadline_days": 30
            })

        return actions

    def _generate_service_recommendations(
        self,
        _client: Client,
        current_types: set
    ) -> List[Dict[str, Any]]:
        """Gera recomendações de serviços."""
        recommendations = []

        # Mapeamento de serviços complementares
        service_map = {
            "portaria_remota": ["cftv", "controle_acesso", "alarme"],
            "cftv": ["portaria_remota", "monitoramento_24h"],
            "controle_acesso": ["portaria_remota", "cftv"],
            "alarme": ["monitoramento_24h", "cerca_eletrica"]
        }

        current_values = {t.value for t in current_types}

        for current in current_values:
            if current in service_map:
                for suggested in service_map[current]:
                    if suggested not in current_values:
                        recommendations.append({
                            "service": suggested,
                            "reason": f"Complementar ao serviço de {current}",
                            "estimated_value": 500.0,
                            "confidence": 0.75
                        })

        return recommendations[:5]  # Limitar a 5 recomendações

    def _get_segmentation_justification(
        self,
        client: Client,
        segment: ClientSegment
    ) -> str:
        """Gera justificativa para segmentação."""
        revenue = float(client.total_revenue or 0)
        contracts = client.active_contracts

        if segment == ClientSegment.ENTERPRISE:
            return f"R$ {revenue:,.2f} e {contracts} contratos indicam enterprise"
        elif segment == ClientSegment.GRANDE:
            return f"Receita de R$ {revenue:,.2f} indica grande cliente"
        elif segment == ClientSegment.MEDIO:
            return "Perfil de cliente médio baseado em receita e contratos"
        return "Perfil de cliente pequeno baseado em volume de negócios"

    def _get_condominium_alerts(
        self,
        condominium: Condominium,
        _units: List[Unit],
        defaulter_rate: float
    ) -> List[Dict[str, str]]:
        """Gera alertas para o condomínio."""
        alerts = []

        if defaulter_rate > 20:
            alerts.append({
                "type": "critical",
                "message": f"Taxa de inadimplência alta: {defaulter_rate:.1f}%"
            })

        if condominium.syndic_end_date:
            days = condominium.days_until_syndic_end
            if days and days <= 30:
                alerts.append({
                    "type": "warning",
                    "message": f"Mandato do síndico expira em {days} dias"
                })

        if condominium.status == CondominiumStatus.EM_IMPLANTACAO:
            alerts.append({
                "type": "info",
                "message": "Condomínio em implantação"
            })

        return alerts

    def _get_condominium_recommendations(
        self,
        condominium: Condominium,
        health_score: int,
        defaulter_rate: float
    ) -> List[str]:
        """Gera recomendações para o condomínio."""
        recommendations = []

        if defaulter_rate > 15:
            recommendations.append("Implementar programa de cobrança proativa")

        if health_score < 60:
            recommendations.append("Revisar SLAs e qualidade do atendimento")

        if not condominium.guardian_enabled:
            recommendations.append("Avaliar integração com Conecta Guardian")

        if not condominium.plus_enabled:
            recommendations.append("Avaliar integração com Conecta Plus")

        if condominium.security_level == "minimo":
            recommendations.append("Propor upgrade de sistema de segurança")

        return recommendations

    def _get_clients_at_risk(self) -> List[Dict[str, Any]]:
        """Retorna clientes em risco."""
        clients = (
            self.db.query(Client)
            .filter(Client.status.in_([
                ClientStatus.INADIMPLENTE,
                ClientStatus.SUSPENSO
            ]))
            .limit(10)
            .all()
        )

        return [
            {
                "id": str(c.id),
                "code": c.code,
                "name": c.display_name,
                "status": c.status.value,
                "risk_level": self._assess_risk_level(c)
            }
            for c in clients
        ]

    def _get_expiring_contracts(self) -> List[Dict[str, Any]]:
        """Retorna contratos expirando em 30 dias."""
        threshold = date.today() + timedelta(days=30)
        contracts = (
            self.db.query(ClientContract)
            .filter(ClientContract.end_date <= threshold)
            .filter(ClientContract.end_date >= date.today())
            .filter(ClientContract.status == ServiceStatus.ATIVO)
            .limit(10)
            .all()
        )

        return [
            {
                "id": str(c.id),
                "service_type": c.service_type.value,
                "client_id": str(c.client_id),
                "end_date": c.end_date.isoformat() if c.end_date else None,
                "days_until_end": c.days_until_end
            }
            for c in contracts
        ]

    def _calculate_trends(self) -> Dict[str, Any]:
        """Calcula tendências."""
        # Simplificado para demonstração
        return {
            "new_clients_trend": "stable",
            "churn_trend": "decreasing",
            "revenue_trend": "increasing"
        }

    def _get_critical_alerts(self) -> List[Dict[str, str]]:
        """Retorna alertas críticos."""
        alerts = []

        # Clientes críticos
        critical_count = (
            self.db.query(func.count(Client.id))
            .filter(Client.status == ClientStatus.INADIMPLENTE)
            .filter(Client.is_defaulter.is_(True))
            .scalar() or 0
        )

        if critical_count > 0:
            alerts.append({
                "type": "critical",
                "message": f"{critical_count} clientes em situação crítica de inadimplência"
            })

        return alerts
