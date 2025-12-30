"""
Testes do módulo de autenticação.
"""

from datetime import timedelta

import pytest

from core.auth import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_access_token,
    verify_password,
    verify_refresh_token,
)


class TestPasswordSecurity:
    """Testes de hash e verificação de senhas."""

    def test_hash_password(self):
        """Testa geração de hash."""
        password = "senha_secreta_123"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 50  # bcrypt hash é longo

    def test_verify_password_correct(self):
        """Testa verificação com senha correta."""
        password = "minha_senha_forte"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Testa verificação com senha incorreta."""
        password = "senha_correta"
        wrong_password = "senha_errada"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_different_hashes_same_password(self):
        """Testa que mesmo password gera hashes diferentes (salt)."""
        password = "mesma_senha"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWT:
    """Testes de geração e validação de tokens JWT."""

    def test_create_access_token(self):
        """Testa criação de access token."""
        user_id = "user_123"
        token = create_access_token(user_id)

        assert token is not None
        assert len(token) > 50

    def test_create_access_token_with_extra_data(self):
        """Testa criação de access token com dados extras."""
        user_id = "user_123"
        extra = {"email": "test@example.com", "role": "admin"}
        token = create_access_token(user_id, extra_data=extra)

        payload = decode_token(token)
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "admin"

    def test_create_refresh_token(self):
        """Testa criação de refresh token."""
        user_id = "user_456"
        token = create_refresh_token(user_id)

        assert token is not None
        assert len(token) > 50

    def test_verify_access_token(self):
        """Testa verificação de access token."""
        user_id = "user_789"
        token = create_access_token(user_id)

        payload = verify_access_token(token)
        assert payload["sub"] == user_id
        assert payload["type"] == "access"

    def test_verify_refresh_token(self):
        """Testa verificação de refresh token."""
        user_id = "user_abc"
        token = create_refresh_token(user_id)

        payload = verify_refresh_token(token)
        assert payload["sub"] == user_id
        assert payload["type"] == "refresh"

    def test_access_token_as_refresh_fails(self):
        """Testa que access token não pode ser usado como refresh."""
        user_id = "user_test"
        access_token = create_access_token(user_id)

        with pytest.raises(TokenError, match="não é do tipo refresh"):
            verify_refresh_token(access_token)

    def test_refresh_token_as_access_fails(self):
        """Testa que refresh token não pode ser usado como access."""
        user_id = "user_test"
        refresh_token = create_refresh_token(user_id)

        with pytest.raises(TokenError, match="não é do tipo access"):
            verify_access_token(refresh_token)

    def test_invalid_token_fails(self):
        """Testa que token inválido gera erro."""
        with pytest.raises(TokenError):
            decode_token("token_invalido_123")

    def test_custom_expiration(self):
        """Testa criação de token com expiração customizada."""
        user_id = "user_exp"
        expires = timedelta(hours=2)
        token = create_access_token(user_id, expires_delta=expires)

        payload = decode_token(token)
        assert payload["sub"] == user_id


class TestTokenPayload:
    """Testes de estrutura do payload."""

    def test_access_token_payload_structure(self):
        """Testa estrutura do payload do access token."""
        user_id = "user_struct"
        token = create_access_token(user_id)
        payload = decode_token(token)

        assert "sub" in payload
        assert "exp" in payload
        assert "iat" in payload
        assert "type" in payload
        assert payload["type"] == "access"

    def test_refresh_token_payload_structure(self):
        """Testa estrutura do payload do refresh token."""
        user_id = "user_struct"
        token = create_refresh_token(user_id)
        payload = decode_token(token)

        assert "sub" in payload
        assert "exp" in payload
        assert "iat" in payload
        assert "type" in payload
        assert payload["type"] == "refresh"
