"""
Testes para SPED Fiscal.

Testes unitários e de integração para SPED Fiscal (EFD ICMS/IPI).
"""

import pytest
from decimal import Decimal
from datetime import datetime, date
from unittest.mock import Mock, patch

from modules.government_integrations.schemas.sped_fiscal import (
    ParticipanteRequest,
    ProdutoRequest,
    DocumentoFiscalRequest,
    InventarioRequest,
    GerarArquivoRequest,
    CalcularApuracaoRequest,
    FinalidadeArquivoEnum,
    TipoItemEnum,
)
from modules.government_integrations.services.sped_fiscal_service import (
    SPEDFiscalService,
)
from modules.government_integrations.core.sped_fiscal import (
    SPEDFiscalManager,
    Participante,
    Produto,
    DocumentoFiscal,
    Inventario,
    ApuracaoICMS,
    FinalidadeArquivo,
    PerfilArquivo,
)


class TestSchemas:
    """Testes para schemas de validação."""

    def test_participante_request_valid(self):
        """Testa request de participante válido."""
        request = ParticipanteRequest(
            codigo="FORN001",
            nome="Fornecedor Exemplo",
            cnpj_cpf="12345678000190",
            uf="SP",
        )
        assert request.codigo == "FORN001"
        assert request.cnpj_cpf == "12345678000190"

    def test_produto_request_valid(self):
        """Testa request de produto válido."""
        request = ProdutoRequest(
            codigo="PROD001",
            descricao="Produto Exemplo",
            ncm="84713012",
        )
        assert request.codigo == "PROD001"
        assert request.tipo_item == TipoItemEnum.MERCADORIA_REVENDA

    def test_documento_fiscal_request_valid(self):
        """Testa request de documento válido."""
        request = DocumentoFiscalRequest(
            tipo="55",
            chave="35260100000000000000550010000000011000000011",
            numero="1",
            serie="1",
            data_emissao="2026-01-15",
            data_entrada_saida="2026-01-15",
            codigo_participante="FORN001",
            valor_total=Decimal("10000.00"),
            cfop="1102",
        )
        assert request.tipo == "55"
        assert len(request.chave) == 44

    def test_inventario_request_valid(self):
        """Testa request de inventário válido."""
        request = InventarioRequest(
            codigo_item="PROD001",
            descricao="Produto Exemplo",
            quantidade=Decimal("100"),
            valor_unitario=Decimal("50.00"),
            valor_total=Decimal("5000.00"),
        )
        assert request.quantidade == Decimal("100")


class TestSPEDFiscalManager:
    """Testes para SPEDFiscalManager."""

    @pytest.fixture
    def manager(self):
        """Cria instância do manager."""
        return SPEDFiscalManager(
            cnpj="35710481000103",
            razao_social="Empresa Teste",
            inscricao_estadual="123456789",
            uf="SP",
            codigo_municipio="3550308",
        )

    def test_init(self, manager):
        """Testa inicialização."""
        assert manager.cnpj == "35710481000103"
        assert manager.uf == "SP"
        assert manager.perfil == PerfilArquivo.PERFIL_A

    def test_adicionar_participante(self, manager):
        """Testa adição de participante."""
        participante = Participante(
            codigo="FORN001",
            nome="Fornecedor Teste",
            cnpj_cpf="12345678000190",
            uf="SP",
        )

        manager.adicionar_participante(participante)

        assert "FORN001" in manager.participantes
        assert manager.participantes["FORN001"].nome == "Fornecedor Teste"

    def test_adicionar_produto(self, manager):
        """Testa adição de produto."""
        produto = Produto(
            codigo="PROD001",
            descricao="Produto Teste",
            ncm="84713012",
        )

        manager.adicionar_produto(produto)

        assert "PROD001" in manager.produtos

    def test_adicionar_documento(self, manager):
        """Testa adição de documento."""
        participante = Participante(
            codigo="FORN001",
            nome="Fornecedor",
            cnpj_cpf="12345678000190",
        )
        manager.adicionar_participante(participante)

        documento = DocumentoFiscal(
            tipo="55",
            chave="35260100000000000000550010000000011000000011",
            numero="1",
            serie="1",
            data_emissao=date(2026, 1, 15),
            data_entrada_saida=date(2026, 1, 15),
            participante=participante,
            valor_total=Decimal("10000.00"),
            valor_icms=Decimal("1800.00"),
            cfop="1102",
        )

        manager.adicionar_documento(documento)

        assert len(manager.documentos) == 1

    def test_calcular_apuracao(self, manager):
        """Testa cálculo de apuração."""
        participante = Participante(
            codigo="FORN001",
            nome="Fornecedor",
            cnpj_cpf="12345678000190",
        )
        manager.adicionar_participante(participante)

        # Documento de entrada (crédito)
        doc_entrada = DocumentoFiscal(
            tipo="55",
            chave="35260100000000000000550010000000011000000011",
            numero="1",
            serie="1",
            data_emissao=date(2026, 1, 15),
            data_entrada_saida=date(2026, 1, 15),
            participante=participante,
            valor_total=Decimal("10000.00"),
            valor_icms=Decimal("1800.00"),
            cfop="1102",  # Entrada
        )
        manager.adicionar_documento(doc_entrada)

        # Documento de saída (débito)
        doc_saida = DocumentoFiscal(
            tipo="55",
            chave="35260100000000000000550010000000021000000021",
            numero="2",
            serie="1",
            data_emissao=date(2026, 1, 20),
            data_entrada_saida=date(2026, 1, 20),
            participante=participante,
            valor_total=Decimal("15000.00"),
            valor_icms=Decimal("2700.00"),
            cfop="5102",  # Saída
        )
        manager.adicionar_documento(doc_saida)

        apuracao = manager.calcular_apuracao("2026-01")

        # Débitos = 2700 (saídas)
        # Créditos = 1800 (entradas)
        assert apuracao.valor_debitos == Decimal("2700.00")
        assert apuracao.valor_creditos == Decimal("1800.00")
        # Saldo devedor = 2700 - 1800 = 900
        assert apuracao.saldo_devedor == Decimal("900.00")

    def test_gerar_arquivo(self, manager):
        """Testa geração de arquivo."""
        conteudo = manager.gerar_arquivo(
            periodo_inicio=date(2026, 1, 1),
            periodo_fim=date(2026, 1, 31),
        )

        assert "|0000|" in conteudo
        assert "|9999|" in conteudo
        assert "017" in conteudo  # Versão do leiaute

    def test_validar_arquivo(self, manager):
        """Testa validação de arquivo."""
        conteudo = manager.gerar_arquivo(
            periodo_inicio=date(2026, 1, 1),
            periodo_fim=date(2026, 1, 31),
        )

        validacao = manager.validar_arquivo(conteudo)

        assert validacao["valido"] is True
        assert len(validacao["erros"]) == 0


class TestSPEDFiscalService:
    """Testes para SPEDFiscalService."""

    @pytest.fixture
    def service(self):
        """Cria instância do service."""
        with patch.dict('os.environ', {
            'SPED_CNPJ': '35710481000103',
            'EMPRESA_RAZAO_SOCIAL': 'Empresa Teste',
            'EMPRESA_IE': '123456789',
            'EMPRESA_UF': 'SP',
        }):
            return SPEDFiscalService()

    def test_service_init(self, service):
        """Testa inicialização do service."""
        assert service.cnpj == "35710481000103"
        assert service.uf == "SP"

    def test_validar_status(self, service):
        """Testa validação de status."""
        status = service.validar_status()

        assert status["cnpj"] == "35710481000103"
        assert "gerar_arquivo" in status["operacoes_disponiveis"]

    def test_adicionar_participante(self, service):
        """Testa adição de participante via service."""
        dados = {
            "codigo": "FORN001",
            "nome": "Fornecedor Teste",
            "cnpj_cpf": "12345678000190",
        }

        resultado = service.adicionar_participante(dados)

        assert resultado["codigo"] == "FORN001"
        assert resultado["tipo_pessoa"] == "Jurídica"

    def test_adicionar_produto(self, service):
        """Testa adição de produto via service."""
        dados = {
            "codigo": "PROD001",
            "descricao": "Produto Teste",
            "ncm": "84713012",
        }

        resultado = service.adicionar_produto(dados)

        assert resultado["codigo"] == "PROD001"

    def test_adicionar_documento(self, service):
        """Testa adição de documento via service."""
        dados = {
            "tipo": "55",
            "chave": "35260100000000000000550010000000011000000011",
            "numero": "1",
            "serie": "1",
            "data_emissao": "2026-01-15",
            "data_entrada_saida": "2026-01-15",
            "codigo_participante": "FORN001",
            "valor_total": "10000.00",
            "cfop": "1102",
        }

        resultado = service.adicionar_documento(dados)

        assert resultado["numero"] == "1"

    def test_calcular_apuracao(self, service):
        """Testa cálculo de apuração via service."""
        documentos = [
            {
                "tipo": "55",
                "chave": "35260100000000000000550010000000011000000011",
                "numero": "1",
                "serie": "1",
                "data_emissao": "2026-01-15",
                "data_entrada_saida": "2026-01-15",
                "codigo_participante": "FORN001",
                "valor_total": "10000.00",
                "valor_icms": "1800.00",
                "cfop": "1102",
            }
        ]

        resultado = service.calcular_apuracao("2026-01", documentos)

        assert resultado["periodo"] == "2026-01"
        assert "valor_creditos" in resultado

    def test_gerar_arquivo(self, service):
        """Testa geração de arquivo via service."""
        resultado = service.gerar_arquivo(
            periodo_inicio="2026-01-01",
            periodo_fim="2026-01-31",
        )

        assert resultado["periodo_inicio"] == "2026-01-01"
        assert resultado["total_registros"] > 0
        assert "conteudo" in resultado

    def test_listar_blocos(self, service):
        """Testa listagem de blocos."""
        blocos = service.listar_blocos()

        assert "blocos" in blocos
        assert len(blocos["blocos"]) >= 9


class TestSPEDFiscalEndpoints:
    """Testes para endpoints REST."""

    @pytest.fixture
    def client(self):
        """Cliente de teste HTTP."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI

        app = FastAPI()

        from modules.government_integrations.controllers.sped_fiscal_controller import router
        app.include_router(router, prefix="/api/v1/government")

        return TestClient(app)

    def test_get_status(self, client):
        """Testa endpoint de status."""
        response = client.get("/api/v1/government/sped-fiscal/status")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_listar_blocos_endpoint(self, client):
        """Testa endpoint de blocos."""
        response = client.get("/api/v1/government/sped-fiscal/blocos")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "blocos" in data["data"]

    def test_adicionar_participante_endpoint(self, client):
        """Testa endpoint de adicionar participante."""
        payload = {
            "participante": {
                "codigo": "FORN001",
                "nome": "Fornecedor Teste",
                "cnpj_cpf": "12345678000190"
            }
        }

        response = client.post(
            "/api/v1/government/sped-fiscal/participante",
            json=payload
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    def test_adicionar_produto_endpoint(self, client):
        """Testa endpoint de adicionar produto."""
        payload = {
            "produto": {
                "codigo": "PROD001",
                "descricao": "Produto Teste"
            }
        }

        response = client.post(
            "/api/v1/government/sped-fiscal/produto",
            json=payload
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    def test_adicionar_documento_endpoint(self, client):
        """Testa endpoint de adicionar documento."""
        payload = {
            "documento": {
                "tipo": "55",
                "chave": "35260100000000000000550010000000011000000011",
                "numero": "1",
                "serie": "1",
                "data_emissao": "2026-01-15",
                "data_entrada_saida": "2026-01-15",
                "codigo_participante": "FORN001",
                "valor_total": "10000.00",
                "cfop": "1102"
            }
        }

        response = client.post(
            "/api/v1/government/sped-fiscal/documento",
            json=payload
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    def test_gerar_arquivo_endpoint(self, client):
        """Testa endpoint de gerar arquivo."""
        payload = {
            "periodo_inicio": "2026-01-01",
            "periodo_fim": "2026-01-31",
            "finalidade": "0"
        }

        response = client.post(
            "/api/v1/government/sped-fiscal/gerar",
            json=payload
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "conteudo" in data["data"]

    def test_calcular_apuracao_endpoint(self, client):
        """Testa endpoint de apuração."""
        payload = {
            "periodo": "2026-01",
            "documentos": [
                {
                    "tipo": "55",
                    "chave": "35260100000000000000550010000000011000000011",
                    "numero": "1",
                    "serie": "1",
                    "data_emissao": "2026-01-15",
                    "data_entrada_saida": "2026-01-15",
                    "codigo_participante": "FORN001",
                    "valor_total": "10000.00",
                    "valor_icms": "1800.00",
                    "cfop": "1102"
                }
            ]
        }

        response = client.post(
            "/api/v1/government/sped-fiscal/apuracao",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_limpar_dados_endpoint(self, client):
        """Testa endpoint de limpar dados."""
        response = client.delete("/api/v1/government/sped-fiscal/limpar")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
