"""
tests/modules/fase5/test_quality_framework.py - Quality Framework Tests
========================================================================
Testes para Quality Framework
"""

import pytest
from decimal import Decimal
from uuid import uuid4

from modules.fase5.quality_framework.validator import (
    QualityValidator,
    QualityReport,
    QualityMetric,
    QualityIssue,
    IssueSeverity
)


class TestQualityValidator:
    """Testes para QualityValidator."""

    def test_criar_validator(self):
        """Deve criar validator."""
        validator = QualityValidator()
        assert validator is not None
        assert hasattr(validator, 'validate')
        assert hasattr(validator, 'get_summary')

    def test_thresholds_definidos(self):
        """Deve ter thresholds definidos."""
        assert QualityValidator.THRESHOLDS is not None
        assert "code_coverage" in QualityValidator.THRESHOLDS
        assert "security" in QualityValidator.THRESHOLDS

    def test_weights_definidos(self):
        """Deve ter weights definidos."""
        assert QualityValidator.WEIGHTS is not None
        assert "code_coverage" in QualityValidator.WEIGHTS
        assert "security" in QualityValidator.WEIGHTS

    def test_get_summary_formato(self):
        """Deve retornar summary no formato correto."""
        validator = QualityValidator()
        report = QualityReport(
            component="test",
            phase="test",
            overall_score=Decimal("95.5"),
            passed=True,
            metrics=[
                QualityMetric(name="coverage", score=Decimal("95")),
                QualityMetric(name="security", score=Decimal("96"))
            ],
            issues=[]
        )
        summary = validator.get_summary(report)

        assert "report_id" in summary
        assert "component" in summary
        assert "overall_score" in summary
        assert "passed" in summary
        assert "metrics" in summary


class TestQualityReport:
    """Testes para modelo QualityReport."""

    def test_criar_report(self):
        """Deve criar report valido."""
        report = QualityReport(
            component="fase5",
            phase="grand_finale",
            overall_score=Decimal("99.5"),
            passed=True,
            metrics=[],
            issues=[]
        )
        assert report.report_id is not None
        assert report.validated_at is not None

    def test_report_passed(self):
        """Report deve passar com score alto."""
        report = QualityReport(
            component="test",
            phase="test",
            overall_score=Decimal("99.5"),
            passed=True,
            metrics=[],
            issues=[]
        )
        assert report.passed is True

    def test_report_failed(self):
        """Report deve falhar com score baixo."""
        report = QualityReport(
            component="test",
            phase="test",
            overall_score=Decimal("50"),
            passed=False,
            metrics=[],
            issues=[]
        )
        assert report.passed is False

    def test_report_critical_issues_count(self):
        """Deve contar issues criticas."""
        report = QualityReport(
            component="test",
            phase="test",
            overall_score=Decimal("80"),
            passed=False,
            metrics=[],
            issues=[
                QualityIssue(code="W001", message="Warning", severity=IssueSeverity.WARNING),
                QualityIssue(code="C001", message="Critical", severity=IssueSeverity.CRITICAL),
                QualityIssue(code="C002", message="Critical 2", severity=IssueSeverity.CRITICAL)
            ]
        )
        assert report.critical_issues_count == 2


class TestQualityMetric:
    """Testes para modelo QualityMetric."""

    def test_criar_metrica(self):
        """Deve criar metrica valida."""
        metric = QualityMetric(
            name="code_coverage",
            score=Decimal("95.5")
        )
        assert metric.name == "code_coverage"
        assert metric.score == Decimal("95.5")

    def test_metrica_peso_padrao(self):
        """Peso padrao deve ser 1."""
        metric = QualityMetric(
            name="test",
            score=Decimal("90")
        )
        assert metric.weight == Decimal("1")

    def test_metrica_passed(self):
        """Deve verificar se passou threshold."""
        metric = QualityMetric(
            name="test",
            score=Decimal("96"),
            threshold=Decimal("95")
        )
        assert metric.passed is True

    def test_metrica_failed(self):
        """Deve verificar se falhou threshold."""
        metric = QualityMetric(
            name="test",
            score=Decimal("90"),
            threshold=Decimal("95")
        )
        assert metric.passed is False


class TestQualityIssue:
    """Testes para modelo QualityIssue."""

    def test_criar_issue(self):
        """Deve criar issue valida."""
        issue = QualityIssue(
            code="SEC001",
            message="Vulnerabilidade detectada",
            severity=IssueSeverity.CRITICAL
        )
        assert issue.code == "SEC001"
        assert issue.severity == IssueSeverity.CRITICAL

    def test_issue_com_localizacao(self):
        """Deve aceitar localizacao."""
        issue = QualityIssue(
            code="COV001",
            message="Funcao sem teste",
            severity=IssueSeverity.WARNING,
            file_path="src/module.py",
            line_number=42
        )
        assert issue.file_path == "src/module.py"
        assert issue.line_number == 42

    def test_issue_com_sugestao(self):
        """Deve aceitar sugestao."""
        issue = QualityIssue(
            code="DOC001",
            message="Docstring ausente",
            severity=IssueSeverity.INFO,
            suggestion="Adicionar docstring"
        )
        assert issue.suggestion is not None


class TestIssueSeverity:
    """Testes para enum IssueSeverity."""

    def test_severidades_disponiveis(self):
        """Deve ter todas as severidades."""
        severities = list(IssueSeverity)
        assert IssueSeverity.INFO in severities
        assert IssueSeverity.WARNING in severities
        assert IssueSeverity.ERROR in severities
        assert IssueSeverity.CRITICAL in severities

    def test_valores_severidade(self):
        """Severidades devem ter valores corretos."""
        assert IssueSeverity.INFO.value == "info"
        assert IssueSeverity.WARNING.value == "warning"
        assert IssueSeverity.ERROR.value == "error"
        assert IssueSeverity.CRITICAL.value == "critical"
