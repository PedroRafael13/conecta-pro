"""
Testes para schemas Pydantic do GED.

Cobertura: Client, Kit, Document schemas
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError


def uid():
    return str(uuid.uuid4())


class TestGedClientSchemas:
    """Testes dos schemas de GedClient."""

    def test_client_create_valid(self):
        from modules.people_management.ged.models.client import GedClientType
        from modules.people_management.ged.schemas.client import GedClientCreate

        data = GedClientCreate(
            name="Villa dei Fiore",
            type=GedClientType.CONDOMINIO,
            cnpj="12.345.678/0001-90",
            contact_name="Joao",
        )
        assert data.name == "Villa dei Fiore"

    def test_client_create_without_cnpj(self):
        from modules.people_management.ged.schemas.client import GedClientCreate

        data = GedClientCreate(name="Cond Sem CNPJ")
        assert data.cnpj is None

    def test_client_create_min_name_length(self):
        from modules.people_management.ged.schemas.client import GedClientCreate

        with pytest.raises(ValidationError):
            GedClientCreate(name="A")  # min 2 chars

    def test_client_response_format(self):
        from modules.people_management.ged.schemas.client import GedClientResponse

        data = GedClientResponse(
            id=uid(),
            name="Villa",
            type="condominio",
            cnpj="12.345.678/0001-90",
            portal_access_enabled=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert data.portal_access_enabled is True

    def test_client_update_partial(self):
        from modules.people_management.ged.schemas.client import GedClientUpdate

        data = GedClientUpdate(name="Novo Nome")
        assert data.name == "Novo Nome"


class TestKitSchemas:
    """Testes dos schemas de GedDocumentKit."""

    def test_kit_create_valid(self):
        from modules.people_management.ged.schemas.kit import KitCreate

        data = KitCreate(client_id=uid(), reference_month=date(2026, 3, 1), notes="Kit marco")
        assert data.reference_month == date(2026, 3, 1)

    def test_kit_create_without_notes(self):
        from modules.people_management.ged.schemas.kit import KitCreate

        data = KitCreate(client_id=uid(), reference_month=date(2026, 3, 1))
        assert data.notes is None

    def test_kit_status_update(self):
        from modules.people_management.ged.schemas.kit import KitStatusUpdate

        data = KitStatusUpdate(status="enviado", sent_method="email", sent_to="admin@cond.com")
        assert data.status == "enviado"

    def test_kit_response_format(self):
        from modules.people_management.ged.schemas.kit import KitResponse

        data = KitResponse(
            id=uid(),
            client_id=uid(),
            reference_month=date(2026, 3, 1),
            status="em_montagem",
            total_employees=5,
            total_documents=25,
            documents_signed=10,
            completion_percentage=Decimal("40.00"),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert data.completion_percentage == Decimal("40.00")

    def test_kit_summary_format(self):
        from modules.people_management.ged.schemas.kit import KitSummary

        data = KitSummary(
            total_kits=10,
            by_status=[
                {"status": "em_montagem", "count": 3},
                {"status": "completo", "count": 2},
                {"status": "enviado", "count": 5},
            ],
            total_clients=5,
            kits_pending_send=3,
            kits_pending_approval=2,
            average_completion=Decimal("65.0"),
        )
        assert data.total_kits == 10


class TestDocumentSchemas:
    """Testes dos schemas de KitDocument."""

    def test_document_create_employee_doc(self):
        from modules.people_management.ged.schemas.document import DocumentCreate

        data = DocumentCreate(
            kit_id=uid(),
            employee_id=uid(),
            document_type="contracheque",
            document_name="Contracheque.pdf",
        )
        assert data.document_type == "contracheque"

    def test_document_create_company_doc(self):
        from modules.people_management.ged.schemas.document import DocumentCreate

        data = DocumentCreate(
            kit_id=uid(),
            document_type="cnd_federal",
            document_name="CND.pdf",
        )
        assert data.employee_id is None

    def test_document_response_format(self):
        from modules.people_management.ged.schemas.document import DocumentResponse

        data = DocumentResponse(
            id=uid(),
            kit_id=uid(),
            document_type="contracheque",
            document_name="Contracheque.pdf",
            is_signed=True,
            signed_at=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert data.is_signed is True

    def test_document_signature_request(self):
        from modules.people_management.ged.schemas.document import DocumentSignatureRequest

        data = DocumentSignatureRequest(signer_id=uid(), signature_hash="a" * 64)
        assert len(data.signature_hash) == 64

    def test_document_create_with_file_info(self):
        from modules.people_management.ged.schemas.document import DocumentCreate

        data = DocumentCreate(
            kit_id=uid(),
            document_type="outro",
            document_name="manual.pdf",
            file_path="/uploads/manual.pdf",
            file_size_bytes=50000,
            mime_type="application/pdf",
        )
        assert data.file_size_bytes == 50000
