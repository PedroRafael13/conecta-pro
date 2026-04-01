"""
Operations Schemas — Re-export dos schemas do modulo operacional.
"""

import contextlib

with contextlib.suppress(ImportError):
    from modules.operacional.schemas.employee import (
        EmployeeCreate,
        EmployeeListResponse,
        EmployeeResponse,
        EmployeeUpdate,
    )

__all__ = [
    "EmployeeCreate",
    "EmployeeUpdate",
    "EmployeeResponse",
    "EmployeeListResponse",
]
