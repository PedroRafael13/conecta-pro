"""
Report Exporter - Exportação de relatórios.

Exporta relatórios para diferentes formatos (PDF, Excel, CSV, etc.).
"""

import io
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from modules.ai.report_generator.models import Report
from modules.ai.report_generator.models.report import ReportFormatEnum
from modules.ai.report_generator.repositories import ReportRepository

logger = logging.getLogger(__name__)


class ReportExporter:
    """Serviço de exportação de relatórios."""

    def __init__(self, db: Session):
        """Inicializa exportador."""
        self.db = db
        self.repository = ReportRepository(db)

    def export_report(
        self,
        report_id: UUID,
        format_type: ReportFormatEnum,
        include_charts: bool = True,
        include_data: bool = True,
        page_size: str = "A4",
        orientation: str = "portrait",
        password: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Exporta relatório para o formato especificado.

        Returns:
            Dict com path, url, size e metadata do arquivo gerado.
        """
        report = self.repository.get_report(report_id)
        if not report:
            raise ValueError("Relatório não encontrado")

        # Seleciona exportador
        if format_type == ReportFormatEnum.PDF:
            result = self._export_pdf(report, page_size, orientation, include_charts, password)
        elif format_type == ReportFormatEnum.EXCEL:
            result = self._export_excel(report, include_data)
        elif format_type == ReportFormatEnum.CSV:
            result = self._export_csv(report)
        elif format_type == ReportFormatEnum.JSON:
            result = self._export_json(report)
        elif format_type == ReportFormatEnum.HTML:
            result = self._export_html(report, include_charts)
        else:
            raise ValueError(f"Formato não suportado: {format_type}")

        # Registra exportação
        report.mark_as_downloaded(format_type.value)
        self.repository.update_report(report)

        return result

    def _export_pdf(
        self,
        report: Report,
        page_size: str,
        orientation: str,
        include_charts: bool,
        password: Optional[str],
    ) -> Dict[str, Any]:
        """Exporta para PDF."""
        # Simulação - em produção usaria biblioteca como ReportLab ou WeasyPrint
        content = self._generate_pdf_content(report, include_charts)

        filename = f"{report.code}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = f"/tmp/reports/{filename}"

        # Simulação de tamanho
        file_size = len(json.dumps(report.data or {})) * 2

        return {
            "format": "pdf",
            "filename": filename,
            "file_path": file_path,
            "file_size_bytes": file_size,
            "page_size": page_size,
            "orientation": orientation,
            "pages": self._estimate_pages(report),
            "generated_at": datetime.utcnow().isoformat(),
        }

    def _export_excel(self, report: Report, include_data: bool) -> Dict[str, Any]:
        """Exporta para Excel."""
        # Simulação - em produção usaria openpyxl ou xlsxwriter
        filename = f"{report.code}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = f"/tmp/reports/{filename}"

        # Prepara dados para Excel
        sheets = []

        # Sheet de resumo
        sheets.append({
            "name": "Resumo",
            "data": [
                ["Relatório", report.name],
                ["Código", report.code],
                ["Período", report.period_description],
                ["Gerado em", report.generated_at.strftime("%d/%m/%Y %H:%M") if report.generated_at else ""],
            ]
        })

        # Sheet de métricas
        if report.metrics:
            metrics_data = [["Métrica", "Valor"]]
            for key, value in report.metrics.items():
                metrics_data.append([key, str(value)])
            sheets.append({"name": "Métricas", "data": metrics_data})

        # Sheet de insights
        if report.insights:
            insights_data = [["Tipo", "Categoria", "Título", "Descrição"]]
            for insight in report.insights:
                insights_data.append([
                    insight.get("type", ""),
                    insight.get("category", ""),
                    insight.get("title", ""),
                    insight.get("description", ""),
                ])
            sheets.append({"name": "Insights", "data": insights_data})

        # Sheet de dados brutos
        if include_data and report.data:
            for source, data in report.data.items():
                if isinstance(data, dict) and "records" in data:
                    sheets.append({"name": f"Dados_{source}", "data": data["records"]})

        file_size = len(json.dumps(sheets)) * 3

        return {
            "format": "excel",
            "filename": filename,
            "file_path": file_path,
            "file_size_bytes": file_size,
            "sheets": len(sheets),
            "generated_at": datetime.utcnow().isoformat(),
        }

    def _export_csv(self, report: Report) -> Dict[str, Any]:
        """Exporta para CSV."""
        filename = f"{report.code}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = f"/tmp/reports/{filename}"

        # Gera CSV das métricas
        lines = ["Métrica,Valor"]
        if report.metrics:
            for key, value in report.metrics.items():
                lines.append(f"{key},{value}")

        content = "\n".join(lines)
        file_size = len(content.encode("utf-8"))

        return {
            "format": "csv",
            "filename": filename,
            "file_path": file_path,
            "file_size_bytes": file_size,
            "rows": len(lines),
            "generated_at": datetime.utcnow().isoformat(),
        }

    def _export_json(self, report: Report) -> Dict[str, Any]:
        """Exporta para JSON."""
        filename = f"{report.code}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        file_path = f"/tmp/reports/{filename}"

        export_data = {
            "report": {
                "id": str(report.id),
                "code": report.code,
                "name": report.name,
                "type": report.report_type.value,
                "period": {
                    "start": report.period_start.isoformat() if report.period_start else None,
                    "end": report.period_end.isoformat() if report.period_end else None,
                },
                "generated_at": report.generated_at.isoformat() if report.generated_at else None,
            },
            "summary": report.summary,
            "metrics": report.metrics,
            "insights": report.insights,
            "recommendations": report.recommendations,
            "anomalies": report.anomalies,
            "data": report.data,
        }

        content = json.dumps(export_data, indent=2, default=str)
        file_size = len(content.encode("utf-8"))

        return {
            "format": "json",
            "filename": filename,
            "file_path": file_path,
            "file_size_bytes": file_size,
            "generated_at": datetime.utcnow().isoformat(),
        }

    def _export_html(self, report: Report, include_charts: bool) -> Dict[str, Any]:
        """Exporta para HTML."""
        filename = f"{report.code}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
        file_path = f"/tmp/reports/{filename}"

        html_content = self._generate_html_content(report, include_charts)
        file_size = len(html_content.encode("utf-8"))

        return {
            "format": "html",
            "filename": filename,
            "file_path": file_path,
            "file_size_bytes": file_size,
            "generated_at": datetime.utcnow().isoformat(),
        }

    def _generate_pdf_content(self, report: Report, include_charts: bool) -> bytes:
        """Gera conteúdo do PDF."""
        # Simulação - retorna bytes vazios
        # Em produção, usaria ReportLab ou WeasyPrint
        return b""

    def _generate_html_content(self, report: Report, include_charts: bool) -> str:
        """Gera conteúdo HTML."""
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>{report.name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        .metric {{ display: inline-block; margin: 10px; padding: 20px; background: #f5f5f5; border-radius: 8px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #2196F3; }}
        .metric-label {{ font-size: 14px; color: #666; }}
        .insight {{ padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; background: #f9f9f9; }}
        .insight.warning {{ border-color: #FF9800; }}
        .insight.negative {{ border-color: #f44336; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>{report.name}</h1>
    <p><strong>Código:</strong> {report.code}</p>
    <p><strong>Período:</strong> {report.period_description}</p>
    <p><strong>Gerado em:</strong> {report.generated_at.strftime('%d/%m/%Y %H:%M') if report.generated_at else 'N/A'}</p>

    <h2>Métricas</h2>
    <div class="metrics">
"""
        # Métricas
        if report.metrics:
            for key, value in report.metrics.items():
                formatted_value = self._format_metric_value(key, value)
                label = key.replace("_", " ").title()
                html += f"""
        <div class="metric">
            <div class="metric-value">{formatted_value}</div>
            <div class="metric-label">{label}</div>
        </div>
"""

        html += """
    </div>

    <h2>Insights</h2>
"""
        # Insights
        if report.insights:
            for insight in report.insights:
                insight_type = insight.get("type", "positive")
                css_class = "warning" if insight_type == "warning" else ("negative" if insight_type == "negative" else "")
                html += f"""
    <div class="insight {css_class}">
        <strong>{insight.get('title', '')}</strong><br>
        {insight.get('description', '')}
    </div>
"""

        html += """
</body>
</html>
"""
        return html

    def _format_metric_value(self, key: str, value: Any) -> str:
        """Formata valor de métrica para exibição."""
        if value is None:
            return "N/A"

        # Detecta tipo pelo nome da chave
        key_lower = key.lower()

        if any(k in key_lower for k in ["revenue", "value", "profit", "expense", "ticket"]):
            try:
                return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except (ValueError, TypeError):
                return str(value)

        if any(k in key_lower for k in ["rate", "margin", "growth", "percent"]):
            try:
                return f"{float(value):.1f}%"
            except (ValueError, TypeError):
                return str(value)

        if isinstance(value, float):
            return f"{value:,.2f}"

        if isinstance(value, int):
            return f"{value:,}".replace(",", ".")

        return str(value)

    def _estimate_pages(self, report: Report) -> int:
        """Estima número de páginas do PDF."""
        base_pages = 1  # Capa

        # Métricas
        if report.metrics:
            base_pages += 1

        # Insights
        if report.insights:
            base_pages += max(1, len(report.insights) // 5)

        # Recomendações
        if report.recommendations:
            base_pages += max(1, len(report.recommendations) // 4)

        # Seções de dados
        if report.data:
            base_pages += len(report.data)

        return base_pages

    def get_supported_formats(self) -> List[Dict[str, Any]]:
        """Retorna formatos de exportação suportados."""
        return [
            {
                "format": "pdf",
                "name": "PDF",
                "description": "Documento PDF com gráficos e formatação",
                "supports_charts": True,
                "supports_password": True,
            },
            {
                "format": "excel",
                "name": "Excel",
                "description": "Planilha Excel com múltiplas abas",
                "supports_charts": False,
                "supports_password": False,
            },
            {
                "format": "csv",
                "name": "CSV",
                "description": "Arquivo CSV para análise de dados",
                "supports_charts": False,
                "supports_password": False,
            },
            {
                "format": "json",
                "name": "JSON",
                "description": "Dados estruturados em JSON",
                "supports_charts": False,
                "supports_password": False,
            },
            {
                "format": "html",
                "name": "HTML",
                "description": "Página HTML responsiva",
                "supports_charts": True,
                "supports_password": False,
            },
        ]
