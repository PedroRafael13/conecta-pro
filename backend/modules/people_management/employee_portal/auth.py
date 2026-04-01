"""
Autenticacao JWT do Portal do Funcionario.

Usa core/auth/jwt.py (python-jose) para tokens seguros.
Audience: "employee_portal" — impede uso de tokens admin no portal.
Expiracao: access 8h, refresh 24h.
"""

import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request
from fastapi import status as http_status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import settings

logger = logging.getLogger(__name__)

PORTAL_AUDIENCE = "employee_portal"
PORTAL_ACCESS_EXPIRE_HOURS = 8
PORTAL_REFRESH_EXPIRE_HOURS = 24

_bearer = HTTPBearer(auto_error=False)


def create_portal_access_token(
    employee_id: str,
    nome: str,
    cargo: str = "",
    cpf: str = "",
    escala: str = "",
) -> str:
    """Cria token de acesso JWT para o portal do funcionario.

    Args:
        employee_id: UUID do funcionario.
        nome: Nome do funcionario.
        cargo: Cargo do funcionario.
        cpf: CPF do funcionario (mascarado no token).
        escala: Escala de trabalho (ex: 12x36).

    Returns:
        Token JWT assinado.
    """
    from jose import jwt

    payload = {
        "sub": str(employee_id),
        "employee_id": str(employee_id),
        "nome": nome,
        "cargo": cargo,
        "cpf": cpf,
        "escala": escala,
        "aud": PORTAL_AUDIENCE,
        "type": "portal_access",
        "jti": str(uuid.uuid4()),
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(hours=PORTAL_ACCESS_EXPIRE_HOURS),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_portal_refresh_token(employee_id: str) -> str:
    """Cria token de refresh JWT para o portal.

    Args:
        employee_id: UUID do funcionario.

    Returns:
        Token JWT de refresh.
    """
    from jose import jwt

    payload = {
        "sub": str(employee_id),
        "aud": PORTAL_AUDIENCE,
        "type": "portal_refresh",
        "jti": str(uuid.uuid4()),
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(hours=PORTAL_REFRESH_EXPIRE_HOURS),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def _decode_portal_token(token: str, expected_type: str = "portal_access") -> dict[str, Any]:
    """Decodifica e valida token JWT do portal.

    Args:
        token: Token JWT.
        expected_type: Tipo esperado (portal_access ou portal_refresh).

    Returns:
        Payload do token.

    Raises:
        HTTPException: Se token invalido.
    """
    from jose import jwt
    from jose.exceptions import JWTError

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            audience=PORTAL_AUDIENCE,
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalido ou expirado: {exc}",
        ) from exc

    if payload.get("type") != expected_type:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail=f"Token nao e do tipo {expected_type}",
        )

    return payload


async def get_portal_employee_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str:
    """Extrai employee_id do token JWT do portal.

    Valida audience 'employee_portal' para impedir uso de tokens admin.

    Args:
        request: Objeto Request do FastAPI.
        credentials: Credenciais Bearer extraidas pelo FastAPI.

    Returns:
        employee_id (str UUID) do funcionario autenticado.

    Raises:
        HTTPException: 401 se token ausente, invalido ou expirado.
    """
    if not credentials:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso nao fornecido.",
        )

    payload = _decode_portal_token(credentials.credentials, "portal_access")
    employee_id = payload.get("employee_id") or payload.get("sub")

    if not employee_id:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido: employee_id ausente.",
        )

    return str(employee_id)


# Type alias para uso nos controllers
CurrentEmployeeId = Annotated[str, Depends(get_portal_employee_id)]
