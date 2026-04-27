"""Testes BLOCO B — kit real LARANJEIRAS 04/2026.

Cobrem:
  - Idempotência do seed (2ª execução não duplica)
  - total_esperado=83 via KitBuilderService
  - 83 ged_kit_documents presentes (todos placeholder, pois 04/2026 sem PDFs)
  - Eventuais (rescisao_contrato, comp_rescisao) ausentes quando sem PDF
  - Zonas proibidas intactas (templates=32, presencas=320, onvio=preservado)

Banco real via SyncSessionLocal (sem mocks).
"""

from __future__ import annotations

from uuid import UUID

import pytest
from sqlalchemy import text

from core.database.session import SyncSessionLocal
from modules.gedeon.services.kit_builder_service import KitBuilderService

# Constantes BLOCO B
GED_CLIENT_ID = "e55f6f4c-a641-4b08-9584-eef61dcb5575"
CONDOMINIO_ID = "7c2323fd-e226-4121-806d-d9b2598feeed"
MES_REF = "04.2026"
REFERENCE_MONTH = "2026-04-01"


@pytest.fixture
def db():
    session = SyncSessionLocal()
    yield session
    session.close()


@pytest.fixture
def service(db):
    return KitBuilderService(db)


def _get_kit_id(db) -> UUID | None:
    row = db.execute(
        text(
            "SELECT id FROM ged_document_kits "
            "WHERE client_id = CAST(:cid AS uuid) AND reference_month = CAST(:rm AS date)"
        ),
        {"cid": GED_CLIENT_ID, "rm": REFERENCE_MONTH},
    ).fetchone()
    return UUID(str(row[0])) if row else None


class TestBlocoB:
    def test_kit_laranjeiras_042026_existe(self, db):
        """Kit LARANJEIRAS 04/2026 deve estar presente após seed."""
        kit_id = _get_kit_id(db)
        assert kit_id is not None, "Kit LARANJEIRAS 04/2026 não encontrado em ged_document_kits"

    def test_kit_total_employees_6(self, db):
        """Kit deve registrar 6 funcionários ativos."""
        row = db.execute(
            text(
                "SELECT total_employees FROM ged_document_kits "
                "WHERE client_id = CAST(:cid AS uuid) AND reference_month = CAST(:rm AS date)"
            ),
            {"cid": GED_CLIENT_ID, "rm": REFERENCE_MONTH},
        ).fetchone()
        assert row is not None
        assert row[0] == 6, f"Esperado 6 funcionários, obtido {row[0]}"

    def test_kit_total_documents_83(self, db):
        """Kit deve registrar total_documents=83."""
        row = db.execute(
            text(
                "SELECT total_documents FROM ged_document_kits "
                "WHERE client_id = CAST(:cid AS uuid) AND reference_month = CAST(:rm AS date)"
            ),
            {"cid": GED_CLIENT_ID, "rm": REFERENCE_MONTH},
        ).fetchone()
        assert row is not None
        assert row[0] == 83, f"Esperado 83 docs, obtido {row[0]}"

    def test_kit_documents_count_83(self, db):
        """ged_kit_documents deve ter exatamente 83 rows para o kit LARANJEIRAS 04/2026."""
        kit_id = _get_kit_id(db)
        assert kit_id is not None
        row = db.execute(
            text("SELECT COUNT(*) FROM ged_kit_documents WHERE kit_id = CAST(:kid AS uuid)"),
            {"kid": str(kit_id)},
        ).fetchone()
        assert int(row[0]) == 83, f"Esperado 83 docs, obtido {row[0]}"

    def test_sem_pdfs_todos_placeholder(self, db):
        """Todos os 83 docs devem ter file_path=NULL (04/2026 ainda sem sync)."""
        kit_id = _get_kit_id(db)
        assert kit_id is not None
        row = db.execute(
            text("SELECT COUNT(*) FROM ged_kit_documents WHERE kit_id = CAST(:kid AS uuid) AND file_path IS NOT NULL"),
            {"kid": str(kit_id)},
        ).fetchone()
        assert int(row[0]) == 0, f"Esperado 0 docs com PDF, obtido {row[0]}"

    def test_eventuais_nao_inseridos_sem_pdf(self, db):
        """rescisao_contrato e comp_rescisao NÃO devem ter rows (eventuais sem PDF)."""
        kit_id = _get_kit_id(db)
        assert kit_id is not None
        row = db.execute(
            text(
                "SELECT COUNT(*) FROM ged_kit_documents "
                "WHERE kit_id = CAST(:kid AS uuid) "
                "  AND document_type IN ('rescisao_contrato', 'comp_rescisao')"
            ),
            {"kid": str(kit_id)},
        ).fetchone()
        assert int(row[0]) == 0, f"Esperado 0 eventuais, obtido {row[0]}"

    def test_funcionario_docs_6_instancias_cada(self, db):
        """Templates de funcionário devem ter 6 rows cada (1 por funcionário)."""
        kit_id = _get_kit_id(db)
        assert kit_id is not None
        # contracheque é um template funcionario obrigatorio
        row = db.execute(
            text(
                "SELECT COUNT(*) FROM ged_kit_documents "
                "WHERE kit_id = CAST(:kid AS uuid) AND document_type = 'contracheque'"
            ),
            {"kid": str(kit_id)},
        ).fetchone()
        assert int(row[0]) == 6, f"Esperado 6 rows de contracheque, obtido {row[0]}"

    def test_empresa_docs_1_instancia_cada(self, db):
        """Templates de empresa_matriz devem ter exatamente 1 row cada."""
        kit_id = _get_kit_id(db)
        assert kit_id is not None
        for slug in ("cnd_rfb", "cnd_caixa", "cnd_prefeitura", "cnd_sefaz", "cnd_trabalhista"):
            row = db.execute(
                text(
                    "SELECT COUNT(*) FROM ged_kit_documents "
                    "WHERE kit_id = CAST(:kid AS uuid) AND document_type = :dtype"
                ),
                {"kid": str(kit_id), "dtype": slug},
            ).fetchone()
            assert int(row[0]) == 1, f"Esperado 1 row de {slug}, obtido {row[0]}"

    def test_placeholder_notes_correto(self, db):
        """Todos os faltantes devem ter notes='PDF não localizado no servidor'."""
        kit_id = _get_kit_id(db)
        assert kit_id is not None
        row = db.execute(
            text(
                "SELECT COUNT(*) FROM ged_kit_documents "
                "WHERE kit_id = CAST(:kid AS uuid) "
                "  AND file_path IS NULL "
                "  AND notes != 'PDF não localizado no servidor'"
            ),
            {"kid": str(kit_id)},
        ).fetchone()
        assert int(row[0]) == 0, f"Encontrado {row[0]} rows sem notes correto"


class TestBlocoBIdempotencia:
    def test_idempotencia_unico_kit(self, db):
        """Não deve existir mais de 1 kit LARANJEIRAS 04/2026."""
        row = db.execute(
            text(
                "SELECT COUNT(*) FROM ged_document_kits "
                "WHERE client_id = CAST(:cid AS uuid) AND reference_month = CAST(:rm AS date)"
            ),
            {"cid": GED_CLIENT_ID, "rm": REFERENCE_MONTH},
        ).fetchone()
        assert int(row[0]) == 1, f"Esperado 1 kit, obtido {row[0]}"

    def test_total_kits_sistema(self, db):
        """Mínimo 10 kits no sistema (BLOCO B + C = 04/2026; D2 pode ter criado meses anteriores)."""
        row = db.execute(text("SELECT COUNT(*) FROM ged_document_kits")).fetchone()
        assert int(row[0]) >= 10, f"Esperado >= 10 kits no sistema, obtido {row[0]}"


class TestBlocoBZonasProibidas:
    def test_templates_32_intactos(self, db):
        """BLOCO A intacto: 32 templates canônicos."""
        row = db.execute(text("SELECT COUNT(*) FROM kit_documental_templates")).fetchone()
        assert int(row[0]) == 32, f"Esperado 32 templates, obtido {row[0]}"

    def test_presencas_320_intactas(self, db):
        """BLOCO A intacto: 320 linhas de presença."""
        row = db.execute(text("SELECT COUNT(*) FROM kit_template_presenca")).fetchone()
        assert int(row[0]) == 320, f"Esperado 320 presenças, obtido {row[0]}"

    def test_onvio_documents_preservados(self, db):
        """onvio_documents deve ter >= 436 rows (não foram tocados)."""
        row = db.execute(text("SELECT COUNT(*) FROM onvio_documents")).fetchone()
        assert int(row[0]) >= 436, f"Esperado >=436 onvio_docs, obtido {row[0]}"

    def test_ged_certidoes_preservadas(self, db):
        """ged_certidoes deve ter >= 7 rows (não foram tocadas)."""
        row = db.execute(text("SELECT COUNT(*) FROM ged_certidoes")).fetchone()
        assert int(row[0]) >= 7, f"Esperado >=7 certidoes, obtido {row[0]}"


class TestBlocoBKitBuilderService:
    def test_total_esperado_83_laranjeiras(self, service, db):
        """KitBuilderService deve calcular total_esperado=83 para LARANJEIRAS 04/2026."""
        result = service.build_completude(UUID(CONDOMINIO_ID), MES_REF)
        assert result.metricas is not None
        assert result.metricas.total_esperado == 83, (
            f"Esperado total_esperado=83, obtido {result.metricas.total_esperado}"
        )

    def test_completude_zero_sem_pdfs(self, service, db):
        """Completude confirmada deve ser 0% (nenhum PDF localizado em 04/2026)."""
        result = service.build_completude(UUID(CONDOMINIO_ID), MES_REF)
        assert result.metricas is not None
        assert result.metricas.pct_completude_confirmada == 0.0
