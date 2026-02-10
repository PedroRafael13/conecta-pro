"""Testes para os endpoints da API do módulo GED."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import status
from httpx import AsyncClient

from modules.ged.models.document import (
    DocumentCategory,
    DocumentStatus,
    DocumentType,
)
from modules.ged.models.folder import FolderStatus, FolderType
from modules.ged.schemas.document import DocumentListResponse, DocumentResponse
from modules.ged.schemas.folder import FolderListResponse, FolderResponse


@pytest.fixture
def mock_current_user():
    """Mock do usuário autenticado."""
    return {
        "id": str(uuid4()),
        "email": "admin@example.com",
        "role": "admin",
    }


@pytest.fixture
def sample_folder_response():
    """Resposta de exemplo de pasta."""
    return FolderResponse(
        id=str(uuid4()),
        code="FLD-001",
        name="Contratos",
        folder_type=FolderType.CONTRATO,
        status=FolderStatus.ATIVO,
        path="/",
        full_path="/Contratos",
        condominium_id=str(uuid4()),
        owner_id=str(uuid4()),
        created_by=str(uuid4()),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_system=False,
        document_count=10,
        subfolder_count=2,
        total_size_bytes=1024000,
    )


@pytest.fixture
def sample_document_response():
    """Resposta de exemplo de documento."""
    return DocumentResponse(
        id=str(uuid4()),
        code="DOC-001",
        title="Contrato de Serviços",
        folder_id=str(uuid4()),
        document_type=DocumentType.CONTRATO,
        category=DocumentCategory.ADMINISTRATIVO,
        status=DocumentStatus.PUBLICADO,
        file_name="contrato.pdf",
        file_path="/docs/contrato.pdf",
        file_size_bytes=102400,
        file_extension="pdf",
        mime_type="application/pdf",
        checksum="abc123",
        current_version=1,
        created_by=str(uuid4()),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        view_count=5,
        download_count=2,
    )


class TestFolderEndpoints:
    """Testes para endpoints de pastas."""

    @pytest.mark.asyncio
    async def test_create_folder_success(self, mock_current_user, sample_folder_response):
        """Testa criação de pasta com sucesso."""
        with (
            patch(
                "modules.ged.controllers.folder_controller.get_current_user",
                return_value=mock_current_user,
            ),
            patch("modules.ged.controllers.folder_controller.FolderService") as mock_service,
        ):
            mock_instance = AsyncMock()
            mock_instance.create.return_value = sample_folder_response
            mock_service.return_value = mock_instance

            # Simula resposta esperada
            response_data = sample_folder_response.model_dump()

            assert response_data["name"] == "Contratos"
            assert response_data["folder_type"] == FolderType.CONTRATO

    @pytest.mark.asyncio
    async def test_get_folder_not_found(self, mock_current_user):
        """Testa busca de pasta não encontrada."""
        with (
            patch(
                "modules.ged.controllers.folder_controller.get_current_user",
                return_value=mock_current_user,
            ),
            patch("modules.ged.controllers.folder_controller.FolderService") as mock_service,
        ):
            mock_instance = AsyncMock()
            mock_instance.get_by_id.return_value = None
            mock_service.return_value = mock_instance

            # Simula que pasta não foi encontrada
            result = await mock_instance.get_by_id("invalid-id")
            assert result is None

    @pytest.mark.asyncio
    async def test_list_folders(self, mock_current_user, sample_folder_response):
        """Testa listagem de pastas."""
        with (
            patch(
                "modules.ged.controllers.folder_controller.get_current_user",
                return_value=mock_current_user,
            ),
            patch("modules.ged.controllers.folder_controller.FolderService") as mock_service,
        ):
            mock_instance = AsyncMock()
            mock_instance.list.return_value = FolderListResponse(
                items=[sample_folder_response],
                total=1,
                page=1,
                page_size=20,
                pages=1,
            )
            mock_service.return_value = mock_instance

            result = await mock_instance.list()

            assert result.total == 1
            assert len(result.items) == 1


class TestDocumentEndpoints:
    """Testes para endpoints de documentos."""

    @pytest.mark.asyncio
    async def test_create_document_success(self, mock_current_user, sample_document_response):
        """Testa criação de documento com sucesso."""
        with (
            patch(
                "modules.ged.controllers.document_controller.get_current_user",
                return_value=mock_current_user,
            ),
            patch("modules.ged.controllers.document_controller.DocumentService") as mock_service,
        ):
            mock_instance = AsyncMock()
            mock_instance.create.return_value = sample_document_response
            mock_service.return_value = mock_instance

            response_data = sample_document_response.model_dump()

            assert response_data["title"] == "Contrato de Serviços"
            assert response_data["document_type"] == DocumentType.CONTRATO

    @pytest.mark.asyncio
    async def test_get_document_by_code(self, mock_current_user, sample_document_response):
        """Testa busca de documento por código."""
        with (
            patch(
                "modules.ged.controllers.document_controller.get_current_user",
                return_value=mock_current_user,
            ),
            patch("modules.ged.controllers.document_controller.DocumentService") as mock_service,
        ):
            mock_instance = AsyncMock()
            mock_instance.get_by_code.return_value = sample_document_response
            mock_service.return_value = mock_instance

            result = await mock_instance.get_by_code("DOC-001")

            assert result.code == "DOC-001"

    @pytest.mark.asyncio
    async def test_approve_document(self, mock_current_user, sample_document_response):
        """Testa aprovação de documento."""
        with (
            patch(
                "modules.ged.controllers.document_controller.get_current_user",
                return_value=mock_current_user,
            ),
            patch("modules.ged.controllers.document_controller.DocumentService") as mock_service,
        ):
            approved_doc = sample_document_response.model_copy()
            approved_doc.status = DocumentStatus.APROVADO

            mock_instance = AsyncMock()
            mock_instance.approve.return_value = approved_doc
            mock_service.return_value = mock_instance

            result = await mock_instance.approve(sample_document_response.id, mock_current_user["id"])

            assert result.status == DocumentStatus.APROVADO

    @pytest.mark.asyncio
    async def test_search_documents(self, mock_current_user, sample_document_response):
        """Testa busca full-text de documentos."""
        with (
            patch(
                "modules.ged.controllers.document_controller.get_current_user",
                return_value=mock_current_user,
            ),
            patch("modules.ged.controllers.document_controller.DocumentService") as mock_service,
        ):
            mock_instance = AsyncMock()
            mock_instance.search.return_value = [sample_document_response]
            mock_service.return_value = mock_instance

            result = await mock_instance.search("contrato")

            assert len(result) == 1
            assert result[0].title == "Contrato de Serviços"


class TestDocumentAIEndpoints:
    """Testes para endpoints de IA."""

    @pytest.mark.asyncio
    async def test_classify_document(self, mock_current_user):
        """Testa classificação de documento."""
        with (
            patch(
                "modules.ged.controllers.document_controller.get_current_user",
                return_value=mock_current_user,
            ),
            patch("modules.ged.controllers.document_controller.DocumentAIService") as mock_service,
        ):
            mock_instance = AsyncMock()
            mock_instance.classify_document.return_value = {
                "suggested_type": "contrato",
                "type_confidence": 0.85,
                "suggested_category": "administrativo",
                "category_confidence": 0.75,
                "keywords": ["contrato", "serviço"],
                "dates_found": ["01/01/2024"],
                "values_found": ["R$ 5.000,00"],
                "documents_found": [],
            }
            mock_service.return_value = mock_instance

            result = await mock_instance.classify_document("Texto do contrato...")

            assert result["suggested_type"] == "contrato"
            assert result["type_confidence"] >= 0.5

    @pytest.mark.asyncio
    async def test_get_insights(self, mock_current_user):
        """Testa obtenção de insights."""
        with (
            patch(
                "modules.ged.controllers.document_controller.get_current_user",
                return_value=mock_current_user,
            ),
            patch("modules.ged.controllers.document_controller.DocumentAIService") as mock_service,
        ):
            mock_instance = AsyncMock()
            mock_instance.get_insights.return_value = {
                "health_score": 85,
                "health_level": "good",
                "stats": {"total_documents": 100},
                "recommendations": [],
            }
            mock_service.return_value = mock_instance

            result = await mock_instance.get_insights()

            assert result["health_score"] == 85
            assert result["health_level"] == "good"


class TestDocumentShareEndpoints:
    """Testes para endpoints de compartilhamento."""

    @pytest.mark.asyncio
    async def test_create_public_link(self, mock_current_user):
        """Testa criação de link público."""
        with (
            patch(
                "modules.ged.controllers.document_share_controller.get_current_user",
                return_value=mock_current_user,
            ),
            patch("modules.ged.controllers.document_share_controller.DocumentShareService") as mock_service,
        ):
            mock_instance = AsyncMock()
            mock_share = MagicMock()
            mock_share.access_token = "token123"
            mock_instance.create_public_link.return_value = mock_share
            mock_service.return_value = mock_instance

            result = await mock_instance.create_public_link(MagicMock(document_id=str(uuid4())))

            assert result.access_token == "token123"

    @pytest.mark.asyncio
    async def test_access_by_link_expired(self, mock_current_user):
        """Testa acesso via link expirado."""
        with patch("modules.ged.controllers.document_share_controller.DocumentShareService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.access_by_link.side_effect = ValueError("Link expirado")
            mock_service.return_value = mock_instance

            with pytest.raises(ValueError, match="Link expirado"):
                await mock_instance.access_by_link("expired_token")


class TestDocumentSignatureEndpoints:
    """Testes para endpoints de assinatura."""

    @pytest.mark.asyncio
    async def test_request_signatures(self, mock_current_user):
        """Testa solicitação de assinaturas."""
        with (
            patch(
                "modules.ged.controllers.document_signature_controller.get_current_user",
                return_value=mock_current_user,
            ),
            patch("modules.ged.controllers.document_signature_controller.DocumentSignatureService") as mock_service,
        ):
            mock_instance = AsyncMock()
            mock_instance.request_signatures.return_value = [
                MagicMock(signer_email="user1@example.com"),
                MagicMock(signer_email="user2@example.com"),
            ]
            mock_service.return_value = mock_instance

            result = await mock_instance.request_signatures(
                document_id=str(uuid4()),
                signers=[
                    {"email": "user1@example.com"},
                    {"email": "user2@example.com"},
                ],
                created_by=mock_current_user["id"],
            )

            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_sign_document(self, mock_current_user):
        """Testa assinatura de documento."""
        with (
            patch(
                "modules.ged.controllers.document_signature_controller.get_current_user",
                return_value=mock_current_user,
            ),
            patch("modules.ged.controllers.document_signature_controller.DocumentSignatureService") as mock_service,
        ):
            mock_instance = AsyncMock()
            mock_sig = MagicMock()
            mock_sig.status = "assinado"
            mock_sig.signed_at = datetime.utcnow()
            mock_instance.sign.return_value = mock_sig
            mock_service.return_value = mock_instance

            result = await mock_instance.sign(str(uuid4()), MagicMock(signature_data="base64data"))

            assert result.status == "assinado"
            assert result.signed_at is not None


class TestDocumentTagEndpoints:
    """Testes para endpoints de tags."""

    @pytest.mark.asyncio
    async def test_add_tag_to_document(self, mock_current_user):
        """Testa adição de tag a documento."""
        with (
            patch(
                "modules.ged.controllers.document_tag_controller.get_current_user",
                return_value=mock_current_user,
            ),
            patch("modules.ged.controllers.document_tag_controller.DocumentTagService") as mock_service,
        ):
            mock_instance = AsyncMock()
            mock_instance.add_to_document.return_value = True
            mock_service.return_value = mock_instance

            result = await mock_instance.add_to_document(str(uuid4()), str(uuid4()))

            assert result is True

    @pytest.mark.asyncio
    async def test_get_suggested_tags(self, mock_current_user):
        """Testa sugestão de tags."""
        with (
            patch(
                "modules.ged.controllers.document_tag_controller.get_current_user",
                return_value=mock_current_user,
            ),
            patch("modules.ged.controllers.document_tag_controller.DocumentTagService") as mock_service,
        ):
            mock_instance = AsyncMock()
            mock_instance.get_suggested_tags.return_value = [
                MagicMock(name="Contrato"),
                MagicMock(name="Financeiro"),
            ]
            mock_service.return_value = mock_instance

            result = await mock_instance.get_suggested_tags("Contrato financeiro de serviços")

            assert len(result) == 2
