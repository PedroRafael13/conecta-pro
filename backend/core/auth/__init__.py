"""Módulo de autenticação."""

from .dependencies import CurrentUserId, get_current_user_id
from .jwt import (TokenError, create_access_token, create_refresh_token,
                  decode_token, verify_access_token, verify_refresh_token)
from .security import hash_password, verify_password

__all__ = [
    # JWT
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "verify_access_token",
    "verify_refresh_token",
    "TokenError",
    # Security
    "hash_password",
    "verify_password",
    # Dependencies
    "get_current_user_id",
    "CurrentUserId",
]
