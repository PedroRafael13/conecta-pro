"""
Semantic Search Service - Sprint 53.

Servico de busca semantica usando embeddings.
"""

import hashlib
import logging
import math
import re
import time
from typing import Any

logger = logging.getLogger(__name__)


class SemanticSearchEngine:
    """
    Motor de busca semantica.

    Combina busca por embeddings vetoriais com
    busca tradicional por keywords.
    """

    def __init__(self):
        """Inicializa o motor de busca."""
        self.embedding_model = "all-MiniLM-L6-v2"
        self.vector_dimension = 384
        self.cache: dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutos

        # Stopwords em portugues
        self.stopwords = {
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
            "mas",
            "foi",
            "ao",
            "ele",
            "das",
            "tem",
            "seu",
            "sua",
            "ou",
            "ser",
            "quando",
            "muito",
            "ha",
            "nos",
            "ja",
            "esta",
            "eu",
            "tambem",
            "so",
            "pelo",
            "pela",
            "ate",
            "isso",
            "ela",
            "entre",
            "era",
            "depois",
            "sem",
            "mesmo",
            "aos",
            "ter",
            "seus",
            "quem",
            "nas",
            "me",
            "esse",
            "eles",
            "estao",
            "voce",
            "tinha",
            "foram",
            "essa",
            "num",
            "nem",
            "suas",
            "meu",
            "as",
            "minha",
            "numa",
            "pelos",
            "elas",
            "qual",
            "lhe",
            "deles",
            "essas",
            "esses",
            "pelas",
            "este",
            "dele",
            "tu",
            "te",
            "voces",
            "vos",
            "lhes",
        }

        # Sinonimos comuns
        self.synonyms = {
            "problema": ["erro", "falha", "bug", "defeito", "issue"],
            "acesso": ["entrada", "login", "autenticacao"],
            "pagamento": ["cobranca", "boleto", "fatura", "taxa"],
            "morador": ["condômino", "residente", "proprietário"],
            "visitante": ["convidado", "hóspede"],
            "manutencao": ["reparo", "conserto", "servico"],
            "reserva": ["agendamento", "booking"],
        }

    def generate_embedding(self, text: str) -> list[float]:
        """
        Gera embedding vetorial para texto.

        Simulacao - em producao usaria modelo real.
        """
        # Normaliza texto
        text_normalized = self._normalize_text(text)

        # Gera hash determinístico
        text_hash = hashlib.sha256(text_normalized.encode()).hexdigest()

        # Gera vetor pseudo-aleatorio baseado no hash
        embedding = []
        for i in range(self.vector_dimension):
            # Usa partes do hash para gerar valores
            idx = i % 32
            val = int(text_hash[idx], 16) / 15.0
            # Adiciona variacao baseada na posicao
            val = (val - 0.5) * 2 + math.sin(i * 0.1) * 0.1
            embedding.append(val)

        # Normaliza vetor
        magnitude = math.sqrt(sum(x * x for x in embedding))
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]

        return embedding

    def calculate_similarity(
        self,
        embedding1: list[float],
        embedding2: list[float],
    ) -> float:
        """
        Calcula similaridade cosseno entre dois embeddings.
        """
        if len(embedding1) != len(embedding2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(embedding1, embedding2, strict=False))
        magnitude1 = math.sqrt(sum(a * a for a in embedding1))
        magnitude2 = math.sqrt(sum(b * b for b in embedding2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return (dot_product / (magnitude1 * magnitude2) + 1) / 2  # 0-1

    def search(
        self,
        query: str,
        documents: list[dict[str, Any]],
        search_type: str = "hybrid",
        max_results: int = 10,
        min_score: float = 0.3,
    ) -> list[dict[str, Any]]:
        """
        Executa busca nos documentos.

        Args:
            query: Texto da busca
            documents: Lista de documentos para buscar
            search_type: Tipo de busca (semantic, keyword, hybrid)
            max_results: Maximo de resultados
            min_score: Score minimo para incluir

        Returns:
            Lista de resultados com scores
        """
        start_time = time.time()

        if not query or not documents:
            return []

        results = []

        # Busca semantica
        if search_type in ["semantic", "hybrid"]:
            query_embedding = self.generate_embedding(query)
            for doc in documents:
                if doc.get("embedding"):
                    score = self.calculate_similarity(
                        query_embedding,
                        doc["embedding"],
                    )
                    results.append(
                        {
                            "document": doc,
                            "semantic_score": score,
                            "keyword_score": 0.0,
                        }
                    )

        # Busca por keywords
        if search_type in ["keyword", "hybrid"]:
            query_tokens = self._tokenize(query)
            query_tokens_expanded = self._expand_query(query_tokens)

            for _i, doc in enumerate(documents):
                doc_text = f"{doc.get('title', '')} {doc.get('content', '')}".lower()
                doc_tokens = set(self._tokenize(doc_text))

                # Calcula score de keyword
                matches = query_tokens_expanded & doc_tokens
                if matches:
                    keyword_score = len(matches) / len(query_tokens_expanded)

                    # Encontra resultado existente ou cria novo
                    existing = next(
                        (r for r in results if r["document"].get("id") == doc.get("id")),
                        None,
                    )

                    if existing:
                        existing["keyword_score"] = keyword_score
                    else:
                        results.append(
                            {
                                "document": doc,
                                "semantic_score": 0.0,
                                "keyword_score": keyword_score,
                            }
                        )

        # Calcula score final
        for result in results:
            if search_type == "hybrid":
                # Combina scores com peso
                result["final_score"] = result["semantic_score"] * 0.6 + result["keyword_score"] * 0.4
            elif search_type == "semantic":
                result["final_score"] = result["semantic_score"]
            else:
                result["final_score"] = result["keyword_score"]

            # Encontra keywords que matcharam
            result["matched_keywords"] = self._find_matched_keywords(query, result["document"])

            # Gera highlights
            result["highlights"] = self._generate_highlights(query, result["document"])

        # Filtra e ordena
        results = [r for r in results if r["final_score"] >= min_score]
        results.sort(key=lambda x: x["final_score"], reverse=True)
        results = results[:max_results]

        processing_time = int((time.time() - start_time) * 1000)

        logger.info(
            f"Search completed: query='{query[:50]}', "
            f"type={search_type}, results={len(results)}, "
            f"time={processing_time}ms"
        )

        return results

    def search_similar(
        self,
        reference_embedding: list[float],
        documents: list[dict[str, Any]],
        max_results: int = 5,
        exclude_ids: list[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Busca documentos similares a um embedding de referencia.
        """
        exclude_ids = exclude_ids or []
        results = []

        for doc in documents:
            if doc.get("id") in exclude_ids:
                continue

            if doc.get("embedding"):
                score = self.calculate_similarity(
                    reference_embedding,
                    doc["embedding"],
                )
                results.append(
                    {
                        "document": doc,
                        "similarity_score": score,
                    }
                )

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:max_results]

    def suggest_queries(
        self,
        partial_query: str,
        popular_queries: list[str],
        max_suggestions: int = 5,
    ) -> list[str]:
        """
        Sugere queries baseado em texto parcial.
        """
        if not partial_query:
            return popular_queries[:max_suggestions]

        partial_lower = partial_query.lower()
        suggestions = []

        # Queries que comecam com o texto parcial
        for query in popular_queries:
            if query.lower().startswith(partial_lower):
                suggestions.append(query)

        # Queries que contem o texto parcial
        for query in popular_queries:
            if partial_lower in query.lower() and query not in suggestions:
                suggestions.append(query)

        return suggestions[:max_suggestions]

    def extract_entities(self, text: str) -> list[dict[str, Any]]:
        """
        Extrai entidades do texto.
        """
        entities = []

        # Padroes simples para entidades
        patterns = {
            "apartment": r"\b(?:apto?|apartamento|unidade)\s*\.?\s*(\d+[a-z]?)\b",
            "block": r"\b(?:bloco?|torre)\s*\.?\s*([a-z0-9]+)\b",
            "date": r"\b(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})\b",
            "time": r"\b(\d{1,2}:\d{2}(?::\d{2})?)\b",
            "phone": r"\b(\(?\d{2}\)?\s*\d{4,5}[\-\s]?\d{4})\b",
            "email": r"\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b",
        }

        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append(
                    {
                        "type": entity_type,
                        "value": match,
                        "normalized": match.lower().strip(),
                    }
                )

        return entities

    def detect_intent(self, query: str) -> dict[str, Any]:
        """
        Detecta intencao da query.
        """
        query_lower = query.lower()

        intents = {
            "how_to": ["como", "de que forma", "de que maneira", "qual o passo"],
            "what_is": ["o que e", "o que sao", "qual e", "quais sao"],
            "where": ["onde", "em qual", "em que lugar"],
            "when": ["quando", "a que horas", "em que data"],
            "why": ["por que", "porque", "por qual motivo"],
            "troubleshoot": ["problema", "erro", "nao funciona", "nao consigo"],
            "request": ["preciso", "gostaria", "quero", "solicitar"],
            "complaint": ["reclamar", "reclamacao", "insatisfeito"],
        }

        detected_intent = "general"
        confidence = 0.5

        for intent, keywords in intents.items():
            for keyword in keywords:
                if keyword in query_lower:
                    detected_intent = intent
                    confidence = 0.8
                    break
            if confidence > 0.5:
                break

        return {
            "intent": detected_intent,
            "confidence": confidence,
            "entities": self.extract_entities(query),
        }

    def _normalize_text(self, text: str) -> str:
        """Normaliza texto para processamento."""
        # Remove caracteres especiais
        text = re.sub(r"[^\w\s]", " ", text.lower())
        # Remove espacos multiplos
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _tokenize(self, text: str) -> list[str]:
        """Tokeniza texto removendo stopwords."""
        text = self._normalize_text(text)
        tokens = text.split()
        return [t for t in tokens if t not in self.stopwords and len(t) > 2]

    def _expand_query(self, tokens: list[str]) -> set:
        """Expande query com sinonimos."""
        expanded = set(tokens)
        for token in tokens:
            if token in self.synonyms:
                expanded.update(self.synonyms[token])
        return expanded

    def _find_matched_keywords(
        self,
        query: str,
        document: dict[str, Any],
    ) -> list[str]:
        """Encontra keywords que matcharam."""
        query_tokens = set(self._tokenize(query))
        doc_keywords = document.get("keywords", [])

        matched = []
        for keyword in doc_keywords:
            keyword_tokens = set(self._tokenize(keyword))
            if query_tokens & keyword_tokens:
                matched.append(keyword)

        return matched

    def _generate_highlights(
        self,
        query: str,
        document: dict[str, Any],
        max_highlights: int = 3,
    ) -> list[str]:
        """Gera highlights do texto."""
        content = document.get("content", "")
        if not content:
            return []

        query_tokens = set(self._tokenize(query))
        sentences = re.split(r"[.!?]", content)

        highlights = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sentence_tokens = set(self._tokenize(sentence))
            if query_tokens & sentence_tokens:
                # Limita tamanho
                if len(sentence) > 200:
                    sentence = sentence[:200] + "..."
                highlights.append(sentence)

                if len(highlights) >= max_highlights:
                    break

        return highlights

    def get_stats(self) -> dict[str, Any]:
        """Retorna estatisticas do motor."""
        return {
            "embedding_model": self.embedding_model,
            "vector_dimension": self.vector_dimension,
            "cache_size": len(self.cache),
            "stopwords_count": len(self.stopwords),
            "synonyms_count": len(self.synonyms),
        }
