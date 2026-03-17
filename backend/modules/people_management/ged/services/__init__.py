"""
Servicos do modulo GED — Gestao Eletronica de Documentos.

Exporta todos os services para uso pelos controllers e tasks.
"""

from modules.people_management.ged.services.client_service import ClientService
from modules.people_management.ged.services.document_collector_service import DocumentCollectorService
from modules.people_management.ged.services.export_service import ExportService
from modules.people_management.ged.services.google_drive_service import GoogleDriveService
from modules.people_management.ged.services.kit_builder_service import KitBuilderService
from modules.people_management.ged.services.kit_service import KitService
from modules.people_management.ged.services.signature_integration_service import SignatureIntegrationService

__all__ = [
    "ClientService",
    "DocumentCollectorService",
    "ExportService",
    "GoogleDriveService",
    "KitBuilderService",
    "KitService",
    "SignatureIntegrationService",
]
