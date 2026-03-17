"""
Testes para services do GED.

Foca em instanciação, chamadas de método e validação de tipos de retorno.
Services que dependem de banco são testados com mocks no nível de repositório.
"""

import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def uid():
    return str(uuid.uuid4())


# ════════════════════════════════════════════
# Service Import Tests
# ════════════════════════════════════════════


class TestServiceImports:
    """Testa que todos os services importam corretamente."""

    def test_import_client_service(self):
        from modules.people_management.ged.services.client_service import ClientService

        assert ClientService is not None

    def test_import_kit_service(self):
        from modules.people_management.ged.services.kit_service import KitService

        assert KitService is not None

    def test_import_kit_builder_service(self):
        from modules.people_management.ged.services.kit_builder_service import KitBuilderService

        assert KitBuilderService is not None

    def test_import_document_collector_service(self):
        from modules.people_management.ged.services.document_collector_service import DocumentCollectorService

        assert DocumentCollectorService is not None

    def test_import_signature_service(self):
        from modules.people_management.ged.services.signature_integration_service import SignatureIntegrationService

        assert SignatureIntegrationService is not None

    def test_import_export_service(self):
        from modules.people_management.ged.services.export_service import ExportService

        assert ExportService is not None

    def test_import_google_drive_service(self):
        from modules.people_management.ged.services.google_drive_service import GoogleDriveService

        assert GoogleDriveService is not None


class TestServiceInstantiation:
    """Testa que todos os services podem ser instanciados."""

    def test_client_service_init(self):
        from modules.people_management.ged.services.client_service import ClientService

        service = ClientService(db=AsyncMock())
        assert service is not None

    def test_kit_service_init(self):
        from modules.people_management.ged.services.kit_service import KitService

        service = KitService(db=AsyncMock())
        assert service is not None

    def test_kit_builder_service_init(self):
        from modules.people_management.ged.services.kit_builder_service import KitBuilderService

        service = KitBuilderService(db=AsyncMock())
        assert service is not None

    def test_document_collector_service_init(self):
        from modules.people_management.ged.services.document_collector_service import DocumentCollectorService

        service = DocumentCollectorService(db=AsyncMock())
        assert service is not None

    def test_signature_service_init(self):
        from modules.people_management.ged.services.signature_integration_service import SignatureIntegrationService

        service = SignatureIntegrationService(db=AsyncMock())
        assert service is not None

    def test_export_service_init(self):
        from modules.people_management.ged.services.export_service import ExportService

        service = ExportService(db=AsyncMock())
        assert service is not None

    def test_google_drive_service_init(self):
        from modules.people_management.ged.services.google_drive_service import GoogleDriveService

        service = GoogleDriveService(db=AsyncMock())
        assert service is not None


class TestServiceMethods:
    """Testa que services possuem os métodos esperados."""

    def test_kit_service_has_crud_methods(self):
        from modules.people_management.ged.services.kit_service import KitService

        service = KitService(db=AsyncMock())
        required_methods = [
            "create_kit",
            "get_kit",
            "list_kits",
            "update_kit",
            "delete_kit",
            "get_kit_summary",
            "get_kits_by_month",
            "recalculate_kit_completion",
            "mark_kit_sent",
            "approve_kit",
        ]
        for method in required_methods:
            assert hasattr(service, method), f"KitService missing method: {method}"

    def test_kit_builder_has_build_methods(self):
        from modules.people_management.ged.services.kit_builder_service import KitBuilderService

        service = KitBuilderService(db=AsyncMock())
        required = [
            "build_kit_for_client",
            "collect_payslips",
            "collect_company_certificates",
            "auto_build_all_kits",
            "get_employees_for_client",
        ]
        for method in required:
            assert hasattr(service, method), f"KitBuilderService missing method: {method}"

    def test_document_collector_has_methods(self):
        from modules.people_management.ged.services.document_collector_service import DocumentCollectorService

        service = DocumentCollectorService(db=AsyncMock())
        required = [
            "collect_from_dp",
            "collect_from_fiscal",
            "collect_from_operations",
            "add_manual_document",
            "remove_document",
            "replace_document",
        ]
        for method in required:
            assert hasattr(service, method), f"DocumentCollectorService missing method: {method}"

    def test_signature_service_has_methods(self):
        from modules.people_management.ged.services.signature_integration_service import SignatureIntegrationService

        service = SignatureIntegrationService(db=AsyncMock())
        required = [
            "request_signature",
            "process_signature",
            "get_pending_signatures",
            "get_signed_documents",
            "verify_signature",
            "bulk_check_signatures",
        ]
        for method in required:
            assert hasattr(service, method), f"SignatureIntegrationService missing method: {method}"

    def test_export_service_has_methods(self):
        from modules.people_management.ged.services.export_service import ExportService

        service = ExportService(db=AsyncMock())
        required = [
            "generate_zip",
            "generate_consolidated_pdf",
            "send_via_email",
            "send_to_portal",
            "get_download_url",
            "log_access",
        ]
        for method in required:
            assert hasattr(service, method), f"ExportService missing method: {method}"

    def test_google_drive_service_has_methods(self):
        from modules.people_management.ged.services.google_drive_service import GoogleDriveService

        service = GoogleDriveService(db=AsyncMock())
        required = ["upload_to_drive", "create_kit_folder", "sync_kit_to_drive", "check_credentials"]
        for method in required:
            assert hasattr(service, method), f"GoogleDriveService missing method: {method}"

    def test_client_service_has_crud_methods(self):
        from modules.people_management.ged.services.client_service import ClientService

        service = ClientService(db=AsyncMock())
        required = [
            "create_client",
            "get_client",
            "list_clients",
            "update_client",
            "delete_client",
        ]
        for method in required:
            assert hasattr(service, method), f"ClientService missing method: {method}"


class TestExportServiceMethods:
    """Testa que ExportService possui métodos obrigatórios."""

    def test_export_service_method_signatures(self):
        import inspect

        from modules.people_management.ged.services.export_service import ExportService

        methods = {
            name
            for name, _ in inspect.getmembers(ExportService, predicate=inspect.isfunction)
            if not name.startswith("_")
        }
        required = {
            "generate_zip",
            "generate_consolidated_pdf",
            "send_via_email",
            "send_to_portal",
            "get_download_url",
            "log_access",
        }
        assert required.issubset(methods)


class TestGoogleDriveServiceAsync:
    """Testa métodos do GoogleDriveService."""

    @pytest.mark.asyncio
    async def test_check_credentials_returns_dict(self):
        from modules.people_management.ged.services.google_drive_service import GoogleDriveService

        service = GoogleDriveService(db=AsyncMock())
        result = await service.check_credentials()
        assert isinstance(result, (dict, bool))


class TestControllerImports:
    """Testa importação dos controllers e contagem de rotas."""

    def test_client_controller_import(self):
        from modules.people_management.ged.controllers.client_controller import router

        assert len(router.routes) >= 4

    def test_kit_controller_import(self):
        from modules.people_management.ged.controllers.kit_controller import router

        assert len(router.routes) >= 6

    def test_document_controller_import(self):
        from modules.people_management.ged.controllers.document_controller import router

        assert len(router.routes) >= 4

    def test_aggregator_total_routes(self):
        from modules.people_management.ged.aggregator import router

        assert len(router.routes) >= 14

    def test_events_handler_import(self):
        from modules.people_management.ged.events.handlers import (
            on_cnd_renewed,
            on_document_signed,
            on_payroll_closed,
        )

        assert callable(on_payroll_closed)
        assert callable(on_cnd_renewed)
        assert callable(on_document_signed)


class TestCeleryTaskImports:
    """Testa importação das tasks Celery."""

    def test_auto_collect_task_import(self):
        from modules.people_management.ged.tasks.auto_collect_task import ged_auto_collect_documents

        assert callable(ged_auto_collect_documents)

    def test_cnd_sync_task_import(self):
        from modules.people_management.ged.tasks.cnd_sync_task import ged_sync_cnds

        assert callable(ged_sync_cnds)
