"""
Email Classifier Service - Sprint 54.

Servico de classificacao de emails com IA.
"""

import logging
import re
import time
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class EmailClassifier:
    """
    Classificador de emails com IA.

    Classifica emails por categoria, prioridade,
    sentimento e detecta spam/phishing.
    """

    def __init__(self):
        """Inicializa o classificador."""
        # Keywords por categoria
        self.category_keywords = {
            "support": [
                "ajuda",
                "problema",
                "erro",
                "nao funciona",
                "suporte",
                "duvida",
                "como fazer",
                "nao consigo",
                "bug",
                "falha",
            ],
            "sales": [
                "preco",
                "orcamento",
                "proposta",
                "comprar",
                "adquirir",
                "plano",
                "contrato",
                "promocao",
                "desconto",
                "pagamento",
            ],
            "billing": [
                "fatura",
                "boleto",
                "cobranca",
                "pagamento",
                "taxa",
                "mensalidade",
                "debito",
                "credito",
                "nf",
                "nota fiscal",
            ],
            "complaint": [
                "reclamacao",
                "insatisfeito",
                "pessimo",
                "horrivel",
                "absurdo",
                "inaceitavel",
                "advogado",
                "procon",
                "processo",
            ],
            "scheduling": [
                "agendar",
                "marcar",
                "horario",
                "reuniao",
                "visita",
                "data",
                "disponibilidade",
                "reagendar",
                "cancelar",
            ],
            "feedback": [
                "sugestao",
                "opiniao",
                "avaliacao",
                "feedback",
                "melhoria",
                "elogio",
                "parabens",
                "otimo",
                "excelente",
            ],
        }

        # Keywords de urgencia
        self.urgency_keywords = {
            "critical": [
                "urgente",
                "urgentissimo",
                "emergencia",
                "imediato",
                "critico",
                "parado",
                "bloqueado",
                "crise",
            ],
            "high": [
                "importante",
                "prioridade",
                "rapido",
                "logo",
                "hoje",
                "amanha",
                "prazo",
                "vencimento",
            ],
        }

        # Indicadores de phishing
        self.phishing_indicators = [
            r"clique\s+aqui\s+para\s+atualizar",
            r"sua\s+conta\s+sera\s+bloqueada",
            r"confirme\s+seus\s+dados",
            r"ganhou\s+um\s+premio",
            r"atualize\s+sua\s+senha",
            r"verifique\s+sua\s+identidade",
            r"acesso\s+negado.*clique",
            r"suspeitamos\s+de\s+atividade",
        ]

        # Indicadores de spam
        self.spam_indicators = [
            r"gratis",
            r"ganhe\s+dinheiro",
            r"trabalhe\s+em\s+casa",
            r"perca\s+peso",
            r"viagra",
            r"casino",
            r"loteria",
            r"investimento\s+garantido",
            r"lucro\s+facil",
        ]

        # Keywords de sentimento
        self.sentiment_keywords = {
            "very_positive": ["excelente", "maravilhoso", "perfeito", "incrivel", "fantastico"],
            "positive": ["bom", "otimo", "obrigado", "agradeco", "satisfeito", "gostei"],
            "negative": ["ruim", "problema", "dificil", "chateado", "insatisfeito"],
            "very_negative": ["pessimo", "horrivel", "absurdo", "inaceitavel", "raiva"],
        }

        # Emocoes
        self.emotion_keywords = {
            "anger": ["raiva", "furioso", "indignado", "revoltado", "absurdo"],
            "frustration": ["frustrado", "cansado", "irritado", "dificil"],
            "anxiety": ["preocupado", "ansioso", "urgente", "nervoso"],
            "satisfaction": ["satisfeito", "feliz", "contente", "agradecido"],
            "confusion": ["confuso", "nao entendo", "duvida", "como assim"],
        }

    def classify(
        self,
        subject: str,
        body: str,
        from_address: str = None,
        headers: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """
        Classifica um email.

        Args:
            subject: Assunto do email
            body: Corpo do email
            from_address: Endereco do remetente
            headers: Headers do email

        Returns:
            Resultado da classificacao
        """
        start_time = time.time()
        headers = headers or {}

        # Combina subject e body para analise
        full_text = f"{subject or ''} {body}".lower()

        # Classifica categoria
        category, category_confidence, subcategory = self._classify_category(full_text)

        # Calcula prioridade
        priority, priority_score, priority_factors = self._calculate_priority(full_text, category, from_address)

        # Analisa sentimento
        sentiment, sentiment_score = self._analyze_sentiment(full_text)

        # Detecta emocoes
        emotions = self._detect_emotions(full_text)

        # Detecta intent
        intent, intent_confidence = self._detect_intent(full_text)

        # Extrai keywords
        keywords = self._extract_keywords(full_text)

        # Extrai entidades
        entities = self._extract_entities(full_text)

        # Extrai topicos
        topics = self._extract_topics(full_text, category)

        # Extrai action items
        action_items = self._extract_action_items(full_text)

        # Extrai perguntas
        questions = self._extract_questions(full_text)

        # Verifica spam
        is_spam, spam_score = self._check_spam(full_text, from_address, headers)

        # Verifica phishing
        is_phishing, phishing_indicators = self._check_phishing(full_text, headers)

        # Calcula security score
        security_score = self._calculate_security_score(spam_score, is_phishing, headers)

        processing_time = int((time.time() - start_time) * 1000)

        result = {
            "category": category,
            "category_confidence": category_confidence,
            "subcategory": subcategory,
            "priority": priority,
            "priority_score": priority_score,
            "priority_factors": priority_factors,
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "emotions": emotions,
            "intent": intent,
            "intent_confidence": intent_confidence,
            "keywords": keywords,
            "entities": entities,
            "topics": topics,
            "action_items": action_items,
            "questions": questions,
            "is_spam": is_spam,
            "spam_score": spam_score,
            "is_phishing": is_phishing,
            "phishing_indicators": phishing_indicators,
            "security_score": security_score,
            "processing_time_ms": processing_time,
        }

        logger.info(
            f"Email classified: category={category}, "
            f"priority={priority}, sentiment={sentiment}, "
            f"spam={is_spam}, time={processing_time}ms"
        )

        return result

    def _classify_category(
        self,
        text: str,
    ) -> tuple[str, float, str | None]:
        """Classifica categoria do email."""
        scores = {}

        for category, keywords in self.category_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            scores[category] = score

        if not any(scores.values()):
            return "other", 0.5, None

        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]
        total_keywords = len(self.category_keywords[best_category])
        confidence = min(max_score / max(total_keywords / 2, 1), 1.0)

        return best_category, confidence, None

    def _calculate_priority(
        self,
        text: str,
        category: str,
        from_address: str = None,
    ) -> tuple[str, float, dict[str, float]]:
        """Calcula prioridade do email."""
        factors = {
            "urgency": 0.0,
            "category": 0.0,
            "sender": 0.0,
            "sentiment": 0.0,
        }

        # Verifica urgencia
        for level, keywords in self.urgency_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    if level == "critical":
                        factors["urgency"] = 1.0
                    else:
                        factors["urgency"] = max(factors["urgency"], 0.7)

        # Categoria impacta prioridade
        category_priorities = {
            "complaint": 0.8,
            "support": 0.6,
            "billing": 0.5,
            "sales": 0.4,
            "scheduling": 0.4,
        }
        factors["category"] = category_priorities.get(category, 0.3)

        # Score final
        score = (
            factors["urgency"] * 0.4 + factors["category"] * 0.3 + factors["sender"] * 0.2 + factors["sentiment"] * 0.1
        )

        # Determina prioridade
        if score >= 0.8:
            priority = "critical"
        elif score >= 0.6:
            priority = "high"
        elif score >= 0.4:
            priority = "medium"
        else:
            priority = "low"

        return priority, score, factors

    def _analyze_sentiment(self, text: str) -> tuple[str, float]:
        """Analisa sentimento do texto."""
        scores = {
            "very_positive": 0,
            "positive": 0,
            "negative": 0,
            "very_negative": 0,
        }

        for sentiment, keywords in self.sentiment_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    scores[sentiment] += 1

        positive_score = scores["very_positive"] * 2 + scores["positive"]
        negative_score = scores["very_negative"] * 2 + scores["negative"]

        if positive_score > negative_score:
            if scores["very_positive"] > scores["positive"]:
                return "very_positive", min((positive_score - negative_score) / 5, 1.0)
            return "positive", min((positive_score - negative_score) / 5, 1.0)
        elif negative_score > positive_score:
            if scores["very_negative"] > scores["negative"]:
                return "very_negative", min((negative_score - positive_score) / 5, 1.0) * -1
            return "negative", min((negative_score - positive_score) / 5, 1.0) * -1

        return "neutral", 0.0

    def _detect_emotions(self, text: str) -> dict[str, float]:
        """Detecta emocoes no texto."""
        emotions = {}

        for emotion, keywords in self.emotion_keywords.items():
            count = sum(1 for kw in keywords if kw in text)
            if count > 0:
                emotions[emotion] = min(count / 3, 1.0)

        return emotions

    def _detect_intent(self, text: str) -> tuple[str | None, float]:
        """Detecta intencao do email."""
        intents = {
            "request_help": ["preciso de ajuda", "pode me ajudar", "ajuda com"],
            "ask_question": ["gostaria de saber", "qual", "como", "quando", "onde"],
            "report_problem": ["problema", "erro", "nao funciona", "bug"],
            "make_complaint": ["reclamar", "insatisfeito", "absurdo"],
            "request_information": ["informacoes", "detalhes", "gostaria de saber"],
            "schedule": ["agendar", "marcar", "reuniao"],
            "give_feedback": ["sugestao", "feedback", "opiniao"],
            "cancel": ["cancelar", "desistir", "encerrar"],
        }

        for intent, patterns in intents.items():
            for pattern in patterns:
                if pattern in text:
                    return intent, 0.7

        return None, 0.0

    def _extract_keywords(self, text: str, max_keywords: int = 10) -> list[str]:
        """Extrai keywords do texto."""
        # Stopwords simples
        stopwords = {
            "a",
            "o",
            "e",
            "de",
            "da",
            "do",
            "em",
            "um",
            "uma",
            "para",
            "com",
            "na",
            "no",
            "que",
            "se",
            "por",
            "mais",
            "como",
        }

        # Tokeniza
        words = re.findall(r"\b[a-záéíóúãõç]{3,}\b", text.lower())

        # Conta frequencia
        freq = {}
        for word in words:
            if word not in stopwords:
                freq[word] = freq.get(word, 0) + 1

        # Ordena por frequencia
        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)

        return [word for word, count in sorted_words[:max_keywords]]

    def _extract_entities(self, text: str) -> list[dict[str, Any]]:
        """Extrai entidades do texto."""
        entities = []

        # Email
        emails = re.findall(r"\b[\w.-]+@[\w.-]+\.\w+\b", text)
        for email in emails:
            entities.append({"type": "email", "value": email, "confidence": 0.95})

        # Telefone
        phones = re.findall(r"\(?\d{2}\)?\s*\d{4,5}[-\s]?\d{4}", text)
        for phone in phones:
            entities.append({"type": "phone", "value": phone, "confidence": 0.9})

        # Data
        dates = re.findall(r"\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}", text)
        for date in dates:
            entities.append({"type": "date", "value": date, "confidence": 0.85})

        # Valor monetario
        values = re.findall(r"R\$\s*[\d.,]+", text)
        for value in values:
            entities.append({"type": "money", "value": value, "confidence": 0.9})

        return entities

    def _extract_topics(self, text: str, category: str) -> list[str]:
        """Extrai topicos do email."""
        topics = [category] if category != "other" else []

        topic_patterns = {
            "acesso": ["acesso", "login", "senha", "autenticacao"],
            "pagamento": ["pagamento", "boleto", "fatura", "cobranca"],
            "reserva": ["reserva", "agendamento", "salao", "area comum"],
            "manutencao": ["manutencao", "reparo", "conserto", "problema tecnico"],
            "seguranca": ["seguranca", "camera", "portaria", "acesso"],
        }

        for topic, keywords in topic_patterns.items():
            if any(kw in text for kw in keywords):
                if topic not in topics:
                    topics.append(topic)

        return topics[:5]

    def _extract_action_items(self, text: str) -> list[dict[str, Any]]:
        """Extrai action items do texto."""
        action_items = []

        patterns = [
            (r"preciso\s+(?:que\s+)?(.{10,50})", "request"),
            (r"por\s+favor[,]?\s+(.{10,50})", "request"),
            (r"gostaria\s+(?:de\s+)?(.{10,50})", "request"),
            (r"favor\s+(.{10,50})", "request"),
        ]

        for pattern, action_type in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:3]:
                action_items.append(
                    {
                        "action": match.strip(),
                        "type": action_type,
                        "extracted_at": datetime.utcnow().isoformat(),
                    }
                )

        return action_items

    def _extract_questions(self, text: str) -> list[dict[str, Any]]:
        """Extrai perguntas do texto."""
        questions = []

        # Encontra frases terminando com ?
        sentences = re.split(r"[.!]", text)
        for sentence in sentences:
            if "?" in sentence:
                question = sentence.split("?")[0].strip() + "?"
                if len(question) > 10:
                    questions.append(
                        {
                            "question": question,
                            "answered": False,
                        }
                    )

        return questions[:5]

    def _check_spam(
        self,
        text: str,
        from_address: str = None,
        headers: dict[str, Any] = None,
    ) -> tuple[bool, float]:
        """Verifica se e spam."""
        spam_score = 0.0
        indicators = 0

        # Verifica indicadores de spam
        for pattern in self.spam_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                indicators += 1

        spam_score = min(indicators / 5, 1.0)

        # Verifica se e de dominio suspeito
        if from_address:
            suspicious_domains = [".xyz", ".top", ".click", ".work"]
            for domain in suspicious_domains:
                if domain in from_address.lower():
                    spam_score = min(spam_score + 0.3, 1.0)

        is_spam = spam_score >= 0.6

        return is_spam, spam_score

    def _check_phishing(
        self,
        text: str,
        headers: dict[str, Any] = None,
    ) -> tuple[bool, list[str]]:
        """Verifica se e phishing."""
        indicators_found = []

        for pattern in self.phishing_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                indicators_found.append(pattern)

        is_phishing = len(indicators_found) >= 2

        return is_phishing, indicators_found

    def _calculate_security_score(
        self,
        spam_score: float,
        is_phishing: bool,
        headers: dict[str, Any] = None,
    ) -> float:
        """Calcula score de seguranca."""
        score = 1.0

        # Penaliza por spam
        score -= spam_score * 0.3

        # Penaliza por phishing
        if is_phishing:
            score -= 0.5

        return max(score, 0.0)
