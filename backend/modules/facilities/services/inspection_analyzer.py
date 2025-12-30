"""
InspectionAnalyzerService - Análise inteligente de inspeções.

Este serviço implementa algoritmos de IA para:
- Analisar resultados de inspeções
- Identificar padrões e tendências
- Sugerir ações corretivas
- Prever problemas futuros
- Calcular scores de conformidade
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from core.logging import logger
from modules.facilities.models.inspection import InspectionResult


class InspectionAnalyzerService:
    """
    Serviço inteligente de análise de inspeções.

    Implementa algoritmos de IA para analisar inspeções
    e gerar insights acionáveis.
    """

    # Pesos para categorias de itens
    CATEGORY_WEIGHTS = {
        "seguranca": 2.0,
        "estrutural": 1.8,
        "eletrica": 1.5,
        "hidraulica": 1.4,
        "incendio": 2.0,
        "acessibilidade": 1.3,
        "limpeza": 1.0,
        "documentacao": 1.1,
        "default": 1.0,
    }

    # Limiares de risco
    RISK_THRESHOLDS = {
        "low": 80,
        "medium": 60,
        "high": 40,
        "critical": 20,
    }

    def __init__(self) -> None:
        """Inicializa o serviço."""
        self._initialized = True

    def analyze_inspection(
        self,
        inspection_data: Dict[str, Any],
        checklist_items: List[Dict[str, Any]],
        historical_data: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Analisa uma inspeção completa.

        Args:
            inspection_data: Dados da inspeção
            checklist_items: Itens do checklist preenchidos
            historical_data: Histórico de inspeções anteriores

        Returns:
            Análise detalhada com score, riscos e recomendações
        """
        logger.info(f"Analisando inspeção {inspection_data.get('id', 'N/A')}")

        # Calcular métricas básicas
        metrics = self._calculate_metrics(checklist_items)

        # Calcular score ponderado
        weighted_score = self._calculate_weighted_score(checklist_items)

        # Identificar problemas críticos
        critical_issues = self._identify_critical_issues(checklist_items)

        # Determinar nível de risco
        risk_level = self._determine_risk_level(weighted_score, critical_issues)

        # Analisar tendência (se houver histórico)
        trend = self._analyze_trend(historical_data) if historical_data else None

        # Gerar recomendações
        recommendations = self._generate_recommendations(
            checklist_items,
            critical_issues,
            risk_level,
            trend,
        )

        # Estimar custos de remediação
        remediation_cost = self._estimate_remediation_cost(critical_issues)

        # Priorizar áreas de ação
        priority_areas = self._prioritize_areas(checklist_items, critical_issues)

        # Determinar resultado sugerido
        suggested_result = self._suggest_result(weighted_score, critical_issues)

        return {
            "score": round(weighted_score, 2),
            "risk_level": risk_level,
            "metrics": metrics,
            "critical_issues": critical_issues,
            "recommendations": recommendations,
            "priority_areas": priority_areas,
            "trend": trend,
            "estimated_remediation_cost": remediation_cost,
            "suggested_result": suggested_result,
            "analysis_timestamp": datetime.now().isoformat(),
            "confidence": self._calculate_confidence(checklist_items),
        }

    def compare_inspections(
        self,
        inspection1: Dict[str, Any],
        inspection2: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Compara duas inspeções.

        Args:
            inspection1: Primeira inspeção (mais antiga)
            inspection2: Segunda inspeção (mais recente)

        Returns:
            Comparação detalhada
        """
        logger.info("Comparando inspeções")

        score1 = inspection1.get("score", 0)
        score2 = inspection2.get("score", 0)
        score_diff = score2 - score1

        items_improved = []
        items_worsened = []
        items_unchanged = []

        items1 = {i.get("question"): i for i in inspection1.get("items", [])}
        items2 = {i.get("question"): i for i in inspection2.get("items", [])}

        for question, item2 in items2.items():
            item1 = items1.get(question)
            if not item1:
                continue

            status1 = item1.get("status", "pending")
            status2 = item2.get("status", "pending")

            status_value = {"ok": 3, "warning": 2, "critical": 1, "pending": 0}

            val1 = status_value.get(status1, 0)
            val2 = status_value.get(status2, 0)

            if val2 > val1:
                items_improved.append(
                    {
                        "question": question,
                        "before": status1,
                        "after": status2,
                    }
                )
            elif val2 < val1:
                items_worsened.append(
                    {
                        "question": question,
                        "before": status1,
                        "after": status2,
                    }
                )
            else:
                items_unchanged.append(question)

        return {
            "score_change": round(score_diff, 2),
            "score_change_percent": round(
                (score_diff / score1 * 100) if score1 > 0 else 0, 2
            ),
            "trend": (
                "improving" if score_diff > 0
                else ("declining" if score_diff < 0 else "stable")
            ),
            "items_improved": items_improved,
            "items_worsened": items_worsened,
            "items_unchanged_count": len(items_unchanged),
            "total_items_compared": len(items2),
            "improvement_rate": round(
                len(items_improved) / len(items2) * 100 if items2 else 0, 2
            ),
        }

    def predict_issues(
        self,
        historical_inspections: List[Dict[str, Any]],
        _area_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Prevê problemas futuros baseado em histórico.

        Args:
            historical_inspections: Histórico de inspeções
            _area_data: Dados da área (reservado para uso futuro)

        Returns:
            Lista de previsões de problemas
        """
        logger.info("Prevendo problemas futuros")

        if len(historical_inspections) < 2:
            return []

        predictions = []

        # Analisar padrões de deterioração por categoria
        category_trends = self._analyze_category_trends(historical_inspections)

        for category, trend in category_trends.items():
            if trend["direction"] == "declining" and trend["rate"] > 0.1:
                predictions.append(
                    {
                        "category": category,
                        "probability": min(0.95, trend["rate"] * 2),
                        "estimated_occurrence": self._estimate_occurrence(
                            trend["rate"],
                            trend["current_score"],
                        ),
                        "severity": self._estimate_severity(category, trend),
                        "recommendation": self._get_preventive_recommendation(category),
                    }
                )

        # Ordenar por probabilidade
        predictions.sort(key=lambda x: x["probability"], reverse=True)

        return predictions[:5]  # Top 5 previsões

    def generate_report_summary(
        self,
        inspections: List[Dict[str, Any]],
        period_days: int = 30,
    ) -> Dict[str, Any]:
        """
        Gera resumo executivo de inspeções.

        Args:
            inspections: Lista de inspeções
            period_days: Período em dias

        Returns:
            Resumo executivo
        """
        logger.info(f"Gerando resumo de {len(inspections)} inspeções")

        if not inspections:
            return {
                "total_inspections": 0,
                "period_days": period_days,
                "message": "Sem inspeções no período",
            }

        # Métricas gerais
        scores = [i.get("score", 0) for i in inspections]
        avg_score = sum(scores) / len(scores) if scores else 0

        # Contagem de resultados
        results = {}
        for insp in inspections:
            result = insp.get("result", "pending")
            results[result] = results.get(result, 0) + 1

        # Issues por categoria
        category_issues = {}
        for insp in inspections:
            for item in insp.get("items", []):
                if item.get("status") in ("warning", "critical"):
                    cat = item.get("category", "outros")
                    category_issues[cat] = category_issues.get(cat, 0) + 1

        # Top problemas recorrentes
        problem_frequency = {}
        for insp in inspections:
            for item in insp.get("items", []):
                if item.get("status") in ("warning", "critical"):
                    question = item.get("question", "")
                    problem_frequency[question] = problem_frequency.get(question, 0) + 1

        top_problems = sorted(
            problem_frequency.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:5]

        # Tendência
        if len(inspections) >= 2:
            sorted_insp = sorted(
                inspections,
                key=lambda x: x.get("date", date.min),
            )
            first_half = sorted_insp[: len(sorted_insp) // 2]
            second_half = sorted_insp[len(sorted_insp) // 2 :]

            avg_first = sum(i.get("score", 0) for i in first_half) / len(first_half)
            avg_second = sum(i.get("score", 0) for i in second_half) / len(second_half)

            trend = (
                "improving"
                if avg_second > avg_first
                else ("declining" if avg_second < avg_first else "stable")
            )
        else:
            trend = "insufficient_data"

        return {
            "period_days": period_days,
            "total_inspections": len(inspections),
            "average_score": round(avg_score, 2),
            "min_score": min(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "results_distribution": results,
            "category_issues": category_issues,
            "top_recurring_problems": [
                {"problem": p[0], "count": p[1]} for p in top_problems
            ],
            "trend": trend,
            "compliance_rate": round(
                results.get("approved", 0) / len(inspections) * 100, 2
            ),
            "critical_count": sum(
                1 for i in inspections if i.get("items_critical", 0) > 0
            ),
        }

    def _calculate_metrics(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula métricas básicas dos itens."""
        total = len(items)
        if total == 0:
            return {
                "total_items": 0,
                "items_ok": 0,
                "items_warning": 0,
                "items_critical": 0,
                "items_na": 0,
                "completion_rate": 0,
                "compliance_rate": 0,
            }

        ok = sum(1 for i in items if i.get("status") == "ok")
        warning = sum(1 for i in items if i.get("status") == "warning")
        critical = sum(1 for i in items if i.get("status") == "critical")
        na = sum(1 for i in items if i.get("status") == "na")
        answered = ok + warning + critical + na

        return {
            "total_items": total,
            "items_ok": ok,
            "items_warning": warning,
            "items_critical": critical,
            "items_na": na,
            "completion_rate": round(answered / total * 100, 2),
            "compliance_rate": round(ok / (answered - na) * 100, 2) if (answered - na) > 0 else 0,
        }

    def _calculate_weighted_score(self, items: List[Dict[str, Any]]) -> float:
        """Calcula score ponderado por categoria."""
        if not items:
            return 0.0

        weighted_sum = 0.0
        total_weight = 0.0

        for item in items:
            status = item.get("status", "pending")
            if status == "pending":
                continue

            category = item.get("category", "default").lower()
            weight = self.CATEGORY_WEIGHTS.get(category, 1.0)
            item_weight = item.get("weight", 1.0) * weight

            if status == "ok":
                score = 100
            elif status == "warning":
                score = 50
            elif status == "na":
                continue  # Não conta
            else:  # critical
                score = 0

            weighted_sum += score * item_weight
            total_weight += item_weight

        if total_weight == 0:
            return 0.0

        return weighted_sum / total_weight

    def _identify_critical_issues(
        self,
        items: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Identifica issues críticos."""
        critical = []

        for item in items:
            if item.get("status") == "critical":
                critical.append(
                    {
                        "question": item.get("question", ""),
                        "category": item.get("category", "outros"),
                        "notes": item.get("notes", ""),
                        "requires_immediate_action": True,
                    }
                )
            elif item.get("status") == "warning":
                category = item.get("category", "").lower()
                # Warnings em categorias críticas também são importantes
                if category in ("seguranca", "incendio", "estrutural"):
                    critical.append(
                        {
                            "question": item.get("question", ""),
                            "category": category,
                            "notes": item.get("notes", ""),
                            "requires_immediate_action": False,
                        }
                    )

        return critical

    def _determine_risk_level(
        self,
        score: float,
        critical_issues: List[Dict[str, Any]],
    ) -> str:
        """Determina nível de risco."""
        # Issues críticos aumentam o risco
        immediate_action_count = sum(
            1 for i in critical_issues if i.get("requires_immediate_action")
        )

        if immediate_action_count >= 3 or score < self.RISK_THRESHOLDS["critical"]:
            return "critical"
        if immediate_action_count >= 1 or score < self.RISK_THRESHOLDS["high"]:
            return "high"
        if score < self.RISK_THRESHOLDS["medium"]:
            return "medium"
        return "low"

    def _analyze_trend(
        self,
        historical_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Analisa tendência baseado no histórico."""
        if len(historical_data) < 2:
            return {"direction": "insufficient_data", "change": 0}

        sorted_data = sorted(
            historical_data,
            key=lambda x: x.get("date", date.min),
        )

        scores = [d.get("score", 0) for d in sorted_data]

        # Calcular tendência linear simples
        n = len(scores)
        if n < 2:
            return {"direction": "stable", "change": 0}

        avg_change = (scores[-1] - scores[0]) / (n - 1) if n > 1 else 0

        if avg_change > 2:
            direction = "improving"
        elif avg_change < -2:
            direction = "declining"
        else:
            direction = "stable"

        return {
            "direction": direction,
            "change_per_inspection": round(avg_change, 2),
            "first_score": scores[0],
            "last_score": scores[-1],
            "inspections_analyzed": n,
        }

    def _generate_recommendations(
        self,
        items: List[Dict[str, Any]],
        critical_issues: List[Dict[str, Any]],
        risk_level: str,
        trend: Optional[Dict[str, Any]],
    ) -> List[str]:
        """Gera recomendações baseadas na análise."""
        recommendations = []

        # Recomendações por issues críticos
        if critical_issues:
            categories_affected = set(i["category"] for i in critical_issues)

            for cat in categories_affected:
                if cat == "seguranca":
                    recommendations.append(
                        "Priorizar correção de itens de segurança identificados"
                    )
                elif cat == "incendio":
                    recommendations.append(
                        "Verificar sistema de prevenção contra incêndio urgentemente"
                    )
                elif cat == "estrutural":
                    recommendations.append(
                        "Solicitar laudo técnico estrutural"
                    )
                elif cat == "eletrica":
                    recommendations.append(
                        "Contratar eletricista para verificação das não conformidades"
                    )

        # Recomendações por nível de risco
        if risk_level == "critical":
            recommendations.insert(
                0,
                "URGENTE: Área requer intervenção imediata antes de liberação",
            )
        elif risk_level == "high":
            recommendations.insert(
                0,
                "Agendar manutenção corretiva em até 7 dias",
            )

        # Recomendações por tendência
        if trend and trend.get("direction") == "declining":
            recommendations.append(
                "Tendência de queda detectada - revisar programa de manutenção preventiva"
            )

        # Recomendações gerais baseadas nos itens
        warning_count = sum(1 for i in items if i.get("status") == "warning")
        if warning_count > 5:
            recommendations.append(
                f"{warning_count} itens em alerta - planejar manutenção preventiva"
            )

        return recommendations[:7]  # Limitar a 7 recomendações

    def _estimate_remediation_cost(
        self,
        critical_issues: List[Dict[str, Any]],
    ) -> float:
        """Estima custo de remediação."""
        # Custos médios por categoria (R$)
        category_costs = {
            "seguranca": 2000,
            "estrutural": 5000,
            "eletrica": 1500,
            "hidraulica": 1200,
            "incendio": 3000,
            "acessibilidade": 2500,
            "limpeza": 500,
            "default": 1000,
        }

        total = 0.0
        for issue in critical_issues:
            category = issue.get("category", "default").lower()
            cost = category_costs.get(category, category_costs["default"])
            # Issues que requerem ação imediata custam mais
            if issue.get("requires_immediate_action"):
                cost *= 1.5
            total += cost

        return round(total, 2)

    def _prioritize_areas(
        self,
        items: List[Dict[str, Any]],
        _critical_issues: List[Dict[str, Any]],
    ) -> List[str]:
        """Prioriza áreas de ação."""
        area_scores = {}

        for item in items:
            category = item.get("category", "outros").lower()
            status = item.get("status", "pending")

            if category not in area_scores:
                area_scores[category] = {"critical": 0, "warning": 0, "weight": 0}

            if status == "critical":
                area_scores[category]["critical"] += 1
            elif status == "warning":
                area_scores[category]["warning"] += 1

            area_scores[category]["weight"] = self.CATEGORY_WEIGHTS.get(category, 1.0)

        # Calcular score de prioridade
        priorities = []
        for category, data in area_scores.items():
            score = (data["critical"] * 10 + data["warning"] * 3) * data["weight"]
            if score > 0:
                priorities.append((category, score))

        priorities.sort(key=lambda x: x[1], reverse=True)

        return [p[0] for p in priorities[:5]]

    def _suggest_result(
        self,
        score: float,
        critical_issues: List[Dict[str, Any]],
    ) -> str:
        """Sugere resultado da inspeção."""
        immediate_action = sum(
            1 for i in critical_issues if i.get("requires_immediate_action")
        )

        if immediate_action > 0 or score < 40:
            return InspectionResult.REPROVED.value
        if score < 70 or len(critical_issues) > 0:
            return InspectionResult.APPROVED_WITH_REMARKS.value
        if score >= 90:
            return InspectionResult.APPROVED.value
        return InspectionResult.APPROVED_WITH_REMARKS.value

    def _calculate_confidence(self, items: List[Dict[str, Any]]) -> float:
        """Calcula confiança da análise."""
        if not items:
            return 0.0

        answered = sum(1 for i in items if i.get("status") != "pending")
        completion_rate = answered / len(items)

        # Verificar se há fotos/evidências
        with_evidence = sum(1 for i in items if i.get("photos"))
        evidence_rate = with_evidence / len(items) if items else 0

        # Verificar notas em itens problemáticos
        problematic = [i for i in items if i.get("status") in ("warning", "critical")]
        with_notes = sum(1 for i in problematic if i.get("notes"))
        notes_rate = with_notes / len(problematic) if problematic else 1

        confidence = completion_rate * 0.5 + evidence_rate * 0.25 + notes_rate * 0.25
        return round(min(0.95, confidence), 2)

    def _analyze_category_trends(
        self,
        inspections: List[Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """Analisa tendências por categoria."""
        category_scores = {}

        for insp in inspections:
            for item in insp.get("items", []):
                category = item.get("category", "outros").lower()
                status = item.get("status", "pending")

                if category not in category_scores:
                    category_scores[category] = []

                score = {"ok": 100, "warning": 50, "critical": 0}.get(status, None)
                if score is not None:
                    category_scores[category].append(score)

        trends = {}
        for category, scores in category_scores.items():
            if len(scores) >= 2:
                avg_change = (scores[-1] - scores[0]) / (len(scores) - 1)
                trends[category] = {
                    "direction": "declining" if avg_change < -5 else (
                        "improving" if avg_change > 5 else "stable"
                    ),
                    "rate": abs(avg_change) / 100,
                    "current_score": scores[-1],
                }

        return trends

    def _estimate_occurrence(self, rate: float, current_score: float) -> str:
        """Estima quando o problema pode ocorrer."""
        if rate > 0.3:
            return "Próxima inspeção"
        if rate > 0.15:
            return "2-3 inspeções"
        if current_score < 50:
            return "Próxima inspeção"
        return "3-6 meses"

    def _estimate_severity(
        self,
        category: str,
        trend: Dict[str, Any],
    ) -> str:
        """Estima severidade do problema previsto."""
        high_risk_categories = {"seguranca", "incendio", "estrutural", "eletrica"}

        if category in high_risk_categories:
            if trend["current_score"] < 50:
                return "critical"
            return "high"

        if trend["current_score"] < 30:
            return "high"
        if trend["current_score"] < 60:
            return "medium"
        return "low"

    def _get_preventive_recommendation(self, category: str) -> str:
        """Retorna recomendação preventiva por categoria."""
        recommendations = {
            "seguranca": "Aumentar frequência de inspeções de segurança",
            "estrutural": "Solicitar avaliação técnica preventiva",
            "eletrica": "Realizar manutenção preventiva em instalações elétricas",
            "hidraulica": "Verificar sistema hidráulico e programar manutenção",
            "incendio": "Revisar e testar equipamentos de combate a incêndio",
            "limpeza": "Reforçar programa de limpeza",
            "acessibilidade": "Verificar e adequar itens de acessibilidade",
        }
        return recommendations.get(category, "Programar inspeção detalhada da área")


# Singleton
inspection_analyzer = InspectionAnalyzerService()
