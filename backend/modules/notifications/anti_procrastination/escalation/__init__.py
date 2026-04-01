"""Sistema de Escalation Automático."""

from .escalation_controller import router  # noqa: F401
from .escalation_engine import EscalationEngine

__all__ = ["EscalationEngine", "router"]
