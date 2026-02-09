"""
Article Generator Service - Sprint 53.

Servico de geracao de artigos e conteudo com IA.
"""

import logging
import re
import time
from typing import Any

logger = logging.getLogger(__name__)


class ArticleGenerator:
    """
    Gerador de artigos e conteudo.

    Gera artigos, resumos, FAQs e outro conteudo
    para a base de conhecimento.
    """

    def __init__(self):
        """Inicializa o gerador."""
        self.supported_types = [
            "how_to",
            "tutorial",
            "guide",
            "faq",
            "summary",
            "glossary",
        ]

        # Templates de artigo
        self.article_templates = {
            "how_to": {
                "structure": [
                    "Introdução",
                    "Pré-requisitos",
                    "Passo a passo",
                    "Dicas importantes",
                    "Conclusão",
                ],
                "intro_template": "Este guia mostra como {topic}. Siga os passos abaixo para completar a tarefa.",
            },
            "tutorial": {
                "structure": [
                    "Visão geral",
                    "O que você vai aprender",
                    "Requisitos",
                    "Configuração inicial",
                    "Desenvolvimento",
                    "Teste e validação",
                    "Próximos passos",
                ],
                "intro_template": "Neste tutorial, você aprenderá sobre {topic}.",
            },
            "guide": {
                "structure": [
                    "Introdução",
                    "Conceitos principais",
                    "Como funciona",
                    "Exemplos práticos",
                    "Boas práticas",
                    "Referências",
                ],
                "intro_template": "Este guia aborda {topic} de forma completa e prática.",
            },
            "faq": {
                "structure": [
                    "Perguntas frequentes",
                    "Dúvidas sobre uso",
                    "Problemas comuns",
                    "Outras questões",
                ],
                "intro_template": "Confira as perguntas mais frequentes sobre {topic}.",
            },
        }

    def generate_article_structure(
        self,
        topic: str,
        article_type: str = "guide",
        additional_context: str = None,
    ) -> dict[str, Any]:
        """
        Gera estrutura de artigo.

        Args:
            topic: Topico do artigo
            article_type: Tipo de artigo
            additional_context: Contexto adicional

        Returns:
            Estrutura do artigo
        """
        start_time = time.time()

        if article_type not in self.article_templates:
            article_type = "guide"

        template = self.article_templates[article_type]

        # Gera titulo
        title = self._generate_title(topic, article_type)

        # Gera secoes
        sections = []
        for section_name in template["structure"]:
            section = {
                "title": section_name,
                "content_suggestion": self._suggest_section_content(section_name, topic, article_type),
                "estimated_length": self._estimate_section_length(section_name),
            }
            sections.append(section)

        # Gera introducao
        intro = template["intro_template"].format(topic=topic)

        # Gera keywords sugeridas
        keywords = self._extract_keywords_from_topic(topic)

        # Gera tags sugeridas
        tags = self._suggest_tags(topic, article_type)

        processing_time = int((time.time() - start_time) * 1000)

        return {
            "title": title,
            "suggested_slug": self._generate_slug(title),
            "article_type": article_type,
            "introduction": intro,
            "sections": sections,
            "suggested_keywords": keywords,
            "suggested_tags": tags,
            "estimated_reading_time": self._estimate_reading_time(sections),
            "processing_time_ms": processing_time,
        }

    def generate_summary(
        self,
        content: str,
        max_length: int = 200,
        style: str = "informative",
    ) -> dict[str, Any]:
        """
        Gera resumo de conteudo.

        Args:
            content: Conteudo a resumir
            max_length: Tamanho maximo do resumo
            style: Estilo do resumo (informative, concise, detailed)

        Returns:
            Resumo gerado
        """
        start_time = time.time()

        # Extrai frases principais
        sentences = self._split_sentences(content)

        # Pontua frases por relevancia
        scored_sentences = []
        for sentence in sentences:
            score = self._score_sentence(sentence, content)
            scored_sentences.append((sentence, score))

        # Ordena por score
        scored_sentences.sort(key=lambda x: x[1], reverse=True)

        # Seleciona frases para o resumo
        summary_sentences = []
        current_length = 0

        for sentence, _score in scored_sentences:
            if current_length + len(sentence) <= max_length:
                summary_sentences.append(sentence)
                current_length += len(sentence) + 1
            else:
                break

        # Reordena na ordem original
        original_order = []
        for sentence in sentences:
            if sentence in summary_sentences:
                original_order.append(sentence)

        summary = " ".join(original_order)

        # Ajusta tamanho se necessario
        if len(summary) > max_length:
            summary = summary[: max_length - 3] + "..."

        processing_time = int((time.time() - start_time) * 1000)

        return {
            "summary": summary,
            "original_length": len(content),
            "summary_length": len(summary),
            "compression_ratio": len(summary) / len(content) if content else 0,
            "sentences_used": len(summary_sentences),
            "processing_time_ms": processing_time,
        }

    def generate_faq_from_content(
        self,
        content: str,
        max_faqs: int = 5,
        topic: str = None,
    ) -> dict[str, Any]:
        """
        Gera FAQs a partir de conteudo.

        Args:
            content: Conteudo fonte
            max_faqs: Numero maximo de FAQs
            topic: Topico para contexto

        Returns:
            Lista de FAQs geradas
        """
        start_time = time.time()

        faqs = []

        # Extrai frases que parecem respostas
        sentences = self._split_sentences(content)

        # Identifica frases informativas
        informative_sentences = []
        for sentence in sentences:
            if self._is_informative(sentence):
                informative_sentences.append(sentence)

        # Gera pergunta para cada frase informativa
        for sentence in informative_sentences[:max_faqs]:
            question = self._generate_question_for_answer(sentence, topic)
            if question:
                faqs.append(
                    {
                        "question": question,
                        "answer": sentence,
                        "answer_short": sentence[:200] if len(sentence) > 200 else sentence,
                        "confidence": 0.7,
                        "source": "ai_generated",
                    }
                )

        processing_time = int((time.time() - start_time) * 1000)

        return {
            "faqs": faqs,
            "total_generated": len(faqs),
            "source_length": len(content),
            "processing_time_ms": processing_time,
        }

    def generate_keywords(
        self,
        content: str,
        max_keywords: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Extrai keywords de conteudo.

        Args:
            content: Conteudo para extrair keywords
            max_keywords: Numero maximo de keywords

        Returns:
            Lista de keywords com scores
        """
        # Tokeniza e conta
        words = self._tokenize(content)
        word_freq = {}

        for word in words:
            if len(word) >= 3:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Ordena por frequencia
        sorted_words = sorted(
            word_freq.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        # Formata resultado
        keywords = []
        total_words = len(words)

        for word, count in sorted_words[:max_keywords]:
            keywords.append(
                {
                    "keyword": word,
                    "frequency": count,
                    "relevance": count / total_words if total_words > 0 else 0,
                }
            )

        return keywords

    def suggest_related_topics(
        self,
        topic: str,
        existing_topics: list[str] = None,
        max_suggestions: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Sugere topicos relacionados.

        Args:
            topic: Topico de referencia
            existing_topics: Topicos ja existentes
            max_suggestions: Numero maximo de sugestoes

        Returns:
            Lista de topicos sugeridos
        """
        existing_topics = existing_topics or []
        suggestions = []

        # Padroes de topicos relacionados
        patterns = [
            f"Como configurar {topic}",
            f"Problemas comuns com {topic}",
            f"Boas práticas para {topic}",
            f"Guia completo de {topic}",
            f"FAQ sobre {topic}",
            f"Introdução a {topic}",
            f"Avançado: {topic}",
            f"Dicas de {topic}",
        ]

        for pattern in patterns:
            if pattern not in existing_topics:
                suggestions.append(
                    {
                        "topic": pattern,
                        "type": self._detect_article_type(pattern),
                        "relevance": 0.8,
                    }
                )

                if len(suggestions) >= max_suggestions:
                    break

        return suggestions

    def improve_content(
        self,
        content: str,
        improvements: list[str] = None,
    ) -> dict[str, Any]:
        """
        Sugere melhorias para conteudo.

        Args:
            content: Conteudo a melhorar
            improvements: Tipos de melhoria desejados

        Returns:
            Sugestoes de melhoria
        """
        improvements = improvements or ["readability", "structure", "seo"]
        suggestions = []

        # Analisa legibilidade
        if "readability" in improvements:
            readability = self._analyze_readability(content)
            if readability["score"] < 60:
                suggestions.append(
                    {
                        "type": "readability",
                        "issue": "Texto pode ser difícil de ler",
                        "suggestion": "Considere usar frases mais curtas e palavras simples",
                        "priority": "high",
                    }
                )

        # Analisa estrutura
        if "structure" in improvements:
            structure = self._analyze_structure(content)
            if not structure["has_headings"]:
                suggestions.append(
                    {
                        "type": "structure",
                        "issue": "Falta de títulos e subtítulos",
                        "suggestion": "Adicione títulos para organizar o conteúdo",
                        "priority": "medium",
                    }
                )

        # Analisa SEO
        if "seo" in improvements:
            if len(content) < 300:
                suggestions.append(
                    {
                        "type": "seo",
                        "issue": "Conteúdo muito curto",
                        "suggestion": "Expanda o conteúdo para pelo menos 300 palavras",
                        "priority": "high",
                    }
                )

        return {
            "suggestions": suggestions,
            "total_issues": len(suggestions),
            "priority_breakdown": self._count_priorities(suggestions),
        }

    def _generate_title(self, topic: str, article_type: str) -> str:
        """Gera titulo para artigo."""
        prefixes = {
            "how_to": "Como",
            "tutorial": "Tutorial:",
            "guide": "Guia:",
            "faq": "FAQ:",
        }
        prefix = prefixes.get(article_type, "")
        if prefix:
            return f"{prefix} {topic}"
        return topic.title()

    def _generate_slug(self, title: str) -> str:
        """Gera slug a partir do titulo."""
        slug = title.lower()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        return slug[:100]

    def _suggest_section_content(
        self,
        section_name: str,
        topic: str,
        article_type: str,
    ) -> str:
        """Sugere conteudo para secao."""
        suggestions = {
            "Introdução": f"Apresente o tema {topic} e por que é importante.",
            "Pré-requisitos": "Liste o que o leitor precisa saber ou ter antes de começar.",
            "Passo a passo": "Descreva cada etapa de forma clara e numerada.",
            "Dicas importantes": "Adicione dicas úteis e avisos importantes.",
            "Conclusão": "Resuma os pontos principais e sugira próximos passos.",
            "Visão geral": f"Explique o que é {topic} de forma geral.",
            "Conceitos principais": "Defina os termos e conceitos importantes.",
            "Como funciona": "Explique o funcionamento de forma detalhada.",
            "Exemplos práticos": "Forneça exemplos reais de uso.",
            "Boas práticas": "Liste recomendações e melhores práticas.",
        }
        return suggestions.get(section_name, f"Descreva {section_name} relacionado a {topic}.")

    def _estimate_section_length(self, section_name: str) -> int:
        """Estima tamanho da secao em palavras."""
        lengths = {
            "Introdução": 100,
            "Pré-requisitos": 50,
            "Passo a passo": 300,
            "Dicas importantes": 100,
            "Conclusão": 80,
            "Visão geral": 150,
            "Conceitos principais": 200,
            "Como funciona": 250,
            "Exemplos práticos": 200,
            "Boas práticas": 150,
        }
        return lengths.get(section_name, 100)

    def _estimate_reading_time(self, sections: list[dict[str, Any]]) -> int:
        """Estima tempo de leitura em minutos."""
        total_words = sum(s.get("estimated_length", 100) for s in sections)
        return max(1, total_words // 200)  # ~200 palavras por minuto

    def _extract_keywords_from_topic(self, topic: str) -> list[str]:
        """Extrai keywords do topico."""
        words = self._tokenize(topic)
        return [w for w in words if len(w) >= 3]

    def _suggest_tags(self, topic: str, article_type: str) -> list[str]:
        """Sugere tags para artigo."""
        tags = [article_type]
        words = self._tokenize(topic)
        tags.extend(words[:3])
        return list(set(tags))

    def _split_sentences(self, text: str) -> list[str]:
        """Divide texto em frases."""
        sentences = re.split(r"[.!?]+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _score_sentence(self, sentence: str, full_content: str) -> float:
        """Pontua relevancia de frase."""
        score = 0.0

        # Tamanho adequado
        words = len(sentence.split())
        if 10 <= words <= 30:
            score += 0.3

        # Posicao no texto
        position = full_content.find(sentence)
        if position < len(full_content) * 0.3:  # Primeiro terco
            score += 0.2

        # Contem palavras importantes
        important_words = ["importante", "essencial", "principal", "deve", "precisa"]
        for word in important_words:
            if word in sentence.lower():
                score += 0.1

        return min(score, 1.0)

    def _is_informative(self, sentence: str) -> bool:
        """Verifica se frase e informativa."""
        # Muito curta
        if len(sentence.split()) < 5:
            return False

        # Parece pergunta
        if sentence.strip().endswith("?"):
            return False

        # Contem informacao
        info_patterns = [
            r"\b(?:é|são|significa|representa)\b",
            r"\b(?:pode|deve|precisa|necessita)\b",
            r"\b(?:funciona|trabalha|opera)\b",
        ]
        for pattern in info_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                return True

        return len(sentence.split()) >= 8

    def _generate_question_for_answer(
        self,
        answer: str,
        topic: str = None,
    ) -> str | None:
        """Gera pergunta para uma resposta."""
        # Padroes de transformacao
        if "é" in answer.lower() or "são" in answer.lower():
            subject = answer.split()[0:3]
            return f"O que {' '.join(subject)}?"

        if "deve" in answer.lower() or "precisa" in answer.lower():
            return f"O que é necessário para {topic or 'isso'}?"

        if "funciona" in answer.lower():
            return f"Como funciona {topic or 'isso'}?"

        # Pergunta generica
        if topic:
            return f"Como funciona {topic}?"

        return None

    def _tokenize(self, text: str) -> list[str]:
        """Tokeniza texto."""
        text = re.sub(r"[^\w\s]", " ", text.lower())
        stopwords = {"a", "o", "e", "de", "da", "do", "em", "um", "uma", "para", "com"}
        words = text.split()
        return [w for w in words if w not in stopwords]

    def _detect_article_type(self, topic: str) -> str:
        """Detecta tipo de artigo pelo topico."""
        topic_lower = topic.lower()
        if "como" in topic_lower:
            return "how_to"
        if "tutorial" in topic_lower:
            return "tutorial"
        if "faq" in topic_lower:
            return "faq"
        if "guia" in topic_lower:
            return "guide"
        return "guide"

    def _analyze_readability(self, content: str) -> dict[str, Any]:
        """Analisa legibilidade do texto."""
        sentences = self._split_sentences(content)
        words = content.split()

        avg_sentence_length = len(words) / len(sentences) if sentences else 0

        # Score simplificado (baseado em tamanho medio de frase)
        score = 100 - (avg_sentence_length - 15) * 2
        score = max(0, min(100, score))

        return {
            "score": score,
            "average_sentence_length": avg_sentence_length,
            "total_sentences": len(sentences),
            "total_words": len(words),
        }

    def _analyze_structure(self, content: str) -> dict[str, Any]:
        """Analisa estrutura do texto."""
        has_headings = bool(re.search(r"^#+\s|^[A-Z][^.]*:$", content, re.MULTILINE))
        has_lists = "•" in content or "- " in content or re.search(r"^\d+\.", content, re.MULTILINE)
        paragraphs = content.count("\n\n") + 1

        return {
            "has_headings": has_headings,
            "has_lists": has_lists,
            "paragraph_count": paragraphs,
        }

    def _count_priorities(self, suggestions: list[dict[str, Any]]) -> dict[str, int]:
        """Conta sugestoes por prioridade."""
        counts = {"high": 0, "medium": 0, "low": 0}
        for s in suggestions:
            priority = s.get("priority", "low")
            counts[priority] = counts.get(priority, 0) + 1
        return counts
