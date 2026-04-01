"""
Testes para SPED Contábil.

Testes unitários e de integração para SPED Contábil (ECD).
"""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from modules.government_integrations.core.sped_contabil import (
    ContaContabil,
    DemonstrativoBalancoPatrimonial,
    DemonstrativoDRE,
    LancamentoContabil,
    NaturezaConta,
    SPEDContabilManager,
    TipoConta,
    TipoECD,
)
from modules.government_integrations.schemas.sped_contabil import (
    BalancoPatrimonialRequest,
    ContaContabilRequest,
    DRERequest,
    GerarArquivoRequest,
    LancamentoContabilRequest,
    NaturezaContaEnum,
    TipoContaEnum,
)
from modules.government_integrations.services.sped_contabil_service import (
    SPEDContabilService,
)


class TestSchemas:
    """Testes para schemas de validação."""

    def test_conta_contabil_request_valid(self):
        """Testa request de conta válido."""
        request = ContaContabilRequest(
            codigo="1.1.01",
            descricao="Caixa",
            tipo=TipoContaEnum.ANALITICA,
            nivel=3,
            natureza=NaturezaContaEnum.ATIVO,
        )
        assert request.codigo == "1.1.01"
        assert request.natureza == NaturezaContaEnum.ATIVO

    def test_lancamento_request_valid(self):
        """Testa request de lançamento válido."""
        request = LancamentoContabilRequest(
            numero=1,
            data="2026-01-15",
            conta_debito="1.1.01",
            conta_credito="3.1.01",
            valor=Decimal("10000.00"),
            historico="Receita de serviços",
        )
        assert request.numero == 1
        assert request.valor == Decimal("10000.00")

    def test_balanco_request_valid(self):
        """Testa request de balanço válido."""
        request = BalancoPatrimonialRequest(
            data_referencia="2026-12-31",
            ativo_circulante=Decimal("500000.00"),
            passivo_circulante=Decimal("200000.00"),
            patrimonio_liquido=Decimal("300000.00"),
        )
        assert request.ativo_circulante == Decimal("500000.00")

    def test_dre_request_valid(self):
        """Testa request de DRE válido."""
        request = DRERequest(
            periodo_inicio="2026-01-01",
            periodo_fim="2026-12-31",
            receita_bruta=Decimal("1200000.00"),
            custos=Decimal("600000.00"),
        )
        assert request.receita_bruta == Decimal("1200000.00")


class TestSPEDContabilManager:
    """Testes para SPEDContabilManager."""

    @pytest.fixture
    def manager(self):
        """Cria instância do manager."""
        return SPEDContabilManager(
            cnpj="35710481000103",
            razao_social="Empresa Teste",
        )

    def test_init(self, manager):
        """Testa inicialização."""
        assert manager.cnpj == "35710481000103"
        assert manager.tipo_ecd == TipoECD.LIVRO_DIARIO_GERAL

    def test_adicionar_conta(self, manager):
        """Testa adição de conta."""
        conta = ContaContabil(
            codigo="1.1.01",
            descricao="Caixa",
            tipo=TipoConta.ANALITICA,
            nivel=3,
            natureza=NaturezaConta.ATIVO,
        )

        manager.adicionar_conta(conta)

        assert "1.1.01" in manager.plano_contas

    def test_adicionar_lancamento(self, manager):
        """Testa adição de lançamento."""
        lancamento = LancamentoContabil(
            numero=1,
            data=date(2026, 1, 15),
            conta_debito="1.1.01",
            conta_credito="3.1.01",
            valor=Decimal("10000.00"),
            historico="Receita de serviços",
        )

        manager.adicionar_lancamento(lancamento)

        assert len(manager.lancamentos) == 1

    def test_calcular_saldos(self, manager):
        """Testa cálculo de saldos."""
        # Adiciona conta
        conta = ContaContabil(
            codigo="1.1.01",
            descricao="Caixa",
            tipo=TipoConta.ANALITICA,
            nivel=3,
            natureza=NaturezaConta.ATIVO,
            saldo_inicial_debito=Decimal("1000.00"),
        )
        manager.adicionar_conta(conta)

        # Adiciona lançamento
        lancamento = LancamentoContabil(
            numero=1,
            data=date(2026, 1, 15),
            conta_debito="1.1.01",
            conta_credito="3.1.01",
            valor=Decimal("500.00"),
            historico="Receita",
        )
        manager.adicionar_lancamento(lancamento)

        saldos = manager.calcular_saldos(date(2026, 1, 1), date(2026, 1, 31))

        assert len(saldos) == 1
        # Saldo inicial 1000 + débito 500 = 1500
        assert saldos[0].saldo_final_debito == Decimal("1500.00")

    def test_gerar_arquivo(self, manager):
        """Testa geração de arquivo."""
        conteudo = manager.gerar_arquivo(
            ano_referencia=2026,
            periodo_inicio=date(2026, 1, 1),
            periodo_fim=date(2026, 12, 31),
        )

        assert "|0000|" in conteudo
        assert "|9999|" in conteudo
        assert "LECD" in conteudo

    def test_validar_arquivo(self, manager):
        """Testa validação de arquivo."""
        conteudo = manager.gerar_arquivo(
            ano_referencia=2026,
            periodo_inicio=date(2026, 1, 1),
            periodo_fim=date(2026, 12, 31),
        )

        validacao = manager.validar_arquivo(conteudo)

        assert validacao["valido"] is True


class TestSPEDContabilService:
    """Testes para SPEDContabilService."""

    @pytest.fixture
    def service(self):
        """Cria instância do service."""
        with patch.dict(
            "os.environ",
            {
                "SPED_CNPJ": "35710481000103",
                "EMPRESA_RAZAO_SOCIAL": "Empresa Teste",
            },
        ):
            return SPEDContabilService()

    def test_service_init(self, service):
        """Testa inicialização do service."""
        assert service.cnpj == "35710481000103"

    def test_validar_status(self, service):
        """Testa validação de status."""
        status = service.validar_status()

        assert status["cnpj"] == "35710481000103"
        assert "gerar_arquivo" in status["operacoes_disponiveis"]

    def test_adicionar_conta(self, service):
        """Testa adição de conta via service."""
        dados = {
            "codigo": "1.1.01",
            "descricao": "Caixa",
            "tipo": "A",
            "nivel": 3,
            "natureza": "01",
        }

        resultado = service.adicionar_conta(dados)

        assert resultado["codigo"] == "1.1.01"

    def test_adicionar_lancamento(self, service):
        """Testa adição de lançamento via service."""
        dados = {
            "numero": 1,
            "data": "2026-01-15",
            "conta_debito": "1.1.01",
            "conta_credito": "3.1.01",
            "valor": "10000.00",
            "historico": "Receita",
        }

        resultado = service.adicionar_lancamento(dados)

        assert resultado["numero"] == 1

    def test_definir_balanco(self, service):
        """Testa definição de balanço via service."""
        dados = {
            "data_referencia": "2026-12-31",
            "ativo_circulante": "500000.00",
            "patrimonio_liquido": "500000.00",
        }

        resultado = service.definir_balanco(dados)

        # Compara valores numericos ignorando formatacao
        assert Decimal(resultado["total_ativo"]) == Decimal("500000")

    def test_definir_dre(self, service):
        """Testa definição de DRE via service."""
        dados = {
            "periodo_inicio": "2026-01-01",
            "periodo_fim": "2026-12-31",
            "receita_bruta": "1200000.00",
            "custos": "600000.00",
        }

        resultado = service.definir_dre(dados)

        assert resultado["receita_liquida"] == "1200000.00"
        assert resultado["lucro_bruto"] == "600000.00"

    def test_gerar_arquivo(self, service):
        """Testa geração de arquivo via service."""
        resultado = service.gerar_arquivo(
            ano_referencia=2026,
            periodo_inicio="2026-01-01",
            periodo_fim="2026-12-31",
        )

        assert resultado["ano_referencia"] == 2026
        assert resultado["total_registros"] > 0

    def test_listar_blocos(self, service):
        """Testa listagem de blocos."""
        blocos = service.listar_blocos()

        assert "blocos" in blocos
        assert len(blocos["blocos"]) >= 5


class TestSPEDContabilEndpoints:
    """Testes para endpoints REST."""

    @pytest.fixture
    def client(self):
        """Cliente de teste HTTP."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()

        from modules.government_integrations.controllers.sped_contabil_controller import router

        app.include_router(router, prefix="/api/v1/government")

        return TestClient(app)

    def test_get_status(self, client):
        """Testa endpoint de status."""
        response = client.get("/api/v1/government/sped-contabil/status")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_listar_blocos_endpoint(self, client):
        """Testa endpoint de blocos."""
        response = client.get("/api/v1/government/sped-contabil/blocos")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_listar_tipos_ecd_endpoint(self, client):
        """Testa endpoint de tipos ECD."""
        response = client.get("/api/v1/government/sped-contabil/tipos-ecd")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_adicionar_conta_endpoint(self, client):
        """Testa endpoint de adicionar conta."""
        payload = {"conta": {"codigo": "1.1.01", "descricao": "Caixa", "tipo": "A", "nivel": 3, "natureza": "01"}}

        response = client.post("/api/v1/government/sped-contabil/conta", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    def test_adicionar_lancamento_endpoint(self, client):
        """Testa endpoint de adicionar lançamento."""
        payload = {
            "lancamento": {
                "numero": 1,
                "data": "2026-01-15",
                "conta_debito": "1.1.01",
                "conta_credito": "3.1.01",
                "valor": "10000.00",
                "historico": "Receita de serviços",
            }
        }

        response = client.post("/api/v1/government/sped-contabil/lancamento", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    def test_definir_balanco_endpoint(self, client):
        """Testa endpoint de definir balanço."""
        payload = {
            "balanco": {
                "data_referencia": "2026-12-31",
                "ativo_circulante": "500000.00",
                "patrimonio_liquido": "500000.00",
            }
        }

        response = client.post("/api/v1/government/sped-contabil/balanco", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    def test_definir_dre_endpoint(self, client):
        """Testa endpoint de definir DRE."""
        payload = {"dre": {"periodo_inicio": "2026-01-01", "periodo_fim": "2026-12-31", "receita_bruta": "1200000.00"}}

        response = client.post("/api/v1/government/sped-contabil/dre", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    def test_gerar_arquivo_endpoint(self, client):
        """Testa endpoint de gerar arquivo."""
        payload = {"ano_referencia": 2026, "periodo_inicio": "2026-01-01", "periodo_fim": "2026-12-31"}

        response = client.post("/api/v1/government/sped-contabil/gerar", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "conteudo" in data["data"]

    def test_limpar_dados_endpoint(self, client):
        """Testa endpoint de limpar dados."""
        response = client.delete("/api/v1/government/sped-contabil/limpar")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
