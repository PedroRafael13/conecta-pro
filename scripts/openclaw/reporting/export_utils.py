"""
Export Utilities for OpenClaw - Exporta relatórios para CSV/Excel.

Converte relatórios JSON para formatos compatíveis com
planilhas e ferramentas de análise.

Author: Conecta PRO Team
Date: 2026-02-02
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class ExportUtils:
    """Utilitários de exportação de relatórios."""

    @staticmethod
    def export_to_csv(report: Dict[str, Any], output_file: Path) -> Path:
        """
        Exporta relatório para CSV.

        Args:
            report: Relatório OpenClaw (dict)
            output_file: Path do arquivo CSV de saída

        Returns:
            Path do arquivo gerado
        """
        checks = report.get("checks", [])

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["check_name", "status", "duration_seconds", "message", "timestamp"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            for check in checks:
                writer.writerow(
                    {
                        "check_name": check.get("name", ""),
                        "status": check.get("status", ""),
                        "duration_seconds": check.get("duration_seconds", 0),
                        "message": check.get("message", ""),
                        "timestamp": check.get("timestamp", ""),
                    }
                )

        return output_file

    @staticmethod
    def export_summary_to_csv(reports: List[Dict[str, Any]], output_file: Path) -> Path:
        """
        Exporta sumário de múltiplos relatórios para CSV.

        Args:
            reports: Lista de relatórios OpenClaw
            output_file: Path do arquivo CSV de saída

        Returns:
            Path do arquivo gerado
        """
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "cycle_id",
                "timestamp",
                "overall_status",
                "health_score",
                "duration_seconds",
                "total_checks",
                "pass_count",
                "fail_count",
                "warn_count",
                "error_count",
                "skip_count",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()

            for report in reports:
                summary = report.get("summary", {})
                status_counts = summary.get("status_counts", {})

                writer.writerow(
                    {
                        "cycle_id": report.get("cycle_id", ""),
                        "timestamp": report.get("started_at", ""),
                        "overall_status": report.get("overall_status", ""),
                        "health_score": report.get("health_score", 0),
                        "duration_seconds": report.get("duration_seconds", 0),
                        "total_checks": summary.get("total_checks", 0),
                        "pass_count": status_counts.get("pass", 0),
                        "fail_count": status_counts.get("fail", 0),
                        "warn_count": status_counts.get("warn", 0),
                        "error_count": status_counts.get("error", 0),
                        "skip_count": status_counts.get("skip", 0),
                    }
                )

        return output_file

    @staticmethod
    def export_to_markdown(report: Dict[str, Any], output_file: Path) -> Path:
        """
        Exporta relatório para Markdown.

        Args:
            report: Relatório OpenClaw (dict)
            output_file: Path do arquivo MD de saída

        Returns:
            Path do arquivo gerado
        """
        cycle_id = report.get("cycle_id", "Unknown")
        overall_status = report.get("overall_status", "unknown")
        health_score = report.get("health_score", 0)
        duration = report.get("duration_seconds", 0)
        checks = report.get("checks", [])
        summary = report.get("summary", {})
        status_counts = summary.get("status_counts", {})

        # Emojis por status
        status_emoji = {
            "pass": "✅",
            "fail": "❌",
            "warn": "⚠️",
            "error": "🔴",
            "skip": "⏭️",
        }

        md_content = f"""# OpenClaw Quality Report

**Ciclo:** `{cycle_id}`
**Data:** {report.get('started_at', 'N/A')}
**Status:** {status_emoji.get(overall_status, '❓')} **{overall_status.upper()}**

## 📊 Métricas

| Métrica | Valor |
|---------|-------|
| Health Score | **{health_score}/100** |
| Duração | {duration:.1f}s |
| Total Checks | {summary.get('total_checks', 0)} |
| Pass Rate | {(status_counts.get('pass', 0) / max(summary.get('total_checks', 1), 1) * 100):.0f}% |

## 📋 Resumo

- ✅ Pass: {status_counts.get('pass', 0)}
- ❌ Fail: {status_counts.get('fail', 0)}
- ⚠️ Warn: {status_counts.get('warn', 0)}
- 🔴 Error: {status_counts.get('error', 0)}
- ⏭️ Skip: {status_counts.get('skip', 0)}

## 🔍 Detalhes dos Checks

| Check | Status | Duração | Mensagem |
|-------|--------|---------|----------|
"""

        for check in checks:
            check_name = check.get("name", "Unknown")
            check_status = check.get("status", "unknown")
            check_duration = check.get("duration_seconds", 0)
            check_message = check.get("message", "")

            emoji = status_emoji.get(check_status, "❓")
            md_content += f"| {emoji} {check_name} | {check_status.upper()} | {check_duration:.1f}s | {check_message} |\n"

        md_content += f"""
---
*Gerado por OpenClaw v3.0 • {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*
"""

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        return output_file

    @staticmethod
    def load_reports_from_dir(reports_dir: Path, days: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Carrega todos os relatórios de um diretório.

        Args:
            reports_dir: Diretório com relatórios JSON
            days: Filtrar últimos N dias (opcional)

        Returns:
            Lista de relatórios
        """
        from datetime import timedelta, timezone

        reports_dir = Path(reports_dir)
        reports = []

        cutoff = None
        if days:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        for report_file in sorted(reports_dir.glob("cycle_*.json")):
            try:
                with open(report_file, "r", encoding="utf-8") as f:
                    report = json.load(f)

                # Filtrar por data se especificado
                if cutoff:
                    started_at_str = report.get("started_at", "")
                    if started_at_str:
                        started_at_str = started_at_str.replace("+00:00", "").replace("Z", "")
                        started_at = datetime.fromisoformat(started_at_str).replace(tzinfo=timezone.utc)

                        if started_at < cutoff:
                            continue

                reports.append(report)

            except (json.JSONDecodeError, ValueError, OSError):
                continue

        return reports
