"""
Testes para e-CAC - Centro Virtual de Atendimento ao Contribuinte.

Testes unitarios e de integracao para o modulo e-CAC.
"""

from datetime import date, datetime
from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

import pytest

from modules.government_integrations.core.ecac import (
    Certidao,
    DebitoFiscal,
    DeclaracaoConsultada,
    EcacManager,
    PendenciaFiscal,
    ResultadoSituacaoFiscal,
    SituacaoFiscal,
    TipoCertidao,
    TipoDeclaracaoConsulta,
    TipoPendencia,
)
from modules.government_integrations.schemas.ecac import (
    ConsultaDebitosRequest,
    ConsultaDeclaracoesRequest,
    ConsultaParcelamentosRequest,
    ConsultaProcessosRequest,
    ConsultaSituacaoFiscalRequest,
    EmitirCertidaoRequest,
    SimularParcelamentoRequest,
    SituacaoDebitoEnum,
    SituacaoFiscalEnum,
    SituacaoProcessoEnum,
    TipoCertidaoEnum,
    TipoDeclaracaoEnum,
    TipoPendenciaEnum,
    ValidarCertidaoRequest,
)
from modules.government_integrations.services.ecac_service import (
    EcacService,
)


class TestSchemas:
    """Testes para schemas de validacao."""

    def test_consulta_situacao_fiscal_request_valid(self):
        """Testa ConsultaSituacaoFiscalRequest valido."""
        request = ConsultaSituacaoFiscalRequest(cpf_cnpj="12345678000199")
        assert request.cpf_cnpj == "12345678000199"

    def test_consulta_situacao_fiscal_request_limpa_formatacao(self):
        """Testa limpeza de formatacao do CPF/CNPJ."""
        request = ConsultaSituacaoFiscalRequest(cpf_cnpj="12.345.678/0001-99")
        assert request.cpf_cnpj == "12345678000199"

    def test_consulta_situacao_fiscal_request_opcional(self):
        """Testa request sem CPF/CNPJ."""
        request = ConsultaSituacaoFiscalRequest()
        assert request.cpf_cnpj is None

    def test_consulta_debitos_request_valid(self):
        """Testa ConsultaDebitosRequest valido."""
        request = ConsultaDebitosRequest(
            situacao=SituacaoDebitoEnum.ABERTO, competencia_inicio="2025-01", competencia_fim="2025-12"
        )
        assert request.situacao == SituacaoDebitoEnum.ABERTO
        assert request.competencia_inicio == "2025-01"

    def test_consulta_debitos_request_sem_filtros(self):
        """Testa request de debitos sem filtros."""
        request = ConsultaDebitosRequest()
        assert request.situacao is None
        assert request.competencia_inicio is None

    def test_consulta_declaracoes_request_valid(self):
        """Testa ConsultaDeclaracoesRequest valido."""
        request = ConsultaDeclaracoesRequest(tipo=TipoDeclaracaoEnum.DCTFWEB, exercicio_inicio=2025, exercicio_fim=2026)
        assert request.tipo == TipoDeclaracaoEnum.DCTFWEB
        assert request.exercicio_inicio == 2025

    def test_consulta_declaracoes_request_sem_fim(self):
        """Testa request sem exercicio final."""
        request = ConsultaDeclaracoesRequest(tipo=TipoDeclaracaoEnum.IRPF, exercicio_inicio=2025)
        assert request.exercicio_fim is None

    def test_emitir_certidao_request_valid(self):
        """Testa EmitirCertidaoRequest valido."""
        request = EmitirCertidaoRequest(finalidade="Licitacao publica", cpf_cnpj="12345678000199")
        assert request.finalidade == "Licitacao publica"

    def test_emitir_certidao_request_limpa_cpf_cnpj(self):
        """Testa limpeza de CPF/CNPJ na emissao."""
        request = EmitirCertidaoRequest(cpf_cnpj="12.345.678/0001-99")
        assert request.cpf_cnpj == "12345678000199"

    def test_validar_certidao_request_valid(self):
        """Testa ValidarCertidaoRequest valido."""
        request = ValidarCertidaoRequest(numero="123456789", codigo_controle="ABCD1234EFGH5678")
        assert request.numero == "123456789"
        assert request.codigo_controle == "ABCD1234EFGH5678"

    def test_simular_parcelamento_request_valid(self):
        """Testa SimularParcelamentoRequest valido."""
        request = SimularParcelamentoRequest(debitos=["DEB001", "DEB002"], quantidade_parcelas=12)
        assert len(request.debitos) == 2
        assert request.quantidade_parcelas == 12

    def test_simular_parcelamento_request_limite_parcelas(self):
        """Testa limite de parcelas (2 a 60)."""
        # Valido
        request = SimularParcelamentoRequest(debitos=["DEB001"], quantidade_parcelas=60)
        assert request.quantidade_parcelas == 60

    def test_consulta_processos_request_valid(self):
        """Testa ConsultaProcessosRequest valido."""
        request = ConsultaProcessosRequest(situacao=SituacaoProcessoEnum.ATIVO, numero_processo="12345.678901/2025-01")
        assert request.situacao == SituacaoProcessoEnum.ATIVO

    def test_enums_valores(self):
        """Testa valores dos enums."""
        assert TipoCertidaoEnum.CND.value == "cnd"
        assert TipoCertidaoEnum.CPEN.value == "cpen"
        assert TipoCertidaoEnum.CPD.value == "cpd"

        assert SituacaoFiscalEnum.REGULAR.value == "regular"
        assert SituacaoFiscalEnum.PENDENTE.value == "pendente"
        assert SituacaoFiscalEnum.IRREGULAR.value == "irregular"

        assert TipoDeclaracaoEnum.DCTFWEB.value == "dctfweb"
        assert TipoDeclaracaoEnum.IRPF.value == "irpf"


class TestEcacManager:
    """Testes para EcacManager."""

    @pytest.fixture
    def manager(self):
        """Cria instancia do manager para testes."""
        return EcacManager(
            cnpj_cpf="35710481000103",
            certificado_path="",
            certificado_senha="",
        )

    @pytest.fixture
    def manager_cpf(self):
        """Cria instancia do manager para CPF."""
        return EcacManager(
            cnpj_cpf="12345678901",
            certificado_path="",
            certificado_senha="",
        )

    def test_init_cnpj(self, manager):
        """Testa inicializacao com CNPJ."""
        assert manager.cnpj_cpf == "35710481000103"
        assert manager.tipo_documento == "CNPJ"

    def test_init_cpf(self, manager_cpf):
        """Testa inicializacao com CPF."""
        assert manager_cpf.cnpj_cpf == "12345678901"
        assert manager_cpf.tipo_documento == "CPF"

    def test_init_limpa_formatacao(self):
        """Testa limpeza de formatacao na inicializacao."""
        manager = EcacManager(
            cnpj_cpf="35.710.481/0001-03",
            certificado_path="",
            certificado_senha="",
        )
        assert manager.cnpj_cpf == "35710481000103"

    def test_consultar_situacao_fiscal(self, manager):
        """Testa consulta de situacao fiscal."""
        resultado = manager.consultar_situacao_fiscal()

        assert resultado.cpf_cnpj == "35710481000103"
        assert resultado.situacao == SituacaoFiscal.REGULAR
        assert isinstance(resultado.data_consulta, datetime)

    def test_consultar_debitos(self, manager):
        """Testa consulta de debitos."""
        debitos = manager.consultar_debitos()

        assert isinstance(debitos, list)

    def test_consultar_debitos_com_filtro(self, manager):
        """Testa consulta de debitos com filtro."""
        debitos = manager.consultar_debitos(situacao="aberto")

        assert isinstance(debitos, list)

    def test_emitir_certidao(self, manager):
        """Testa emissao de certidao."""
        certidao = manager.emitir_certidao(finalidade="Licitacao")

        assert certidao.tipo == TipoCertidao.CND
        assert certidao.contribuinte_cpf_cnpj == "35710481000103"
        assert certidao.finalidade == "Licitacao"

    def test_validar_certidao(self, manager):
        """Testa validacao de certidao."""
        resultado = manager.validar_certidao(numero="123456", codigo_controle="ABCD1234")

        assert resultado["numero"] == "123456"
        assert resultado["codigo_controle"] == "ABCD1234"
        assert resultado["valida"] is True

    def test_consultar_declaracoes(self, manager):
        """Testa consulta de declaracoes."""
        declaracoes = manager.consultar_declaracoes(
            tipo=TipoDeclaracaoConsulta.DCTFWEB, exercicio_inicio=2025, exercicio_fim=2026
        )

        assert isinstance(declaracoes, list)

    def test_consultar_declaracoes_sem_fim(self, manager):
        """Testa consulta com apenas exercicio inicial."""
        declaracoes = manager.consultar_declaracoes(tipo=TipoDeclaracaoConsulta.IRPF, exercicio_inicio=2025)

        assert isinstance(declaracoes, list)

    def test_consultar_parcelamentos(self, manager):
        """Testa consulta de parcelamentos."""
        parcelamentos = manager.consultar_parcelamentos()

        assert isinstance(parcelamentos, list)

    def test_simular_parcelamento(self, manager):
        """Testa simulacao de parcelamento."""
        resultado = manager.simular_parcelamento(debitos=["DEB001", "DEB002"], quantidade_parcelas=12)

        assert resultado["debitos"] == ["DEB001", "DEB002"]
        assert resultado["quantidade_parcelas"] == 12
        assert resultado["status"] == "simulacao"

    def test_consultar_processos(self, manager):
        """Testa consulta de processos."""
        processos = manager.consultar_processos()

        assert isinstance(processos, list)

    def test_consultar_processos_com_filtro(self, manager):
        """Testa consulta de processos com filtro."""
        processos = manager.consultar_processos(situacao="ativo")

        assert isinstance(processos, list)

    def test_url_producao(self, manager):
        """Testa URL de producao."""
        assert "receita.fazenda.gov.br" in manager.URL_PRODUCAO


class TestEcacService:
    """Testes para EcacService."""

    @pytest.fixture
    def service(self):
        """Cria instancia do service para testes."""
        with patch.dict(
            "os.environ",
            {
                "ECAC_CPF_CNPJ": "35710481000103",
                "CERTIFICATE_PATH": "",
            },
        ):
            return EcacService()

    def test_service_init(self, service):
        """Testa inicializacao do service."""
        assert service.cpf_cnpj == "35710481000103"
        assert service.manager.tipo_documento == "CNPJ"

    def test_consultar_situacao_fiscal(self, service):
        """Testa consulta de situacao fiscal via service."""
        resultado = service.consultar_situacao_fiscal()

        assert resultado["cpf_cnpj"] == "35710481000103"
        assert resultado["situacao"] == "regular"
        assert "data_consulta" in resultado
        assert "pendencias" in resultado
        assert "debitos" in resultado

    def test_consultar_situacao_fiscal_outro_documento(self, service):
        """Testa consulta com outro documento."""
        resultado = service.consultar_situacao_fiscal(cpf_cnpj="12345678901")

        assert resultado["cpf_cnpj"] == "12345678901"

    def test_consultar_debitos(self, service):
        """Testa consulta de debitos via service."""
        resultado = service.consultar_debitos()

        assert resultado["cpf_cnpj"] == "35710481000103"
        assert "quantidade" in resultado
        assert "valor_total" in resultado
        assert "debitos" in resultado

    def test_consultar_debitos_com_filtros(self, service):
        """Testa consulta de debitos com filtros."""
        resultado = service.consultar_debitos(
            situacao="aberto", competencia_inicio="2025-01", competencia_fim="2025-12"
        )

        assert resultado["filtros"]["situacao"] == "aberto"
        assert resultado["filtros"]["competencia_inicio"] == "2025-01"

    def test_emitir_certidao(self, service):
        """Testa emissao de certidao via service."""
        resultado = service.emitir_certidao(finalidade="Licitacao")

        assert resultado["tipo"] == "cnd"
        assert resultado["contribuinte_cpf_cnpj"] == "35710481000103"
        assert resultado["finalidade"] == "Licitacao"

    def test_emitir_certidao_outro_documento(self, service):
        """Testa emissao com outro documento."""
        resultado = service.emitir_certidao(cpf_cnpj="12345678901")

        assert resultado["contribuinte_cpf_cnpj"] == "12345678901"

    def test_validar_certidao(self, service):
        """Testa validacao de certidao via service."""
        resultado = service.validar_certidao(numero="123456", codigo_controle="ABCD1234")

        assert resultado["numero"] == "123456"
        assert resultado["valida"] is True
        assert "data_validacao" in resultado

    def test_consultar_declaracoes(self, service):
        """Testa consulta de declaracoes via service."""
        resultado = service.consultar_declaracoes(tipo="dctfweb", exercicio_inicio=2025)

        assert resultado["cpf_cnpj"] == "35710481000103"
        assert resultado["tipo"] == "dctfweb"
        assert resultado["exercicio_inicio"] == 2025

    def test_consultar_declaracoes_range(self, service):
        """Testa consulta de declaracoes com range."""
        resultado = service.consultar_declaracoes(tipo="irpf", exercicio_inicio=2020, exercicio_fim=2025)

        assert resultado["exercicio_inicio"] == 2020
        assert resultado["exercicio_fim"] == 2025

    def test_consultar_parcelamentos(self, service):
        """Testa consulta de parcelamentos via service."""
        resultado = service.consultar_parcelamentos()

        assert resultado["cpf_cnpj"] == "35710481000103"
        assert "quantidade" in resultado
        assert "parcelamentos" in resultado

    def test_consultar_parcelamentos_com_filtro(self, service):
        """Testa consulta de parcelamentos com filtro."""
        resultado = service.consultar_parcelamentos(situacao="ativo")

        assert isinstance(resultado["parcelamentos"], list)

    def test_simular_parcelamento(self, service):
        """Testa simulacao de parcelamento via service."""
        resultado = service.simular_parcelamento(debitos=["DEB001", "DEB002", "DEB003"], quantidade_parcelas=12)

        assert resultado["cpf_cnpj"] == "35710481000103"
        assert resultado["quantidade_debitos"] == 3
        assert resultado["quantidade_parcelas"] == 12
        assert resultado["status"] == "simulacao"

    def test_consultar_processos(self, service):
        """Testa consulta de processos via service."""
        resultado = service.consultar_processos()

        assert resultado["cpf_cnpj"] == "35710481000103"
        assert "quantidade" in resultado
        assert "processos" in resultado

    def test_consultar_processos_com_filtros(self, service):
        """Testa consulta de processos com filtros."""
        resultado = service.consultar_processos(situacao="ativo", numero_processo="12345")

        assert resultado["filtros"]["situacao"] == "ativo"
        assert resultado["filtros"]["numero_processo"] == "12345"

    def test_validar_status(self, service):
        """Testa validacao de status."""
        status = service.validar_status()

        assert status["cpf_cnpj"] == "35710481000103"
        assert status["tipo_documento"] == "CNPJ"
        assert status["certificado_configurado"] is False
        assert len(status["servicos_disponiveis"]) > 0


class TestEcacEndpoints:
    """Testes para endpoints REST."""

    @pytest.fixture
    def client(self):
        """Cliente de teste HTTP."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()

        from modules.government_integrations.controllers.ecac_controller import router

        app.include_router(router, prefix="/api/v1/government")

        return TestClient(app)

    def test_get_status(self, client):
        """Testa endpoint de status."""
        response = client.get("/api/v1/government/ecac/status")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "servicos_disponiveis" in data["data"]

    def test_consultar_situacao_fiscal_endpoint(self, client):
        """Testa endpoint de situacao fiscal."""
        response = client.get("/api/v1/government/ecac/situacao-fiscal")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "situacao" in data["data"]

    def test_consultar_situacao_fiscal_com_documento(self, client):
        """Testa endpoint com documento especifico."""
        response = client.get("/api/v1/government/ecac/situacao-fiscal", params={"cpf_cnpj": "12345678901"})

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["cpf_cnpj"] == "12345678901"

    def test_consultar_debitos_endpoint(self, client):
        """Testa endpoint de debitos."""
        response = client.get("/api/v1/government/ecac/debitos")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "debitos" in data["data"]

    def test_consultar_debitos_com_filtros(self, client):
        """Testa endpoint de debitos com filtros."""
        response = client.get(
            "/api/v1/government/ecac/debitos",
            params={"situacao": "aberto", "competencia_inicio": "2025-01", "competencia_fim": "2025-12"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["filtros"]["situacao"] == "aberto"

    def test_consultar_declaracoes_endpoint(self, client):
        """Testa endpoint de declaracoes."""
        response = client.get(
            "/api/v1/government/ecac/declaracoes", params={"tipo": "dctfweb", "exercicio_inicio": 2025}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["tipo"] == "dctfweb"

    def test_consultar_declaracoes_range(self, client):
        """Testa endpoint de declaracoes com range."""
        response = client.get(
            "/api/v1/government/ecac/declaracoes",
            params={"tipo": "irpf", "exercicio_inicio": 2020, "exercicio_fim": 2025},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["exercicio_inicio"] == 2020
        assert data["data"]["exercicio_fim"] == 2025

    def test_emitir_certidao_endpoint(self, client):
        """Testa endpoint de emissao de certidao."""
        payload = {"finalidade": "Licitacao publica"}

        response = client.post("/api/v1/government/ecac/certidao", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "tipo" in data["data"]

    def test_emitir_certidao_com_documento(self, client):
        """Testa emissao de certidao com documento especifico."""
        payload = {"finalidade": "Contratacao", "cpf_cnpj": "12345678901"}

        response = client.post("/api/v1/government/ecac/certidao", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["contribuinte_cpf_cnpj"] == "12345678901"

    def test_validar_certidao_endpoint(self, client):
        """Testa endpoint de validacao de certidao."""
        payload = {"numero": "123456789", "codigo_controle": "ABCD1234EFGH5678"}

        response = client.post("/api/v1/government/ecac/validar-certidao", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "valida" in data["data"]

    def test_consultar_parcelamentos_endpoint(self, client):
        """Testa endpoint de parcelamentos."""
        response = client.get("/api/v1/government/ecac/parcelamentos")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "parcelamentos" in data["data"]

    def test_consultar_parcelamentos_com_filtro(self, client):
        """Testa endpoint de parcelamentos com filtro."""
        response = client.get("/api/v1/government/ecac/parcelamentos", params={"situacao": "ativo"})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_simular_parcelamento_endpoint(self, client):
        """Testa endpoint de simulacao de parcelamento."""
        payload = {"debitos": ["DEB001", "DEB002", "DEB003"], "quantidade_parcelas": 12}

        response = client.post("/api/v1/government/ecac/simular-parcelamento", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["quantidade_parcelas"] == 12

    def test_consultar_processos_endpoint(self, client):
        """Testa endpoint de processos."""
        response = client.get("/api/v1/government/ecac/processos")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "processos" in data["data"]

    def test_consultar_processos_com_filtros(self, client):
        """Testa endpoint de processos com filtros."""
        response = client.get(
            "/api/v1/government/ecac/processos", params={"situacao": "ativo", "numero_processo": "12345"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["filtros"]["situacao"] == "ativo"


class TestSingleton:
    """Testes para singleton do service."""

    def test_get_ecac_service_singleton(self):
        """Testa que get_ecac_service retorna singleton."""
        # Reset singleton
        import modules.government_integrations.services.ecac_service as module
        from modules.government_integrations.services.ecac_service import _ecac_service, get_ecac_service

        module._ecac_service = None

        service1 = get_ecac_service()
        service2 = get_ecac_service()

        assert service1 is service2

        # Cleanup
        module._ecac_service = None
