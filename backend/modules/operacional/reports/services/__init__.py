"""
Services de Relatorios Operacionais.

Author: Conecta PRO Team
Date: 2026-01-18
"""

from .coverage_report import (
    CoverageReportService,
    CoverageReport,
    PostCoverage,
    EmployeeCoverage,
)
from .overtime_report import (
    OvertimeReportService,
    OvertimeReport,
    EmployeeOvertime,
    ClientOvertime,
)
from .disciplinary_report import (
    DisciplinaryReportService,
    DisciplinaryReport,
    DisciplinaryStats,
    EmployeeDisciplinary,
    ReasonBreakdown,
)

__all__ = [
    # Coverage Report
    "CoverageReportService",
    "CoverageReport",
    "PostCoverage",
    "EmployeeCoverage",
    # Overtime Report
    "OvertimeReportService",
    "OvertimeReport",
    "EmployeeOvertime",
    "ClientOvertime",
    # Disciplinary Report
    "DisciplinaryReportService",
    "DisciplinaryReport",
    "DisciplinaryStats",
    "EmployeeDisciplinary",
    "ReasonBreakdown",
]
