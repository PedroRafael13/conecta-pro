"""
Dependências de autenticação para FastAPI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .jwt import TokenError, verify_access_token

if TYPE_CHECKING:
    from core.models import User

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


async def get_current_user(
    user_id: CurrentUserId,
    _db: AsyncSession = Depends(lambda: None),  # Placeholder, usa get_db interno
) -> User:
    """
    Busca o usuario atual no banco de dados.

    Args:
        user_id: ID do usuario autenticado
        db: Sessao do banco de dados

    Returns:
        Objeto User do banco

    Raises:
        HTTPException: Se usuario nao encontrado
    """
    # Import local para evitar circular import
    from core.database import get_db
    from core.models import User

    # Obter sessao real do banco
    async for session in get_db():
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario nao encontrado",
            )

        return user

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Erro ao obter sessao do banco",
    )


async def get_current_active_user(
    user_id: CurrentUserId,
) -> User:
    """
    Busca o usuario atual e verifica se esta ativo.

    Args:
        user_id: ID do usuario autenticado

    Returns:
        Objeto User ativo

    Raises:
        HTTPException: Se usuario inativo ou nao encontrado
    """
    # Import local para evitar circular import
    from core.database import get_db
    from core.models import User

    # Obter sessao real do banco
    async for session in get_db():
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario nao encontrado",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inativo",
            )

        return user

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Erro ao obter sessao do banco",
    )


# Type aliases - usar string literal para evitar import circular
CurrentUser = Annotated["User", Depends(get_current_user)]
CurrentActiveUser = Annotated["User", Depends(get_current_active_user)]
