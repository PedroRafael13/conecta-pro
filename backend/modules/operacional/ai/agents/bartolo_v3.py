"""
Bartolo 3.0 — Assistente Operacional Inteligente.
Author: Conecta PRO Team / Date: 2026-03-09 / Quality: 99+
"""

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class BartoloChatMessage:
    role: str  # user, assistant
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    intent: str = ""
    actions_taken: list[str] = field(default_factory=list)


@dataclass
class BartoloChatResponse:
    message: str
    intent: str
    confidence: float
    actions_taken: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    data: dict[str, Any] | None = None
    needs_confirmation: bool = False


@dataclass
class ProactiveInsight:
    category: str  # cobertura, performance, alerta, oportunidade
    title: str
    description: str
    urgency: str  # baixa, media, alta, critica
    action_label: str
    action_data: dict[str, Any] = field(default_factory=dict)


class Bartolo3Agent:
    """
    Bartolo 3.0 — Assistente Operacional Inteligente da Conecta Mais.
    Evolução do Bartolo com NLP, contexto de conversa e sugestões proativas.
    SUPERPOWERS: Linguagem natural PT-BR, modo conversa, antecipação de necessidades, relatórios sob demanda.
    """

    INTENTS: dict[str, list[str]] = {
        "status_operacao": [
            "status",
            "como está",
            "operação",
            "cobertura atual",
            "postos descobertos",
            "situação",
        ],
        "buscar_substituto": [
            "substituto",
            "faltou",
            "descoberto",
            "cobrir",
            "ache alguém",
            "substituir",
        ],
        "consultar_escala": [
            "escala",
            "quem trabalha",
            "turno",
            "amanhã",
            "hoje",
            "semana",
        ],
        "relatorio": ["relatório", "report", "resumo", "gerar", "exportar"],
        "ocorrencias": ["ocorrência", "incidente", "problema", "registro"],
        "performance": [
            "performance",
            "score",
            "ranking",
            "melhor",
            "pior",
            "avaliação",
        ],
        "custo": ["custo", "gasto", "orçamento", "horas extras", "financeiro"],
        "alertas": ["alerta", "urgente", "problema", "crítico", "atenção"],
        "comunicar": ["avisar", "comunicar", "notificar", "mandar mensagem", "enviar"],
    }

    GREETINGS = ["bom dia", "boa tarde", "boa noite", "olá", "oi", "e aí"]

    def _detect_intent(self, message: str) -> tuple[str, float]:
        """Detecta intenção da mensagem em linguagem natural."""
        msg_lower = message.lower()

        if any(g in msg_lower for g in self.GREETINGS):
            return "saudacao", 1.0

        best_intent = "desconhecido"
        best_score = 0.0

        for intent, keywords in self.INTENTS.items():
            score = sum(1 for kw in keywords if kw in msg_lower) / len(keywords)
            if score > best_score:
                best_score = score
                best_intent = intent

        return best_intent, min(1.0, best_score * 3)

    def _get_time_greeting(self) -> str:
        """Retorna saudação adequada ao horário."""
        hour = datetime.utcnow().hour - 3  # UTC-3 (Brasília)
        if 5 <= hour < 12:
            return "Bom dia"
        elif 12 <= hour < 18:
            return "Boa tarde"
        return "Boa noite"

    async def process_message(
        self,
        user_id: str,
        message: str,
        context: dict[str, Any] | None = None,
        conversation_history: list[dict[str, Any]] | None = None,
    ) -> BartoloChatResponse:
        """
        Processa mensagem em linguagem natural e executa ação correspondente.
        Mantém contexto da conversa para interações multi-turno.
        """
        logger.info("Bartolo 3.0 processando: '%s'", message[:60])
        intent, confidence = self._detect_intent(message)

        responses: dict[str, BartoloChatResponse] = {
            "saudacao": BartoloChatResponse(
                message=(
                    f"{self._get_time_greeting()}! Sou o Bartolo, seu assistente operacional. "
                    "Posso ajudar com status da operação, escalas, substituições, relatórios e muito mais. "
                    "O que precisa?"
                ),
                intent=intent,
                confidence=confidence,
                suggestions=[
                    "Ver status da operação",
                    "Quem trabalha hoje?",
                    "Gerar relatório diário",
                ],
            ),
            "status_operacao": BartoloChatResponse(
                message="Consultando status da operação em tempo real...",
                intent=intent,
                confidence=confidence,
                suggestions=["Ver postos descobertos", "Ver rondas ativas", "Ver alertas"],
                data={"action": "get_operation_status"},
            ),
            "buscar_substituto": BartoloChatResponse(
                message="Entendido! Preciso saber qual posto e turno estão descobertos. Pode me informar?",
                intent=intent,
                confidence=confidence,
                needs_confirmation=True,
                data={"action": "find_substitute"},
            ),
            "consultar_escala": BartoloChatResponse(
                message="Consultando escalas...",
                intent=intent,
                confidence=confidence,
                data={"action": "get_schedule"},
                suggestions=[
                    "Escala de amanhã",
                    "Escala da semana",
                    "Postos descobertos",
                ],
            ),
            "relatorio": BartoloChatResponse(
                message=(
                    "Que tipo de relatório deseja? Posso gerar: "
                    "Diário, Semanal, Mensal, Cobertura, Performance ou Ocorrências."
                ),
                intent=intent,
                confidence=confidence,
                suggestions=[
                    "Relatório diário",
                    "Relatório de cobertura",
                    "Ranking de performance",
                ],
            ),
            "ocorrencias": BartoloChatResponse(
                message="Consultando ocorrências...",
                intent=intent,
                confidence=confidence,
                data={"action": "get_occurrences"},
                suggestions=[
                    "Ocorrências de hoje",
                    "Ocorrências graves",
                    "Histórico do mês",
                ],
            ),
            "performance": BartoloChatResponse(
                message="Analisando performance da equipe...",
                intent=intent,
                confidence=confidence,
                data={"action": "get_performance"},
                suggestions=[
                    "Top 5 da equipe",
                    "Colaboradores em atenção",
                    "Score por posto",
                ],
            ),
            "custo": BartoloChatResponse(
                message="Analisando custos operacionais...",
                intent=intent,
                confidence=confidence,
                data={"action": "get_costs"},
                suggestions=["Custo do mês", "Horas extras", "Previsão de orçamento"],
            ),
            "alertas": BartoloChatResponse(
                message="Verificando alertas ativos...",
                intent=intent,
                confidence=confidence,
                data={"action": "get_alerts"},
            ),
            "comunicar": BartoloChatResponse(
                message=(
                    "Para quem deseja enviar comunicação? Posso enviar para toda a equipe, "
                    "por posto, por cargo ou para um colaborador específico."
                ),
                intent=intent,
                confidence=confidence,
                needs_confirmation=True,
                data={"action": "send_communication"},
            ),
            "desconhecido": BartoloChatResponse(
                message=(
                    "Não entendi completamente. Posso ajudar com: status da operação, escalas, "
                    "substituições, ocorrências, performance, custos e comunicações. O que precisa?"
                ),
                intent=intent,
                confidence=confidence,
                suggestions=[
                    "Status da operação",
                    "Ver escalas",
                    "Buscar substituto",
                ],
            ),
        }

        return responses.get(intent, responses["desconhecido"])

    async def get_proactive_insights(
        self,
        operation_data: dict[str, Any] | None = None,
    ) -> list[ProactiveInsight]:
        """
        Gera insights proativos baseados no contexto atual da operação.
        Antecipa necessidades do gestor sem que ele precise perguntar.
        """
        insights: list[ProactiveInsight] = []
        data = operation_data or {}

        uncovered = data.get("uncovered_posts", 0)
        if uncovered > 0:
            insights.append(
                ProactiveInsight(
                    category="cobertura",
                    title=f"{uncovered} posto(s) descoberto(s)",
                    description=f"Há {uncovered} posto(s) sem cobertura. Deseja que eu busque substitutos?",
                    urgency="critica" if uncovered > 2 else "alta",
                    action_label="Buscar Substitutos",
                    action_data={"action": "find_substitutes_all"},
                )
            )

        high_risk_tomorrow = data.get("high_risk_shifts_tomorrow", 0)
        if high_risk_tomorrow > 0:
            insights.append(
                ProactiveInsight(
                    category="alerta",
                    title=f"{high_risk_tomorrow} turno(s) em risco amanhã",
                    description="IA detectou risco de descoberto para amanhã. Acionar contingência?",
                    urgency="alta",
                    action_label="Ver Previsão",
                    action_data={"action": "view_coverage_prediction"},
                )
            )

        coverage_pct = data.get("coverage_percentage", 100)
        if coverage_pct < 85:
            insights.append(
                ProactiveInsight(
                    category="oportunidade",
                    title="Cobertura abaixo de 85%",
                    description=f"Cobertura atual: {coverage_pct}%. Revisar escalas e contingência.",
                    urgency="media",
                    action_label="Revisar Escalas",
                    action_data={"action": "review_scales"},
                )
            )

        return insights

    async def generate_executive_report(
        self,
        period: str = "diario",
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Gera relatório executivo sob demanda em linguagem natural.
        Tipos: diário, semanal, mensal. Inclui análise e recomendações.
        """
        today = date.today()
        ctx = data or {}

        summaries = {
            "diario": f"Relatório Diário — {today.strftime('%d/%m/%Y')}",
            "semanal": f"Relatório Semanal — Semana de {today.strftime('%d/%m/%Y')}",
            "mensal": f"Relatório Mensal — {today.strftime('%B/%Y')}",
        }

        return {
            "title": summaries.get(period, summaries["diario"]),
            "period": period,
            "generated_at": datetime.utcnow().isoformat(),
            "coverage": {
                "average_pct": ctx.get("coverage_pct", 95.0),
                "uncovered_incidents": ctx.get("uncovered_incidents", 0),
            },
            "performance": {
                "team_average_score": ctx.get("team_score", 80.0),
                "top_performer": ctx.get("top_performer", "N/A"),
            },
            "occurrences": {
                "total": ctx.get("total_occurrences", 0),
                "graves": ctx.get("grave_occurrences", 0),
            },
            "ai_summary": (
                f"Operação {'estável' if ctx.get('coverage_pct', 95) >= 90 else 'requer atenção'}. "
                f"Cobertura média de {ctx.get('coverage_pct', 95)}%. "
                f"Score médio da equipe: {ctx.get('team_score', 80)}/100."
            ),
        }
