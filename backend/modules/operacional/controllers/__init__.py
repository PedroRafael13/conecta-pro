"""Controllers do módulo Operations - Postos e Escalas."""

from .allocation_controller import router as allocation_router
from .employee_controller import router as employee_router
# occurrence_controller foi movido para occurrences/controllers/
from .post_controller import router as post_router
from .scale_controller import router as scale_router
from .shift_controller import router as shift_router
from .substitution_controller import router as substitution_router
from .time_bank_controller import router as time_bank_router
from .dashboard_controller import router as dashboard_router
from .reports_controller import router as reports_router

__all__ = [
    "post_router",
    "scale_router",
    "shift_router",
    "allocation_router",
    "employee_router",
    # "occurrence_router",  # movido para occurrences/controllers/
    "substitution_router",
    "time_bank_router",
    "dashboard_router",
    "reports_router",
]
