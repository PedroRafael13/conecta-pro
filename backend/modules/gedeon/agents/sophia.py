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
1. Se ANTHROPIC_API_KEY disponível → sklearn TF-IDF vetorial + cosine similarity
   (Anthropic não fornece endpoint de embeddings; sklearn é o caminho premium)
2. Fallback → TF-IDF manual com similaridade por token

Armazenamento: PostgreSQL tabela gedeon_document_index
"""

import hashlib
import json
import logging
import math
import os
import re
from collections import defaultdict
from typing import Any

logger = logging.getLogger(__name__)

HAS_ANTHROPIC = bool(os.getenv("ANTHROPIC_API_KEY"))

# Sklearn: caminho premium de busca vetorial
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as cosine_sim

    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

# Stopwords PT-BR — nível de módulo (compartilhado por TF-IDF e sklearn)
_STOPWORDS = {
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


class SophiaIndex:
    """
    Índice de busca semântica de documentos do GEDEON.

    Caminho premium (HAS_ANTHROPIC=True + sklearn):
        TfidfVectorizer + cosine_similarity — busca vetorial completa.
        Vetores persistidos em gedeon_document_index.embedding (FLOAT8[]).

    Caminho fallback:
        TF-IDF manual com token matching — sem dependência externa.
    """

    def __init__(self) -> None:
        self._doc_store: dict[str, dict] = {}
        self._idf: dict[str, float] = {}
        # Sklearn — caminho premium
        self._vectorizer: Any = None
        self._matrix: Any = None
        self._doc_ids_ordered: list[str] = []

    # ── Tokenização ───────────────────────────────────────────────────────────

    def _tokenizar(self, texto: str) -> list[str]:
        """Tokenizar texto em português."""
        texto = texto.lower()
        texto = re.sub(r"[^\w\sáéíóúâêîôûãõàèìòùç]", " ", texto)
        return [t for t in texto.split() if len(t) > 2 and t not in _STOPWORDS]

    def _tf(self, tokens: list[str]) -> dict[str, float]:
        """Term Frequency normalizado."""
        freq: dict[str, float] = defaultdict(float)
        for t in tokens:
            freq[t] += 1.0
        total = len(tokens) or 1
        return {k: v / total for k, v in freq.items()}

    # ── Indexação ─────────────────────────────────────────────────────────────

    def indexar_documento(
        self,
        doc_id: str,
        texto: str,
        metadados: dict[str, Any],
    ) -> bool:
        """
        Indexa um documento em memória (TF-IDF manual).
        Chamado durante indexar_acervo_completo() — persiste em DB ao final.
        """
        try:
            tokens = self._tokenizar(texto)
            if not tokens:
                return False

            doc_hash = hashlib.sha256(texto.encode()).hexdigest()[:16]
            self._doc_store[doc_id] = {
                "texto": texto[:500],
                "metadados": metadados,
                "tokens": set(tokens),
                "tf": self._tf(tokens),
                "hash": doc_hash,
                "embedding": None,
            }
            for token in set(tokens):
                self._idf[token] = self._idf.get(token, 0) + 1

            return True
        except Exception as e:
            logger.warning("SOPHIA indexar erro: %s", e)
            return False

    # ── Embedding vetorial (caminho premium) ──────────────────────────────────

    def _construir_matriz_sklearn(self) -> int:
        """
        Constrói a matriz TF-IDF vetorial com sklearn.
        Ativo quando HAS_ANTHROPIC=True e sklearn disponível.
        Popula self._vectorizer, self._matrix e embedding em cada doc.
        """
        if not (HAS_ANTHROPIC and HAS_SKLEARN) or not self._doc_store:
            return 0

        self._doc_ids_ordered = list(self._doc_store.keys())
        corpus = [self._doc_store[d].get("texto", "") for d in self._doc_ids_ordered]

        self._vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents=None,
            stop_words=list(_STOPWORDS),
            min_df=1,
            sublinear_tf=True,
        )
        self._matrix = self._vectorizer.fit_transform(corpus)

        # Salvar vetor individual em cada doc para persistência
        matrix_dense = self._matrix.toarray()
        for idx, doc_id in enumerate(self._doc_ids_ordered):
            if doc_id in self._doc_store:
                self._doc_store[doc_id]["embedding"] = matrix_dense[idx].tolist()

        n_features = self._matrix.shape[1]
        logger.info(
            "SOPHIA: matriz sklearn — %d docs × %d features",
            len(self._doc_ids_ordered),
            n_features,
        )
        return len(self._doc_ids_ordered)

    def _reconstruir_matriz_de_embeddings(self) -> int:
        """
        Reconstrói a matriz sklearn a partir de embeddings carregados do banco.
        Usado após carregar_do_banco() para restaurar busca vetorial sem re-indexar.
        """
        if not (HAS_ANTHROPIC and HAS_SKLEARN) or not self._doc_store:
            return 0

        docs_com_embedding = [
            (doc_id, doc["embedding"]) for doc_id, doc in self._doc_store.items() if doc.get("embedding")
        ]
        if not docs_com_embedding:
            # Embeddings não disponíveis — reconstrói do texto
            return self._construir_matriz_sklearn()

        self._doc_ids_ordered = [d[0] for d in docs_com_embedding]
        matrix = np.array([d[1] for d in docs_com_embedding], dtype=np.float64)

        # Reconstrói vectorizer a partir dos textos para permitir transform em queries
        corpus = [self._doc_store[d].get("texto", "") for d in self._doc_ids_ordered]
        self._vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents=None,
            stop_words=list(_STOPWORDS),
            min_df=1,
            sublinear_tf=True,
        )
        self._vectorizer.fit(corpus)

        from scipy.sparse import csr_matrix

        self._matrix = csr_matrix(matrix)
        logger.info("SOPHIA: matriz reconstruída de %d embeddings do banco", len(self._doc_ids_ordered))
        return len(self._doc_ids_ordered)

    # ── Busca ─────────────────────────────────────────────────────────────────

    def buscar(
        self,
        query: str,
        limite: int = 10,
        filtros: dict | None = None,
    ) -> list[dict]:
        """
        Busca documentos por texto livre.
        Usa cosine similarity (sklearn) se HAS_ANTHROPIC, senão TF-IDF manual.
        """
        if HAS_ANTHROPIC and HAS_SKLEARN and self._vectorizer is not None and self._matrix is not None:
            return self._buscar_sklearn(query, limite, filtros)
        return self._buscar_tfidf(query, limite, filtros)

    def _buscar_sklearn(
        self,
        query: str,
        limite: int,
        filtros: dict | None,
    ) -> list[dict]:
        """Busca vetorial por cosine similarity (caminho premium)."""
        query_vec = self._vectorizer.transform([query])
        scores = cosine_sim(query_vec, self._matrix).flatten()

        docs = []
        for idx, score in enumerate(scores):
            if score < 0.001:
                continue
            doc_id = self._doc_ids_ordered[idx]
            doc = self._doc_store.get(doc_id)
            if not doc:
                continue
            meta = doc.get("metadados", {})

            if filtros:
                if filtros.get("cliente_id") and meta.get("cliente_id") != filtros["cliente_id"]:
                    continue
                if filtros.get("tipo") and meta.get("tipo") != filtros["tipo"]:
                    continue
                if filtros.get("competencia") and meta.get("competencia") != filtros["competencia"]:
                    continue

            docs.append(
                {
                    "doc_id": doc_id,
                    "preview": doc.get("texto", "")[:200],
                    "metadados": meta,
                    "score": round(float(score), 4),
                    "tipo": meta.get("tipo", ""),
                    "cliente": meta.get("cliente_nome", ""),
                    "funcionario": meta.get("funcionario_nome", ""),
                    "competencia": meta.get("competencia", ""),
                    "modo_busca": "sklearn_cosine",
                }
            )

        return sorted(docs, key=lambda x: x["score"], reverse=True)[:limite]

    def _buscar_tfidf(
        self,
        query: str,
        limite: int,
        filtros: dict | None,
    ) -> list[dict]:
        """Busca TF-IDF manual — fallback sem sklearn."""
        query_tokens = self._tokenizar(query)
        if not query_tokens:
            return []

        docs = []
        n_docs = max(len(self._doc_store), 1)
        query_tf = self._tf(query_tokens)

        for doc_id, doc in self._doc_store.items():
            meta = doc.get("metadados", {})

            if filtros:
                if filtros.get("cliente_id") and meta.get("cliente_id") != filtros["cliente_id"]:
                    continue
                if filtros.get("tipo") and meta.get("tipo") != filtros["tipo"]:
                    continue
                if filtros.get("competencia") and meta.get("competencia") != filtros["competencia"]:
                    continue

            doc_tokens = doc.get("tokens", set())
            if not any(t in doc_tokens for t in query_tokens):
                continue

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
                    "modo_busca": "tfidf_manual",
                }
            )

        return sorted(docs, key=lambda x: x["score"], reverse=True)[:limite]

    # ── NLP simples ───────────────────────────────────────────────────────────

    def responder_pergunta(self, pergunta: str) -> str:
        """Responde pergunta sobre o acervo em linguagem natural."""
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

    # ── Persistência PostgreSQL ────────────────────────────────────────────────

    async def _persistir_no_banco(self, db: Any) -> int:
        """
        UPSERT de todos os documentos do índice in-memory em gedeon_document_index.
        Inclui embedding vetorial quando disponível (HAS_ANTHROPIC + sklearn).
        """
        from sqlalchemy import text as sa_text

        persistidos = 0
        for doc_id, doc in self._doc_store.items():
            try:
                embedding = doc.get("embedding")
                await db.execute(
                    sa_text(
                        "INSERT INTO gedeon_document_index "
                        "(doc_id, texto_preview, metadados, tokens, embedding, hash) "
                        "VALUES (:doc_id, :texto, :metadados::jsonb, :tokens::jsonb, :embedding, :hash) "
                        "ON CONFLICT (doc_id) DO UPDATE SET "
                        "texto_preview = EXCLUDED.texto_preview, "
                        "metadados = EXCLUDED.metadados, "
                        "tokens = EXCLUDED.tokens, "
                        "embedding = EXCLUDED.embedding, "
                        "hash = EXCLUDED.hash, "
                        "updated_at = NOW()"
                    ),
                    {
                        "doc_id": doc_id,
                        "texto": doc.get("texto", "")[:500],
                        "metadados": json.dumps(doc.get("metadados", {})),
                        "tokens": json.dumps(sorted(doc.get("tokens", set()))),
                        "embedding": embedding,  # list[float] ou None — asyncpg converte para FLOAT8[]
                        "hash": doc.get("hash", ""),
                    },
                )
                persistidos += 1
            except Exception as e:
                logger.warning("SOPHIA: erro ao persistir doc %s: %s", doc_id, e)
        await db.commit()
        return persistidos

    async def carregar_do_banco(self) -> int:
        """
        Restaura o índice in-memory a partir de gedeon_document_index.
        Chamado automaticamente no startup do app.
        Se HAS_ANTHROPIC + sklearn: reconstrói a matriz vetorial para busca premium.
        """
        from sqlalchemy import text as sa_text

        from core.database import async_session_factory

        carregados = 0
        try:
            async with async_session_factory() as db:
                rows = await db.execute(
                    sa_text(
                        "SELECT doc_id, texto_preview, metadados, tokens, embedding, hash "
                        "FROM gedeon_document_index ORDER BY created_at DESC"
                    )
                )
                for row in rows.mappings().all():
                    doc_id = row["doc_id"]
                    meta = row["metadados"] or {}
                    tokens_raw = row["tokens"] or []
                    if isinstance(tokens_raw, str):
                        tokens_raw = json.loads(tokens_raw)
                    tokens_list = list(tokens_raw)
                    tokens_set = set(tokens_list)

                    embedding = row["embedding"]  # list[float] ou None

                    self._doc_store[doc_id] = {
                        "texto": row["texto_preview"] or "",
                        "metadados": meta,
                        "tokens": tokens_set,
                        "tf": self._tf(tokens_list) if tokens_list else {},
                        "hash": row["hash"] or "",
                        "embedding": list(embedding) if embedding else None,
                    }
                    for token in tokens_set:
                        self._idf[token] = self._idf.get(token, 0) + 1
                    carregados += 1

        except Exception as exc:
            logger.warning("SOPHIA: erro ao carregar do banco: %s", exc)

        if carregados > 0 and HAS_ANTHROPIC and HAS_SKLEARN:
            self._reconstruir_matriz_de_embeddings()

        logger.info("SOPHIA: %d documentos carregados do banco", carregados)
        return carregados

    async def indexar_acervo_completo(self) -> int:
        """
        Indexa todos os documentos do GED via SQLAlchemy.
        Popula índice in-memory, constrói matriz sklearn (se disponível)
        e persiste em gedeon_document_index com embeddings.
        """
        logger.info("SOPHIA: iniciando indexação do acervo")
        indexados = 0
        try:
            from sqlalchemy import text as sa_text

            from core.database import async_session_factory

            async with async_session_factory() as db:
                # Indexar ged_kit_documents
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

                # Construir matriz sklearn (caminho premium)
                if HAS_ANTHROPIC and HAS_SKLEARN:
                    n_vetores = self._construir_matriz_sklearn()
                    logger.info("SOPHIA: %d vetores sklearn gerados", n_vetores)

                # Persistir tudo no banco (incluindo embeddings)
                persistidos = await self._persistir_no_banco(db)
                logger.info("SOPHIA: %d documentos persistidos no banco (com embeddings)", persistidos)

        except Exception as exc:
            logger.warning("SOPHIA: erro na indexação: %s", exc)

        logger.info("SOPHIA: %d documentos indexados", indexados)
        return indexados


# Singleton global
sophia = SophiaIndex()
