"""
Central de IA Unificada - Conecta PRO
Hub central de inteligência artificial que serve todos os módulos do sistema.

Arquitetura:
- Unified AI Engine: Motor central de IA
- Cross Module Analytics: Analytics integrados entre módulos  
- Predictive Orchestra: Orquestrador de predições
- Insight Distributor: Distribuidor de insights para módulos
- Module Integration Manager: Gerenciador de integrações

Autor: Conecta PRO Development Team
Data: 2024-01-11
"""

from .unified_ai_engine import UnifiedAIEngine
from .cross_module_analytics import CrossModuleAnalytics
from .predictive_orchestra import PredictiveOrchestra
from .insight_distributor import InsightDistributor
from .module_integration_manager import ModuleIntegrationManager

__all__ = [
    "UnifiedAIEngine",
    "CrossModuleAnalytics",
    "PredictiveOrchestra",
    "InsightDistributor",
    "ModuleIntegrationManager"
]

# Versão da Central de IA
__version__ = "1.0.0"
