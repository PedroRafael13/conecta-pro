"""
Sistema Anti-Procrastinação - Conecta PRO
Fase 6.1 - Expansão do Sistema de Notificações

Garantia de zero procrastinação através de:
- Dashboard unificado de pendências
- Checklist diário obrigatório
- Engine de escalation automático
- Relatórios departamentais inteligentes

Autor: Conecta PRO Team + Claude AI
Data: 2026-01-10
"""

from .daily_checklist.checklist_manager import ChecklistManager
from .dashboard.unified_dashboard import UnifiedDashboard
from .department_reports.report_generator import DepartmentReportGenerator
from .escalation.escalation_engine import EscalationEngine
from .integration.module_integrator import ModuleIntegrator

__all__ = ["UnifiedDashboard", "ChecklistManager", "EscalationEngine", "DepartmentReportGenerator", "ModuleIntegrator"]

__version__ = "6.1.0"
__author__ = "Conecta PRO Team"
__description__ = "Sistema Anti-Procrastinação - Zero Pendências, Máxima Produtividade"
