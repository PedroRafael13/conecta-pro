"""
AI Integration para Sistema Anti-Procrastinação
==============================================

Integra a Central de IA com o sistema anti-procrastinação existente,
transformando-o em um sistema verdadeiramente inteligente e preditivo.

Componentes:
- Intelligent Task Predictor: Prevê tarefas antes de se tornarem urgentes
- AI-Enhanced Escalation: Escalação inteligente baseada em contexto
- Cross-Module Task Analytics: Análise de dependências entre tarefas
- Predictive Alerts: Alertas personalizados com IA
- Smart Insights Distributor: Distribuição inteligente de insights

Autor: Conecta PRO Team + Central AI
Data: 2026-01-11
"""

from .ai_anti_procrastination_engine import AIAntiProcrastinationEngine
from .ai_enhanced_escalation import AIEnhancedEscalation
from .cross_module_task_analytics import CrossModuleTaskAnalytics
from .intelligent_task_predictor import IntelligentTaskPredictor
from .predictive_alerts import PredictiveAlerts
from .smart_insights_distributor import SmartInsightsDistributor

__all__ = [
    "IntelligentTaskPredictor",
    "AIEnhancedEscalation",
    "CrossModuleTaskAnalytics",
    "PredictiveAlerts",
    "SmartInsightsDistributor",
    "AIAntiProcrastinationEngine",
]

# Versão da integração AI
__version__ = "1.0.0"
