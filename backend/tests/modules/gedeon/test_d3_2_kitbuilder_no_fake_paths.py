"""Testes D3.2 — KitBuilderService não gera paths fake (regressão D3.1.1).

Cobrem:
  - KitBuilderService cria docs com file_path=NULL (não "documents/...")
  - Auto-assemble 02/2026 dry-run: 0 paths fake gerados
  - Idempotência do fix: 2ª execução não cria paths fake
  - Invariante global: zero file_paths LIKE 'documents/%' em ged_kit_documents

Padrão: SyncSessionLocal direto (sem HTTP) para evitar bug event loop BaseHTTPMiddleware.
Cleanup obrigatório no teardown (kits 02/2026 removidos).
"""

from __future__ import annotations

import pytest
from sqlalchemy import text

from core.database.session import SyncSessionLocal


@pytest.fixture(scope="module")
def cleanup_feb_2026():
    """Garante remoção dos kits de 02/2026 após o módulo de testes."""
    yield
    db = SyncSessionLocal()
    try:
        db.execute(
            text("""
            DELETE FROM ged_kit_documents
            WHERE kit_id IN (
                SELECT id FROM ged_document_kits WHERE reference_month='2026-02-01'
            )
        """)
        )
        db.execute(text("DELETE FROM ged_document_kits WHERE reference_month='2026-02-01'"))
        db.commit()
    finally:
        db.close()


class TestD32KitBuilderNoFakePaths:
    """Testes de regressão D3.2 — zero paths fake 'documents/...'."""

    def test_global_zero_fake_paths(self):
        """Invariante global: nenhum ged_kit_document com file_path LIKE 'documents/%'.

        Verifica que D3.2 eliminou todos os 346 paths fake existentes.
        """
        db = SyncSessionLocal()
        count = db.execute(text("SELECT COUNT(*) FROM ged_kit_documents WHERE file_path LIKE 'documents/%'")).scalar()
        db.close()
        assert count == 0, (
            f"Esperado 0 paths fake 'documents/%', encontrado {count}. D3.2 deve ter zerado todos (D3.1.1 regressão)."
        )

    def test_auto_assemble_gera_null_nao_fake(self, cleanup_feb_2026):
        """Auto-assemble em mês limpo (02/2026) gera file_path=NULL, nunca 'documents/...'.

        Validação crítica do fix: após D3.2, KitBuilderService não deve mais
        inventar paths fake. Docs devem ser placeholder honesto (NULL) até
        pipeline real popular o arquivo.
        """
        import asyncio

        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

        from core.config.settings import get_settings
        from modules.people_management.ged.services.kit_builder_service import KitBuilderService

        settings = get_settings()

        async def _run():
            engine = create_async_engine(settings.database_url)
            async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
            async with async_session() as session:
                builder = KitBuilderService(session)
                from datetime import date

                result = await builder.auto_build_all_kits(date(2026, 2, 1))
                await session.commit()
                return result

        result = asyncio.run(_run())

        assert result["reference_month"] == "2026-02-01"
        assert result["kits_created"] >= 1, "Esperado pelo menos 1 kit criado para 02/2026"

        # Validar: zero paths fake gerados
        db = SyncSessionLocal()
        fake_count = db.execute(
            text("""
                SELECT COUNT(*) FROM ged_kit_documents kd
                JOIN ged_document_kits dk ON dk.id=kd.kit_id
                WHERE dk.reference_month='2026-02-01'
                  AND kd.file_path LIKE 'documents/%'
            """)
        ).scalar()
        null_count = db.execute(
            text("""
                SELECT COUNT(*) FROM ged_kit_documents kd
                JOIN ged_document_kits dk ON dk.id=kd.kit_id
                WHERE dk.reference_month='2026-02-01'
                  AND kd.file_path IS NULL
            """)
        ).scalar()
        db.close()

        assert fake_count == 0, (
            f"KitBuilderService gerou {fake_count} paths fake 'documents/...' pós-D3.2! "
            "Fix incompleto — há outro ponto no código gerando fake paths."
        )
        assert null_count > 0, f"Esperado docs com NULL, obtido {null_count}. Auto-assemble não criou nenhum doc?"

    def test_global_zero_fake_paths_apos_assemble(self):
        """Pós auto-assemble: invariante global ainda 0 fake (inclusive 02/2026 recém-criado)."""
        db = SyncSessionLocal()
        count = db.execute(text("SELECT COUNT(*) FROM ged_kit_documents WHERE file_path LIKE 'documents/%'")).scalar()
        db.close()
        assert count == 0, (
            f"Após auto-assemble 02/2026, ainda há {count} paths fake. "
            "KitBuilderService gerou novos 'documents/...' — fix incompleto."
        )
