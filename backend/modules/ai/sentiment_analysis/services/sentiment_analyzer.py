"""
Sentiment Analyzer Service - Sprint 46

Servico principal para analise de sentimento com NLP.
"""

import logging
import re
import time
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from modules.ai.sentiment_analysis.models import (
    AnalysisStatus,
    EmotionType,
    SentimentAnalysis,
    SentimentType,
    SourceType,
)
from modules.ai.sentiment_analysis.repositories import SentimentRepository
from modules.ai.sentiment_analysis.schemas import (
    AnalyzeTextRequest,
    AnalyzeTextResponse,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
)

logger = logging.getLogger(__name__)

# Versao do modelo de analise
MODEL_VERSION = "sentiment_v1.0.0"


class SentimentAnalyzer:
    """Servico de analise de sentimento."""

    # Palavras-chave por categoria de sentimento (PT-BR)
    POSITIVE_WORDS = {
        "excelente",
        "otimo",
        "perfeito",
        "maravilhoso",
        "incrivel",
        "fantastico",
        "sensacional",
        "espetacular",
        "adorei",
        "amei",
        "parabens",
        "satisfeito",
        "feliz",
        "contente",
        "grato",
        "agradecer",
        "obrigado",
        "recomendo",
        "eficiente",
        "rapido",
        "profissional",
        "atencioso",
        "competente",
        "dedicado",
        "prestativo",
        "simpatico",
        "educado",
        "cordial",
        "gentil",
        "solucao",
        "resolveu",
        "funcionou",
        "perfeicao",
        "qualidade",
        "top",
        "nota 10",
        "show",
        "demais",
        "legal",
        "bom",
    }

    NEGATIVE_WORDS = {
        "pessimo",
        "horrivel",
        "terrivel",
        "inaceitavel",
        "absurdo",
        "ridiculo",
        "vergonha",
        "decepcionado",
        "frustrado",
        "irritado",
        "raiva",
        "odio",
        "pior",
        "nunca",
        "jamais",
        "insatisfeito",
        "ruim",
        "mal",
        "lento",
        "demorado",
        "incompetente",
        "desrespeitoso",
        "grosseiro",
        "ignorante",
        "negligente",
        "problema",
        "erro",
        "falha",
        "bug",
        "defeito",
        "reclamar",
        "cancelar",
        "devolver",
        "reembolso",
        "procon",
        "advogado",
        "processo",
        "judicial",
        "denunciar",
        "fraude",
        "golpe",
        "enganado",
        "mentira",
        "descaso",
        "abandono",
    }

    URGENCY_WORDS = {
        "urgente",
        "emergencia",
        "imediato",
        "agora",
        "rapido",
        "pressa",
        "socorro",
        "help",
        "ajuda",
        "grave",
        "critico",
        "serio",
        "importante",
        "prioridade",
        "deadline",
    }

    CHURN_INDICATORS = {
        "cancelar",
        "cancelamento",
        "desistir",
        "trocar",
        "mudar",
        "concorrente",
        "outro servico",
        "encerrar",
        "sair",
        "abandonar",
        "nunca mais",
        "ultima vez",
        "fim",
        "tchau",
        "adeus",
    }

    COMPLAINT_INDICATORS = {
        "reclamacao",
        "reclamar",
        "problema",
        "erro",
        "falha",
        "nao funciona",
        "defeito",
        "quebrado",
        "danificado",
        "procon",
        "ouvidoria",
        "advogado",
        "processo",
        "indenizacao",
    }

    # Emocoes e suas palavras associadas
    EMOTION_KEYWORDS = {
        EmotionType.JOY: {
            "feliz",
            "alegre",
            "contente",
            "animado",
            "empolgado",
        },
        EmotionType.SATISFACTION: {
            "satisfeito",
            "realizado",
            "completo",
            "atendido",
        },
        EmotionType.GRATITUDE: {
            "grato",
            "agradecido",
            "obrigado",
            "agradecer",
            "reconhecido",
        },
        EmotionType.TRUST: {
            "confianca",
            "confio",
            "seguro",
            "tranquilo",
            "credibilidade",
        },
        EmotionType.FRUSTRATION: {
            "frustrado",
            "frustracao",
            "desapontado",
            "chateado",
        },
        EmotionType.ANGER: {
            "raiva",
            "irritado",
            "furioso",
            "revoltado",
            "indignado",
        },
        EmotionType.DISAPPOINTMENT: {
            "decepcionado",
            "decepcao",
            "esperava mais",
            "aquem",
        },
        EmotionType.FEAR: {
            "medo",
            "receio",
            "preocupado",
            "ansioso",
            "inseguro",
        },
        EmotionType.SADNESS: {
            "triste",
            "tristeza",
            "infeliz",
            "desanimado",
            "abatido",
        },
        EmotionType.URGENCY: {
            "urgente",
            "emergencia",
            "imediato",
            "rapido",
            "agora",
        },
    }

    # Aspectos comuns em servicos
    ASPECT_KEYWORDS = {
        "atendimento": [
            "atendimento",
            "atendente",
            "suporte",
            "sac",
            "call center",
            "chat",
            "telefone",
            "email",
            "whatsapp",
        ],
        "preco": [
            "preco",
            "valor",
            "custo",
            "caro",
            "barato",
            "taxa",
            "tarifa",
            "cobranca",
            "fatura",
            "boleto",
            "pagamento",
        ],
        "qualidade": [
            "qualidade",
            "produto",
            "material",
            "acabamento",
            "durabilidade",
        ],
        "entrega": [
            "entrega",
            "prazo",
            "chegou",
            "enviado",
            "frete",
            "transportadora",
        ],
        "plataforma": [
            "site",
            "app",
            "aplicativo",
            "sistema",
            "plataforma",
            "interface",
        ],
        "instalacao": [
            "instalacao",
            "tecnico",
            "visita",
            "montagem",
            "configuracao",
        ],
        "seguranca": [
            "seguranca",
            "camera",
            "alarme",
            "monitoramento",
            "vigilancia",
        ],
    }

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = SentimentRepository(session)

    async def analyze_text(
        self,
        request: AnalyzeTextRequest,
    ) -> AnalyzeTextResponse:
        """
        Analisa sentimento de um texto.

        Args:
            request: Dados do texto para analise

        Returns:
            Resultado da analise de sentimento
        """
        start_time = time.time()

        # Criar registro
        analysis = SentimentAnalysis(
            original_text=request.text,
            source_type=SourceType(request.source_type.value),
            source_id=request.source_id,
            source_reference=request.source_reference,
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            entity_name=request.entity_name,
            customer_id=request.customer_id,
            customer_name=request.customer_name,
            customer_segment=request.customer_segment,
            language=request.language,
            nps_score=request.nps_score,
            metadata=request.metadata or {},
            tags=request.tags or [],
            status=AnalysisStatus.PROCESSING,
        )

        try:
            # Normalizar texto
            normalized = self._normalize_text(request.text)
            analysis.normalized_text = normalized
            analysis.word_count = len(normalized.split())
            analysis.char_count = len(request.text)

            # Analisar sentimento
            sentiment_result = self._analyze_sentiment(normalized)
            analysis.sentiment_score = sentiment_result["score"]
            analysis.positive_score = sentiment_result["positive"]
            analysis.negative_score = sentiment_result["negative"]
            analysis.neutral_score = sentiment_result["neutral"]
            analysis.confidence_score = sentiment_result["confidence"]
            analysis.sentiment_type = analysis.determine_sentiment_type()

            # Detectar emocoes
            if request.detect_emotions:
                emotions = self._detect_emotions(normalized)
                analysis.primary_emotion = emotions.get("primary")
                analysis.secondary_emotion = emotions.get("secondary")
                analysis.emotion_scores = emotions.get("scores", {})

            # Extrair aspectos
            if request.extract_aspects:
                aspects = self._extract_aspects(normalized)
                analysis.aspects = aspects

            # Extrair keywords
            if request.extract_keywords:
                keywords = self._extract_keywords(normalized)
                analysis.keywords = keywords
                analysis.topics = self._identify_topics(normalized)

            # Extrair frases-chave
            phrases = self._extract_key_phrases(request.text, sentiment_result["score"])
            analysis.key_phrases = phrases["key"]
            analysis.positive_phrases = phrases["positive"]
            analysis.negative_phrases = phrases["negative"]

            # Verificar indicadores especiais
            if request.check_urgency:
                urgency = self._check_urgency(normalized)
                analysis.has_urgency = urgency["has_urgency"]
                analysis.urgency_level = urgency["level"]

            analysis.has_complaint = self._check_complaint(normalized)
            analysis.has_praise = self._check_praise(normalized)
            analysis.has_question = self._check_question(request.text)
            analysis.has_suggestion = self._check_suggestion(normalized)
            analysis.has_intent_to_leave = self._check_churn_intent(normalized)

            # Determinar se requer acao
            analysis.requires_action = self._determine_requires_action(analysis)

            # NPS category
            if request.nps_score is not None:
                analysis.nps_category = self._categorize_nps(request.nps_score)

            # Aplicar regras
            triggered_rules = []
            if request.apply_rules:
                rules = await self.repository.get_active_rules(analysis.source_type)
                for rule in rules:
                    result = rule.evaluate(self._analysis_to_dict(analysis))
                    if result["matched"]:
                        triggered_rules.append(
                            {
                                "rule_id": str(rule.id),
                                "rule_code": rule.code,
                                "rule_name": rule.name,
                                "reasons": result["reasons"],
                                "actions": rule.get_actions(),
                            }
                        )
                        await self.repository.increment_rule_trigger(rule.id)

            analysis.triggered_rules = triggered_rules
            analysis.alert_generated = len(triggered_rules) > 0

            # Finalizar
            processing_time = int((time.time() - start_time) * 1000)
            analysis.processing_time_ms = processing_time
            analysis.model_version = MODEL_VERSION
            analysis.status = AnalysisStatus.COMPLETED
            analysis.analyzed_at = datetime.utcnow()

            # Salvar
            analysis = await self.repository.create_analysis(analysis)

            logger.info(
                f"Analise concluida: {analysis.id} - "
                f"Score: {analysis.sentiment_score} - "
                f"Tipo: {analysis.sentiment_type.value}"
            )

            return self._to_response(analysis)

        except Exception as e:
            logger.error(f"Erro na analise de sentimento: {e}")
            analysis.status = AnalysisStatus.FAILED
            analysis.error_message = str(e)
            analysis = await self.repository.create_analysis(analysis)
            raise

    async def batch_analyze(
        self,
        request: BatchAnalyzeRequest,
    ) -> BatchAnalyzeResponse:
        """Analisa multiplos textos em lote."""
        start_time = time.time()
        results = []
        errors = []

        for i, text_request in enumerate(request.texts):
            try:
                result = await self.analyze_text(text_request)
                results.append(result)
            except Exception as e:
                errors.append(
                    {
                        "index": i,
                        "error": str(e),
                        "text_preview": text_request.text[:100],
                    }
                )

        processing_time = int((time.time() - start_time) * 1000)

        return BatchAnalyzeResponse(
            total=len(request.texts),
            processed=len(results),
            failed=len(errors),
            results=results,
            errors=errors,
            processing_time_ms=processing_time,
        )

    def _normalize_text(self, text: str) -> str:
        """Normaliza texto para analise."""
        # Lowercase
        normalized = text.lower()

        # Remover URLs
        normalized = re.sub(r"http[s]?://\S+", "", normalized)

        # Remover emails
        normalized = re.sub(r"\S+@\S+", "", normalized)

        # Remover caracteres especiais mas manter acentos
        normalized = re.sub(r"[^\w\sáéíóúâêîôûãõàèìòùäëïöüç]", " ", normalized)

        # Remover espacos extras
        normalized = re.sub(r"\s+", " ", normalized).strip()

        return normalized

    def _analyze_sentiment(self, text: str) -> dict[str, Any]:
        """Analisa polaridade do sentimento."""
        words = set(text.split())

        positive_count = len(words & self.POSITIVE_WORDS)
        negative_count = len(words & self.NEGATIVE_WORDS)
        total_sentiment_words = positive_count + negative_count

        if total_sentiment_words == 0:
            # Neutro
            return {
                "score": 0,
                "positive": 30,
                "negative": 30,
                "neutral": 40,
                "confidence": 50,
            }

        # Calcular proporcoes
        positive_ratio = positive_count / total_sentiment_words
        negative_ratio = negative_count / total_sentiment_words

        # Score de -100 a +100
        score = (positive_ratio - negative_ratio) * 100

        # Ajustar baseado em intensificadores
        score = self._adjust_for_intensifiers(text, score)

        # Calcular scores de polaridade
        if score > 0:
            positive_pct = min(100, 50 + score / 2)
            negative_pct = max(0, 50 - score / 2)
            neutral_pct = 100 - positive_pct - negative_pct
        else:
            positive_pct = max(0, 50 + score / 2)
            negative_pct = min(100, 50 - score / 2)
            neutral_pct = 100 - positive_pct - negative_pct

        # Confianca baseada na quantidade de palavras de sentimento
        confidence = min(95, 40 + total_sentiment_words * 10)

        return {
            "score": round(score, 2),
            "positive": round(max(0, positive_pct), 2),
            "negative": round(max(0, negative_pct), 2),
            "neutral": round(max(0, neutral_pct), 2),
            "confidence": round(confidence, 2),
        }

    def _adjust_for_intensifiers(self, text: str, score: float) -> float:
        """Ajusta score baseado em intensificadores."""
        intensifiers_positive = ["muito", "extremamente", "super", "mega", "demais"]
        intensifiers_negative = ["nada", "nem", "nunca", "jamais", "pessimo"]
        negators = ["nao", "nem", "nunca", "jamais"]

        text_lower = text.lower()

        # Verificar negacoes
        for negator in negators:
            if negator in text_lower:
                score *= -0.5

        # Verificar intensificadores
        for intensifier in intensifiers_positive:
            if intensifier in text_lower:
                score *= 1.2

        for intensifier in intensifiers_negative:
            if intensifier in text_lower:
                score *= 0.8

        return max(-100, min(100, score))

    def _detect_emotions(self, text: str) -> dict[str, Any]:
        """Detecta emocoes no texto."""
        words = set(text.split())
        emotion_scores = {}

        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            matches = len(words & keywords)
            if matches > 0:
                emotion_scores[emotion.value] = min(100, matches * 25)

        if not emotion_scores:
            return {
                "primary": EmotionType.NEUTRAL,
                "secondary": None,
                "scores": {"neutral": 50},
            }

        # Ordenar por score
        sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)

        primary = EmotionType(sorted_emotions[0][0])
        secondary = None
        if len(sorted_emotions) > 1 and sorted_emotions[1][1] >= 25:
            secondary = EmotionType(sorted_emotions[1][0])

        return {
            "primary": primary,
            "secondary": secondary,
            "scores": emotion_scores,
        }

    def _extract_aspects(self, text: str) -> list[dict[str, Any]]:
        """Extrai aspectos mencionados e seu sentimento."""
        aspects = []
        text.split()

        for aspect_name, keywords in self.ASPECT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    # Analisar contexto ao redor
                    context = self._get_context(text, keyword, window=10)
                    aspect_sentiment = self._analyze_sentiment(context)

                    aspects.append(
                        {
                            "aspect": aspect_name,
                            "keyword": keyword,
                            "sentiment": self._score_to_sentiment_label(aspect_sentiment["score"]),
                            "score": aspect_sentiment["score"],
                            "mentions": text.count(keyword),
                        }
                    )
                    break  # Apenas uma entrada por aspecto

        return aspects

    def _get_context(self, text: str, keyword: str, window: int = 10) -> str:
        """Extrai contexto ao redor de uma palavra."""
        words = text.split()
        try:
            idx = None
            for i, w in enumerate(words):
                if keyword in w:
                    idx = i
                    break
            if idx is None:
                return ""

            start = max(0, idx - window)
            end = min(len(words), idx + window + 1)
            return " ".join(words[start:end])
        except (ValueError, IndexError):
            return ""

    def _score_to_sentiment_label(self, score: float) -> str:
        """Converte score para label."""
        if score >= 60:
            return "very_positive"
        elif score >= 20:
            return "positive"
        elif score >= -20:
            return "neutral"
        elif score >= -60:
            return "negative"
        else:
            return "very_negative"

    def _extract_keywords(self, text: str) -> list[dict[str, Any]]:
        """Extrai palavras-chave relevantes."""
        # Stop words em portugues
        stop_words = {
            "de",
            "da",
            "do",
            "das",
            "dos",
            "a",
            "o",
            "as",
            "os",
            "e",
            "em",
            "para",
            "com",
            "por",
            "um",
            "uma",
            "que",
            "se",
            "na",
            "no",
            "nas",
            "nos",
            "ao",
            "aos",
            "pela",
            "pelo",
            "pelas",
            "pelos",
            "este",
            "esta",
            "esse",
            "essa",
            "aquele",
            "aquela",
            "seu",
            "sua",
            "seus",
            "suas",
            "meu",
            "minha",
            "meus",
            "minhas",
            "ele",
            "ela",
            "eles",
            "elas",
            "voce",
            "voces",
            "eu",
            "tu",
            "foi",
            "era",
            "ser",
            "ter",
            "estou",
            "estava",
            "nao",
            "sim",
            "mais",
            "muito",
            "tambem",
            "ja",
            "ainda",
            "quando",
            "onde",
            "como",
        }

        words = text.split()
        word_freq = {}

        for word in words:
            if len(word) > 3 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Ordenar por frequencia
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        return [{"word": word, "frequency": freq} for word, freq in sorted_words[:20]]

    def _identify_topics(self, text: str) -> list[str]:
        """Identifica topicos principais."""
        topics = []

        topic_keywords = {
            "atendimento": ["atendimento", "atendente", "suporte", "ajuda"],
            "pagamento": ["pagamento", "pagar", "boleto", "cobranca", "fatura"],
            "produto": ["produto", "equipamento", "material", "pecas"],
            "entrega": ["entrega", "prazo", "chegou", "enviado"],
            "instalacao": ["instalacao", "instalar", "tecnico", "visita"],
            "preco": ["preco", "valor", "custo", "caro", "barato"],
            "qualidade": ["qualidade", "bom", "ruim", "funcionando"],
            "seguranca": ["seguranca", "camera", "alarme", "monitoramento"],
        }

        for topic, keywords in topic_keywords.items():
            if any(kw in text for kw in keywords):
                topics.append(topic)

        return topics

    def _extract_key_phrases(
        self,
        text: str,
        sentiment_score: float,
    ) -> dict[str, list[str]]:
        """Extrai frases-chave do texto."""
        sentences = re.split(r"[.!?]+", text)
        key_phrases = []
        positive_phrases = []
        negative_phrases = []

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue

            normalized = self._normalize_text(sentence)
            sent_analysis = self._analyze_sentiment(normalized)

            if sent_analysis["score"] > 30:
                positive_phrases.append(sentence[:200])
            elif sent_analysis["score"] < -30:
                negative_phrases.append(sentence[:200])

            # Frases com palavras-chave importantes
            if any(kw in normalized for kw in ["problema", "solucao", "melhorar", "sugestao"]):
                key_phrases.append(sentence[:200])

        return {
            "key": key_phrases[:5],
            "positive": positive_phrases[:5],
            "negative": negative_phrases[:5],
        }

    def _check_urgency(self, text: str) -> dict[str, Any]:
        """Verifica indicadores de urgencia."""
        urgency_matches = sum(1 for word in self.URGENCY_WORDS if word in text)

        has_urgency = urgency_matches > 0
        level = min(10, urgency_matches * 3)

        # Aumentar nivel se tiver exclamacoes multiplas
        if "!!!" in text or text.count("!") > 3:
            level = min(10, level + 2)

        return {"has_urgency": has_urgency, "level": level}

    def _check_complaint(self, text: str) -> bool:
        """Verifica se e uma reclamacao."""
        return any(word in text for word in self.COMPLAINT_INDICATORS)

    def _check_praise(self, text: str) -> bool:
        """Verifica se tem elogio."""
        praise_words = {"parabens", "excelente", "otimo", "adorei", "perfeito", "incrivel"}
        return any(word in text for word in praise_words)

    def _check_question(self, text: str) -> bool:
        """Verifica se tem pergunta."""
        return "?" in text

    def _check_suggestion(self, text: str) -> bool:
        """Verifica se tem sugestao."""
        suggestion_patterns = [
            "sugiro",
            "sugestao",
            "poderia",
            "seria bom",
            "deveria",
            "que tal",
            "melhorar",
            "melhoraria",
        ]
        return any(pattern in text.lower() for pattern in suggestion_patterns)

    def _check_churn_intent(self, text: str) -> bool:
        """Verifica intencao de cancelamento."""
        return any(word in text for word in self.CHURN_INDICATORS)

    def _determine_requires_action(self, analysis: SentimentAnalysis) -> bool:
        """Determina se analise requer acao."""
        return (
            analysis.sentiment_type in [SentimentType.VERY_NEGATIVE, SentimentType.NEGATIVE]
            or analysis.has_intent_to_leave
            or analysis.has_urgency
            or analysis.has_complaint
            or (analysis.urgency_level or 0) >= 5
        )

    def _categorize_nps(self, score: int) -> str:
        """Categoriza score NPS."""
        if score >= 9:
            return "promoter"
        elif score >= 7:
            return "passive"
        else:
            return "detractor"

    def _analysis_to_dict(self, analysis: SentimentAnalysis) -> dict[str, Any]:
        """Converte analise para dicionario para avaliacao de regras."""
        return {
            "sentiment_score": analysis.sentiment_score,
            "sentiment_type": analysis.sentiment_type.value if analysis.sentiment_type else None,
            "primary_emotion": analysis.primary_emotion.value if analysis.primary_emotion else None,
            "secondary_emotion": analysis.secondary_emotion.value if analysis.secondary_emotion else None,
            "has_urgency": analysis.has_urgency,
            "urgency_level": analysis.urgency_level,
            "has_complaint": analysis.has_complaint,
            "has_intent_to_leave": analysis.has_intent_to_leave,
            "source_type": analysis.source_type.value if analysis.source_type else None,
            "original_text": analysis.original_text,
            "customer_segment": analysis.customer_segment,
            "nps_score": analysis.nps_score,
        }

    def _to_response(self, analysis: SentimentAnalysis) -> AnalyzeTextResponse:
        """Converte analise para response."""
        return AnalyzeTextResponse(
            id=analysis.id,
            sentiment_type=SentimentTypeEnum(analysis.sentiment_type.value),
            sentiment_label=analysis.sentiment_label,
            sentiment_score=analysis.sentiment_score,
            confidence_score=analysis.confidence_score,
            positive_score=analysis.positive_score,
            negative_score=analysis.negative_score,
            neutral_score=analysis.neutral_score,
            primary_emotion=EmotionTypeEnum(analysis.primary_emotion.value) if analysis.primary_emotion else None,
            secondary_emotion=EmotionTypeEnum(analysis.secondary_emotion.value) if analysis.secondary_emotion else None,
            emotion_scores=analysis.emotion_scores or {},
            aspects=[AspectSchema(**a) for a in (analysis.aspects or [])],
            keywords=[KeywordSchema(**k) for k in (analysis.keywords or [])],
            topics=analysis.topics or [],
            has_urgency=analysis.has_urgency,
            urgency_level=analysis.urgency_level or 0,
            has_complaint=analysis.has_complaint,
            has_praise=analysis.has_praise,
            has_question=analysis.has_question,
            has_suggestion=analysis.has_suggestion,
            has_intent_to_leave=analysis.has_intent_to_leave,
            requires_action=analysis.requires_action,
            is_critical=analysis.is_critical,
            key_phrases=analysis.key_phrases or [],
            negative_phrases=analysis.negative_phrases or [],
            positive_phrases=analysis.positive_phrases or [],
            nps_score=analysis.nps_score,
            nps_category=analysis.nps_category,
            triggered_rules=analysis.triggered_rules or [],
            alert_generated=analysis.alert_generated,
            processing_time_ms=analysis.processing_time_ms or 0,
            model_version=analysis.model_version or MODEL_VERSION,
            analyzed_at=analysis.analyzed_at or datetime.utcnow(),
        )


# Import para response
from modules.ai.sentiment_analysis.schemas.sentiment_schemas import (  # noqa: E402
    AspectSchema,
    EmotionTypeEnum,
    KeywordSchema,
    SentimentTypeEnum,
)
