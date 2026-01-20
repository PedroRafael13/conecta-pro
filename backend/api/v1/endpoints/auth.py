"""
Endpoints de autenticacao.
"""

import secrets
from datetime import datetime
from typing import Optional
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import create_access_token, create_refresh_token, verify_refresh_token
from core.auth.dependencies import get_current_active_user
from core.auth.security import get_password_hash, verify_password
from core.config import settings
from core.database import get_db
from core.logging import logger
from core.models import User
from core.schemas.auth import Token, TokenRefresh
from core.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Google OAuth Config
GOOGLE_CLIENT_ID = getattr(settings, 'GOOGLE_CLIENT_ID', None)
GOOGLE_CLIENT_SECRET = getattr(settings, 'GOOGLE_CLIENT_SECRET', None)
GOOGLE_REDIRECT_URI = getattr(settings, 'GOOGLE_REDIRECT_URI', 'https://erp.conectamais.pro/api/v1/auth/google/callback')
FRONTEND_URL = getattr(settings, 'FRONTEND_URL', 'https://erp.conectamais.pro')


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


# =============================================================================
# Google OAuth2 Endpoints
# =============================================================================

@router.get("/google")
async def google_login():
    """Inicia fluxo de autenticacao com Google OAuth2."""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth nao configurado",
        )

    # Gerar state para seguranca CSRF
    state = secrets.token_urlsafe(32)

    # Parametros para autorizacao Google
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "state": state,
        "prompt": "select_account",
    }

    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    logger.info("Redirecionando para Google OAuth")
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_callback(
    code: Optional[str] = Query(None),
    error: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Callback do Google OAuth2 - processa autenticacao."""
    if error:
        logger.warning(f"Erro no Google OAuth: {error}")
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=google_auth_failed")

    if not code:
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=no_code")

    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=oauth_not_configured")

    try:
        # Trocar code por tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": GOOGLE_REDIRECT_URI,
                },
            )

            if token_response.status_code != 200:
                logger.error(f"Erro ao obter token Google: {token_response.text}")
                return RedirectResponse(url=f"{FRONTEND_URL}/login?error=token_exchange_failed")

            tokens = token_response.json()
            access_token = tokens.get("access_token")

            # Obter informacoes do usuario
            userinfo_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            if userinfo_response.status_code != 200:
                logger.error(f"Erro ao obter userinfo Google: {userinfo_response.text}")
                return RedirectResponse(url=f"{FRONTEND_URL}/login?error=userinfo_failed")

            google_user = userinfo_response.json()

        email = google_user.get("email")
        name = google_user.get("name", email.split("@")[0])
        google_id = google_user.get("id")

        if not email:
            return RedirectResponse(url=f"{FRONTEND_URL}/login?error=no_email")

        # Verificar se usuario existe
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            # Criar novo usuario via Google com status PENDING (aguardando aprovacao)
            user = User(
                email=email,
                name=name,
                password_hash=get_password_hash(secrets.token_urlsafe(32)),  # Senha aleatoria
                role="pending",  # Aguardando aprovacao do admin
                is_active=True,
                google_id=google_id,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"Novo usuario criado via Google (pendente): {email}")
        else:
            # Atualizar google_id se necessario
            if not getattr(user, 'google_id', None):
                user.google_id = google_id
            user.last_login = datetime.utcnow().isoformat()
            await db.commit()
            logger.info(f"Login Google existente: {email}")

        if not user.is_active:
            return RedirectResponse(url=f"{FRONTEND_URL}/login?error=user_inactive")

        # Gerar tokens JWT
        jwt_access_token = create_access_token(
            subject=str(user.id),
            extra_data={"email": user.email, "role": user.role},
        )
        jwt_refresh_token = create_refresh_token(subject=str(user.id))

        # Redirecionar para frontend com tokens
        redirect_params = urlencode({
            "access_token": jwt_access_token,
            "refresh_token": jwt_refresh_token,
            "token_type": "bearer",
        })

        return RedirectResponse(url=f"{FRONTEND_URL}/auth/callback?{redirect_params}")

    except Exception as e:
        logger.error(f"Erro no Google OAuth callback: {e}")
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=internal_error")
