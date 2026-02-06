"""
AIWorkflow Analyzer Service - Sprint 55.

Servico para analise de workflows com IA.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import statistics

logger = logging.getLogger(__name__)


class WorkflowAnalyzer:
    """
    Analisador de workflows com IA.

    Analisa performance, identifica bottlenecks e gera sugestoes.
    """

    def __init__(self):
        """Inicializa o analisador."""
        self._thresholds = {
            "success_rate_warning": 0.9,
            "success_rate_critical": 0.7,
            "execution_time_warning": 60000,  # 60s
            "execution_time_critical": 300000,  # 5min
            "failure_rate_warning": 0.1,
            "failure_rate_critical": 0.3,
        }

    def analyze_workflow(
        self,
        workflow_data: Dict[str, Any],
        executions: List[Dict[str, Any]],
        period_days: int = 30,
    ) -> Dict[str, Any]:
        """
        Analisa workflow completo.

        Args:
            workflow_data: Dados do workflow
            executions: Lista de execucoes
            period_days: Periodo de analise em dias

        Returns:
            Dict com resultado da analise
        """
        start_time = datetime.utcnow()

        try:
            # Filtra execucoes do periodo
            cutoff_date = datetime.utcnow() - timedelta(days=period_days)
            recent_executions = [
                e for e in executions
                if e.get("created_at", datetime.min) >= cutoff_date
            ]

            if not recent_executions:
                return self._empty_analysis(workflow_data)

            # Metricas basicas
            metrics = self._calculate_metrics(recent_executions)

            # Analise de steps
            step_analysis = self._analyze_steps(
                workflow_data.get("steps", []),
                recent_executions,
            )

            # Identifica bottlenecks
            bottlenecks = self._identify_bottlenecks(step_analysis)

            # Erros frequentes
            frequent_errors = self._analyze_errors(recent_executions)

            # Gera sugestoes de otimizacao
            optimizations = self._generate_optimizations(
                workflow_data,
                metrics,
                step_analysis,
                bottlenecks,
                frequent_errors,
            )

            # Calcula scores
            health_score = self._calculate_health_score(metrics, frequent_errors)
            efficiency_score = self._calculate_efficiency_score(metrics, step_analysis)
            reliability_score = self._calculate_reliability_score(metrics)

            processing_time = int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )

            return {
                "workflow_id": workflow_data.get("id"),
                "analysis_type": "full",
                # Metricas
                "total_executions": metrics["total"],
                "success_rate": metrics["success_rate"],
                "failure_rate": metrics["failure_rate"],
                "avg_execution_time_ms": metrics["avg_time"],
                # Performance
                "p50_execution_time_ms": metrics["p50"],
                "p95_execution_time_ms": metrics["p95"],
                "p99_execution_time_ms": metrics["p99"],
                # Problemas
                "bottleneck_steps": bottlenecks,
                "frequent_errors": frequent_errors,
                # Sugestoes
                "optimizations": optimizations,
                # Scores
                "health_score": health_score,
                "efficiency_score": efficiency_score,
                "reliability_score": reliability_score,
                # Meta
                "processing_time_ms": processing_time,
            }

        except Exception as e:
            logger.error(f"Erro na analise do workflow: {e}")
            return self._empty_analysis(workflow_data)

    def _empty_analysis(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Retorna analise vazia."""
        return {
            "workflow_id": workflow_data.get("id"),
            "analysis_type": "full",
            "total_executions": 0,
            "success_rate": 0.0,
            "failure_rate": 0.0,
            "avg_execution_time_ms": 0.0,
            "p50_execution_time_ms": 0.0,
            "p95_execution_time_ms": 0.0,
            "p99_execution_time_ms": 0.0,
            "bottleneck_steps": [],
            "frequent_errors": [],
            "optimizations": [],
            "health_score": 0.0,
            "efficiency_score": 0.0,
            "reliability_score": 0.0,
            "processing_time_ms": 0,
        }

    def _calculate_metrics(
        self,
        executions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Calcula metricas de execucoes."""
        total = len(executions)
        if total == 0:
            return {
                "total": 0,
                "success_rate": 0.0,
                "failure_rate": 0.0,
                "avg_time": 0.0,
                "p50": 0.0,
                "p95": 0.0,
                "p99": 0.0,
            }

        # Contadores
        success = sum(1 for e in executions if e.get("status") == "completed")
        failed = sum(1 for e in executions if e.get("status") == "failed")

        # Tempos de execucao
        times = [
            e.get("execution_time_ms", 0)
            for e in executions
            if e.get("execution_time_ms", 0) > 0
        ]

        if times:
            sorted_times = sorted(times)
            avg_time = statistics.mean(times)
            p50 = self._percentile(sorted_times, 50)
            p95 = self._percentile(sorted_times, 95)
            p99 = self._percentile(sorted_times, 99)
        else:
            avg_time = p50 = p95 = p99 = 0.0

        return {
            "total": total,
            "success_rate": success / total if total > 0 else 0.0,
            "failure_rate": failed / total if total > 0 else 0.0,
            "avg_time": avg_time,
            "p50": p50,
            "p95": p95,
            "p99": p99,
        }

    def _percentile(self, sorted_data: List[float], percentile: int) -> float:
        """Calcula percentil."""
        if not sorted_data:
            return 0.0
        k = (len(sorted_data) - 1) * (percentile / 100)
        f = int(k)
        c = f + 1
        if c >= len(sorted_data):
            return sorted_data[-1]
        return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])

    def _analyze_steps(
        self,
        steps: List[Dict[str, Any]],
        executions: List[Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """Analisa performance por step."""
        step_stats = {}

        for step in steps:
            step_id = step.get("id", "")
            if not step_id:
                continue

            step_stats[step_id] = {
                "name": step.get("name", step_id),
                "type": step.get("step_type", "unknown"),
                "executions": 0,
                "failures": 0,
                "total_time": 0,
                "times": [],
            }

        # Coleta dados das execucoes
        for execution in executions:
            step_results = execution.get("step_results", {})

            for step_id, result in step_results.items():
                if step_id not in step_stats:
                    step_stats[step_id] = {
                        "name": step_id,
                        "type": "unknown",
                        "executions": 0,
                        "failures": 0,
                        "total_time": 0,
                        "times": [],
                    }

                step_stats[step_id]["executions"] += 1

                if result.get("status") == "failed":
                    step_stats[step_id]["failures"] += 1

                time_ms = result.get("execution_time_ms", 0)
                if time_ms > 0:
                    step_stats[step_id]["total_time"] += time_ms
                    step_stats[step_id]["times"].append(time_ms)

        # Calcula estatisticas
        for step_id, stats in step_stats.items():
            total = stats["executions"]
            if total > 0:
                stats["failure_rate"] = stats["failures"] / total
                stats["avg_time"] = stats["total_time"] / total
            else:
                stats["failure_rate"] = 0.0
                stats["avg_time"] = 0.0

            # P95
            if stats["times"]:
                sorted_times = sorted(stats["times"])
                stats["p95_time"] = self._percentile(sorted_times, 95)
            else:
                stats["p95_time"] = 0.0

        return step_stats

    def _identify_bottlenecks(
        self,
        step_analysis: Dict[str, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Identifica bottlenecks."""
        bottlenecks = []

        if not step_analysis:
            return bottlenecks

        # Calcula media geral
        all_times = []
        for stats in step_analysis.values():
            all_times.extend(stats.get("times", []))

        if not all_times:
            return bottlenecks

        avg_all = statistics.mean(all_times) if all_times else 0
        threshold = avg_all * 2  # Steps com tempo > 2x a media

        for step_id, stats in step_analysis.items():
            is_bottleneck = False
            reasons = []

            # Tempo muito alto
            if stats.get("avg_time", 0) > threshold and threshold > 0:
                is_bottleneck = True
                reasons.append(f"Tempo medio ({stats['avg_time']:.0f}ms) > 2x media geral")

            # Alta taxa de falha
            if stats.get("failure_rate", 0) > 0.1:
                is_bottleneck = True
                reasons.append(f"Taxa de falha alta ({stats['failure_rate']:.1%})")

            # P95 muito alto
            if stats.get("p95_time", 0) > self._thresholds["execution_time_warning"]:
                is_bottleneck = True
                reasons.append(f"P95 alto ({stats['p95_time']:.0f}ms)")

            if is_bottleneck:
                bottlenecks.append({
                    "step_id": step_id,
                    "step_name": stats.get("name", step_id),
                    "step_type": stats.get("type", "unknown"),
                    "avg_time_ms": stats.get("avg_time", 0),
                    "p95_time_ms": stats.get("p95_time", 0),
                    "failure_rate": stats.get("failure_rate", 0),
                    "reasons": reasons,
                    "severity": "high" if stats.get("failure_rate", 0) > 0.2 else "medium",
                })

        # Ordena por severidade
        bottlenecks.sort(
            key=lambda x: (
                0 if x["severity"] == "high" else 1,
                -x.get("failure_rate", 0),
            )
        )

        return bottlenecks[:5]

    def _analyze_errors(
        self,
        executions: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Analisa erros frequentes."""
        error_counts = {}

        for execution in executions:
            if execution.get("status") != "failed":
                continue

            error_msg = execution.get("error_message", "Unknown error")
            error_step = execution.get("error_step", "unknown")

            # Normaliza mensagem (remove detalhes especificos)
            normalized_msg = self._normalize_error_message(error_msg)
            key = f"{error_step}::{normalized_msg}"

            if key not in error_counts:
                error_counts[key] = {
                    "error_type": normalized_msg,
                    "step": error_step,
                    "count": 0,
                    "examples": [],
                }

            error_counts[key]["count"] += 1
            if len(error_counts[key]["examples"]) < 3:
                error_counts[key]["examples"].append(error_msg)

        # Converte para lista e ordena
        errors = list(error_counts.values())
        errors.sort(key=lambda x: -x["count"])

        return errors[:10]

    def _normalize_error_message(self, message: str) -> str:
        """Normaliza mensagem de erro."""
        if not message:
            return "Unknown error"

        # Remove IDs, timestamps, etc
        import re

        normalized = message[:100]  # Limita tamanho
        normalized = re.sub(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", "<UUID>", normalized)
        normalized = re.sub(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", "<TIMESTAMP>", normalized)
        normalized = re.sub(r"\d+", "<N>", normalized)

        return normalized.strip()

    def _generate_optimizations(
        self,
        workflow_data: Dict[str, Any],
        metrics: Dict[str, Any],
        step_analysis: Dict[str, Dict[str, Any]],
        bottlenecks: List[Dict[str, Any]],
        frequent_errors: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Gera sugestoes de otimizacao."""
        optimizations = []

        # 1. Otimizacoes de performance
        if metrics.get("avg_time", 0) > self._thresholds["execution_time_warning"]:
            optimizations.append({
                "optimization_type": "performance",
                "title": "Reduzir tempo de execucao",
                "description": f"O tempo medio de execucao ({metrics['avg_time']:.0f}ms) esta acima do recomendado.",
                "suggestion": "Considere paralelizar steps independentes ou otimizar steps com maior tempo.",
                "estimated_improvement": 0.2,
                "confidence": 0.7,
                "priority": 8,
                "current_state": {"avg_execution_time_ms": metrics["avg_time"]},
                "proposed_state": {"avg_execution_time_ms": metrics["avg_time"] * 0.8},
                "changes": [{"type": "parallel_execution", "steps": []}],
            })

        # 2. Otimizacoes de confiabilidade
        if metrics.get("success_rate", 1) < self._thresholds["success_rate_warning"]:
            optimizations.append({
                "optimization_type": "reliability",
                "title": "Melhorar taxa de sucesso",
                "description": f"A taxa de sucesso ({metrics['success_rate']:.1%}) esta abaixo do ideal.",
                "suggestion": "Adicione tratamento de erros e retries nos steps problematicos.",
                "estimated_improvement": 0.15,
                "confidence": 0.8,
                "priority": 9,
                "current_state": {"success_rate": metrics["success_rate"]},
                "proposed_state": {"success_rate": min(0.95, metrics["success_rate"] + 0.1)},
                "changes": [{"type": "add_retry", "steps": [b["step_id"] for b in bottlenecks]}],
            })

        # 3. Otimizacoes por bottleneck
        for bottleneck in bottlenecks[:2]:
            if bottleneck.get("failure_rate", 0) > 0.1:
                optimizations.append({
                    "optimization_type": "reliability",
                    "title": f"Corrigir step '{bottleneck['step_name']}'",
                    "description": f"Step com taxa de falha de {bottleneck['failure_rate']:.1%}.",
                    "suggestion": "Revise a implementacao do step e adicione validacoes.",
                    "estimated_improvement": bottleneck["failure_rate"] * 0.5,
                    "confidence": 0.6,
                    "priority": 7,
                    "current_state": {"step_failure_rate": bottleneck["failure_rate"]},
                    "proposed_state": {"step_failure_rate": bottleneck["failure_rate"] * 0.5},
                    "changes": [{"type": "fix_step", "step_id": bottleneck["step_id"]}],
                })

        # 4. Otimizacoes baseadas em erros
        if frequent_errors:
            top_error = frequent_errors[0]
            if top_error.get("count", 0) > 5:
                optimizations.append({
                    "optimization_type": "reliability",
                    "title": f"Corrigir erro recorrente no step '{top_error['step']}'",
                    "description": f"Erro '{top_error['error_type']}' ocorreu {top_error['count']} vezes.",
                    "suggestion": "Implemente tratamento especifico para este tipo de erro.",
                    "estimated_improvement": 0.1,
                    "confidence": 0.7,
                    "priority": 6,
                    "current_state": {"error_count": top_error["count"]},
                    "proposed_state": {"error_count": 0},
                    "changes": [{"type": "handle_error", "error_type": top_error["error_type"]}],
                })

        # 5. Otimizacoes de automacao
        steps = workflow_data.get("steps", [])
        approval_steps = [s for s in steps if s.get("step_type") == "approval"]
        if len(approval_steps) > 2:
            optimizations.append({
                "optimization_type": "automation",
                "title": "Reduzir aprovacoes manuais",
                "description": f"AIWorkflow possui {len(approval_steps)} steps de aprovacao.",
                "suggestion": "Considere automatizar aprovacoes de baixo risco com regras.",
                "estimated_improvement": 0.3,
                "confidence": 0.5,
                "priority": 5,
                "current_state": {"manual_approvals": len(approval_steps)},
                "proposed_state": {"manual_approvals": max(1, len(approval_steps) - 1)},
                "changes": [{"type": "auto_approval", "condition": "low_risk"}],
            })

        # Ordena por prioridade
        optimizations.sort(key=lambda x: -x.get("priority", 0))

        return optimizations[:5]

    def _calculate_health_score(
        self,
        metrics: Dict[str, Any],
        errors: List[Dict[str, Any]],
    ) -> float:
        """Calcula score de saude do workflow."""
        score = 100.0

        # Penaliza por taxa de sucesso baixa
        success_rate = metrics.get("success_rate", 0)
        if success_rate < 0.99:
            penalty = (0.99 - success_rate) * 100
            score -= penalty

        # Penaliza por tempo de execucao alto
        avg_time = metrics.get("avg_time", 0)
        if avg_time > self._thresholds["execution_time_warning"]:
            score -= 10
        if avg_time > self._thresholds["execution_time_critical"]:
            score -= 20

        # Penaliza por erros frequentes
        if errors:
            total_errors = sum(e.get("count", 0) for e in errors)
            if total_errors > 10:
                score -= min(30, total_errors / 2)

        return max(0, min(100, score))

    def _calculate_efficiency_score(
        self,
        metrics: Dict[str, Any],
        step_analysis: Dict[str, Dict[str, Any]],
    ) -> float:
        """Calcula score de eficiencia."""
        score = 100.0

        # Penaliza por steps lentos
        slow_steps = 0
        for stats in step_analysis.values():
            if stats.get("avg_time", 0) > 30000:  # > 30s
                slow_steps += 1

        score -= slow_steps * 5

        # Penaliza por variancia alta (p95 >> media)
        avg = metrics.get("avg_time", 1)
        p95 = metrics.get("p95", 0)
        if avg > 0 and p95 > avg * 3:
            score -= 15

        return max(0, min(100, score))

    def _calculate_reliability_score(
        self,
        metrics: Dict[str, Any],
    ) -> float:
        """Calcula score de confiabilidade."""
        success_rate = metrics.get("success_rate", 0)
        return success_rate * 100


class WorkflowOptimizer:
    """
    Otimizador de workflows.

    Aplica otimizacoes sugeridas.
    """

    def __init__(self):
        """Inicializa o otimizador."""
        self._analyzer = WorkflowAnalyzer()

    def suggest_optimizations(
        self,
        workflow_data: Dict[str, Any],
        executions: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Sugere otimizacoes para workflow.

        Args:
            workflow_data: Dados do workflow
            executions: Lista de execucoes

        Returns:
            Lista de sugestoes
        """
        analysis = self._analyzer.analyze_workflow(workflow_data, executions)
        return analysis.get("optimizations", [])

    def apply_optimization(
        self,
        workflow_data: Dict[str, Any],
        optimization: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Aplica otimizacao ao workflow.

        Args:
            workflow_data: Dados do workflow
            optimization: Otimizacao a aplicar

        Returns:
            AIWorkflow atualizado
        """
        updated = workflow_data.copy()
        changes = optimization.get("changes", [])

        for change in changes:
            change_type = change.get("type")

            if change_type == "add_retry":
                updated = self._apply_retry_changes(updated, change)
            elif change_type == "parallel_execution":
                updated = self._apply_parallel_changes(updated, change)
            elif change_type == "auto_approval":
                updated = self._apply_auto_approval(updated, change)

        updated["is_ai_optimized"] = True
        updated["last_optimization"] = datetime.utcnow().isoformat()

        return updated

    def _apply_retry_changes(
        self,
        workflow: Dict[str, Any],
        change: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Aplica configuracao de retry."""
        steps = workflow.get("steps", [])
        target_steps = change.get("steps", [])

        for step in steps:
            if step.get("id") in target_steps or not target_steps:
                config = step.get("config", {})
                config["retry_count"] = config.get("retry_count", 0) + 1
                config["retry_delay"] = config.get("retry_delay", 5000)
                step["config"] = config

        workflow["steps"] = steps
        return workflow

    def _apply_parallel_changes(
        self,
        workflow: Dict[str, Any],
        change: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Aplica paralelizacao de steps."""
        # Implementacao simplificada
        settings = workflow.get("settings", {})
        settings["parallel_enabled"] = True
        workflow["settings"] = settings
        return workflow

    def _apply_auto_approval(
        self,
        workflow: Dict[str, Any],
        change: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Aplica aprovacao automatica."""
        steps = workflow.get("steps", [])
        condition = change.get("condition", "low_risk")

        for step in steps:
            if step.get("step_type") == "approval":
                config = step.get("config", {})
                config["auto_approve_condition"] = condition
                step["config"] = config
                break  # Apenas primeiro

        workflow["steps"] = steps
        return workflow
