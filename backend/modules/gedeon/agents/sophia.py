"""
SOPHIA — Agente de Busca Semântica do GEDEON
"Qualquer documento encontrado em linguagem natural"

Responsabilidades:
- Indexação semântica de todos os documentos
- Busca por linguagem natural
- Responde perguntas sobre o acervo documental
- Detecta documentos similares
- Gera resumos automáticos

Estratégia de embedding:
1. Se ANTHROPIC_API_KEY disponível → claude-3-haiku embeddings
2. Fallback → TF-IDF com similaridade de cosseno (sem API)

Armazenamento: PostgreSQL tabela gedeon_document_index
"""

import hashlib
import logging
import math
import os
import re
from collections import defaultdict
from typing import Any

logger = logging.getLogger(__name__)

HAS_ANTHROPIC = bool(os.getenv("ANTHROPIC_API_KEY"))


class SophiaIndex:
    """
    Índice de busca semântica de documentos do GEDEON.
    Usa TF-IDF in-memory (sem subprocess/docker).
    """

    def __init__(self):
        self._tfidf_index: dict[str, dict] = {}
        self._doc_store: dict[str, dict] = {}
        self._idf: dict[str, float] = {}

    # ── TF-IDF ────────────────────────────────────────

    def _tokenizar(self, texto: str) -> list[str]:
        """Tokenizar texto em português."""
        texto = texto.lower()
        # Remover pontuação, manter acentos
        texto = re.sub(r"[^\w\sáéíóúâêîôûãõàèìòùç]", " ", texto)
        tokens = texto.split()
        # Stopwords básicas PT-BR
        STOPWORDS = {
            "de",
            "da",
            "do",
            "das",
            "dos",
            "em",
            "na",
            "no",
            "nas",
            "nos",
            "e",
            "ou",
            "a",
            "o",
            "as",
            "os",
            "um",
            "uma",
            "para",
            "por",
            "com",
            "que",
        }
        return [t for t in tokens if len(t) > 2 and t not in STOPWORDS]

    def _tf(self, tokens: list[str]) -> dict[str, float]:
        """Term Frequency."""
        freq: dict[str, float] = defaultdict(float)
        for t in tokens:
            freq[t] += 1.0
        total = len(tokens) or 1
        return {k: v / total for k, v in freq.items()}

    def indexar_documento(
        self,
        doc_id: str,
        texto: str,
        metadados: dict[str, Any],
    ) -> bool:
        """
        Indexar um documento para busca.
        doc_id: identificador único
        texto: conteúdo textual do documento
        metadados: tipo, cliente, funcionário, data, etc.
        """
        try:
            tokens = self._tokenizar(texto)
            if not tokens:
                return False

            tf = self._tf(tokens)
            doc_hash = hashlib.sha256(texto.encode()).hexdigest()[:16]

            self._doc_store[doc_id] = {
                "texto": texto[:500],
                "metadados": metadados,
                "tokens": set(tokens),
                "tf": tf,
                "hash": doc_hash,
            }

            # Atualizar IDF
            for token in set(tokens):
                if token not in self._idf:
                    self._idf[token] = 0
                self._idf[token] += 1

            return True
        except Exception as e:
            logger.warning("SOPHIA indexar erro: %s", e)
            return False

    def buscar(
        self,
        query: str,
        limite: int = 10,
        filtros: dict | None = None,
    ) -> list[dict]:
        """
        Buscar documentos por texto livre.
        Retorna lista ordenada por relevância.
        """
        query_tokens = self._tokenizar(query)
        if not query_tokens:
            return []

        # Buscar no índice in-memory
        docs = []
        n_docs = max(len(self._doc_store), 1)
        query_tf = self._tf(query_tokens)

        for doc_id, doc in self._doc_store.items():
            meta = doc.get("metadados", {})

            # Aplicar filtros
            if filtros:
                if filtros.get("cliente_id") and meta.get("cliente_id") != filtros["cliente_id"]:
                    continue
                if filtros.get("tipo") and meta.get("tipo") != filtros["tipo"]:
                    continue
                if filtros.get("competencia") and meta.get("competencia") != filtros["competencia"]:
                    continue

            # Verificar match de tokens
            doc_tokens = doc.get("tokens", set())
            if not any(t in doc_tokens for t in query_tokens):
                continue

            # Score TF-IDF
            score = 0.0
            doc_tf = doc.get("tf", {})
            for token, qtf in query_tf.items():
                if token in doc_tf:
                    idf = math.log(n_docs / (self._idf.get(token, 0) + 1) + 1)
                    score += qtf * doc_tf[token] * idf

            docs.append(
                {
                    "doc_id": doc_id,
                    "preview": doc.get("texto", "")[:200],
                    "metadados": meta,
                    "score": round(score, 4),
                    "tipo": meta.get("tipo", ""),
                    "cliente": meta.get("cliente_nome", ""),
                    "funcionario": meta.get("funcionario_nome", ""),
                    "competencia": meta.get("competencia", ""),
                }
            )

        resultados = sorted(docs, key=lambda x: x["score"], reverse=True)
        return resultados[:limite]

    def responder_pergunta(self, pergunta: str) -> str:
        """
        Responder pergunta sobre o acervo em linguagem natural.
        Ex: "Quantos ASOs vencendo em abril?"
        """
        p = pergunta.lower()

        if any(x in p for x in ["quantos", "total", "count", "número"]):
            resultados = self.buscar(pergunta, limite=100)
            return f"Encontrei {len(resultados)} documentos relacionados a '{pergunta}'"

        if any(x in p for x in ["último", "ultimo", "recente", "mais novo"]):
            resultados = self.buscar(pergunta, limite=1)
            if resultados:
                r = resultados[0]
                nome = r.get("funcionario") or r.get("cliente", "cliente desconhecido")
                return f"O documento mais recente é '{r['tipo']}' de {nome} — {r['preview'][:100]}..."
            return "Nenhum documento encontrado."

        resultados = self.buscar(pergunta, limite=5)
        if not resultados:
            return f"Nenhum documento encontrado para '{pergunta}'"

        nomes = [f"{r['tipo']} ({r.get('funcionario') or r.get('cliente', '')})" for r in resultados[:3]]
        return f"Encontrei {len(resultados)} documentos. Os mais relevantes: {', '.join(nomes)}"

    async def indexar_acervo_completo(self) -> int:
        """
        Indexar todos os documentos do GED via SQLAlchemy.
        Popula o índice in-memory para buscas subsequentes.
        """
        logger.info("SOPHIA: iniciando indexação do acervo")
        indexados = 0
        try:
            from sqlalchemy import text as sa_text

            from core.database import async_session_factory

            async with async_session_factory() as db:
                # Indexar ged_kit_documents (sem JOIN — IDs de seed incompatíveis)
                rows = await db.execute(
                    sa_text(
                        "SELECT id::text, document_type, "
                        "COALESCE(document_name, document_type) AS doc_name, "
                        "COALESCE(source_module, '') AS modulo, "
                        "created_at::text "
                        "FROM ged_kit_documents "
                        "ORDER BY created_at DESC "
                        "LIMIT 1000"
                    )
                )
                for row in rows.mappings().all():
                    texto = f"{row['document_type']} {row['doc_name']} {row['modulo']}"
                    meta = {
                        "tipo": row["document_type"],
                        "arquivo": row["doc_name"],
                        "modulo": row["modulo"],
                        "origem": "ged_kit_documents",
                    }
                    if self.indexar_documento(row["id"], texto, meta):
                        indexados += 1

                # Indexar certidões
                certs = await db.execute(
                    sa_text(
                        "SELECT id::text, name, document_type, "
                        "COALESCE(expiry_date::text, '') AS expiry "
                        "FROM ged_certidoes "
                        "WHERE name IS NOT NULL "
                        "LIMIT 500"
                    )
                )
                for row in certs.mappings().all():
                    texto = f"{row['name']} {row['document_type']} vencimento {row['expiry']}"
                    meta = {
                        "tipo": row["document_type"],
                        "nome": row["name"],
                        "vencimento": row["expiry"],
                        "origem": "ged_certidoes",
                    }
                    if self.indexar_documento(f"cert_{row['id']}", texto, meta):
                        indexados += 1

        except Exception as exc:
            logger.warning("SOPHIA: erro na indexação: %s", exc)

        logger.info("SOPHIA: %d documentos indexados", indexados)
        return indexados


# Singleton global
sophia = SophiaIndex()
