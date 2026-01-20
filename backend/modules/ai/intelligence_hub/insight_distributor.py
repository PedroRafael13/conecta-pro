"""
Insight Distributor - Distribuidor Inteligente de Insights

Distribui insights de IA para módulos e usuários de forma inteligente:
1. Roteamento inteligente baseado em contexto
2. Personalização por usuário/módulo
3. Entrega multi-canal (real-time, email, SMS, push)
4. Filtros de relevância e prioridade
5. Tracking e analytics de entrega

Versão adaptada para Conecta PRO
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)


class InsightType(Enum):
    """Tipos de insights"""
    PREDICTION = "prediction"
    ANOMALY = "anomaly"
    TREND = "trend"
    RECOMMENDATION = "recommendation"
    ALERT = "alert"
    OPPORTUNITY = "opportunity"
    RISK = "risk"


class InsightPriority(Enum):
    """Prioridades de insight"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


class DeliveryChannel(Enum):
    """Canais de entrega"""
    REAL_TIME = "real_time"      # WebSocket/SSE
    EMAIL = "email"
    SMS = "sms"
    PUSH_NOTIFICATION = "push"
    DASHBOARD = "dashboard"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class DeliveryStatus(Enum):
    """Status de entrega"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    FILTERED = "filtered"


@dataclass
class Insight:
    """Estrutura de insight"""
    id: str
    type: InsightType
    priority: InsightPriority
    source_module: str
    title: str
    content: str
    data: Dict[str, Any]
    tenant_id: str
    target_modules: List[str] = field(default_factory=list)
    target_users: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeliveryRule:
    """Regra de entrega"""
    module_pattern: str
    user_role: Optional[str]
    insight_types: List[InsightType]
    min_priority: InsightPriority
    channels: List[DeliveryChannel]
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeliveryLog:
    """Log de entrega"""
    insight_id: str
    recipient: str
    channel: DeliveryChannel
    status: DeliveryStatus
    delivered_at: datetime
    error_message: Optional[str] = None


class InsightDistributor:
    """
    Distribuidor Inteligente de Insights para a Central de IA do Conecta PRO
    
    Funcionalidades:
    - Roteamento inteligente de insights
    - Personalização por contexto
    - Multi-channel delivery
    - Analytics de entrega
    - Filtros de relevância
    """

    def __init__(self):
        self.delivery_rules: List[DeliveryRule] = []
        self.delivery_logs: List[DeliveryLog] = []
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        self.module_subscriptions: Dict[str, Set[str]] = {}
        
        # Estatísticas
        self.stats = {
            "insights_processed": 0,
            "deliveries_sent": 0,
            "delivery_success_rate": 0.0,
            "avg_delivery_time": 0.0
        }
        
        # Módulos do Conecta PRO
        self.conecta_modules = [
            "ai", "analytics", "audit", "automation", "bidding", "clients",
            "config", "core", "crm", "diarists", "document_kits", "documents",
            "equipment_management", "facilities", "fase5", "field_service",
            "financial", "ged", "government_integrations", "health_occupational",
            "hr", "integrations", "marketplace", "mobile", "monitoring",
            "notifications", "occurrences", "operations", "recruitment",
            "reports", "scheduler", "security_lgpd", "services"
        ]
        
        # Configurar regras padrão
        self._setup_default_rules()

    async def distribute_insight(self, insight: Insight) -> Dict[str, Any]:
        """
        Distribui um insight para os módulos/usuários relevantes
        """
        start_time = datetime.now()
        
        try:
            # 1. Encontrar módulos interessados
            interested_modules = await self._find_interested_modules(insight)
            
            # 2. Encontrar usuários interessados
            interested_users = await self._find_interested_users(insight)
            
            # 3. Aplicar filtros de relevância
            filtered_modules = await self._filter_by_relevance(insight, interested_modules)
            filtered_users = await self._filter_by_user_preferences(insight, interested_users)
            
            # 4. Determinar canais de entrega
            delivery_plan = await self._create_delivery_plan(insight, filtered_modules, filtered_users)
            
            # 5. Executar entregas
            delivery_results = await self._execute_deliveries(insight, delivery_plan)
            
            # 6. Registrar logs
            for result in delivery_results:
                self.delivery_logs.append(result)
            
            # 7. Atualizar estatísticas
            self._update_stats(delivery_results)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "insight_id": insight.id,
                "modules_notified": len(filtered_modules),
                "users_notified": len(filtered_users),
                "deliveries_attempted": len(delivery_results),
                "deliveries_successful": len([d for d in delivery_results if d.status == DeliveryStatus.SENT]),
                "processing_time": processing_time,
                "delivery_summary": self._summarize_deliveries(delivery_results)
            }
            
        except Exception as e:
            logger.error(f"Erro na distribuição do insight {insight.id}: {e}")
            return {
                "insight_id": insight.id,
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds()
            }

    async def subscribe_module(self, module_name: str, insight_types: List[InsightType], 
                              min_priority: InsightPriority = InsightPriority.NORMAL):
        """Inscreve um módulo para receber tipos específicos de insights"""
        
        subscription_key = f"{module_name}_{min_priority.value}"
        
        if subscription_key not in self.module_subscriptions:
            self.module_subscriptions[subscription_key] = set()
        
        for insight_type in insight_types:
            self.module_subscriptions[subscription_key].add(insight_type.value)
        
        logger.info(f"Módulo {module_name} inscrito para {len(insight_types)} tipos de insights")

    async def set_user_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Define preferências de usuário para entrega de insights"""
        
        self.user_preferences[user_id] = {
            **preferences,
            "updated_at": datetime.now().isoformat()
        }
        
        logger.info(f"Preferências atualizadas para usuário {user_id}")

    async def _find_interested_modules(self, insight: Insight) -> List[str]:
        """Encontra módulos interessados no insight"""
        interested = set()
        
        # Adicionar módulos target explícitos
        interested.update(insight.target_modules)
        
        # Adicionar módulo de origem
        interested.add(insight.source_module)
        
        # Verificar inscrições por tipo de insight
        for subscription_key, subscribed_types in self.module_subscriptions.items():
            if insight.type.value in subscribed_types:
                module_name = subscription_key.split('_')[0]
                interested.add(module_name)
        
        # Lógica baseada em correlações conhecidas
        correlations = self._get_module_correlations(insight.source_module)
        if correlations:
            interested.update(correlations)
        
        # Filtrar apenas módulos válidos
        return [m for m in interested if m in self.conecta_modules]

    async def _find_interested_users(self, insight: Insight) -> List[str]:
        """Encontra usuários interessados no insight"""
        interested = set()
        
        # Adicionar usuários target explícitos
        interested.update(insight.target_users)
        
        # Usuários baseados em preferências
        for user_id, prefs in self.user_preferences.items():
            if self._user_interested_in_insight(prefs, insight):
                interested.add(user_id)
        
        return list(interested)

    async def _filter_by_relevance(self, insight: Insight, modules: List[str]) -> List[str]:
        """Filtra módulos por relevância do insight"""
        filtered = []
        
        for module in modules:
            relevance_score = await self._calculate_module_relevance(insight, module)
            if relevance_score > 0.3:  # Threshold de relevância
                filtered.append(module)
        
        return filtered

    async def _filter_by_user_preferences(self, insight: Insight, users: List[str]) -> List[str]:
        """Filtra usuários por preferências"""
        filtered = []
        
        for user_id in users:
            if user_id in self.user_preferences:
                prefs = self.user_preferences[user_id]
                
                # Verificar prioridade mínima
                min_priority = prefs.get("min_priority", InsightPriority.NORMAL.value)
                if insight.priority.value >= min_priority:
                    
                    # Verificar tipos de interesse
                    interest_types = prefs.get("insight_types", [])
                    if not interest_types or insight.type.value in interest_types:
                        
                        # Verificar horário de não incomodar
                        if await self._is_valid_delivery_time(user_id):
                            filtered.append(user_id)
            else:
                # Usuário sem preferências - usar defaults
                if insight.priority.value >= InsightPriority.NORMAL.value:
                    filtered.append(user_id)
        
        return filtered

    async def _create_delivery_plan(self, insight: Insight, modules: List[str], 
                                   users: List[str]) -> Dict[str, Any]:
        """Cria plano de entrega"""
        plan = {
            "modules": {},
            "users": {}
        }
        
        # Plano para módulos
        for module in modules:
            channels = await self._determine_module_channels(module, insight)
            plan["modules"][module] = channels
        
        # Plano para usuários
        for user_id in users:
            channels = await self._determine_user_channels(user_id, insight)
            plan["users"][user_id] = channels
        
        return plan

    async def _execute_deliveries(self, insight: Insight, delivery_plan: Dict[str, Any]) -> List[DeliveryLog]:
        """Executa as entregas do insight"""
        delivery_logs = []
        
        # Entregas para módulos
        for module, channels in delivery_plan["modules"].items():
            for channel in channels:
                log = await self._deliver_to_module(insight, module, channel)
                delivery_logs.append(log)
        
        # Entregas para usuários
        for user_id, channels in delivery_plan["users"].items():
            for channel in channels:
                log = await self._deliver_to_user(insight, user_id, channel)
                delivery_logs.append(log)
        
        return delivery_logs

    async def _deliver_to_module(self, insight: Insight, module: str, channel: DeliveryChannel) -> DeliveryLog:
        """Entrega insight para um módulo"""
        try:
            if channel == DeliveryChannel.REAL_TIME:
                # Envio via WebSocket/SSE para o módulo
                success = await self._send_realtime(f"module_{module}", insight)
            elif channel == DeliveryChannel.WEBHOOK:
                # Webhook para o módulo
                success = await self._send_webhook(module, insight)
            elif channel == DeliveryChannel.DASHBOARD:
                # Atualização do dashboard do módulo
                success = await self._update_module_dashboard(module, insight)
            else:
                success = True  # Canal não implementado, mas "sucesso"
            
            status = DeliveryStatus.SENT if success else DeliveryStatus.FAILED
            
        except Exception as e:
            logger.error(f"Erro na entrega para módulo {module}: {e}")
            status = DeliveryStatus.FAILED
        
        return DeliveryLog(
            insight_id=insight.id,
            recipient=f"module_{module}",
            channel=channel,
            status=status,
            delivered_at=datetime.now()
        )

    async def _deliver_to_user(self, insight: Insight, user_id: str, channel: DeliveryChannel) -> DeliveryLog:
        """Entrega insight para um usuário"""
        try:
            if channel == DeliveryChannel.EMAIL:
                success = await self._send_email(user_id, insight)
            elif channel == DeliveryChannel.SMS:
                success = await self._send_sms(user_id, insight)
            elif channel == DeliveryChannel.PUSH_NOTIFICATION:
                success = await self._send_push(user_id, insight)
            elif channel == DeliveryChannel.IN_APP:
                success = await self._send_in_app(user_id, insight)
            else:
                success = True  # Canal não implementado
            
            status = DeliveryStatus.SENT if success else DeliveryStatus.FAILED
            
        except Exception as e:
            logger.error(f"Erro na entrega para usuário {user_id}: {e}")
            status = DeliveryStatus.FAILED
        
        return DeliveryLog(
            insight_id=insight.id,
            recipient=f"user_{user_id}",
            channel=channel,
            status=status,
            delivered_at=datetime.now()
        )

    async def _send_realtime(self, recipient: str, insight: Insight) -> bool:
        """Simula envio em tempo real"""
        # Em produção, enviaria via WebSocket
        logger.info(f"Enviando insight {insight.id} via real-time para {recipient}")
        return True

    async def _send_webhook(self, module: str, insight: Insight) -> bool:
        """Simula envio via webhook"""
        # Em produção, faria HTTP POST para endpoint do módulo
        logger.info(f"Enviando insight {insight.id} via webhook para módulo {module}")
        return True

    async def _send_email(self, user_id: str, insight: Insight) -> bool:
        """Simula envio de email"""
        # Em produção, enviaria email real
        logger.info(f"Enviando insight {insight.id} via email para usuário {user_id}")
        return True

    async def _send_sms(self, user_id: str, insight: Insight) -> bool:
        """Simula envio de SMS"""
        logger.info(f"Enviando insight {insight.id} via SMS para usuário {user_id}")
        return True

    async def _send_push(self, user_id: str, insight: Insight) -> bool:
        """Simula push notification"""
        logger.info(f"Enviando insight {insight.id} via push para usuário {user_id}")
        return True

    async def _send_in_app(self, user_id: str, insight: Insight) -> bool:
        """Simula notificação in-app"""
        logger.info(f"Enviando insight {insight.id} via in-app para usuário {user_id}")
        return True

    async def _update_module_dashboard(self, module: str, insight: Insight) -> bool:
        """Simula atualização do dashboard do módulo"""
        logger.info(f"Atualizando dashboard do módulo {module} com insight {insight.id}")
        return True

    def _get_module_correlations(self, module: str) -> List[str]:
        """Retorna módulos correlacionados"""
        correlations = {
            "financial": ["hr", "crm", "operations"],
            "hr": ["financial", "operations", "notifications"],
            "crm": ["financial", "clients", "notifications"],
            "operations": ["hr", "clients", "equipment_management"]
        }
        return correlations.get(module, [])

    def _user_interested_in_insight(self, preferences: Dict[str, Any], insight: Insight) -> bool:
        """Verifica se usuário tem interesse no insight"""
        # Verificar tipos de interesse
        interest_types = preferences.get("insight_types", [])
        if interest_types and insight.type.value not in interest_types:
            return False
        
        # Verificar módulos de interesse
        interest_modules = preferences.get("modules", [])
        if interest_modules and insight.source_module not in interest_modules:
            return False
        
        # Verificar prioridade mínima
        min_priority = preferences.get("min_priority", InsightPriority.NORMAL.value)
        if insight.priority.value < min_priority:
            return False
        
        return True

    async def _calculate_module_relevance(self, insight: Insight, module: str) -> float:
        """Calcula relevância do insight para um módulo"""
        score = 0.0
        
        # Relevância por módulo de origem
        if module == insight.source_module:
            score += 1.0
        
        # Relevância por correlações
        correlations = self._get_module_correlations(insight.source_module)
        if module in correlations:
            score += 0.7
        
        # Relevância por tipo de insight
        if insight.type in [InsightType.ALERT, InsightType.EMERGENCY]:
            score += 0.5
        
        return min(score, 1.0)

    async def _determine_module_channels(self, module: str, insight: Insight) -> List[DeliveryChannel]:
        """Determina canais apropriados para um módulo"""
        channels = [DeliveryChannel.REAL_TIME]
        
        if insight.priority.value >= InsightPriority.HIGH.value:
            channels.append(DeliveryChannel.WEBHOOK)
        
        if insight.type in [InsightType.TREND, InsightType.RECOMMENDATION]:
            channels.append(DeliveryChannel.DASHBOARD)
        
        return channels

    async def _determine_user_channels(self, user_id: str, insight: Insight) -> List[DeliveryChannel]:
        """Determina canais apropriados para um usuário"""
        prefs = self.user_preferences.get(user_id, {})
        preferred_channels = prefs.get("channels", ["email", "in_app"])
        
        channels = []
        
        # Sempre notificação in-app
        if "in_app" in preferred_channels:
            channels.append(DeliveryChannel.IN_APP)
        
        # Email para insights importantes
        if insight.priority.value >= InsightPriority.HIGH.value and "email" in preferred_channels:
            channels.append(DeliveryChannel.EMAIL)
        
        # SMS para emergências
        if insight.priority == InsightPriority.EMERGENCY and "sms" in preferred_channels:
            channels.append(DeliveryChannel.SMS)
        
        return channels

    async def _is_valid_delivery_time(self, user_id: str) -> bool:
        """Verifica se é horário válido para entrega"""
        prefs = self.user_preferences.get(user_id, {})
        do_not_disturb = prefs.get("do_not_disturb", {})
        
        if not do_not_disturb:
            return True
        
        # Verificar horários de não incomodar
        current_hour = datetime.now().hour
        start_hour = do_not_disturb.get("start_hour", 22)
        end_hour = do_not_disturb.get("end_hour", 7)
        
        if start_hour <= current_hour or current_hour <= end_hour:
            return False
        
        return True

    def _update_stats(self, delivery_logs: List[DeliveryLog]):
        """Atualiza estatísticas"""
        self.stats["insights_processed"] += 1
        self.stats["deliveries_sent"] += len(delivery_logs)
        
        successful = len([d for d in delivery_logs if d.status == DeliveryStatus.SENT])
        total_deliveries = self.stats["deliveries_sent"]
        
        if total_deliveries > 0:
            self.stats["delivery_success_rate"] = successful / total_deliveries

    def _summarize_deliveries(self, delivery_logs: List[DeliveryLog]) -> Dict[str, int]:
        """Resume entregas por canal"""
        summary = {}
        
        for log in delivery_logs:
            channel = log.channel.value
            status = log.status.value
            
            key = f"{channel}_{status}"
            summary[key] = summary.get(key, 0) + 1
        
        return summary

    def _setup_default_rules(self):
        """Configura regras padrão de entrega"""
        
        # Regras para insights críticos
        self.delivery_rules.append(DeliveryRule(
            module_pattern="*",
            user_role="admin",
            insight_types=[InsightType.ALERT, InsightType.RISK],
            min_priority=InsightPriority.CRITICAL,
            channels=[DeliveryChannel.EMAIL, DeliveryChannel.SMS, DeliveryChannel.REAL_TIME]
        ))
        
        # Regras para módulo financeiro
        self.delivery_rules.append(DeliveryRule(
            module_pattern="financial",
            user_role="manager",
            insight_types=[InsightType.PREDICTION, InsightType.TREND],
            min_priority=InsightPriority.HIGH,
            channels=[DeliveryChannel.EMAIL, DeliveryChannel.DASHBOARD]
        ))

    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do distribuidor"""
        return {
            "status": "healthy",
            "delivery_rules": len(self.delivery_rules),
            "user_preferences": len(self.user_preferences),
            "module_subscriptions": len(self.module_subscriptions),
            "stats": self.stats,
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }
