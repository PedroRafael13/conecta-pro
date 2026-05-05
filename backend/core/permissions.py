"""
Controle de acesso por módulo — Conecta Mais
INV-3: Jordan Jesus (CEO) sempre tem acesso total.
INV-4: Financeiro = apenas Jordan (validado no backend).
"""

from fastapi import Depends, HTTPException, status

from core.auth.dependencies import CurrentActiveUser

CEO_EMAIL = "jjesus@conectamais.pro"
_WILDCARD = "all"


def requer_modulo(modulo: str):
    """
    Dependency factory para proteger routers por módulo.

    Permite acesso se:
      - usuário é o CEO (email jjesus@conectamais.pro) — INV-3
      - usuário tem "all" em permissions (wildcard)
      - usuário tem "module:<modulo>" em permissions

    Uso:
        router = APIRouter()
        router.dependencies.append(Depends(requer_modulo("financeiro")))
    """

    async def _verificar(current_user: CurrentActiveUser):
        # INV-3: CEO sempre tem acesso total
        if current_user.email == CEO_EMAIL:
            return current_user

        perms: list[str] = current_user.permissions or []

        if _WILDCARD in perms or f"module:{modulo}" in perms:
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acesso negado ao módulo '{modulo}'. Solicite permissão ao administrador.",
        )

    return Depends(_verificar)
