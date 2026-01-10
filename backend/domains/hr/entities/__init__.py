"""
domains/hr/entities/__init__.py - ENTITIES
==========================================
"""

from .enums import (
    EmploymentType,
    EmployeeStatus,
    DepartmentType,
    WorkScheduleType,
    PayrollEventType,
    TimeClockEventType,
    LeaveType,
    TerminationType
)
from .employee import (
    EmployeeEntity,
    Address,
    BankAccount,
    EmergencyContact,
    Dependent,
    LeaveRecord,
    EmployeeId,
    DepartmentId,
    PositionId
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
    "PositionId"
]
