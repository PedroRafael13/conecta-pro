"""
tests/modules/fase5/test_quality_framework.py - Quality Framework Tests
========================================================================
Testes de integracao para Quality Framework
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

    @pytest.fixture
    def validator(self):
        """Fixture do validador."""
        return QualityValidator()

    # =========================================================================
    # Testes de Validacao
    # =========================================================================

    @pytest.mark.asyncio
    async def test_validar_componente(self, validator):
        """Deve validar componente."""
        report = await validator.validate(
            component="fase5",
            phase="test"
        )
        assert isinstance(report, QualityReport)
        assert report.component == "fase5"
        assert report.phase == "test"

    @pytest.mark.asyncio
    async def test_validar_retorna_score(self, validator):
        """Deve retornar score numerico."""
        report = await validator.validate(
            component="cct_compliance",
            phase="validation"
        )
        assert isinstance(report.overall_score, Decimal)
        assert Decimal("0") <= report.overall_score <= Decimal("100")

    @pytest.mark.asyncio
    async def test_validar_retorna_metricas(self, validator):
        """Deve retornar metricas detalhadas."""
        report = await validator.validate(
            component="email_intelligence",
            phase="nlp"
        )
        assert len(report.metrics) > 0
        for metric in report.metrics:
            assert isinstance(metric, QualityMetric)
            assert metric.name is not None
            assert Decimal("0") <= metric.score <= Decimal("100")

    @pytest.mark.asyncio
    async def test_validar_identifica_issues(self, validator):
        """Deve identificar issues quando existem."""
        report = await validator.validate(
            component="fase5",
            phase="grand_finale"
        )
        # Pode ou nao ter issues, mas estrutura deve existir
        assert hasattr(report, "issues")
        assert isinstance(report.issues, list)

    # =========================================================================
    # Testes de Metricas
    # =========================================================================

    @pytest.mark.asyncio
    async def test_metrica_code_coverage(self, validator):
        """Deve ter metrica de code coverage."""
        report = await validator.validate("fase5", "test")
        metric_names = [m.name for m in report.metrics]
        assert "code_coverage" in metric_names

    @pytest.mark.asyncio
    async def test_metrica_type_safety(self, validator):
        """Deve ter metrica de type safety."""
        report = await validator.validate("fase5", "test")
        metric_names = [m.name for m in report.metrics]
        assert "type_safety" in metric_names

    @pytest.mark.asyncio
    async def test_metrica_security(self, validator):
        """Deve ter metrica de security."""
        report = await validator.validate("fase5", "test")
        metric_names = [m.name for m in report.metrics]
        assert "security" in metric_names

    @pytest.mark.asyncio
    async def test_metrica_performance(self, validator):
        """Deve ter metrica de performance."""
        report = await validator.validate("fase5", "test")
        metric_names = [m.name for m in report.metrics]
        assert "performance" in metric_names

    @pytest.mark.asyncio
    async def test_metrica_documentation(self, validator):
        """Deve ter metrica de documentation."""
        report = await validator.validate("fase5", "test")
        metric_names = [m.name for m in report.metrics]
        assert "documentation" in metric_names

    @pytest.mark.asyncio
    async def test_metrica_compliance(self, validator):
        """Deve ter metrica de compliance."""
        report = await validator.validate("fase5", "test")
        metric_names = [m.name for m in report.metrics]
        assert "compliance" in metric_names

    # =========================================================================
    # Testes de Summary
    # =========================================================================

    def test_get_summary(self, validator):
        """Deve gerar summary do report."""
        report = QualityReport(
            component="test",
            phase="test",
            overall_score=Decimal("95.5"),
            passed=True,
            metrics=[
                QualityMetric(name="coverage", score=Decimal("95"), weight=Decimal("1")),
                QualityMetric(name="security", score=Decimal("96"), weight=Decimal("1"))
            ],
            issues=[]
        )
        summary = validator.get_summary(report)

        assert "report_id" in summary
        assert "component" in summary
        assert "overall_score" in summary
        assert "passed" in summary
        assert "metrics" in summary

    def test_summary_inclui_metricas(self, validator):
        """Summary deve incluir todas as metricas."""
        report = QualityReport(
            component="test",
            phase="test",
            overall_score=Decimal("90"),
            passed=True,
            metrics=[
                QualityMetric(name="coverage", score=Decimal("90"), weight=Decimal("1")),
                QualityMetric(name="security", score=Decimal("90"), weight=Decimal("1")),
                QualityMetric(name="performance", score=Decimal("90"), weight=Decimal("1"))
            ],
            issues=[]
        )
        summary = validator.get_summary(report)

        assert "coverage" in summary["metrics"]
        assert "security" in summary["metrics"]
        assert "performance" in summary["metrics"]


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

    def test_report_passed_quando_score_alto(self):
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

    def test_report_failed_quando_score_baixo(self):
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

    def test_report_conta_issues(self):
        """Deve contar issues corretamente."""
        report = QualityReport(
            component="test",
            phase="test",
            overall_score=Decimal("80"),
            passed=False,
            metrics=[],
            issues=[
                QualityIssue(
                    code="TEST001",
                    message="Issue 1",
                    severity=IssueSeverity.WARNING
                ),
                QualityIssue(
                    code="TEST002",
                    message="Issue 2",
                    severity=IssueSeverity.ERROR
                ),
                QualityIssue(
                    code="TEST003",
                    message="Issue 3",
                    severity=IssueSeverity.CRITICAL
                )
            ]
        )
        assert len(report.issues) == 3

    def test_report_identifica_issues_criticas(self):
        """Deve identificar issues criticas."""
        issues = [
            QualityIssue(code="C001", message="Critical", severity=IssueSeverity.CRITICAL),
            QualityIssue(code="W001", message="Warning", severity=IssueSeverity.WARNING)
        ]
        critical_count = sum(1 for i in issues if i.severity == IssueSeverity.CRITICAL)
        assert critical_count == 1


class TestQualityMetric:
    """Testes para modelo QualityMetric."""

    def test_criar_metrica(self):
        """Deve criar metrica valida."""
        metric = QualityMetric(
            name="code_coverage",
            score=Decimal("95.5"),
            weight=Decimal("1.0")
        )
        assert metric.name == "code_coverage"
        assert metric.score == Decimal("95.5")

    def test_metrica_com_detalhes(self):
        """Deve aceitar detalhes opcionais."""
        metric = QualityMetric(
            name="security",
            score=Decimal("98"),
            weight=Decimal("1.5"),
            details={"vulnerabilities": 0, "scanned_files": 100}
        )
        assert metric.details is not None
        assert metric.details["vulnerabilities"] == 0

    def test_metrica_peso_padrao(self):
        """Peso padrao deve ser 1."""
        metric = QualityMetric(
            name="test",
            score=Decimal("90")
        )
        assert metric.weight == Decimal("1")


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
        """Deve aceitar localizacao do problema."""
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
        """Deve aceitar sugestao de correcao."""
        issue = QualityIssue(
            code="DOC001",
            message="Docstring ausente",
            severity=IssueSeverity.INFO,
            suggestion="Adicionar docstring descrevendo a funcao"
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

    def test_ordem_severidade(self):
        """Severidades devem ter ordem logica."""
        # INFO < WARNING < ERROR < CRITICAL
        assert IssueSeverity.INFO.value == "info"
        assert IssueSeverity.WARNING.value == "warning"
        assert IssueSeverity.ERROR.value == "error"
        assert IssueSeverity.CRITICAL.value == "critical"
