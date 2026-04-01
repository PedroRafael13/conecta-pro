"""
Middleware de autenticacao do Portal do Cliente.

Fornece a dependencia FastAPI get_current_portal_client que
extrai e valida o token JWT do header Authorization.
"""

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from modules.client_portal.services.auth_service import PortalAuthService

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


async def get_current_portal_client(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> str:
    """Dependencia FastAPI que extrai e valida o token do portal.

    Extrai o token Bearer do header Authorization, valida contra
    as sessoes ativas e retorna o client_id do cliente autenticado.

    Args:
        credentials: Credenciais extraidas do header Authorization.
        db: Sessao async do banco de dados.

    Returns:
        client_id (str) do cliente autenticado.

    Raises:
        HTTPException 401: Se token ausente, invalido ou expirado.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticacao nao fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    auth_service = PortalAuthService(db)
    try:
        client_id = await auth_service.validate_token(token)
    except ValueError as e:
        logger.warning("Autenticacao portal falhou: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    return client_id
