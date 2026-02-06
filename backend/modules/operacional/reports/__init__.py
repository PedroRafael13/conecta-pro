"""
Module: reports
Description: Modulo de Relatorios Operacionais Avancados
Author: Conecta PRO Team
Date: 2026-01-18

Este modulo fornece:
- Relatorio de Cobertura Operacional
- Relatorio de Horas Extras
- Relatorio de Ocorrencias
- Relatorio de Substituicoes
- Relatorio Disciplinar
- Relatorio de Performance
- Relatorio para Cliente
- Geracao de PDF/Excel/CSV
"""

from .services import (
    # Coverage Report
    CoverageReportService,
    CoverageReport,
    PostCoverage,
    EmployeeCoverage,
    # Overtime Report
    OvertimeReportService,
    OvertimeReport,
    EmployeeOvertime,
    ClientOvertime,
    # Disciplinary Report
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

__version__ = "1.0.0"
