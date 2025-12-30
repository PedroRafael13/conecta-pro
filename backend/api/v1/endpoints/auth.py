"""
Endpoints de autenticacao.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import create_access_token, create_refresh_token, verify_refresh_token
from core.auth.dependencies import get_current_active_user
from core.auth.security import get_password_hash, verify_password
from core.database import get_db
from core.logging import logger
from core.models import User
from core.schemas.auth import Token, TokenRefresh
from core.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Registra novo usuario."""
    # Verificar se email ja existe
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        logger.warning(f"Tentativa de registro com email existente: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ja cadastrado",
        )

    # Criar usuario
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        name=user_data.name,
        phone=user_data.phone,
        role=user_data.role,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info(f"Usuario registrado: {user.email}")
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Autentica usuario e retorna tokens."""
    # Buscar usuario (username = email)
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        logger.warning(f"Tentativa de login invalida: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.warning(f"Tentativa de login com usuario inativo: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inativo",
        )

    # Atualizar ultimo login
    user.last_login = datetime.utcnow().isoformat()
    await db.commit()

    # Gerar tokens
    access_token = create_access_token(
        subject=str(user.id),
        extra_data={"email": user.email, "role": user.role},
    )
    user_refresh_token = create_refresh_token(subject=str(user.id))

    logger.info(f"Login bem-sucedido: {user.email}")
    return Token(
        access_token=access_token,
        refresh_token=user_refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Renova tokens usando refresh token."""
    try:
        payload = verify_refresh_token(token_data.refresh_token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalido",
            )

        # Buscar usuario
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario nao encontrado ou inativo",
            )

        # Gerar novos tokens
        access_token = create_access_token(
            subject=str(user.id),
            extra_data={"email": user.email, "role": user.role},
        )
        new_refresh_token = create_refresh_token(subject=str(user.id))

        logger.info(f"Tokens renovados para: {user.email}")
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )

    except Exception as e:
        logger.warning(f"Erro ao renovar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou expirado",
        ) from e


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Retorna informacoes do usuario atual."""
    return UserResponse.model_validate(current_user)
