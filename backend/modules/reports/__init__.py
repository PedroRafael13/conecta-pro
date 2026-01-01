"""
Módulo de Relatórios Gerenciais
Sprint 34: Relatórios Gerenciais

Funcionalidades:
- Templates de relatórios configuráveis
- Agendamento de geração automática
- Exportação em múltiplos formatos (PDF, Excel, CSV, etc.)
- KPIs executivos com alertas
- Benchmarks de mercado
- Dashboard executivo
"""

from modules.reports.controllers import router

__all__ = ["router"]
