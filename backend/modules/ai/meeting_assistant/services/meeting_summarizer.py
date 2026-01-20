"""
Meeting Summarizer Service - Sprint 49.

Serviço de geração de resumos automáticos de reuniões.
"""

import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

from modules.ai.meeting_assistant.models import (
    Meeting,
    MeetingNote,
    MeetingSummary,
    MeetingParticipant,
)


class MeetingSummarizer:
    """Serviço de resumo de reuniões."""

    def __init__(self):
        self.action_patterns = [
            r"(?:action|ação|tarefa|task):\s*(.+)",
            r"(?:TODO|to-do|todo):\s*(.+)",
            r"@(\w+)\s+(?:deve|should|will|vai)\s+(.+)",
            r"(?:responsável|assignee|owner):\s*(\w+)\s*[-:]\s*(.+)",
        ]

        self.decision_patterns = [
            r"(?:decisão|decision|decided|decidido):\s*(.+)",
            r"(?:aprovado|approved):\s*(.+)",
            r"(?:ficou definido|was defined):\s*(.+)",
        ]

        self.topic_stopwords = {"a", "o", "e", "de", "da", "do", "em", "para", "com", "the", "and", "or", "to"}

    def generate_summary(
        self,
        meeting: Meeting,
        notes: List[MeetingNote] = None
    ) -> Dict[str, Any]:
        """
        Gera resumo da reunião.

        Args:
            meeting: Reunião
            notes: Notas da reunião

        Returns:
            Dict com resumo estruturado
        """
        start_time = datetime.utcnow()

        # Combina todas as fontes de texto
        text_sources = self._gather_text_sources(meeting, notes)

        # Extrai componentes
        key_points = self._extract_key_points(text_sources, meeting)
        action_items = self._extract_action_items(text_sources, meeting)
        decisions = self._extract_decisions(text_sources)
        topics = self._extract_topics(text_sources)
        keywords = self._extract_keywords(text_sources)
        next_steps = self._generate_next_steps(action_items, decisions)

        # Gera resumo textual
        summary_text = self._generate_summary_text(
            meeting=meeting,
            key_points=key_points,
            decisions=decisions,
            action_items=action_items
        )

        # Análise de sentimento simplificada
        sentiment = self._analyze_sentiment(text_sources)

        # Contribuições por participante
        contributions = self._analyze_contributions(notes) if notes else {}

        generation_time = (datetime.utcnow() - start_time).total_seconds()

        return {
            "summary": summary_text,
            "key_points": key_points,
            "action_items": action_items,
            "decisions": decisions,
            "next_steps": next_steps,
            "topics_discussed": topics,
            "keywords": keywords,
            "sentiment_analysis": sentiment,
            "participant_contributions": contributions,
            "ai_model": "rule_based_v1",
            "ai_confidence": 0.75,
            "generation_time_seconds": generation_time
        }

    def _gather_text_sources(self, meeting: Meeting, notes: List[MeetingNote] = None) -> List[str]:
        """Coleta todas as fontes de texto."""
        sources = []

        # Título e descrição
        if meeting.title:
            sources.append(meeting.title)
        if meeting.description:
            sources.append(meeting.description)

        # Agenda
        if meeting.agenda:
            for item in meeting.agenda:
                if isinstance(item, dict) and "title" in item:
                    sources.append(item["title"])

        # Objetivos
        if meeting.objectives:
            sources.extend(meeting.objectives)

        # Notas da reunião
        if meeting.meeting_notes:
            sources.append(meeting.meeting_notes)

        # Notas individuais
        if notes:
            for note in notes:
                if not note.is_private:
                    sources.append(note.content)

        # Action items existentes
        if meeting.action_items:
            for item in meeting.action_items:
                if isinstance(item, dict) and "description" in item:
                    sources.append(item["description"])

        # Decisões existentes
        if meeting.decisions:
            for decision in meeting.decisions:
                if isinstance(decision, dict) and "decision" in decision:
                    sources.append(decision["decision"])

        return sources

    def _extract_key_points(self, sources: List[str], meeting: Meeting) -> List[str]:
        """Extrai pontos-chave."""
        key_points = []

        # Adiciona objetivos como pontos-chave
        if meeting.objectives:
            for obj in meeting.objectives[:3]:
                key_points.append(f"Objetivo: {obj}")

        # Extrai de agenda
        if meeting.agenda:
            for item in meeting.agenda[:5]:
                if isinstance(item, dict) and "title" in item:
                    key_points.append(f"Discutido: {item['title']}")

        # Extrai pontos das notas (frases importantes)
        for source in sources:
            # Procura frases que parecem conclusões
            sentences = re.split(r'[.!?]\s+', source)
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20 and len(sentence) < 200:
                    # Indicadores de importância
                    importance_indicators = [
                        "importante", "principal", "key", "main",
                        "conclusão", "conclusion", "resultado", "result",
                        "destaque", "highlight"
                    ]
                    if any(ind in sentence.lower() for ind in importance_indicators):
                        key_points.append(sentence)

        return list(dict.fromkeys(key_points))[:10]  # Remove duplicatas, max 10

    def _extract_action_items(self, sources: List[str], meeting: Meeting) -> List[Dict[str, Any]]:
        """Extrai itens de ação."""
        actions = []

        # Actions já definidos na reunião
        if meeting.action_items:
            actions.extend(meeting.action_items)

        # Extrai de texto usando patterns
        full_text = " ".join(sources)
        for pattern in self.action_patterns:
            matches = re.finditer(pattern, full_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 2:
                    assignee = groups[0]
                    description = groups[1]
                else:
                    assignee = None
                    description = groups[0] if groups else match.group()

                if description and len(description) > 5:
                    action = {
                        "description": description.strip(),
                        "assignee": assignee,
                        "status": "pending",
                        "source": "extracted"
                    }
                    if action not in actions:
                        actions.append(action)

        return actions[:15]  # Max 15 actions

    def _extract_decisions(self, sources: List[str]) -> List[str]:
        """Extrai decisões."""
        decisions = []
        full_text = " ".join(sources)

        for pattern in self.decision_patterns:
            matches = re.finditer(pattern, full_text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                decision = match.group(1).strip() if match.groups() else match.group().strip()
                if decision and len(decision) > 10:
                    decisions.append(decision)

        return list(dict.fromkeys(decisions))[:10]

    def _extract_topics(self, sources: List[str]) -> List[str]:
        """Extrai tópicos discutidos."""
        # Extrai palavras significativas
        full_text = " ".join(sources).lower()
        words = re.findall(r'\b[a-záéíóúãõâêîôû]{4,}\b', full_text)

        # Conta frequência
        word_freq = {}
        for word in words:
            if word not in self.topic_stopwords:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Top palavras como tópicos
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        topics = [word.capitalize() for word, freq in sorted_words[:10] if freq > 1]

        return topics

    def _extract_keywords(self, sources: List[str]) -> List[str]:
        """Extrai palavras-chave."""
        full_text = " ".join(sources).lower()

        # Encontra termos técnicos e nomes próprios
        keywords = set()

        # Siglas
        siglas = re.findall(r'\b[A-Z]{2,6}\b', " ".join(sources))
        keywords.update(siglas)

        # Termos compostos comuns
        compound_patterns = [
            r'[a-z]+ de [a-z]+',
            r'[a-z]+ para [a-z]+',
        ]
        for pattern in compound_patterns:
            matches = re.findall(pattern, full_text)
            keywords.update(matches[:5])

        return list(keywords)[:15]

    def _generate_next_steps(self, actions: List[Dict], decisions: List[str]) -> List[str]:
        """Gera próximos passos."""
        next_steps = []

        # Baseado em actions
        for action in actions[:5]:
            if isinstance(action, dict) and "description" in action:
                assignee = action.get("assignee", "Responsável")
                next_steps.append(f"{assignee}: {action['description']}")

        # Baseado em decisões que implicam ação
        for decision in decisions[:3]:
            if any(word in decision.lower() for word in ["implementar", "criar", "fazer", "develop", "create"]):
                next_steps.append(f"Implementar: {decision}")

        return next_steps[:10]

    def _generate_summary_text(
        self,
        meeting: Meeting,
        key_points: List[str],
        decisions: List[str],
        action_items: List[Dict]
    ) -> str:
        """Gera texto de resumo."""
        lines = []

        # Cabeçalho
        lines.append(f"**Resumo: {meeting.title}**")
        lines.append("")

        # Data e participantes
        lines.append(f"Data: {meeting.scheduled_start.strftime('%d/%m/%Y %H:%M')}")
        if meeting.participants:
            names = [p.name for p in meeting.participants[:5]]
            lines.append(f"Participantes: {', '.join(names)}")
        lines.append("")

        # Pontos principais
        if key_points:
            lines.append("**Pontos Principais:**")
            for point in key_points[:5]:
                lines.append(f"- {point}")
            lines.append("")

        # Decisões
        if decisions:
            lines.append("**Decisões Tomadas:**")
            for decision in decisions[:5]:
                lines.append(f"- {decision}")
            lines.append("")

        # Actions
        if action_items:
            lines.append("**Itens de Ação:**")
            for action in action_items[:5]:
                if isinstance(action, dict):
                    desc = action.get("description", str(action))
                    assignee = action.get("assignee", "A definir")
                    lines.append(f"- [{assignee}] {desc}")
            lines.append("")

        return "\n".join(lines)

    def _analyze_sentiment(self, sources: List[str]) -> Dict[str, Any]:
        """Análise de sentimento simplificada."""
        full_text = " ".join(sources).lower()

        positive_words = ["sucesso", "ótimo", "excelente", "bom", "aprovado", "positivo", "great", "good", "success"]
        negative_words = ["problema", "erro", "falha", "ruim", "atraso", "bloqueado", "bad", "issue", "problem"]
        neutral_words = ["discutido", "apresentado", "revisado", "analisado", "discussed"]

        positive_count = sum(1 for word in positive_words if word in full_text)
        negative_count = sum(1 for word in negative_words if word in full_text)
        neutral_count = sum(1 for word in neutral_words if word in full_text)

        total = positive_count + negative_count + neutral_count + 1  # +1 para evitar divisão por zero

        return {
            "overall": "positive" if positive_count > negative_count else ("negative" if negative_count > positive_count else "neutral"),
            "positive_score": round(positive_count / total, 2),
            "negative_score": round(negative_count / total, 2),
            "neutral_score": round(neutral_count / total, 2)
        }

    def _analyze_contributions(self, notes: List[MeetingNote]) -> Dict[str, Any]:
        """Analisa contribuições por participante."""
        contributions = {}

        for note in notes:
            author_id = str(note.author_id)
            if author_id not in contributions:
                contributions[author_id] = {
                    "author_name": note.author_name,
                    "note_count": 0,
                    "total_words": 0
                }

            contributions[author_id]["note_count"] += 1
            contributions[author_id]["total_words"] += len(note.content.split())

        return contributions

    def extract_action_items_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extrai action items de um texto.

        Útil para processar notas ou transcrições.
        """
        return self._extract_action_items([text], Meeting(
            meeting_code="temp",
            title="temp",
            scheduled_start=datetime.utcnow(),
            scheduled_end=datetime.utcnow(),
            duration_minutes=0,
            organizer_id=uuid.uuid4()
        ))
