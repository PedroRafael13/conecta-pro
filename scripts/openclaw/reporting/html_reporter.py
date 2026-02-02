"""
HTML Reporter for OpenClaw - Gera dashboards interativos.

Cria relatórios HTML com gráficos, métricas e visualizações
para análise de qualidade do projeto.

Author: Conecta PRO Team
Date: 2026-02-02
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class HTMLReporter:
    """Gerador de relatórios HTML interativos."""

    def __init__(self, reports_dir: Path, output_dir: Path):
        """
        Initialize HTML reporter.

        Args:
            reports_dir: Diretório com relatórios JSON
            output_dir: Diretório para salvar HTMLs gerados
        """
        self.reports_dir = Path(reports_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_dashboard(self, report: Dict[str, Any]) -> Path:
        """
        Gera dashboard HTML para um relatório.

        Args:
            report: Relatório OpenClaw (dict)

        Returns:
            Path do arquivo HTML gerado
        """
        cycle_id = report.get("cycle_id", "unknown")
        output_file = self.output_dir / f"dashboard_{cycle_id}.html"

        html_content = self._build_html(report)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        return output_file

    def generate_historical_dashboard(self, days: int = 30) -> Path:
        """
        Gera dashboard com histórico dos últimos N dias.

        Args:
            days: Número de dias para incluir

        Returns:
            Path do arquivo HTML gerado
        """
        # Carregar relatórios
        reports = self._load_recent_reports(days)

        if not reports:
            raise ValueError("Nenhum relatório encontrado")

        output_file = self.output_dir / f"historical_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.html"
        html_content = self._build_historical_html(reports)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        return output_file

    def _load_recent_reports(self, days: int) -> List[Dict[str, Any]]:
        """Carrega relatórios recentes."""
        from datetime import timedelta

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        reports = []

        for report_file in sorted(self.reports_dir.glob("cycle_*.json")):
            try:
                with open(report_file, "r", encoding="utf-8") as f:
                    report = json.load(f)

                # Parse timestamp
                started_at_str = report.get("started_at", "")
                if started_at_str:
                    started_at_str = started_at_str.replace("+00:00", "").replace("Z", "")
                    started_at = datetime.fromisoformat(started_at_str).replace(tzinfo=timezone.utc)

                    if started_at >= cutoff:
                        reports.append(report)
            except (json.JSONDecodeError, ValueError, OSError):
                continue

        # Ordenar por data
        reports.sort(key=lambda r: r.get("started_at", ""))
        return reports

    def _build_html(self, report: Dict[str, Any]) -> str:
        """Constrói HTML para um relatório individual."""
        cycle_id = report.get("cycle_id", "Unknown")
        overall_status = report.get("overall_status", "unknown")
        health_score = report.get("health_score", 0)
        duration = report.get("duration_seconds", 0)
        checks = report.get("checks", [])
        summary = report.get("summary", {})
        status_counts = summary.get("status_counts", {})

        # Cores por status
        status_colors = {
            "pass": "#10b981",
            "fail": "#ef4444",
            "warn": "#f59e0b",
            "error": "#dc2626",
            "skip": "#6b7280",
        }

        badge_color = status_colors.get(overall_status, "#6b7280")
        health_color = "#10b981" if health_score >= 70 else "#f59e0b" if health_score >= 50 else "#ef4444"

        # Construir tabela de checks
        checks_rows = ""
        for check in checks:
            check_name = check.get("name", "Unknown")
            check_status = check.get("status", "unknown")
            check_duration = check.get("duration_seconds", 0)
            check_message = check.get("message", "")

            status_badge_color = status_colors.get(check_status, "#6b7280")
            status_emoji = {"pass": "✅", "fail": "❌", "warn": "⚠️", "error": "🔴", "skip": "⏭️"}.get(check_status, "❓")

            checks_rows += f"""
            <tr>
                <td class="px-4 py-3">{status_emoji} {check_name}</td>
                <td class="px-4 py-3">
                    <span class="px-2 py-1 text-xs font-semibold rounded" style="background-color: {status_badge_color}20; color: {status_badge_color};">
                        {check_status.upper()}
                    </span>
                </td>
                <td class="px-4 py-3">{check_duration:.1f}s</td>
                <td class="px-4 py-3 text-sm text-gray-600">{check_message}</td>
            </tr>
            """

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw Dashboard - {cycle_id}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body class="bg-gray-50">
    <div class="container mx-auto px-4 py-8">
        <!-- Header -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900">OpenClaw Quality Monitor</h1>
                    <p class="text-gray-600 mt-1">Ciclo: {cycle_id}</p>
                </div>
                <div class="text-right">
                    <div class="inline-flex items-center px-4 py-2 rounded-lg text-white font-semibold" style="background-color: {badge_color};">
                        {overall_status.upper()}
                    </div>
                </div>
            </div>
        </div>

        <!-- Métricas -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <!-- Health Score -->
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-sm font-medium text-gray-600 mb-2">Health Score</h3>
                <div class="text-4xl font-bold" style="color: {health_color};">{health_score}/100</div>
                <div class="mt-2 w-full bg-gray-200 rounded-full h-2">
                    <div class="h-2 rounded-full transition-all" style="width: {health_score}%; background-color: {health_color};"></div>
                </div>
            </div>

            <!-- Duração -->
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-sm font-medium text-gray-600 mb-2">Duração</h3>
                <div class="text-4xl font-bold text-gray-900">{duration:.1f}s</div>
                <p class="text-sm text-gray-500 mt-2">Tempo total de execução</p>
            </div>

            <!-- Total Checks -->
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-sm font-medium text-gray-600 mb-2">Total Checks</h3>
                <div class="text-4xl font-bold text-gray-900">{summary.get('total_checks', 0)}</div>
                <p class="text-sm text-gray-500 mt-2">Verificações executadas</p>
            </div>

            <!-- Pass Rate -->
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-sm font-medium text-gray-600 mb-2">Pass Rate</h3>
                <div class="text-4xl font-bold text-green-600">
                    {(status_counts.get('pass', 0) / max(summary.get('total_checks', 1), 1) * 100):.0f}%
                </div>
                <p class="text-sm text-gray-500 mt-2">{status_counts.get('pass', 0)} de {summary.get('total_checks', 0)} passaram</p>
            </div>
        </div>

        <!-- Gráfico de Status -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h2 class="text-xl font-bold text-gray-900 mb-4">Distribuição de Status</h2>
            <canvas id="statusChart" style="max-height: 300px;"></canvas>
        </div>

        <!-- Tabela de Checks -->
        <div class="bg-white rounded-lg shadow overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-200">
                <h2 class="text-xl font-bold text-gray-900">Detalhes dos Checks</h2>
            </div>
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Check</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duração</th>
                            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mensagem</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        {checks_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Footer -->
        <div class="mt-8 text-center text-gray-500 text-sm">
            <p>Gerado por OpenClaw v3.0 • {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
        </div>
    </div>

    <script>
        // Gráfico de Pizza - Status Distribution
        const ctx = document.getElementById('statusChart');
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: ['Pass', 'Fail', 'Warn', 'Error', 'Skip'],
                datasets: [{{
                    data: [{status_counts.get('pass', 0)}, {status_counts.get('fail', 0)}, {status_counts.get('warn', 0)}, {status_counts.get('error', 0)}, {status_counts.get('skip', 0)}],
                    backgroundColor: ['#10b981', '#ef4444', '#f59e0b', '#dc2626', '#6b7280']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

        return html

    def _build_historical_html(self, reports: List[Dict[str, Any]]) -> str:
        """Constrói HTML com gráficos históricos."""
        # Extrair dados para gráficos
        dates = []
        health_scores = []
        durations = []

        for report in reports:
            cycle_id = report.get("cycle_id", "")
            if cycle_id:
                # Format: YYYYMMDD_HHMMSS
                try:
                    dt = datetime.strptime(cycle_id, "%Y%m%d_%H%M%S")
                    dates.append(dt.strftime("%d/%m %H:%M"))
                except ValueError:
                    dates.append(cycle_id[:8])

            health_scores.append(report.get("health_score", 0))
            durations.append(report.get("duration_seconds", 0))

        # Calcular estatísticas
        avg_health = sum(health_scores) / len(health_scores) if health_scores else 0
        avg_duration = sum(durations) / len(durations) if durations else 0
        total_reports = len(reports)

        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenClaw Historical Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body class="bg-gray-50">
    <div class="container mx-auto px-4 py-8">
        <!-- Header -->
        <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h1 class="text-3xl font-bold text-gray-900">OpenClaw Historical Dashboard</h1>
            <p class="text-gray-600 mt-1">Análise de {total_reports} ciclos de qualidade</p>
        </div>

        <!-- Estatísticas Gerais -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-sm font-medium text-gray-600 mb-2">Health Score Médio</h3>
                <div class="text-4xl font-bold text-blue-600">{avg_health:.1f}/100</div>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-sm font-medium text-gray-600 mb-2">Duração Média</h3>
                <div class="text-4xl font-bold text-purple-600">{avg_duration:.1f}s</div>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-sm font-medium text-gray-600 mb-2">Total de Ciclos</h3>
                <div class="text-4xl font-bold text-green-600">{total_reports}</div>
            </div>
        </div>

        <!-- Gráfico Health Score Over Time -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h2 class="text-xl font-bold text-gray-900 mb-4">Health Score Over Time</h2>
            <canvas id="healthChart"></canvas>
        </div>

        <!-- Gráfico Performance Over Time -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h2 class="text-xl font-bold text-gray-900 mb-4">Performance Over Time</h2>
            <canvas id="performanceChart"></canvas>
        </div>

        <!-- Footer -->
        <div class="mt-8 text-center text-gray-500 text-sm">
            <p>Gerado por OpenClaw v3.0 • {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
        </div>
    </div>

    <script>
        // Health Score Chart
        const healthCtx = document.getElementById('healthChart');
        new Chart(healthCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(dates)},
                datasets: [{{
                    label: 'Health Score',
                    data: {json.dumps(health_scores)},
                    borderColor: '#3b82f6',
                    backgroundColor: '#3b82f620',
                    tension: 0.4,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});

        // Performance Chart
        const perfCtx = document.getElementById('performanceChart');
        new Chart(perfCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(dates)},
                datasets: [{{
                    label: 'Duração (s)',
                    data: {json.dumps(durations)},
                    backgroundColor: '#8b5cf6'
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

        return html
