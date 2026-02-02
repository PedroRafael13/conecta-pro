"""
OpenClaw Intelligence Module - IA e Auto-healing.

Módulos:
- TrendAnalyzer: Análise de tendências e padrões
- AutoHealer: Correções automáticas de problemas
- HistoricalAnalyzer: Métricas e visualizações históricas

Author: Conecta PRO Team
Date: 2026-02-02
"""

from .auto_healer import AutoHealer
from .trend_analyzer import TrendAnalyzer

__all__ = ["TrendAnalyzer", "AutoHealer"]
