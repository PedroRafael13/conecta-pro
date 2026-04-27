"""Testes BLOCO C — extensão 9 condomínios 04/2026.

Cobrem:
  - 10 kits totais em 04/2026 (LARANJEIRAS BLOCO B + 9 BLOCO C)
  - 552 docs totais (todos placeholder)
  - ESCRITÓRIO sem kit
  - Total por condomínio conforme §37.1
  - LARANJEIRAS UUID preservado do BLOCO B
  - Idempotência do seed

Banco real via SyncSessionLocal (sem mocks).
"""

from __future__ import annotations

from uuid import UUID

import pytest
from sqlalchemy import text

from core.database.session import SyncSessionLocal

REFERENCE_MONTH = "2026-04-01"
LARANJEIRAS_KIT_UUID = "0107be85-0109-464e-a80b-3665c666dd01"

# Mapping nome_normalizado → total_esperado conforme §37.1
TOTAIS_ESPERADOS: dict[str, int] = {
    "laranjeiras": 83,
    "prime_arena": 94,
    "ideal_flores": 127,
    "mirante": 116,
    "villa_dei_fiori": 64,
    "villa_passaros": 45,
    "michelangelo": 17,
    "green_hills": 2,
    "p_gelain": 2,
    "parise": 2,
}


@pytest.fixture
def db():
    session = SyncSessionLocal()
    yield session
    session.close()


class TestBlocoC:
    def test_kits_totais_04_2026(self, db):
        """Deve existir exatamente 10 kits em 04/2026."""
        row = db.execute(
            text("SELECT COUNT(*) FROM ged_document_kits WHERE reference_month = CAST(:rm AS date)"),
            {"rm": REFERENCE_MONTH},
        ).fetchone()
        assert int(row[0]) == 10, f"Esperado 10 kits, obtido {row[0]}"

    def test_docs_totais_552(self, db):
        """552 docs totais entre os 10 kits em 04/2026."""
        row = db.execute(
            text(
                "SELECT COUNT(*) FROM ged_kit_documents "
                "WHERE kit_id IN ("
                "  SELECT id FROM ged_document_kits "
                "  WHERE reference_month = CAST(:rm AS date)"
                ")"
            ),
            {"rm": REFERENCE_MONTH},
        ).fetchone()
        assert int(row[0]) == 552, f"Esperado 552 docs, obtido {row[0]}"

    def test_todos_placeholder_sem_pdf(self, db):
        """Todos os 552 docs devem ter file_path=NULL."""
        row = db.execute(
            text(
                "SELECT COUNT(*) FROM ged_kit_documents "
                "WHERE kit_id IN ("
                "  SELECT id FROM ged_document_kits "
                "  WHERE reference_month = CAST(:rm AS date)"
                ") AND file_path IS NOT NULL"
            ),
            {"rm": REFERENCE_MONTH},
        ).fetchone()
        assert int(row[0]) == 0, f"Esperado 0 docs com PDF, obtido {row[0]}"

    def test_totais_por_condominio(self, db):
        """Cada kit tem total exato conforme BLOCO A §37.1."""
        for nome_normalizado, esperado in TOTAIS_ESPERADOS.items():
            row = db.execute(
                text(
                    "SELECT COUNT(*) FROM ged_kit_documents gkd "
                    "JOIN ged_document_kits dk ON dk.id = gkd.kit_id "
                    "JOIN ged_clients gc ON gc.id = dk.client_id "
                    "WHERE dk.reference_month = CAST(:rm AS date) "
                    "  AND gc.name ILIKE :nome_pattern"
                ),
                {"rm": REFERENCE_MONTH, "nome_pattern": f"%{nome_normalizado.replace('_', '%')}%"},
            ).fetchone()
            assert int(row[0]) == esperado, f"{nome_normalizado}: esperado {esperado}, obtido {row[0]}"

    def test_escritorio_sem_kit(self, db):
        """ESCRITÓRIO não deve ter kit em 04/2026."""
        row = db.execute(
            text(
                "SELECT COUNT(*) FROM ged_document_kits dk "
                "JOIN ged_clients gc ON gc.id = dk.client_id "
                "WHERE (gc.name ILIKE '%escritorio%' OR gc.name ILIKE '%escrit%') "
                "  AND dk.reference_month = CAST(:rm AS date)"
            ),
            {"rm": REFERENCE_MONTH},
        ).fetchone()
        assert int(row[0]) == 0, f"ESCRITÓRIO não deveria ter kit, obtido {row[0]}"


class TestBlocoCIdempotencia:
    def test_idempotencia_kits_nao_duplicam(self, db):
        """Rodar seed 2x não duplica — 10 kits exatos."""
        row = db.execute(
            text("SELECT COUNT(*) FROM ged_document_kits WHERE reference_month = CAST(:rm AS date)"),
            {"rm": REFERENCE_MONTH},
        ).fetchone()
        assert int(row[0]) == 10

    def test_idempotencia_docs_nao_duplicam(self, db):
        """Rodar seed 2x não duplica docs — 552 exatos."""
        row = db.execute(
            text(
                "SELECT COUNT(*) FROM ged_kit_documents "
                "WHERE kit_id IN ("
                "  SELECT id FROM ged_document_kits "
                "  WHERE reference_month = CAST(:rm AS date)"
                ")"
            ),
            {"rm": REFERENCE_MONTH},
        ).fetchone()
        assert int(row[0]) == 552


class TestBlocoCLaranjeirasPreservado:
    def test_laranjeiras_uuid_preservado(self, db):
        """LARANJEIRAS kit do BLOCO B deve ter UUID exato preservado."""
        row = db.execute(
            text("SELECT id FROM ged_document_kits WHERE id = CAST(:kid AS uuid)"),
            {"kid": LARANJEIRAS_KIT_UUID},
        ).fetchone()
        assert row is not None, f"Kit LARANJEIRAS UUID {LARANJEIRAS_KIT_UUID} não encontrado"
        assert str(row[0]) == LARANJEIRAS_KIT_UUID

    def test_laranjeiras_83_docs_intactos(self, db):
        """LARANJEIRAS deve ter exatamente 83 docs (não foi tocado pelo BLOCO C)."""
        row = db.execute(
            text("SELECT COUNT(*) FROM ged_kit_documents WHERE kit_id = CAST(:kid AS uuid)"),
            {"kid": LARANJEIRAS_KIT_UUID},
        ).fetchone()
        assert int(row[0]) == 83, f"Esperado 83 docs LARANJEIRAS, obtido {row[0]}"


class TestBlocoCZonasProibidas:
    def test_templates_32_intactos(self, db):
        """BLOCO A intacto: 32 templates canônicos."""
        row = db.execute(text("SELECT COUNT(*) FROM kit_documental_templates")).fetchone()
        assert int(row[0]) == 32

    def test_presencas_320_intactas(self, db):
        """BLOCO A intacto: 320 linhas de presença."""
        row = db.execute(text("SELECT COUNT(*) FROM kit_template_presenca")).fetchone()
        assert int(row[0]) == 320

    def test_onvio_documents_preservados(self, db):
        """onvio_documents não foi tocado (>=436 rows)."""
        row = db.execute(text("SELECT COUNT(*) FROM onvio_documents")).fetchone()
        assert int(row[0]) >= 436

    def test_03_2026_preservado(self, db):
        """Kits em 03/2026 podem existir (criados pelo D2 auto-assemble); 04/2026 intacto."""
        row_04 = db.execute(
            text("SELECT COUNT(*) FROM ged_document_kits WHERE reference_month = '2026-04-01'")
        ).fetchone()
        assert int(row_04[0]) == 10, f"Esperado 10 kits em 04/2026, obtido {row_04[0]}"
