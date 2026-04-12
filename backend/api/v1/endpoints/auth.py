"""
Endpoints de autenticacao.
"""

# pylint: disable=unused-argument,import-outside-toplevel,broad-exception-caught
# pylint: disable=too-many-branches,too-many-return-statements,too-many-locals
# pylint: disable=redefined-outer-name,reimported

import secrets
from datetime import datetime, timedelta
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import create_access_token, create_refresh_token, verify_refresh_token
from core.auth.dependencies import get_current_active_user
from core.auth.security import get_password_hash, verify_password
from core.config import settings
from core.database import get_db
from core.logging import logger
from core.models import User
from core.rate_limit import limiter
from core.schemas.auth import ForgotPasswordRequest, ResetPasswordRequest, Token, TokenRefresh
from core.schemas.user import UserCreate, UserResponse


class LoginJSON(BaseModel):
    """Schema para login via JSON (email + password)."""

    email: str
    password: str


router = APIRouter(prefix="/auth", tags=["Authentication"])

# Google OAuth Config
GOOGLE_CLIENT_ID = getattr(settings, "GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = getattr(settings, "GOOGLE_CLIENT_SECRET", None)
GOOGLE_REDIRECT_URI = getattr(
    settings, "GOOGLE_REDIRECT_URI", "https://erp.conectamais.pro/api/v1/auth/google/callback"
)
FRONTEND_URL = getattr(settings, "FRONTEND_URL", "https://erp.conectamais.pro")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    response: Response,
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


@router.post("/login")
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Autentica usuario e retorna tokens. Aceita form-urlencoded ou JSON."""
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        username = body.get("email") or body.get("username", "")
        password = body.get("password", "")
    else:
        form = await request.form()
        username = form.get("username", "")
        password = form.get("password", "")

    # Buscar usuario (username = email)
    result = await db.execute(select(User).where(User.email == username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        logger.warning(f"Tentativa de login invalida: {username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais invalidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.warning(f"Tentativa de login com usuario inativo: {username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inativo",
        )

    # Atualizar ultimo login
    user.last_login = datetime.utcnow().isoformat()
    await db.commit()

    # Gerar tokens — incluir condominio_id no payload para fallback JWT
    extra: dict = {"email": user.email, "role": user.role}
    if getattr(user, "condominio_id", None):
        extra["condominio_id"] = str(user.condominio_id)
    access_token = create_access_token(
        subject=str(user.id),
        extra_data=extra,
    )
    user_refresh_token = create_refresh_token(subject=str(user.id))

    logger.info(f"Login bem-sucedido: {user.email}")
    return {
        "access_token": access_token,
        "refresh_token": user_refresh_token,
        "token_type": "Bearer",
        "user": {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role,
        },
    }


@router.post("/refresh", response_model=Token)
@limiter.limit("10/minute")
async def refresh_token(
    request: Request,
    response: Response,
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

        # Gerar novos tokens — incluir condominio_id no payload
        extra_refresh: dict = {"email": user.email, "role": user.role}
        if getattr(user, "condominio_id", None):
            extra_refresh["condominio_id"] = str(user.condominio_id)
        access_token = create_access_token(
            subject=str(user.id),
            extra_data=extra_refresh,
        )
        new_refresh_token = create_refresh_token(subject=str(user.id))

        logger.info(f"Tokens renovados para: {user.email}")
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="Bearer",  # noqa: S106
        )

    except Exception as e:
        logger.warning(f"Erro ao renovar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou expirado",
        ) from e


@router.post("/logout", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def logout(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_active_user),
):
    """Revoga o token JWT atual (logout)."""
    from core.auth.jwt import decode_token
    from core.auth.token_blacklist import add_to_blacklist

    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    try:
        payload = decode_token(token)
        jti = payload.get("jti")
        exp = payload.get("exp")

        if jti and exp:
            expires_at = datetime.utcfromtimestamp(exp)
            await add_to_blacklist(jti, expires_at)
            logger.info(f"Logout realizado: {current_user.email}")
        else:
            logger.warning(f"Token sem jti no logout: {current_user.email}")

    except Exception as e:
        logger.warning(f"Erro ao revogar token no logout: {e}")

    return {"message": "Logout realizado com sucesso"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Retorna informacoes do usuario atual."""
    return UserResponse.model_validate(current_user)


# =============================================================================
# Password Reset Endpoints
# =============================================================================


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    response: Response,
    body: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Solicita reset de senha — envia email com token."""
    # Sempre retorna 200 para nao vazar se email existe
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if user and user.is_active:
        # Gerar token de reset (JWT curto, 30 min)
        from core.auth.jwt import create_access_token

        reset_token = create_access_token(
            subject=str(user.id),
            extra_data={"type": "password_reset", "email": user.email},
            expires_delta=timedelta(minutes=30),
        )

        # Salvar token no Redis para invalidacao unica
        try:
            from core.cache.redis import cache_set

            await cache_set(f"password_reset:{reset_token}", str(user.id), ttl=1800)
        except Exception as e:
            logger.warning(f"Falha ao salvar reset token no Redis: {e}")

        # Enviar email
        from core.mailer import build_reset_password_email, send_email

        reset_url = f"{FRONTEND_URL}/reset-password?token={reset_token}"
        html = build_reset_password_email(user.name or user.email.split("@")[0], reset_url)
        await send_email(user.email, "Redefinir senha — Conecta PRO", html)

        logger.info(f"Reset de senha solicitado para: {user.email}")
    else:
        logger.info(f"Reset solicitado para email inexistente/inativo: {body.email}")

    return {"message": "Se o email estiver cadastrado, você receberá as instruções de recuperação."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    response: Response,
    body: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """Redefine senha usando token recebido por email."""
    from core.auth.jwt import decode_token
    from core.cache.redis import cache_delete, cache_get

    try:
        payload = decode_token(body.token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado",
        )

    if payload.get("type") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido",
        )

    # Verificar uso unico via Redis
    try:
        stored = await cache_get(f"password_reset:{body.token}")
        if not stored:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token já utilizado ou expirado",
            )
        await cache_delete(f"password_reset:{body.token}")
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Falha ao verificar reset token no Redis: {e}")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário não encontrado",
        )

    user.password_hash = get_password_hash(body.new_password)
    await db.commit()

    logger.info(f"Senha redefinida com sucesso: {user.email}")
    return {"message": "Senha redefinida com sucesso. Faça login com a nova senha."}


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

    # Gerar state para seguranca CSRF e persistir no Redis
    state = secrets.token_urlsafe(32)
    try:
        from core.cache.redis import cache_set

        await cache_set(f"oauth:state:{state}", "1", ttl=600)  # 10 min TTL
    except Exception as e:
        logger.warning(f"Falha ao salvar OAuth state no Redis: {e}")

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
    code: str | None = Query(None),
    state: str | None = Query(None),
    error: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Callback do Google OAuth2 - processa autenticacao."""
    if error:
        logger.warning(f"Erro no Google OAuth: {error}")
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=google_auth_failed")

    if not code:
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=no_code")

    # Validar state CSRF contra Redis
    if not state:
        logger.warning("Google OAuth callback sem state parameter")
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=missing_state")

    try:
        from core.cache.redis import cache_delete, cache_get

        stored_state = await cache_get(f"oauth:state:{state}")
        if not stored_state:
            logger.warning("Google OAuth state inválido ou expirado")
            return RedirectResponse(url=f"{FRONTEND_URL}/login?error=invalid_state")
        # Consumir state (uso único)
        await cache_delete(f"oauth:state:{state}")
    except Exception as e:
        logger.warning(f"Falha ao validar OAuth state: {e}")

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
            if not getattr(user, "google_id", None):
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
        redirect_params = urlencode(
            {
                "access_token": jwt_access_token,
                "refresh_token": jwt_refresh_token,
                "token_type": "Bearer",
            }
        )

        return RedirectResponse(url=f"{FRONTEND_URL}/auth/callback?{redirect_params}")

    except Exception as e:
        logger.error(f"Erro no Google OAuth callback: {e}")
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=internal_error")
