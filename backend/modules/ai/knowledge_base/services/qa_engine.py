"""
QA Engine Service - Sprint 53.

Motor de perguntas e respostas com IA.
"""

import logging
import re
import time
from datetime import datetime
from typing import Any
from uuid import UUID

from modules.ai.knowledge_base.services.semantic_search import SemanticSearchEngine

logger = logging.getLogger(__name__)


class QAEngine:
    """
    Motor de perguntas e respostas.

    Processa perguntas em linguagem natural e
    gera respostas baseadas na base de conhecimento.
    """

    def __init__(self):
        """Inicializa o motor Q&A."""
        self.search_engine = SemanticSearchEngine()
        self.confidence_threshold = 0.6
        self.max_context_length = 2000

        # Templates de resposta
        self.response_templates = {
            "direct": "Com base nas informações disponíveis: {answer}",
            "article": "Encontrei um artigo que pode ajudar: {title}\n\n{excerpt}",
            "faq": "Essa pergunta é frequente! {answer}",
            "multiple": "Encontrei várias informações relevantes:\n\n{items}",
            "no_answer": "Não encontrei uma resposta específica para sua pergunta. Posso ajudar de outra forma?",
            "clarification": "Para ajudá-lo melhor, poderia esclarecer: {question}",
        }

        # Perguntas de esclarecimento
        self.clarification_patterns = {
            "acesso": "Você se refere a acesso físico (portaria) ou acesso ao sistema?",
            "pagamento": "Qual tipo de pagamento: taxa condominial, reserva ou outro?",
            "problema": "Poderia descrever o problema com mais detalhes?",
            "reserva": "Qual área você gostaria de reservar?",
        }

    def process_question(
        self,
        question: str,
        articles: list[dict[str, Any]],
        faqs: list[dict[str, Any]],
        context: dict[str, Any] = None,
        session_history: list[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Processa uma pergunta e gera resposta.

        Args:
            question: Pergunta do usuario
            articles: Artigos disponiveis para busca
            faqs: FAQs disponiveis para busca
            context: Contexto adicional
            session_history: Historico da sessao

        Returns:
            Resposta com metadados
        """
        start_time = time.time()
        context = context or {}
        session_history = session_history or []

        # Analisa pergunta
        intent_analysis = self.search_engine.detect_intent(question)

        # Verifica se precisa esclarecimento
        clarification = self._check_need_clarification(question, context)
        if clarification:
            return self._build_response(
                response_type="clarification_needed",
                answer=clarification,
                confidence=0.5,
                processing_time_ms=int((time.time() - start_time) * 1000),
            )

        # Prepara query com contexto
        enhanced_query = self._enhance_query(question, context, session_history)

        # Busca em FAQs (prioridade)
        faq_results = self._search_faqs(enhanced_query, faqs)

        # Busca em artigos
        article_results = self._search_articles(enhanced_query, articles)

        # Gera resposta baseada nos resultados
        response = self._generate_response(
            question=question,
            faq_results=faq_results,
            article_results=article_results,
            intent=intent_analysis,
            context=context,
        )

        # Gera follow-ups e sugestoes
        response["follow_up_questions"] = self._generate_follow_ups(question, response, context)
        response["suggestions"] = self._generate_suggestions(question, faq_results, article_results)

        # Calcula tempo de processamento
        response["processing_time_ms"] = int((time.time() - start_time) * 1000)

        logger.info(
            f"Q&A processed: question='{question[:50]}...', "
            f"type={response['response_type']}, "
            f"confidence={response['confidence_score']:.2f}, "
            f"time={response['processing_time_ms']}ms"
        )

        return response

    def _search_faqs(
        self,
        query: str,
        faqs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Busca FAQs relevantes."""
        if not faqs:
            return []

        # Prepara documentos para busca
        documents = []
        for faq in faqs:
            doc = {
                "id": str(faq.get("id", "")),
                "type": "faq",
                "title": faq.get("question", ""),
                "content": f"{faq.get('question', '')} {faq.get('answer', '')}",
                "embedding": faq.get("question_embedding"),
                "keywords": faq.get("keywords", []),
                "original": faq,
            }
            documents.append(doc)

        # Executa busca
        results = self.search_engine.search(
            query=query,
            documents=documents,
            search_type="hybrid",
            max_results=5,
            min_score=0.4,
        )

        # Formata resultados
        formatted = []
        for result in results:
            original = result["document"]["original"]
            formatted.append(
                {
                    "id": original.get("id"),
                    "question": original.get("question"),
                    "answer": original.get("answer"),
                    "answer_short": original.get("answer_short"),
                    "relevance_score": result["final_score"],
                    "confidence": min(result["final_score"] * 1.2, 1.0),
                    "matched_variation": None,
                }
            )

        return formatted

    def _search_articles(
        self,
        query: str,
        articles: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Busca artigos relevantes."""
        if not articles:
            return []

        # Prepara documentos para busca
        documents = []
        for article in articles:
            doc = {
                "id": str(article.get("id", "")),
                "type": "article",
                "title": article.get("title", ""),
                "content": f"{article.get('title', '')} {article.get('content', '')}",
                "embedding": article.get("embedding"),
                "keywords": article.get("keywords", []),
                "original": article,
            }
            documents.append(doc)

        # Executa busca
        results = self.search_engine.search(
            query=query,
            documents=documents,
            search_type="hybrid",
            max_results=5,
            min_score=0.3,
        )

        # Formata resultados
        formatted = []
        for result in results:
            original = result["document"]["original"]
            formatted.append(
                {
                    "id": original.get("id"),
                    "title": original.get("title"),
                    "excerpt": original.get("excerpt") or original.get("summary", "")[:200],
                    "article_type": original.get("article_type"),
                    "relevance_score": result["final_score"],
                    "matched_keywords": result.get("matched_keywords", []),
                    "highlights": result.get("highlights", []),
                }
            )

        return formatted

    def _generate_response(
        self,
        question: str,
        faq_results: list[dict[str, Any]],
        article_results: list[dict[str, Any]],
        intent: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Gera resposta baseada nos resultados."""
        # Verifica se tem FAQ com alta confianca
        if faq_results and faq_results[0]["confidence"] >= self.confidence_threshold:
            best_faq = faq_results[0]
            return self._build_response(
                response_type="faq_match",
                answer=best_faq["answer"],
                answer_formatted=self._format_answer(best_faq["answer"]),
                confidence=best_faq["confidence"],
                sources=[{"type": "faq", "id": best_faq["id"]}],
                matched_faqs=faq_results[:3],
                matched_articles=article_results[:3],
            )

        # Verifica se tem artigo relevante
        if article_results and article_results[0]["relevance_score"] >= 0.5:
            best_article = article_results[0]
            answer = self._extract_answer_from_article(question, best_article)
            return self._build_response(
                response_type="article_match",
                answer=answer,
                answer_formatted=self._format_answer(answer),
                confidence=best_article["relevance_score"] * 0.9,
                sources=[{"type": "article", "id": best_article["id"]}],
                matched_faqs=faq_results[:3],
                matched_articles=article_results[:3],
            )

        # Verifica se tem resultados combinados
        if faq_results or article_results:
            combined_answer = self._generate_combined_answer(question, faq_results, article_results)
            confidence = max(
                (faq_results[0]["confidence"] if faq_results else 0) * 0.8,
                (article_results[0]["relevance_score"] if article_results else 0) * 0.7,
            )
            return self._build_response(
                response_type="generated",
                answer=combined_answer,
                answer_formatted=self._format_answer(combined_answer),
                confidence=confidence,
                sources=self._collect_sources(faq_results, article_results),
                matched_faqs=faq_results[:3],
                matched_articles=article_results[:3],
            )

        # Sem resultados
        return self._build_response(
            response_type="no_answer",
            answer=self.response_templates["no_answer"],
            confidence=0.0,
            matched_faqs=[],
            matched_articles=[],
        )

    def _build_response(
        self,
        response_type: str,
        answer: str,
        confidence: float,
        answer_formatted: str = None,
        sources: list[dict[str, Any]] = None,
        matched_faqs: list[dict[str, Any]] = None,
        matched_articles: list[dict[str, Any]] = None,
        processing_time_ms: int = 0,
    ) -> dict[str, Any]:
        """Constroi objeto de resposta."""
        return {
            "response_type": response_type,
            "answer": answer,
            "answer_formatted": answer_formatted or answer,
            "confidence_score": confidence,
            "sources": sources or [],
            "matched_faqs": matched_faqs or [],
            "matched_articles": matched_articles or [],
            "follow_up_questions": [],
            "suggestions": [],
            "processing_time_ms": processing_time_ms,
        }

    def _check_need_clarification(
        self,
        question: str,
        context: dict[str, Any],
    ) -> str | None:
        """Verifica se precisa de esclarecimento."""
        question_lower = question.lower()

        # Pergunta muito curta
        if len(question.split()) < 3:
            for pattern, clarification in self.clarification_patterns.items():
                if pattern in question_lower:
                    return clarification

        return None

    def _enhance_query(
        self,
        question: str,
        context: dict[str, Any],
        history: list[dict[str, Any]],
    ) -> str:
        """Melhora query com contexto."""
        enhanced = question

        # Adiciona contexto da pagina
        if context.get("page"):
            enhanced = f"{question} (contexto: {context['page']})"

        # Referencia a mensagens anteriores
        if history and len(history) > 0:
            last_topic = history[-1].get("topic", "")
            if last_topic and len(question.split()) < 5:
                enhanced = f"{question} (relacionado a: {last_topic})"

        return enhanced

    def _extract_answer_from_article(
        self,
        question: str,
        article: dict[str, Any],
    ) -> str:
        """Extrai resposta relevante do artigo."""
        # Usa excerpt se disponivel
        if article.get("excerpt"):
            return f"De acordo com o artigo '{article['title']}':\n\n{article['excerpt']}"

        # Usa highlights
        if article.get("highlights"):
            highlights_text = "\n".join(f"• {h}" for h in article["highlights"][:3])
            return f"Encontrei estas informações no artigo '{article['title']}':\n\n{highlights_text}"

        return f"Encontrei o artigo '{article['title']}' que pode ajudar com sua pergunta."

    def _generate_combined_answer(
        self,
        question: str,
        faqs: list[dict[str, Any]],
        articles: list[dict[str, Any]],
    ) -> str:
        """Gera resposta combinando multiplas fontes."""
        parts = []

        if faqs:
            parts.append("**Informações encontradas:**\n")
            for faq in faqs[:2]:
                short_answer = faq.get("answer_short") or faq.get("answer", "")[:200]
                parts.append(f"• {short_answer}")

        if articles:
            parts.append("\n**Artigos relacionados:**\n")
            for article in articles[:2]:
                parts.append(f"• {article['title']}")

        if not parts:
            return self.response_templates["no_answer"]

        return "\n".join(parts)

    def _collect_sources(
        self,
        faqs: list[dict[str, Any]],
        articles: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Coleta fontes usadas na resposta."""
        sources = []

        for faq in faqs[:3]:
            sources.append(
                {
                    "type": "faq",
                    "id": faq.get("id"),
                    "title": faq.get("question", "")[:100],
                }
            )

        for article in articles[:3]:
            sources.append(
                {
                    "type": "article",
                    "id": article.get("id"),
                    "title": article.get("title", "")[:100],
                }
            )

        return sources

    def _format_answer(self, answer: str) -> str:
        """Formata resposta para exibicao."""
        # Converte markdown basico para HTML simples
        formatted = answer

        # Bold
        formatted = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", formatted)

        # Listas
        formatted = re.sub(r"^• ", r"<li>", formatted, flags=re.MULTILINE)

        # Quebras de linha
        formatted = formatted.replace("\n\n", "</p><p>")
        formatted = formatted.replace("\n", "<br>")

        return f"<p>{formatted}</p>"

    def _generate_follow_ups(
        self,
        question: str,
        response: dict[str, Any],
        context: dict[str, Any],
    ) -> list[str]:
        """Gera perguntas de follow-up."""
        follow_ups = []

        # Baseado no tipo de resposta
        if response["response_type"] == "faq_match":
            follow_ups.append("Isso respondeu sua dúvida?")
            follow_ups.append("Precisa de mais detalhes?")

        elif response["response_type"] == "article_match":
            follow_ups.append("Gostaria de ver o artigo completo?")
            follow_ups.append("Tem alguma dúvida específica sobre este tema?")

        elif response["response_type"] == "no_answer":
            follow_ups.append("Poderia reformular sua pergunta?")
            follow_ups.append("Gostaria de falar com um atendente?")

        return follow_ups[:3]

    def _generate_suggestions(
        self,
        question: str,
        faqs: list[dict[str, Any]],
        articles: list[dict[str, Any]],
    ) -> list[str]:
        """Gera sugestoes de perguntas relacionadas."""
        suggestions = []

        # Baseado em FAQs relacionadas
        for faq in faqs[1:4]:  # Pula a primeira (ja usada)
            suggestions.append(faq.get("question", "")[:100])

        # Baseado em artigos
        for article in articles[1:3]:
            suggestions.append(f"Como funciona {article.get('title', '')[:50]}?")

        return suggestions[:5]

    def rate_response(
        self,
        interaction_id: UUID,
        is_helpful: bool,
        rating: int | None = None,
        feedback_text: str | None = None,
    ) -> dict[str, Any]:
        """Registra avaliacao de resposta."""
        return {
            "interaction_id": str(interaction_id),
            "is_helpful": is_helpful,
            "rating": rating,
            "feedback_text": feedback_text,
            "recorded_at": datetime.utcnow().isoformat(),
        }

    def get_stats(self) -> dict[str, Any]:
        """Retorna estatisticas do motor."""
        return {
            "confidence_threshold": self.confidence_threshold,
            "max_context_length": self.max_context_length,
            "search_engine_stats": self.search_engine.get_stats(),
        }
