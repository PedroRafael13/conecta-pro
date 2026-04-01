"""
Service para Pipeline de Vendas com metricas e previsoes.
"""

from datetime import date, datetime, timedelta

from modules.crm.models.opportunity import Opportunity, OpportunityStage
from modules.crm.schemas.opportunity import PipelineForecast


class PipelineService:
    """Service para analise e metricas do pipeline de vendas."""

    # Probabilidades por estagio (usadas para previsao)
    STAGE_PROBABILITIES = {
        OpportunityStage.QUALIFICATION.value: 10,
        OpportunityStage.NEEDS_ANALYSIS.value: 25,
        OpportunityStage.PROPOSAL.value: 50,
        OpportunityStage.NEGOTIATION.value: 75,
        OpportunityStage.CLOSED_WON.value: 100,
        OpportunityStage.CLOSED_LOST.value: 0,
    }

    # Tempo medio por estagio (em dias)
    AVG_STAGE_DURATION = {
        OpportunityStage.QUALIFICATION.value: 7,
        OpportunityStage.NEEDS_ANALYSIS.value: 14,
        OpportunityStage.PROPOSAL.value: 10,
        OpportunityStage.NEGOTIATION.value: 21,
    }

    def calculate_weighted_pipeline(self, opportunities: list[Opportunity]) -> float:
        """
        Calcula o valor ponderado total do pipeline.

        Args:
            opportunities: Lista de opportunities

        Returns:
            Valor ponderado total
        """
        total = 0.0
        for opp in opportunities:
            if opp.is_open:
                total += opp.weighted_value
        return total

    def calculate_win_rate(self, opportunities: list[Opportunity], period_days: int = 90) -> float:
        """
        Calcula a taxa de conversao (win rate) em um periodo.

        Args:
            opportunities: Lista de opportunities
            period_days: Dias para analise

        Returns:
            Win rate em percentual
        """
        cutoff = datetime.utcnow() - timedelta(days=period_days)

        won = 0
        lost = 0

        for opp in opportunities:
            if opp.actual_close_date and opp.updated_at >= cutoff:
                if opp.is_won:
                    won += 1
                elif opp.is_lost:
                    lost += 1

        total = won + lost
        if total == 0:
            return 0.0

        return (won / total) * 100

    def calculate_avg_deal_size(self, opportunities: list[Opportunity]) -> float:
        """
        Calcula o ticket medio de negocios fechados (ganhos).

        Args:
            opportunities: Lista de opportunities

        Returns:
            Ticket medio
        """
        won_values = [opp.value for opp in opportunities if opp.is_won]

        if not won_values:
            return 0.0

        return sum(won_values) / len(won_values)

    def calculate_sales_velocity(self, opportunities: list[Opportunity]) -> float:
        """
        Calcula a velocidade de vendas.

        Formula: (Oportunidades x Win Rate x Ticket Medio) / Ciclo de Vendas

        Args:
            opportunities: Lista de opportunities

        Returns:
            Velocidade de vendas (receita por dia)
        """
        open_count = sum(1 for opp in opportunities if opp.is_open)
        win_rate = self.calculate_win_rate(opportunities) / 100
        avg_deal = self.calculate_avg_deal_size(opportunities)
        avg_cycle = self.calculate_avg_sales_cycle(opportunities)

        if avg_cycle <= 0:
            return 0.0

        return (open_count * win_rate * avg_deal) / avg_cycle

    def calculate_avg_sales_cycle(self, opportunities: list[Opportunity]) -> float:
        """
        Calcula o ciclo medio de vendas (dias ate fechamento).

        Args:
            opportunities: Lista de opportunities

        Returns:
            Ciclo medio em dias
        """
        cycles = []
        for opp in opportunities:
            if opp.actual_close_date and (opp.is_won or opp.is_lost):
                cycles.append(opp.days_in_pipeline)

        if not cycles:
            return 0.0

        return sum(cycles) / len(cycles)

    def get_stage_conversion_rates(self, opportunities: list[Opportunity]) -> dict[str, float]:
        """
        Calcula taxas de conversao entre estagios.

        Args:
            opportunities: Lista de opportunities

        Returns:
            Dict com taxas de conversao por estagio
        """
        stage_order = [
            OpportunityStage.QUALIFICATION.value,
            OpportunityStage.NEEDS_ANALYSIS.value,
            OpportunityStage.PROPOSAL.value,
            OpportunityStage.NEGOTIATION.value,
            OpportunityStage.CLOSED_WON.value,
        ]

        # Contagem por estagio (incluindo os que ja passaram)
        stage_counts: dict[str, int] = dict.fromkeys(stage_order, 0)

        for opp in opportunities:
            current_idx = stage_order.index(opp.stage) if opp.stage in stage_order else -1
            # Conta para todos os estagios ate o atual (ou todos se fechado)
            if opp.is_won:
                for stage in stage_order:
                    stage_counts[stage] += 1
            elif opp.is_lost:
                # Conta ate o estagio onde perdeu
                for i, stage in enumerate(stage_order):
                    if i <= current_idx:
                        stage_counts[stage] += 1
            else:
                # Conta ate o estagio atual
                for i, stage in enumerate(stage_order):
                    if i <= current_idx:
                        stage_counts[stage] += 1

        # Calcula conversao entre estagios
        conversions = {}
        for i in range(len(stage_order) - 1):
            current = stage_order[i]
            next_stage = stage_order[i + 1]
            current_count = stage_counts.get(current, 0)
            next_count = stage_counts.get(next_stage, 0)

            if current_count > 0:
                rate = (next_count / current_count) * 100
            else:
                rate = 0.0

            conversions[f"{current}_to_{next_stage}"] = round(rate, 2)

        return conversions

    def forecast_revenue(
        self,
        opportunities: list[Opportunity],
        months_ahead: int = 3,
    ) -> list[PipelineForecast]:
        """
        Gera previsao de receita para os proximos meses.

        Args:
            opportunities: Lista de opportunities
            months_ahead: Numero de meses para prever

        Returns:
            Lista de previsoes por mes
        """
        forecasts = []
        today = date.today()

        for month_offset in range(months_ahead):
            # Determinar mes/ano
            target_month = today.month + month_offset
            target_year = today.year

            while target_month > 12:
                target_month -= 12
                target_year += 1

            period = f"{target_year}-{target_month:02d}"

            # Filtrar opportunities com previsao de fechamento nesse mes
            month_opps = [
                opp
                for opp in opportunities
                if opp.is_open
                and opp.expected_close_date
                and opp.expected_close_date.year == target_year
                and opp.expected_close_date.month == target_month
            ]

            if not month_opps:
                forecasts.append(
                    PipelineForecast(
                        period=period,
                        expected_value=0.0,
                        weighted_value=0.0,
                        opportunity_count=0,
                        avg_probability=0.0,
                    )
                )
                continue

            expected = sum(opp.value for opp in month_opps)
            weighted = sum(opp.weighted_value for opp in month_opps)
            avg_prob = sum(opp.probability for opp in month_opps) / len(month_opps)

            forecasts.append(
                PipelineForecast(
                    period=period,
                    expected_value=expected,
                    weighted_value=weighted,
                    opportunity_count=len(month_opps),
                    avg_probability=round(avg_prob, 2),
                )
            )

        return forecasts

    def get_overdue_opportunities(self, opportunities: list[Opportunity]) -> list[Opportunity]:
        """
        Retorna opportunities com prazo vencido.

        Args:
            opportunities: Lista de opportunities

        Returns:
            Lista de opportunities atrasadas
        """
        return [opp for opp in opportunities if opp.is_overdue]

    def get_stagnant_opportunities(
        self,
        opportunities: list[Opportunity],
        days_threshold: int = 30,
    ) -> list[Opportunity]:
        """
        Retorna opportunities estagnadas (sem atividade recente).

        Args:
            opportunities: Lista de opportunities
            days_threshold: Dias sem atividade para considerar estagnado

        Returns:
            Lista de opportunities estagnadas
        """
        cutoff = datetime.utcnow() - timedelta(days=days_threshold)
        return [opp for opp in opportunities if opp.is_open and opp.updated_at < cutoff]

    def calculate_loss_analysis(self, opportunities: list[Opportunity]) -> dict:
        """
        Analisa motivos de perda de negocios.

        Args:
            opportunities: Lista de opportunities

        Returns:
            Dict com analise de perdas
        """
        lost_opps = [opp for opp in opportunities if opp.is_lost]

        if not lost_opps:
            return {
                "total_lost": 0,
                "total_lost_value": 0.0,
                "by_reason": {},
                "top_competitors": [],
            }

        # Por motivo
        by_reason: dict[str, dict] = {}
        for opp in lost_opps:
            reason = opp.loss_reason or "not_specified"
            if reason not in by_reason:
                by_reason[reason] = {"count": 0, "value": 0.0}
            by_reason[reason]["count"] += 1
            by_reason[reason]["value"] += opp.value

        # Top concorrentes
        competitors: dict[str, int] = {}
        for opp in lost_opps:
            if opp.competitor:
                competitors[opp.competitor] = competitors.get(opp.competitor, 0) + 1

        top_competitors = sorted(competitors.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_lost": len(lost_opps),
            "total_lost_value": sum(opp.value for opp in lost_opps),
            "by_reason": by_reason,
            "top_competitors": [{"name": name, "count": count} for name, count in top_competitors],
        }

    def get_health_score(  # pylint: disable=too-many-branches
        self, opportunities: list[Opportunity]
    ) -> dict:
        """
        Calcula score de saude do pipeline.

        Args:
            opportunities: Lista de opportunities

        Returns:
            Dict com score e recomendacoes
        """
        if not opportunities:
            return {
                "score": 0,
                "status": "empty",
                "recommendations": ["Nao ha opportunities no pipeline"],
            }

        recommendations = []
        score = 100

        # Verificar overdue
        overdue = self.get_overdue_opportunities(opportunities)
        overdue_pct = (len(overdue) / len(opportunities)) * 100
        if overdue_pct > 20:
            score -= 20
            recommendations.append(f"{len(overdue)} opportunities com prazo vencido (>20%)")
        elif overdue_pct > 10:
            score -= 10
            recommendations.append(f"{len(overdue)} opportunities com prazo vencido (>10%)")

        # Verificar estagnadas
        stagnant = self.get_stagnant_opportunities(opportunities)
        stagnant_pct = (len(stagnant) / len(opportunities)) * 100
        if stagnant_pct > 30:
            score -= 15
            recommendations.append(f"{len(stagnant)} opportunities estagnadas (>30 dias)")

        # Verificar win rate
        win_rate = self.calculate_win_rate(opportunities)
        if win_rate < 20:
            score -= 15
            recommendations.append(f"Win rate baixo: {win_rate:.1f}%")
        elif win_rate < 30:
            score -= 5
            recommendations.append(f"Win rate abaixo do ideal: {win_rate:.1f}%")

        # Verificar distribuicao de estagios
        open_opps = [opp for opp in opportunities if opp.is_open]
        if open_opps:
            qualification_count = sum(1 for opp in open_opps if opp.stage == OpportunityStage.QUALIFICATION.value)
            qualification_pct = (qualification_count / len(open_opps)) * 100
            if qualification_pct > 50:
                score -= 10
                recommendations.append("Muitas opportunities em Qualification - acelerar qualificacao")

        # Determinar status
        if score >= 80:
            status = "healthy"
        elif score >= 60:
            status = "attention"
        elif score >= 40:
            status = "warning"
        else:  # pragma: no cover
            status = "critical"

        if not recommendations:
            recommendations.append("Pipeline saudavel - manter o ritmo!")

        return {
            "score": max(0, score),
            "status": status,
            "recommendations": recommendations,
        }


# Singleton
pipeline_service = PipelineService()
