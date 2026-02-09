"""Testes para core services de autenticação.

Coverage: core/auth/jwt.py
"""

from datetime import UTC, datetime, timedelta

import jwt
import pytest

from core.auth.jwt import (
    TokenError,
    create_access_token,
    decode_token,
    verify_access_token,
)
from core.config import settings


class TestCreateAccessToken:
    """Testes para criação de token JWT."""

    def test_create_access_token_basic(self):
        """Testa criação de token JWT básico."""
        token = create_access_token(subject="test-user-id")

        assert token is not None
        assert isinstance(token, str)

        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        assert payload["sub"] == "test-user-id"
        assert payload["type"] == "access"
        assert "jti" in payload
        assert "exp" in payload
        assert "iat" in payload

    def test_create_access_token_with_custom_expiry(self):
        """Testa token com expiração customizada."""
        expires = timedelta(minutes=15)
        token = create_access_token(
            subject="user-123",
            expires_delta=expires,
        )

        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        assert payload["sub"] == "user-123"
        assert payload["exp"] > datetime.now(UTC).timestamp()

    def test_create_access_token_with_extra_data(self):
        """Testa token com dados extras no payload."""
        token = create_access_token(
            subject="user-456",
            extra_data={"role": "admin", "tenant_id": "t-123"},
        )

        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        assert payload["sub"] == "user-456"
        assert payload["role"] == "admin"
        assert payload["tenant_id"] == "t-123"

    def test_create_access_token_default_expiry(self):
        """Testa que token sem expires_delta usa valor padrão do settings."""
        token = create_access_token(subject="user-789")

        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
        iat = datetime.fromtimestamp(payload["iat"], tz=UTC)
        delta = exp - iat

        expected_minutes = settings.jwt_access_token_expire_minutes
        assert abs(delta.total_seconds() - expected_minutes * 60) < 5


class TestVerifyAccessToken:
    """Testes para verificação de token JWT."""

    def test_verify_valid_access_token(self):
        """Testa verificação de token válido."""
        token = create_access_token(subject="valid-user")
        payload = verify_access_token(token)

        assert payload is not None
        assert payload["sub"] == "valid-user"
        assert payload["type"] == "access"

    def test_verify_invalid_token_raises(self):
        """Testa que token inválido levanta TokenError."""
        with pytest.raises(TokenError):
            verify_access_token("invalid-token-string")

    def test_verify_expired_token_raises(self):
        """Testa que token expirado levanta TokenError."""
        token = create_access_token(
            subject="expired-user",
            expires_delta=timedelta(seconds=-1),
        )

        with pytest.raises(TokenError):
            verify_access_token(token)


class TestDecodeToken:
    """Testes para decodificação genérica de token."""

    def test_decode_valid_token(self):
        """Testa decodificação de token válido."""
        token = create_access_token(subject="decode-test")
        payload = decode_token(token)

        assert payload["sub"] == "decode-test"
        assert "exp" in payload

    def test_decode_tampered_token_raises(self):
        """Testa que token adulterado levanta TokenError."""
        token = create_access_token(subject="tamper-test")
        tampered = token[:-5] + "XXXXX"

        with pytest.raises(TokenError):
            decode_token(tampered)


class TestPasswordHashing:
    """Testes para hash de senha com passlib."""

    def test_password_hash_and_verify(self):
        """Testa hash e verificação de senha."""
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password = "test-password-123"

        hashed = pwd_context.hash(password)
        assert hashed != password

        assert pwd_context.verify(password, hashed) is True
        assert pwd_context.verify("wrong-password", hashed) is False

    def test_different_hashes_for_same_password(self):
        """Testa que hash é diferente a cada chamada (salt)."""
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password = "same-password"

        hash1 = pwd_context.hash(password)
        hash2 = pwd_context.hash(password)

        assert hash1 != hash2
        assert pwd_context.verify(password, hash1) is True
        assert pwd_context.verify(password, hash2) is True
