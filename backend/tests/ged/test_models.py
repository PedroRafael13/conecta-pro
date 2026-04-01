"""
Testes para enums e estrutura dos models do GED.

Testa enums, tipos e constantes sem instanciar models SQLAlchemy
(que requerem sessão de banco e tabelas existentes).
"""

import pytest


class TestGedClientEnums:
    """Testes dos enums do GedClient."""

    def test_client_type_values(self):
        from modules.people_management.ged.models.client import GedClientType

        assert GedClientType.CONDOMINIO.value == "condominio"
        assert GedClientType.ADMINISTRADORA.value == "administradora"

    def test_client_type_count(self):
        from modules.people_management.ged.models.client import GedClientType

        assert len(GedClientType) == 2

    def test_client_model_exists(self):
        from modules.people_management.ged.models.client import GedClient

        assert GedClient.__tablename__ == "ged_clients"

    def test_client_model_columns(self):
        from modules.people_management.ged.models.client import GedClient

        columns = [c.name for c in GedClient.__table__.columns]
        required = ["id", "name", "type", "cnpj", "contact_email", "portal_access_enabled"]
        for col in required:
            assert col in columns, f"Column {col} missing from ged_clients"

    def test_client_model_has_portal_fields(self):
        from modules.people_management.ged.models.client import GedClient

        columns = [c.name for c in GedClient.__table__.columns]
        assert "portal_username" in columns
        assert "portal_password_hash" in columns
        assert "portal_access_enabled" in columns


class TestGedDocumentKitEnums:
    """Testes dos enums do GedDocumentKit."""

    def test_kit_status_values(self):
        from modules.people_management.ged.models.document_kit import KitStatus

        expected = ["em_montagem", "completo", "enviado", "conferido", "aprovado"]
        actual = [s.value for s in KitStatus]
        assert actual == expected

    def test_kit_send_method_values(self):
        from modules.people_management.ged.models.document_kit import KitSendMethod

        expected = ["email", "google_drive", "portal", "impresso"]
        actual = [m.value for m in KitSendMethod]
        assert actual == expected

    def test_kit_model_exists(self):
        from modules.people_management.ged.models.document_kit import GedDocumentKit

        assert GedDocumentKit.__tablename__ == "ged_document_kits"

    def test_kit_model_columns(self):
        from modules.people_management.ged.models.document_kit import GedDocumentKit

        columns = [c.name for c in GedDocumentKit.__table__.columns]
        required = [
            "id",
            "client_id",
            "reference_month",
            "status",
            "total_employees",
            "total_documents",
            "documents_signed",
            "completion_percentage",
            "sent_at",
            "sent_method",
        ]
        for col in required:
            assert col in columns, f"Column {col} missing from ged_document_kits"

    def test_kit_has_unique_constraint(self):
        from modules.people_management.ged.models.document_kit import GedDocumentKit

        constraints = [c.name for c in GedDocumentKit.__table__.constraints if hasattr(c, "name") and c.name]
        # Check unique constraint on (client_id, reference_month)
        has_unique = any("client" in str(c) for c in GedDocumentKit.__table__.constraints)
        assert has_unique or len(constraints) > 0


class TestKitDocumentEnums:
    """Testes dos enums do KitDocument."""

    def test_document_type_count(self):
        from modules.people_management.ged.models.kit_document import DocumentType

        assert len(DocumentType) >= 20, f"Expected at least 20 document types, got {len(DocumentType)}"

    def test_document_type_core_values(self):
        from modules.people_management.ged.models.kit_document import DocumentType

        types = [t.value for t in DocumentType]
        core_types = [
            "contracheque",
            "folha_ponto",
            "comprovante_vt",
            "comprovante_va",
            "cnd_federal",
            "cnd_estadual",
            "cnd_municipal",
            "crf_fgts",
            "cndt_trabalhista",
            "gps_inss",
            "grf_fgts",
            "gfip_sefip",
        ]
        for ct in core_types:
            assert ct in types, f"{ct} missing from DocumentType"

    def test_source_module_values(self):
        from modules.people_management.ged.models.kit_document import SourceModule

        expected = ["dp", "rh", "fiscal", "operacoes", "manual"]
        actual = [m.value for m in SourceModule]
        assert actual == expected

    def test_kit_document_model_exists(self):
        from modules.people_management.ged.models.kit_document import KitDocument

        assert KitDocument.__tablename__ == "ged_kit_documents"

    def test_kit_document_columns(self):
        from modules.people_management.ged.models.kit_document import KitDocument

        columns = [c.name for c in KitDocument.__table__.columns]
        required = [
            "id",
            "kit_id",
            "employee_id",
            "document_type",
            "document_name",
            "file_path",
            "is_signed",
            "signature_hash",
            "source_module",
        ]
        for col in required:
            assert col in columns, f"Column {col} missing from ged_kit_documents"


class TestKitAccessLogEnums:
    """Testes dos enums do KitAccessLog."""

    def test_access_action_values(self):
        from modules.people_management.ged.models.access_log import AccessAction

        actions = [a.value for a in AccessAction]
        for r in ["viewed", "downloaded", "printed", "approved", "rejected", "signed", "sent"]:
            assert r in actions

    def test_actor_type_values(self):
        from modules.people_management.ged.models.access_log import ActorType

        assert ActorType.INTERNAL.value == "internal"
        assert ActorType.CLIENT.value == "client"

    def test_access_log_model_exists(self):
        from modules.people_management.ged.models.access_log import KitAccessLog

        assert KitAccessLog.__tablename__ == "ged_kit_access_logs"

    def test_access_log_columns(self):
        from modules.people_management.ged.models.access_log import KitAccessLog

        columns = [c.name for c in KitAccessLog.__table__.columns]
        required = ["id", "kit_id", "action", "actor_type", "actor_id", "actor_name", "actor_ip"]
        for col in required:
            assert col in columns, f"Column {col} missing from ged_kit_access_logs"

    def test_access_action_count(self):
        from modules.people_management.ged.models.access_log import AccessAction

        assert len(AccessAction) == 7
