"""
Gerenciamento de tokens JWT para autenticação.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt

from core.config import settings


class TokenError(Exception):
    """Exceção para erros relacionados a tokens."""


def create_access_token(
    subject: str,
    extra_data: Optional[dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
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
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
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
    expires_delta: Optional[timedelta] = None,
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
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
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
