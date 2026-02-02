"""
Trend Analyzer for OpenClaw - Análise de tendências com IA.

Analisa histórico de relatórios para identificar padrões,
degradação de qualidade e fornecer insights com LLM.

Author: Conecta PRO Team
Date: 2026-02-02
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """Analisador de tendências usando histórico de relatórios."""

    def __init__(self, reports_dir: Path):
        """
        Initialize trend analyzer.

        Args:
            reports_dir: Diretório com relatórios JSON do OpenClaw
        """
        self.reports_dir = Path(reports_dir)

    def load_reports(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Carrega relatórios dos últimos N dias.

        Args:
            days: Número de dias para carregar

        Returns:
            Lista de relatórios ordenados por data (mais recente primeiro)
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        reports = []

        if not self.reports_dir.exists():
            logger.warning(f"Diretório de relatórios não existe: {self.reports_dir}")
            return reports

        for report_file in self.reports_dir.glob("cycle_*.json"):
            try:
                with open(report_file, "r", encoding="utf-8") as f:
                    report = json.load(f)

                # Parse timestamp
                started_at_str = report.get("started_at", "")
                if started_at_str:
                    # Remove timezone info if present for parsing
                    started_at_str = started_at_str.replace("+00:00", "").replace("Z", "")
                    try:
                        started_at = datetime.fromisoformat(started_at_str).replace(tzinfo=timezone.utc)
                    except ValueError:
                        # Fallback: tentar extrair do nome do arquivo
                        cycle_id = report.get("cycle_id", "")
                        if cycle_id:
                            # Format: YYYYMMDD_HHMMSS
                            started_at = datetime.strptime(cycle_id, "%Y%m%d_%H%M%S").replace(
                                tzinfo=timezone.utc
                            )
                        else:
                            continue

                    if started_at >= cutoff_date:
                        reports.append(report)

            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Erro ao carregar relatório {report_file}: {e}")
                continue

        # Ordenar por data (mais recente primeiro)
        reports.sort(key=lambda r: r.get("started_at", ""), reverse=True)
        return reports

    def calculate_health_trend(self, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcula tendência do health score ao longo do tempo.

        Args:
            reports: Lista de relatórios

        Returns:
            Dict com análise de tendência
        """
        if not reports:
            return {"trend": "unknown", "message": "Nenhum relatório disponível"}

        health_scores = [r.get("health_score", 0) for r in reports]

        # Calcular métricas
        current_score = health_scores[0] if health_scores else 0
        avg_score = sum(health_scores) / len(health_scores) if health_scores else 0
        min_score = min(health_scores) if health_scores else 0
        max_score = max(health_scores) if health_scores else 0

        # Determinar tendência (comparar última semana com semana anterior)
        mid_point = len(health_scores) // 2
        if mid_point > 0:
            recent_avg = sum(health_scores[:mid_point]) / mid_point
            older_avg = sum(health_scores[mid_point:]) / (len(health_scores) - mid_point)

            if recent_avg > older_avg + 5:
                trend = "improving"
                trend_emoji = "📈"
            elif recent_avg < older_avg - 5:
                trend = "declining"
                trend_emoji = "📉"
            else:
                trend = "stable"
                trend_emoji = "➡️"
        else:
            trend = "insufficient_data"
            trend_emoji = "❓"

        return {
            "trend": trend,
            "trend_emoji": trend_emoji,
            "current_score": current_score,
            "average_score": round(avg_score, 1),
            "min_score": min_score,
            "max_score": max_score,
            "total_reports": len(reports),
            "message": self._generate_trend_message(trend, current_score, avg_score),
        }

    def _generate_trend_message(self, trend: str, current: float, average: float) -> str:
        """Gera mensagem descritiva sobre a tendência."""
        messages = {
            "improving": f"Health score melhorando! Atual: {current}/100 vs Média: {average:.1f}/100",
            "declining": f"⚠️ Health score em declínio. Atual: {current}/100 vs Média: {average:.1f}/100",
            "stable": f"Health score estável em torno de {average:.1f}/100",
            "insufficient_data": "Dados insuficientes para determinar tendência",
        }
        return messages.get(trend, "Tendência desconhecida")

    def identify_recurring_failures(self, reports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identifica checks que falham frequentemente.

        Args:
            reports: Lista de relatórios

        Returns:
            Lista de checks problemáticos com estatísticas
        """
        check_stats = {}

        for report in reports:
            for check in report.get("checks", []):
                check_name = check.get("name", "Unknown")

                if check_name not in check_stats:
                    check_stats[check_name] = {
                        "name": check_name,
                        "total_runs": 0,
                        "failures": 0,
                        "errors": 0,
                        "warnings": 0,
                        "passes": 0,
                    }

                check_stats[check_name]["total_runs"] += 1
                status = check.get("status", "unknown")

                if status == "fail":
                    check_stats[check_name]["failures"] += 1
                elif status == "error":
                    check_stats[check_name]["errors"] += 1
                elif status == "warn":
                    check_stats[check_name]["warnings"] += 1
                elif status == "pass":
                    check_stats[check_name]["passes"] += 1

        # Calcular failure rate e ordenar
        recurring_issues = []
        for check_name, stats in check_stats.items():
            total = stats["total_runs"]
            if total > 0:
                failure_rate = (stats["failures"] + stats["errors"]) / total * 100
                stats["failure_rate"] = round(failure_rate, 1)

                # Considerar problemático se failure rate > 20%
                if failure_rate > 20:
                    recurring_issues.append(stats)

        # Ordenar por failure rate (maior primeiro)
        recurring_issues.sort(key=lambda x: x["failure_rate"], reverse=True)
        return recurring_issues

    def analyze_performance_degradation(self, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa degradação de performance (duração dos checks).

        Args:
            reports: Lista de relatórios

        Returns:
            Análise de performance
        """
        if len(reports) < 2:
            return {"degradation": False, "message": "Dados insuficientes"}

        durations = [r.get("duration_seconds", 0) for r in reports]

        # Comparar últimos 3 vs 3 anteriores
        sample_size = min(3, len(durations) // 2)
        if sample_size == 0:
            return {"degradation": False, "message": "Dados insuficientes"}

        recent_avg = sum(durations[:sample_size]) / sample_size
        older_avg = sum(durations[sample_size : sample_size * 2]) / sample_size

        degradation_pct = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0

        return {
            "degradation": degradation_pct > 20,
            "degradation_percentage": round(degradation_pct, 1),
            "recent_avg_duration": round(recent_avg, 1),
            "older_avg_duration": round(older_avg, 1),
            "message": (
                f"⚠️ Performance degradou {degradation_pct:.1f}%: {recent_avg:.1f}s vs {older_avg:.1f}s"
                if degradation_pct > 20
                else f"Performance estável: {recent_avg:.1f}s"
            ),
        }

    def generate_insights(self, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Gera insights completos baseados no histórico.

        Args:
            reports: Lista de relatórios

        Returns:
            Dict com análises e recomendações
        """
        health_trend = self.calculate_health_trend(reports)
        recurring_failures = self.identify_recurring_failures(reports)
        performance = self.analyze_performance_degradation(reports)

        # Gerar recomendações
        recommendations = []

        if health_trend["trend"] == "declining":
            recommendations.append(
                "⚠️ URGENTE: Health score em declínio. Revisar checks falhando e corrigir issues."
            )

        if recurring_failures:
            top_issue = recurring_failures[0]
            recommendations.append(
                f"🔴 Check '{top_issue['name']}' falha {top_issue['failure_rate']}% do tempo. "
                "Investigar causa raiz."
            )

        if performance["degradation"]:
            recommendations.append(
                f"🐌 Performance degradou {performance['degradation_percentage']}%. "
                "Considerar otimizações ou aumentar timeouts."
            )

        if not recommendations:
            recommendations.append("✅ Sistema saudável. Continuar monitorando.")

        return {
            "analysis_period_days": 30,
            "total_reports_analyzed": len(reports),
            "health_trend": health_trend,
            "recurring_failures": recurring_failures[:5],  # Top 5
            "performance_analysis": performance,
            "recommendations": recommendations,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def generate_ai_summary(
        self, insights: Dict[str, Any], llm_provider: Optional[Any] = None
    ) -> str:
        """
        Gera sumário em linguagem natural usando LLM (opcional).

        Args:
            insights: Insights gerados por generate_insights()
            llm_provider: Provider LLM (ex: OpenAI, Anthropic) - opcional

        Returns:
            Sumário em texto natural
        """
        # Se LLM provider disponível, usar para gerar sumário mais sofisticado
        if llm_provider:
            try:
                prompt = f"""Analise os seguintes insights de qualidade de software e gere um sumário executivo em português:

{json.dumps(insights, indent=2, ensure_ascii=False)}

Gere um relatório conciso (3-5 parágrafos) destacando:
1. Status geral da qualidade
2. Principais problemas identificados
3. Recomendações prioritárias
"""
                # Aqui você chamaria o LLM provider
                # summary = llm_provider.generate(prompt)
                # return summary

                # Fallback se LLM falhar
                pass
            except Exception as e:
                logger.warning(f"Erro ao gerar sumário com LLM: {e}")

        # Fallback: sumário baseado em template
        health = insights["health_trend"]
        recurring = insights["recurring_failures"]
        perf = insights["performance_analysis"]

        summary_parts = [
            f"📊 **Análise de {insights['total_reports_analyzed']} ciclos** ({insights['analysis_period_days']} dias)",
            "",
            f"**Health Score**: {health['trend_emoji']} {health['message']}",
            f"- Atual: {health['current_score']}/100",
            f"- Média: {health['average_score']}/100",
            f"- Range: {health['min_score']}-{health['max_score']}/100",
            "",
        ]

        if recurring:
            summary_parts.append("**Checks Problemáticos**:")
            for issue in recurring[:3]:
                summary_parts.append(
                    f"- {issue['name']}: {issue['failure_rate']}% falhas "
                    f"({issue['failures']+issue['errors']}/{issue['total_runs']} runs)"
                )
            summary_parts.append("")

        summary_parts.append(f"**Performance**: {perf['message']}")
        summary_parts.append("")

        if insights["recommendations"]:
            summary_parts.append("**Recomendações**:")
            for rec in insights["recommendations"]:
                summary_parts.append(f"- {rec}")

        return "\n".join(summary_parts)
