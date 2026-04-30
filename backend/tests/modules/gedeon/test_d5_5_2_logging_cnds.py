"""D5.5.2 — testes de logging do /cnds/run em ged_coleta_logs."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.execute = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    return db


@pytest.fixture
def updater_result():
    return {"certidoes_atualizadas": 6, "alertas_disparados": 5, "erros": []}


# ── Test 1: write_log=True grava log em ged_coleta_logs ──────────────────────


@pytest.mark.asyncio
async def test_cnds_run_grava_log_em_ged_coleta_logs(mock_db, updater_result):
    """write_log=True (default) deve chamar db.add + db.commit."""
    from modules.people_management.ged.services.certidoes_updater_service import (
        CertidoesUpdaterService,
    )

    svc = CertidoesUpdaterService(mock_db)

    with (
        patch.object(svc, "_chamar_client", new_callable=AsyncMock) as mock_client,
        patch.object(svc, "_atualizar_certidao", new_callable=AsyncMock) as mock_atualiza,
        patch.object(svc, "_set_alerta", new_callable=AsyncMock),
    ):
        mock_client.return_value = {"regular": None, "fonte": "BrasilAPI (fallback)", "situacao": "indeterminado"}
        mock_atualiza.return_value = {"id": "abc", "expiry_date": None}

        await svc.executar("35710481000103", write_log=True)

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


# ── Test 2: run_type='cnds_only' no log gravado ───────────────────────────────


@pytest.mark.asyncio
async def test_cnds_run_log_run_type_cnds_only(mock_db):
    """Log gravado deve ter run_type='cnds_only' e triggered_by correto."""
    from modules.people_management.ged.models.coleta_automatica import GedColetaLog
    from modules.people_management.ged.services.certidoes_updater_service import (
        CertidoesUpdaterService,
    )

    svc = CertidoesUpdaterService(mock_db)
    captured_log = {}

    def capture_add(obj):
        if isinstance(obj, GedColetaLog):
            captured_log["run_type"] = obj.run_type
            captured_log["triggered_by"] = obj.triggered_by
            captured_log["sync_novos"] = obj.sync_novos
            captured_log["kits_assembled"] = obj.kits_assembled

    mock_db.add.side_effect = capture_add

    with (
        patch.object(svc, "_chamar_client", new_callable=AsyncMock) as mock_client,
        patch.object(svc, "_atualizar_certidao", new_callable=AsyncMock) as mock_atualiza,
        patch.object(svc, "_set_alerta", new_callable=AsyncMock),
    ):
        mock_client.return_value = {"regular": True, "fonte": "Sefaz-AM", "situacao": "regular"}
        mock_atualiza.return_value = {"id": "abc", "expiry_date": None}

        await svc.executar(
            "35710481000103",
            run_type="cnds_only",
            triggered_by="jjesus@conectamais.pro",
            write_log=True,
        )

    assert captured_log.get("run_type") == "cnds_only"
    assert captured_log.get("triggered_by") == "jjesus@conectamais.pro"
    assert captured_log.get("sync_novos") == 0
    assert captured_log.get("kits_assembled") == 0


# ── Test 3: write_log=False NÃO grava log ────────────────────────────────────


@pytest.mark.asyncio
async def test_certidoes_updater_write_log_false_nao_grava(mock_db):
    """write_log=False não deve chamar db.add nem db.commit."""
    from modules.people_management.ged.services.certidoes_updater_service import (
        CertidoesUpdaterService,
    )

    svc = CertidoesUpdaterService(mock_db)

    with (
        patch.object(svc, "_chamar_client", new_callable=AsyncMock) as mock_client,
        patch.object(svc, "_atualizar_certidao", new_callable=AsyncMock) as mock_atualiza,
        patch.object(svc, "_set_alerta", new_callable=AsyncMock),
    ):
        mock_client.return_value = {"regular": None, "fonte": "BrasilAPI (fallback)", "situacao": "indeterminado"}
        mock_atualiza.return_value = {"id": "abc", "expiry_date": None}

        result = await svc.executar("35710481000103", write_log=False)

    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()
    assert "certidoes_atualizadas" in result


# ── Test 4: coleta completa (write_log=False) não duplica ────────────────────


@pytest.mark.asyncio
async def test_coleta_completa_grava_apenas_um_log_unificado(mock_db):
    """ColetaAutomaticaService chama executar com write_log=False.

    O log unificado é gravado pelo ColetaAutomaticaService, não pelo Updater.
    """
    from modules.people_management.ged.services.certidoes_updater_service import (
        CertidoesUpdaterService,
    )

    svc = CertidoesUpdaterService(mock_db)

    with (
        patch.object(svc, "_chamar_client", new_callable=AsyncMock) as mock_client,
        patch.object(svc, "_atualizar_certidao", new_callable=AsyncMock) as mock_atualiza,
        patch.object(svc, "_set_alerta", new_callable=AsyncMock),
    ):
        mock_client.return_value = {"regular": True, "fonte": "Sefaz-AM", "situacao": "regular"}
        mock_atualiza.return_value = {"id": "abc", "expiry_date": None}

        # simula como ColetaAutomaticaService chama (Fase 3)
        result = await svc.executar(
            "35710481000103",
            run_type="manual",
            triggered_by="system",
            write_log=False,
        )

    # Updater não gravou log
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()
    # Mas retornou resultado para ColetaAutomaticaService usar no log unificado
    assert result["certidoes_atualizadas"] >= 0
