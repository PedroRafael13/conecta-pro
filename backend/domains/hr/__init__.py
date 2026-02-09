"""
domains/hr/__init__.py - HR DOMAIN
==================================
Enterprise HR domain with Brazilian labor law compliance
"""

from .entities import (
    Address,
    BankAccount,
    DepartmentId,
    DepartmentType,
    Dependent,
    EmergencyContact,
    # Employee
    EmployeeEntity,
    # Type aliases
    EmployeeId,
    EmployeeStatus,
    # Enums
    EmploymentType,
    LeaveRecord,
    LeaveType,
    PayrollEventType,
    PositionId,
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
