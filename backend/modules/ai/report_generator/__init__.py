"""
AI Report Generator Module - Sprint 47

Módulo de geração automática de relatórios com IA.
Gera relatórios com insights, gráficos, análises e exportação multi-formato.

Funcionalidades:
- Templates de relatórios personalizáveis
- Geração automática com IA
- Scheduling (diário, semanal, mensal)
- Exportação PDF, Excel, CSV, JSON
- Insights e recomendações automáticas
- Gráficos e visualizações
- Distribuição por email
"""

from modules.ai.report_generator.models import (
    Report,
    AIReportTemplate,
    AIReportSchedule,
    ReportExecution,
    ReportSection,
    ReportWidget,
)
from modules.ai.report_generator.schemas import (
    ReportCreate,
    ReportUpdate,
    ReportResponse,
    ReportTemplateCreate,
    ReportTemplateResponse,
    ReportScheduleCreate,
    ReportScheduleResponse,
    ReportExecutionResponse,
)
from modules.ai.report_generator.services import (
    ReportGeneratorService,
    TemplateEngine,
    ReportScheduler,
    ReportExporter,
    InsightExtractor,
)
from modules.ai.report_generator.controllers import report_router

__all__ = [
    # Models
    "Report",
    "AIReportTemplate",
    "AIReportSchedule",
    "ReportExecution",
    "ReportSection",
    "ReportWidget",
    # Schemas
    "ReportCreate",
    "ReportUpdate",
    "ReportResponse",
    "ReportTemplateCreate",
    "ReportTemplateResponse",
    "ReportScheduleCreate",
    "ReportScheduleResponse",
    "ReportExecutionResponse",
    # Services
    "ReportGeneratorService",
    "TemplateEngine",
    "ReportScheduler",
    "ReportExporter",
    "InsightExtractor",
    # Router
    "report_router",
]
