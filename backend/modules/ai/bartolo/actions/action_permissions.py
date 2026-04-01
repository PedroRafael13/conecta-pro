"""
Mapeamento de ações para permissões do sistema operacional.
"""

from modules.operacional.permissions import Permission

from .action_types import ActionType

ACTION_PERMISSIONS: dict[ActionType, Permission] = {
    # Escalas
    ActionType.CREATE_SCALE: Permission.SCALES_CREATE,
    ActionType.APPROVE_SCALE: Permission.SCALES_APPROVE,
    ActionType.PUBLISH_SCALE: Permission.SCALES_PUBLISH,
    # Alocações
    ActionType.ALLOCATE_EMPLOYEE: Permission.ALLOCATIONS_CREATE,
    ActionType.TERMINATE_ALLOCATION: Permission.ALLOCATIONS_EDIT,
    ActionType.TRANSFER_EMPLOYEE: Permission.ALLOCATIONS_EDIT,
    # Turnos
    ActionType.CREATE_SHIFT: Permission.SHIFTS_CREATE,
    ActionType.REGISTER_CHECKIN: Permission.SHIFTS_CHECKIN,
    ActionType.REGISTER_CHECKOUT: Permission.SHIFTS_CHECKIN,
    ActionType.MARK_ABSENCE: Permission.SHIFTS_MARK_MISSED,
    # Substituições
    ActionType.CREATE_SUBSTITUTION: Permission.SUBSTITUTIONS_CREATE,
    # Notificações (usa permissão de visualizar postos)
    ActionType.SEND_NOTIFICATION: Permission.POSTS_VIEW,
    # Relatórios
    ActionType.GENERATE_REPORT: Permission.REPORTS_VIEW,
}


def get_required_permission(action_type: ActionType) -> Permission:
    """
    Retorna a permissão necessária para executar uma ação.

    Args:
        action_type: Tipo de ação

    Returns:
        Permissão necessária

    Raises:
        ValueError: Se ação não tem permissão mapeada
    """
    permission = ACTION_PERMISSIONS.get(action_type)
    if not permission:
        raise ValueError(f"Ação {action_type.value} não tem permissão mapeada")
    return permission
