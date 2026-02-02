"""
Utilitários de autenticação e autorização.
"""

from fastapi import HTTPException, status

from core.auth.dependencies import CurrentActiveUser
from core.logging import logger


def get_tenant_id(user: CurrentActiveUser) -> str:
    """
    Obtém tenant_id do usuário de forma segura.

    Tenta obter o tenant_id do atributo `tenant_id` ou `condominio_id`.
    Útil para garantir que o usuário está associado a um tenant antes
    de acessar recursos multitenancy.

    Args:
        user: Usuário autenticado e ativo

    Returns:
        ID do tenant como string

    Raises:
        HTTPException(403): Se usuário não possui tenant_id válido

    Example:
        ```python
        @router.get("/resource")
        async def get_resource(current_user: CurrentActiveUser):
            tenant_id = get_tenant_id(current_user)
            # Usar tenant_id para filtrar dados...
        ```
    """
    tenant_id = getattr(user, "tenant_id", None) or getattr(user, "condominio_id", None)

    if not tenant_id:
        logger.error(
            "Usuário sem tenant_id tentou acessar recurso",
            action="get_tenant_id_error",
            user_id=str(user.id),
            user_email=user.email,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário não está associado a nenhum condomínio/tenant. Contate o administrador.",
        )

    return str(tenant_id)
