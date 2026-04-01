"""
Testes para CT-e (Conhecimento de Transporte Eletronico).

Testes unitarios e de integracao para CT-e.
"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from modules.government_integrations.core.cte import (
    Carga,
    ComponenteValor,
    CTe,
    CTeManager,
    ModalTransporte,
    NFReferenciada,
    Participante,
    SituacaoCTe,
    TipoServico,
    TomadorServico,
)
from modules.government_integrations.schemas.cte import (
    CargaRequest,
    ComponenteValorRequest,
    CriarCTeRequest,
    GerarXMLRequest,
    ModalTransporteEnum,
    NFReferenciadaRequest,
    ParticipanteRequest,
    SituacaoCTeEnum,
    TipoServicoEnum,
    TomadorServicoEnum,
)
from modules.government_integrations.services.cte_service import (
    CTeService,
)


class TestSchemas:
    """Testes para schemas de validacao."""

    def test_participante_request_valid(self):
        """Testa request de participante valido."""
        request = ParticipanteRequest(
            tipo="remetente",
            cnpj_cpf="12345678000190",
            nome="Empresa Remetente Ltda",
            uf="SP",
        )
        assert request.tipo == "remetente"
        assert request.cnpj_cpf == "12345678000190"

    def test_nf_referenciada_request_valid(self):
        """Testa request de NF referenciada valida."""
        request = NFReferenciadaRequest(chave="35260100000000000000550010000000011000000011")
        assert len(request.chave) == 44

    def test_carga_request_valid(self):
        """Testa request de carga valida."""
        request = CargaRequest(
            valor_total_carga=Decimal("50000.00"),
            produto_predominante="ELETRONICOS",
            peso_bruto=Decimal("1000.00"),
            quantidade_volumes=50,
        )
        assert request.valor_total_carga == Decimal("50000.00")
        assert request.produto_predominante == "ELETRONICOS"

    def test_componente_valor_request_valid(self):
        """Testa request de componente de valor valido."""
        request = ComponenteValorRequest(
            nome="FRETE VALOR",
            valor=Decimal("1500.00"),
        )
        assert request.nome == "FRETE VALOR"
        assert request.valor == Decimal("1500.00")

    def test_criar_cte_request_valid(self):
        """Testa request de criacao de CT-e valido."""
        request = CriarCTeRequest(
            numero=1,
            serie=1,
            modal=ModalTransporteEnum.RODOVIARIO,
            tipo_servico=TipoServicoEnum.NORMAL,
            valor_total_servico=Decimal("1500.00"),
            valor_receber=Decimal("1500.00"),
        )
        assert request.numero == 1
        assert request.modal == ModalTransporteEnum.RODOVIARIO

    def test_gerar_xml_request_valid(self):
        """Testa request de geracao de XML valido."""
        request = GerarXMLRequest(
            numero=1,
            serie=1,
            modal=ModalTransporteEnum.RODOVIARIO,
        )
        assert request.numero == 1


class TestCTeManager:
    """Testes para CTeManager."""

    @pytest.fixture
    def manager(self):
        """Cria instancia do manager."""
        return CTeManager(
            cnpj="35710481000103",
            razao_social="Transportadora Teste",
            inscricao_estadual="123456789",
            uf="SP",
            ambiente="homologacao",
        )

    def test_init(self, manager):
        """Testa inicializacao."""
        assert manager.cnpj == "35710481000103"
        assert manager.uf == "SP"
        assert manager.ambiente == "homologacao"

    def test_criar_cte(self, manager):
        """Testa criacao de CT-e."""
        cte = manager.criar_cte(
            numero=1,
            serie=1,
            modal=ModalTransporte.RODOVIARIO,
        )

        assert cte.numero == 1
        assert cte.serie == 1
        assert cte.modal == ModalTransporte.RODOVIARIO
        assert cte.situacao == SituacaoCTe.EM_DIGITACAO

    def test_criar_cte_aereo(self, manager):
        """Testa criacao de CT-e aereo."""
        cte = manager.criar_cte(
            numero=2,
            serie=1,
            modal=ModalTransporte.AEREO,
        )

        assert cte.modal == ModalTransporte.AEREO

    def test_criar_cte_aquaviario(self, manager):
        """Testa criacao de CT-e aquaviario."""
        cte = manager.criar_cte(
            numero=3,
            serie=1,
            modal=ModalTransporte.AQUAVIARIO,
        )

        assert cte.modal == ModalTransporte.AQUAVIARIO

    def test_gerar_xml(self, manager):
        """Testa geracao de XML."""
        cte = manager.criar_cte(numero=1, serie=1)

        # Adiciona remetente
        cte.remetente = Participante(
            tipo="remetente",
            cnpj_cpf="12345678000190",
            nome="Empresa Remetente",
            uf="SP",
        )

        # Adiciona destinatario
        cte.destinatario = Participante(
            tipo="destinatario",
            cnpj_cpf="98765432000110",
            nome="Empresa Destinatario",
            uf="RJ",
        )

        # Configura valores
        cte.valor_total_servico = Decimal("1500.00")
        cte.valor_receber = Decimal("1500.00")
        cte.icms_base_calculo = Decimal("1500.00")
        cte.icms_aliquota = Decimal("12.00")
        cte.icms_valor = Decimal("180.00")

        xml = manager.gerar_xml(cte)

        assert "<?xml version" in xml
        assert "<CTe" in xml
        assert "<infCte" in xml
        assert "4.00" in xml  # Versao

    def test_gerar_xml_com_carga(self, manager):
        """Testa geracao de XML com dados de carga."""
        cte = manager.criar_cte(numero=1, serie=1)

        # Adiciona carga
        cte.carga = Carga(
            valor_total_carga=Decimal("50000.00"),
            produto_predominante="ELETRONICOS",
            peso_bruto=Decimal("1000.00"),
            quantidade_volumes=50,
        )

        xml = manager.gerar_xml(cte)

        assert "<infCarga>" in xml
        assert "ELETRONICOS" in xml

    def test_gerar_xml_com_nf_referenciada(self, manager):
        """Testa geracao de XML com NF-e referenciada."""
        cte = manager.criar_cte(numero=1, serie=1)

        # Adiciona NF referenciada
        cte.nf_referenciadas.append(NFReferenciada(chave="35260100000000000000550010000000011000000011"))

        cte.carga = Carga(
            valor_total_carga=Decimal("50000.00"),
            produto_predominante="ELETRONICOS",
        )

        xml = manager.gerar_xml(cte)

        assert "<infDoc>" in xml
        assert "<infNFe>" in xml

    def test_consultar_status_servico(self, manager):
        """Testa consulta de status do servico."""
        resultado = manager.consultar_status_servico()

        assert "servico" in resultado
        assert "url" in resultado
        assert "status" in resultado


class TestCTeService:
    """Testes para CTeService."""

    @pytest.fixture
    def service(self):
        """Cria instancia do service."""
        with patch.dict(
            "os.environ",
            {
                "CTE_CNPJ": "35710481000103",
                "EMPRESA_RAZAO_SOCIAL": "Transportadora Teste",
                "EMPRESA_IE": "123456789",
                "EMPRESA_UF": "SP",
                "CTE_AMBIENTE": "homologacao",
            },
        ):
            return CTeService()

    def test_service_init(self, service):
        """Testa inicializacao do service."""
        assert service.cnpj == "35710481000103"
        assert service.uf == "SP"
        assert service.ambiente == "homologacao"

    def test_validar_status(self, service):
        """Testa validacao de status."""
        status = service.validar_status()

        assert status["cnpj"] == "35710481000103"
        assert "criar_cte" in status["operacoes_disponiveis"]
        assert "gerar_xml" in status["operacoes_disponiveis"]

    def test_criar_cte(self, service):
        """Testa criacao de CT-e via service."""
        dados = {
            "numero": 1,
            "serie": 1,
            "modal": "01",
            "tipo_servico": "0",
            "tomador": "0",
            "valor_total_servico": "1500.00",
            "valor_receber": "1500.00",
        }

        resultado = service.criar_cte(dados)

        assert resultado["numero"] == 1
        assert resultado["modal"] == "01"
        assert resultado["situacao"] == "em_digitacao"

    def test_criar_cte_com_participantes(self, service):
        """Testa criacao de CT-e com participantes."""
        dados = {
            "numero": 2,
            "serie": 1,
            "modal": "01",
            "remetente": {
                "tipo": "remetente",
                "cnpj_cpf": "12345678000190",
                "nome": "Empresa Remetente",
                "uf": "SP",
            },
            "destinatario": {
                "tipo": "destinatario",
                "cnpj_cpf": "98765432000110",
                "nome": "Empresa Destinatario",
                "uf": "RJ",
            },
            "valor_total_servico": "1500.00",
            "valor_receber": "1500.00",
        }

        resultado = service.criar_cte(dados)

        assert resultado["numero"] == 2

    def test_criar_cte_com_carga(self, service):
        """Testa criacao de CT-e com carga."""
        dados = {
            "numero": 3,
            "serie": 1,
            "modal": "01",
            "carga": {
                "valor_total_carga": "50000.00",
                "produto_predominante": "ELETRONICOS",
                "peso_bruto": "1000.00",
                "quantidade_volumes": 50,
            },
            "valor_total_servico": "1500.00",
            "valor_receber": "1500.00",
        }

        resultado = service.criar_cte(dados)

        assert resultado["numero"] == 3

    def test_gerar_xml(self, service):
        """Testa geracao de XML via service."""
        # Primeiro cria o CT-e
        dados_criar = {
            "numero": 10,
            "serie": 1,
            "modal": "01",
            "valor_total_servico": "1500.00",
            "valor_receber": "1500.00",
        }
        service.criar_cte(dados_criar)

        # Depois gera o XML
        dados_xml = {
            "numero": 10,
            "serie": 1,
            "modal": "01",
        }

        resultado = service.gerar_xml(dados_xml)

        assert resultado["numero"] == 10
        assert "xml" in resultado
        assert "<CTe" in resultado["xml"]

    def test_consultar_status_servico(self, service):
        """Testa consulta de status do servico via service."""
        resultado = service.consultar_status_servico()

        assert "servico" in resultado
        assert resultado["servico"] == "CTeStatusServico"

    def test_listar_modais(self, service):
        """Testa listagem de modais."""
        modais = service.listar_modais()

        assert "modais" in modais
        assert len(modais["modais"]) == 6
        # Verifica se rodoviario esta presente
        codigos = [m["codigo"] for m in modais["modais"]]
        assert "01" in codigos

    def test_listar_tipos_servico(self, service):
        """Testa listagem de tipos de servico."""
        tipos = service.listar_tipos_servico()

        assert "tipos_servico" in tipos
        assert len(tipos["tipos_servico"]) == 5
        # Verifica se normal esta presente
        codigos = [t["codigo"] for t in tipos["tipos_servico"]]
        assert "0" in codigos

    def test_obter_cte(self, service):
        """Testa obtencao de CT-e do cache."""
        # Cria CT-e
        dados = {
            "numero": 20,
            "serie": 1,
            "modal": "01",
            "valor_total_servico": "1500.00",
        }
        service.criar_cte(dados)

        # Obtem CT-e
        cte = service.obter_cte(20, 1)

        assert cte is not None
        assert cte["numero"] == 20

    def test_obter_cte_inexistente(self, service):
        """Testa obtencao de CT-e inexistente."""
        cte = service.obter_cte(999, 1)

        assert cte is None

    def test_listar_ctes(self, service):
        """Testa listagem de CT-e."""
        # Cria alguns CT-e
        for i in range(30, 33):
            service.criar_cte(
                {
                    "numero": i,
                    "serie": 1,
                    "modal": "01",
                    "valor_total_servico": "1500.00",
                }
            )

        ctes = service.listar_ctes()

        assert "ctes" in ctes
        assert len(ctes["ctes"]) >= 3

    def test_limpar_cache(self, service):
        """Testa limpeza de cache."""
        # Cria CT-e
        service.criar_cte(
            {
                "numero": 40,
                "serie": 1,
                "modal": "01",
            }
        )

        # Limpa cache
        resultado = service.limpar_cache()

        assert "message" in resultado

        # Verifica se cache foi limpo
        ctes = service.listar_ctes()
        assert len(ctes["ctes"]) == 0


class TestCTeEndpoints:
    """Testes para endpoints REST."""

    @pytest.fixture
    def client(self):
        """Cliente de teste HTTP."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()

        from modules.government_integrations.controllers.cte_controller import router

        app.include_router(router, prefix="/api/v1/government")

        return TestClient(app)

    def test_get_status(self, client):
        """Testa endpoint de status."""
        response = client.get("/api/v1/government/cte/status")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "operacoes_disponiveis" in data["data"]

    def test_criar_cte_endpoint(self, client):
        """Testa endpoint de criacao de CT-e."""
        payload = {
            "numero": 100,
            "serie": 1,
            "modal": "01",
            "tipo_servico": "0",
            "tomador": "0",
            "valor_total_servico": "1500.00",
            "valor_receber": "1500.00",
        }

        response = client.post("/api/v1/government/cte/criar", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["numero"] == 100

    def test_criar_cte_com_participantes_endpoint(self, client):
        """Testa endpoint de criacao de CT-e com participantes."""
        payload = {
            "numero": 101,
            "serie": 1,
            "modal": "01",
            "remetente": {"tipo": "remetente", "cnpj_cpf": "12345678000190", "nome": "Empresa Remetente"},
            "destinatario": {"tipo": "destinatario", "cnpj_cpf": "98765432000110", "nome": "Empresa Destinatario"},
            "valor_total_servico": "1500.00",
            "valor_receber": "1500.00",
        }

        response = client.post("/api/v1/government/cte/criar", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    def test_gerar_xml_endpoint(self, client):
        """Testa endpoint de geracao de XML."""
        # Primeiro cria o CT-e
        client.post(
            "/api/v1/government/cte/criar",
            json={"numero": 102, "serie": 1, "modal": "01", "valor_total_servico": "1500.00"},
        )

        # Depois gera o XML
        payload = {"numero": 102, "serie": 1, "modal": "01"}

        response = client.post("/api/v1/government/cte/gerar-xml", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "xml" in data["data"]

    def test_consultar_status_servico_endpoint(self, client):
        """Testa endpoint de consulta de status do servico."""
        response = client.get("/api/v1/government/cte/consultar-status-servico")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "servico" in data["data"]

    def test_listar_modais_endpoint(self, client):
        """Testa endpoint de listagem de modais."""
        response = client.get("/api/v1/government/cte/modais")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "modais" in data["data"]
        assert len(data["data"]["modais"]) == 6

    def test_listar_tipos_servico_endpoint(self, client):
        """Testa endpoint de listagem de tipos de servico."""
        response = client.get("/api/v1/government/cte/tipos-servico")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "tipos_servico" in data["data"]
        assert len(data["data"]["tipos_servico"]) == 5

    def test_listar_ctes_endpoint(self, client):
        """Testa endpoint de listagem de CT-e."""
        response = client.get("/api/v1/government/cte/listar")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "ctes" in data["data"]

    def test_obter_cte_endpoint(self, client):
        """Testa endpoint de obtencao de CT-e."""
        # Primeiro cria o CT-e
        client.post("/api/v1/government/cte/criar", json={"numero": 103, "serie": 1, "modal": "01"})

        # Depois obtem
        response = client.get("/api/v1/government/cte/obter/103?serie=1")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["numero"] == 103

    def test_obter_cte_nao_encontrado_endpoint(self, client):
        """Testa endpoint de obtencao de CT-e nao encontrado."""
        response = client.get("/api/v1/government/cte/obter/99999?serie=1")

        assert response.status_code == 404

    def test_limpar_cache_endpoint(self, client):
        """Testa endpoint de limpeza de cache."""
        response = client.delete("/api/v1/government/cte/limpar")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestCTeEnums:
    """Testes para enums do CT-e."""

    def test_modal_transporte_enum(self):
        """Testa enum de modal de transporte."""
        assert ModalTransporteEnum.RODOVIARIO.value == "01"
        assert ModalTransporteEnum.AEREO.value == "02"
        assert ModalTransporteEnum.AQUAVIARIO.value == "03"
        assert ModalTransporteEnum.FERROVIARIO.value == "04"
        assert ModalTransporteEnum.DUTOVIARIO.value == "05"
        assert ModalTransporteEnum.MULTIMODAL.value == "06"

    def test_tipo_servico_enum(self):
        """Testa enum de tipo de servico."""
        assert TipoServicoEnum.NORMAL.value == "0"
        assert TipoServicoEnum.SUBCONTRATACAO.value == "1"
        assert TipoServicoEnum.REDESPACHO.value == "2"
        assert TipoServicoEnum.REDESPACHO_INTERMEDIARIO.value == "3"
        assert TipoServicoEnum.SERVICO_VINCULADO_MULTIMODAL.value == "4"

    def test_tomador_servico_enum(self):
        """Testa enum de tomador de servico."""
        assert TomadorServicoEnum.REMETENTE.value == "0"
        assert TomadorServicoEnum.EXPEDIDOR.value == "1"
        assert TomadorServicoEnum.RECEBEDOR.value == "2"
        assert TomadorServicoEnum.DESTINATARIO.value == "3"
        assert TomadorServicoEnum.OUTROS.value == "4"

    def test_situacao_cte_enum(self):
        """Testa enum de situacao do CT-e."""
        assert SituacaoCTeEnum.EM_DIGITACAO.value == "em_digitacao"
        assert SituacaoCTeEnum.ASSINADO.value == "assinado"
        assert SituacaoCTeEnum.AUTORIZADO.value == "autorizado"
        assert SituacaoCTeEnum.CANCELADO.value == "cancelado"
        assert SituacaoCTeEnum.DENEGADO.value == "denegado"
        assert SituacaoCTeEnum.REJEITADO.value == "rejeitado"
