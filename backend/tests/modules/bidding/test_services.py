"""
Tests for bidding services: ContractService, ERPIntegrationService, TenderService.

Uses pytest + unittest.mock to mock database sessions and repositories.
All tests run WITHOUT a database connection.
"""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch
from uuid import UUID, uuid4

import pytest

# ══════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════


@pytest.fixture
def mock_db():
    """Mock SQLAlchemy async Session."""
    db = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    db.execute = AsyncMock()
    return db


@pytest.fixture
def contract_id():
    return uuid4()


@pytest.fixture
def measurement_id():
    return uuid4()


@pytest.fixture
def mock_contract(contract_id):
    """Mock PublicContract model instance."""
    contract = MagicMock()
    contract.id = contract_id
    contract.tender_id = uuid4()
    contract.numero_contrato = "CT-001"
    contract.ano_contrato = 2026
    contract.objeto = "Vigilancia patrimonial para predios publicos em Manaus-AM"
    contract.objeto_resumido = "Vigilancia patrimonial"
    contract.orgao_cnpj = "04.378.626/0001-97"
    contract.orgao_nome = "UFAM"
    contract.orgao_uf = "AM"
    contract.unidade_gestora = "Reitoria"
    contract.gestor_contrato = "Joao Silva"
    contract.fiscal_contrato = "Maria Santos"
    contract.status = "active"
    contract.ativo = True
    contract.valor_contrato = Decimal("1500000.00")
    contract.valor_empenhado = Decimal("500000.00")
    contract.valor_executado = Decimal("300000.00")
    contract.valor_pago = Decimal("250000.00")
    contract.saldo_contrato = Decimal("1200000.00")
    contract.numero_empenho = "2026NE00123"
    contract.data_empenho = date(2026, 1, 15)
    contract.nota_empenho_url = None
    contract.data_assinatura = date(2026, 1, 10)
    contract.data_publicacao = date(2026, 1, 12)
    contract.data_vigencia_inicio = date(2026, 2, 1)
    contract.data_vigencia_fim = date(2027, 1, 31)
    contract.prazo_meses = 12
    contract.indice_reajuste = "IGPM"
    contract.data_base_reajuste = date(2026, 2, 1)
    contract.ultimo_reajuste = None
    contract.percentual_ultimo_reajuste = None
    contract.garantia_tipo = "seguro_garantia"
    contract.garantia_valor = Decimal("75000.00")
    contract.garantia_percentual = Decimal("5.0")
    contract.garantia_vencimento = date(2027, 1, 31)
    contract.garantia_documento_url = None
    contract.aditivos = []
    contract.quantidade_aditivos = 0
    contract.pncp_id = None
    contract.pncp_link = None
    contract.arquivo_contrato_url = None
    contract.arquivo_publicacao_url = None
    contract.esta_vigente = True
    contract.dias_para_vencer = 300
    contract.percentual_executado = 20.0
    contract.saldo_a_executar = Decimal("1200000.00")
    contract.medicoes = []
    contract.observacoes = None
    contract.created_at = datetime(2026, 1, 10)
    contract.updated_at = datetime(2026, 1, 10)
    contract.calcular_reajuste = MagicMock()
    return contract


@pytest.fixture
def mock_measurement(contract_id, measurement_id):
    """Mock Measurement model instance."""
    m = MagicMock()
    m.id = measurement_id
    m.contrato_id = contract_id
    m.numero_medicao = 1
    m.competencia = "2026-03"
    m.tipo = "mensal"
    m.periodo_inicio = date(2026, 3, 1)
    m.periodo_fim = date(2026, 3, 31)
    m.valor_bruto = Decimal("125000.00")
    m.valor_retencoes = Decimal("5000.00")
    m.valor_glosas = Decimal("0.00")
    m.valor_liquido = Decimal("120000.00")
    m.status = "draft"
    m.data_envio = None
    m.data_aprovacao = None
    m.aprovador_nome = None
    m.nota_fiscal_numero = None
    m.created_at = datetime(2026, 3, 1)
    m.esta_aprovada = False
    m.itens_medidos = []
    m.descricao_servicos = "Medicao #1 - 2026-03"
    m.created_by = None
    m.calcular_retencoes = MagicMock()
    m.ativo = True
    return m


# ══════════════════════════════════════════════════════════════
# 1. ContractService Tests
# ══════════════════════════════════════════════════════════════


class TestContractService:
    """Tests for ContractService — measurement and contract operations."""

    @pytest.mark.asyncio
    async def test_add_measurement(self, mock_db, contract_id, mock_measurement):
        """Verifies add_measurement creates a new measurement with correct numbering."""
        with patch("modules.bidding.services.contract_service.ContractRepository") as MockRepo:
            mock_repo = MagicMock()
            # Existing measurements: empty list (so new will be #1)
            mock_repo.get_measurements = AsyncMock(return_value=[])
            mock_repo.add_measurement = AsyncMock(return_value=mock_measurement)
            MockRepo.return_value = mock_repo

            from modules.bidding.services.contract_service import ContractService

            service = ContractService(mock_db)
            result = await service.add_measurement(
                contract_id=contract_id,
                competencia="2026-03",
                periodo_inicio=date(2026, 3, 1),
                periodo_fim=date(2026, 3, 31),
                valor_bruto=Decimal("125000.00"),
            )

            assert isinstance(result, dict)
            assert result["numero_medicao"] == 1
            assert result["competencia"] == "2026-03"
            assert float(result["valor_bruto"]) == 125000.0

            # Should call add_measurement with numero=1
            mock_repo.add_measurement.assert_called_once()
            call_kwargs = mock_repo.add_measurement.call_args
            assert call_kwargs.kwargs.get("numero") == 1 or call_kwargs[1].get("numero") == 1

    @pytest.mark.asyncio
    async def test_approve_measurement(self, mock_db, measurement_id, mock_measurement):
        """Verifies approve_measurement delegates to repository and returns dict."""
        mock_measurement.data_aprovacao = datetime(2026, 3, 15)
        mock_measurement.aprovador_nome = "Fiscal Silva"
        mock_measurement.status = "approved"

        with patch("modules.bidding.services.contract_service.ContractRepository") as MockRepo:
            mock_repo = MagicMock()
            mock_repo.approve_measurement = AsyncMock(return_value=mock_measurement)
            MockRepo.return_value = mock_repo

            from modules.bidding.services.contract_service import ContractService

            service = ContractService(mock_db)
            result = await service.approve_measurement(
                measurement_id=measurement_id,
                aprovador="Fiscal Silva",
                cargo="Fiscal de Contrato",
                observacoes="Medicao OK",
            )

            assert result is not None
            assert result["aprovador_nome"] == "Fiscal Silva"
            assert result["status"] == "approved"

    @pytest.mark.asyncio
    async def test_approve_measurement_not_found(self, mock_db, measurement_id):
        """Verifies approve_measurement returns None when measurement is not found."""
        with patch("modules.bidding.services.contract_service.ContractRepository") as MockRepo:
            mock_repo = MagicMock()
            mock_repo.approve_measurement = AsyncMock(return_value=None)
            MockRepo.return_value = mock_repo

            from modules.bidding.services.contract_service import ContractService

            service = ContractService(mock_db)
            result = await service.approve_measurement(
                measurement_id=measurement_id,
                aprovador="Fiscal",
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_get_measurements(self, mock_db, contract_id, mock_measurement):
        """Verifies get_measurements returns a list of measurement dicts."""
        with patch("modules.bidding.services.contract_service.ContractRepository") as MockRepo:
            mock_repo = MagicMock()
            mock_repo.get_measurements = AsyncMock(return_value=[mock_measurement])
            MockRepo.return_value = mock_repo

            from modules.bidding.services.contract_service import ContractService

            service = ContractService(mock_db)
            result = await service.get_measurements(contract_id)

            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0]["numero_medicao"] == 1
            assert result[0]["competencia"] == "2026-03"


# ══════════════════════════════════════════════════════════════
# 2. ERPIntegrationService Tests
# ══════════════════════════════════════════════════════════════


class TestERPIntegrationService:
    """Tests for ERPIntegrationService — contract-to-operational conversion."""

    @pytest.mark.asyncio
    async def test_converter_para_operacional(self, mock_db, contract_id, mock_contract):
        """Verifies converter creates posts from a public contract."""
        # Setup DB mock to return the contract
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_contract
        mock_db.execute = AsyncMock(return_value=mock_result)

        with (
            patch(
                "modules.bidding.services.erp_integration_service.ERPIntegrationService._get_postos_por_contrato",
                new_callable=AsyncMock,
                return_value=[],
            ),
            patch(
                "modules.bidding.services.erp_integration_service.ERPIntegrationService._next_post_code",
                new_callable=AsyncMock,
                return_value=1,
            ),
        ):
            from modules.bidding.services.erp_integration_service import ERPIntegrationService

            service = ERPIntegrationService(mock_db)

            # Mock Post creation
            mock_post = MagicMock()
            mock_post.id = str(uuid4())
            mock_post.code = "POST-0001"
            mock_post.name = "Posto Vigilancia"
            mock_post.post_type = "vigilante"
            mock_post.shift_type = "diurno"
            mock_post.required_headcount = 1
            mock_post.monthly_cost = 0.0

            with patch.object(service, "_criar_posto", new_callable=AsyncMock, return_value=mock_post):
                result = await service.converter_para_contrato_operacional(
                    contract_id=contract_id,
                    postos_config=None,
                )

                assert isinstance(result, dict)
                assert result["numero_contrato"] == "CT-001"
                assert result["total_postos"] >= 1
                assert len(result["postos_criados"]) >= 1
                mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_converter_para_operacional_already_exists(self, mock_db, contract_id, mock_contract):
        """Verifies converter raises when posts already exist for contract."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_contract
        mock_db.execute = AsyncMock(return_value=mock_result)

        existing_post = MagicMock()
        existing_post.id = str(uuid4())

        with (
            patch(
                "modules.bidding.services.erp_integration_service.ERPIntegrationService._get_postos_por_contrato",
                new_callable=AsyncMock,
                return_value=[existing_post],
            ),
            patch(
                "modules.bidding.services.erp_integration_service.ERPIntegrationService._next_post_code",
                new_callable=AsyncMock,
                return_value=1,
            ),
        ):
            from modules.bidding.services.erp_integration_service import ERPIntegrationService

            service = ERPIntegrationService(mock_db)

            with pytest.raises(ValueError, match="ja possui"):
                await service.converter_para_contrato_operacional(contract_id=contract_id)

    @pytest.mark.asyncio
    async def test_gerar_medicao(self, mock_db, contract_id, mock_contract):
        """Verifies gerar_medicao creates measurement with correct calculations."""
        mock_contract.status = "active"
        mock_contract.medicoes = []

        # First call: select PublicContract (returns contract)
        mock_result_contract = MagicMock()
        mock_result_contract.scalar_one_or_none.return_value = mock_contract

        # Second call: select Measurement for existing competencia (returns None)
        mock_result_existing = MagicMock()
        mock_result_existing.scalar_one_or_none.return_value = None

        mock_db.execute = AsyncMock(side_effect=[mock_result_contract, mock_result_existing])

        with (
            patch(
                "modules.bidding.services.erp_integration_service.ERPIntegrationService._get_postos_por_contrato",
                new_callable=AsyncMock,
                return_value=[],
            ),
            patch(
                "modules.bidding.services.erp_integration_service.ERPIntegrationService._get_alocacoes_ativas_por_contrato",
                new_callable=AsyncMock,
                return_value=[],
            ),
        ):
            from modules.bidding.services.erp_integration_service import ERPIntegrationService

            service = ERPIntegrationService(mock_db)
            result = await service.gerar_medicao(
                contract_id=contract_id,
                competencia="2026-03",
                periodo_inicio=date(2026, 3, 1),
                periodo_fim=date(2026, 3, 31),
            )

            assert isinstance(result, dict)
            assert result["competencia"] == "2026-03"
            assert result["numero_medicao"] == 1
            assert result["valor_bruto"] > 0
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_gerar_medicao_invalid_period(self, mock_db, contract_id, mock_contract):
        """Verifies gerar_medicao raises for invalid period (inicio > fim)."""
        mock_contract.status = "active"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_contract
        mock_db.execute = AsyncMock(return_value=mock_result)

        from modules.bidding.services.erp_integration_service import ERPIntegrationService

        service = ERPIntegrationService(mock_db)

        with pytest.raises(ValueError, match="periodo_inicio"):
            await service.gerar_medicao(
                contract_id=contract_id,
                competencia="2026-03",
                periodo_inicio=date(2026, 3, 31),
                periodo_fim=date(2026, 3, 1),  # End before start
            )

    @pytest.mark.asyncio
    async def test_gerar_fatura(self, mock_db, measurement_id, mock_measurement, mock_contract):
        """Verifies gerar_fatura creates invoice stub from approved measurement."""
        mock_measurement.esta_aprovada = True
        mock_measurement.status = "approved"

        # First execute returns measurement, second returns contract
        mock_result_measurement = MagicMock()
        mock_result_measurement.scalar_one_or_none.return_value = mock_measurement

        mock_result_contract = MagicMock()
        mock_result_contract.scalar_one_or_none.return_value = mock_contract

        mock_db.execute = AsyncMock(side_effect=[mock_result_measurement, mock_result_contract])

        from modules.bidding.services.erp_integration_service import ERPIntegrationService

        service = ERPIntegrationService(mock_db)
        result = await service.gerar_fatura(medicao_id=measurement_id)

        assert isinstance(result, dict)
        assert result["medicao_id"] == str(measurement_id)
        assert result["valor_liquido"] == float(mock_measurement.valor_liquido)
        assert result["integracao_pendente"] is True

    @pytest.mark.asyncio
    async def test_gerar_fatura_not_approved(self, mock_db, measurement_id, mock_measurement):
        """Verifies gerar_fatura raises when measurement is not approved."""
        mock_measurement.esta_aprovada = False
        mock_measurement.status = "draft"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_measurement
        mock_db.execute = AsyncMock(return_value=mock_result)

        from modules.bidding.services.erp_integration_service import ERPIntegrationService

        service = ERPIntegrationService(mock_db)

        with pytest.raises(ValueError, match="nao esta aprovada"):
            await service.gerar_fatura(medicao_id=measurement_id)


# ══════════════════════════════════════════════════════════════
# 3. TenderService Tests
# ══════════════════════════════════════════════════════════════


class TestTenderService:
    """Tests for TenderService — tender CRUD operations."""

    @pytest.mark.asyncio
    async def test_search_tenders(self, mock_db):
        """Verifies list calls repository and returns paginated results."""
        with patch("modules.bidding.services.tender_service.TenderRepository") as MockRepo:
            mock_repo = MagicMock()
            mock_repo.list = AsyncMock(return_value=([], 0))
            MockRepo.return_value = mock_repo

            from modules.bidding.schemas.tender import TenderSearchParams
            from modules.bidding.services.tender_service import TenderService

            service = TenderService(mock_db)
            params = TenderSearchParams(page=1, size=10)
            result = await service.list(params)

            assert result.total == 0
            assert result.page == 1
            assert len(result.items) == 0
            mock_repo.list.assert_called_once_with(params)

    @pytest.mark.asyncio
    async def test_update_tender_status(self, mock_db):
        """Verifies update changes tender fields and returns response."""
        tender_id = uuid4()
        mock_tender = MagicMock()
        mock_tender.id = tender_id
        mock_tender.status = "open"

        with patch("modules.bidding.services.tender_service.TenderRepository") as MockRepo:
            mock_repo = MagicMock()
            mock_repo.update = AsyncMock(return_value=mock_tender)
            MockRepo.return_value = mock_repo

            from modules.bidding.services.tender_service import TenderService

            service = TenderService(mock_db)

            mock_response = MagicMock()
            with patch.object(service, "_to_response", return_value=mock_response):
                from modules.bidding.schemas.tender import TenderUpdate

                update_data = TenderUpdate(status="open")
                result = await service.update(tender_id, update_data)

                assert result is not None
                mock_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_duplicate_tender_raises(self, mock_db):
        """Verifies create raises ValueError for duplicate numero/ano."""
        existing_tender = MagicMock()

        with patch("modules.bidding.services.tender_service.TenderRepository") as MockRepo:
            mock_repo = MagicMock()
            mock_repo.get_by_numero = AsyncMock(return_value=existing_tender)
            MockRepo.return_value = mock_repo

            from modules.bidding.services.tender_service import TenderService

            service = TenderService(mock_db)

            from modules.bidding.schemas.tender import TenderCreate

            create_data = MagicMock(spec=TenderCreate)
            create_data.numero = "PE-001"
            create_data.ano = 2026

            with pytest.raises(ValueError, match="ja existe"):
                await service.create(create_data)
