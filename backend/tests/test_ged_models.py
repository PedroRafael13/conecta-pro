"""Testes para os models do módulo GED."""

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from modules.ged.models.document import (
    Document,
    DocumentCategory,
    DocumentConfidentiality,
    DocumentStatus,
    DocumentType,
    FileType,
)
from modules.ged.models.document_share import (
    DocumentShare,
    SharePermission,
    ShareStatus,
    ShareType,
)
from modules.ged.models.document_signature import (
    DocumentSignature,
    SignatureRole,
    SignatureStatus,
    SignatureType,
)
from modules.ged.models.document_tag import (
    DocumentTag,
    TagColor,
    TagType,
)
from modules.ged.models.document_version import (
    DocumentVersion,
    VersionStatus,
    VersionType,
)
from modules.ged.models.folder import (
    Folder,
    FolderPermission,
    FolderStatus,
    FolderType,
)


class TestFolderModel:
    """Testes para o model Folder."""

    def test_create_folder(self):
        """Testa criação de pasta."""
        folder = Folder(
            name="Contratos",
            folder_type=FolderType.CONTRATO,
            condominium_id=str(uuid4()),
            created_by=str(uuid4()),
        )
        assert folder.name == "Contratos"
        assert folder.folder_type == FolderType.CONTRATO
        assert folder.status == FolderStatus.ATIVO

    def test_folder_update_path(self):
        """Testa atualização de path."""
        folder = Folder(
            name="SubPasta",
            path="/Contratos",
            folder_type=FolderType.DEPARTAMENTO,
            created_by=str(uuid4()),
        )
        folder.update_path()
        assert folder.full_path == "/Contratos/SubPasta"

    def test_folder_archive(self):
        """Testa arquivamento de pasta."""
        folder = Folder(
            name="Pasta",
            folder_type=FolderType.DEPARTAMENTO,
            created_by=str(uuid4()),
        )
        user_id = str(uuid4())
        folder.archive(user_id)
        assert folder.status == FolderStatus.ARQUIVADO
        assert folder.archived_by == user_id
        assert folder.archived_at is not None

    def test_folder_unarchive(self):
        """Testa desarquivamento de pasta."""
        folder = Folder(
            name="Pasta",
            folder_type=FolderType.DEPARTAMENTO,
            status=FolderStatus.ARQUIVADO,
            created_by=str(uuid4()),
        )
        folder.unarchive()
        assert folder.status == FolderStatus.ATIVO
        assert folder.archived_by is None
        assert folder.archived_at is None

    def test_folder_block(self):
        """Testa bloqueio de pasta."""
        folder = Folder(
            name="Pasta",
            folder_type=FolderType.DEPARTAMENTO,
            created_by=str(uuid4()),
        )
        folder.block()
        assert folder.status == FolderStatus.BLOQUEADO

    def test_folder_grant_permission(self):
        """Testa concessão de permissão."""
        folder = Folder(
            name="Pasta",
            folder_type=FolderType.DEPARTAMENTO,
            created_by=str(uuid4()),
        )
        user_id = str(uuid4())
        folder.grant_permission(user_id, FolderPermission.LEITURA)
        assert folder.has_permission(user_id, FolderPermission.LEITURA)

    def test_folder_revoke_permission(self):
        """Testa revogação de permissão."""
        user_id = str(uuid4())
        folder = Folder(
            name="Pasta",
            folder_type=FolderType.DEPARTAMENTO,
            created_by=str(uuid4()),
            permissions={user_id: ["leitura", "escrita"]},
        )
        folder.revoke_permission(user_id, FolderPermission.ESCRITA)
        assert folder.has_permission(user_id, FolderPermission.LEITURA)
        assert not folder.has_permission(user_id, FolderPermission.ESCRITA)

    def test_folder_extension_allowed(self):
        """Testa validação de extensão."""
        folder = Folder(
            name="Pasta",
            folder_type=FolderType.DEPARTAMENTO,
            allowed_extensions=["pdf", "doc", "docx"],
            created_by=str(uuid4()),
        )
        assert folder.is_extension_allowed("pdf")
        assert not folder.is_extension_allowed("exe")

    def test_folder_size_allowed(self):
        """Testa validação de tamanho."""
        folder = Folder(
            name="Pasta",
            folder_type=FolderType.DEPARTAMENTO,
            max_file_size_mb=10,
            created_by=str(uuid4()),
        )
        assert folder.is_size_allowed(5 * 1024 * 1024)  # 5MB
        assert not folder.is_size_allowed(15 * 1024 * 1024)  # 15MB


class TestDocumentModel:
    """Testes para o model Document."""

    def test_create_document(self):
        """Testa criação de documento."""
        doc = Document(
            title="Contrato de Serviço",
            folder_id=str(uuid4()),
            document_type=DocumentType.CONTRATO,
            category=DocumentCategory.ADMINISTRATIVO,
            file_name="contrato.pdf",
            file_path="/docs/contrato.pdf",
            file_size_bytes=1024000,
            file_extension="pdf",
            file_type=FileType.PDF,
            mime_type="application/pdf",
            checksum="abc123",
            created_by=str(uuid4()),
        )
        assert doc.title == "Contrato de Serviço"
        assert doc.status == DocumentStatus.RASCUNHO

    def test_document_publish(self):
        """Testa publicação de documento."""
        doc = Document(
            title="Documento",
            folder_id=str(uuid4()),
            status=DocumentStatus.APROVADO,
            created_by=str(uuid4()),
        )
        doc.publish()
        assert doc.status == DocumentStatus.PUBLICADO
        assert doc.published_at is not None

    def test_document_approve(self):
        """Testa aprovação de documento."""
        doc = Document(
            title="Documento",
            folder_id=str(uuid4()),
            status=DocumentStatus.PENDENTE_APROVACAO,
            created_by=str(uuid4()),
        )
        user_id = str(uuid4())
        doc.approve(user_id)
        assert doc.status == DocumentStatus.APROVADO
        assert doc.approved_by == user_id

    def test_document_reject(self):
        """Testa rejeição de documento."""
        doc = Document(
            title="Documento",
            folder_id=str(uuid4()),
            status=DocumentStatus.PENDENTE_APROVACAO,
            created_by=str(uuid4()),
        )
        doc.reject("Motivo da rejeição")
        assert doc.status == DocumentStatus.REJEITADO
        assert doc.rejection_reason == "Motivo da rejeição"

    def test_document_archive(self):
        """Testa arquivamento de documento."""
        doc = Document(
            title="Documento",
            folder_id=str(uuid4()),
            created_by=str(uuid4()),
        )
        user_id = str(uuid4())
        doc.archive(user_id)
        assert doc.status == DocumentStatus.ARQUIVADO
        assert doc.archived_by == user_id

    def test_document_set_ocr_result(self):
        """Testa definição de resultado OCR."""
        doc = Document(
            title="Documento",
            folder_id=str(uuid4()),
            created_by=str(uuid4()),
        )
        doc.set_ocr_result("Texto extraído", 0.95, ["palavra1", "palavra2"])
        assert doc.is_ocr_processed
        assert doc.ocr_text == "Texto extraído"
        assert doc.ocr_confidence == 0.95

    def test_document_create_new_version(self):
        """Testa criação de nova versão."""
        doc = Document(
            title="Documento",
            folder_id=str(uuid4()),
            current_version=1,
            created_by=str(uuid4()),
        )
        new_version = doc.create_new_version()
        assert new_version == 2
        assert doc.current_version == 2

    def test_document_check_expiry(self):
        """Testa verificação de expiração."""
        doc = Document(
            title="Documento",
            folder_id=str(uuid4()),
            expires_at=datetime.utcnow() - timedelta(days=1),
            created_by=str(uuid4()),
        )
        assert doc.check_expiry()
        assert doc.status == DocumentStatus.EXPIRADO

    def test_document_verify_checksum(self):
        """Testa verificação de checksum."""
        doc = Document(
            title="Documento",
            folder_id=str(uuid4()),
            checksum="abc123",
            created_by=str(uuid4()),
        )
        assert doc.verify_checksum("abc123")
        assert not doc.verify_checksum("xyz789")


class TestDocumentVersionModel:
    """Testes para o model DocumentVersion."""

    def test_create_version(self):
        """Testa criação de versão."""
        version = DocumentVersion(
            document_id=str(uuid4()),
            version_number=1,
            file_name="doc_v1.pdf",
            file_path="/docs/v1/doc.pdf",
            file_size_bytes=1024,
            mime_type="application/pdf",
            checksum="abc123",
            created_by=str(uuid4()),
        )
        assert version.version_number == 1
        assert version.is_current

    def test_version_set_as_current(self):
        """Testa definição como versão atual."""
        version = DocumentVersion(
            document_id=str(uuid4()),
            version_number=2,
            is_current=False,
            created_by=str(uuid4()),
        )
        version.set_as_current()
        assert version.is_current

    def test_version_archive(self):
        """Testa arquivamento de versão."""
        version = DocumentVersion(
            document_id=str(uuid4()),
            version_number=1,
            created_by=str(uuid4()),
        )
        version.archive()
        assert version.status == VersionStatus.ARQUIVADO


class TestDocumentShareModel:
    """Testes para o model DocumentShare."""

    def test_create_share(self):
        """Testa criação de compartilhamento."""
        share = DocumentShare(
            document_id=str(uuid4()),
            share_type=ShareType.USUARIO,
            permission=SharePermission.VISUALIZAR,
            shared_by=str(uuid4()),
            recipient_id=str(uuid4()),
        )
        assert share.share_type == ShareType.USUARIO
        assert share.status == ShareStatus.ATIVO

    def test_share_generate_token(self):
        """Testa geração de token."""
        share = DocumentShare(
            document_id=str(uuid4()),
            share_type=ShareType.LINK,
            shared_by=str(uuid4()),
        )
        token = share.generate_token()
        assert token is not None
        assert share.access_token == token

    def test_share_revoke(self):
        """Testa revogação de compartilhamento."""
        share = DocumentShare(
            document_id=str(uuid4()),
            share_type=ShareType.USUARIO,
            shared_by=str(uuid4()),
        )
        share.revoke()
        assert share.status == ShareStatus.REVOGADO

    def test_share_access_count(self):
        """Testa contagem de acessos."""
        share = DocumentShare(
            document_id=str(uuid4()),
            share_type=ShareType.LINK,
            max_access_count=5,
            access_count=5,
            shared_by=str(uuid4()),
        )
        assert share.access_count_exceeded

    def test_share_expired(self):
        """Testa verificação de expiração."""
        share = DocumentShare(
            document_id=str(uuid4()),
            share_type=ShareType.LINK,
            expires_at=datetime.utcnow() - timedelta(hours=1),
            shared_by=str(uuid4()),
        )
        assert share.is_expired


class TestDocumentTagModel:
    """Testes para o model DocumentTag."""

    def test_create_tag(self):
        """Testa criação de tag."""
        tag = DocumentTag(
            name="Importante",
            tag_type=TagType.PRIORIDADE,
            color=TagColor.VERMELHO,
            created_by=str(uuid4()),
        )
        assert tag.name == "Importante"
        assert tag.slug == "importante"

    def test_tag_generate_slug(self):
        """Testa geração de slug."""
        tag = DocumentTag(
            name="Contrato de Prestação de Serviços",
            tag_type=TagType.CATEGORIA,
            created_by=str(uuid4()),
        )
        assert tag.slug == "contrato-de-prestacao-de-servicos"

    def test_tag_increment_count(self):
        """Testa incremento de contagem."""
        tag = DocumentTag(
            name="Tag",
            tag_type=TagType.PERSONALIZADA,
            document_count=5,
            created_by=str(uuid4()),
        )
        tag.increment_count()
        assert tag.document_count == 6

    def test_tag_decrement_count(self):
        """Testa decremento de contagem."""
        tag = DocumentTag(
            name="Tag",
            tag_type=TagType.PERSONALIZADA,
            document_count=5,
            created_by=str(uuid4()),
        )
        tag.decrement_count()
        assert tag.document_count == 4


class TestDocumentSignatureModel:
    """Testes para o model DocumentSignature."""

    def test_create_signature(self):
        """Testa criação de assinatura."""
        signature = DocumentSignature(
            document_id=str(uuid4()),
            signer_email="user@example.com",
            signer_name="João Silva",
            signer_role=SignatureRole.PARTE,
            signature_type=SignatureType.ELETRONICA,
            created_by=str(uuid4()),
        )
        assert signature.status == SignatureStatus.PENDENTE

    def test_signature_generate_token(self):
        """Testa geração de token."""
        signature = DocumentSignature(
            document_id=str(uuid4()),
            signer_email="user@example.com",
            created_by=str(uuid4()),
        )
        token = signature.generate_token()
        assert token is not None
        assert signature.signature_token == token

    def test_signature_sign(self):
        """Testa assinatura."""
        signature = DocumentSignature(
            document_id=str(uuid4()),
            signer_email="user@example.com",
            created_by=str(uuid4()),
        )
        signature.sign(
            signature_data="base64data",
            signature_hash="hash123",
            ip_address="127.0.0.1",
        )
        assert signature.status == SignatureStatus.ASSINADO
        assert signature.signed_at is not None

    def test_signature_refuse(self):
        """Testa recusa de assinatura."""
        signature = DocumentSignature(
            document_id=str(uuid4()),
            signer_email="user@example.com",
            created_by=str(uuid4()),
        )
        signature.refuse("Motivo da recusa")
        assert signature.status == SignatureStatus.RECUSADO
        assert signature.refusal_reason == "Motivo da recusa"

    def test_signature_cancel(self):
        """Testa cancelamento."""
        signature = DocumentSignature(
            document_id=str(uuid4()),
            signer_email="user@example.com",
            created_by=str(uuid4()),
        )
        signature.cancel()
        assert signature.status == SignatureStatus.CANCELADO

    def test_signature_verify(self):
        """Testa verificação."""
        signature = DocumentSignature(
            document_id=str(uuid4()),
            signer_email="user@example.com",
            status=SignatureStatus.ASSINADO,
            created_by=str(uuid4()),
        )
        signature.verify("hash_validation")
        assert signature.is_verified
        assert signature.verified_at is not None

    def test_signature_expired(self):
        """Testa verificação de expiração."""
        signature = DocumentSignature(
            document_id=str(uuid4()),
            signer_email="user@example.com",
            deadline=datetime.utcnow() - timedelta(days=1),
            created_by=str(uuid4()),
        )
        assert signature.check_and_expire()
        assert signature.status == SignatureStatus.EXPIRADO
