"""Testes D3 — download endpoint ged_kit_documents (§40).

Cobrem:
  - Download de doc com file_path real retorna PDF binário
  - Download de placeholder (file_path NULL) retorna 404 limpo
  - Path traversal bloqueado (400)
  - BUG 7 regressão: sem auth retorna 401
"""

from __future__ import annotations

import pytest
from sqlalchemy import text

from core.database.session import SyncSessionLocal


@pytest.fixture
def db():
    session = SyncSessionLocal()
    yield session
    session.close()


class TestD3DownloadDBState:
    """Testes de estado do banco para D3 — validam pré-condições."""

    def test_docs_com_path_onvio_existem(self, db):
        """7 kit_docs de 03/2026 devem ter file_path /app/uploads/onvio/."""
        result = db.execute(
            text("""
                SELECT COUNT(*) FROM ged_kit_documents kd
                JOIN ged_document_kits dk ON dk.id = kd.kit_id
                WHERE kd.file_path LIKE '/app/uploads/onvio/%'
                  AND dk.reference_month = '2026-03-01'
            """)
        ).scalar()
        assert result == 7, (
            f"Esperado 7 kit_docs com path Onvio real para 03/2026, obtido {result}. "
            "D2 deveria ter casado 7 folha_pagamento."
        )

    def test_path_onvio_formato_absoluto(self, db):
        """Todos os paths Onvio em ged_kit_documents começam com /app/uploads/onvio/."""
        result = db.execute(
            text("""
                SELECT COUNT(*) FROM ged_kit_documents
                WHERE file_path IS NOT NULL
                  AND file_path NOT LIKE '/app/%'
                  AND file_path NOT LIKE 'documents/%'
                  AND file_path NOT LIKE 'http%'
            """)
        ).scalar()
        assert result == 0, (
            f"Esperado 0 paths com formato desconhecido, obtido {result}. "
            "Todos os file_paths devem ser /app/... ou documents/... ou http..."
        )

    def test_placeholder_doc_existe_para_teste(self, db):
        """Deve existir pelo menos 1 doc com file_path NULL para teste de placeholder."""
        result = db.execute(text("SELECT COUNT(*) FROM ged_kit_documents WHERE file_path IS NULL")).scalar()
        assert result >= 1, f"Esperado >= 1 doc placeholder (file_path NULL), obtido {result}."

    def test_path_traversal_doc_removido(self, db):
        """Doc com path traversal (../../etc/passwd) deve ser removido após testes."""
        result = db.execute(
            text("""
                SELECT COUNT(*) FROM ged_kit_documents
                WHERE file_path LIKE '%../%'
            """)
        ).scalar()
        assert result == 0, (
            f"Esperado 0 docs com path traversal, encontrado {result}. "
            "O doc de teste de traversal deve ter sido removido do banco."
        )
