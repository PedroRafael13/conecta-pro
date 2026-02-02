"""
Sistema de permissoes para o modulo operacional.

Define roles, permissoes e decorators para controle de acesso.
"""

from enum import Enum
from functools import wraps
from typing import Callable, List, Union

from fastapi import Depends, HTTPException, status

from core.auth.dependencies import CurrentActiveUser


class OperacionalRole(str, Enum):
    """Roles do modulo operacional."""

    ADMINISTRADOR = "administrador"
    GERENTE_OPERACIONAL = "gerente_operacional"
    SUPERVISOR = "supervisor"
    INSPETOR = "inspetor"
    LIDER = "lider"
    AGENTE = "agente"


# Hierarquia de poder (maior numero = mais poder)
ROLE_POWER = {
    OperacionalRole.ADMINISTRADOR: 100,
    OperacionalRole.GERENTE_OPERACIONAL: 80,
    OperacionalRole.SUPERVISOR: 60,
    OperacionalRole.INSPETOR: 40,
    OperacionalRole.LIDER: 20,
    OperacionalRole.AGENTE: 10,
}


class Permission(str, Enum):
    """Permissoes do modulo operacional."""

    # Postos
    POSTS_CREATE = "posts:create"
    POSTS_EDIT = "posts:edit"
    POSTS_DELETE = "posts:delete"
    POSTS_VIEW = "posts:view"

    # Escalas
    SCALES_CREATE = "scales:create"
    SCALES_APPROVE = "scales:approve"
    SCALES_PUBLISH = "scales:publish"
    SCALES_VIEW_ALL = "scales:view_all"
    SCALES_VIEW_OWN = "scales:view_own"

    # Alocacoes
    ALLOCATIONS_CREATE = "allocations:create"
    ALLOCATIONS_EDIT = "allocations:edit"
    ALLOCATIONS_VIEW = "allocations:view"

    # Turnos
    SHIFTS_CREATE = "shifts:create"
    SHIFTS_CHECKIN = "shifts:checkin"
    SHIFTS_MARK_MISSED = "shifts:mark_missed"
    SHIFTS_VIEW_ALL = "shifts:view_all"
    SHIFTS_VIEW_OWN = "shifts:view_own"

    # Substituicoes
    SUBSTITUTIONS_CREATE = "substitutions:create"
    SUBSTITUTIONS_APPROVE = "substitutions:approve"

    # Banco de Horas
    TIMEBANK_CREATE = "timebank:create"
    TIMEBANK_APPROVE = "timebank:approve"
    TIMEBANK_VIEW_ALL = "timebank:view_all"
    TIMEBANK_VIEW_OWN = "timebank:view_own"

    # Relatorios
    REPORTS_VIEW = "reports:view"

    # Funcionarios
    EMPLOYEES_VIEW = "employees:view"
    EMPLOYEES_EDIT = "employees:edit"
    EMPLOYEES_CREATE = "employees:create"
    EMPLOYEES_DELETE = "employees:delete"

    # Ocorrencias
    OCCURRENCES_CREATE = "occurrences:create"
    OCCURRENCES_VIEW = "occurrences:view"
    OCCURRENCES_EDIT = "occurrences:edit"
    OCCURRENCES_DELETE = "occurrences:delete"
    OCCURRENCES_RESOLVE = "occurrences:resolve"

    # Rondas de Inspecao
    INSPECTION_ROUNDS_CREATE = "inspection_rounds:create"
    INSPECTION_ROUNDS_VIEW = "inspection_rounds:view"
    INSPECTION_ROUNDS_START = "inspection_rounds:start"
    INSPECTION_ROUNDS_COMPLETE = "inspection_rounds:complete"
    INSPECTION_ROUNDS_REGISTER_OCCURRENCE = "inspection_rounds:register_occurrence"

    # Disciplinar
    DISCIPLINARY_CREATE = "disciplinary:create"
    DISCIPLINARY_VIEW = "disciplinary:view"
    DISCIPLINARY_EDIT = "disciplinary:edit"
    DISCIPLINARY_DELETE = "disciplinary:delete"
    DISCIPLINARY_SUBMIT_APPROVAL = "disciplinary:submit_approval"
    DISCIPLINARY_APPROVE = "disciplinary:approve"
    DISCIPLINARY_REJECT = "disciplinary:reject"

    # Comunicacao - Comunicados
    ANNOUNCEMENTS_CREATE = "announcements:create"
    ANNOUNCEMENTS_VIEW = "announcements:view"
    ANNOUNCEMENTS_EDIT = "announcements:edit"
    ANNOUNCEMENTS_DELETE = "announcements:delete"
    ANNOUNCEMENTS_PUBLISH = "announcements:publish"

    # Comunicacao - Notificacoes
    NOTIFICATIONS_CREATE = "notifications:create"
    NOTIFICATIONS_VIEW = "notifications:view"
    NOTIFICATIONS_VIEW_ALL = "notifications:view_all"
    NOTIFICATIONS_MARK_READ = "notifications:mark_read"

    # Reembolsos (mantido aqui por compatibilidade - sera movido para financeiro)
    REIMBURSEMENTS_CREATE = "reimbursements:create"
    REIMBURSEMENTS_VIEW = "reimbursements:view"
    REIMBURSEMENTS_EDIT = "reimbursements:edit"
    REIMBURSEMENTS_APPROVE = "reimbursements:approve"
    REIMBURSEMENTS_REJECT = "reimbursements:reject"


# Mapeamento Role -> Permissoes
ROLE_PERMISSIONS: dict[OperacionalRole, list[Permission]] = {
    OperacionalRole.ADMINISTRADOR: list(Permission),  # Todas as permissoes
    OperacionalRole.GERENTE_OPERACIONAL: [
        Permission.POSTS_CREATE,
        Permission.POSTS_EDIT,
        Permission.POSTS_DELETE,
        Permission.POSTS_VIEW,
        Permission.SCALES_CREATE,
        Permission.SCALES_APPROVE,
        Permission.SCALES_PUBLISH,
        Permission.SCALES_VIEW_ALL,
        Permission.SCALES_VIEW_OWN,
        Permission.ALLOCATIONS_CREATE,
        Permission.ALLOCATIONS_EDIT,
        Permission.ALLOCATIONS_VIEW,
        Permission.SHIFTS_CREATE,
        Permission.SHIFTS_CHECKIN,
        Permission.SHIFTS_MARK_MISSED,
        Permission.SHIFTS_VIEW_ALL,
        Permission.SHIFTS_VIEW_OWN,
        Permission.SUBSTITUTIONS_CREATE,
        Permission.SUBSTITUTIONS_APPROVE,
        Permission.TIMEBANK_CREATE,
        Permission.TIMEBANK_APPROVE,
        Permission.TIMEBANK_VIEW_ALL,
        Permission.TIMEBANK_VIEW_OWN,
        Permission.REPORTS_VIEW,
        Permission.EMPLOYEES_VIEW,
        Permission.EMPLOYEES_EDIT,
        Permission.EMPLOYEES_CREATE,
        Permission.EMPLOYEES_DELETE,
        Permission.OCCURRENCES_CREATE,
        Permission.OCCURRENCES_VIEW,
        Permission.OCCURRENCES_EDIT,
        Permission.OCCURRENCES_DELETE,
        Permission.OCCURRENCES_RESOLVE,
        Permission.INSPECTION_ROUNDS_CREATE,
        Permission.INSPECTION_ROUNDS_VIEW,
        Permission.INSPECTION_ROUNDS_START,
        Permission.INSPECTION_ROUNDS_COMPLETE,
        Permission.INSPECTION_ROUNDS_REGISTER_OCCURRENCE,
        Permission.DISCIPLINARY_CREATE,
        Permission.DISCIPLINARY_VIEW,
        Permission.DISCIPLINARY_EDIT,
        Permission.DISCIPLINARY_DELETE,
        Permission.DISCIPLINARY_SUBMIT_APPROVAL,
        Permission.DISCIPLINARY_APPROVE,
        Permission.DISCIPLINARY_REJECT,
        Permission.ANNOUNCEMENTS_CREATE,
        Permission.ANNOUNCEMENTS_VIEW,
        Permission.ANNOUNCEMENTS_EDIT,
        Permission.ANNOUNCEMENTS_DELETE,
        Permission.ANNOUNCEMENTS_PUBLISH,
        Permission.NOTIFICATIONS_CREATE,
        Permission.NOTIFICATIONS_VIEW,
        Permission.NOTIFICATIONS_VIEW_ALL,
        Permission.NOTIFICATIONS_MARK_READ,
        Permission.REIMBURSEMENTS_CREATE,
        Permission.REIMBURSEMENTS_VIEW,
        Permission.REIMBURSEMENTS_EDIT,
        Permission.REIMBURSEMENTS_APPROVE,
        Permission.REIMBURSEMENTS_REJECT,
    ],
    OperacionalRole.SUPERVISOR: [
        Permission.POSTS_VIEW,
        Permission.SCALES_CREATE,
        Permission.SCALES_APPROVE,
        Permission.SCALES_PUBLISH,
        Permission.SCALES_VIEW_ALL,
        Permission.SCALES_VIEW_OWN,
        Permission.ALLOCATIONS_CREATE,
        Permission.ALLOCATIONS_EDIT,
        Permission.ALLOCATIONS_VIEW,
        Permission.SHIFTS_CREATE,
        Permission.SHIFTS_CHECKIN,
        Permission.SHIFTS_MARK_MISSED,
        Permission.SHIFTS_VIEW_ALL,
        Permission.SHIFTS_VIEW_OWN,
        Permission.SUBSTITUTIONS_CREATE,
        Permission.SUBSTITUTIONS_APPROVE,
        Permission.TIMEBANK_CREATE,
        Permission.TIMEBANK_APPROVE,
        Permission.TIMEBANK_VIEW_ALL,
        Permission.TIMEBANK_VIEW_OWN,
        Permission.REPORTS_VIEW,
        Permission.EMPLOYEES_VIEW,
        Permission.EMPLOYEES_EDIT,
        Permission.OCCURRENCES_CREATE,
        Permission.OCCURRENCES_VIEW,
        Permission.OCCURRENCES_EDIT,
        Permission.OCCURRENCES_RESOLVE,
        Permission.INSPECTION_ROUNDS_CREATE,
        Permission.INSPECTION_ROUNDS_VIEW,
        Permission.INSPECTION_ROUNDS_START,
        Permission.INSPECTION_ROUNDS_COMPLETE,
        Permission.INSPECTION_ROUNDS_REGISTER_OCCURRENCE,
        Permission.DISCIPLINARY_CREATE,
        Permission.DISCIPLINARY_VIEW,
        Permission.DISCIPLINARY_EDIT,
        Permission.DISCIPLINARY_SUBMIT_APPROVAL,
        Permission.ANNOUNCEMENTS_CREATE,
        Permission.ANNOUNCEMENTS_VIEW,
        Permission.ANNOUNCEMENTS_EDIT,
        Permission.ANNOUNCEMENTS_PUBLISH,
        Permission.NOTIFICATIONS_CREATE,
        Permission.NOTIFICATIONS_VIEW,
        Permission.NOTIFICATIONS_VIEW_ALL,
        Permission.NOTIFICATIONS_MARK_READ,
        Permission.REIMBURSEMENTS_CREATE,
        Permission.REIMBURSEMENTS_VIEW,
        Permission.REIMBURSEMENTS_EDIT,
    ],
    OperacionalRole.INSPETOR: [
        Permission.POSTS_VIEW,
        Permission.SCALES_VIEW_ALL,
        Permission.SCALES_VIEW_OWN,
        Permission.ALLOCATIONS_VIEW,
        Permission.SHIFTS_CHECKIN,
        Permission.SHIFTS_MARK_MISSED,
        Permission.SHIFTS_VIEW_ALL,
        Permission.SHIFTS_VIEW_OWN,
        Permission.SUBSTITUTIONS_CREATE,
        Permission.SUBSTITUTIONS_APPROVE,
        Permission.TIMEBANK_VIEW_ALL,
        Permission.TIMEBANK_VIEW_OWN,
        Permission.REPORTS_VIEW,
        Permission.EMPLOYEES_VIEW,
        Permission.OCCURRENCES_CREATE,
        Permission.OCCURRENCES_VIEW,
        Permission.OCCURRENCES_EDIT,
        Permission.INSPECTION_ROUNDS_CREATE,
        Permission.INSPECTION_ROUNDS_VIEW,
        Permission.INSPECTION_ROUNDS_START,
        Permission.INSPECTION_ROUNDS_COMPLETE,
        Permission.INSPECTION_ROUNDS_REGISTER_OCCURRENCE,
        Permission.DISCIPLINARY_VIEW,
        Permission.ANNOUNCEMENTS_VIEW,
        Permission.NOTIFICATIONS_VIEW,
        Permission.NOTIFICATIONS_MARK_READ,
    ],
    OperacionalRole.LIDER: [
        Permission.POSTS_VIEW,
        Permission.SCALES_VIEW_ALL,
        Permission.SCALES_VIEW_OWN,
        Permission.ALLOCATIONS_VIEW,
        Permission.SHIFTS_CHECKIN,
        Permission.SHIFTS_VIEW_ALL,
        Permission.SHIFTS_VIEW_OWN,
        Permission.SUBSTITUTIONS_CREATE,
        Permission.TIMEBANK_VIEW_OWN,
        Permission.EMPLOYEES_VIEW,
        Permission.OCCURRENCES_CREATE,
        Permission.OCCURRENCES_VIEW,
        Permission.INSPECTION_ROUNDS_VIEW,
        Permission.DISCIPLINARY_VIEW,
        Permission.ANNOUNCEMENTS_VIEW,
        Permission.NOTIFICATIONS_VIEW,
        Permission.NOTIFICATIONS_MARK_READ,
    ],
    OperacionalRole.AGENTE: [
        Permission.SCALES_VIEW_OWN,
        Permission.SHIFTS_CHECKIN,
        Permission.SHIFTS_VIEW_OWN,
        Permission.TIMEBANK_VIEW_OWN,
        Permission.OCCURRENCES_CREATE,
        Permission.OCCURRENCES_VIEW,
        Permission.ANNOUNCEMENTS_VIEW,
        Permission.NOTIFICATIONS_VIEW,
        Permission.NOTIFICATIONS_MARK_READ,
    ],
}

# Roles que tem acesso total (admin do sistema + admin do operacional)
ADMIN_ROLES = {"admin", "super_admin", "administrador"}


def get_user_permissions(user_role: str) -> list[str]:
    """
    Retorna lista de permissoes para um role.

    Args:
        user_role: Role do usuario

    Returns:
        Lista de permissoes (strings)
    """
    # Admins tem todas as permissoes
    if user_role in ADMIN_ROLES:
        return [p.value for p in Permission]

    # Buscar permissoes do role operacional
    try:
        role_enum = OperacionalRole(user_role)
        permissions = ROLE_PERMISSIONS.get(role_enum, [])
        return [p.value for p in permissions]
    except ValueError:
        return []


def has_permission(user_role: str, permission: Permission) -> bool:
    """
    Verifica se um role tem uma permissao especifica.

    Args:
        user_role: Role do usuario
        permission: Permissao a verificar

    Returns:
        True se tem permissao
    """
    user_permissions = get_user_permissions(user_role)
    return permission.value in user_permissions


def require_operacional_permission(*permissions: Permission):
    """
    Dependency factory para validar permissoes do modulo operacional.

    Uso:
        @router.get("/", dependencies=[Depends(require_operacional_permission(Permission.POSTS_VIEW))])
        async def list_posts(): ...

    Args:
        *permissions: Uma ou mais permissoes requeridas (basta ter uma)

    Returns:
        Dependency function para FastAPI
    """

    async def permission_checker(current_user: CurrentActiveUser):
        user_role = current_user.role

        # Admins sempre tem acesso
        if user_role in ADMIN_ROLES:
            return current_user

        # Buscar permissoes do role
        user_permissions = get_user_permissions(user_role)

        # Verificar se tem alguma das permissoes requeridas
        for perm in permissions:
            if perm.value in user_permissions:
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permissao insuficiente. Requer: {[p.value for p in permissions]}",
        )

    return Depends(permission_checker)


def require_minimum_role(minimum_role: OperacionalRole):
    """
    Dependency factory que verifica se o usuario tem no minimo o role especificado.

    Usa a hierarquia de poder para comparacao.

    Uso:
        @router.get("/", dependencies=[Depends(require_minimum_role(OperacionalRole.SUPERVISOR))])
        async def supervisor_endpoint(): ...

    Args:
        minimum_role: Role minimo requerido

    Returns:
        Dependency function para FastAPI
    """

    async def role_checker(current_user: CurrentActiveUser):
        user_role = current_user.role

        # Admins sempre tem acesso
        if user_role in ADMIN_ROLES:
            return current_user

        # Verificar hierarquia
        try:
            role_enum = OperacionalRole(user_role)
            user_power = ROLE_POWER.get(role_enum, 0)
            required_power = ROLE_POWER.get(minimum_role, 0)

            if user_power >= required_power:
                return current_user
        except ValueError:
            pass

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role minimo requerido: {minimum_role.value}",
        )

    return Depends(role_checker)


def check_own_resource(user_id: str, resource_user_id: str, user_role: str) -> bool:
    """
    Verifica se o usuario pode acessar um recurso proprio ou de outros.

    Util para endpoints que permitem ver recursos proprios mesmo sem
    permissao de VIEW_ALL.

    Args:
        user_id: ID do usuario autenticado
        resource_user_id: ID do usuario dono do recurso
        user_role: Role do usuario autenticado

    Returns:
        True se pode acessar
    """
    # Admin sempre pode
    if user_role in ADMIN_ROLES:
        return True

    # Proprio recurso
    if str(user_id) == str(resource_user_id):
        return True

    return False
