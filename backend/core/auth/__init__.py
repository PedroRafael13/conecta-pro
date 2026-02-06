"""Módulo de autenticação."""

from .dependencies import (
    CurrentActiveUser,
    CurrentUser,
    CurrentUserId,
    get_current_active_user,
    get_current_user,
    get_current_user_id,
)
from .jwt import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_access_token,
    verify_refresh_token,
    verify_token_not_blacklisted,
)
from .security import get_password_hash, hash_password, verify_password
from .utils import get_tenant_id

__all__ = [
    # JWT
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "verify_access_token",
    "verify_refresh_token",
    "verify_token_not_blacklisted",
    "TokenError",
    # Security
    "hash_password",
    "get_password_hash",
    "verify_password",
    # Dependencies
    "get_current_user_id",
    "get_current_user",
    "get_current_active_user",
    "CurrentUserId",
    "CurrentUser",
    "CurrentActiveUser",
    # Utils
    "get_tenant_id",
]
