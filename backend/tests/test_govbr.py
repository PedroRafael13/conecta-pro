"""
Testes para Gov.br - Plataforma de Login Unico do Governo Federal.

Testes unitarios e de integracao para o modulo Gov.br.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest

from modules.government_integrations.core.govbr import (
    GovBrManager,
    NivelAutenticacao,
    TipoDocumento,
    TokenGovBr,
    UsuarioGovBr,
)
from modules.government_integrations.schemas.govbr import (
    AmbienteGovBrEnum,
    GerarUrlAutorizacaoRequest,
    GerarUrlLogoutRequest,
    NivelAutenticacaoEnum,
    ObterDadosUsuarioRequest,
    ObterEmpresasRequest,
    RenovarTokenRequest,
    TipoDocumentoEnum,
    TrocarCodigoRequest,
    ValidarTokenRequest,
)
from modules.government_integrations.services.govbr_service import (
    GovBrService,
)


class TestSchemas:
    """Testes para schemas de validacao."""

    def test_gerar_url_autorizacao_request_valid(self):
        """Testa GerarUrlAutorizacaoRequest valido."""
        request = GerarUrlAutorizacaoRequest(
            scopes=["openid", "email", "profile"], nivel_minimo=NivelAutenticacaoEnum.PRATA
        )
        assert request.scopes == ["openid", "email", "profile"]
        assert request.nivel_minimo == NivelAutenticacaoEnum.PRATA

    def test_gerar_url_autorizacao_request_opcional(self):
        """Testa request sem parametros opcionais."""
        request = GerarUrlAutorizacaoRequest()
        assert request.scopes is None
        assert request.nivel_minimo is None

    def test_gerar_url_autorizacao_request_com_empresa(self):
        """Testa request com scope govbr_empresa."""
        request = GerarUrlAutorizacaoRequest(scopes=["openid", "govbr_empresa"])
        assert "govbr_empresa" in request.scopes

    def test_trocar_codigo_request_valid(self):
        """Testa TrocarCodigoRequest valido."""
        request = TrocarCodigoRequest(
            code="abc123def456", state="random_state_string", code_verifier="pkce_verifier_string"
        )
        assert request.code == "abc123def456"
        assert request.state == "random_state_string"
        assert request.code_verifier == "pkce_verifier_string"

    def test_trocar_codigo_request_sem_verifier(self):
        """Testa request sem code_verifier."""
        request = TrocarCodigoRequest(code="abc123", state="state123")
        assert request.code_verifier is None

    def test_renovar_token_request_valid(self):
        """Testa RenovarTokenRequest valido."""
        request = RenovarTokenRequest(refresh_token="refresh_token_string")
        assert request.refresh_token == "refresh_token_string"

    def test_obter_dados_usuario_request_valid(self):
        """Testa ObterDadosUsuarioRequest valido."""
        request = ObterDadosUsuarioRequest(access_token="access_token_string")
        assert request.access_token == "access_token_string"

    def test_validar_token_request_valid(self):
        """Testa ValidarTokenRequest valido."""
        request = ValidarTokenRequest(
            access_token="access_token_string", token_type="Bearer", expires_in=3600, scope="openid email profile"
        )
        assert request.access_token == "access_token_string"
        assert request.token_type == "Bearer"
        assert request.expires_in == 3600

    def test_validar_token_request_defaults(self):
        """Testa defaults do ValidarTokenRequest."""
        request = ValidarTokenRequest(access_token="token")
        assert request.token_type == "Bearer"
        assert request.expires_in == 0
        assert request.scope is None

    def test_gerar_url_logout_request_valid(self):
        """Testa GerarUrlLogoutRequest valido."""
        request = GerarUrlLogoutRequest(
            id_token="id_token_string", post_logout_redirect_uri="https://app.example.com/logout"
        )
        assert request.id_token == "id_token_string"
        assert request.post_logout_redirect_uri == "https://app.example.com/logout"

    def test_gerar_url_logout_request_sem_redirect(self):
        """Testa request sem redirect_uri."""
        request = GerarUrlLogoutRequest(id_token="id_token")
        assert request.post_logout_redirect_uri is None

    def test_obter_empresas_request_valid(self):
        """Testa ObterEmpresasRequest valido."""
        request = ObterEmpresasRequest(access_token="token", token_type="Bearer", scope="openid govbr_empresa")
        assert request.access_token == "token"
        assert request.scope == "openid govbr_empresa"

    def test_enums_nivel_autenticacao(self):
        """Testa valores dos enums de nivel."""
        assert NivelAutenticacaoEnum.BRONZE.value == "1"
        assert NivelAutenticacaoEnum.PRATA.value == "2"
        assert NivelAutenticacaoEnum.OURO.value == "3"

    def test_enums_tipo_documento(self):
        """Testa valores dos enums de documento."""
        assert TipoDocumentoEnum.CNH.value == "cnh"
        assert TipoDocumentoEnum.RG.value == "rg"
        assert TipoDocumentoEnum.PASSAPORTE.value == "passaporte"

    def test_enums_ambiente(self):
        """Testa valores dos enums de ambiente."""
        assert AmbienteGovBrEnum.PRODUCAO.value == "producao"
        assert AmbienteGovBrEnum.STAGING.value == "staging"


class TestGovBrManager:
    """Testes para GovBrManager."""

    @pytest.fixture
    def manager(self):
        """Cria instancia do manager para testes."""
        return GovBrManager(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="https://app.example.com/callback",
            ambiente="producao",
        )

    @pytest.fixture
    def manager_staging(self):
        """Cria instancia do manager para staging."""
        return GovBrManager(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="https://app.example.com/callback",
            ambiente="staging",
        )

    def test_init_producao(self, manager):
        """Testa inicializacao em producao."""
        assert manager.client_id == "test_client_id"
        assert manager.ambiente == "producao"
        assert manager.base_url == manager.URL_PRODUCAO

    def test_init_staging(self, manager_staging):
        """Testa inicializacao em staging."""
        assert manager_staging.ambiente == "staging"
        assert manager_staging.base_url == manager_staging.URL_STAGING

    def test_gerar_url_autorizacao(self, manager):
        """Testa geracao de URL de autorizacao."""
        resultado = manager.gerar_url_autorizacao()

        assert "url" in resultado
        assert "state" in resultado
        assert "nonce" in resultado
        assert "code_verifier" in resultado
        assert manager.URL_PRODUCAO in resultado["url"]
        assert "client_id=" in resultado["url"]
        assert "response_type=code" in resultado["url"]

    def test_gerar_url_autorizacao_com_scopes(self, manager):
        """Testa URL com scopes personalizados."""
        resultado = manager.gerar_url_autorizacao(scopes=["openid", "email", "govbr_empresa"])

        assert "openid" in resultado["url"]
        assert "email" in resultado["url"]

    def test_gerar_url_autorizacao_com_nivel_minimo(self, manager):
        """Testa URL com nivel minimo."""
        resultado = manager.gerar_url_autorizacao(nivel_minimo=NivelAutenticacao.OURO)

        assert "acr_values=" in resultado["url"]

    def test_gerar_code_verifier(self, manager):
        """Testa geracao de code verifier PKCE."""
        verifier = manager._gerar_code_verifier()

        assert len(verifier) <= 128
        assert len(verifier) >= 43

    def test_gerar_code_challenge(self, manager):
        """Testa geracao de code challenge PKCE."""
        verifier = "test_verifier_string"
        challenge = manager._gerar_code_challenge(verifier)

        assert challenge is not None
        assert len(challenge) > 0

    def test_trocar_codigo_por_token_state_invalido(self, manager):
        """Testa troca com state invalido."""
        # Gera URL para definir state interno
        manager.gerar_url_autorizacao()

        with pytest.raises(ValueError, match="State inv[aá]lido"):
            manager.trocar_codigo_por_token(
                code="test_code",
                state="invalid_state",
            )

    def test_trocar_codigo_por_token_sem_verifier(self, manager):
        """Testa troca sem code verifier."""
        with pytest.raises(ValueError, match="Code verifier"):
            manager.trocar_codigo_por_token(
                code="test_code",
                state="test_state",
            )

    def test_obter_dados_usuario_token_expirado(self, manager):
        """Testa obter dados com token expirado."""
        token = TokenGovBr(
            access_token="expired_token",
            expires_in=0,  # Expira imediatamente
            data_obtencao=datetime.now() - timedelta(hours=1),
        )

        with pytest.raises(ValueError, match="Token expirado"):
            manager.obter_dados_usuario(token)

    def test_validar_token(self, manager):
        """Testa validacao de token."""
        token = TokenGovBr(
            access_token="test_token",
            expires_in=3600,
            scope="openid email",
        )

        resultado = manager.validar_token(token)

        assert "valido" in resultado
        assert "expiracao" in resultado
        assert "scopes" in resultado

    def test_validar_token_expirado(self, manager):
        """Testa validacao de token expirado."""
        token = TokenGovBr(
            access_token="expired_token",
            expires_in=0,
            data_obtencao=datetime.now() - timedelta(hours=1),
        )

        resultado = manager.validar_token(token)

        assert resultado["valido"] is False

    def test_gerar_url_logout(self, manager):
        """Testa geracao de URL de logout."""
        url = manager.gerar_url_logout(
            id_token="test_id_token", post_logout_redirect_uri="https://app.example.com/logout"
        )

        assert manager.ENDPOINT_LOGOUT in url
        assert "id_token_hint=" in url
        assert "post_logout_redirect_uri=" in url

    def test_gerar_url_logout_sem_redirect(self, manager):
        """Testa logout sem redirect URI."""
        url = manager.gerar_url_logout(id_token="test_id_token")

        assert "id_token_hint=" in url
        assert "post_logout_redirect_uri" not in url

    def test_obter_empresas_sem_scope(self, manager):
        """Testa consulta de empresas sem scope adequado."""
        token = TokenGovBr(
            access_token="test_token",
            expires_in=3600,
            scope="openid email",  # Sem govbr_empresa
        )

        with pytest.raises(ValueError, match="govbr_empresa"):
            manager.obter_empresas_vinculadas(token)

    def test_scopes_disponiveis(self, manager):
        """Testa lista de scopes disponiveis."""
        scopes = manager.SCOPES

        assert "openid" in scopes
        assert "email" in scopes
        assert "profile" in scopes
        assert "govbr_empresa" in scopes
        assert "govbr_confiabilidades" in scopes


class TestTokenGovBr:
    """Testes para dataclass TokenGovBr."""

    def test_token_valido(self):
        """Testa token valido."""
        token = TokenGovBr(
            access_token="test_token",
            expires_in=3600,
        )

        assert token.expirado is False
        assert token.token_type == "Bearer"

    def test_token_expirado(self):
        """Testa token expirado."""
        token = TokenGovBr(
            access_token="test_token",
            expires_in=0,
            data_obtencao=datetime.now() - timedelta(hours=1),
        )

        assert token.expirado is True

    def test_token_expiracao(self):
        """Testa calculo de expiracao."""
        token = TokenGovBr(
            access_token="test_token",
            expires_in=3600,
        )

        expected = token.data_obtencao + timedelta(seconds=3600)
        assert abs((token.expiracao - expected).total_seconds()) < 1


class TestUsuarioGovBr:
    """Testes para dataclass UsuarioGovBr."""

    def test_usuario_basico(self):
        """Testa usuario com dados basicos."""
        usuario = UsuarioGovBr(
            cpf="12345678901",
            nome="Teste Usuario",
        )

        assert usuario.cpf == "12345678901"
        assert usuario.nome == "Teste Usuario"
        assert usuario.nivel_autenticacao == NivelAutenticacao.BRONZE

    def test_usuario_completo(self):
        """Testa usuario com dados completos."""
        usuario = UsuarioGovBr(
            cpf="12345678901",
            nome="Teste Usuario",
            email="teste@email.com",
            telefone="11999999999",
            nivel_autenticacao=NivelAutenticacao.OURO,
            data_nascimento="1990-01-01",
            nome_mae="Mae Teste",
            cnpj_vinculados=["12345678000199"],
        )

        assert usuario.email == "teste@email.com"
        assert usuario.nivel_autenticacao == NivelAutenticacao.OURO
        assert len(usuario.cnpj_vinculados) == 1


class TestGovBrService:
    """Testes para GovBrService."""

    @pytest.fixture
    def service(self):
        """Cria instancia do service para testes."""
        with patch.dict(
            "os.environ",
            {
                "GOVBR_CLIENT_ID": "test_client_id",
                "GOVBR_CLIENT_SECRET": "test_client_secret",
                "GOVBR_REDIRECT_URI": "https://app.example.com/callback",
                "GOVBR_AMBIENTE": "staging",
            },
        ):
            return GovBrService()

    def test_service_init(self, service):
        """Testa inicializacao do service."""
        assert service.client_id == "test_client_id"
        assert service.ambiente == "staging"

    def test_gerar_url_autorizacao(self, service):
        """Testa geracao de URL via service."""
        resultado = service.gerar_url_autorizacao()

        assert "url" in resultado
        assert "state" in resultado
        assert "code_verifier" in resultado

    def test_gerar_url_autorizacao_com_scopes(self, service):
        """Testa geracao de URL com scopes."""
        resultado = service.gerar_url_autorizacao(scopes=["openid", "email", "govbr_empresa"])

        assert "url" in resultado

    def test_gerar_url_autorizacao_com_nivel(self, service):
        """Testa geracao de URL com nivel minimo."""
        resultado = service.gerar_url_autorizacao(nivel_minimo="2")

        assert "url" in resultado

    def test_gerar_url_autorizacao_nivel_invalido(self, service):
        """Testa geracao de URL com nivel invalido."""
        # Nao deve lancar erro, apenas ignorar nivel invalido
        resultado = service.gerar_url_autorizacao(nivel_minimo="999")

        assert "url" in resultado

    def test_trocar_codigo_state_armazenado(self, service):
        """Testa troca de codigo com state armazenado."""
        # Primeiro gera URL para armazenar state
        resultado = service.gerar_url_autorizacao()
        state = resultado["state"]

        # Agora troca codigo
        token_result = service.trocar_codigo_por_token(
            code="test_code",
            state=state,
        )

        assert "access_token" in token_result
        assert "data_obtencao" in token_result

    def test_trocar_codigo_state_nao_encontrado(self, service):
        """Testa troca com state nao encontrado."""
        with pytest.raises(ValueError, match="Code verifier nao encontrado"):
            service.trocar_codigo_por_token(
                code="test_code",
                state="invalid_state",
            )

    def test_trocar_codigo_com_verifier(self, service):
        """Testa troca com code_verifier fornecido."""
        token_result = service.trocar_codigo_por_token(
            code="test_code",
            state="test_state",
            code_verifier="test_verifier",
        )

        assert "access_token" in token_result

    def test_obter_dados_usuario(self, service):
        """Testa obtencao de dados do usuario."""
        resultado = service.obter_dados_usuario(
            access_token="test_token",
            expires_in=3600,
        )

        assert "cpf" in resultado
        assert "nome" in resultado
        assert "nivel_autenticacao" in resultado

    def test_renovar_token(self, service):
        """Testa renovacao de token."""
        resultado = service.renovar_token(refresh_token="test_refresh_token")

        assert "access_token" in resultado
        assert "data_obtencao" in resultado

    def test_validar_token(self, service):
        """Testa validacao de token."""
        resultado = service.validar_token(
            access_token="test_token",
            expires_in=3600,
            scope="openid email",
        )

        assert "valido" in resultado
        assert "scopes" in resultado

    def test_gerar_url_logout(self, service):
        """Testa geracao de URL de logout."""
        resultado = service.gerar_url_logout(
            id_token="test_id_token",
            post_logout_redirect_uri="https://app.example.com/logout",
        )

        assert "url" in resultado
        assert resultado["post_logout_redirect_uri"] == "https://app.example.com/logout"

    def test_obter_empresas_vinculadas(self, service):
        """Testa obtencao de empresas vinculadas."""
        resultado = service.obter_empresas_vinculadas(
            access_token="test_token",
            scope="openid govbr_empresa",
        )

        assert "quantidade" in resultado
        assert "empresas" in resultado
        assert "data_consulta" in resultado

    def test_validar_status(self, service):
        """Testa validacao de status."""
        status = service.validar_status()

        assert status["ambiente"] == "staging"
        assert status["client_id_configurado"] is True
        assert "scopes_disponiveis" in status
        assert "servicos" in status

    def test_limpar_autenticacoes_pendentes(self, service):
        """Testa limpeza de autenticacoes pendentes."""
        # Adiciona autenticacao pendente antiga
        service._pending_auth["old_state"] = {
            "code_verifier": "verifier",
            "nonce": "nonce",
            "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
        }

        # Adiciona autenticacao pendente recente
        service._pending_auth["new_state"] = {
            "code_verifier": "verifier",
            "nonce": "nonce",
            "timestamp": datetime.now().isoformat(),
        }

        removidas = service.limpar_autenticacoes_pendentes(max_age_minutes=15)

        assert removidas == 1
        assert "old_state" not in service._pending_auth
        assert "new_state" in service._pending_auth


class TestGovBrEndpoints:
    """Testes para endpoints REST."""

    @pytest.fixture
    def client(self):
        """Cliente de teste HTTP."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        app = FastAPI()

        from modules.government_integrations.controllers.govbr_controller import router

        app.include_router(router, prefix="/api/v1/government")

        return TestClient(app)

    def test_get_status(self, client):
        """Testa endpoint de status."""
        response = client.get("/api/v1/government/govbr/status")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "scopes_disponiveis" in data["data"]
        assert "servicos" in data["data"]

    def test_gerar_url_autorizacao_post(self, client):
        """Testa endpoint POST de autorizacao."""
        payload = {"scopes": ["openid", "email", "profile"]}

        response = client.post("/api/v1/government/govbr/autorizar", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "url" in data["data"]
        assert "state" in data["data"]

    def test_gerar_url_autorizacao_post_com_nivel(self, client):
        """Testa endpoint POST com nivel minimo."""
        payload = {"scopes": ["openid", "email"], "nivel_minimo": "2"}

        response = client.post("/api/v1/government/govbr/autorizar", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_gerar_url_autorizacao_get(self, client):
        """Testa endpoint GET de autorizacao."""
        response = client.get("/api/v1/government/govbr/autorizar", params={"scopes": "openid,email,profile"})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "url" in data["data"]

    def test_gerar_url_autorizacao_get_com_nivel(self, client):
        """Testa endpoint GET com nivel minimo."""
        response = client.get(
            "/api/v1/government/govbr/autorizar", params={"scopes": "openid,email", "nivel_minimo": "3"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_callback_post(self, client):
        """Testa endpoint POST de callback."""
        # Primeiro gera URL para ter state valido
        auth_response = client.get("/api/v1/government/govbr/autorizar")
        auth_data = auth_response.json()["data"]
        state = auth_data["state"]
        code_verifier = auth_data.get("code_verifier", "test_verifier")

        payload = {"code": "test_code", "state": state, "code_verifier": code_verifier}

        response = client.post("/api/v1/government/govbr/callback", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]

    def test_callback_get(self, client):
        """Testa endpoint GET de callback."""
        # Primeiro gera URL para ter state valido
        auth_response = client.get("/api/v1/government/govbr/autorizar")
        state = auth_response.json()["data"]["state"]

        response = client.get("/api/v1/government/govbr/callback", params={"code": "test_code", "state": state})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_renovar_token_endpoint(self, client):
        """Testa endpoint de renovacao de token."""
        payload = {"refresh_token": "test_refresh_token"}

        response = client.post("/api/v1/government/govbr/renovar-token", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]

    def test_obter_usuario_endpoint(self, client):
        """Testa endpoint de dados do usuario."""
        payload = {"access_token": "test_access_token"}

        response = client.post("/api/v1/government/govbr/usuario", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "cpf" in data["data"]
        assert "nome" in data["data"]

    def test_validar_token_endpoint(self, client):
        """Testa endpoint de validacao de token."""
        payload = {"access_token": "test_token", "token_type": "Bearer", "expires_in": 3600, "scope": "openid email"}

        response = client.post("/api/v1/government/govbr/validar-token", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "valido" in data["data"]

    def test_logout_endpoint(self, client):
        """Testa endpoint de logout."""
        payload = {"id_token": "test_id_token", "post_logout_redirect_uri": "https://app.example.com/logout"}

        response = client.post("/api/v1/government/govbr/logout", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "url" in data["data"]

    def test_empresas_endpoint(self, client):
        """Testa endpoint de empresas vinculadas."""
        payload = {"access_token": "test_token", "scope": "openid govbr_empresa"}

        response = client.post("/api/v1/government/govbr/empresas", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "empresas" in data["data"]

    def test_scopes_endpoint(self, client):
        """Testa endpoint de listagem de scopes."""
        response = client.get("/api/v1/government/govbr/scopes")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "scopes" in data["data"]
        assert "openid" in data["data"]["scopes"]

    def test_limpar_pendentes_endpoint(self, client):
        """Testa endpoint de limpeza de pendentes."""
        response = client.post("/api/v1/government/govbr/limpar-pendentes", params={"max_age_minutes": 15})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "removidas" in data["data"]


class TestSingleton:
    """Testes para singleton do service."""

    def test_get_govbr_service_singleton(self):
        """Testa que get_govbr_service retorna singleton."""
        # Reset singleton
        import modules.government_integrations.services.govbr_service as module
        from modules.government_integrations.services.govbr_service import _govbr_service, get_govbr_service

        module._govbr_service = None

        service1 = get_govbr_service()
        service2 = get_govbr_service()

        assert service1 is service2

        # Cleanup
        module._govbr_service = None
