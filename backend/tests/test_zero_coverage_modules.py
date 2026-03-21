"""
Testes de importacao e schemas para modulos com 0% de cobertura.

Cobre: campo, retention, bidding, automation, health_occupational,
       security_lgpd, scheduler, reimbursement.

Esses testes exercitam imports (que carregam models, schemas, enums)
e validam que os modulos sao importaveis sem erros.
"""

import importlib

import pytest

# =============================================================================
# Modulos com 0% de cobertura — import tests
# =============================================================================

ZERO_COVERAGE_MODULES = [
    "modules.campo",
    "modules.retention",
    "modules.bidding",
    "modules.automation",
    "modules.health_occupational",
    "modules.security_lgpd",
    "modules.scheduler",
    "modules.reimbursement",
]


@pytest.mark.parametrize("module_path", ZERO_COVERAGE_MODULES)
def test_module_importable(module_path):
    """Cada modulo deve ser importavel sem erros."""
    mod = importlib.import_module(module_path)
    assert mod is not None


# =============================================================================
# CAMPO — models, schemas, controllers
# =============================================================================


class TestCampoModule:
    def test_import_models(self):
        from modules.campo.models import checklist, ordem_servico, visita

        assert ordem_servico is not None
        assert visita is not None
        assert checklist is not None

    def test_import_schemas(self):
        from modules.campo.schemas import (
            checklist,
            ordem_servico,
            visita,
        )

        assert ordem_servico is not None

    def test_import_controllers(self):
        from modules.campo.controllers import (
            campo_service_controller,
            ordem_servico_controller,
            visita_controller,
        )

        assert campo_service_controller.router is not None

    def test_import_services(self):
        from modules.campo.services import estoque_integration

        assert estoque_integration is not None


# =============================================================================
# BIDDING — models, schemas
# =============================================================================


class TestBiddingModule:
    def test_import_models(self):
        from modules.bidding import models

        assert models is not None

    def test_import_schemas(self):
        from modules.bidding import schemas

        assert schemas is not None

    def test_import_services(self):
        from modules.bidding.services import opportunity_service, sync_service

        assert opportunity_service is not None
        assert sync_service is not None

    def test_import_controllers(self):
        from modules.bidding import (
            agent_router,
            contract_router,
            document_router,
        )

        assert agent_router is not None


# =============================================================================
# RETENTION — models, schemas
# =============================================================================


class TestRetentionModule:
    def test_import_climate(self):
        from modules.retention.climate.services import climate_service

        assert climate_service is not None

    def test_import_turnover(self):
        from modules.retention.turnover.controllers import turnover_controller

        assert turnover_controller is not None


# =============================================================================
# AUTOMATION — workflow
# =============================================================================


class TestAutomationModule:
    def test_import_workflow(self):
        from modules.automation.workflow import controllers

        assert controllers is not None


# =============================================================================
# HEALTH OCCUPATIONAL — models, schemas
# =============================================================================


class TestHealthOccupationalModule:
    def test_import_module(self):
        from modules import health_occupational

        assert health_occupational is not None

    def test_import_controllers(self):
        from modules.health_occupational import controllers

        assert controllers is not None


# =============================================================================
# SECURITY LGPD — models, schemas, controllers
# =============================================================================


class TestSecurityLgpdModule:
    def test_import_module(self):
        from modules import security_lgpd

        assert security_lgpd is not None

    def test_import_controllers(self):
        from modules.security_lgpd import controllers

        assert controllers is not None


# =============================================================================
# SCHEDULER — models, schemas
# =============================================================================


class TestSchedulerModule:
    def test_import_module(self):
        from modules import scheduler

        assert scheduler is not None


# =============================================================================
# REIMBURSEMENT — models, schemas
# =============================================================================


class TestReimbursementModule:
    def test_import_module(self):
        from modules import reimbursement

        assert reimbursement is not None

    def test_import_controllers(self):
        from modules.reimbursement import controllers

        assert controllers is not None
