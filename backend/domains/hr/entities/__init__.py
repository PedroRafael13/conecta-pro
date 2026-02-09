"""
domains/hr/entities/__init__.py - ENTITIES
==========================================
"""

from .employee import (
    Address,
    BankAccount,
    DepartmentId,
    Dependent,
    EmergencyContact,
    EmployeeEntity,
    EmployeeId,
    LeaveRecord,
    PositionId,
)
from .enums import (
    DepartmentType,
    EmployeeStatus,
    EmploymentType,
    LeaveType,
    PayrollEventType,
    TerminationType,
    TimeClockEventType,
    WorkScheduleType,
)

__all__ = [
    # Enums
    "EmploymentType",
    "EmployeeStatus",
    "DepartmentType",
    "WorkScheduleType",
    "PayrollEventType",
    "TimeClockEventType",
    "LeaveType",
    "TerminationType",
    # Employee
    "EmployeeEntity",
    "Address",
    "BankAccount",
    "EmergencyContact",
    "Dependent",
    "LeaveRecord",
    # Type aliases
    "EmployeeId",
    "DepartmentId",
    "PositionId",
]
