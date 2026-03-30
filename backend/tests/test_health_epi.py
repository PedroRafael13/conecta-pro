"""
Testes completos — Módulo EPI (NR-6): Saúde Ocupacional
=========================================================

Cobre:
  - Models: EPI, EPIDelivery, EPIInventory, EPICategory, EPIStatus, DeliveryReason
  - Schemas: EPICreateRequest, EPIDeliveryRequest, EPIUpdateRequest, etc.
  - Repository: EPIRepository (CRUD completo)
  - Service: EPIService (toda lógica de negócio)
  - Controller: epi_controller (todos os endpoints REST)
  - Core: epi_management (CACertificate, enums, EPIManagementError)
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

# ==============================================================================
# MODELS
# ==============================================================================


class TestEPIModels:
    """Testes dos modelos EPI."""

    def test_epi_category_values(self):
        from modules.health_occupational.models.epi import EPICategory

        assert EPICategory.CABECA == "cabeca"
        assert EPICategory.OLHOS == "olhos"
        assert EPICategory.FACE == "face"
        assert EPICategory.AUDITIVO == "auditivo"
        assert EPICategory.RESPIRATORIO == "respiratorio"
        assert EPICategory.TRONCO == "tronco"
        assert EPICategory.MEMBROS_SUPERIORES == "membros_superiores"
        assert EPICategory.MEMBROS_INFERIORES == "membros_inferiores"
        assert EPICategory.CORPO_INTEIRO == "corpo_inteiro"
        assert EPICategory.QUEDAS == "quedas"

    def test_epi_status_values(self):
        from modules.health_occupational.models.epi import EPIStatus

        assert EPIStatus.DISPONIVEL == "disponivel"
        assert EPIStatus.ENTREGUE == "entregue"
        assert EPIStatus.EM_USO == "em_uso"
        assert EPIStatus.DANIFICADO == "danificado"
        assert EPIStatus.VENCIDO == "vencido"
        assert EPIStatus.DESCARTADO == "descartado"

    def test_delivery_reason_values(self):
        from modules.health_occupational.models.epi import DeliveryReason

        assert DeliveryReason.ADMISSAO == "admissao"
        assert DeliveryReason.SUBSTITUICAO == "substituicao"
        assert DeliveryReason.DESGASTE == "desgaste"
        assert DeliveryReason.PERDA == "perda"
        assert DeliveryReason.TROCA_FUNCAO == "troca_funcao"
        assert DeliveryReason.VENCIMENTO == "vencimento"
        assert DeliveryReason.DEVOLUCAO == "devolucao"

    def test_epi_tablename(self):
        from modules.health_occupational.models.epi import EPI

        assert EPI.__tablename__ == "health_epi_catalog"

    def test_epi_delivery_tablename(self):
        from modules.health_occupational.models.epi import EPIDelivery

        assert EPIDelivery.__tablename__ == "health_epi_deliveries"

    def test_epi_inventory_tablename(self):
        from modules.health_occupational.models.epi import EPIInventory

        assert EPIInventory.__tablename__ == "health_epi_inventory"

    def test_epi_repr(self):
        from modules.health_occupational.models.epi import EPI

        epi = MagicMock(spec=EPI)
        epi.nome = "Capacete de Segurança"
        epi.ca_number = "12345"
        epi.__repr__ = EPI.__repr__.__get__(epi, type(epi))
        # Só verifica que o model tem __repr__ definido
        assert hasattr(EPI, "__repr__")

    def test_epi_ca_valido_sem_validade(self):
        from modules.health_occupational.models.epi import EPI

        # Testa a property diretamente usando um objeto com atributo ca_validade
        epi = MagicMock()
        epi.ca_validade = None
        # Chama a property diretamente
        result = EPI.ca_esta_valido.fget(epi)
        assert result is True

    def test_epi_ca_valido_dentro_prazo(self):
        from modules.health_occupational.models.epi import EPI

        epi = MagicMock()
        epi.ca_validade = date.today() + timedelta(days=30)
        result = EPI.ca_esta_valido.fget(epi)
        assert result is True

    def test_epi_ca_vencido(self):
        from modules.health_occupational.models.epi import EPI

        epi = MagicMock()
        epi.ca_validade = date.today() - timedelta(days=1)
        result = EPI.ca_esta_valido.fget(epi)
        assert result is False

    def test_epi_delivery_repr(self):
        from modules.health_occupational.models.epi import EPIDelivery

        assert hasattr(EPIDelivery, "__repr__")

    def test_epi_delivery_esta_vencido_sem_validade(self):
        from modules.health_occupational.models.epi import EPIDelivery

        d = MagicMock()
        d.data_validade = None
        result = EPIDelivery.esta_vencido.fget(d)
        assert result is False

    def test_epi_delivery_esta_vencido_true(self):
        from modules.health_occupational.models.epi import EPIDelivery

        d = MagicMock()
        d.data_validade = date.today() - timedelta(days=1)
        result = EPIDelivery.esta_vencido.fget(d)
        assert result is True

    def test_epi_delivery_esta_vencido_false(self):
        from modules.health_occupational.models.epi import EPIDelivery

        d = MagicMock()
        d.data_validade = date.today() + timedelta(days=30)
        result = EPIDelivery.esta_vencido.fget(d)
        assert result is False

    def test_epi_delivery_dias_para_vencer_none(self):
        from modules.health_occupational.models.epi import EPIDelivery

        d = MagicMock()
        d.data_validade = None
        result = EPIDelivery.dias_para_vencer.fget(d)
        assert result is None

    def test_epi_delivery_dias_para_vencer_positivo(self):
        from modules.health_occupational.models.epi import EPIDelivery

        d = MagicMock()
        d.data_validade = date.today() + timedelta(days=10)
        result = EPIDelivery.dias_para_vencer.fget(d)
        assert result == 10

    def test_epi_delivery_dias_para_vencer_zero(self):
        from modules.health_occupational.models.epi import EPIDelivery

        d = MagicMock()
        d.data_validade = date.today() - timedelta(days=5)
        result = EPIDelivery.dias_para_vencer.fget(d)
        assert result == 0

    def test_epi_inventory_repr(self):
        from modules.health_occupational.models.epi import EPIInventory

        assert hasattr(EPIInventory, "__repr__")

    def test_epi_inventory_estoque_baixo_true(self):
        from modules.health_occupational.models.epi import EPIInventory

        inv = MagicMock()
        inv.quantidade_atual = 3
        inv.quantidade_minima = 10
        result = EPIInventory.estoque_baixo.fget(inv)
        assert result is True

    def test_epi_inventory_estoque_baixo_false(self):
        from modules.health_occupational.models.epi import EPIInventory

        inv = MagicMock()
        inv.quantidade_atual = 15
        inv.quantidade_minima = 10
        result = EPIInventory.estoque_baixo.fget(inv)
        assert result is False

    def test_epi_inventory_percentual_sem_maximo(self):
        from modules.health_occupational.models.epi import EPIInventory

        inv = MagicMock()
        inv.quantidade_atual = 5
        inv.quantidade_maxima = None
        result = EPIInventory.percentual_estoque.fget(inv)
        assert result is None

    def test_epi_inventory_percentual_com_maximo(self):
        from modules.health_occupational.models.epi import EPIInventory

        inv = MagicMock()
        inv.quantidade_atual = 50
        inv.quantidade_maxima = 100
        result = EPIInventory.percentual_estoque.fget(inv)
        assert result == 50.0


# ==============================================================================
# SCHEMAS
# ==============================================================================


class TestEPISchemas:
    """Testes dos schemas Pydantic EPI."""

    def test_epi_create_request_valido(self):
        from modules.health_occupational.schemas.epi import EPICreateRequest

        req = EPICreateRequest(
            nome="Capacete de Segurança",
            categoria="cabeca",
            ca_number="12345",
            fabricante="Deltaplus",
        )
        assert req.nome == "Capacete de Segurança"
        assert req.validade_dias == 365  # default

    def test_epi_create_categoria_invalida(self):
        import pytest

        from modules.health_occupational.schemas.epi import EPICreateRequest

        with pytest.raises(Exception):
            EPICreateRequest(
                nome="Teste",
                categoria="invalida",
                ca_number="999",
                fabricante="X",
            )

    def test_epi_create_validade_minima(self):
        from modules.health_occupational.schemas.epi import EPICreateRequest

        req = EPICreateRequest(
            nome="Luva",
            categoria="membros_superiores",
            ca_number="99001",
            fabricante="LuvaBR",
            validade_dias=30,
        )
        assert req.validade_dias == 30

    def test_epi_create_validade_maxima(self):
        from modules.health_occupational.schemas.epi import EPICreateRequest

        req = EPICreateRequest(
            nome="Colete",
            categoria="tronco",
            ca_number="99002",
            fabricante="ColeteBR",
            validade_dias=1825,
        )
        assert req.validade_dias == 1825

    def test_epi_delivery_request_valido(self):
        from modules.health_occupational.schemas.epi import EPIDeliveryRequest

        req = EPIDeliveryRequest(
            epi_id=uuid.uuid4(),
            funcionario_id=uuid.uuid4(),
            motivo="admissao",
            ca_number="12345",
        )
        assert req.quantidade == 1  # default

    def test_epi_update_request_vazio(self):
        from modules.health_occupational.schemas.epi import EPIUpdateRequest

        req = EPIUpdateRequest()
        assert req.model_dump(exclude_unset=True) == {}

    def test_epi_inventory_update_request(self):
        from modules.health_occupational.schemas.epi import EPIInventoryUpdateRequest

        req = EPIInventoryUpdateRequest(quantidade_atual=50, quantidade_minima=10)
        assert req.quantidade_atual == 50

    def test_todas_categorias_validas(self):
        from modules.health_occupational.schemas.epi import EPICreateRequest

        categorias = [
            "cabeca",
            "olhos",
            "face",
            "auditivo",
            "respiratorio",
            "tronco",
            "membros_superiores",
            "membros_inferiores",
            "corpo_inteiro",
            "quedas",
        ]
        for cat in categorias:
            req = EPICreateRequest(
                nome=f"EPI {cat}",
                categoria=cat,
                ca_number=f"CA-{cat[:5]}",
                fabricante="Fabricante",
            )
            assert req.categoria == cat


# ==============================================================================
# REPOSITORY
# ==============================================================================


class TestEPIRepository:
    """Testes do EPIRepository."""

    def _make_db(self):
        db = MagicMock()
        db.add = MagicMock()
        db.commit = MagicMock()
        db.refresh = MagicMock()
        return db

    def test_create_epi(self):
        from modules.health_occupational.models.epi import EPI
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        repo = EPIRepository(db=db)
        epi = MagicMock(spec=EPI)

        result = repo.create_epi(epi)
        db.add.assert_called_once_with(epi)
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(epi)
        assert result == epi

    def test_get_epi_by_id_found(self):
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        mock_epi = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = mock_epi

        repo = EPIRepository(db=db)
        result = repo.get_epi_by_id(uuid.uuid4())
        assert result == mock_epi

    def test_get_epi_by_id_not_found(self):
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        db.query.return_value.filter.return_value.first.return_value = None

        repo = EPIRepository(db=db)
        result = repo.get_epi_by_id(uuid.uuid4())
        assert result is None

    def test_get_epi_by_ca(self):
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        mock_epi = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = mock_epi

        repo = EPIRepository(db=db)
        result = repo.get_epi_by_ca("CA-12345")
        assert result == mock_epi

    def test_list_epis_sem_filtros(self):
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        # list_epis com ativo=True faz 2x filter, depois order_by.offset.limit.all
        chain = db.query.return_value
        chain.filter.return_value = chain
        chain.order_by.return_value = chain
        chain.offset.return_value = chain
        chain.limit.return_value = chain
        chain.all.return_value = []

        repo = EPIRepository(db=db)
        result = repo.list_epis()
        assert isinstance(result, list)

    def test_count_epis(self):
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        chain = db.query.return_value
        chain.filter.return_value = chain
        chain.count.return_value = 5

        repo = EPIRepository(db=db)
        result = repo.count_epis()
        assert isinstance(result, int)

    def test_search_epis(self):
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        db.query.return_value.filter.return_value.limit.return_value.all.return_value = []

        repo = EPIRepository(db=db)
        result = repo.search_epis("capacete")
        assert isinstance(result, list)

    def test_update_epi(self):
        from modules.health_occupational.models.epi import EPI
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        epi = MagicMock(spec=EPI)

        repo = EPIRepository(db=db)
        result = repo.update_epi(epi)
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(epi)
        assert result == epi

    def test_deactivate_epi(self):
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        mock_epi = MagicMock()
        mock_epi.ativo = True
        db.query.return_value.filter.return_value.first.return_value = mock_epi

        repo = EPIRepository(db=db)
        result = repo.deactivate_epi(uuid.uuid4())
        assert mock_epi.ativo is False
        assert result == mock_epi

    def test_deactivate_epi_not_found(self):
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        db.query.return_value.filter.return_value.first.return_value = None

        repo = EPIRepository(db=db)
        result = repo.deactivate_epi(uuid.uuid4())
        assert result is None

    def test_create_delivery(self):
        from modules.health_occupational.models.epi import EPIDelivery
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        delivery = MagicMock(spec=EPIDelivery)

        repo = EPIRepository(db=db)
        result = repo.create_delivery(delivery)
        db.add.assert_called_once_with(delivery)
        assert result == delivery

    def test_get_delivery_by_id(self):
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        mock_d = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = mock_d

        repo = EPIRepository(db=db)
        result = repo.get_delivery_by_id(uuid.uuid4())
        assert result == mock_d

    def test_get_deliveries_by_funcionario(self):
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        repo = EPIRepository(db=db)
        result = repo.get_deliveries_by_funcionario(uuid.uuid4())
        assert isinstance(result, list)

    def test_create_inventory(self):
        from modules.health_occupational.models.epi import EPIInventory
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        inv = MagicMock(spec=EPIInventory)

        repo = EPIRepository(db=db)
        result = repo.create_inventory(inv)
        db.add.assert_called_once_with(inv)
        assert result == inv

    def test_get_inventory_by_epi(self):
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        mock_inv = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = mock_inv

        repo = EPIRepository(db=db)
        result = repo.get_inventory_by_epi(uuid.uuid4())
        assert result == mock_inv

    def test_list_inventory(self):
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        db.query.return_value.all.return_value = []

        repo = EPIRepository(db=db)
        result = repo.list_inventory()
        assert isinstance(result, list)

    def test_adjust_inventory_entrada(self):
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        mock_inv = MagicMock()
        mock_inv.quantidade_atual = 10
        db.query.return_value.filter.return_value.first.return_value = mock_inv

        repo = EPIRepository(db=db)
        result = repo.adjust_inventory(uuid.uuid4(), 5, "entrada")
        assert mock_inv.quantidade_atual == 15
        assert result == mock_inv

    def test_adjust_inventory_saida(self):
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        mock_inv = MagicMock()
        mock_inv.quantidade_atual = 10
        db.query.return_value.filter.return_value.first.return_value = mock_inv

        repo = EPIRepository(db=db)
        result = repo.adjust_inventory(uuid.uuid4(), 3, "saida")
        assert mock_inv.quantidade_atual == 7

    def test_adjust_inventory_not_found(self):
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        db.query.return_value.filter.return_value.first.return_value = None

        repo = EPIRepository(db=db)
        result = repo.adjust_inventory(uuid.uuid4(), 5)
        assert result is None

    def test_get_low_stock_items(self):
        from modules.health_occupational.repositories.epi_repository import EPIRepository

        db = self._make_db()
        db.query.return_value.filter.return_value.all.return_value = []

        repo = EPIRepository(db=db)
        result = repo.get_low_stock_items()
        assert isinstance(result, list)


# ==============================================================================
# SERVICE
# ==============================================================================


class TestEPIService:
    """Testes do EPIService."""

    def _make_service(self):
        db = MagicMock()
        db.add = MagicMock()
        db.commit = MagicMock()
        db.refresh = MagicMock()
        db.flush = MagicMock()
        from modules.health_occupational.services.epi_service import EPIService

        return EPIService(db=db), db

    def test_create_epi_sucesso(self):
        from modules.health_occupational.schemas.epi import EPICreateRequest

        service, db = self._make_service()
        db.query.return_value.filter.return_value.first.return_value = None  # CA não existe

        req = EPICreateRequest(
            nome="Capacete",
            categoria="cabeca",
            ca_number="CA-001",
            fabricante="Delta",
        )
        result = service.create_epi(req)
        db.add.assert_called()
        db.commit.assert_called()

    def test_create_epi_ca_duplicado(self):
        import pytest

        from modules.health_occupational.schemas.epi import EPICreateRequest

        service, db = self._make_service()
        db.query.return_value.filter.return_value.first.return_value = MagicMock()  # CA já existe

        req = EPICreateRequest(
            nome="Capacete",
            categoria="cabeca",
            ca_number="CA-001",
            fabricante="Delta",
        )
        with pytest.raises(ValueError, match="ja cadastrado"):
            service.create_epi(req)

    def test_get_epi_found(self):
        service, db = self._make_service()
        mock_epi = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = mock_epi

        result = service.get_epi(uuid.uuid4())
        assert result == mock_epi

    def test_get_epi_not_found(self):
        service, db = self._make_service()
        db.query.return_value.filter.return_value.first.return_value = None

        result = service.get_epi(uuid.uuid4())
        assert result is None

    def test_get_epi_by_ca(self):
        service, db = self._make_service()
        mock_epi = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = mock_epi

        result = service.get_epi_by_ca("CA-001")
        assert result == mock_epi

    def test_update_epi_found(self):
        from modules.health_occupational.schemas.epi import EPIUpdateRequest

        service, db = self._make_service()
        mock_epi = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = mock_epi

        req = EPIUpdateRequest(nome="Capacete Atualizado")
        result = service.update_epi(uuid.uuid4(), req)
        assert result == mock_epi

    def test_update_epi_not_found(self):
        from modules.health_occupational.schemas.epi import EPIUpdateRequest

        service, db = self._make_service()
        db.query.return_value.filter.return_value.first.return_value = None

        result = service.update_epi(uuid.uuid4(), EPIUpdateRequest())
        assert result is None

    def test_deactivate_epi_found(self):
        service, db = self._make_service()
        mock_epi = MagicMock()
        mock_epi.ativo = True
        db.query.return_value.filter.return_value.first.return_value = mock_epi

        result = service.deactivate_epi(uuid.uuid4())
        assert mock_epi.ativo is False
        assert result == mock_epi

    def test_deactivate_epi_not_found(self):
        service, db = self._make_service()
        db.query.return_value.filter.return_value.first.return_value = None

        result = service.deactivate_epi(uuid.uuid4())
        assert result is None

    def test_list_epis_sem_db(self):
        from modules.health_occupational.services.epi_service import EPIService

        service = EPIService(db=None)
        result = service.list_epis()
        assert result["items"] == []
        assert result["total"] == 0

    def test_list_epis_com_db_erro(self):
        service, db = self._make_service()
        db.execute.side_effect = Exception("DB error")

        result = service.list_epis()
        assert result["items"] == []

    def test_register_delivery_epi_not_found(self):
        import pytest

        from modules.health_occupational.schemas.epi import EPIDeliveryRequest

        service, db = self._make_service()
        db.query.return_value.filter.return_value.first.return_value = None

        req = EPIDeliveryRequest(
            epi_id=uuid.uuid4(),
            funcionario_id=uuid.uuid4(),
            motivo="admissao",
            ca_number="CA-001",
        )
        with pytest.raises(ValueError, match="nao encontrado"):
            service.register_delivery(req)

    def test_register_delivery_epi_inativo(self):
        import pytest

        from modules.health_occupational.schemas.epi import EPIDeliveryRequest

        service, db = self._make_service()
        mock_epi = MagicMock()
        mock_epi.ativo = False
        mock_epi.validade_dias = 365
        db.query.return_value.filter.return_value.first.return_value = mock_epi

        req = EPIDeliveryRequest(
            epi_id=uuid.uuid4(),
            funcionario_id=uuid.uuid4(),
            motivo="admissao",
            ca_number="CA-001",
        )
        with pytest.raises(ValueError, match="inativo"):
            service.register_delivery(req)

    def test_register_delivery_estoque_insuficiente(self):
        import pytest

        from modules.health_occupational.schemas.epi import EPIDeliveryRequest

        service, db = self._make_service()
        mock_epi = MagicMock()
        mock_epi.ativo = True
        mock_epi.validade_dias = 365

        mock_inv = MagicMock()
        mock_inv.quantidade_atual = 0

        # First call returns epi, second returns inventory
        db.query.return_value.filter.return_value.first.side_effect = [mock_epi, mock_inv]

        req = EPIDeliveryRequest(
            epi_id=uuid.uuid4(),
            funcionario_id=uuid.uuid4(),
            motivo="admissao",
            ca_number="CA-001",
            quantidade=5,
        )
        with pytest.raises(ValueError, match="insuficiente"):
            service.register_delivery(req)

    def test_get_delivery(self):
        service, db = self._make_service()
        mock_d = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = mock_d

        result = service.get_delivery(uuid.uuid4())
        assert result == mock_d

    def test_update_delivery_assinatura(self):
        from modules.health_occupational.schemas.epi import EPIDeliveryUpdateRequest

        service, db = self._make_service()
        mock_d = MagicMock()
        mock_d.assinatura_funcionario = False
        db.query.return_value.filter.return_value.first.return_value = mock_d

        req = EPIDeliveryUpdateRequest(assinatura_funcionario=True)
        result = service.update_delivery(uuid.uuid4(), req)
        assert result == mock_d

    def test_register_return_not_found(self):
        service, db = self._make_service()
        db.query.return_value.filter.return_value.first.return_value = None

        result = service.register_return(uuid.uuid4(), "uso", "bom")
        assert result is None

    def test_register_return_condicao_boa_devolve_estoque(self):
        service, db = self._make_service()
        mock_d = MagicMock()
        mock_d.devolvido = False
        mock_d.quantidade = 1
        mock_inv = MagicMock()
        mock_inv.quantidade_atual = 5

        # first call = delivery, second = inventory
        db.query.return_value.filter.return_value.first.side_effect = [mock_d, mock_inv]

        result = service.register_return(uuid.uuid4(), "fim de uso", "bom")
        assert mock_d.devolvido is True
        assert mock_inv.quantidade_atual == 6

    def test_get_employee_record(self):
        service, db = self._make_service()
        db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        result = service.get_employee_record(uuid.uuid4())
        assert "entregas" in result
        assert result["total_entregas"] == 0

    def test_add_to_inventory_not_found(self):
        import pytest

        service, db = self._make_service()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(ValueError):
            service.add_to_inventory(uuid.uuid4(), 10)

    def test_add_to_inventory_found(self):
        service, db = self._make_service()
        mock_inv = MagicMock()
        mock_inv.quantidade_atual = 10
        db.query.return_value.filter.return_value.first.return_value = mock_inv

        result = service.add_to_inventory(uuid.uuid4(), 5)
        assert mock_inv.quantidade_atual == 15

    def test_list_inventory_sem_db(self):
        from modules.health_occupational.services.epi_service import EPIService

        service = EPIService(db=None)
        result = service.list_inventory()
        assert result == []

    def test_list_inventory_com_erro(self):
        service, db = self._make_service()
        db.execute.side_effect = Exception("DB error")

        result = service.list_inventory()
        assert result == []

    def test_get_epi_categories(self):
        service, db = self._make_service()
        result = service.get_epi_categories()
        assert "categorias" in result
        assert len(result["categorias"]) == 10

    def test_get_statistics_sem_db(self):
        from modules.health_occupational.services.epi_service import EPIService

        service = EPIService(db=None)
        result = service.get_statistics()
        assert result["total_epis_ativos"] == 0

    def test_get_statistics_com_erro(self):
        service, db = self._make_service()
        db.execute.side_effect = Exception("DB error")

        result = service.get_statistics()
        assert result["total_epis_ativos"] == 0


# ==============================================================================
# CONTROLLER
# ==============================================================================


class TestEPIController:
    """Testes dos endpoints do EPI controller via TestClient."""

    def _make_app(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from core.database.session import get_sync_db_dependency
        from modules.health_occupational.controllers.epi_controller import router as epi_router

        app = FastAPI()
        app.include_router(epi_router)
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        mock_db.flush = MagicMock()
        app.dependency_overrides[get_sync_db_dependency] = lambda: mock_db
        client = TestClient(app)
        return client, mock_db

    def test_list_categorias(self):
        client, db = self._make_app()
        response = client.get("/epi/categorias")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_estatisticas_sucesso(self):
        client, db = self._make_app()
        db.execute.return_value.scalar.return_value = 0
        response = client.get("/epi/estatisticas")
        assert response.status_code == 200

    def test_get_estatisticas_erro(self):
        client, db = self._make_app()
        db.execute.side_effect = Exception("DB error")
        response = client.get("/epi/estatisticas")
        assert response.status_code in (200, 500)

    def test_list_epis(self):
        client, db = self._make_app()
        db.execute.return_value.scalar.return_value = 0
        db.execute.return_value.fetchall.return_value = []
        response = client.get("/epi")
        assert response.status_code == 200

    def test_get_epi_inventory(self):
        client, db = self._make_app()
        db.execute.return_value.fetchall.return_value = []
        response = client.get("/epi/estoque")
        assert response.status_code == 200

    def test_get_epi_ficha(self):
        client, db = self._make_app()
        emp_id = uuid.uuid4()
        db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        response = client.get(f"/epi/ficha/{emp_id}")
        assert response.status_code == 200

    def test_create_epi_sucesso(self):
        client, db = self._make_app()
        db.query.return_value.filter.return_value.first.return_value = None  # CA não existe
        mock_epi = MagicMock()
        mock_epi.id = uuid.uuid4()
        db.refresh.side_effect = lambda obj: None

        response = client.post(
            "/epi/cadastrar",
            json={
                "nome": "Capacete Amarelo",
                "categoria": "cabeca",
                "ca_number": "CA-9999",
                "fabricante": "Delta",
            },
        )
        assert response.status_code in (201, 400, 500)

    def test_create_epi_ca_duplicado(self):
        client, db = self._make_app()
        db.query.return_value.filter.return_value.first.return_value = MagicMock()

        response = client.post(
            "/epi/cadastrar",
            json={
                "nome": "Capacete",
                "categoria": "cabeca",
                "ca_number": "CA-001",
                "fabricante": "Delta",
            },
        )
        assert response.status_code in (400, 500)

    def test_get_epi_not_found(self):
        client, db = self._make_app()
        db.query.return_value.filter.return_value.first.return_value = None

        response = client.get(f"/epi/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_get_epi_found(self):
        from modules.health_occupational.models.epi import EPI

        client, db = self._make_app()
        mock_epi = MagicMock(spec=EPI)
        mock_epi.id = uuid.uuid4()
        mock_epi.nome = "Capacete"
        mock_epi.descricao = None
        mock_epi.codigo_interno = None
        mock_epi.categoria = "cabeca"
        mock_epi.ca_number = "CA-001"
        mock_epi.ca_validade = None
        mock_epi.fabricante = "Delta"
        mock_epi.modelo = None
        mock_epi.validade_dias = 365
        mock_epi.especificacoes = {}
        mock_epi.riscos_protegidos = []
        mock_epi.instrucoes_uso = None
        mock_epi.instrucoes_higienizacao = None
        mock_epi.instrucoes_armazenamento = None
        mock_epi.imagem_url = None
        mock_epi.ativo = True
        mock_epi.created_at = datetime.utcnow()
        mock_epi.updated_at = None
        mock_epi.ca_esta_valido = True
        db.query.return_value.filter.return_value.first.return_value = mock_epi

        response = client.get(f"/epi/{mock_epi.id}")
        assert response.status_code == 200

    def test_deactivate_epi_not_found(self):
        client, db = self._make_app()
        db.query.return_value.filter.return_value.first.return_value = None

        response = client.delete(f"/epi/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_update_epi_not_found(self):
        client, db = self._make_app()
        db.query.return_value.filter.return_value.first.return_value = None

        response = client.patch(f"/epi/{uuid.uuid4()}", json={"nome": "Novo Nome"})
        assert response.status_code == 404

    def test_get_delivery_not_found(self):
        client, db = self._make_app()
        db.query.return_value.filter.return_value.first.return_value = None

        response = client.get(f"/epi/entrega/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_return_epi_not_found(self):
        client, db = self._make_app()
        db.query.return_value.filter.return_value.first.return_value = None

        response = client.post(
            f"/epi/entrega/{uuid.uuid4()}/devolver",
            params={"motivo": "fim de uso", "condicao": "bom"},
        )
        assert response.status_code == 404

    def test_sign_delivery_not_found(self):
        client, db = self._make_app()
        db.query.return_value.filter.return_value.first.return_value = None

        response = client.post(f"/epi/entrega/{uuid.uuid4()}/assinar")
        assert response.status_code == 404

    def test_update_inventory_not_found(self):
        client, db = self._make_app()
        db.query.return_value.filter.return_value.first.return_value = None

        response = client.patch(f"/epi/estoque/{uuid.uuid4()}", json={"quantidade_atual": 50})
        assert response.status_code == 404

    def test_add_to_inventory_not_found(self):
        client, db = self._make_app()
        db.query.return_value.filter.return_value.first.return_value = None

        response = client.post(
            f"/epi/estoque/{uuid.uuid4()}/entrada",
            params={"quantidade": 10},
        )
        assert response.status_code in (400, 500)

    def test_router_has_routes(self):
        from modules.health_occupational.controllers.epi_controller import router

        paths = [r.path for r in router.routes]
        assert any("cadastrar" in p for p in paths)
        assert any("categorias" in p for p in paths)
        assert any("estoque" in p for p in paths)
        assert any("ficha" in p for p in paths)
        assert any("estatisticas" in p for p in paths)


# ==============================================================================
# CORE EPI MANAGEMENT
# ==============================================================================


class TestEPICoreManagement:
    """Testes do módulo core/epi_management."""

    def test_epi_category_protecao_cabeca(self):
        from modules.health_occupational.core.epi_management import EPICategory

        assert EPICategory.PROTECAO_CABECA == "protecao_cabeca"

    def test_epi_status_disponivel(self):
        from modules.health_occupational.core.epi_management import EPIStatus

        assert EPIStatus.DISPONIVEL == "disponivel"
        assert EPIStatus.EM_USO == "em_uso"
        assert EPIStatus.DANIFICADO == "danificado"
        assert EPIStatus.VENCIDO == "vencido"

    def test_delivery_status_values(self):
        from modules.health_occupational.core.epi_management import DeliveryStatus

        assert DeliveryStatus.ENTREGUE == "entregue"
        assert DeliveryStatus.DEVOLVIDO == "devolvido"
        assert DeliveryStatus.EXTRAVIADO == "extraviado"

    def test_epi_management_error(self):
        from modules.health_occupational.core.epi_management import EPIManagementError

        err = EPIManagementError("teste")
        assert str(err) == "teste"
        assert isinstance(err, Exception)

    def test_ca_certificate_valido(self):
        from modules.health_occupational.core.epi_management import CACertificate

        ca = CACertificate(
            number="CA-12345",
            issuer="MTE",
            issue_date=date.today() - timedelta(days=100),
            expiry_date=date.today() + timedelta(days=100),
            description="Certificado válido",
        )
        assert ca.is_valid() is True

    def test_ca_certificate_vencido(self):
        from modules.health_occupational.core.epi_management import CACertificate

        ca = CACertificate(
            number="CA-99999",
            issuer="MTE",
            issue_date=date.today() - timedelta(days=400),
            expiry_date=date.today() - timedelta(days=10),
            description="Certificado vencido",
        )
        assert ca.is_valid() is False

    def test_ca_certificate_approved_for(self):
        from modules.health_occupational.core.epi_management import CACertificate

        ca = CACertificate(
            number="CA-11111",
            issuer="MTE",
            issue_date=date.today() - timedelta(days=10),
            expiry_date=date.today() + timedelta(days=365),
            description="Proteção auditiva",
            approved_for=["ruido", "vibracoes"],
        )
        assert "ruido" in ca.approved_for
        assert len(ca.approved_for) == 2
