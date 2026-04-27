"""Testes D2 — matching Onvio → ged_kit_documents (§39).

Cobrem:
  - matching casa docs existentes (file_path Onvio real preenchido)
  - matching conservador: não sobrescreve file_path real de outro mês
  - matching idempotente: rodar 2x não cria duplicatas

Estado pós-D2: 7 folha_pagamento de 03/2026 casados com PDFs Onvio reais.
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


class TestD2OnvioMatching:
    """Testes de integração para _match_onvio_docs() (D2)."""

    def test_match_onvio_casa_docs_existentes(self, db):
        """Com onvio_documents populado, auto-assemble deve preencher file_paths Onvio."""
        result = db.execute(
            text("""
                SELECT COUNT(*) FROM ged_kit_documents kd
                JOIN ged_document_kits dk ON dk.id = kd.kit_id
                WHERE kd.file_path LIKE '/app/uploads/onvio/%'
                  AND dk.reference_month = '2026-03-01'
                  AND kd.employee_id IS NULL
            """)
        ).scalar()
        assert result >= 1, (
            f"Esperado >= 1 kit_doc com path Onvio real para 03/2026, obtido {result}. "
            "O _match_onvio_docs() deveria ter casado folha_pagamento de pelo menos 1 condomínio."
        )

    def test_match_onvio_nao_sobrescreve(self, db):
        """Matching conservador: kits 04/2026 sem PDFs Onvio não foram sobrescritos.

        Onvio ainda não tem PDFs de 04/2026 (Cenário E — D1). Nenhum kit_doc
        de 04/2026 deve ter path Onvio real.
        """
        result = db.execute(
            text("""
                SELECT COUNT(*) FROM ged_kit_documents kd
                JOIN ged_document_kits dk ON dk.id = kd.kit_id
                WHERE dk.reference_month = '2026-04-01'
                  AND kd.file_path LIKE '/app/uploads/onvio/%'
            """)
        ).scalar()
        assert result == 0, (
            f"Esperado 0 paths Onvio em kits de 04/2026 (sem PDFs ainda), obtido {result}. "
            "O matching não deve sobrescrever docs de meses sem correspondência Onvio."
        )

    def test_match_onvio_idempotente(self, db):
        """Rodar matching 2x não cria duplicatas: cada cliente tem ≤ 1 kit_doc Onvio por tipo.

        Verifica que não existem clientes com mais de 1 folha_pagamento Onvio
        para o mesmo kit (03/2026), o que provaria que o INSERT foi feito 2x.
        """
        duplicatas = db.execute(
            text("""
                SELECT dk.client_id, COUNT(*) as c
                FROM ged_kit_documents kd
                JOIN ged_document_kits dk ON dk.id = kd.kit_id
                WHERE kd.file_path LIKE '/app/uploads/onvio/%'
                  AND kd.document_type = 'folha_pagamento'
                  AND dk.reference_month = '2026-03-01'
                  AND kd.employee_id IS NULL
                GROUP BY dk.client_id
                HAVING COUNT(*) > 1
            """)
        ).fetchall()
        assert len(duplicatas) == 0, (
            f"Esperado 0 clientes com kit_docs duplicados, encontrado {len(duplicatas)}: "
            f"{[str(d[0]) for d in duplicatas]}. "
            "O _match_onvio_docs() deve ser idempotente — 2ª execução não insere duplicata."
        )
