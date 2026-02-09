"""Relatórios Departamentais de Pendências."""

from .report_controller import router  # noqa: F401
from .report_generator import DepartmentReportGenerator

__all__ = ["DepartmentReportGenerator", "router"]
