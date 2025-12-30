"""
Testes unitários para os services do módulo Facilities.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from modules.facilities.services.inspection_analyzer import (
    InspectionAnalyzerService,
    inspection_analyzer,
)
from modules.facilities.services.maintenance_scheduler import (
    MaintenanceSchedulerService,
    maintenance_scheduler,
)
from modules.facilities.services.request_classifier import (
    RequestClassifierService,
    request_classifier,
)


class TestMaintenanceSchedulerService:
    """Testes para MaintenanceSchedulerService."""

    def test_service_singleton(self):
        """Testa que existe instância singleton."""
        assert maintenance_scheduler is not None
        assert isinstance(maintenance_scheduler, MaintenanceSchedulerService)

    def test_suggest_schedule_preventive(self):
        """Testa sugestão de agendamento para manutenção preventiva."""
        result = maintenance_scheduler.suggest_schedule(
            maintenance_type="preventive",
            equipment_type="elevator",
            last_maintenance=date.today() - timedelta(days=30),
            priority="medium",
        )

        assert "suggested_date" in result
        assert "confidence" in result
        assert "reasoning" in result
        assert result["confidence"] > 0

    def test_suggest_schedule_corrective(self):
        """Testa sugestão de agendamento para manutenção corretiva."""
        result = maintenance_scheduler.suggest_schedule(
            maintenance_type="corrective",
            equipment_type="hvac",
            priority="high",
        )

        assert "suggested_date" in result
        assert result["confidence"] > 0

    def test_suggest_schedule_emergency(self):
        """Testa sugestão de agendamento para emergência."""
        result = maintenance_scheduler.suggest_schedule(
            maintenance_type="emergency",
            equipment_type="electrical",
            priority="critical",
        )

        assert "suggested_date" in result
        # Emergência deve ter data próxima
        suggested = date.fromisoformat(result["suggested_date"])
        assert suggested <= date.today() + timedelta(days=1)

    def test_suggest_schedule_no_last_maintenance(self):
        """Testa sugestão sem data de última manutenção."""
        result = maintenance_scheduler.suggest_schedule(
            maintenance_type="preventive",
            equipment_type="fire_system",
            priority="medium",
        )

        assert "suggested_date" in result
        assert "confidence" in result

    def test_optimize_schedule(self):
        """Testa otimização de agenda."""
        maintenances = [
            {
                "id": "m1",
                "type": "preventive",
                "priority": "medium",
                "estimated_hours": 2.0,
            },
            {
                "id": "m2",
                "type": "corrective",
                "priority": "high",
                "estimated_hours": 3.0,
            },
            {
                "id": "m3",
                "type": "preventive",
                "priority": "low",
                "estimated_hours": 1.0,
            },
        ]
        resources = [
            {"id": "r1", "name": "Técnico A", "available_hours": 8},
            {"id": "r2", "name": "Técnico B", "available_hours": 6},
        ]

        result = maintenance_scheduler.optimize_schedule(
            maintenances=maintenances,
            available_resources=resources,
            start_date=date.today(),
            days_ahead=7,
        )

        assert "schedule" in result
        assert "utilization" in result
        assert len(result["schedule"]) > 0

    def test_predict_next_maintenance(self):
        """Testa previsão de próxima manutenção."""
        history = [
            {"date": "2024-01-15", "type": "preventive", "success": True},
            {"date": "2024-04-15", "type": "preventive", "success": True},
            {"date": "2024-07-15", "type": "preventive", "success": True},
        ]

        result = maintenance_scheduler.predict_next_maintenance(
            equipment_type="elevator",
            maintenance_history=history,
        )

        assert "predicted_date" in result
        assert "predicted_type" in result
        assert "confidence" in result


class TestInspectionAnalyzerService:
    """Testes para InspectionAnalyzerService."""

    def test_service_singleton(self):
        """Testa que existe instância singleton."""
        assert inspection_analyzer is not None
        assert isinstance(inspection_analyzer, InspectionAnalyzerService)

    def test_analyze_inspection_good_score(self):
        """Testa análise de inspeção com boa pontuação."""
        inspection_data = {
            "id": "insp-001",
            "score": 95,
            "items_ok": 18,
            "items_warning": 2,
            "items_critical": 0,
        }
        checklist_items = [
            {"question": "Piso limpo?", "category": "cleaning", "status": "ok"},
            {"question": "Iluminação OK?", "category": "electrical", "status": "ok"},
            {"question": "Extintores?", "category": "safety", "status": "warning"},
        ]

        result = inspection_analyzer.analyze_inspection(
            inspection_data, checklist_items
        )

        assert "overall_assessment" in result
        assert "risk_level" in result
        assert "recommendations" in result
        assert "priority_actions" in result

    def test_analyze_inspection_critical_issues(self):
        """Testa análise de inspeção com problemas críticos."""
        inspection_data = {
            "id": "insp-002",
            "score": 45,
            "items_ok": 5,
            "items_warning": 8,
            "items_critical": 7,
        }
        checklist_items = [
            {"question": "Saída de emergência?", "category": "safety", "status": "critical"},
            {"question": "Alarme de incêndio?", "category": "safety", "status": "critical"},
        ]

        result = inspection_analyzer.analyze_inspection(
            inspection_data, checklist_items
        )

        assert result["risk_level"] in ["high", "critical"]
        assert len(result["priority_actions"]) > 0

    def test_compare_inspections(self):
        """Testa comparação entre inspeções."""
        current = {
            "id": "insp-002",
            "score": 88,
            "items_ok": 16,
            "items_warning": 3,
            "items_critical": 1,
            "date": "2024-10-01",
        }
        previous = {
            "id": "insp-001",
            "score": 92,
            "items_ok": 18,
            "items_warning": 2,
            "items_critical": 0,
            "date": "2024-09-01",
        }

        result = inspection_analyzer.compare_inspections(current, previous)

        assert "score_change" in result
        assert "trend" in result
        assert "improvements" in result
        assert "deteriorations" in result

    def test_predict_issues(self):
        """Testa previsão de problemas."""
        history = [
            {"date": "2024-01-01", "category": "electrical", "count": 2},
            {"date": "2024-02-01", "category": "electrical", "count": 3},
            {"date": "2024-03-01", "category": "electrical", "count": 4},
        ]

        result = inspection_analyzer.predict_issues(history)

        assert "predictions" in result
        assert "high_risk_areas" in result

    def test_generate_report_summary(self):
        """Testa geração de resumo de relatório."""
        inspection = {
            "id": "insp-001",
            "title": "Vistoria Mensal",
            "score": 92,
            "result": "approved",
            "findings": "Pequenos ajustes necessários",
            "recommendations": "Aumentar frequência de limpeza",
        }
        checklist_results = [
            {"category": "cleaning", "ok": 8, "warning": 2, "critical": 0},
            {"category": "safety", "ok": 10, "warning": 0, "critical": 0},
        ]

        result = inspection_analyzer.generate_report_summary(
            inspection, checklist_results
        )

        assert "executive_summary" in result
        assert "key_findings" in result
        assert "action_items" in result


class TestRequestClassifierService:
    """Testes para RequestClassifierService."""

    def test_service_singleton(self):
        """Testa que existe instância singleton."""
        assert request_classifier is not None
        assert isinstance(request_classifier, RequestClassifierService)

    def test_classify_plumbing(self):
        """Testa classificação de solicitação de hidráulica."""
        result = request_classifier.classify(
            title="Vazamento no banheiro",
            description="Está vazando água da torneira da pia",
        )

        assert "category" in result
        assert "priority" in result
        assert "confidence" in result
        assert result["category"] == "plumbing"

    def test_classify_electrical(self):
        """Testa classificação de solicitação elétrica."""
        result = request_classifier.classify(
            title="Tomada queimada",
            description="A tomada da sala está queimada e não funciona",
        )

        assert result["category"] == "electrical"

    def test_classify_security(self):
        """Testa classificação de solicitação de segurança."""
        result = request_classifier.classify(
            title="Câmera com defeito",
            description="A câmera do estacionamento não está funcionando",
        )

        assert result["category"] == "security"

    def test_classify_cleaning(self):
        """Testa classificação de solicitação de limpeza."""
        result = request_classifier.classify(
            title="Limpeza do corredor",
            description="O corredor do 3º andar precisa de limpeza",
        )

        assert result["category"] == "cleaning"

    def test_classify_general(self):
        """Testa classificação de solicitação genérica."""
        result = request_classifier.classify(
            title="Problema no condomínio",
            description="Preciso de ajuda com algo",
        )

        # Solicitação vaga deve ser classificada como "general" ou "other"
        assert result["category"] in ["general", "other"]

    def test_suggest_assignee(self):
        """Testa sugestão de responsável."""
        result = request_classifier.suggest_assignee(
            category="plumbing",
            priority="high",
            area_id="area-001",
        )

        assert "suggested_team" in result
        assert "suggested_skills" in result
        assert "escalation_path" in result

    def test_analyze_sentiment_positive(self):
        """Testa análise de sentimento positivo."""
        result = request_classifier.analyze_sentiment(
            "Obrigado pelo excelente atendimento!"
        )

        assert "sentiment" in result
        assert "score" in result
        assert result["sentiment"] == "positive"

    def test_analyze_sentiment_negative(self):
        """Testa análise de sentimento negativo."""
        result = request_classifier.analyze_sentiment(
            "Estou muito insatisfeito, péssimo atendimento, demora absurda!"
        )

        assert result["sentiment"] == "negative"

    def test_analyze_sentiment_neutral(self):
        """Testa análise de sentimento neutro."""
        result = request_classifier.analyze_sentiment(
            "Solicitação de manutenção para o elevador"
        )

        assert result["sentiment"] == "neutral"


class TestMaintenanceSchedulerEdgeCases:
    """Testes de casos extremos para MaintenanceScheduler."""

    def test_empty_maintenances_list(self):
        """Testa otimização com lista vazia."""
        result = maintenance_scheduler.optimize_schedule(
            maintenances=[],
            available_resources=[{"id": "r1", "available_hours": 8}],
            start_date=date.today(),
            days_ahead=7,
        )

        assert result["schedule"] == []

    def test_empty_resources_list(self):
        """Testa otimização sem recursos."""
        result = maintenance_scheduler.optimize_schedule(
            maintenances=[{"id": "m1", "type": "preventive", "estimated_hours": 2}],
            available_resources=[],
            start_date=date.today(),
            days_ahead=7,
        )

        assert "schedule" in result

    def test_empty_history(self):
        """Testa previsão sem histórico."""
        result = maintenance_scheduler.predict_next_maintenance(
            equipment_type="elevator",
            maintenance_history=[],
        )

        assert "predicted_date" in result


class TestInspectionAnalyzerEdgeCases:
    """Testes de casos extremos para InspectionAnalyzer."""

    def test_analyze_empty_checklist(self):
        """Testa análise sem itens de checklist."""
        inspection_data = {"id": "insp-001", "score": 0}
        result = inspection_analyzer.analyze_inspection(inspection_data, [])

        assert "overall_assessment" in result

    def test_compare_same_inspection(self):
        """Testa comparação de inspeção consigo mesma."""
        inspection = {"id": "insp-001", "score": 90}
        result = inspection_analyzer.compare_inspections(inspection, inspection)

        assert result["score_change"] == 0

    def test_predict_empty_history(self):
        """Testa previsão sem histórico."""
        result = inspection_analyzer.predict_issues([])

        assert "predictions" in result
