"""D6 — testes unitários: Redis cache token, InterSyncService, ConciliacaoService."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    return db


# ── D6.0 — Redis token cache ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_token_cache_hit_redis():
    """Se Redis tem token, authenticate() não chama Inter."""
    from modules.integrations.banking.adapters.base import BankCredentials
    from modules.integrations.banking.adapters.inter import InterAdapter

    adapter = InterAdapter(BankCredentials(client_id="test", client_secret="test", environment="sandbox"))

    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=b"cached_token_123")

    with patch("core.cache.redis.get_redis", return_value=mock_redis):
        result = await adapter.authenticate()

    assert result is True
    assert adapter._access_token == "cached_token_123"
    mock_redis.get.assert_called_once_with("inter:token")


@pytest.mark.asyncio
async def test_token_cache_miss_chama_inter():
    """Se Redis não tem token, faz request para Inter e salva no Redis."""
    from modules.integrations.banking.adapters.base import BankCredentials
    from modules.integrations.banking.adapters.inter import InterAdapter

    adapter = InterAdapter(BankCredentials(client_id="test", client_secret="test", environment="sandbox"))

    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "novo_token_456", "expires_in": 3600}

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    with (
        patch("core.cache.redis.get_redis", return_value=mock_redis),
        patch.object(adapter, "_get_client", return_value=mock_client),
    ):
        result = await adapter.authenticate()

    assert result is True
    assert adapter._access_token == "novo_token_456"
    mock_redis.set.assert_called_once()
    call_args = mock_redis.set.call_args
    assert call_args[0][0] == "inter:token"
    assert call_args[0][1] == "novo_token_456"


@pytest.mark.asyncio
async def test_redis_indisponivel_autentica_direto():
    """Se Redis falha, authenticate() ainda funciona via Inter direto."""
    from modules.integrations.banking.adapters.base import BankCredentials
    from modules.integrations.banking.adapters.inter import InterAdapter

    adapter = InterAdapter(BankCredentials(client_id="test", client_secret="test", environment="sandbox"))

    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(side_effect=ConnectionError("Redis offline"))

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "fallback_token", "expires_in": 3600}

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    with (
        patch("core.cache.redis.get_redis", return_value=mock_redis),
        patch.object(adapter, "_get_client", return_value=mock_client),
    ):
        result = await adapter.authenticate()

    assert result is True
    assert adapter._access_token == "fallback_token"


# ── D6.1 — InterSyncService ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_sincronizar_extrato_insere_transactions(mock_db):
    """sincronizar_extrato() chama get_statement e executa INSERTs."""
    from datetime import date, datetime
    from decimal import Decimal

    from modules.integrations.banking.adapters.base import (
        AccountType,
        BankStatement,
        BankTransaction,
        TransactionType,
    )
    from modules.integrations.inter.inter_sync_service import InterSyncService

    svc = InterSyncService(mock_db)

    mock_statement = BankStatement(
        account_agency="0001",
        account_number="370990072",
        account_type=AccountType.CHECKING,
        start_date=date.today(),
        end_date=date.today(),
        opening_balance=Decimal("0"),
        closing_balance=Decimal("1000"),
        transactions=[
            BankTransaction(
                transaction_id="tx001",
                date=datetime.now(),
                amount=Decimal("500"),
                transaction_type=TransactionType.PIX,
                description="PIX recebido",
            ),
        ],
        bank_code="077",
        bank_name="Banco Inter",
    )

    with patch("modules.integrations.inter.inter_sync_service._build_adapter") as mock_build:
        mock_adapter = AsyncMock()
        mock_adapter.get_statement = AsyncMock(return_value=mock_statement)
        mock_adapter.close = AsyncMock()
        mock_build.return_value = mock_adapter

        result = await svc.sincronizar_extrato(dias=7)

    assert result["sincronizadas"] == 1
    assert result["erros"] == []
    mock_db.commit.assert_called_once()


# ── D6.2 — ConciliacaoService ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_conciliacao_match_forte(mock_db):
    """Quando CPF e valor exato correspondem, status deve ser 'pago'."""
    import uuid
    from unittest.mock import MagicMock

    from modules.integrations.inter.conciliacao_service import ConciliacaoService

    emp_id = uuid.uuid4()
    conc_id = uuid.uuid4()
    tx_id = uuid.uuid4()

    # Simular retorno das queries:
    # 1ª execute = transactions débito
    # 2ª execute = employees + conciliação
    call_count = 0

    def side_effect_execute(sql, params=None):
        nonlocal call_count
        result = MagicMock()
        result.mappings = MagicMock(return_value=result)
        if call_count == 0:
            # transactions
            result.all.return_value = [
                {
                    "id": tx_id,
                    "valor": "3500.00",
                    "descricao": "PIX Salario",
                    "data_lancamento": "2026-04-05",
                    "detalhes_destinatario": {"cpfCnpj": "12345678901"},
                }
            ]
        elif call_count == 1:
            # employees
            result.all.return_value = [
                {
                    "id": emp_id,
                    "nome": "Fulano Silva",
                    "cpf": "123.456.789-01",
                    "conc_id": conc_id,
                    "valor_liquido": "3500.00",
                }
            ]
        else:
            result.all.return_value = []
        call_count += 1
        return result

    mock_db.execute = AsyncMock(side_effect=side_effect_execute)

    svc = ConciliacaoService(mock_db)
    result = await svc.conciliar_folha("2026-04")

    assert result["matches_fortes"] == 1
    assert result["total_txs_analisadas"] == 1
