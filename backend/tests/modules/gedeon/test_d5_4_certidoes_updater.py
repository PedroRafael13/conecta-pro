"""Tests D5.4 — CertidoesUpdaterService."""

from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    return db


def _make_resultado(regular, situacao="regular", fonte="portal", validade_dias=180):
    return {
        "regular": regular,
        "situacao": situacao,
        "fonte": fonte,
        "cnpj_ativo_rfb": regular is not False,
        "validade_dias": validade_dias,
        "consultado_em": "2026-04-28T18:00:00",
        "nota": None,
        "data_validade": (date.today() + timedelta(days=validade_dias)).isoformat(),
    }


def _make_row(doc_type):
    row = MagicMock()
    row.__getitem__ = lambda self, k: ("uuid-1234" if k == "id" else date.today() + timedelta(days=180))
    row.get = lambda k, d=None: ("uuid-1234" if k == "id" else date.today() + timedelta(days=180))
    return row


# ── Teste 1: atualiza 6 rows (as 6 cobertos) ──────────────────────────────────


@pytest.mark.asyncio
async def test_certidoes_updater_atualiza_6_tipos(mock_db):
    """Service deve atualizar as 6 rows de certidoes (alvara e cnpj sao skip)."""
    from modules.people_management.ged.services.certidoes_updater_service import (
        CLIENTS_MAP,
        CertidoesUpdaterService,
    )

    resultado_mock = _make_resultado(True)
    row_mock = _make_row("certidao_negativa_federal")
    mappings_mock = MagicMock()
    mappings_mock.first.return_value = row_mock
    execute_result = MagicMock()
    execute_result.mappings.return_value = mappings_mock
    mock_db.execute.return_value = execute_result

    service = CertidoesUpdaterService(mock_db)

    with patch.object(service, "_chamar_client", return_value=resultado_mock) as mock_call:
        result = await service.executar("35710481000103")

    # 6 doc_types no CLIENTS_MAP
    assert len(CLIENTS_MAP) == 6
    assert result["certidoes_atualizadas"] == 6
    assert result["erros"] == []


# ── Teste 2: alerta quando regular=False ──────────────────────────────────────


@pytest.mark.asyncio
async def test_certidoes_updater_alerta_quando_regular_false(mock_db):
    """alerta_ativo=True quando client retorna regular=False."""
    from modules.people_management.ged.services.certidoes_updater_service import (
        CertidoesUpdaterService,
    )

    resultado_irregular = _make_resultado(False, situacao="irregular")
    row_mock = _make_row("certidao_negativa_federal")
    mappings_mock = MagicMock()
    mappings_mock.first.return_value = row_mock
    execute_result = MagicMock()
    execute_result.mappings.return_value = mappings_mock
    mock_db.execute.return_value = execute_result

    service = CertidoesUpdaterService(mock_db)

    with patch.object(service, "_chamar_client", return_value=resultado_irregular):
        result = await service.executar("35710481000103")

    assert result["alertas_disparados"] == 6  # todos irregulares
    assert result["certidoes_atualizadas"] == 6


# ── Teste 3: sem alerta quando regular=True e vencimento longo ────────────────


@pytest.mark.asyncio
async def test_certidoes_updater_sem_alerta_quando_regular_true(mock_db):
    """alerta_ativo=False quando regular=True e expiry_date > hoje+30d."""
    from modules.people_management.ged.services.certidoes_updater_service import (
        CertidoesUpdaterService,
    )

    resultado_regular = _make_resultado(True, validade_dias=180)
    row_mock = MagicMock()
    row_mock.__getitem__ = lambda self, k: ("uuid-1234" if k == "id" else date.today() + timedelta(days=180))
    row_mock.get = lambda k, d=None: ("uuid-1234" if k == "id" else date.today() + timedelta(days=180))
    mappings_mock = MagicMock()
    mappings_mock.first.return_value = row_mock
    execute_result = MagicMock()
    execute_result.mappings.return_value = mappings_mock
    mock_db.execute.return_value = execute_result

    service = CertidoesUpdaterService(mock_db)

    with patch.object(service, "_chamar_client", return_value=resultado_regular):
        result = await service.executar("35710481000103")

    assert result["alertas_disparados"] == 0
    assert result["certidoes_atualizadas"] == 6


# ── Teste 4: dedup CND federal + INSS = 1 chamada ─────────────────────────────


@pytest.mark.asyncio
async def test_certidoes_updater_dedup_cnd_federal_inss(mock_db):
    """CNDFederalClient.consultar_cnd chamado 1x, nao 2x (federal+inss dedup)."""
    from modules.people_management.ged.services.certidoes_updater_service import (
        CertidoesUpdaterService,
    )

    resultado_mock = _make_resultado(True)
    row_mock = _make_row("certidao_negativa_federal")
    mappings_mock = MagicMock()
    mappings_mock.first.return_value = row_mock
    execute_result = MagicMock()
    execute_result.mappings.return_value = mappings_mock
    mock_db.execute.return_value = execute_result

    service = CertidoesUpdaterService(mock_db)
    call_count = 0

    async def mock_chamar(mod_path, cls_name, method_name, cnpj):
        nonlocal call_count
        call_count += 1
        return resultado_mock

    with patch.object(service, "_chamar_client", side_effect=mock_chamar):
        await service.executar("35710481000103")

    # 6 doc_types mas apenas 5 chamadas (federal e inss usam mesmo client/method)
    assert call_count == 5, f"Esperado 5 chamadas (dedup), got {call_count}"


# ── Teste 5: erro em 1 client nao interrompe os outros ────────────────────────


@pytest.mark.asyncio
async def test_certidoes_updater_erro_em_um_client_nao_interrompe(mock_db):
    """Exception em 1 client: outros 5 ainda rodam, erros[] tem 1 entrada."""
    from modules.people_management.ged.services.certidoes_updater_service import (
        CertidoesUpdaterService,
    )

    resultado_ok = _make_resultado(True)
    row_mock = _make_row("certidao")
    mappings_mock = MagicMock()
    mappings_mock.first.return_value = row_mock
    execute_result = MagicMock()
    execute_result.mappings.return_value = mappings_mock
    mock_db.execute.return_value = execute_result

    service = CertidoesUpdaterService(mock_db)
    call_count = 0

    async def mock_chamar(mod_path, cls_name, method_name, cnpj):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ConnectionError("Portal indisponivel")
        return resultado_ok

    with patch.object(service, "_chamar_client", side_effect=mock_chamar):
        result = await service.executar("35710481000103")

    assert len(result["erros"]) == 1, f"Esperado 1 erro, got {result['erros']}"
    assert result["certidoes_atualizadas"] >= 4, "Outros clients devem ter rodado"
