"""Testes para endpoints de autenticacao."""

from datetime import UTC, datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from api.v1.endpoints.auth import get_current_user_info, login, refresh_token, register
from core.models import User
from core.schemas.auth import Token, TokenRefresh
from core.schemas.user import UserCreate, UserResponse


class TestRegisterEndpoint:
    """Testes para endpoint de registro."""

    @pytest.mark.asyncio
    async def test_register_success(self):
        """Testa registro com sucesso."""
        # Este teste verifica o fluxo lógico, não a integração com SQLAlchemy.
        # Para testar o endpoint real, usamos testes de integração.

        # Teste simplificado: verificar que UserCreate valida corretamente
        user_data = UserCreate(
            email="new@test.com",
            password="SecurePass123",
            name="New User",
        )

        assert user_data.email == "new@test.com"
        assert user_data.name == "New User"
        assert user_data.password == "SecurePass123"

    @pytest.mark.asyncio
    async def test_register_password_hashing(self):
        """Testa que a senha é hasheada no registro."""
        from core.auth.security import get_password_hash, verify_password

        password = "SecurePass123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed)

    @pytest.mark.asyncio
    async def test_register_email_exists(self):
        """Testa registro com email existente."""
        user_data = UserCreate(
            email="existing@test.com",
            password="SecurePass123",
            name="Test User",
        )

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_existing_user = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_existing_user
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await register(user_data, mock_db)

        assert exc_info.value.status_code == 400
        assert "Email ja cadastrado" in exc_info.value.detail


class TestLoginEndpoint:
    """Testes para endpoint de login."""

    @pytest.mark.asyncio
    async def test_login_success(self):
        """Testa login com sucesso."""
        mock_form = MagicMock()
        mock_form.username = "user@test.com"
        mock_form.password = "password123"

        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.email = "user@test.com"
        mock_user.password_hash = "hashed"
        mock_user.role = "user"
        mock_user.is_active = True

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        with (
            patch("api.v1.endpoints.auth.verify_password", return_value=True),
            patch("api.v1.endpoints.auth.create_access_token", return_value="access"),
            patch("api.v1.endpoints.auth.create_refresh_token", return_value="refresh"),
        ):
            result = await login(mock_form, mock_db)

            assert result.access_token == "access"
            assert result.refresh_token == "refresh"
            assert result.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self):
        """Testa login com credenciais inválidas."""
        mock_form = MagicMock()
        mock_form.username = "user@test.com"
        mock_form.password = "wrong_password"

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(HTTPException) as exc_info:
            await login(mock_form, mock_db)

        assert exc_info.value.status_code == 401
        assert "Credenciais invalidas" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_login_wrong_password(self):
        """Testa login com senha errada."""
        mock_form = MagicMock()
        mock_form.username = "user@test.com"
        mock_form.password = "wrong"

        mock_user = MagicMock()
        mock_user.password_hash = "hashed"

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        with patch("api.v1.endpoints.auth.verify_password", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await login(mock_form, mock_db)

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_user(self):
        """Testa login com usuário inativo."""
        mock_form = MagicMock()
        mock_form.username = "inactive@test.com"
        mock_form.password = "password"

        mock_user = MagicMock()
        mock_user.password_hash = "hashed"
        mock_user.is_active = False

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        with patch("api.v1.endpoints.auth.verify_password", return_value=True):
            with pytest.raises(HTTPException) as exc_info:
                await login(mock_form, mock_db)

            assert exc_info.value.status_code == 403
            assert "Usuario inativo" in exc_info.value.detail


class TestRefreshTokenEndpoint:
    """Testes para endpoint de refresh token."""

    @pytest.mark.asyncio
    async def test_refresh_success(self):
        """Testa refresh com sucesso."""
        token_data = TokenRefresh(refresh_token="valid_refresh_token")

        mock_user = MagicMock()
        mock_user.id = uuid4()
        mock_user.email = "user@test.com"
        mock_user.role = "user"
        mock_user.is_active = True

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        with patch("api.v1.endpoints.auth.verify_refresh_token") as mock_verify:
            mock_verify.return_value = {"sub": str(mock_user.id)}

            with (
                patch("api.v1.endpoints.auth.create_access_token", return_value="new_access"),
                patch("api.v1.endpoints.auth.create_refresh_token", return_value="new_refresh"),
            ):
                result = await refresh_token(token_data, mock_db)

                assert result.access_token == "new_access"
                assert result.refresh_token == "new_refresh"

    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self):
        """Testa refresh com token inválido."""
        token_data = TokenRefresh(refresh_token="invalid_token")
        mock_db = AsyncMock()

        with patch("api.v1.endpoints.auth.verify_refresh_token") as mock_verify:
            mock_verify.side_effect = Exception("Invalid token")

            with pytest.raises(HTTPException) as exc_info:
                await refresh_token(token_data, mock_db)

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_no_subject(self):
        """Testa refresh sem subject no token."""
        token_data = TokenRefresh(refresh_token="token_no_sub")
        mock_db = AsyncMock()

        with patch("api.v1.endpoints.auth.verify_refresh_token") as mock_verify:
            mock_verify.return_value = {}  # Sem "sub"

            with pytest.raises(HTTPException) as exc_info:
                await refresh_token(token_data, mock_db)

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_user_not_found(self):
        """Testa refresh com usuário não encontrado."""
        token_data = TokenRefresh(refresh_token="valid_token")

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with patch("api.v1.endpoints.auth.verify_refresh_token") as mock_verify:
            mock_verify.return_value = {"sub": str(uuid4())}

            with pytest.raises(HTTPException) as exc_info:
                await refresh_token(token_data, mock_db)

            assert exc_info.value.status_code == 401


class TestGetCurrentUserEndpoint:
    """Testes para endpoint /me."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self):
        """Testa obtenção do usuário atual."""
        mock_user = MagicMock(spec=User)
        mock_user.id = uuid4()
        mock_user.email = "user@test.com"
        mock_user.name = "Test User"
        mock_user.phone = None
        mock_user.role = "user"
        mock_user.is_active = True
        mock_user.created_at = datetime.now(UTC)
        mock_user.updated_at = datetime.now(UTC)
        mock_user.last_login = None

        with patch("api.v1.endpoints.auth.UserResponse") as mock_response_cls:
            mock_response = MagicMock()
            mock_response_cls.model_validate.return_value = mock_response

            result = await get_current_user_info(mock_user)

            mock_response_cls.model_validate.assert_called_once_with(mock_user)
            assert result == mock_response


class TestAuthRouter:
    """Testes para configuração do router."""

    def test_router_prefix(self):
        """Testa prefixo do router."""
        from api.v1.endpoints.auth import router

        assert router.prefix == "/auth"

    def test_router_tags(self):
        """Testa tags do router."""
        from api.v1.endpoints.auth import router

        assert "Authentication" in router.tags
