"""
Operations Controllers — Re-export dos controllers do modulo operacional.
"""

import contextlib

with contextlib.suppress(ImportError):
    from modules.operacional.controllers import (
        allocation_router,
        dashboard_router,
        employee_router,
        post_router,
        scale_router,
        scale_template_router,
        shift_router,
        substitution_router,
        time_bank_router,
    )

__all__ = [
    "post_router",
    "scale_router",
    "scale_template_router",
    "shift_router",
    "allocation_router",
    "substitution_router",
    "time_bank_router",
    "dashboard_router",
    "employee_router",
]
