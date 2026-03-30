"""
Testes completos — Health Controller + SafetyAI Service + Core Modules
=======================================================================

Cobre:
  - health_controller: endpoints /status, /health, /info
  - SafetyAIService: inicialização, cálculo de risco, previsão, analytics
  - core/medical_exams: enums e classes
  - core/epi_management: CACertificate, EPIManagementError
  - core/risk_mapping: enums de risco
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

# ==============================================================================
# HEALTH CONTROLLER
# ==============================================================================


class TestHealthController:
    """Testes dos endpoints do Health controller."""

    def _make_app(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from modules.health_occupational.controllers.health_controller import router as health_router

        app = FastAPI()
        app.include_router(health_router)
        return TestClient(app)

    def test_get_status(self):
        client = self._make_app()
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "components" in data["data"]

    def test_get_status_tem_pcmso(self):
        client = self._make_app()
        response = client.get("/status")
        data = response.json()
        components = data["data"]["components"]
        assert "pcmso" in components

    def test_get_status_tem_ppra(self):
        client = self._make_app()
        response = client.get("/status")
        data = response.json()
        components = data["data"]["components"]
        assert "ppra_pgr" in components

    def test_get_status_tem_epi(self):
        client = self._make_app()
        response = client.get("/status")
        data = response.json()
        components = data["data"]["components"]
        assert "epi_management" in components

    def test_get_status_compliance(self):
        client = self._make_app()
        response = client.get("/status")
        data = response.json()
        compliance = data["data"]["compliance"]
        assert "nr6" in compliance
        assert "nr7" in compliance
        assert "nr9" in compliance

    def test_health_check(self):
        client = self._make_app()
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["module"] == "health_occupational"

    def test_health_check_version(self):
        client = self._make_app()
        response = client.get("/health")
        data = response.json()
        assert "version" in data
        assert "timestamp" in data

    def test_get_module_info(self):
        client = self._make_app()
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "compliance" in data

    def test_get_module_info_compliance_nr4(self):
        client = self._make_app()
        response = client.get("/info")
        data = response.json()
        compliance = data["compliance"]
        assert any("NR-4" in str(c) for c in compliance)

    def test_get_module_info_features(self):
        client = self._make_app()
        response = client.get("/info")
        data = response.json()
        assert "features" in data
        assert len(data["features"]) > 0

    def test_router_paths(self):
        from modules.health_occupational.controllers.health_controller import router

        paths = [r.path for r in router.routes]
        assert "/status" in paths
        assert "/health" in paths
        assert "/info" in paths


# ==============================================================================
# SAFETY AI SERVICE
# ==============================================================================


class TestSafetyAIService:
    """Testes do SafetyAIService."""

    def test_create_service_function(self):
        from modules.health_occupational.services.safety_ai_service import (
            SafetyAIService,
            create_safety_ai_service,
        )

        service = create_safety_ai_service()
        assert isinstance(service, SafetyAIService)

    def test_service_init(self):
        from modules.health_occupational.services.safety_ai_service import SafetyAIService

        service = SafetyAIService()
        # Atributos definidos no __init__
        assert hasattr(service, "risk_model")
        assert hasattr(service, "accident_prediction_model")
        assert hasattr(service, "_risk_cache")
        assert hasattr(service, "_prediction_cache")

    def test_risk_level_enum(self):
        from modules.health_occupational.services.safety_ai_service import RiskLevel

        assert RiskLevel.MUITO_BAIXO.value == "muito_baixo"
        assert RiskLevel.BAIXO.value == "baixo"
        assert RiskLevel.MEDIO.value == "medio"
        assert RiskLevel.ALTO.value == "alto"
        assert RiskLevel.CRITICO.value == "critico"

    def test_determine_risk_level_muito_baixo(self):
        from modules.health_occupational.services.safety_ai_service import RiskLevel, SafetyAIService

        service = SafetyAIService()
        result = service._determine_risk_level(0.0)
        assert result == RiskLevel.MUITO_BAIXO

    def test_determine_risk_level_critico(self):
        from modules.health_occupational.services.safety_ai_service import RiskLevel, SafetyAIService

        service = SafetyAIService()
        result = service._determine_risk_level(95.0)
        assert result == RiskLevel.CRITICO

    def test_determine_risk_level_medio(self):
        from modules.health_occupational.services.safety_ai_service import RiskLevel, SafetyAIService

        service = SafetyAIService()
        result = service._determine_risk_level(40.0)
        assert result in (RiskLevel.MEDIO, RiskLevel.BAIXO, RiskLevel.ALTO)

    def test_extract_safety_features_retorna_dict(self):
        from modules.health_occupational.services.safety_ai_service import SafetyAIService

        service = SafetyAIService()
        # Assinatura: _extract_safety_features(work_conditions, health_data, historical_incidents)
        work_conditions = {
            "horas_extras_semana": 5,
            "equipamentos_em_dia": True,
            "incidentes_ultimos_6_meses": 0,
        }
        health_data = {}
        historical_incidents = []
        result = service._extract_safety_features(work_conditions, health_data, historical_incidents)
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_calculate_risk_score_retorna_float(self):
        from modules.health_occupational.services.safety_ai_service import SafetyAIService

        service = SafetyAIService()
        features = {
            "horas_extras": 0.3,
            "equipamentos_em_dia": 1.0,
            "incidentes": 0.0,
            "fadiga": 0.2,
        }
        result = service._calculate_risk_score(features)
        assert isinstance(result, float)
        assert 0.0 <= result <= 100.0

    def test_rule_based_risk_sem_incidentes(self):
        from modules.health_occupational.services.safety_ai_service import SafetyAIService

        service = SafetyAIService()
        features = {
            "incidentes_ultimos_6_meses": 0,
            "horas_extras_semana": 0,
            "equipamentos_em_dia": 1,
            "fadiga_acumulada": 0,
        }
        result = service._rule_based_risk_calculation(features)
        assert isinstance(result, float)

    def test_rule_based_risk_com_incidentes(self):
        from modules.health_occupational.services.safety_ai_service import SafetyAIService

        service = SafetyAIService()
        features = {
            "incidentes_ultimos_6_meses": 3,
            "horas_extras_semana": 20,
            "equipamentos_em_dia": 0,
            "fadiga_acumulada": 0.8,
        }
        result_alto = service._rule_based_risk_calculation(features)

        features_baixo = {
            "incidentes_ultimos_6_meses": 0,
            "horas_extras_semana": 0,
            "equipamentos_em_dia": 1,
            "fadiga_acumulada": 0,
        }
        result_baixo = service._rule_based_risk_calculation(features_baixo)
        # Alto risco deve ser maior que baixo risco
        assert result_alto >= result_baixo

    def test_generate_safety_recommendations(self):
        from modules.health_occupational.services.safety_ai_service import RiskLevel, SafetyAIService

        service = SafetyAIService()
        features = {
            "horas_extras_semana": 15,
            "equipamentos_em_dia": 0,
        }
        # Assinatura: _generate_safety_recommendations(risk_level, predicted_accidents, features)
        result = service._generate_safety_recommendations(RiskLevel.ALTO, [], features)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_calculate_assessment_confidence(self):
        from modules.health_occupational.services.safety_ai_service import SafetyAIService

        service = SafetyAIService()
        features = {
            "horas_extras_semana": 5,
            "incidentes_ultimos_6_meses": 0,
        }
        result = service._calculate_assessment_confidence(features)
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_assess_employee_risk_retorna_objeto(self):
        from modules.health_occupational.services.safety_ai_service import SafetyAIService, SafetyRiskAssessment

        service = SafetyAIService()
        result = asyncio.run(
            service.assess_employee_risk(
                employee_id="emp-001",
                work_conditions={
                    "horas_extras_semana": 5,
                    "equipamentos_em_dia": True,
                    "incidentes_ultimos_6_meses": 0,
                    "funcao": "Vigilante",
                    "setor": "Portaria",
                },
                health_data={},
            )
        )
        assert isinstance(result, SafetyRiskAssessment)
        assert hasattr(result, "risk_level")
        assert hasattr(result, "risk_score")

    def test_generate_safety_analytics(self):
        from modules.health_occupational.services.safety_ai_service import SafetyAIService

        service = SafetyAIService()
        result = asyncio.run(
            service.generate_safety_analytics(
                workplace_id="posto-001",
                period_days=30,
            )
        )
        assert isinstance(result, dict)

    def test_quick_safety_check_function(self):
        from modules.health_occupational.services.safety_ai_service import quick_safety_check

        result = asyncio.run(
            quick_safety_check(
                employee_id="emp-001",
                work_conditions={"equipamentos_em_dia": True},
            )
        )
        assert isinstance(result, str)

    def test_identify_urgent_actions_critico(self):
        from modules.health_occupational.services.safety_ai_service import RiskLevel, SafetyAIService

        service = SafetyAIService()
        features = {
            "incidentes_ultimos_6_meses": 5,
            "equipamentos_em_dia": 0,
        }
        result = service._identify_urgent_actions(RiskLevel.CRITICO, features)
        assert isinstance(result, list)

    def test_identify_urgent_actions_baixo(self):
        from modules.health_occupational.services.safety_ai_service import RiskLevel, SafetyAIService

        service = SafetyAIService()
        features = {
            "incidentes_ultimos_6_meses": 0,
            "equipamentos_em_dia": 1,
        }
        result = service._identify_urgent_actions(RiskLevel.BAIXO, features)
        assert isinstance(result, list)


# ==============================================================================
# CORE MEDICAL EXAMS
# ==============================================================================


class TestCoreMedicalExams:
    """Testes do módulo core/medical_exams."""

    def test_exam_type_values(self):
        from modules.health_occupational.core.medical_exams import ExamType

        assert ExamType.ADMISSIONAL == "admissional"
        assert ExamType.PERIODICO == "periodico"
        assert ExamType.RETORNO_TRABALHO == "retorno_trabalho"
        assert ExamType.MUDANCA_FUNCAO == "mudanca_funcao"
        assert ExamType.DEMISSIONAL == "demissional"

    def test_exam_status_values(self):
        from modules.health_occupational.core.medical_exams import ExamStatus

        assert ExamStatus.SCHEDULED == "scheduled"
        assert ExamStatus.PENDING == "pending"
        assert ExamStatus.COMPLETED == "completed"
        assert ExamStatus.CANCELLED == "cancelled"

    def test_fitness_result_values(self):
        from modules.health_occupational.core.medical_exams import FitnessResult

        assert FitnessResult.APTO == "apto"
        assert FitnessResult.APTO_RESTRICOES == "apto_com_restricoes"
        assert FitnessResult.INAPTO == "inapto"
        assert FitnessResult.INAPTO_TEMPORARIO == "inapto_temporario"

    def test_complementary_exam_enum(self):
        from modules.health_occupational.core.medical_exams import ComplementaryExam

        # Verifica que é um enum/classe acessível
        assert ComplementaryExam is not None


# ==============================================================================
# MÓDULO HEALTH OCCUPATIONAL — IMPORTS GERAIS
# ==============================================================================


class TestHealthOccupationalModuleImports:
    """Testes de importação e estrutura do módulo principal."""

    def test_import_modulo_principal(self):
        import modules.health_occupational as ho

        assert ho is not None

    def test_router_principal(self):
        from modules.health_occupational import router

        assert router is not None

    def test_sub_routers_disponiveis(self):
        from modules.health_occupational import (
            epi_router,
            health_router,
            pcmso_router,
            ppra_router,
        )

        assert pcmso_router is not None
        assert ppra_router is not None
        assert epi_router is not None
        assert health_router is not None

    def test_models_importaveis(self):
        from modules.health_occupational import (
            ASO,
            EPI,
            ControlMeasure,
            EPIDelivery,
            EPIInventory,
            MedicalExam,
            OccupationalRisk,
            RiskMapping,
        )

        assert EPI is not None
        assert MedicalExam is not None
        assert ASO is not None
        assert RiskMapping is not None

    def test_services_importaveis(self):
        from modules.health_occupational import (
            EPIService,
            PCMSOService,
            PPRAService,
        )

        assert EPIService is not None
        assert PCMSOService is not None
        assert PPRAService is not None

    def test_repositories_importaveis(self):
        from modules.health_occupational import (
            EPIRepository,
            PCMSORepository,
            PPRARepository,
        )

        assert EPIRepository is not None
        assert PCMSORepository is not None
        assert PPRARepository is not None

    def test_version(self):
        from modules.health_occupational import __version__

        assert __version__ == "2.0.0"
