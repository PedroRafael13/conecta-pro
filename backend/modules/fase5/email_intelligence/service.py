"""
modules/fase5/email_intelligence/service.py - Email Intelligence Service
========================================================================
Servico de inteligencia para emails com NLP
"""

import logging
import re
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from .enums import ActionType, EmailCategory, EmailIntent, EmailPriority, SentimentType
from .models import EmailAnalysis, EmailContext, EmailMessage, EmailSuggestion

logger = logging.getLogger(__name__)


class EmailIntelligenceService:
    """
    Servico de inteligencia para analise de emails.

    Responsabilidades:
    1. Classificar emails por categoria e prioridade
    2. Identificar intencao do remetente
    3. Extrair entidades (CNPJ, valores, datas)
    4. Analisar sentimento
    5. Sugerir respostas e acoes
    6. Manter contexto historico
    """

    def __init__(self):
        self._setup_patterns()
        self._setup_keywords()

    def _setup_patterns(self) -> None:
        """Configura padroes de regex para extracao."""
        self.patterns = {
            "cnpj": r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}",
            "cpf": r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}",
            "telefone": r"(?:\+55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}",
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "valor": r"R\$\s*[\d.,]+(?:\s*(?:mil|milhao|milhoes))?",
            "data": r"\d{1,2}/\d{1,2}/\d{2,4}",
            "cep": r"\d{5}-?\d{3}",
        }

    def _setup_keywords(self) -> None:
        """Configura keywords para classificacao."""
        self.category_keywords = {
            EmailCategory.PROPOSTA_COMERCIAL: [
                "proposta",
                "orcamento",
                "cotacao",
                "preco",
                "valores",
                "servicos",
                "contrato",
                "negociacao",
            ],
            EmailCategory.SOLICITACAO_ORCAMENTO: [
                "orcamento",
                "cotacao",
                "quanto custa",
                "valor",
                "precisa de",
                "gostaria de contratar",
            ],
            EmailCategory.RECLAMACAO: [
                "reclamacao",
                "insatisfeito",
                "problema",
                "nao funciona",
                "pessimo",
                "horrivel",
                "cancelar",
                "nunca mais",
            ],
            EmailCategory.LICITACAO: [
                "licitacao",
                "pregao",
                "edital",
                "proposta comercial",
                "certame",
                "habilitacao",
                "documentacao",
            ],
            EmailCategory.RH: [
                "funcionario",
                "contratacao",
                "admissao",
                "demissao",
                "ferias",
                "salario",
                "beneficio",
                "atestado",
            ],
            EmailCategory.FINANCEIRO: [
                "pagamento",
                "boleto",
                "nota fiscal",
                "fatura",
                "cobranca",
                "inadimplencia",
                "parcelamento",
            ],
        }

        self.intent_keywords = {
            EmailIntent.SOLICITAR_PROPOSTA: [
                "gostaria de receber",
                "solicito proposta",
                "envie orcamento",
                "preciso de uma proposta",
            ],
            EmailIntent.FAZER_RECLAMACAO: ["reclamo", "insatisfeito", "problema grave", "absurdo", "inaceitavel"],
            EmailIntent.RENOVAR_CONTRATO: ["renovacao", "prorrogacao", "novo contrato", "continuar"],
            EmailIntent.CANCELAR_SERVICO: ["cancelamento", "encerrar", "rescindir", "nao quero mais"],
        }

        self.urgency_keywords = [
            "urgente",
            "emergencia",
            "imediato",
            "agora",
            "hoje",
            "prazo",
            "deadline",
            "critico",
            "importante",
        ]

        self.negative_keywords = [
            "insatisfeito",
            "problema",
            "reclamacao",
            "pessimo",
            "horrivel",
            "nao funciona",
            "cancelar",
            "advogado",
            "procon",
            "processo",
        ]

        self.positive_keywords = [
            "obrigado",
            "excelente",
            "otimo",
            "satisfeito",
            "parabens",
            "recomendo",
            "gostei",
            "perfeito",
        ]

    async def analyze_email(self, email: EmailMessage) -> EmailAnalysis:
        """Analisa um email completo."""
        logger.info(f"Analyzing email: {email.message_id}")

        # Combinar subject e body para analise
        text = f"{email.subject} {email.body_text or ''}"
        text_lower = text.lower()

        # Classificar categoria
        category, category_conf = self._classify_category(text_lower)

        # Determinar prioridade
        priority, priority_conf = self._determine_priority(text_lower)

        # Identificar intent
        intent, secondary_intents, intent_conf = self._identify_intent(text_lower)

        # Analisar sentimento
        sentiment, sentiment_score = self._analyze_sentiment(text_lower)

        # Extrair entidades
        entities = self._extract_entities(text)

        # Extrair keywords
        keywords = self._extract_keywords(text_lower)

        # Gerar resumo
        summary = self._generate_summary(email.subject, text_lower[:500])

        # Criar analise
        analysis = EmailAnalysis(
            message_id=email.message_id,
            category=category,
            category_confidence=category_conf,
            priority=priority,
            priority_confidence=priority_conf,
            primary_intent=intent,
            secondary_intents=secondary_intents,
            intent_confidence=intent_conf,
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            entities=entities,
            keywords=keywords,
            summary=summary,
            is_urgent=priority == EmailPriority.URGENTE,
            requires_response=category != EmailCategory.SPAM,
            is_spam=category == EmailCategory.SPAM,
        )

        logger.info(f"Email analyzed: category={category.value}, priority={priority.value}, intent={intent.value}")

        return analysis

    def _classify_category(self, text: str) -> tuple[EmailCategory, Decimal]:
        """Classifica categoria do email."""
        scores = {}

        for category, keywords in self.category_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[category] = score

        if not scores:
            return EmailCategory.OUTROS, Decimal("0.5")

        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]
        confidence = min(Decimal("0.95"), Decimal(str(max_score)) / Decimal("5"))

        return best_category, confidence

    def _determine_priority(self, text: str) -> tuple[EmailPriority, Decimal]:
        """Determina prioridade do email."""
        urgency_count = sum(1 for kw in self.urgency_keywords if kw in text)
        negative_count = sum(1 for kw in self.negative_keywords if kw in text)

        if urgency_count >= 2 or negative_count >= 3:
            return EmailPriority.URGENTE, Decimal("0.9")
        elif urgency_count >= 1 or negative_count >= 2:
            return EmailPriority.ALTA, Decimal("0.8")
        elif negative_count >= 1:
            return EmailPriority.MEDIA, Decimal("0.7")
        else:
            return EmailPriority.BAIXA, Decimal("0.6")

    def _identify_intent(self, text: str) -> tuple[EmailIntent, list[EmailIntent], Decimal]:
        """Identifica intencao do email."""
        scores = {}

        for intent, keywords in self.intent_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[intent] = score

        if not scores:
            return EmailIntent.OUTRO, [], Decimal("0.5")

        sorted_intents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_intents[0][0]
        secondary = [i[0] for i in sorted_intents[1:3]]
        confidence = min(Decimal("0.9"), Decimal(str(sorted_intents[0][1])) / Decimal("3"))

        return primary, secondary, confidence

    def _analyze_sentiment(self, text: str) -> tuple[SentimentType, Decimal]:
        """Analisa sentimento do email."""
        positive_count = sum(1 for kw in self.positive_keywords if kw in text)
        negative_count = sum(1 for kw in self.negative_keywords if kw in text)
        urgency_count = sum(1 for kw in self.urgency_keywords if kw in text)

        # Calcular score (-1 a 1)
        total = positive_count + negative_count + 1
        score = (positive_count - negative_count) / total

        if urgency_count >= 2 and negative_count >= 1:
            return SentimentType.FRUSTRADO, Decimal(str(score))
        elif urgency_count >= 2:
            return SentimentType.URGENTE, Decimal(str(score))
        elif score > 0.3:
            return SentimentType.POSITIVO, Decimal(str(score))
        elif score < -0.3:
            return SentimentType.NEGATIVO, Decimal(str(score))
        else:
            return SentimentType.NEUTRO, Decimal(str(score))

    def _extract_entities(self, text: str) -> dict[str, list[str]]:
        """Extrai entidades do texto."""
        entities = {}

        for entity_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                entities[entity_type] = list(set(matches))

        return entities

    def _extract_keywords(self, text: str) -> list[str]:
        """Extrai keywords relevantes."""
        # Palavras comuns para ignorar
        stopwords = {
            "de",
            "a",
            "o",
            "que",
            "e",
            "do",
            "da",
            "em",
            "um",
            "para",
            "com",
            "nao",
            "uma",
            "os",
            "no",
            "se",
            "na",
            "por",
            "mais",
            "as",
            "dos",
            "como",
            "mas",
            "foi",
            "ao",
            "ele",
            "das",
            "tem",
        }

        words = re.findall(r"\b\w{4,}\b", text)
        keywords = [w for w in words if w not in stopwords]

        # Contar frequencia
        freq = {}
        for w in keywords:
            freq[w] = freq.get(w, 0) + 1

        # Retornar top 10
        sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [w[0] for w in sorted_words[:10]]

    def _generate_summary(self, subject: str, text: str) -> str:
        """Gera resumo do email."""
        # Simples: primeiras 200 caracteres relevantes
        clean_text = re.sub(r"\s+", " ", text).strip()
        summary = clean_text[:200]
        if len(clean_text) > 200:
            summary += "..."
        return f"{subject}: {summary}"

    async def generate_suggestions(self, email: EmailMessage, analysis: EmailAnalysis) -> list[EmailSuggestion]:
        """Gera sugestoes de acao para o email."""
        suggestions = []

        # Sugestao baseada na categoria
        if analysis.category == EmailCategory.PROPOSTA_COMERCIAL:
            suggestions.append(
                EmailSuggestion(
                    message_id=email.message_id,
                    analysis_id=analysis.analysis_id,
                    action_type=ActionType.CRIAR_PROPOSTA,
                    action_description="Criar proposta comercial baseada na solicitacao",
                    action_priority=1,
                    suggested_department="Comercial",
                    confidence=analysis.category_confidence,
                )
            )

        elif analysis.category == EmailCategory.RECLAMACAO:
            suggestions.append(
                EmailSuggestion(
                    message_id=email.message_id,
                    analysis_id=analysis.analysis_id,
                    action_type=ActionType.NOTIFICAR_EQUIPE,
                    action_description="Notificar equipe de suporte sobre reclamacao",
                    action_priority=1,
                    suggested_department="Suporte",
                    confidence=Decimal("0.9"),
                )
            )

        # Sugestao de resposta
        if analysis.requires_response:
            response_template = self._get_response_template(analysis)
            suggestions.append(
                EmailSuggestion(
                    message_id=email.message_id,
                    analysis_id=analysis.analysis_id,
                    action_type=ActionType.RESPONDER,
                    action_description="Responder email",
                    action_priority=2 if analysis.is_urgent else 5,
                    suggested_response=response_template,
                    confidence=Decimal("0.8"),
                )
            )

        return suggestions

    def _get_response_template(self, analysis: EmailAnalysis) -> str:
        """Retorna template de resposta baseado na analise."""
        templates = {
            EmailCategory.PROPOSTA_COMERCIAL: (
                "Prezado(a),\n\n"
                "Agradecemos o contato e seu interesse em nossos servicos.\n\n"
                "Estamos analisando sua solicitacao e em breve enviaremos "
                "uma proposta comercial detalhada.\n\n"
                "Atenciosamente,\nEquipe Comercial"
            ),
            EmailCategory.RECLAMACAO: (
                "Prezado(a),\n\n"
                "Recebemos sua mensagem e lamentamos qualquer inconveniente.\n\n"
                "Nossa equipe ja esta trabalhando para resolver a questao "
                "o mais rapido possivel.\n\n"
                "Atenciosamente,\nEquipe de Suporte"
            ),
            EmailCategory.SOLICITACAO_ORCAMENTO: (
                "Prezado(a),\n\n"
                "Agradecemos sua solicitacao de orcamento.\n\n"
                "Para elaborarmos uma proposta adequada as suas necessidades, "
                "poderia nos informar mais detalhes sobre o servico desejado?\n\n"
                "Atenciosamente,\nEquipe Comercial"
            ),
        }

        return templates.get(analysis.category, "Prezado(a),\n\nAgradecemos o contato.\n\nAtenciosamente")

    async def get_email_context(self, email_address: str, tenant_id: UUID) -> EmailContext:
        """Obtem contexto historico do email."""
        # Em producao, buscar do banco de dados
        context = EmailContext(email_address=email_address, total_emails_received=0, total_emails_sent=0)

        return context

    async def process_incoming_email(self, email: EmailMessage) -> dict[str, Any]:
        """Processa email recebido completo."""
        # Analisar email
        analysis = await self.analyze_email(email)

        # Gerar sugestoes
        suggestions = await self.generate_suggestions(email, analysis)

        # Obter contexto
        context = await self.get_email_context(str(email.from_address), email.tenant_id)

        return {
            "email_id": str(email.message_id),
            "analysis": analysis.model_dump(),
            "suggestions": [s.model_dump() for s in suggestions],
            "context": context.model_dump(),
            "processed_at": datetime.utcnow().isoformat(),
        }
