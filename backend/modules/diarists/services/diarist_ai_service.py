"""Service de IA para Diaristas."""

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from modules.diarists.models.diarist import (
    Diarist,
    DiaristSchedule,
    DiaristStatus,
    DiaristType,
    ScheduleStatus,
    Weekday,
)
from modules.diarists.repositories.diarist_repository import DiaristRepository
from modules.diarists.schemas.diarist_schemas import (
    DiaristSuggestionResponse,
    DiaristAvailabilityResponse,
    DiaristPerformanceResponse,
    ScheduleOptimizationResponse,
)

logger = logging.getLogger(__name__)


class DiaristAIService:
    """Service de IA para recomendações e análises de diaristas."""

    def __init__(self, db: Session):
        """Inicializa o service."""
        self.db = db
        self.repository = DiaristRepository(db)

    def suggest_diarists(
        self,
        condominio_id: UUID,
        data: date,
        tipo: Optional[DiaristType] = None,
        duracao_horas: int = 8,
        priorizar_conhecidas: bool = True,
    ) -> DiaristSuggestionResponse:
        """
        Sugere diaristas para uma data específica usando IA.

        Critérios de pontuação:
        - Avaliação média (peso 30%)
        - Taxa de conclusão (peso 20%)
        - Experiência no condomínio (peso 25%)
        - Pontualidade (peso 15%)
        - Disponibilidade de horário (peso 10%)
        """
        available = self.repository.get_available_diarists(
            data=data,
            tipo=tipo,
            condominio_id=condominio_id if priorizar_conhecidas else None,
        )

        if not available:
            return DiaristSuggestionResponse(
                data=data,
                tipo_servico=tipo,
                sugestoes=[],
                total_disponiveis=0,
                mensagem="Nenhuma diarista disponível para esta data",
            )

        scored_diarists = []
        for diarist in available:
            score = self._calculate_suggestion_score(
                diarist=diarist,
                condominio_id=condominio_id,
                duracao_horas=duracao_horas,
            )
            scored_diarists.append({
                "diarist": diarist,
                "score": score,
                "motivos": self._get_score_reasons(diarist, score),
            })

        # Ordenar por score
        scored_diarists.sort(key=lambda x: x["score"], reverse=True)

        # Pegar top 5
        top_suggestions = scored_diarists[:5]

        return DiaristSuggestionResponse(
            data=data,
            tipo_servico=tipo,
            sugestoes=[
                {
                    "diarist_id": str(s["diarist"].id),
                    "nome": s["diarist"].nome,
                    "avaliacao": float(s["diarist"].avaliacao_media or 0),
                    "score": round(s["score"], 2),
                    "motivos": s["motivos"],
                    "valor_diaria": float(s["diarist"].valor_diaria or 0),
                    "valor_hora": float(s["diarist"].valor_hora or 0),
                }
                for s in top_suggestions
            ],
            total_disponiveis=len(available),
            mensagem=f"Encontradas {len(available)} diaristas disponíveis",
        )

    def _calculate_suggestion_score(
        self,
        diarist: Diarist,
        condominio_id: UUID,
        duracao_horas: int,
    ) -> float:
        """Calcula score de sugestão para uma diarista."""
        score = 0.0

        # Avaliação média (peso 30%) - máximo 30 pontos
        if diarist.avaliacao_media:
            score += float(diarist.avaliacao_media) * 6  # 5 * 6 = 30

        # Taxa de conclusão (peso 20%) - máximo 20 pontos
        metrics = self.repository.get_diarist_metrics(diarist.id)
        if metrics["agendamentos"]["total"] > 0:
            taxa = metrics["agendamentos"]["taxa_conclusao"]
            score += taxa * 0.2

        # Experiência no condomínio (peso 25%) - máximo 25 pontos
        assignments = self.repository.list_assignments(
            diarist_id=diarist.id,
            condominio_id=condominio_id,
        )
        if assignments:
            # Bonus por já conhecer o condomínio
            score += min(len(assignments) * 5, 25)

        # Pontualidade (peso 15%) - máximo 15 pontos
        score += metrics.get("taxa_pontualidade", 0) * 0.15

        # Disponibilidade de horário (peso 10%) - máximo 10 pontos
        if diarist.hora_fim_disponivel and diarist.hora_inicio_disponivel:
            horas_disponiveis = (
                diarist.hora_fim_disponivel.hour - diarist.hora_inicio_disponivel.hour
            )
            if horas_disponiveis >= duracao_horas:
                score += 10
            else:
                score += (horas_disponiveis / duracao_horas) * 10

        return score

    def _get_score_reasons(self, diarist: Diarist, score: float) -> list[str]:
        """Gera motivos para a pontuação."""
        reasons = []

        if diarist.avaliacao_media and diarist.avaliacao_media >= 4.5:
            reasons.append("Excelente avaliação dos clientes")
        elif diarist.avaliacao_media and diarist.avaliacao_media >= 4.0:
            reasons.append("Boa avaliação dos clientes")

        if diarist.experiencia_anos and diarist.experiencia_anos >= 5:
            reasons.append(f"{diarist.experiencia_anos} anos de experiência")

        if diarist.total_servicos and diarist.total_servicos >= 50:
            reasons.append(f"{diarist.total_servicos} serviços realizados")

        if diarist.aceita_hora_extra:
            reasons.append("Aceita hora extra")

        if score >= 80:
            reasons.append("Altamente recomendada")
        elif score >= 60:
            reasons.append("Recomendada")

        return reasons if reasons else ["Disponível para a data"]

    def analyze_availability(
        self,
        condominio_id: UUID,
        data_inicio: date,
        data_fim: date,
        tipo: Optional[DiaristType] = None,
    ) -> DiaristAvailabilityResponse:
        """
        Analisa disponibilidade de diaristas em um período.

        Retorna análise detalhada por dia e recomendações.
        """
        days_analysis = []
        current = data_inicio

        while current <= data_fim:
            available = self.repository.get_available_diarists(
                data=current,
                tipo=tipo,
                condominio_id=condominio_id,
            )

            scheduled = self.repository.get_schedules_by_date(
                data=current,
                condominio_id=condominio_id,
            )

            weekday = Weekday(current.strftime("%A").upper())

            days_analysis.append({
                "data": current.isoformat(),
                "dia_semana": weekday.value,
                "disponiveis": len(available),
                "agendados": len(scheduled),
                "status": self._get_day_status(len(available), len(scheduled)),
            })

            current += timedelta(days=1)

        # Calcular estatísticas
        total_days = len(days_analysis)
        avg_available = sum(d["disponiveis"] for d in days_analysis) / total_days
        critical_days = [d for d in days_analysis if d["status"] == "critico"]

        # Gerar recomendações
        recommendations = self._generate_availability_recommendations(
            days_analysis=days_analysis,
            avg_available=avg_available,
            critical_days=critical_days,
        )

        return DiaristAvailabilityResponse(
            periodo={"inicio": data_inicio, "fim": data_fim},
            tipo_servico=tipo,
            analise_diaria=days_analysis,
            estatisticas={
                "media_disponiveis": round(avg_available, 1),
                "dias_criticos": len(critical_days),
                "total_dias": total_days,
            },
            recomendacoes=recommendations,
        )

    def _get_day_status(self, available: int, scheduled: int) -> str:
        """Determina status do dia."""
        if available == 0 and scheduled == 0:
            return "vazio"
        elif available == 0:
            return "critico"
        elif available <= 2:
            return "alerta"
        else:
            return "ok"

    def _generate_availability_recommendations(
        self,
        days_analysis: list[dict],
        avg_available: float,
        critical_days: list[dict],
    ) -> list[str]:
        """Gera recomendações baseadas na análise."""
        recommendations = []

        if critical_days:
            dates = [d["data"] for d in critical_days[:3]]
            recommendations.append(
                f"Atenção: {len(critical_days)} dias sem diaristas disponíveis. "
                f"Considere contratar mais profissionais para: {', '.join(dates)}"
            )

        if avg_available < 3:
            recommendations.append(
                "Média de disponibilidade baixa. "
                "Recomendado ampliar o cadastro de diaristas."
            )

        # Verificar dias da semana problemáticos
        weekday_counts = {}
        for day in days_analysis:
            wd = day["dia_semana"]
            if wd not in weekday_counts:
                weekday_counts[wd] = {"total": 0, "available": 0}
            weekday_counts[wd]["total"] += 1
            weekday_counts[wd]["available"] += day["disponiveis"]

        for wd, counts in weekday_counts.items():
            avg = counts["available"] / counts["total"]
            if avg < 2:
                recommendations.append(
                    f"Baixa disponibilidade às {wd}s. "
                    "Considere incentivar diaristas a trabalhar neste dia."
                )

        if not recommendations:
            recommendations.append("Disponibilidade adequada para o período analisado.")

        return recommendations

    def analyze_performance(
        self,
        diarist_id: UUID,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
    ) -> DiaristPerformanceResponse:
        """
        Analisa performance de uma diarista usando IA.

        Avalia múltiplas dimensões e gera insights.
        """
        if not data_inicio:
            data_inicio = date.today() - timedelta(days=90)
        if not data_fim:
            data_fim = date.today()

        diarist = self.repository.get_by_id(diarist_id)
        if not diarist:
            raise ValueError("Diarista não encontrada")

        metrics = self.repository.get_diarist_metrics(
            diarist_id=diarist_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )

        # Calcular scores por dimensão
        dimensions = self._calculate_performance_dimensions(diarist, metrics)

        # Score geral (média ponderada)
        overall_score = (
            dimensions["qualidade"] * 0.30 +
            dimensions["pontualidade"] * 0.25 +
            dimensions["confiabilidade"] * 0.25 +
            dimensions["produtividade"] * 0.20
        )

        # Gerar insights
        insights = self._generate_performance_insights(diarist, metrics, dimensions)

        # Determinar tendência
        trend = self._calculate_trend(diarist_id, data_inicio, data_fim)

        return DiaristPerformanceResponse(
            diarist_id=str(diarist_id),
            nome=diarist.nome,
            periodo={"inicio": data_inicio, "fim": data_fim},
            score_geral=round(overall_score, 1),
            dimensoes=dimensions,
            metricas=metrics,
            insights=insights,
            tendencia=trend,
            classificacao=self._get_classification(overall_score),
        )

    def _calculate_performance_dimensions(
        self, diarist: Diarist, metrics: dict
    ) -> dict[str, float]:
        """Calcula scores por dimensão de performance."""
        # Qualidade (baseado em avaliações)
        qualidade = float(diarist.avaliacao_media or 0) * 20  # 0-100

        # Pontualidade
        pontualidade = metrics.get("taxa_pontualidade", 0)

        # Confiabilidade (taxa de conclusão)
        confiabilidade = metrics["agendamentos"]["taxa_conclusao"]

        # Produtividade (horas trabalhadas / esperadas)
        horas = metrics.get("horas_trabalhadas", 0)
        expected = metrics["agendamentos"]["concluidos"] * 8  # 8h por dia
        produtividade = min((horas / expected * 100) if expected > 0 else 0, 100)

        return {
            "qualidade": round(qualidade, 1),
            "pontualidade": round(pontualidade, 1),
            "confiabilidade": round(confiabilidade, 1),
            "produtividade": round(produtividade, 1),
        }

    def _generate_performance_insights(
        self,
        _diarist: Diarist,
        metrics: dict,
        dimensions: dict,
    ) -> list[str]:
        """Gera insights sobre a performance."""
        insights = []

        # Análise de qualidade
        if dimensions["qualidade"] >= 90:
            insights.append(
                "Excelente qualidade de serviço! "
                "Avaliações consistentemente positivas."
            )
        elif dimensions["qualidade"] < 60:
            insights.append(
                "Qualidade abaixo do esperado. "
                "Recomendado feedback e treinamento."
            )

        # Análise de pontualidade
        if dimensions["pontualidade"] >= 95:
            insights.append("Pontualidade exemplar em todos os serviços.")
        elif dimensions["pontualidade"] < 80:
            insights.append(
                "Taxa de pontualidade precisa melhorar. "
                "Sugestão: confirmar agendamentos com antecedência."
            )

        # Análise de confiabilidade
        if dimensions["confiabilidade"] >= 95:
            insights.append("Alta confiabilidade - raramente cancela serviços.")
        elif dimensions["confiabilidade"] < 80:
            insights.append(
                "Taxa de cancelamento elevada. "
                "Verificar motivos e disponibilidade real."
            )

        # Análise de produtividade
        if dimensions["produtividade"] >= 100:
            insights.append("Produtividade acima da média - trabalha horas extras.")
        elif dimensions["produtividade"] < 80:
            insights.append(
                "Produtividade pode ser melhorada. "
                "Avaliar organização e planejamento."
            )

        # Insight geral
        total = metrics["agendamentos"]["total"]
        if total >= 20:
            insights.append(f"Profissional experiente com {total} serviços no período.")

        return insights

    def _calculate_trend(
        self,
        diarist_id: UUID,
        data_inicio: date,
        data_fim: date,
    ) -> str:
        """Calcula tendência de performance."""
        # Dividir período em duas partes
        mid_date = data_inicio + (data_fim - data_inicio) / 2

        first_half = self.repository.get_diarist_metrics(
            diarist_id=diarist_id,
            data_inicio=data_inicio,
            data_fim=mid_date,
        )

        second_half = self.repository.get_diarist_metrics(
            diarist_id=diarist_id,
            data_inicio=mid_date,
            data_fim=data_fim,
        )

        # Comparar taxas de conclusão
        rate1 = first_half["agendamentos"]["taxa_conclusao"]
        rate2 = second_half["agendamentos"]["taxa_conclusao"]

        if rate2 > rate1 + 5:
            return "melhorando"
        elif rate2 < rate1 - 5:
            return "declinando"
        else:
            return "estavel"

    def _get_classification(self, score: float) -> str:
        """Classifica a diarista baseado no score."""
        if score >= 90:
            return "Excepcional"
        elif score >= 80:
            return "Excelente"
        elif score >= 70:
            return "Bom"
        elif score >= 60:
            return "Regular"
        else:
            return "Precisa Melhorar"

    def optimize_schedule(
        self,
        condominio_id: UUID,
        data_inicio: date,
        data_fim: date,
        budget: Optional[Decimal] = None,
    ) -> ScheduleOptimizationResponse:
        """
        Otimiza agendamentos do condomínio usando IA.

        Considera:
        - Distribuição equilibrada de trabalho
        - Preferências e avaliações das diaristas
        - Custos e orçamento disponível
        - Histórico de serviços
        """
        # Buscar agendamentos existentes
        existing_schedules = self.repository.list_schedules(
            condominio_id=condominio_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )

        # Buscar diaristas disponíveis
        all_diarists = self.repository.list_all(
            status=DiaristStatus.ATIVO,
            condominio_id=condominio_id,
        )

        # Analisar distribuição atual
        distribution = self._analyze_distribution(existing_schedules, all_diarists)

        # Gerar sugestões de otimização
        suggestions = self._generate_optimization_suggestions(
            schedules=existing_schedules,
            _diarists=all_diarists,
            distribution=distribution,
            budget=budget,
        )

        # Calcular economia potencial
        potential_savings = self._calculate_potential_savings(
            schedules=existing_schedules,
            suggestions=suggestions,
        )

        return ScheduleOptimizationResponse(
            periodo={"inicio": data_inicio, "fim": data_fim},
            condominio_id=str(condominio_id),
            distribuicao_atual=distribution,
            sugestoes=suggestions,
            economia_potencial=float(potential_savings),
            impacto_qualidade=self._estimate_quality_impact(suggestions),
        )

    def _analyze_distribution(
        self,
        schedules: list[DiaristSchedule],
        diarists: list[Diarist],
    ) -> dict:
        """Analisa distribuição de trabalho."""
        distribution = {}

        for diarist in diarists:
            diarist_schedules = [s for s in schedules if s.diarist_id == diarist.id]
            distribution[str(diarist.id)] = {
                "nome": diarist.nome,
                "total_agendamentos": len(diarist_schedules),
                "horas_totais": sum(
                    float(s.calcular_horas_trabalhadas() or 0)
                    for s in diarist_schedules
                    if s.status == ScheduleStatus.CONCLUIDO
                ),
                "valor_total": sum(
                    float(s.valor_final or s.valor_previsto or 0)
                    for s in diarist_schedules
                ),
            }

        return distribution

    def _generate_optimization_suggestions(
        self,
        schedules: list[DiaristSchedule],
        _diarists: list[Diarist],
        distribution: dict,
        budget: Optional[Decimal],
    ) -> list[dict]:
        """Gera sugestões de otimização."""
        suggestions = []

        # Verificar desbalanceamento
        if distribution:
            totals = [d["total_agendamentos"] for d in distribution.values()]
            avg = sum(totals) / len(totals) if totals else 0
            max_val = max(totals) if totals else 0
            min_val = min(totals) if totals else 0

            if max_val - min_val > avg * 0.5:
                suggestions.append({
                    "tipo": "rebalanceamento",
                    "descricao": "Distribuição de trabalho desbalanceada",
                    "acao": "Redistribuir agendamentos entre diaristas",
                    "impacto": "medio",
                })

        # Verificar custos
        if budget:
            total_cost = sum(
                float(s.valor_previsto or 0) for s in schedules
            )
            if Decimal(str(total_cost)) > budget:
                suggestions.append({
                    "tipo": "reducao_custos",
                    "descricao": f"Custos excedem orçamento em R$ {total_cost - float(budget):.2f}",
                    "acao": "Considerar diaristas com menor custo ou reduzir frequência",
                    "impacto": "alto",
                })

        # Verificar diaristas subutilizadas
        top_diarists = self.repository.get_top_diarists(limit=5)
        for td in top_diarists:
            dist = distribution.get(str(td["diarist"].id), {})
            if dist.get("total_agendamentos", 0) == 0:
                suggestions.append({
                    "tipo": "aproveitamento",
                    "descricao": f"{td['diarist'].nome} está disponível mas sem agendamentos",
                    "acao": "Considerar alocar esta profissional bem avaliada",
                    "impacto": "baixo",
                })

        return suggestions

    def _calculate_potential_savings(
        self,
        schedules: list[DiaristSchedule],
        suggestions: list[dict],
    ) -> Decimal:
        """Calcula economia potencial com otimizações."""
        total_cost = sum(float(s.valor_previsto or 0) for s in schedules)

        # Estimar economia baseada nas sugestões
        savings = Decimal("0")

        for suggestion in suggestions:
            if suggestion["tipo"] == "reducao_custos":
                savings += Decimal(str(total_cost * 0.1))  # 10% de economia estimada
            elif suggestion["tipo"] == "rebalanceamento":
                savings += Decimal(str(total_cost * 0.05))  # 5% de economia

        return savings

    def _estimate_quality_impact(self, suggestions: list[dict]) -> str:
        """Estima impacto das sugestões na qualidade."""
        high_impact = sum(1 for s in suggestions if s.get("impacto") == "alto")
        medium_impact = sum(1 for s in suggestions if s.get("impacto") == "medio")

        if high_impact > 0:
            return "Implementar com cuidado - pode afetar qualidade"
        elif medium_impact > 1:
            return "Impacto moderado - monitorar satisfação"
        else:
            return "Baixo impacto na qualidade"
