"""
Utilitários de autenticação e autorização.
"""

from core.auth.dependencies import CurrentActiveUser

# ID padrão para sistemas single-tenant (ERP de empresa única)
DEFAULT_TENANT_ID = "00000000-0000-0000-0000-000000000001"


def get_tenant_id(user: CurrentActiveUser) -> str:
    """
    Obtém tenant_id do usuário de forma segura.

    Em sistemas single-tenant, retorna o DEFAULT_TENANT_ID quando o usuário
    não possui tenant_id explícito (caso comum em ERPs de empresa única).

    Args:
        user: Usuário autenticado e ativo

    Returns:
        ID do tenant como string
    """
    tenant_id = getattr(user, "tenant_id", None) or getattr(user, "condominio_id", None)

    if not tenant_id:
        # Sistema single-tenant: todos os usuários pertencem ao mesmo tenant
        return DEFAULT_TENANT_ID

    return str(tenant_id)
