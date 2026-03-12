"""
IA para Analise de Clima Organizacional.

Implementa algoritmos de analise de resultados de pesquisas
de clima, deteccao de tendencias e sugestao de acoes.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Dimensoes de clima avaliadas
CLIMATE_DIMENSIONS: list[str] = [
    "satisfacao",
    "lideranca",
    "operacional",
    "carreira",
    "comunicacao",
    "reconhecimento",
    "seguranca_trabalho",
]

# Acoes recomendadas por dimensao com baixa pontuacao
DIMENSION_ACTIONS: dict[str, list[str]] = {
    "satisfacao": [
        "Realizar grupos focais para identificar causas de insatisfacao",
        "Programa de melhoria de qualidade de vida no trabalho",
        "Revisar politica de beneficios",
    ],
    "lideranca": [
        "Treinamento de lideranca para gestores",
        "Implementar programa de feedback 360",
        "Reunioes periodicas one-on-one gestor-funcionario",
    ],
    "operacional": [
        "Avaliar e melhorar condicoes de trabalho nos postos",
        "Revisar escalas de trabalho e adequacao de cargas",
        "Investir em equipamentos e infraestrutura",
    ],
    "carreira": [
        "Implementar planos de carreira formais",
        "Criar programa de promocao interna",
        "Treinamentos de desenvolvimento profissional",
    ],
    "comunicacao": [
        "Criar canais de comunicacao direta com a diretoria",
        "Reunioes mensais de alinhamento por equipe",
        "App de comunicacao interna",
    ],
    "reconhecimento": [
        "Programa de reconhecimento mensal (funcionario destaque)",
        "Politica de bonus por desempenho",
        "Celebracao de marcos (tempo de casa, metas alcancadas)",
    ],
    "seguranca_trabalho": [
        "Revisao de protocolos de seguranca",
        "Treinamento de seguranca obrigatorio",
        "Canal de denuncias anonimo",
    ],
}


class ClimateAnalysisAI:
    """Servico de IA para analise de clima organizacional.

    Analisa resultados de pesquisas de clima, detecta tendencias
    e sugere acoes de melhoria.
    """

    def __init__(self) -> None:
        """Inicializa o servico de analise de clima."""
        self.dimensions = CLIMATE_DIMENSIONS

    async def analyze_survey_results(self, survey_data: dict[str, Any]) -> dict[str, Any]:
        """Analisa resultados de uma pesquisa de clima.

        Args:
            survey_data: Dados da pesquisa com campos:
                - total_responses (int): Total de respostas
                - total_employees (int): Total de funcionarios
                - dimension_scores (dict[str, float]): Score por dimensao (0-100)
                - responses_by_workplace (dict[str, dict]): Scores por posto
                - responses_by_team (dict[str, dict]): Scores por equipe
                - open_comments (list[str]): Comentarios abertos

        Returns:
            Dicionario com analise geral, destaques, alertas,
            comparativo e recomendacoes.
        """
        dimension_scores = survey_data.get("dimension_scores", {})
        total_responses = survey_data.get("total_responses", 0)
        total_employees = survey_data.get("total_employees", 1)
        responses_by_workplace = survey_data.get("responses_by_workplace", {})

        # Calcular score geral
        if dimension_scores:
            overall_score = sum(dimension_scores.values()) / len(dimension_scores)
        else:
            overall_score = 0.0

        participation_rate = (total_responses / max(total_employees, 1)) * 100

        # Classificar dimensoes
        strong_dimensions = []
        weak_dimensions = []
        critical_dimensions = []

        for dim, score in dimension_scores.items():
            if score >= 75:
                strong_dimensions.append({"dimension": dim, "score": round(score, 1)})
            elif score < 50:
                critical_dimensions.append({"dimension": dim, "score": round(score, 1)})
            elif score < 65:
                weak_dimensions.append({"dimension": dim, "score": round(score, 1)})

        # Identificar postos criticos
        critical_workplaces = []
        for wp_name, wp_data in responses_by_workplace.items():
            wp_score = wp_data.get("overall_score", 0)
            if wp_score < 50:
                critical_workplaces.append(
                    {
                        "workplace": wp_name,
                        "score": round(wp_score, 1),
                        "responses": wp_data.get("response_count", 0),
                    }
                )

        # Gerar alertas
        alerts = []
        if participation_rate < 50:
            alerts.append(
                {
                    "type": "low_participation",
                    "severity": "warning",
                    "message": f"Taxa de participacao baixa: {participation_rate:.1f}%. "
                    f"Resultados podem nao ser representativos.",
                }
            )

        for dim_info in critical_dimensions:
            alerts.append(
                {
                    "type": "critical_dimension",
                    "severity": "critical",
                    "message": f"Dimensao '{dim_info['dimension']}' em nivel critico: {dim_info['score']}/100.",
                }
            )

        for wp in critical_workplaces:
            alerts.append(
                {
                    "type": "critical_workplace",
                    "severity": "high",
                    "message": f"Posto '{wp['workplace']}' com clima critico: {wp['score']}/100.",
                }
            )

        # Classificar satisfacao geral
        if overall_score >= 80:
            satisfaction_level = "excelente"
        elif overall_score >= 65:
            satisfaction_level = "bom"
        elif overall_score >= 50:
            satisfaction_level = "regular"
        elif overall_score >= 35:
            satisfaction_level = "ruim"
        else:
            satisfaction_level = "critico"

        # Analisar comentarios
        comment_analysis = self._analyze_comments(survey_data.get("open_comments", []))

        return {
            "overall_score": round(overall_score, 1),
            "satisfaction_level": satisfaction_level,
            "participation_rate": round(participation_rate, 1),
            "total_responses": total_responses,
            "total_employees": total_employees,
            "dimension_scores": {k: round(v, 1) for k, v in dimension_scores.items()},
            "strong_dimensions": strong_dimensions,
            "weak_dimensions": weak_dimensions,
            "critical_dimensions": critical_dimensions,
            "critical_workplaces": critical_workplaces,
            "alerts": alerts,
            "comment_analysis": comment_analysis,
        }

    async def detect_trends(self, historical_data: list[dict[str, Any]]) -> dict[str, Any]:
        """Detecta tendencias em series historicas de pesquisas de clima.

        Args:
            historical_data: Lista de pesquisas ordenadas por data, cada uma com:
                - date (str): Data da pesquisa
                - overall_score (float): Score geral
                - dimension_scores (dict[str, float]): Scores por dimensao

        Returns:
            Dicionario com tendencias gerais e por dimensao.
        """
        if len(historical_data) < 2:
            return {
                "has_enough_data": False,
                "message": "Dados historicos insuficientes (minimo 2 pesquisas).",
                "trends": {},
            }

        # Tendencia geral
        scores = [d.get("overall_score", 0) for d in historical_data]
        overall_trend = self._calculate_trend(scores)

        # Tendencia por dimensao
        dimension_trends = {}
        all_dimensions = set()
        for data_point in historical_data:
            all_dimensions.update(data_point.get("dimension_scores", {}).keys())

        for dim in all_dimensions:
            dim_scores = [
                d.get("dimension_scores", {}).get(dim)
                for d in historical_data
                if d.get("dimension_scores", {}).get(dim) is not None
            ]
            if len(dim_scores) >= 2:
                dimension_trends[dim] = self._calculate_trend(dim_scores)

        # Identificar dimensoes com tendencia preocupante
        declining_dimensions = [
            {"dimension": dim, **trend} for dim, trend in dimension_trends.items() if trend["direction"] == "declining"
        ]

        improving_dimensions = [
            {"dimension": dim, **trend} for dim, trend in dimension_trends.items() if trend["direction"] == "improving"
        ]

        return {
            "has_enough_data": True,
            "overall_trend": overall_trend,
            "dimension_trends": dimension_trends,
            "declining_dimensions": declining_dimensions,
            "improving_dimensions": improving_dimensions,
            "data_points": len(historical_data),
        }

    async def suggest_actions(self, analysis: dict[str, Any]) -> list[dict[str, Any]]:
        """Sugere acoes de melhoria baseadas na analise de clima.

        Args:
            analysis: Resultado de analyze_survey_results.

        Returns:
            Lista de acoes recomendadas com prioridade.
        """
        actions = []
        priority_counter = 1

        # Acoes para dimensoes criticas (prioridade maxima)
        for dim_info in analysis.get("critical_dimensions", []):
            dim = dim_info["dimension"]
            dim_actions = DIMENSION_ACTIONS.get(dim, [])
            for action_text in dim_actions[:2]:
                actions.append(
                    {
                        "priority": priority_counter,
                        "dimension": dim,
                        "action": action_text,
                        "urgency": "imediata",
                        "expected_impact": "alto",
                        "score_reference": dim_info["score"],
                    }
                )
                priority_counter += 1

        # Acoes para dimensoes fracas (prioridade media)
        for dim_info in analysis.get("weak_dimensions", []):
            dim = dim_info["dimension"]
            dim_actions = DIMENSION_ACTIONS.get(dim, [])
            for action_text in dim_actions[:1]:
                actions.append(
                    {
                        "priority": priority_counter,
                        "dimension": dim,
                        "action": action_text,
                        "urgency": "curto_prazo",
                        "expected_impact": "medio",
                        "score_reference": dim_info["score"],
                    }
                )
                priority_counter += 1

        # Acoes para postos criticos
        for wp in analysis.get("critical_workplaces", []):
            actions.append(
                {
                    "priority": priority_counter,
                    "dimension": "workplace_specific",
                    "action": f"Intervencao direta no posto '{wp['workplace']}': "
                    f"reuniao com equipe, avaliacao de condicoes, plano de acao local.",
                    "urgency": "imediata",
                    "expected_impact": "alto",
                    "score_reference": wp["score"],
                }
            )
            priority_counter += 1

        # Acao geral de participacao
        participation_rate = analysis.get("participation_rate", 100)
        if participation_rate < 60:
            actions.append(
                {
                    "priority": priority_counter,
                    "dimension": "participacao",
                    "action": "Campanha de engajamento para proxima pesquisa de clima. "
                    "Garantir anonimato e comunicar resultados e acoes tomadas.",
                    "urgency": "medio_prazo",
                    "expected_impact": "medio",
                    "score_reference": participation_rate,
                }
            )

        return actions

    @staticmethod
    def _calculate_trend(scores: list[float]) -> dict[str, Any]:
        """Calcula tendencia de uma serie de scores.

        Args:
            scores: Lista de scores ordenados cronologicamente.

        Returns:
            Dicionario com direcao, variacao e detalhes.
        """
        if len(scores) < 2:
            return {"direction": "insufficient_data", "variation": 0, "detail": ""}

        first = scores[0]
        last = scores[-1]
        variation = last - first

        # Media movel simples dos ultimos 2 pontos vs anteriores
        recent_avg = sum(scores[-2:]) / min(2, len(scores))
        older_avg = sum(scores[:-1]) / max(1, len(scores) - 1)
        trend_diff = recent_avg - older_avg

        if trend_diff > 3:
            direction = "improving"
            detail = f"Melhoria de {variation:+.1f} pontos no periodo"
        elif trend_diff < -3:
            direction = "declining"
            detail = f"Queda de {abs(variation):.1f} pontos no periodo"
        else:
            direction = "stable"
            detail = f"Estavel (variacao de {variation:+.1f} pontos)"

        return {
            "direction": direction,
            "variation": round(variation, 1),
            "current_score": round(last, 1),
            "initial_score": round(first, 1),
            "detail": detail,
        }

    @staticmethod
    def _analyze_comments(comments: list[str]) -> dict[str, Any]:
        """Analisa comentarios abertos da pesquisa.

        Usa heuristicas de palavras-chave para categorizar sentimentos
        e identificar temas recorrentes.

        Args:
            comments: Lista de comentarios em texto livre.

        Returns:
            Dicionario com categorias de sentimento e temas.
        """
        if not comments:
            return {
                "total_comments": 0,
                "sentiment": {"positive": 0, "neutral": 0, "negative": 0},
                "themes": [],
            }

        positive_keywords = {
            "bom",
            "otimo",
            "excelente",
            "satisfeito",
            "gosto",
            "feliz",
            "orgulho",
            "bem",
            "legal",
            "parabens",
            "melhorou",
            "obrigado",
        }
        negative_keywords = {
            "ruim",
            "pessimo",
            "insatisfeito",
            "problema",
            "reclamacao",
            "falta",
            "nao",
            "nunca",
            "demora",
            "desrespeito",
            "desorganizado",
            "abandono",
            "esquecido",
            "injusto",
            "salario",
            "pagar",
            "atraso",
        }

        theme_keywords = {
            "salario": {"salario", "pagamento", "dinheiro", "remuneracao", "vale", "beneficio"},
            "lideranca": {"gestor", "supervisor", "chefe", "lider", "encarregado", "coordenador"},
            "escala": {"escala", "folga", "horario", "hora", "plantao", "turno"},
            "equipamento": {"equipamento", "radio", "uniforme", "material", "farda", "colete"},
            "treinamento": {"treinamento", "capacitacao", "curso", "aprender"},
            "comunicacao": {"comunicacao", "informacao", "aviso", "reuniao"},
            "seguranca": {"seguranca", "risco", "perigo", "medo"},
        }

        positive_count = 0
        negative_count = 0
        neutral_count = 0
        theme_counts: dict[str, int] = dict.fromkeys(theme_keywords, 0)

        for comment in comments:
            words = set(comment.lower().split())
            has_positive = bool(words & positive_keywords)
            has_negative = bool(words & negative_keywords)

            if has_positive and not has_negative:
                positive_count += 1
            elif has_negative:
                negative_count += 1
            else:
                neutral_count += 1

            for theme, keywords in theme_keywords.items():
                if words & keywords:
                    theme_counts[theme] += 1

        # Top temas mencionados
        themes = sorted(
            [
                {"theme": t, "mentions": c, "percentage": round(c / len(comments) * 100, 1)}
                for t, c in theme_counts.items()
                if c > 0
            ],
            key=lambda x: x["mentions"],
            reverse=True,
        )

        return {
            "total_comments": len(comments),
            "sentiment": {
                "positive": positive_count,
                "neutral": neutral_count,
                "negative": negative_count,
            },
            "sentiment_ratio": {
                "positive_pct": round(positive_count / len(comments) * 100, 1),
                "neutral_pct": round(neutral_count / len(comments) * 100, 1),
                "negative_pct": round(negative_count / len(comments) * 100, 1),
            },
            "themes": themes[:5],
        }
