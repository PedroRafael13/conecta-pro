"""
domains/hr/__init__.py - HR DOMAIN
==================================
Enterprise HR domain with Brazilian labor law compliance
"""

from .entities import (
    # Enums
    EmploymentType,
    EmployeeStatus,
    DepartmentType,
    WorkScheduleType,
    PayrollEventType,
    TimeClockEventType,
    LeaveType,
    TerminationType,
    # Employee
    EmployeeEntity,
    Address,
    BankAccount,
    EmergencyContact,
    Dependent,
    LeaveRecord,
    # Type aliases
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
