"""
Testes para MDF-e (Manifesto Eletronico de Documentos Fiscais).

Testes unitarios e de integracao para MDF-e.
"""

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch

from modules.government_integrations.schemas.mdfe import (
    CondutorRequest,
    VeiculoRequest,
    ReboqueRequest,
    DocumentoVinculadoRequest,
    MunicipioRequest,
    CriarMDFeRequest,
    GerarXMLRequest,
    EncerrarMDFeRequest,
    IncluirCondutorRequest,
    ModalTransporteEnum,
    TipoEmitenteEnum,
    TipoCarroceriaEnum,
    TipoRodadoEnum,
    SituacaoMDFeEnum,
)
from modules.government_integrations.services.mdfe_service import (
    MDFeService,
)
from modules.government_integrations.core.mdfe import (
    MDFeManager,
    MDFe,
    Condutor,
    Veiculo,
    Reboque,
    DocumentoVinculado,
    Municipio,
    Percurso,
    ModalTransporteMDFe,
    TipoEmitente,
    TipoCarroceria,
    TipoRodado,
    SituacaoMDFe,
)


class TestSchemas:
    """Testes para schemas de validacao."""

    def test_condutor_request_valid(self):
        """Testa request de condutor valido."""
        request = CondutorRequest(
            cpf="12345678901",
            nome="Joao Silva",
        )
        assert request.cpf == "12345678901"
        assert request.nome == "Joao Silva"

    def test_veiculo_request_valid(self):
        """Testa request de veiculo valido."""
        request = VeiculoRequest(
            placa="ABC1234",
            uf="AM",
            tara=Decimal("8000"),
            capacidade_kg=Decimal("30000"),
        )
        assert request.placa == "ABC1234"
        assert request.tipo_rodado == TipoRodadoEnum.TRUCK

    def test_reboque_request_valid(self):
        """Testa request de reboque valido."""
        request = ReboqueRequest(
            placa="XYZ9876",
            uf="AM",
            tara=Decimal("5000"),
        )
        assert request.placa == "XYZ9876"
        assert request.tipo_carroceria == TipoCarroceriaEnum.FECHADA_BAU

    def test_documento_vinculado_request_valid(self):
        """Testa request de documento vinculado valido."""
        request = DocumentoVinculadoRequest(
            tipo="NFe",
            chave="35260100000000000000550010000000011000000011",
        )
        assert request.tipo == "NFe"
        assert len(request.chave) == 44

    def test_municipio_request_valid(self):
        """Testa request de municipio valido."""
        request = MunicipioRequest(
            codigo_ibge="1302603",
            nome="MANAUS",
        )
        assert request.codigo_ibge == "1302603"

    def test_criar_mdfe_request_valid(self):
        """Testa request de criacao de MDF-e valido."""
        request = CriarMDFeRequest(
            numero=1,
            serie=1,
            uf_inicio="AM",
            uf_fim="SP",
            valor_total_carga=Decimal("50000.00"),
            peso_bruto_total=Decimal("15000.0000"),
        )
        assert request.numero == 1
        assert request.modal == ModalTransporteEnum.RODOVIARIO

    def test_encerrar_mdfe_request_valid(self):
        """Testa request de encerramento valido."""
        request = EncerrarMDFeRequest(
            chave="35260100000000000000580010000000011000000011",
            protocolo_autorizacao="135260000000001",
            uf_encerramento="SP",
            codigo_municipio="3550308",
        )
        assert len(request.chave) == 44

    def test_incluir_condutor_request_valid(self):
        """Testa request de inclusao de condutor valido."""
        request = IncluirCondutorRequest(
            chave="35260100000000000000580010000000011000000011",
            condutor=CondutorRequest(
                cpf="12345678901",
                nome="Joao Silva",
            )
        )
        assert request.condutor.cpf == "12345678901"


class TestMDFeManager:
    """Testes para MDFeManager."""

    @pytest.fixture
    def manager(self):
        """Cria instancia do manager."""
        return MDFeManager(
            cnpj="35710481000103",
            razao_social="Transportadora Teste",
            inscricao_estadual="123456789",
            uf="AM",
            ambiente="homologacao",
        )

    def test_init(self, manager):
        """Testa inicializacao."""
        assert manager.cnpj == "35710481000103"
        assert manager.uf == "AM"
        assert manager.ambiente == "homologacao"

    def test_criar_mdfe(self, manager):
        """Testa criacao de MDF-e."""
        mdfe = manager.criar_mdfe(
            numero=1,
            serie=1,
            modal=ModalTransporteMDFe.RODOVIARIO,
        )

        assert mdfe.numero == 1
        assert mdfe.serie == 1
        assert mdfe.modal == ModalTransporteMDFe.RODOVIARIO
        assert mdfe.situacao == SituacaoMDFe.EM_DIGITACAO

    def test_gerar_xml(self, manager):
        """Testa geracao de XML."""
        mdfe = manager.criar_mdfe(numero=1, serie=1)
        mdfe.uf_fim = "SP"

        # Adiciona veiculo
        mdfe.veiculo_tracao = Veiculo(
            placa="ABC1234",
            uf="AM",
            tara=Decimal("8000"),
            capacidade_kg=Decimal("30000"),
            capacidade_m3=Decimal("60"),
        )

        # Adiciona condutor
        mdfe.condutores.append(Condutor(cpf="12345678901", nome="Joao Silva"))

        # Adiciona municipio de descarregamento
        mdfe.municipios_descarregamento.append(
            Municipio(
                codigo_ibge="3550308",
                nome="SAO PAULO",
                documentos=[
                    DocumentoVinculado(
                        tipo="NFe",
                        chave="35260100000000000000550010000000011000000011",
                    )
                ],
            )
        )
        mdfe.quantidade_nfe = 1
        mdfe.valor_total_carga = Decimal("50000.00")
        mdfe.peso_bruto_total = Decimal("15000.0000")

        xml = manager.gerar_xml(mdfe)

        assert "<?xml version" in xml
        assert "<MDFe" in xml
        assert "<infMDFe" in xml
        assert "ABC1234" in xml

    def test_encerrar(self, manager):
        """Testa encerramento de MDF-e."""
        mdfe = manager.criar_mdfe(numero=1, serie=1)
        mdfe.chave = "35260100000000000000580010000000011000000011"
        mdfe.protocolo_autorizacao = "135260000000001"

        resultado = manager.encerrar(mdfe)

        assert resultado["evento"]["tipo_evento"] == "110112"
        assert resultado["evento"]["chave_mdfe"] == mdfe.chave
        assert resultado["status"] == "pendente"

    def test_encerrar_sem_chave(self, manager):
        """Testa encerramento sem chave."""
        mdfe = manager.criar_mdfe(numero=1, serie=1)

        with pytest.raises(ValueError, match="n[aã]o possui chave"):
            manager.encerrar(mdfe)

    def test_incluir_condutor(self, manager):
        """Testa inclusao de condutor."""
        mdfe = manager.criar_mdfe(numero=1, serie=1)
        mdfe.chave = "35260100000000000000580010000000011000000011"

        condutor = Condutor(cpf="12345678901", nome="Joao Silva")
        resultado = manager.incluir_condutor(mdfe, condutor)

        assert resultado["evento"]["tipo_evento"] == "110114"
        assert resultado["evento"]["condutor_cpf"] == "12345678901"

    def test_incluir_condutor_sem_chave(self, manager):
        """Testa inclusao de condutor sem chave."""
        mdfe = manager.criar_mdfe(numero=1, serie=1)
        condutor = Condutor(cpf="12345678901", nome="Joao Silva")

        with pytest.raises(ValueError, match="n[aã]o possui chave"):
            manager.incluir_condutor(mdfe, condutor)

    def test_consultar_status_servico(self, manager):
        """Testa consulta de status do servico."""
        resultado = manager.consultar_status_servico()

        assert resultado["servico"] == "MDFeStatusServico"
        assert "url" in resultado
        assert resultado["status"] == "pendente"

    def test_consultar_nao_encerrados(self, manager):
        """Testa consulta de MDF-e nao encerrados."""
        resultado = manager.consultar_nao_encerrados()

        assert isinstance(resultado, list)


class TestMDFeService:
    """Testes para MDFeService."""

    @pytest.fixture
    def service(self):
        """Cria instancia do service."""
        with patch.dict('os.environ', {
            'MDFE_CNPJ': '35710481000103',
            'EMPRESA_RAZAO_SOCIAL': 'Transportadora Teste',
            'EMPRESA_IE': '123456789',
            'EMPRESA_UF': 'AM',
            'MDFE_AMBIENTE': 'homologacao',
        }):
            return MDFeService()

    def test_service_init(self, service):
        """Testa inicializacao do service."""
        assert service.cnpj == "35710481000103"
        assert service.uf == "AM"
        assert service.ambiente == "homologacao"

    def test_validar_status(self, service):
        """Testa validacao de status."""
        status = service.validar_status()

        assert status["cnpj"] == "35710481000103"
        assert "criar" in status["operacoes_disponiveis"]

    def test_criar_mdfe(self, service):
        """Testa criacao de MDF-e via service."""
        dados = {
            "numero": 1,
            "serie": 1,
            "modal": "1",
            "tipo_emitente": "1",
            "uf_inicio": "AM",
            "uf_fim": "SP",
            "valor_total_carga": "50000.00",
            "peso_bruto_total": "15000.0000",
        }

        resultado = service.criar_mdfe(dados)

        assert resultado["numero"] == 1
        assert resultado["uf_inicio"] == "AM"
        assert resultado["situacao"] == "em_digitacao"

    def test_criar_mdfe_com_veiculo(self, service):
        """Testa criacao de MDF-e com veiculo."""
        dados = {
            "numero": 2,
            "serie": 1,
            "modal": "1",
            "uf_inicio": "AM",
            "uf_fim": "SP",
            "veiculo_tracao": {
                "placa": "ABC1234",
                "uf": "AM",
                "tara": "8000",
                "capacidade_kg": "30000",
                "tipo_rodado": "03",
                "tipo_carroceria": "02",
            },
            "condutores": [
                {"cpf": "12345678901", "nome": "Joao Silva"}
            ],
        }

        resultado = service.criar_mdfe(dados)

        assert resultado["numero"] == 2

    def test_criar_mdfe_com_documentos(self, service):
        """Testa criacao de MDF-e com documentos."""
        dados = {
            "numero": 3,
            "serie": 1,
            "modal": "1",
            "uf_inicio": "AM",
            "uf_fim": "SP",
            "municipios_descarregamento": [
                {
                    "codigo_ibge": "3550308",
                    "nome": "SAO PAULO",
                    "documentos": [
                        {
                            "tipo": "NFe",
                            "chave": "35260100000000000000550010000000011000000011",
                        }
                    ],
                }
            ],
        }

        resultado = service.criar_mdfe(dados)

        assert resultado["numero"] == 3
        assert resultado["quantidade_nfe"] == 1

    def test_gerar_xml(self, service):
        """Testa geracao de XML via service."""
        # Cria MDF-e primeiro
        dados = {
            "numero": 10,
            "serie": 1,
            "modal": "1",
            "uf_inicio": "AM",
            "uf_fim": "SP",
        }
        criado = service.criar_mdfe(dados)

        # Gera XML
        resultado = service.gerar_xml(criado["mdfe_id"])

        assert resultado["numero"] == 10
        assert "<MDFe" in resultado["xml"]
        assert "hash_md5" in resultado

    def test_gerar_xml_nao_encontrado(self, service):
        """Testa geracao de XML para MDF-e inexistente."""
        with pytest.raises(ValueError, match="nao encontrado"):
            service.gerar_xml("mdfe_inexistente")

    def test_encerrar_mdfe(self, service):
        """Testa encerramento de MDF-e via service."""
        dados = {
            "chave": "35260100000000000000580010000000011000000011",
            "protocolo_autorizacao": "135260000000001",
            "uf_encerramento": "SP",
            "codigo_municipio": "3550308",
        }

        resultado = service.encerrar_mdfe(dados)

        assert resultado["tipo_evento"] == "110112"
        assert resultado["status"] == "pendente"

    def test_incluir_condutor(self, service):
        """Testa inclusao de condutor via service."""
        dados = {
            "chave": "35260100000000000000580010000000011000000011",
            "condutor": {
                "cpf": "12345678901",
                "nome": "Joao Silva",
            },
        }

        resultado = service.incluir_condutor(dados)

        assert resultado["tipo_evento"] == "110114"
        assert resultado["condutor_cpf"] == "12345678901"

    def test_consultar_status_servico(self, service):
        """Testa consulta de status do servico via service."""
        resultado = service.consultar_status_servico()

        assert resultado["servico"] == "MDFeStatusServico"
        assert resultado["ambiente"] == "homologacao"

    def test_consultar_nao_encerrados(self, service):
        """Testa consulta de nao encerrados via service."""
        resultado = service.consultar_nao_encerrados()

        assert "quantidade" in resultado
        assert "mdfes" in resultado

    def test_listar_modais(self, service):
        """Testa listagem de modais."""
        resultado = service.listar_modais()

        assert "modais" in resultado
        assert len(resultado["modais"]) == 4

    def test_listar_tipos_emitente(self, service):
        """Testa listagem de tipos de emitente."""
        resultado = service.listar_tipos_emitente()

        assert "tipos_emitente" in resultado
        assert len(resultado["tipos_emitente"]) == 3

    def test_listar_tipos_carroceria(self, service):
        """Testa listagem de tipos de carroceria."""
        resultado = service.listar_tipos_carroceria()

        assert "tipos_carroceria" in resultado
        assert len(resultado["tipos_carroceria"]) == 6

    def test_buscar_mdfe(self, service):
        """Testa busca de MDF-e."""
        # Cria MDF-e
        dados = {"numero": 20, "serie": 1, "modal": "1", "uf_inicio": "AM", "uf_fim": "SP"}
        criado = service.criar_mdfe(dados)

        # Busca
        resultado = service.buscar_mdfe(criado["mdfe_id"])

        assert resultado["numero"] == 20

    def test_buscar_mdfe_nao_encontrado(self, service):
        """Testa busca de MDF-e inexistente."""
        resultado = service.buscar_mdfe("mdfe_inexistente")

        assert resultado is None

    def test_listar_mdfes(self, service):
        """Testa listagem de MDF-e."""
        # Cria alguns MDF-e
        service.criar_mdfe({"numero": 30, "serie": 1, "modal": "1", "uf_inicio": "AM", "uf_fim": "SP"})
        service.criar_mdfe({"numero": 31, "serie": 1, "modal": "1", "uf_inicio": "AM", "uf_fim": "RJ"})

        resultado = service.listar_mdfes()

        assert resultado["quantidade"] >= 2

    def test_limpar_dados(self, service):
        """Testa limpeza de dados."""
        # Cria MDF-e
        service.criar_mdfe({"numero": 40, "serie": 1, "modal": "1", "uf_inicio": "AM", "uf_fim": "SP"})

        # Limpa
        resultado = service.limpar_dados()

        assert "Dados limpos" in resultado["message"]
        assert service.listar_mdfes()["quantidade"] == 0


class TestMDFeEndpoints:
    """Testes para endpoints REST."""

    @pytest.fixture
    def client(self):
        """Cliente de teste HTTP."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI

        app = FastAPI()

        from modules.government_integrations.controllers.mdfe_controller import router
        app.include_router(router, prefix="/api/v1/government")

        return TestClient(app)

    def test_get_status(self, client):
        """Testa endpoint de status."""
        response = client.get("/api/v1/government/mdfe/status")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_listar_modais_endpoint(self, client):
        """Testa endpoint de modais."""
        response = client.get("/api/v1/government/mdfe/modais")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "modais" in data["data"]

    def test_listar_tipos_emitente_endpoint(self, client):
        """Testa endpoint de tipos de emitente."""
        response = client.get("/api/v1/government/mdfe/tipos-emitente")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "tipos_emitente" in data["data"]

    def test_listar_tipos_carroceria_endpoint(self, client):
        """Testa endpoint de tipos de carroceria."""
        response = client.get("/api/v1/government/mdfe/tipos-carroceria")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "tipos_carroceria" in data["data"]

    def test_criar_mdfe_endpoint(self, client):
        """Testa endpoint de criacao de MDF-e."""
        payload = {
            "numero": 100,
            "serie": 1,
            "modal": "1",
            "tipo_emitente": "1",
            "uf_inicio": "AM",
            "uf_fim": "SP",
            "valor_total_carga": "50000.00",
            "peso_bruto_total": "15000.0000",
        }

        response = client.post(
            "/api/v1/government/mdfe/criar",
            json=payload
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["numero"] == 100

    def test_criar_mdfe_com_veiculo_endpoint(self, client):
        """Testa endpoint de criacao de MDF-e com veiculo."""
        payload = {
            "numero": 101,
            "serie": 1,
            "modal": "1",
            "tipo_emitente": "1",
            "uf_inicio": "AM",
            "uf_fim": "SP",
            "veiculo_tracao": {
                "placa": "ABC1234",
                "uf": "AM",
                "tara": "8000",
                "capacidade_kg": "30000",
                "tipo_rodado": "03",
                "tipo_carroceria": "02",
            },
            "condutores": [
                {"cpf": "12345678901", "nome": "Joao Silva"}
            ],
        }

        response = client.post(
            "/api/v1/government/mdfe/criar",
            json=payload
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    def test_gerar_xml_endpoint(self, client):
        """Testa endpoint de geracao de XML."""
        # Cria MDF-e primeiro
        payload_criar = {
            "numero": 102,
            "serie": 1,
            "modal": "1",
            "uf_inicio": "AM",
            "uf_fim": "SP",
        }
        response_criar = client.post("/api/v1/government/mdfe/criar", json=payload_criar)
        mdfe_id = response_criar.json()["data"]["mdfe_id"]

        # Gera XML
        payload_xml = {"mdfe_id": mdfe_id}
        response = client.post("/api/v1/government/mdfe/gerar-xml", json=payload_xml)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "xml" in data["data"]

    def test_gerar_xml_nao_encontrado_endpoint(self, client):
        """Testa endpoint de XML para MDF-e inexistente."""
        payload = {"mdfe_id": "mdfe_inexistente"}
        response = client.post("/api/v1/government/mdfe/gerar-xml", json=payload)

        assert response.status_code == 404

    def test_encerrar_mdfe_endpoint(self, client):
        """Testa endpoint de encerramento."""
        payload = {
            "chave": "35260100000000000000580010000000011000000011",
            "protocolo_autorizacao": "135260000000001",
            "uf_encerramento": "SP",
            "codigo_municipio": "3550308",
        }

        response = client.post(
            "/api/v1/government/mdfe/encerrar",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["tipo_evento"] == "110112"

    def test_incluir_condutor_endpoint(self, client):
        """Testa endpoint de inclusao de condutor."""
        payload = {
            "chave": "35260100000000000000580010000000011000000011",
            "condutor": {
                "cpf": "12345678901",
                "nome": "Joao Silva"
            }
        }

        response = client.post(
            "/api/v1/government/mdfe/incluir-condutor",
            json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["tipo_evento"] == "110114"

    def test_consultar_status_servico_endpoint(self, client):
        """Testa endpoint de status do servico."""
        response = client.get("/api/v1/government/mdfe/consultar-status-servico")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_nao_encerrados_endpoint(self, client):
        """Testa endpoint de nao encerrados."""
        response = client.get("/api/v1/government/mdfe/nao-encerrados")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "mdfes" in data["data"]

    def test_listar_mdfes_endpoint(self, client):
        """Testa endpoint de listagem."""
        response = client.get("/api/v1/government/mdfe/listar")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_buscar_mdfe_nao_encontrado_endpoint(self, client):
        """Testa endpoint de busca para MDF-e inexistente."""
        response = client.get("/api/v1/government/mdfe/mdfe_inexistente")

        assert response.status_code == 404

    def test_limpar_dados_endpoint(self, client):
        """Testa endpoint de limpeza."""
        response = client.delete("/api/v1/government/mdfe/limpar")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
