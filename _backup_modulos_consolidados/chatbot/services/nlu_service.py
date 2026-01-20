"""NLU Service - Natural Language Understanding.

Sprint 38 - Chatbot IA.

Responsavel por:
- Deteccao de intents
- Extracao de entidades
- Analise de sentimento
- Normalizacao de texto
"""

import hashlib
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple

from modules.ai.chatbot.models import (
    Entity,
    EntityType,
    Intent,
    SentimentType,
)


@dataclass
class DetectedIntent:
    """Intent detectado."""

    name: str
    confidence: float
    display_name: Optional[str] = None
    category: Optional[str] = None
    responses: List[str] = field(default_factory=list)
    action: Optional[str] = None
    slots: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ExtractedEntity:
    """Entidade extraida."""

    entity: str
    entity_type: EntityType
    value: str
    original_value: str
    confidence: float
    start: int
    end: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NLUResult:
    """Resultado da analise NLU."""

    text: str
    normalized_text: str
    language: str
    intents: List[DetectedIntent]
    top_intent: Optional[DetectedIntent]
    entities: List[ExtractedEntity]
    sentiment: SentimentType
    sentiment_score: float
    is_ambiguous: bool
    processing_time_ms: int


class NLUService:
    """Servico de Natural Language Understanding."""

    # Patterns para entidades do sistema
    ENTITY_PATTERNS = {
        EntityType.EMAIL: r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        EntityType.PHONE: r"(?:\+55\s?)?(?:\(?\d{2}\)?[\s.-]?)?\d{4,5}[\s.-]?\d{4}",
        EntityType.CPF: r"\d{3}\.?\d{3}\.?\d{3}[-.]?\d{2}",
        EntityType.CNPJ: r"\d{2}\.?\d{3}\.?\d{3}[/.]?\d{4}[-.]?\d{2}",
        EntityType.CEP: r"\d{5}[-.]?\d{3}",
        EntityType.DATE: r"\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}",
        EntityType.TIME: r"\d{1,2}[h:]\d{2}(?:\s?[ap]m)?",
        EntityType.CURRENCY: r"R\$\s?\d+(?:[.,]\d{3})*(?:[.,]\d{2})?",
        EntityType.URL: r"https?://[^\s]+",
        EntityType.NUMBER: r"\b\d+(?:[.,]\d+)?\b",
    }

    # Palavras para analise de sentimento
    POSITIVE_WORDS = {
        "otimo", "excelente", "maravilhoso", "perfeito", "adorei", "amei",
        "obrigado", "obrigada", "grato", "grata", "satisfeito", "feliz",
        "bom", "legal", "bacana", "show", "top", "massa", "demais",
        "incrivel", "fantastico", "sensacional", "parabens", "muito bom",
    }

    NEGATIVE_WORDS = {
        "pessimo", "horrivel", "terrivel", "ruim", "odiei", "detestei",
        "insatisfeito", "frustrado", "irritado", "bravo", "raiva",
        "problema", "erro", "falha", "nao funciona", "travou", "bug",
        "demora", "lento", "caro", "absurdo", "vergonha", "descaso",
        "porcaria", "lixo", "nunca mais", "cancelar", "reclamar",
    }

    INTENSIFIERS = {
        "muito", "demais", "extremamente", "totalmente", "completamente",
        "absolutamente", "super", "mega", "ultra", "hiper",
    }

    NEGATORS = {"nao", "nem", "nunca", "jamais", "nenhum", "nada"}

    def __init__(
        self,
        confidence_threshold: float = 0.7,
        ambiguity_threshold: float = 0.15,
        enable_spell_check: bool = True,
        enable_sentiment: bool = True,
    ):
        """Inicializa o servico NLU."""
        self.confidence_threshold = confidence_threshold
        self.ambiguity_threshold = ambiguity_threshold
        self.enable_spell_check = enable_spell_check
        self.enable_sentiment = enable_sentiment
        self._intents_cache: Dict[str, List[Intent]] = {}
        self._entities_cache: Dict[str, List[Entity]] = {}

    def analyze(
        self,
        text: str,
        intents: List[Intent],
        entities: List[Entity],
        context: Optional[Dict[str, Any]] = None,
        language: str = "pt_BR",
    ) -> NLUResult:
        """Analisa texto e retorna resultado NLU completo."""
        start_time = datetime.utcnow()

        # Normalizar texto
        normalized = self.normalize_text(text)

        # Detectar intents
        detected_intents = self.detect_intents(normalized, intents, context)

        # Verificar ambiguidade
        is_ambiguous = self._check_ambiguity(detected_intents)

        # Top intent
        top_intent = detected_intents[0] if detected_intents else None

        # Extrair entidades
        extracted_entities = self.extract_entities(text, normalized, entities)

        # Analisar sentimento
        sentiment, sentiment_score = self.analyze_sentiment(text)

        # Calcular tempo
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        return NLUResult(
            text=text,
            normalized_text=normalized,
            language=language,
            intents=detected_intents,
            top_intent=top_intent,
            entities=extracted_entities,
            sentiment=sentiment if self.enable_sentiment else SentimentType.NEUTRAL,
            sentiment_score=sentiment_score if self.enable_sentiment else 0.0,
            is_ambiguous=is_ambiguous,
            processing_time_ms=processing_time,
        )

    def normalize_text(self, text: str) -> str:
        """Normaliza texto para processamento NLU."""
        if not text:
            return ""

        # Converter para minusculas
        normalized = text.lower()

        # Remover acentos (opcional, manter para portugues)
        # normalized = self._remove_accents(normalized)

        # Remover pontuacao extra
        normalized = re.sub(r"[^\w\sáéíóúàèìòùâêîôûãõç@.-]", " ", normalized)

        # Normalizar espacos
        normalized = " ".join(normalized.split())

        return normalized.strip()

    def _remove_accents(self, text: str) -> str:
        """Remove acentos do texto."""
        nfkd = unicodedata.normalize("NFKD", text)
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    def detect_intents(
        self,
        text: str,
        intents: List[Intent],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[DetectedIntent]:
        """Detecta intents no texto."""
        if not text or not intents:
            return []

        scores: List[Tuple[Intent, float]] = []

        for intent in intents:
            if not intent.active:
                continue

            # Verificar contextos de entrada
            if intent.input_contexts and context:
                active_contexts = context.get("active_contexts", [])
                if not any(ctx in active_contexts for ctx in intent.input_contexts):
                    continue

            # Calcular score
            score = self._calculate_intent_score(text, intent)

            if score >= self.confidence_threshold:
                scores.append((intent, score))

        # Ordenar por score
        scores.sort(key=lambda x: (-x[1], -x[0].priority))

        # Converter para DetectedIntent
        detected = []
        for intent, score in scores:
            detected.append(
                DetectedIntent(
                    name=intent.name,
                    confidence=score,
                    display_name=intent.display_name,
                    category=intent.category.value if intent.category else None,
                    responses=intent.responses or [],
                    action=intent.action,
                    slots=intent.slots or [],
                )
            )

        return detected

    def _calculate_intent_score(self, text: str, intent: Intent) -> float:
        """Calcula score de match entre texto e intent."""
        if not intent.training_phrases:
            return 0.0

        max_score = 0.0
        text_words = set(text.split())

        for phrase in intent.training_phrases:
            phrase_normalized = self.normalize_text(phrase)

            # Score exato
            if text == phrase_normalized:
                return 1.0

            # Score por similaridade de sequencia
            seq_score = SequenceMatcher(None, text, phrase_normalized).ratio()

            # Score por palavras em comum
            phrase_words = set(phrase_normalized.split())
            common_words = text_words & phrase_words
            if phrase_words:
                word_score = len(common_words) / len(phrase_words)
            else:
                word_score = 0.0

            # Combinar scores
            combined_score = (seq_score * 0.6) + (word_score * 0.4)

            # Aplicar sinonimos
            if intent.synonyms:
                combined_score = self._apply_synonyms(text, phrase_normalized, intent.synonyms, combined_score)

            max_score = max(max_score, combined_score)

        return max_score

    def _apply_synonyms(
        self,
        text: str,
        phrase: str,
        synonyms: Dict[str, List[str]],
        base_score: float,
    ) -> float:
        """Aplica bonus de sinonimos ao score."""
        bonus = 0.0

        for word, syns in synonyms.items():
            word_in_phrase = word in phrase
            syn_in_text = any(syn in text for syn in syns)

            if word_in_phrase and syn_in_text:
                bonus += 0.1

        return min(1.0, base_score + bonus)

    def _check_ambiguity(self, intents: List[DetectedIntent]) -> bool:
        """Verifica se ha ambiguidade entre intents."""
        if len(intents) < 2:
            return False

        top_confidence = intents[0].confidence
        second_confidence = intents[1].confidence

        return (top_confidence - second_confidence) < self.ambiguity_threshold

    def extract_entities(
        self,
        original_text: str,
        normalized_text: str,
        entities: List[Entity],
    ) -> List[ExtractedEntity]:
        """Extrai entidades do texto."""
        extracted: List[ExtractedEntity] = []

        # Extrair entidades do sistema
        extracted.extend(self._extract_system_entities(original_text))

        # Extrair entidades customizadas
        for entity in entities:
            if not entity.active:
                continue

            matches = self._extract_custom_entity(original_text, normalized_text, entity)
            extracted.extend(matches)

        # Remover duplicatas e ordenar
        extracted = self._deduplicate_entities(extracted)
        extracted.sort(key=lambda x: x.start)

        return extracted

    def _extract_system_entities(self, text: str) -> List[ExtractedEntity]:
        """Extrai entidades do sistema usando regex."""
        extracted = []

        for entity_type, pattern in self.ENTITY_PATTERNS.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                value = match.group()
                normalized_value = self._normalize_entity_value(value, entity_type)

                extracted.append(
                    ExtractedEntity(
                        entity=entity_type.value,
                        entity_type=entity_type,
                        value=normalized_value,
                        original_value=value,
                        confidence=0.95,
                        start=match.start(),
                        end=match.end(),
                    )
                )

        return extracted

    def _normalize_entity_value(self, value: str, entity_type: EntityType) -> str:
        """Normaliza valor de entidade."""
        if entity_type == EntityType.CPF:
            return re.sub(r"[^\d]", "", value)
        elif entity_type == EntityType.CNPJ:
            return re.sub(r"[^\d]", "", value)
        elif entity_type == EntityType.CEP:
            return re.sub(r"[^\d]", "", value)
        elif entity_type == EntityType.PHONE:
            return re.sub(r"[^\d+]", "", value)
        elif entity_type == EntityType.CURRENCY:
            value = re.sub(r"[^\d,.]", "", value)
            value = value.replace(".", "").replace(",", ".")
            return value

        return value

    def _extract_custom_entity(
        self,
        original_text: str,
        normalized_text: str,
        entity: Entity,
    ) -> List[ExtractedEntity]:
        """Extrai entidade customizada."""
        extracted = []

        # Entidade tipo REGEX
        if entity.entity_type == EntityType.REGEX and entity.regex_pattern:
            for match in re.finditer(entity.regex_pattern, original_text, re.IGNORECASE):
                extracted.append(
                    ExtractedEntity(
                        entity=entity.name,
                        entity_type=entity.entity_type,
                        value=match.group(),
                        original_value=match.group(),
                        confidence=0.9,
                        start=match.start(),
                        end=match.end(),
                    )
                )

        # Entidade tipo LIST
        elif entity.entity_type == EntityType.LIST and entity.values:
            for value_entry in entity.values:
                canonical = value_entry.get("value", "")
                synonyms = value_entry.get("synonyms", [])

                # Buscar valor canonico
                matches = list(re.finditer(re.escape(canonical), normalized_text, re.IGNORECASE))

                # Buscar sinonimos
                for syn in synonyms:
                    matches.extend(re.finditer(re.escape(syn), normalized_text, re.IGNORECASE))

                for match in matches:
                    extracted.append(
                        ExtractedEntity(
                            entity=entity.name,
                            entity_type=entity.entity_type,
                            value=canonical,
                            original_value=match.group(),
                            confidence=0.9 if match.group().lower() == canonical.lower() else 0.85,
                            start=match.start(),
                            end=match.end(),
                        )
                    )

        # Fuzzy matching
        if entity.enable_fuzzy and entity.values:
            for value_entry in entity.values:
                canonical = value_entry.get("value", "")
                words = normalized_text.split()

                for i, word in enumerate(words):
                    ratio = SequenceMatcher(None, word, canonical.lower()).ratio()
                    if ratio >= (entity.fuzzy_threshold or 0.8):
                        start = normalized_text.find(word)
                        extracted.append(
                            ExtractedEntity(
                                entity=entity.name,
                                entity_type=entity.entity_type,
                                value=canonical,
                                original_value=word,
                                confidence=ratio,
                                start=start,
                                end=start + len(word),
                            )
                        )

        return extracted

    def _deduplicate_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """Remove entidades duplicadas."""
        if not entities:
            return []

        # Agrupar por posicao
        unique = {}
        for entity in entities:
            key = (entity.start, entity.end, entity.entity)
            if key not in unique or entity.confidence > unique[key].confidence:
                unique[key] = entity

        return list(unique.values())

    def analyze_sentiment(self, text: str) -> Tuple[SentimentType, float]:
        """Analisa sentimento do texto."""
        if not text:
            return SentimentType.NEUTRAL, 0.0

        text_lower = text.lower()
        words = text_lower.split()

        positive_count = 0
        negative_count = 0
        intensifier_bonus = 0
        negation_active = False

        for i, word in enumerate(words):
            # Verificar negador
            if word in self.NEGATORS:
                negation_active = True
                continue

            # Verificar intensificador
            if word in self.INTENSIFIERS:
                intensifier_bonus = 0.5
                continue

            # Verificar palavras positivas
            if word in self.POSITIVE_WORDS:
                if negation_active:
                    negative_count += 1 + intensifier_bonus
                else:
                    positive_count += 1 + intensifier_bonus
                negation_active = False
                intensifier_bonus = 0

            # Verificar palavras negativas
            elif word in self.NEGATIVE_WORDS:
                if negation_active:
                    positive_count += 1 + intensifier_bonus
                else:
                    negative_count += 1 + intensifier_bonus
                negation_active = False
                intensifier_bonus = 0

        # Calcular score
        total = positive_count + negative_count
        if total == 0:
            return SentimentType.NEUTRAL, 0.0

        score = (positive_count - negative_count) / max(total, 1)
        score = max(-1.0, min(1.0, score))

        # Classificar sentimento
        if score >= 0.5:
            sentiment = SentimentType.VERY_POSITIVE
        elif score >= 0.2:
            sentiment = SentimentType.POSITIVE
        elif score <= -0.5:
            sentiment = SentimentType.VERY_NEGATIVE
        elif score <= -0.2:
            sentiment = SentimentType.NEGATIVE
        else:
            sentiment = SentimentType.NEUTRAL

        return sentiment, score

    def get_text_hash(self, text: str) -> str:
        """Gera hash do texto para deduplicacao."""
        normalized = self.normalize_text(text)
        return hashlib.sha256(normalized.encode()).hexdigest()
