"""
Sistema de ações executivas do Bartolo.

Permite ao Bartolo executar ações operacionais reais no sistema
após confirmação do usuário.
"""

from .action_detector import ActionDetector
from .action_executor import ActionExecutor
from .action_permissions import ACTION_PERMISSIONS, get_required_permission
from .action_schemas import (
    ActionConfirmation,
    ActionPreview,
    ActionRequest,
    ActionResult,
)
from .action_types import ActionCategory, ActionStatus, ActionType
from .enhanced_action_detector import EnhancedActionDetector

__all__ = [
    "ActionType",
    "ActionCategory",
    "ActionStatus",
    "ActionRequest",
    "ActionPreview",
    "ActionConfirmation",
    "ActionResult",
    "ActionDetector",
    "EnhancedActionDetector",
    "ActionExecutor",
    "ACTION_PERMISSIONS",
    "get_required_permission",
]
