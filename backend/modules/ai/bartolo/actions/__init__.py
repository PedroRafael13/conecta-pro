"""
Sistema de ações executivas do Bartolo.

Permite ao Bartolo executar ações operacionais reais no sistema
após confirmação do usuário.
"""
from .action_types import ActionType, ActionCategory, ActionStatus
from .action_schemas import (
    ActionRequest,
    ActionPreview,
    ActionConfirmation,
    ActionResult,
)
from .action_detector import ActionDetector
from .action_permissions import ACTION_PERMISSIONS, get_required_permission
from .action_executor import ActionExecutor

__all__ = [
    "ActionType",
    "ActionCategory",
    "ActionStatus",
    "ActionRequest",
    "ActionPreview",
    "ActionConfirmation",
    "ActionResult",
    "ActionDetector",
    "ActionExecutor",
    "ACTION_PERMISSIONS",
    "get_required_permission",
]
