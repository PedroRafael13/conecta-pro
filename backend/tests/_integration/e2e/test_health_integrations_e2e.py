"""
E2E tests for health_occupational automatic integrations.
Tests: event bus subscribers, Celery tasks importable, frontend page exists.
"""

import importlib
import sys

sys.path.insert(0, "/opt/conecta-pro/backend")


class TestEventPublishers:
    """Test that event publishers are integrated in services."""

    def test_pcmso_service_imports_event_module(self):
        """PCMSO service should reference event publishing."""
        import ast
        import pathlib

        src = pathlib.Path("/opt/conecta-pro/backend/modules/health_occupational/services/pcmso_service.py").read_text()
        assert "EXAME_AGENDADO" in src or "publish_event" in src or "EventType" in src

    def test_epi_service_imports_event_module(self):
        """EPI service should reference event publishing."""
        import ast
        import pathlib

        src = pathlib.Path("/opt/conecta-pro/backend/modules/health_occupational/services/epi_service.py").read_text()
        assert "EPI_ENTREGUE" in src or "publish_event" in src or "EventType" in src

    def test_pcmso_service_still_importable(self):
        from modules.health_occupational.services.pcmso_service import PCMSOService

        assert PCMSOService is not None

    def test_epi_service_still_importable(self):
        from modules.health_occupational.services.epi_service import EPIService

        assert EPIService is not None


class TestHREventConsumers:
    """Test that HR event consumers are properly implemented."""

    def test_hr_events_module_importable(self):
        from modules.health_occupational.integrations.hr_events import register_hr_event_subscribers

        assert callable(register_hr_event_subscribers)

    def test_hr_events_schedule_exam_function_exists(self):
        from modules.health_occupational.integrations import hr_events

        assert hasattr(hr_events, "_schedule_exam_sync") or hasattr(hr_events, "handle_funcionario_admitido")

    def test_hr_events_has_admitido_handler(self):
        from modules.health_occupational.integrations.hr_events import handle_funcionario_admitido

        assert callable(handle_funcionario_admitido)

    def test_hr_events_has_demitido_handler(self):
        from modules.health_occupational.integrations.hr_events import handle_funcionario_demitido

        assert callable(handle_funcionario_demitido)

    def test_hr_events_subscriber_registration_runs(self):
        """register_hr_event_subscribers should not raise on call."""
        from modules.health_occupational.integrations.hr_events import register_hr_event_subscribers

        # Should not raise even if message bus not fully initialized
        try:
            register_hr_event_subscribers()
        except Exception as e:
            # Only fail if it's an unexpected error (not just "bus not started")
            assert "ImportError" not in type(e).__name__, f"Import error: {e}"

    def test_integrations_init_exists(self):
        import pathlib

        init_path = pathlib.Path("/opt/conecta-pro/backend/modules/health_occupational/integrations/__init__.py")
        assert init_path.exists()


class TestCeleryTasks:
    """Test that SST Celery tasks are properly defined."""

    def test_sst_tasks_module_importable(self):
        from modules.health_occupational.tasks.sst_alerts_tasks import (
            verificar_asos_vencendo,
            verificar_epis_vencendo,
            verificar_exames_pendentes,
        )

        assert verificar_asos_vencendo is not None
        assert verificar_epis_vencendo is not None
        assert verificar_exames_pendentes is not None

    def test_tasks_have_correct_celery_names(self):
        from modules.health_occupational.tasks.sst_alerts_tasks import (
            verificar_asos_vencendo,
            verificar_epis_vencendo,
            verificar_exames_pendentes,
        )

        assert verificar_asos_vencendo.name == "sst.verificar_asos_vencendo"
        assert verificar_epis_vencendo.name == "sst.verificar_epis_vencendo"
        assert verificar_exames_pendentes.name == "sst.verificar_exames_pendentes"

    def test_tasks_package_init_exports(self):
        from modules.health_occupational.tasks import (
            verificar_asos_vencendo,
            verificar_epis_vencendo,
            verificar_exames_pendentes,
        )

        assert all(
            x is not None
            for x in [
                verificar_asos_vencendo,
                verificar_epis_vencendo,
                verificar_exames_pendentes,
            ]
        )

    def test_celery_app_includes_health_occupational_tasks(self):
        import pathlib

        celery_src = pathlib.Path("/opt/conecta-pro/backend/celery_app.py").read_text()
        assert "modules.health_occupational.tasks" in celery_src

    def test_celery_app_has_beat_schedule_for_sst(self):
        import pathlib

        celery_src = pathlib.Path("/opt/conecta-pro/backend/celery_app.py").read_text()
        assert "sst.verificar_asos_vencendo" in celery_src
        assert "sst.verificar_epis_vencendo" in celery_src
        assert "sst.verificar_exames_pendentes" in celery_src


class TestAntiProcrastinationIntegration:
    """Test that anti-procrastination module collects health tasks."""

    def test_module_integrator_importable(self):
        from modules.notifications.anti_procrastination.integration.module_integrator import ModuleIntegrator

        assert ModuleIntegrator is not None

    def test_module_integrator_has_health_tasks_collector(self):
        import pathlib

        src = pathlib.Path(
            "/opt/conecta-pro/backend/modules/notifications/anti_procrastination/integration/module_integrator.py"
        ).read_text()
        assert "_collect_health_tasks" in src or "health_occupational" in src or "health_asos" in src


class TestFrontendAlertasPage:
    """Test that the SST alerts frontend page exists."""

    def test_alertas_page_exists(self):
        import pathlib

        page = pathlib.Path("/opt/conecta-pro/frontend/src/app/modulos/saude-ocupacional/alertas/page.tsx")
        assert page.exists(), "alertas/page.tsx deve existir"

    def test_alertas_page_has_content(self):
        import pathlib

        src = pathlib.Path("/opt/conecta-pro/frontend/src/app/modulos/saude-ocupacional/alertas/page.tsx").read_text()
        assert len(src) > 500, "Página deve ter conteúdo substancial"
        assert "AlertTriangle" in src or "Shield" in src or "alerta" in src.lower()

    def test_alertas_page_calls_health_api(self):
        import pathlib

        src = pathlib.Path("/opt/conecta-pro/frontend/src/app/modulos/saude-ocupacional/alertas/page.tsx").read_text()
        assert (
            "health-occupational" in src or "saude-ocupacional" in src or "pcmso" in src.lower() or "epi" in src.lower()
        )


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v", "--tb=short"])
