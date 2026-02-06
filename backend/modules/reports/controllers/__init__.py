"""
Controllers do módulo de Relatórios Gerenciais
Sprint 34: Relatórios Gerenciais + FASE 3 ONDA 1
"""

from .report_controller import router
from .intelligent_reports_controller import router as intelligent_reports_router

__all__ = ["router", "intelligent_reports_router"]
