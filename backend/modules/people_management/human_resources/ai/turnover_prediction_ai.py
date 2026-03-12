"""IA para Predicao de Turnover com algoritmo heuristico multi-fatorial."""

import logging
from datetime import date
from typing import Any

logger = logging.getLogger(__name__)

# Pesos dos fatores de risco
RISK_FACTOR_WEIGHTS: dict[str, float] = {
    "tenure": 0.15,
    "salary_vs_market": 0.20,
    "overtime_frequency": 0.15,
    "absence_pattern": 0.15,
    "performance_trend": 0.15,
    "manager_changes": 0.10,
    "climate_survey": 0.10,
}

# Acoes de retencao recomendadas por fator
RETENTION_ACTIONS: dict[str, list[str]] = {
    "tenure": [
        "Programa de reconhecimento por tempo de casa",
        "Mentoria com colaboradores senior",
        "Plano de desenvolvimento individual",
    ],
    "salary_vs_market": [
        "Revisao salarial urgente",
        "Analise de pacote de beneficios",
        "Oferta de bonus de retencao",
    ],
    "overtime_frequency": [
        "Redistribuicao de carga de trabalho",
        "Contratacao de reforco para equipe",
        "Avaliacao de escalas e folgas",
    ],
    "absence_pattern": [
        "Reuniao de acompanhamento com gestor",
        "Encaminhamento para programa de saude",
        "Avaliacao de problemas no posto de trabalho",
    ],
    "performance_trend": [
        "Feedback estruturado imediato",
        "Treinamento de reciclagem",
        "Reavaliacao de adequacao ao posto",
    ],
    "manager_changes": [
        "Acompanhamento proximo durante transicao",
        "Reunioes one-on-one mais frequentes",
        "Apresentacao formal ao novo gestor",
    ],
    "climate_survey": [
        "Grupo focal para entender insatisfacao",
        "Acoes de melhoria no ambiente de trabalho",
        "Canal de comunicacao direta com RH",
    ],
}


class TurnoverPredictionAI:
    """Servico de IA para predicao de risco de turnover.

    Analisa multiplos fatores do funcionario para calcular uma
    pontuacao de risco de 0-100, classificar o nivel de risco
    e sugerir acoes de retencao.
    """

    def __init__(self) -> None:
        """Inicializa o servico de predicao."""
        self.weights = RISK_FACTOR_WEIGHTS

    async def predict_turnover_risk(self, employee: dict[str, Any]) -> dict[str, Any]:
        """Prediz o risco de turnover de um funcionario."""
        factors = {}
        alerts = []
        actions = []

        # 1. Tenure Risk (15%)
        tenure_risk = self._analyze_tenure(employee)
        factors["tenure"] = tenure_risk
        if tenure_risk["score"] >= 60:
            alerts.append(tenure_risk["alert"])
            actions.extend(RETENTION_ACTIONS["tenure"][:2])

        # 2. Salary vs Market (20%)
        salary_risk = self._analyze_salary(employee)
        factors["salary_vs_market"] = salary_risk
        if salary_risk["score"] >= 60:
            alerts.append(salary_risk["alert"])
            actions.extend(RETENTION_ACTIONS["salary_vs_market"][:2])

        # 3. Overtime Frequency (15%)
        overtime_risk = self._analyze_overtime(employee)
        factors["overtime_frequency"] = overtime_risk
        if overtime_risk["score"] >= 60:
            alerts.append(overtime_risk["alert"])
            actions.extend(RETENTION_ACTIONS["overtime_frequency"][:2])

        # 4. Absence Pattern (15%)
        absence_risk = self._analyze_absences(employee)
        factors["absence_pattern"] = absence_risk
        if absence_risk["score"] >= 60:
            alerts.append(absence_risk["alert"])
            actions.extend(RETENTION_ACTIONS["absence_pattern"][:2])

        # 5. Performance Trend (15%)
        perf_risk = self._analyze_performance(employee)
        factors["performance_trend"] = perf_risk
        if perf_risk["score"] >= 60:
            alerts.append(perf_risk["alert"])
            actions.extend(RETENTION_ACTIONS["performance_trend"][:2])

        # 6. Manager Changes (10%)
        mgr_risk = self._analyze_manager_changes(employee)
        factors["manager_changes"] = mgr_risk
        if mgr_risk["score"] >= 60:
            alerts.append(mgr_risk["alert"])
            actions.extend(RETENTION_ACTIONS["manager_changes"][:2])

        # 7. Climate Survey (10%)
        climate_risk = self._analyze_climate(employee)
        factors["climate_survey"] = climate_risk
        if climate_risk["score"] >= 60:
            alerts.append(climate_risk["alert"])
            actions.extend(RETENTION_ACTIONS["climate_survey"][:2])

        # Calcular score final ponderado
        risk_score = sum(factors[factor]["score"] * weight for factor, weight in self.weights.items())
        risk_score = round(min(100, max(0, risk_score)), 1)

        risk_level = self._classify_risk(risk_score)
        departure_window = self._predict_departure_window(risk_score, factors)

        # Remover acoes duplicadas mantendo ordem
        unique_actions = list(dict.fromkeys(actions))

        result = {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "factors": factors,
            "alerts": alerts,
            "retention_actions": unique_actions[:6],
            "predicted_departure_window": departure_window,
        }

        logger.info(f"Turnover risk calculado: score={risk_score}, level={risk_level}")
        return result

    @staticmethod
    def _classify_risk(score: float) -> str:
        """Classifica o nivel de risco."""
        if score < 30:
            return "baixo"
        if score < 50:
            return "moderado"
        if score < 70:
            return "alto"
        return "critico"

    @staticmethod
    def _analyze_tenure(employee: dict) -> dict[str, Any]:
        """Analisa risco baseado no tempo de casa.

        Funcionarios com menos de 6 meses ou entre 1-2 anos
        (pico historico de turnover em seguranca) tem risco maior.
        """
        hire_date = employee.get("hire_date")
        has_career_plan = employee.get("has_career_plan", False)
        last_promotion = employee.get("last_promotion_date")

        if not hire_date:
            return {"score": 50, "detail": "Data de admissao nao informada", "alert": ""}

        if isinstance(hire_date, str):
            hire_date = date.fromisoformat(hire_date)

        tenure_days = (date.today() - hire_date).days
        tenure_months = tenure_days / 30

        score = 0.0
        detail = f"Tempo de casa: {tenure_months:.0f} meses"

        if tenure_months < 3:
            score = 70.0
            detail += " - Periodo de adaptacao (alto risco)"
        elif tenure_months < 6:
            score = 60.0
            detail += " - Periodo critico inicial"
        elif tenure_months < 12:
            score = 40.0
            detail += " - Primeiro ano"
        elif tenure_months < 24:
            score = 55.0
            detail += " - Pico historico de turnover no setor"
        elif tenure_months < 36:
            score = 35.0
            detail += " - Estabilizando"
        else:
            score = 20.0
            detail += " - Funcionario estavel"

        # Reduzir risco se tem plano de carreira
        if has_career_plan:
            score = max(0, score - 15)
            detail += " (+plano de carreira)"

        # Reduzir risco se teve promocao recente
        if last_promotion:
            if isinstance(last_promotion, str):
                last_promotion = date.fromisoformat(last_promotion)
            months_since_promotion = (date.today() - last_promotion).days / 30
            if months_since_promotion < 12:
                score = max(0, score - 10)
                detail += " (+promocao recente)"

        alert = f"Risco de tenure: {detail}" if score >= 60 else ""
        return {"score": round(score, 1), "detail": detail, "alert": alert}

    @staticmethod
    def _analyze_salary(employee: dict) -> dict[str, Any]:
        """Analisa risco baseado em comparacao salarial com mercado."""
        salary = employee.get("salary")
        market_salary = employee.get("market_salary")

        if not salary or not market_salary:
            return {"score": 40, "detail": "Dados salariais incompletos", "alert": ""}

        salary = float(salary)
        market_salary = float(market_salary)

        if market_salary == 0:
            return {"score": 30, "detail": "Salario de mercado nao definido", "alert": ""}

        ratio = salary / market_salary
        detail = f"Salario: R${salary:.2f} (mercado: R${market_salary:.2f}, ratio: {ratio:.2%})"

        if ratio >= 1.1:
            score = 10.0
            detail += " - Acima do mercado"
        elif ratio >= 1.0:
            score = 20.0
            detail += " - Na media do mercado"
        elif ratio >= 0.9:
            score = 45.0
            detail += " - Ligeiramente abaixo"
        elif ratio >= 0.8:
            score = 70.0
            detail += " - Significativamente abaixo"
        elif ratio >= 0.7:
            score = 85.0
            detail += " - Muito abaixo do mercado"
        else:
            score = 95.0
            detail += " - Criticamente abaixo do mercado"

        alert = f"Alerta salarial: {detail}" if score >= 60 else ""
        return {"score": round(score, 1), "detail": detail, "alert": alert}

    @staticmethod
    def _analyze_overtime(employee: dict) -> dict[str, Any]:
        """Analisa risco baseado em horas extras."""
        overtime = employee.get("overtime_hours_last_3months", 0)
        expected = employee.get("expected_monthly_hours", 220)

        if not overtime:
            return {"score": 15, "detail": "Sem horas extras registradas", "alert": ""}

        # Calcular percentual de horas extras sobre esperado (3 meses)
        overtime_ratio = overtime / (expected * 3) if expected > 0 else 0
        detail = f"Horas extras: {overtime:.0f}h em 3 meses (ratio: {overtime_ratio:.1%})"

        if overtime_ratio <= 0.05:
            score = 10.0
        elif overtime_ratio <= 0.10:
            score = 25.0
        elif overtime_ratio <= 0.15:
            score = 45.0
        elif overtime_ratio <= 0.25:
            score = 65.0
            detail += " - Carga elevada"
        elif overtime_ratio <= 0.35:
            score = 80.0
            detail += " - Carga excessiva"
        else:
            score = 95.0
            detail += " - Risco de burnout"

        alert = f"Alerta de horas extras: {detail}" if score >= 60 else ""
        return {"score": round(score, 1), "detail": detail, "alert": alert}

    @staticmethod
    def _analyze_absences(employee: dict) -> dict[str, Any]:
        """Analisa risco baseado em padroes de ausencia."""
        total_absences = employee.get("absences_last_6months", 0)
        unexcused = employee.get("unexcused_absences", 0)

        detail = f"Faltas 6 meses: {total_absences} (injustificadas: {unexcused})"

        # Peso maior para injustificadas
        weighted_absences = total_absences + unexcused * 2

        if weighted_absences == 0:
            score = 5.0
        elif weighted_absences <= 2:
            score = 15.0
        elif weighted_absences <= 4:
            score = 35.0
        elif weighted_absences <= 6:
            score = 55.0
        elif weighted_absences <= 10:
            score = 75.0
            detail += " - Padrao preocupante"
        else:
            score = 90.0
            detail += " - Padrao critico de ausencias"

        alert = f"Alerta de ausencias: {detail}" if score >= 60 else ""
        return {"score": round(score, 1), "detail": detail, "alert": alert}

    @staticmethod
    def _analyze_performance(employee: dict) -> dict[str, Any]:
        """Analisa risco baseado na tendencia de desempenho.

        Queda consistente de performance e indicador de desengajamento.
        """
        scores = employee.get("performance_scores", [])

        if not scores or len(scores) < 2:
            return {
                "score": 40,
                "detail": "Dados de desempenho insuficientes para tendencia",
                "alert": "",
            }

        # Analisar tendencia (ultimos vs anteriores)
        recent = scores[-1]
        previous_avg = sum(scores[:-1]) / len(scores[:-1])
        trend = recent - previous_avg
        avg_score = sum(scores) / len(scores)

        detail = f"Score atual: {recent:.1f}, media anterior: {previous_avg:.1f}, tendencia: {trend:+.1f}"

        # Score baseado em tendencia e nivel absoluto
        if trend >= 5:
            score = 10.0
            detail += " - Tendencia positiva"
        elif trend >= 0:
            score = 20.0
            detail += " - Estavel"
        elif trend >= -5:
            score = 40.0
            detail += " - Leve queda"
        elif trend >= -10:
            score = 60.0
            detail += " - Queda significativa"
        elif trend >= -20:
            score = 80.0
            detail += " - Queda acentuada (desengajamento)"
        else:
            score = 95.0
            detail += " - Queda drastica"

        # Ajuste se nivel absoluto e baixo
        if avg_score < 40:
            score = min(100, score + 15)
            detail += " (desempenho geral baixo)"

        alert = f"Alerta de desempenho: {detail}" if score >= 60 else ""
        return {"score": round(score, 1), "detail": detail, "alert": alert}

    @staticmethod
    def _analyze_manager_changes(employee: dict) -> dict[str, Any]:
        """Analisa risco baseado em trocas de gestor.

        Trocas frequentes de gestor desestabilizam o funcionario.
        """
        changes = employee.get("manager_changes_last_year", 0)
        detail = f"Trocas de gestor no ultimo ano: {changes}"

        if changes == 0:
            score = 5.0
        elif changes == 1:
            score = 25.0
        elif changes == 2:
            score = 55.0
            detail += " - Instabilidade moderada"
        elif changes == 3:
            score = 75.0
            detail += " - Alta rotatividade de gestao"
        else:
            score = 90.0
            detail += " - Instabilidade critica de gestao"

        alert = f"Alerta de gestao: {detail}" if score >= 60 else ""
        return {"score": round(score, 1), "detail": detail, "alert": alert}

    @staticmethod
    def _analyze_climate(employee: dict) -> dict[str, Any]:
        """Analisa risco baseado na pesquisa de clima."""
        climate_score = employee.get("climate_score")

        if climate_score is None:
            return {
                "score": 45,
                "detail": "Sem resposta em pesquisa de clima",
                "alert": "",
            }

        climate_score = float(climate_score)
        detail = f"Score de clima: {climate_score:.1f}/100"

        # Inverter: clima alto = risco baixo
        if climate_score >= 80:
            score = 10.0
            detail += " - Satisfeito"
        elif climate_score >= 65:
            score = 25.0
            detail += " - Razoavelmente satisfeito"
        elif climate_score >= 50:
            score = 50.0
            detail += " - Insatisfacao moderada"
        elif climate_score >= 35:
            score = 70.0
            detail += " - Insatisfeito"
        else:
            score = 90.0
            detail += " - Muito insatisfeito"

        alert = f"Alerta de clima: {detail}" if score >= 60 else ""
        return {"score": round(score, 1), "detail": detail, "alert": alert}

    @staticmethod
    def _predict_departure_window(risk_score: float, factors: dict[str, Any]) -> dict[str, Any]:
        """Estima janela provavel de desligamento."""
        if risk_score < 30:
            return {
                "probability": "baixa",
                "window": "Nao ha indicacao de desligamento proximo",
                "estimated_months": None,
            }
        elif risk_score < 50:
            return {
                "probability": "moderada",
                "window": "6 a 12 meses",
                "estimated_months": 9,
            }
        elif risk_score < 70:
            return {
                "probability": "alta",
                "window": "3 a 6 meses",
                "estimated_months": 4,
            }
        else:
            # Verificar fatores criticos para refinar
            critical_factors = [f for f, data in factors.items() if data.get("score", 0) >= 80]
            if len(critical_factors) >= 3:
                return {
                    "probability": "muito_alta",
                    "window": "1 a 2 meses",
                    "estimated_months": 1,
                    "critical_factors": critical_factors,
                }
            return {
                "probability": "muito_alta",
                "window": "1 a 3 meses",
                "estimated_months": 2,
                "critical_factors": critical_factors,
            }
