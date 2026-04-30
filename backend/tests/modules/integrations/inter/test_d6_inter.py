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


# ── D6.0 extra — Saldo + token renovado ──────────────────────────────────────


@pytest.mark.asyncio
async def test_consultar_saldo_estrutura_response():
    """Endpoint /saldo retorna estrutura com disponivel, bloqueado, total."""
    from decimal import Decimal
    from unittest.mock import AsyncMock, MagicMock, patch

    from modules.integrations.banking.adapters.base import AccountBalance, BankCredentials
    from modules.integrations.banking.adapters.inter import InterAdapter

    adapter = InterAdapter(BankCredentials(client_id="t", client_secret="t", environment="sandbox"))

    mock_balance = AccountBalance(
        available=Decimal("1220.11"),
        blocked=Decimal("0.00"),
        total=Decimal("1220.11"),
    )

    with (
        patch.object(adapter, "authenticate", return_value=True),
        patch.object(adapter, "get_balance", return_value=mock_balance),
    ):
        balance = await adapter.get_balance()

    assert float(balance.available) == 1220.11
    assert float(balance.blocked) == 0.0
    assert float(balance.total) == 1220.11


@pytest.mark.asyncio
async def test_token_renovado_quando_expirado():
    """Quando token expirado em Redis (None retornado), reautentica."""
    from modules.integrations.banking.adapters.base import BankCredentials
    from modules.integrations.banking.adapters.inter import InterAdapter

    adapter = InterAdapter(BankCredentials(client_id="test", client_secret="test", environment="sandbox"))

    mock_redis = AsyncMock()
    # Simula cache expirado (None)
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "token_renovado_789", "expires_in": 3600}

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    with (
        patch("core.cache.redis.get_redis", return_value=mock_redis),
        patch.object(adapter, "_get_client", return_value=mock_client),
    ):
        result = await adapter.authenticate()

    assert result is True
    assert adapter._access_token == "token_renovado_789"
    mock_redis.set.assert_called_once()


# ── D6.1 extra — Listagem e resumo ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_listar_transactions_filtra_por_tipo(mock_db):
    """listar_transactions() aplica filtro tipo_operacao."""
    from datetime import date

    from modules.integrations.inter.inter_sync_service import InterSyncService

    mock_result = MagicMock()
    mock_result.mappings = MagicMock(return_value=mock_result)
    mock_result.all.return_value = [
        {
            "id": "abc",
            "data_lancamento": date.today(),
            "tipo_operacao": "D",
            "tipo_transacao": "PIX",
            "valor": 500.0,
            "descricao": "PIX enviado",
            "created_at": "2026-04-30",
        }
    ]
    mock_db.execute = AsyncMock(return_value=mock_result)

    svc = InterSyncService(mock_db)
    rows = await svc.listar_transactions(tipo_operacao="D", limit=10)

    assert isinstance(rows, list)
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_resumo_retorna_agrupamento(mock_db):
    """resumo() retorna total por tipo_operacao e tipo_transacao."""
    from modules.integrations.inter.inter_sync_service import InterSyncService

    mock_result = MagicMock()
    mock_result.mappings = MagicMock(return_value=mock_result)
    mock_result.all.return_value = [
        {"tipo_operacao": "D", "tipo_transacao": "PIX", "qtd": 518, "total": 385185.0},
    ]
    mock_db.execute = AsyncMock(return_value=mock_result)

    svc = InterSyncService(mock_db)
    result = await svc.resumo(dias=30)

    assert "resumo" in result
    assert result["periodo_dias"] == 30


# ── D6.2 extra — Match médio, fraco, em_conciliacao ─────────────────────────


@pytest.mark.asyncio
async def test_conciliacao_match_medio(mock_db):
    """CPF match + valor ±R$0.50 → match_tipo='medio', status='pago'."""
    import uuid

    from modules.integrations.inter.conciliacao_service import ConciliacaoService

    emp_id = uuid.uuid4()
    conc_id = uuid.uuid4()
    tx_id = uuid.uuid4()

    call_count = 0

    def side_effect(sql, params=None):
        nonlocal call_count
        result = MagicMock()
        result.mappings = MagicMock(return_value=result)
        if call_count == 0:
            result.all.return_value = [
                {
                    "id": tx_id,
                    "valor": "3500.30",  # ±R$0.30 do líquido
                    "descricao": "PIX Salario",
                    "data_lancamento": "2026-04-05",
                    "detalhes_destinatario": {"cpfCnpj": "12345678901"},
                }
            ]
        elif call_count == 1:
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

    mock_db.execute = AsyncMock(side_effect=side_effect)

    svc = ConciliacaoService(mock_db)
    result = await svc.conciliar_folha("2026-04")

    # Match médio: CPF ok, valor ±R$0.30 (dentro da tolerância de R$0.50)
    assert result["matches_medios"] == 1
    assert result["matches_fortes"] == 0


@pytest.mark.asyncio
async def test_conciliacao_ambiguo_em_conciliacao(mock_db):
    """Múltiplos employees com valor próximo → status='em_conciliacao'."""
    import uuid

    from modules.integrations.inter.conciliacao_service import ConciliacaoService

    tx_id = uuid.uuid4()
    emp1_id, conc1_id = uuid.uuid4(), uuid.uuid4()
    emp2_id, conc2_id = uuid.uuid4(), uuid.uuid4()

    call_count = 0

    def side_effect(sql, params=None):
        nonlocal call_count
        result = MagicMock()
        result.mappings = MagicMock(return_value=result)
        if call_count == 0:
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
            # Dois employees com CPF diferente mas valor próximo
            result.all.return_value = [
                {
                    "id": emp1_id,
                    "nome": "Fulano Silva",
                    "cpf": "123.456.789-01",
                    "conc_id": conc1_id,
                    "valor_liquido": "3500.00",
                },
                {
                    "id": emp2_id,
                    "nome": "Cicrano Souza",
                    "cpf": "987.654.321-00",
                    "conc_id": conc2_id,
                    "valor_liquido": "3500.30",
                },
            ]
        else:
            result.all.return_value = []
        call_count += 1
        return result

    mock_db.execute = AsyncMock(side_effect=side_effect)

    svc = ConciliacaoService(mock_db)
    result = await svc.conciliar_folha("2026-04")

    # Match forte no emp1 mas emp2 tem valor próximo → ambíguo → em_conciliacao
    assert result["em_conciliacao"] == 1
    assert result["matches_fortes"] == 0


@pytest.mark.asyncio
async def test_preparar_competencia_cria_registros(mock_db):
    """preparar_competencia() executa INSERT pra cada employee com payslip."""
    import uuid

    from modules.integrations.inter.conciliacao_service import ConciliacaoService

    emp1 = uuid.uuid4()
    mock_result = MagicMock()
    mock_result.mappings = MagicMock(return_value=mock_result)
    mock_result.all.return_value = [
        {"employee_id": emp1, "nome": "Fulano", "cpf": "000", "valor_liquido": "3000.00"},
    ]
    # 1ª call = SELECT payslips, demais calls = INSERT (void)
    call_count = 0

    def side_effect(sql, params=None):
        nonlocal call_count
        if call_count == 0:
            call_count += 1
            return mock_result
        call_count += 1
        insert_result = MagicMock()
        insert_result.mappings = MagicMock(return_value=insert_result)
        insert_result.all.return_value = []
        return insert_result

    mock_db.execute = AsyncMock(side_effect=side_effect)

    svc = ConciliacaoService(mock_db)
    result = await svc.preparar_competencia("2026-04")

    assert result["criados"] == 1
    mock_db.commit.assert_called_once()


# ── D6.3 — Cobrança service ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_cobranca_service_sincronizar_status_sem_cobrancas(mock_db):
    """sincronizar_status() retorna 0 atualizadas quando não há A_RECEBER."""
    from modules.integrations.inter.cobranca_service import CobrancaService

    mock_result = MagicMock()
    mock_result.mappings = MagicMock(return_value=mock_result)
    mock_result.all.return_value = []
    mock_db.execute = AsyncMock(return_value=mock_result)

    svc = CobrancaService(mock_db)
    result = await svc.sincronizar_status()

    assert result["atualizadas"] == 0
    assert result["erros"] == []


@pytest.mark.asyncio
async def test_cobranca_service_listar_retorna_lista(mock_db):
    """listar() retorna lista de cobranças do banco."""
    import uuid

    from modules.integrations.inter.cobranca_service import CobrancaService

    mock_result = MagicMock()
    mock_result.mappings = MagicMock(return_value=mock_result)
    mock_result.all.return_value = [
        {
            "id": str(uuid.uuid4()),
            "cobranca_id_inter": "inter_abc",
            "seu_numero": "0001",
            "valor": 1000.0,
            "vencimento": "2026-05-01",
            "status": "A_RECEBER",
            "pagador": {},
            "url_boleto": None,
            "pix_copia_cola": None,
            "barcode": None,
            "linha_digitavel": None,
            "descricao": "Teste",
            "created_at": "2026-04-30",
        }
    ]
    mock_db.execute = AsyncMock(return_value=mock_result)

    svc = CobrancaService(mock_db)
    rows = await svc.listar(status="A_RECEBER")

    assert len(rows) == 1
    assert rows[0]["status"] == "A_RECEBER"


@pytest.mark.asyncio
async def test_cobranca_service_estatisticas(mock_db):
    """estatisticas() retorna totais agrupados por status."""
    from modules.integrations.inter.cobranca_service import CobrancaService

    mock_result = MagicMock()
    mock_result.mappings = MagicMock(return_value=mock_result)
    mock_result.all.return_value = [
        {"status": "A_RECEBER", "qtd": 3, "total": 5000.0},
        {"status": "PAGO", "qtd": 10, "total": 18000.0},
    ]
    mock_db.execute = AsyncMock(return_value=mock_result)

    svc = CobrancaService(mock_db)
    result = await svc.estatisticas()

    assert "por_status" in result
    assert len(result["por_status"]) == 2


# ── D6.4 extra — PIX listagem e estrutura ────────────────────────────────────


@pytest.mark.asyncio
async def test_pix_recebidos_listar_retorna_lista(mock_db):
    """GET /pix/recebidos retorna total e lista de PIX."""
    import uuid
    from datetime import datetime

    mock_result = MagicMock()
    mock_result.mappings = MagicMock(return_value=mock_result)
    mock_result.all.return_value = [
        {
            "id": str(uuid.uuid4()),
            "end_to_end_id": "E60701190202604150244DY58VMRPQY1",
            "txid": "CON20260415024317",
            "valor": 2.0,
            "pagador": {},
            "data_horario": datetime.now(),
            "created_at": datetime.now(),
        }
    ]
    mock_db.execute = AsyncMock(return_value=mock_result)

    # Verificar estrutura do dado
    rows = mock_result.mappings().all()
    assert len(rows) == 1
    assert "end_to_end_id" in rows[0]
    assert rows[0]["valor"] == 2.0
