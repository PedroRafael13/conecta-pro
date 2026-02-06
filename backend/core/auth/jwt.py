"""
Gerenciamento de tokens JWT para autenticação.
"""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from core.config import settings


class TokenError(Exception):
    """Exceção para erros relacionados a tokens."""


def create_access_token(
    subject: str,
    extra_data: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Cria token de acesso JWT.

    Args:
        subject: Identificador do usuário (geralmente user_id)
        extra_data: Dados adicionais para incluir no payload
        expires_delta: Tempo de expiração customizado

    Returns:
        Token JWT assinado
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": "access",
        "jti": str(uuid.uuid4()),
    }

    if extra_data:
        payload.update(extra_data)

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Cria token de refresh JWT.

    Args:
        subject: Identificador do usuário
        expires_delta: Tempo de expiração customizado

    Returns:
        Token JWT de refresh
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_token_expire_days)

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": "refresh",
        "jti": str(uuid.uuid4()),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    Decodifica e valida um token JWT.

    Args:
        token: Token JWT para decodificar

    Returns:
        Payload do token

    Raises:
        TokenError: Se o token for inválido ou expirado
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError as e:
        raise TokenError(f"Token inválido: {str(e)}") from e


def verify_access_token(token: str) -> dict[str, Any]:
    """
    Verifica se é um token de acesso válido.

    Args:
        token: Token para verificar

    Returns:
        Payload do token

    Raises:
        TokenError: Se não for um token de acesso válido
    """
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise TokenError("Token não é do tipo access")

    return payload


def verify_refresh_token(token: str) -> dict[str, Any]:
    """
    Verifica se é um token de refresh válido.

    Args:
        token: Token para verificar

    Returns:
        Payload do token

    Raises:
        TokenError: Se não for um token de refresh válido
    """
    payload = decode_token(token)

    if payload.get("type") != "refresh":
        raise TokenError("Token não é do tipo refresh")

    return payload


async def verify_token_not_blacklisted(payload: dict[str, Any]) -> None:
    """
    Verifica se o token foi revogado (blacklist via Redis).

    Args:
        payload: Payload JWT decodificado

    Raises:
        TokenError: Se o token estiver na blacklist
    """
    jti = payload.get("jti")
    if not jti:
        return  # Tokens legados sem jti são aceitos

    from core.auth.token_blacklist import is_blacklisted

    if await is_blacklisted(jti):
        raise TokenError("Token foi revogado")
