"""
modules/fase5/quality_framework/__init__.py - Quality Framework
==============================================================
Framework de validacao de qualidade 99+/100
"""

from .validator import IssueSeverity, QualityIssue, QualityMetric, QualityReport, QualityValidator

__all__ = ["QualityValidator", "QualityMetric", "QualityReport", "QualityIssue", "IssueSeverity"]
