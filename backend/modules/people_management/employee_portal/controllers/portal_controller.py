"""
Portal Controller — Autenticacao e dashboard do portal do funcionario.

Endpoints:
- POST /portal/auth/login
- GET /portal/dashboard
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from modules.people_management.employee_portal.schemas.portal import (
    PortalDashboard,
    PortalLoginRequest,
    PortalLoginResponse,
)
from modules.people_management.employee_portal.services.portal_service import PortalService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Portal - Auth"])

# JWT secret para tokens do portal
PORTAL_JWT_SECRET = os.getenv("PORTAL_JWT_SECRET", "portal-secret-key-2026")


@router.post(
    "/auth/login",
    response_model=PortalLoginResponse,
    summary="Login do funcionario no portal",
    description="Autentica o funcionario por CPF e senha, retornando token de acesso.",
)
async def portal_login(
    request: Request,
    login_data: PortalLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Autentica funcionario no portal por CPF e senha.

    Args:
        request: Objeto Request do FastAPI.
        login_data: CPF e senha do funcionario.
        db: Sessao do banco de dados.

    Returns:
        PortalLoginResponse com token, nome e ID do funcionario.

    Raises:
        HTTPException: 401 se credenciais invalidas.
    """
    service = PortalService(db)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    result = await service.authenticate_employee(
        cpf=login_data.cpf,
        password=login_data.password,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    if not result:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="CPF ou senha invalidos.",
        )

    # Gerar token simples (em producao usar jose/jwt)
    try:
        import jwt

        token_payload = {
            "employee_id": result["employee_id"],
            "nome": result["nome"],
            "exp": datetime.utcnow() + timedelta(hours=8),
            "type": "portal",
        }
        access_token = jwt.encode(token_payload, PORTAL_JWT_SECRET, algorithm="HS256")
    except ImportError:
        # Fallback sem PyJWT
        import hashlib

        token_data = f"{result['employee_id']}:{datetime.utcnow().isoformat()}:{PORTAL_JWT_SECRET}"
        access_token = hashlib.sha256(token_data.encode()).hexdigest()

    return PortalLoginResponse(
        access_token=access_token,
        employee_name=result["nome"],
        employee_id=result["employee_id"],
    )


@router.get(
    "/dashboard",
    response_model=PortalDashboard,
    summary="Dashboard do funcionario",
    description="Retorna dados resumidos do painel do funcionario logado.",
)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Retorna dados do dashboard do funcionario.

    Args:
        db: Sessao do banco de dados.

    Returns:
        PortalDashboard com informacoes do funcionario.

    Note:
        Em producao, o employee_id deve vir do token JWT decodificado.
        Aqui esta simplificado para demonstracao.
    """
    # TODO: Extrair employee_id do token JWT do portal
    # Por enquanto retorna dashboard vazio
    return PortalDashboard(
        name="Funcionario",
        position=None,
        workplace=None,
        next_shift=None,
        pending_documents=0,
        unread_notifications=0,
    )
