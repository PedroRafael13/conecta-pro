"""Service de IA para classificação de ocorrências."""

import logging
import re
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.occurrences.models.category import OccurrenceCategory
from modules.occurrences.models.occurrence import (
    Occurrence,
    OccurrencePriority,
    OccurrenceType,
)

logger = logging.getLogger(__name__)


class ClassificationAIService:
    """Service de IA para classificação e análise de ocorrências."""

    def __init__(self, session: AsyncSession):
        """Inicializa o service."""
        self.session = session

    # Keywords para classificação por tipo
    TYPE_KEYWORDS = {
        OccurrenceType.RECLAMACAO: [
            "reclamação", "reclamo", "insatisfeito", "problema", "péssimo",
            "ruim", "horrível", "absurdo", "demora", "atraso", "não funciona",
        ],
        OccurrenceType.SUGESTAO: [
            "sugestão", "sugiro", "poderia", "seria bom", "melhoria",
            "proposta", "ideia", "implementar", "considerar",
        ],
        OccurrenceType.ELOGIO: [
            "elogio", "parabéns", "excelente", "ótimo", "maravilhoso",
            "obrigado", "agradecimento", "satisfeito", "bom trabalho",
        ],
        OccurrenceType.INCIDENTE: [
            "incidente", "acidente", "emergência", "urgente", "perigo",
            "ferido", "quebrou", "caiu", "bateu", "explosão",
        ],
        OccurrenceType.DENUNCIA: [
            "denúncia", "denuncio", "irregularidade", "ilegal", "fraude",
            "roubo", "furto", "assédio", "ameaça", "violação",
        ],
        OccurrenceType.SOLICITACAO: [
            "solicito", "gostaria", "preciso", "necessito", "requeiro",
            "pedido", "favor", "possível", "autorização",
        ],
        OccurrenceType.MANUTENCAO: [
            "manutenção", "conserto", "reparo", "vazamento", "quebrado",
            "não funciona", "estragado", "defeito", "lâmpada", "torneira",
        ],
        OccurrenceType.SEGURANCA: [
            "segurança", "invasão", "arrombamento", "suspeito", "câmera",
            "portaria", "acesso", "alarme", "cerca", "vigia",
        ],
        OccurrenceType.BARULHO: [
            "barulho", "ruído", "som alto", "música", "festa", "gritaria",
            "latido", "cachorro", "perturbação", "silêncio",
        ],
        OccurrenceType.ANIMAL: [
            "animal", "cachorro", "gato", "pet", "bicho", "pombo",
            "rato", "inseto", "barata", "formiga", "mosquito",
        ],
        OccurrenceType.VEICULO: [
            "veículo", "carro", "moto", "estacionamento", "vaga", "garagem",
            "placa", "multa", "guincho", "reboque",
        ],
        OccurrenceType.AREA_COMUM: [
            "área comum", "salão de festas", "piscina", "academia", "churrasqueira",
            "playground", "jardim", "hall", "elevador", "escada",
        ],
    }

    # Keywords para prioridade
    PRIORITY_KEYWORDS = {
        OccurrencePriority.CRITICA: [
            "urgentíssimo", "crítico", "vida", "morte", "emergência médica",
            "incêndio", "desabamento", "explosão", "evacuação",
        ],
        OccurrencePriority.URGENTE: [
            "urgente", "imediato", "agora", "rápido", "pressa",
            "não pode esperar", "hoje", "já", "prioridade máxima",
        ],
        OccurrencePriority.ALTA: [
            "importante", "prioritário", "grave", "sério", "preocupante",
            "risco", "perigo", "atenção especial",
        ],
        OccurrencePriority.MEDIA: [
            "normal", "regular", "quando possível", "moderado",
        ],
        OccurrencePriority.BAIXA: [
            "baixa prioridade", "não urgente", "pode esperar",
            "quando der", "sem pressa", "futuro",
        ],
    }

    # Sentimentos
    SENTIMENT_KEYWORDS = {
        "positivo": [
            "obrigado", "agradeço", "satisfeito", "feliz", "contente",
            "ótimo", "excelente", "parabéns", "bom", "maravilhoso",
        ],
        "negativo": [
            "insatisfeito", "irritado", "frustrado", "decepcionado", "revoltado",
            "péssimo", "horrível", "absurdo", "inaceitável", "vergonha",
        ],
        "neutro": [],
    }

    async def classify_occurrence(self, title: str, description: str) -> dict:
        """Classifica uma ocorrência baseado no texto."""
        text = f"{title} {description}".lower()

        # Classificar tipo
        suggested_type = self._classify_type(text)

        # Classificar prioridade
        suggested_priority, priority_score = self._classify_priority(text)

        # Analisar sentimento
        sentiment = self._analyze_sentiment(text)

        # Extrair palavras-chave
        keywords = self._extract_keywords(text)

        # Sugerir categoria
        suggested_category = await self._suggest_category(text, suggested_type)

        cat_id = suggested_category.get("id") if suggested_category else None
        cat_name = suggested_category.get("name") if suggested_category else None
        conf = self._calculate_confidence(text, suggested_type, suggested_priority)

        return {
            "suggested_type": suggested_type.value if suggested_type else None,
            "suggested_priority": suggested_priority.value,
            "priority_score": priority_score,
            "sentiment": sentiment,
            "keywords": keywords,
            "suggested_category_id": cat_id,
            "suggested_category_name": cat_name,
            "confidence": conf,
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }

    def _classify_type(self, text: str) -> Optional[OccurrenceType]:
        """Classifica o tipo da ocorrência."""
        scores = {}

        for occ_type, keywords in self.TYPE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[occ_type] = score

        if not scores:
            return OccurrenceType.OUTRO

        return max(scores, key=scores.get)

    def _classify_priority(self, text: str) -> tuple[OccurrencePriority, float]:
        """Classifica a prioridade da ocorrência."""
        scores = {
            OccurrencePriority.CRITICA: 0,
            OccurrencePriority.URGENTE: 0,
            OccurrencePriority.ALTA: 0,
            OccurrencePriority.MEDIA: 0,
            OccurrencePriority.BAIXA: 0,
        }

        # Contar keywords
        for priority, keywords in self.PRIORITY_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    scores[priority] += 1

        # Adicionar pontos por indicadores de urgência
        if "!" in text:
            scores[OccurrencePriority.URGENTE] += text.count("!") * 0.5
        if text.isupper():
            scores[OccurrencePriority.ALTA] += 1

        # Calcular score normalizado (0-100)
        max_score = max(scores.values()) if any(scores.values()) else 0
        total_score = sum(scores.values())

        if total_score == 0:
            return OccurrencePriority.MEDIA, 50.0

        # Determinar prioridade
        priority = max(scores, key=scores.get)

        # Score baseado na prioridade
        priority_scores = {
            OccurrencePriority.CRITICA: 100,
            OccurrencePriority.URGENTE: 80,
            OccurrencePriority.ALTA: 60,
            OccurrencePriority.MEDIA: 40,
            OccurrencePriority.BAIXA: 20,
        }

        base_score = priority_scores[priority]
        # Ajustar baseado na força das keywords
        adjustment = min(max_score * 5, 15)
        final_score = min(base_score + adjustment, 100)

        return priority, final_score

    def _analyze_sentiment(self, text: str) -> str:
        """Analisa o sentimento do texto."""
        positive_count = sum(1 for kw in self.SENTIMENT_KEYWORDS["positivo"] if kw in text)
        negative_count = sum(1 for kw in self.SENTIMENT_KEYWORDS["negativo"] if kw in text)

        if positive_count > negative_count:
            return "positivo"
        if negative_count > positive_count:
            return "negativo"
        return "neutro"

    def _extract_keywords(self, text: str) -> list[str]:
        """Extrai palavras-chave do texto."""
        # Remover pontuação e normalizar
        clean_text = re.sub(r"[^\w\s]", " ", text)
        words = clean_text.split()

        # Stopwords em português
        stopwords = {
            "o", "a", "os", "as", "um", "uma", "uns", "umas", "de", "da", "do",
            "das", "dos", "em", "na", "no", "nas", "nos", "por", "para", "com",
            "sem", "sob", "sobre", "entre", "que", "qual", "quais", "como",
            "quando", "onde", "porque", "e", "ou", "mas", "se", "não", "sim",
            "muito", "pouco", "mais", "menos", "bem", "mal", "já", "ainda",
            "sempre", "nunca", "também", "só", "apenas", "mesmo", "próprio",
            "todo", "toda", "todos", "todas", "este", "esta", "estes", "estas",
            "esse", "essa", "esses", "essas", "aquele", "aquela", "aqueles",
            "aquelas", "isto", "isso", "aquilo", "meu", "minha", "meus", "minhas",
            "seu", "sua", "seus", "suas", "nosso", "nossa", "nossos", "nossas",
            "estar", "ser", "ter", "haver", "fazer", "poder", "dever", "ir",
            "vir", "ver", "dar", "saber", "querer", "dizer", "ficar",
        }

        # Filtrar palavras
        keywords = []
        for word in words:
            if len(word) > 3 and word not in stopwords:
                keywords.append(word)

        # Retornar top 10 únicas
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
                if len(unique_keywords) >= 10:
                    break

        return unique_keywords

    async def _suggest_category(
        self, text: str, _occurrence_type: Optional[OccurrenceType]
    ) -> Optional[dict]:
        """Sugere categoria baseado no texto e tipo."""
        # Buscar categorias ativas
        result = await self.session.execute(
            select(OccurrenceCategory).where(OccurrenceCategory.is_active.is_(True))
        )
        categories = list(result.scalars().all())

        if not categories:
            return None

        # Pontuar categorias
        scores = {}
        for cat in categories:
            score = 0
            cat_name = cat.name.lower()
            cat_desc = (cat.description or "").lower()

            # Match no nome
            if cat_name in text:
                score += 10
            for word in cat_name.split():
                if word in text:
                    score += 2

            # Match na descrição
            if cat_desc:
                for word in cat_desc.split():
                    if len(word) > 3 and word in text:
                        score += 1

            if score > 0:
                scores[cat.id] = {"category": cat, "score": score}

        if not scores:
            return None

        # Retornar categoria com maior score
        best = max(scores.values(), key=lambda x: x["score"])
        return {
            "id": str(best["category"].id),
            "name": best["category"].name,
            "score": best["score"],
        }

    def _calculate_confidence(
        self,
        text: str,
        suggested_type: Optional[OccurrenceType],
        suggested_priority: OccurrencePriority,
    ) -> float:
        """Calcula nível de confiança da classificação."""
        confidence = 50.0  # Base

        # Texto mais longo = mais confiança
        word_count = len(text.split())
        if word_count > 20:
            confidence += 10
        elif word_count > 10:
            confidence += 5

        # Tipo identificado = mais confiança
        if suggested_type and suggested_type != OccurrenceType.OUTRO:
            confidence += 20

        # Prioridade não-média = mais confiança
        if suggested_priority != OccurrencePriority.MEDIA:
            confidence += 10

        # Keywords encontradas = mais confiança
        type_keywords_found = 0
        if suggested_type:
            for kw in self.TYPE_KEYWORDS.get(suggested_type, []):
                if kw in text:
                    type_keywords_found += 1
        confidence += min(type_keywords_found * 5, 15)

        return min(confidence, 100.0)

    async def calculate_priority_score(  # pylint: disable=too-many-locals
        self, occurrence_id: str | UUID
    ) -> Optional[dict]:
        """Calcula score de prioridade para uma ocorrência."""
        if isinstance(occurrence_id, str):
            occurrence_id = UUID(occurrence_id)

        result = await self.session.execute(
            select(Occurrence).where(Occurrence.id == occurrence_id)
        )
        occurrence = result.scalar_one_or_none()

        if not occurrence:
            return None

        score = 0.0
        factors = []

        # Fator 1: Prioridade definida (0-30 pontos)
        priority_scores = {
            OccurrencePriority.CRITICA: 30,
            OccurrencePriority.URGENTE: 24,
            OccurrencePriority.ALTA: 18,
            OccurrencePriority.MEDIA: 12,
            OccurrencePriority.BAIXA: 6,
        }
        priority_score = priority_scores.get(occurrence.priority, 12)
        score += priority_score
        factors.append({"factor": "priority", "score": priority_score, "max": 30})

        # Fator 2: Tipo de ocorrência (0-20 pontos)
        type_scores = {
            OccurrenceType.INCIDENTE: 20,
            OccurrenceType.DENUNCIA: 18,
            OccurrenceType.SEGURANCA: 16,
            OccurrenceType.MANUTENCAO: 14,
            OccurrenceType.RECLAMACAO: 12,
            OccurrenceType.SOLICITACAO: 10,
        }
        type_score = type_scores.get(occurrence.occurrence_type, 8)
        score += type_score
        factors.append({"factor": "type", "score": type_score, "max": 20})

        # Fator 3: Tempo aberto (0-20 pontos)
        age_hours = occurrence.age_hours
        if age_hours > 72:
            age_score = 20
        elif age_hours > 48:
            age_score = 16
        elif age_hours > 24:
            age_score = 12
        elif age_hours > 8:
            age_score = 8
        else:
            age_score = 4
        score += age_score
        factors.append({"factor": "age", "score": age_score, "max": 20, "hours": age_hours})

        # Fator 4: SLA (0-15 pontos)
        sla_score = 0
        if occurrence.is_overdue_resolution:
            sla_score = 15
        elif occurrence.is_overdue_response:
            sla_score = 10
        elif occurrence.sla_resolution_deadline:
            # Próximo do deadline
            now = datetime.utcnow()
            if occurrence.sla_resolution_deadline < now + timedelta(hours=4):
                sla_score = 8
            elif occurrence.sla_resolution_deadline < now + timedelta(hours=12):
                sla_score = 5
        score += sla_score
        factors.append({"factor": "sla", "score": sla_score, "max": 15})

        # Fator 5: Escalonamento (0-10 pontos)
        escalation_score = min(occurrence.escalation_level * 5, 10)
        score += escalation_score
        factors.append({"factor": "escalation", "score": escalation_score, "max": 10})

        # Fator 6: Recorrência (0-5 pontos)
        recurrence_score = min(occurrence.recurrence_count * 2.5, 5)
        score += recurrence_score
        factors.append({"factor": "recurrence", "score": recurrence_score, "max": 5})

        # Atualizar score na ocorrência
        occurrence.ai_priority_score = score
        await self.session.flush()

        return {
            "occurrence_id": str(occurrence.id),
            "occurrence_code": occurrence.occurrence_code,
            "priority_score": score,
            "max_score": 100,
            "factors": factors,
            "recommendation": self._get_priority_recommendation(score),
        }

    def _get_priority_recommendation(self, score: float) -> str:
        """Retorna recomendação baseada no score."""
        if score >= 80:
            return "CRÍTICO: Requer atenção imediata. Escalonar se necessário."
        if score >= 60:
            return "ALTO: Priorizar atendimento. Verificar SLA."
        if score >= 40:
            return "MÉDIO: Atender dentro do prazo normal."
        if score >= 20:
            return "BAIXO: Pode ser atendido quando disponível."
        return "MÍNIMO: Sem urgência."

    async def suggest_assignee(self, occurrence_id: str | UUID) -> Optional[dict]:
        """Sugere responsável para a ocorrência."""
        if isinstance(occurrence_id, str):
            occurrence_id = UUID(occurrence_id)

        result = await self.session.execute(
            select(Occurrence).where(Occurrence.id == occurrence_id)
        )
        occurrence = result.scalar_one_or_none()

        if not occurrence:
            return None

        suggestions = []

        # Sugestão 1: Da categoria
        if occurrence.category_id:
            cat_result = await self.session.execute(
                select(OccurrenceCategory).where(OccurrenceCategory.id == occurrence.category_id)
            )
            category = cat_result.scalar_one_or_none()
            if category and category.auto_assign_to_id:
                suggestions.append({
                    "assignee_id": category.auto_assign_to_id,
                    "assignee_name": category.auto_assign_to_name,
                    "reason": f"Responsável padrão da categoria {category.name}",
                    "confidence": 90,
                })

        # Sugestão 2: Por tipo de ocorrência (simulado)
        type_assignees = {
            OccurrenceType.MANUTENCAO: {"id": "manutencao-team", "name": "Equipe de Manutenção"},
            OccurrenceType.SEGURANCA: {"id": "seguranca-team", "name": "Equipe de Segurança"},
            OccurrenceType.BARULHO: {"id": "sindico", "name": "Síndico"},
        }
        if occurrence.occurrence_type in type_assignees:
            assignee = type_assignees[occurrence.occurrence_type]
            suggestions.append({
                "assignee_id": assignee["id"],
                "assignee_name": assignee["name"],
                "reason": f"Responsável por ocorrências de {occurrence.occurrence_type.value}",
                "confidence": 70,
            })

        return {
            "occurrence_id": str(occurrence.id),
            "suggestions": suggestions,
            "best_suggestion": suggestions[0] if suggestions else None,
        }

    async def analyze_trends(  # pylint: disable=too-many-locals
        self, condominium_id: Optional[str] = None, days: int = 30
    ) -> dict:
        """Analisa tendências de ocorrências."""
        date_from = datetime.utcnow() - timedelta(days=days)

        query = select(Occurrence).where(
            Occurrence.created_at >= date_from,
            Occurrence.is_active.is_(True),
        )
        if condominium_id:
            query = query.where(Occurrence.condominium_id == condominium_id)

        result = await self.session.execute(query)
        occurrences = list(result.scalars().all())

        if not occurrences:
            return {
                "period_days": days,
                "total": 0,
                "trends": [],
                "insights": ["Sem ocorrências no período analisado."],
            }

        # Agrupar por dia
        by_day = {}
        for occ in occurrences:
            day_key = occ.created_at.strftime("%Y-%m-%d")
            if day_key not in by_day:
                by_day[day_key] = {"total": 0, "by_type": {}, "by_priority": {}}
            by_day[day_key]["total"] += 1

            type_key = occ.occurrence_type.value
            type_dict = by_day[day_key]["by_type"]
            type_dict[type_key] = type_dict.get(type_key, 0) + 1

            priority_key = occ.priority.value
            prio_dict = by_day[day_key]["by_priority"]
            prio_dict[priority_key] = prio_dict.get(priority_key, 0) + 1

        # Calcular tendências
        daily_totals = [v["total"] for v in by_day.values()]
        avg_daily = sum(daily_totals) / len(daily_totals) if daily_totals else 0

        # Insights
        insights = []

        # Tendência de volume
        if len(daily_totals) >= 7:
            first_half = sum(daily_totals[: len(daily_totals) // 2])
            second_half = sum(daily_totals[len(daily_totals) // 2:])
            if second_half > first_half * 1.2:
                insights.append("Aumento de ocorrências nos últimos dias.")
            elif second_half < first_half * 0.8:
                insights.append("Redução de ocorrências nos últimos dias.")

        # Tipo mais comum
        type_counts = {}
        for occ in occurrences:
            t = occ.occurrence_type.value
            type_counts[t] = type_counts.get(t, 0) + 1
        if type_counts:
            most_common = max(type_counts, key=type_counts.get)
            count = type_counts[most_common]
            insights.append(f"Tipo mais comum: {most_common} ({count} ocorrências)")

        # Prioridades altas
        high_priorities = [
            OccurrencePriority.ALTA,
            OccurrencePriority.URGENTE,
            OccurrencePriority.CRITICA,
        ]
        high_priority_count = sum(
            1 for occ in occurrences if occ.priority in high_priorities
        )
        if high_priority_count > len(occurrences) * 0.3:
            pct = high_priority_count * 100 // len(occurrences)
            msg = f"Alto índice de ocorrências prioritárias: {high_priority_count} ({pct}%)"
            insights.append(msg)

        return {
            "period_days": days,
            "total": len(occurrences),
            "avg_daily": round(avg_daily, 1),
            "by_day": by_day,
            "type_distribution": type_counts,
            "insights": insights,
            "analysis_date": datetime.utcnow().isoformat(),
        }
