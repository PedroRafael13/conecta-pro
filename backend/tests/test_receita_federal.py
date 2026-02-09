"""
Testes para Receita Federal.

Testes unitarios e de integracao para o modulo Receita Federal.
"""

from datetime import date, datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
from pydantic import ValidationError

from modules.government_integrations.schemas.receita_federal import (
    ConsultaCNPJRequest,
    ConsultaCPFRequest,
    ValidateDocumentRequest,
)
from modules.government_integrations.services.receita_federal_service import (
    ReceitaFederalApiService,
)


class TestSchemas:
    """Testes para schemas de validacao."""

    # Testes para ValidateDocumentRequest

    def test_validate_document_request_cpf_valid(self):
        """Testa ValidateDocumentRequest com CPF valido."""
        request = ValidateDocumentRequest(documento="12345678901", tipo="cpf")
        assert request.documento == "12345678901"
        assert request.tipo == "cpf"

    def test_validate_document_request_cnpj_valid(self):
        """Testa ValidateDocumentRequest com CNPJ valido."""
        request = ValidateDocumentRequest(documento="12345678000199", tipo="cnpj")
        assert request.documento == "12345678000199"
        assert request.tipo == "cnpj"

    def test_validate_document_request_limpa_formatacao_cpf(self):
        """Testa limpeza de formatacao do CPF."""
        request = ValidateDocumentRequest(documento="123.456.789-01", tipo="cpf")
        assert request.documento == "12345678901"

    def test_validate_document_request_limpa_formatacao_cnpj(self):
        """Testa limpeza de formatacao do CNPJ."""
        request = ValidateDocumentRequest(documento="12.345.678/0001-99", tipo="cnpj")
        assert request.documento == "12345678000199"

    def test_validate_document_request_tipo_invalido(self):
        """Testa ValidateDocumentRequest com tipo invalido."""
        with pytest.raises(ValidationError) as exc_info:
            ValidateDocumentRequest(documento="12345678901", tipo="rg")
        assert "tipo" in str(exc_info.value)

    def test_validate_document_request_documento_curto(self):
        """Testa ValidateDocumentRequest com documento muito curto."""
        with pytest.raises(ValidationError) as exc_info:
            ValidateDocumentRequest(documento="1234567890", tipo="cpf")
        assert "documento" in str(exc_info.value).lower()

    def test_validate_document_request_documento_longo(self):
        """Testa ValidateDocumentRequest com documento muito longo."""
        with pytest.raises(ValidationError) as exc_info:
            ValidateDocumentRequest(documento="1234567890123456789", tipo="cnpj")
        assert "documento" in str(exc_info.value).lower()

    # Testes para ConsultaCPFRequest

    def test_consulta_cpf_request_valid(self):
        """Testa ConsultaCPFRequest valido."""
        request = ConsultaCPFRequest(cpf="12345678901", data_nascimento=date(1990, 1, 15))
        assert request.cpf == "12345678901"
        assert request.data_nascimento == date(1990, 1, 15)

    def test_consulta_cpf_request_com_formatacao(self):
        """Testa ConsultaCPFRequest com CPF formatado."""
        request = ConsultaCPFRequest(cpf="123.456.789-01", data_nascimento=date(1985, 6, 20))
        assert request.cpf == "123.456.789-01"
        assert request.data_nascimento == date(1985, 6, 20)

    def test_consulta_cpf_request_cpf_curto(self):
        """Testa ConsultaCPFRequest com CPF muito curto."""
        with pytest.raises(ValidationError) as exc_info:
            ConsultaCPFRequest(cpf="1234567890", data_nascimento=date(1990, 1, 15))
        assert "cpf" in str(exc_info.value).lower()

    def test_consulta_cpf_request_cpf_longo(self):
        """Testa ConsultaCPFRequest com CPF muito longo."""
        with pytest.raises(ValidationError) as exc_info:
            ConsultaCPFRequest(cpf="123456789012345", data_nascimento=date(1990, 1, 15))
        assert "cpf" in str(exc_info.value).lower()

    def test_consulta_cpf_request_data_nascimento_obrigatoria(self):
        """Testa ConsultaCPFRequest sem data de nascimento."""
        with pytest.raises(ValidationError) as exc_info:
            ConsultaCPFRequest(cpf="12345678901")
        assert "data_nascimento" in str(exc_info.value)

    # Testes para ConsultaCNPJRequest

    def test_consulta_cnpj_request_valid(self):
        """Testa ConsultaCNPJRequest valido."""
        request = ConsultaCNPJRequest(cnpj="12345678000199")
        assert request.cnpj == "12345678000199"

    def test_consulta_cnpj_request_com_formatacao(self):
        """Testa ConsultaCNPJRequest com CNPJ formatado."""
        request = ConsultaCNPJRequest(cnpj="12.345.678/0001-99")
        assert request.cnpj == "12.345.678/0001-99"

    def test_consulta_cnpj_request_cnpj_curto(self):
        """Testa ConsultaCNPJRequest com CNPJ muito curto."""
        with pytest.raises(ValidationError) as exc_info:
            ConsultaCNPJRequest(cnpj="1234567800019")
        assert "cnpj" in str(exc_info.value).lower()

    def test_consulta_cnpj_request_cnpj_longo(self):
        """Testa ConsultaCNPJRequest com CNPJ muito longo."""
        with pytest.raises(ValidationError) as exc_info:
            ConsultaCNPJRequest(cnpj="1234567800019901234")
        assert "cnpj" in str(exc_info.value).lower()


class TestReceitaFederalService:
    """Testes para ReceitaFederalApiService."""

    # Testes para validar_documento

    def test_validar_documento_cpf_valido(self):
        """Testa validacao de CPF valido."""
        # CPF valido para teste: 345.598.482-45
        resultado = ReceitaFederalApiService.validar_documento(documento="34559848245", tipo="cpf")

        assert resultado["documento"] == "345.598.482-45"
        assert resultado["tipo"] == "cpf"
        assert resultado["valido"] is True

    def test_validar_documento_cpf_invalido(self):
        """Testa validacao de CPF invalido."""
        resultado = ReceitaFederalApiService.validar_documento(documento="12345678901", tipo="cpf")

        assert resultado["documento"] == "12345678901"
        assert resultado["tipo"] == "cpf"
        assert resultado["valido"] is False

    def test_validar_documento_cpf_todos_digitos_iguais(self):
        """Testa validacao de CPF com todos digitos iguais."""
        resultado = ReceitaFederalApiService.validar_documento(documento="11111111111", tipo="cpf")

        assert resultado["valido"] is False

    def test_validar_documento_cnpj_valido(self):
        """Testa validacao de CNPJ valido."""
        # CNPJ valido para teste: 11.444.777/0001-61
        resultado = ReceitaFederalApiService.validar_documento(documento="11444777000161", tipo="cnpj")

        assert resultado["documento"] == "11.444.777/0001-61"
        assert resultado["tipo"] == "cnpj"
        assert resultado["valido"] is True

    def test_validar_documento_cnpj_invalido(self):
        """Testa validacao de CNPJ invalido."""
        resultado = ReceitaFederalApiService.validar_documento(documento="12345678000199", tipo="cnpj")

        assert resultado["documento"] == "12345678000199"
        assert resultado["tipo"] == "cnpj"
        assert resultado["valido"] is False

    def test_validar_documento_cnpj_todos_digitos_iguais(self):
        """Testa validacao de CNPJ com todos digitos iguais."""
        resultado = ReceitaFederalApiService.validar_documento(documento="11111111111111", tipo="cnpj")

        assert resultado["valido"] is False

    # Testes para consultar_cpf

    def test_consultar_cpf_valido(self):
        """Testa consulta de CPF valido."""
        mock_service = MagicMock()
        mock_service.consultar_cpf.return_value = {
            "situacao": "Regular",
            "nome": "JOAO DA SILVA",
            "data_inscricao": "2000-01-01",
            "digito_verificador": "45",
        }

        with patch(
            "modules.government_integrations.services.receita_federal_service.get_receita_service",
            return_value=mock_service,
        ):
            resultado = ReceitaFederalApiService.consultar_cpf(cpf="34559848245", data_nascimento=date(1990, 1, 15))

            assert resultado["cpf"] == "345.598.482-45"
            assert resultado["situacao"] == "Regular"
            assert resultado["nome"] == "JOAO DA SILVA"

    def test_consultar_cpf_invalido_levanta_erro(self):
        """Testa que consulta de CPF invalido levanta ValueError."""
        with pytest.raises(ValueError) as exc_info:
            ReceitaFederalApiService.consultar_cpf(cpf="12345678901", data_nascimento=date(1990, 1, 15))

        assert "CPF invalido" in str(exc_info.value)

    def test_consultar_cpf_com_formatacao(self):
        """Testa consulta de CPF com formatacao."""
        mock_service = MagicMock()
        mock_service.consultar_cpf.return_value = {
            "situacao": "Regular",
            "nome": "MARIA SANTOS",
            "data_inscricao": "2005-05-10",
            "digito_verificador": "45",
        }

        with patch(
            "modules.government_integrations.services.receita_federal_service.get_receita_service",
            return_value=mock_service,
        ):
            resultado = ReceitaFederalApiService.consultar_cpf(cpf="345.598.482-45", data_nascimento=date(1985, 6, 20))

            assert resultado["cpf"] == "345.598.482-45"
            mock_service.consultar_cpf.assert_called_once()

    def test_consultar_cpf_retorna_campos_esperados(self):
        """Testa que consulta de CPF retorna campos esperados."""
        mock_service = MagicMock()
        mock_service.consultar_cpf.return_value = {
            "situacao": "Pendente de Regularizacao",
            "nome": "PEDRO OLIVEIRA",
            "data_inscricao": "2010-12-01",
            "digito_verificador": "45",
        }

        with patch(
            "modules.government_integrations.services.receita_federal_service.get_receita_service",
            return_value=mock_service,
        ):
            resultado = ReceitaFederalApiService.consultar_cpf(cpf="34559848245", data_nascimento=date(1975, 3, 25))

            assert "cpf" in resultado
            assert "situacao" in resultado
            assert "nome" in resultado
            assert "data_inscricao" in resultado
            assert "digito_verificador" in resultado

    # Testes para consultar_cnpj

    def test_consultar_cnpj_valido(self):
        """Testa consulta de CNPJ valido."""
        mock_service = MagicMock()
        mock_service.consultar_cnpj.return_value = {
            "razao_social": "EMPRESA TESTE LTDA",
            "nome_fantasia": "EMPRESA TESTE",
            "situacao_cadastral": "Ativa",
            "data_situacao": "2020-01-01",
            "cnae_principal": "6201-5/00",
            "endereco": "Rua Teste, 123",
            "porte": "Pequeno Porte",
            "natureza_juridica": "206-2 - Sociedade Empresaria Limitada",
        }

        with patch(
            "modules.government_integrations.services.receita_federal_service.get_receita_service",
            return_value=mock_service,
        ):
            resultado = ReceitaFederalApiService.consultar_cnpj(cnpj="11444777000161")

            assert resultado["cnpj"] == "11.444.777/0001-61"
            assert resultado["razao_social"] == "EMPRESA TESTE LTDA"
            assert resultado["situacao_cadastral"] == "Ativa"

    def test_consultar_cnpj_invalido_levanta_erro(self):
        """Testa que consulta de CNPJ invalido levanta ValueError."""
        with pytest.raises(ValueError) as exc_info:
            ReceitaFederalApiService.consultar_cnpj(cnpj="12345678000199")

        assert "CNPJ invalido" in str(exc_info.value)

    def test_consultar_cnpj_com_formatacao(self):
        """Testa consulta de CNPJ com formatacao."""
        mock_service = MagicMock()
        mock_service.consultar_cnpj.return_value = {
            "razao_social": "EMPRESA ABC S.A.",
            "nome_fantasia": "ABC",
            "situacao_cadastral": "Ativa",
            "data_situacao": "2015-06-15",
            "cnae_principal": "6202-3/00",
            "endereco": "Av. Brasil, 500",
            "porte": "Medio Porte",
            "natureza_juridica": "205-4 - Sociedade Anonima",
        }

        with patch(
            "modules.government_integrations.services.receita_federal_service.get_receita_service",
            return_value=mock_service,
        ):
            resultado = ReceitaFederalApiService.consultar_cnpj(cnpj="11.444.777/0001-61")

            assert resultado["cnpj"] == "11.444.777/0001-61"
            mock_service.consultar_cnpj.assert_called_once()

    def test_consultar_cnpj_retorna_campos_esperados(self):
        """Testa que consulta de CNPJ retorna campos esperados."""
        mock_service = MagicMock()
        mock_service.consultar_cnpj.return_value = {
            "razao_social": "EMPRESA XYZ ME",
            "nome_fantasia": "XYZ",
            "situacao_cadastral": "Baixada",
            "data_situacao": "2023-12-31",
            "cnae_principal": "4711-3/02",
            "endereco": "Praca Central, 10",
            "porte": "Microempresa",
            "natureza_juridica": "213-5 - Empresario Individual",
        }

        with patch(
            "modules.government_integrations.services.receita_federal_service.get_receita_service",
            return_value=mock_service,
        ):
            resultado = ReceitaFederalApiService.consultar_cnpj(cnpj="11444777000161")

            assert "cnpj" in resultado
            assert "razao_social" in resultado
            assert "nome_fantasia" in resultado
            assert "situacao_cadastral" in resultado
            assert "data_situacao" in resultado
            assert "cnae_principal" in resultado
            assert "endereco" in resultado
            assert "porte" in resultado
            assert "natureza_juridica" in resultado


class TestReceitaFederalEndpoints:
    """Testes para endpoints REST."""

    @pytest.fixture
    def client(self):
        """Cliente de teste HTTP."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()

        from modules.government_integrations.controllers.receita_federal_controller import router

        app.include_router(router, prefix="/api/v1/government")

        return TestClient(app)

    # Testes para /validar-documento

    def test_validar_documento_cpf_endpoint(self, client):
        """Testa endpoint de validacao de CPF."""
        payload = {"documento": "34559848245", "tipo": "cpf"}

        response = client.post("/api/v1/government/receita/validar-documento", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "valido" in data["data"]

    def test_validar_documento_cnpj_endpoint(self, client):
        """Testa endpoint de validacao de CNPJ."""
        payload = {"documento": "11444777000161", "tipo": "cnpj"}

        response = client.post("/api/v1/government/receita/validar-documento", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "valido" in data["data"]

    def test_validar_documento_cpf_formatado_endpoint(self, client):
        """Testa endpoint de validacao de CPF formatado."""
        payload = {"documento": "345.598.482-45", "tipo": "cpf"}

        response = client.post("/api/v1/government/receita/validar-documento", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_validar_documento_cnpj_formatado_endpoint(self, client):
        """Testa endpoint de validacao de CNPJ formatado."""
        payload = {"documento": "11.444.777/0001-61", "tipo": "cnpj"}

        response = client.post("/api/v1/government/receita/validar-documento", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_validar_documento_tipo_invalido_endpoint(self, client):
        """Testa endpoint com tipo invalido."""
        payload = {"documento": "12345678901", "tipo": "rg"}

        response = client.post("/api/v1/government/receita/validar-documento", json=payload)

        assert response.status_code == 422

    def test_validar_documento_resposta_cpf_valido(self, client):
        """Testa mensagem de resposta para CPF valido."""
        payload = {"documento": "34559848245", "tipo": "cpf"}

        response = client.post("/api/v1/government/receita/validar-documento", json=payload)

        data = response.json()
        assert data["data"]["valido"] is True
        assert "CPF" in data["message"]
        assert "valido" in data["message"]

    def test_validar_documento_resposta_cpf_invalido(self, client):
        """Testa mensagem de resposta para CPF invalido."""
        payload = {"documento": "12345678901", "tipo": "cpf"}

        response = client.post("/api/v1/government/receita/validar-documento", json=payload)

        data = response.json()
        assert data["data"]["valido"] is False
        assert "CPF" in data["message"]
        assert "invalido" in data["message"]

    # Testes para /consultar-cpf

    def test_consultar_cpf_endpoint(self, client):
        """Testa endpoint de consulta de CPF."""
        mock_service = MagicMock()
        mock_service.consultar_cpf.return_value = {
            "situacao": "Regular",
            "nome": "JOAO DA SILVA",
            "data_inscricao": "2000-01-01",
            "digito_verificador": "45",
        }

        with patch(
            "modules.government_integrations.services.receita_federal_service.get_receita_service",
            return_value=mock_service,
        ):
            payload = {"cpf": "34559848245", "data_nascimento": "1990-01-15"}

            response = client.post("/api/v1/government/receita/consultar-cpf", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Consulta realizada com sucesso"
            assert "cpf" in data["data"]

    def test_consultar_cpf_formatado_endpoint(self, client):
        """Testa endpoint de consulta de CPF formatado."""
        mock_service = MagicMock()
        mock_service.consultar_cpf.return_value = {
            "situacao": "Regular",
            "nome": "MARIA SANTOS",
            "data_inscricao": "2005-05-10",
            "digito_verificador": "45",
        }

        with patch(
            "modules.government_integrations.services.receita_federal_service.get_receita_service",
            return_value=mock_service,
        ):
            payload = {"cpf": "345.598.482-45", "data_nascimento": "1985-06-20"}

            response = client.post("/api/v1/government/receita/consultar-cpf", json=payload)

            assert response.status_code == 200

    def test_consultar_cpf_invalido_endpoint(self, client):
        """Testa endpoint com CPF invalido."""
        payload = {"cpf": "12345678901", "data_nascimento": "1990-01-15"}

        response = client.post("/api/v1/government/receita/consultar-cpf", json=payload)

        assert response.status_code == 400
        data = response.json()
        assert "CPF invalido" in data["detail"]

    def test_consultar_cpf_sem_data_nascimento_endpoint(self, client):
        """Testa endpoint sem data de nascimento."""
        payload = {"cpf": "34559848245"}

        response = client.post("/api/v1/government/receita/consultar-cpf", json=payload)

        assert response.status_code == 422

    def test_consultar_cpf_data_nascimento_formato_invalido(self, client):
        """Testa endpoint com formato de data invalido."""
        payload = {"cpf": "34559848245", "data_nascimento": "15/01/1990"}

        response = client.post("/api/v1/government/receita/consultar-cpf", json=payload)

        assert response.status_code == 422

    # Testes para /consultar-cnpj

    def test_consultar_cnpj_endpoint(self, client):
        """Testa endpoint de consulta de CNPJ."""
        mock_service = MagicMock()
        mock_service.consultar_cnpj.return_value = {
            "razao_social": "EMPRESA TESTE LTDA",
            "nome_fantasia": "EMPRESA TESTE",
            "situacao_cadastral": "Ativa",
            "data_situacao": "2020-01-01",
            "cnae_principal": "6201-5/00",
            "endereco": "Rua Teste, 123",
            "porte": "Pequeno Porte",
            "natureza_juridica": "206-2 - Sociedade Empresaria Limitada",
        }

        with patch(
            "modules.government_integrations.services.receita_federal_service.get_receita_service",
            return_value=mock_service,
        ):
            payload = {"cnpj": "11444777000161"}

            response = client.post("/api/v1/government/receita/consultar-cnpj", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Consulta realizada com sucesso"
            assert "cnpj" in data["data"]
            assert "razao_social" in data["data"]

    def test_consultar_cnpj_formatado_endpoint(self, client):
        """Testa endpoint de consulta de CNPJ formatado."""
        mock_service = MagicMock()
        mock_service.consultar_cnpj.return_value = {
            "razao_social": "EMPRESA ABC S.A.",
            "nome_fantasia": "ABC",
            "situacao_cadastral": "Ativa",
            "data_situacao": "2015-06-15",
            "cnae_principal": "6202-3/00",
            "endereco": "Av. Brasil, 500",
            "porte": "Medio Porte",
            "natureza_juridica": "205-4 - Sociedade Anonima",
        }

        with patch(
            "modules.government_integrations.services.receita_federal_service.get_receita_service",
            return_value=mock_service,
        ):
            payload = {"cnpj": "11.444.777/0001-61"}

            response = client.post("/api/v1/government/receita/consultar-cnpj", json=payload)

            assert response.status_code == 200

    def test_consultar_cnpj_invalido_endpoint(self, client):
        """Testa endpoint com CNPJ invalido."""
        payload = {"cnpj": "12345678000199"}

        response = client.post("/api/v1/government/receita/consultar-cnpj", json=payload)

        assert response.status_code == 400
        data = response.json()
        assert "CNPJ invalido" in data["detail"]

    def test_consultar_cnpj_retorna_campos_completos(self, client):
        """Testa que endpoint retorna todos os campos do CNPJ."""
        mock_service = MagicMock()
        mock_service.consultar_cnpj.return_value = {
            "razao_social": "EMPRESA COMPLETA LTDA",
            "nome_fantasia": "COMPLETA",
            "situacao_cadastral": "Ativa",
            "data_situacao": "2018-03-20",
            "cnae_principal": "4711-3/02",
            "endereco": "Rua Principal, 500",
            "porte": "Microempresa",
            "natureza_juridica": "213-5 - Empresario Individual",
        }

        with patch(
            "modules.government_integrations.services.receita_federal_service.get_receita_service",
            return_value=mock_service,
        ):
            payload = {"cnpj": "11444777000161"}

            response = client.post("/api/v1/government/receita/consultar-cnpj", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert "razao_social" in data["data"]
            assert "nome_fantasia" in data["data"]
            assert "situacao_cadastral" in data["data"]
            assert "data_situacao" in data["data"]
            assert "cnae_principal" in data["data"]
            assert "endereco" in data["data"]
            assert "porte" in data["data"]
            assert "natureza_juridica" in data["data"]


class TestValidacaoDocumentos:
    """Testes adicionais para validacao de documentos."""

    def test_cpf_valido_conhecido(self):
        """Testa CPF valido conhecido."""
        # CPFs validos para teste (gerados com algoritmo correto)
        cpfs_validos = [
            "34559848245",
            "74375809504",
            "98248030027",
        ]

        for cpf in cpfs_validos:
            resultado = ReceitaFederalApiService.validar_documento(cpf, "cpf")
            assert resultado["valido"] is True, f"CPF {cpf} deveria ser valido"

    def test_cpf_invalido_conhecido(self):
        """Testa CPF invalido conhecido."""
        cpfs_invalidos = [
            "12345678901",
            "00000000000",
            "99999999999",
            "11111111111",
        ]

        for cpf in cpfs_invalidos:
            resultado = ReceitaFederalApiService.validar_documento(cpf, "cpf")
            assert resultado["valido"] is False, f"CPF {cpf} deveria ser invalido"

    def test_cnpj_valido_conhecido(self):
        """Testa CNPJ valido conhecido."""
        # CNPJs validos para teste
        cnpjs_validos = [
            "11444777000161",
            "11222333000181",
        ]

        for cnpj in cnpjs_validos:
            resultado = ReceitaFederalApiService.validar_documento(cnpj, "cnpj")
            assert resultado["valido"] is True, f"CNPJ {cnpj} deveria ser valido"

    def test_cnpj_invalido_conhecido(self):
        """Testa CNPJ invalido conhecido."""
        cnpjs_invalidos = [
            "12345678000199",
            "00000000000000",
            "11111111111111",
            "99999999999999",
        ]

        for cnpj in cnpjs_invalidos:
            resultado = ReceitaFederalApiService.validar_documento(cnpj, "cnpj")
            assert resultado["valido"] is False, f"CNPJ {cnpj} deveria ser invalido"


class TestFormatacao:
    """Testes para formatacao de documentos."""

    def test_cpf_formatado_na_resposta(self):
        """Testa que CPF valido e formatado na resposta."""
        resultado = ReceitaFederalApiService.validar_documento("34559848245", "cpf")
        assert resultado["documento"] == "345.598.482-45"

    def test_cnpj_formatado_na_resposta(self):
        """Testa que CNPJ valido e formatado na resposta."""
        resultado = ReceitaFederalApiService.validar_documento("11444777000161", "cnpj")
        assert resultado["documento"] == "11.444.777/0001-61"

    def test_cpf_invalido_nao_formatado(self):
        """Testa que CPF invalido nao e formatado."""
        resultado = ReceitaFederalApiService.validar_documento("12345678901", "cpf")
        assert resultado["documento"] == "12345678901"

    def test_cnpj_invalido_nao_formatado(self):
        """Testa que CNPJ invalido nao e formatado."""
        resultado = ReceitaFederalApiService.validar_documento("12345678000199", "cnpj")
        assert resultado["documento"] == "12345678000199"


class TestErrosInternos:
    """Testes para tratamento de erros internos."""

    @pytest.fixture
    def client(self):
        """Cliente de teste HTTP."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()

        from modules.government_integrations.controllers.receita_federal_controller import router

        app.include_router(router, prefix="/api/v1/government")

        return TestClient(app)

    def test_erro_interno_consulta_cpf(self, client):
        """Testa erro interno na consulta de CPF."""
        mock_service = MagicMock()
        mock_service.consultar_cpf.side_effect = Exception("Erro de conexao")

        with patch(
            "modules.government_integrations.services.receita_federal_service.get_receita_service",
            return_value=mock_service,
        ):
            payload = {"cpf": "34559848245", "data_nascimento": "1990-01-15"}

            response = client.post("/api/v1/government/receita/consultar-cpf", json=payload)

            assert response.status_code == 500
            data = response.json()
            assert "Erro interno" in data["detail"]

    def test_erro_interno_consulta_cnpj(self, client):
        """Testa erro interno na consulta de CNPJ."""
        mock_service = MagicMock()
        mock_service.consultar_cnpj.side_effect = Exception("Timeout")

        with patch(
            "modules.government_integrations.services.receita_federal_service.get_receita_service",
            return_value=mock_service,
        ):
            payload = {"cnpj": "11444777000161"}

            response = client.post("/api/v1/government/receita/consultar-cnpj", json=payload)

            assert response.status_code == 500
            data = response.json()
            assert "Erro interno" in data["detail"]
