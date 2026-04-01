"""
Endpoints de gerenciamento de usuarios.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth.dependencies import get_current_active_user
from core.database import get_db
from core.logging import logger
from core.models import User
from core.schemas.user import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


# Schemas para gerenciamento de usuarios
class UserUpdateRole(BaseModel):
    """Schema para atualizar role do usuario."""

    role: str


class UserListResponse(BaseModel):
    """Schema para lista paginada de usuarios."""

    users: list[UserResponse]
    total: int
    page: int
    per_page: int


# Roles validos no sistema
VALID_ROLES = [
    # Roles gerais
    "admin",  # Acesso total ao ERP
    "gestor",  # Dashboard, relatorios, operacoes
    "operador",  # Operacoes basicas
    "funcionario",  # Portal do Funcionario (ponto, escalas, docs)
    "pending",  # Aguardando aprovacao
    # Roles do modulo operacional
    "administrador",  # Poder total no operacional
    "gerente_operacional",  # Gestao completa do operacional
    "supervisor",  # Aprova escalas, coordena
    "inspetor",  # Fiscaliza, visualiza relatorios
    "lider",  # Coordena equipe local
    "agente",  # Apenas propria escala + check-in/out
]


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Verifica se usuario atual é admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores",
        )
    return current_user


@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    role: str | None = Query(None, description="Filtrar por role"),
    search: str | None = Query(None, description="Buscar por nome ou email"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> UserListResponse:
    """Lista todos os usuarios (admin only)."""
    query = select(User)
    count_query = select(func.count(User.id))

    # Filtrar por role
    if role:
        query = query.where(User.role == role)
        count_query = count_query.where(User.role == role)

    # Buscar por nome ou email
    if search:
        search_filter = f"%{search}%"
        query = query.where((User.name.ilike(search_filter)) | (User.email.ilike(search_filter)))
        count_query = count_query.where((User.name.ilike(search_filter)) | (User.email.ilike(search_filter)))

    # Paginacao
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page).order_by(User.created_at.desc())

    # Executar queries
    result = await db.execute(query)
    users = result.scalars().all()

    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/pending", response_model=list[UserResponse])
async def list_pending_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> list[UserResponse]:
    """Lista usuarios aguardando aprovacao (admin only)."""
    result = await db.execute(select(User).where(User.role == "pending").order_by(User.created_at.desc()))
    users = result.scalars().all()
    logger.info(f"Admin {current_user.email} listou {len(users)} usuarios pendentes")
    return [UserResponse.model_validate(u) for u in users]


@router.get("/roles")
async def list_roles(
    current_user: User = Depends(require_admin),
):
    """Lista roles disponiveis no sistema."""
    return {
        "roles": [
            # Roles gerais
            {"value": "admin", "label": "Administrador", "description": "Acesso total ao ERP"},
            {"value": "gestor", "label": "Gestor", "description": "Dashboard, relatórios, operações"},
            {"value": "operador", "label": "Operador", "description": "Operações básicas"},
            {"value": "funcionario", "label": "Funcionário", "description": "Portal do Funcionário"},
            {"value": "pending", "label": "Pendente", "description": "Aguardando aprovação"},
            # Roles do modulo operacional
            {
                "value": "administrador",
                "label": "Administrador Operacional",
                "description": "Poder total no módulo operacional",
            },
            {
                "value": "gerente_operacional",
                "label": "Gerente Operacional",
                "description": "Gestão completa do operacional",
            },
            {"value": "supervisor", "label": "Supervisor", "description": "Aprova escalas, coordena equipes"},
            {"value": "inspetor", "label": "Inspetor", "description": "Fiscaliza postos, visualiza relatórios"},
            {"value": "lider", "label": "Líder", "description": "Coordena equipe local"},
            {"value": "agente", "label": "Agente", "description": "Acesso à própria escala e check-in/out"},
        ]
    }


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> UserResponse:
    """Obtem detalhes de um usuario (admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario nao encontrado",
        )

    return UserResponse.model_validate(user)


@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    role_data: UserUpdateRole,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> UserResponse:
    """Atualiza role de um usuario (admin only)."""
    if role_data.role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role invalido. Valores aceitos: {', '.join(VALID_ROLES)}",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario nao encontrado",
        )

    # Nao permitir que admin remova seu proprio acesso
    if str(user.id) == str(current_user.id) and role_data.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voce nao pode remover seu proprio acesso de admin",
        )

    old_role = user.role
    user.role = role_data.role
    await db.commit()
    await db.refresh(user)

    logger.info(f"Admin {current_user.email} alterou role de {user.email}: {old_role} -> {role_data.role}")
    return UserResponse.model_validate(user)


@router.patch("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> UserResponse:
    """Ativa um usuario (admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario nao encontrado",
        )

    user.is_active = True
    await db.commit()
    await db.refresh(user)

    logger.info(f"Admin {current_user.email} ativou usuario {user.email}")
    return UserResponse.model_validate(user)


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> UserResponse:
    """Desativa um usuario (admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario nao encontrado",
        )

    # Nao permitir que admin desative a si mesmo
    if str(user.id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voce nao pode desativar sua propria conta",
        )

    user.is_active = False
    await db.commit()
    await db.refresh(user)

    logger.info(f"Admin {current_user.email} desativou usuario {user.email}")
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Exclui um usuario permanentemente (admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario nao encontrado",
        )

    # Nao permitir que admin exclua a si mesmo
    if str(user.id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voce nao pode excluir sua propria conta",
        )

    email = user.email
    await db.delete(user)
    await db.commit()

    logger.info(f"Admin {current_user.email} excluiu usuario {email}")
