"""Sistema de Checklist Diário."""

from .checklist_controller import router  # noqa: F401
from .checklist_manager import ChecklistManager

__all__ = ["ChecklistManager", "router"]
