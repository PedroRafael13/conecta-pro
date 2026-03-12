"""
Employee Portal Controllers — Routers do portal do funcionario.
"""

from .my_data_controller import router as my_data_router
from .my_documents_controller import router as my_documents_router
from .my_payslips_controller import router as my_payslips_router
from .my_schedules_controller import router as my_schedules_router
from .portal_controller import router as portal_auth_router

__all__ = [
    "portal_auth_router",
    "my_schedules_router",
    "my_payslips_router",
    "my_documents_router",
    "my_data_router",
]
