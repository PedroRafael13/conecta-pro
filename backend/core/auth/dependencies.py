"""
Dependências de autenticação para FastAPI.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .jwt import TokenError, verify_access_token

security = HTTPBearer()


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> str:
    """
    Extrai e valida o user_id do token JWT.

    Args:
        credentials: Credenciais do header Authorization

    Returns:
        ID do usuário autenticado

    Raises:
        HTTPException: Se o token for inválido
    """
    try:
        payload = verify_access_token(credentials.credentials)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: subject não encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    except TokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


# Type alias para uso nos endpoints
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
