"""Criar tabelas do modulo GED - Gestao Eletronica de Documentos.

Revision ID: sprint58_ged
Revises:
Create Date: 2026-01-23

Tabelas criadas:
- ged_folders (pastas/diretorios)
- ged_documents (documentos)
- ged_document_versions (versoes)
- ged_document_shares (compartilhamentos)
- ged_document_tags (tags)
- ged_document_tag_associations (associacao documento-tag)
- ged_document_signatures (assinaturas)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
import uuid

# revision identifiers
revision = "sprint58_ged"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria tabelas do modulo GED."""

    # === GED_FOLDERS (Pastas) ===
    op.create_table(
        "ged_folders",
        # Identificacao
        sa.Column("id", UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),

        # Hierarquia
        sa.Column("parent_id", UUID(as_uuid=False), sa.ForeignKey("ged_folders.id"), nullable=True),
        sa.Column("path", sa.String(1000), nullable=False, default="/"),
        sa.Column("level", sa.Integer(), default=0),

        # Classificacao
        sa.Column("folder_type", sa.String(20), default="condominio"),
        sa.Column("status", sa.String(20), default="ativa"),

        # Vinculo com entidades
        sa.Column("condominium_id", UUID(as_uuid=False), nullable=True, index=True),
        sa.Column("contract_id", UUID(as_uuid=False), nullable=True),
        sa.Column("employee_id", UUID(as_uuid=False), nullable=True),
        sa.Column("client_id", UUID(as_uuid=False), nullable=True),

        # Permissoes
        sa.Column("owner_id", UUID(as_uuid=False), nullable=False),
        sa.Column("is_public", sa.Boolean(), default=False),
        sa.Column("inherit_permissions", sa.Boolean(), default=True),
        sa.Column("permissions", JSONB(), nullable=True),

        # Configuracoes
        sa.Column("max_file_size_mb", sa.Integer(), nullable=True),
        sa.Column("allowed_extensions", ARRAY(sa.String()), nullable=True),
        sa.Column("require_approval", sa.Boolean(), default=False),
        sa.Column("auto_versioning", sa.Boolean(), default=True),

        # Retencao
        sa.Column("retention_days", sa.Integer(), nullable=True),
        sa.Column("retention_policy", sa.String(100), nullable=True),
        sa.Column("delete_after_retention", sa.Boolean(), default=False),

        # Metadados
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("color", sa.String(7), nullable=True),
        sa.Column("order", sa.Integer(), default=0),
        sa.Column("tags", ARRAY(sa.String()), nullable=True),
        sa.Column("extra_metadata", JSONB(), nullable=True),

        # Estatisticas
        sa.Column("document_count", sa.Integer(), default=0),
        sa.Column("subfolder_count", sa.Integer(), default=0),
        sa.Column("total_size_bytes", sa.BigInteger(), default=0),

        # Timestamps
        sa.Column("created_at", sa.DateTime(), default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("archived_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),

        # Auditoria
        sa.Column("created_by", UUID(as_uuid=False), nullable=False),
        sa.Column("updated_by", UUID(as_uuid=False), nullable=True),
        sa.Column("archived_by", UUID(as_uuid=False), nullable=True),
    )

    op.create_index("ix_ged_folders_parent_id", "ged_folders", ["parent_id"])
    op.create_index("ix_ged_folders_path", "ged_folders", ["path"])
    op.create_index("ix_ged_folders_status", "ged_folders", ["status"])

    # === GED_DOCUMENTS (Documentos) ===
    op.create_table(
        "ged_documents",
        # Identificacao
        sa.Column("id", UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),

        # Pasta
        sa.Column("folder_id", UUID(as_uuid=False), sa.ForeignKey("ged_folders.id"), nullable=False, index=True),

        # Classificacao
        sa.Column("document_type", sa.String(30), default="outro"),
        sa.Column("category", sa.String(30), default="outro"),
        sa.Column("status", sa.String(30), default="rascunho"),
        sa.Column("confidentiality", sa.String(20), default="interno"),

        # Arquivo
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_extension", sa.String(20), nullable=False),
        sa.Column("file_type", sa.String(20), default="outro"),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),

        # Thumbnail
        sa.Column("thumbnail_path", sa.String(1000), nullable=True),
        sa.Column("preview_path", sa.String(1000), nullable=True),

        # Versionamento
        sa.Column("current_version", sa.Integer(), default=1),
        sa.Column("version_count", sa.Integer(), default=1),
        sa.Column("is_latest", sa.Boolean(), default=True),

        # Vinculo com entidades
        sa.Column("condominium_id", UUID(as_uuid=False), nullable=True, index=True),
        sa.Column("contract_id", UUID(as_uuid=False), nullable=True),
        sa.Column("employee_id", UUID(as_uuid=False), nullable=True),
        sa.Column("client_id", UUID(as_uuid=False), nullable=True),
        sa.Column("resident_id", UUID(as_uuid=False), nullable=True),
        sa.Column("occurrence_id", UUID(as_uuid=False), nullable=True),

        # Proprietario e permissoes
        sa.Column("owner_id", UUID(as_uuid=False), nullable=False),
        sa.Column("is_public", sa.Boolean(), default=False),
        sa.Column("inherit_folder_permissions", sa.Boolean(), default=True),
        sa.Column("permissions", JSONB(), nullable=True),

        # Validade
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("is_perpetual", sa.Boolean(), default=False),

        # Aprovacao
        sa.Column("requires_approval", sa.Boolean(), default=False),
        sa.Column("approved_by", UUID(as_uuid=False), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),

        # Assinatura digital
        sa.Column("is_signed", sa.Boolean(), default=False),
        sa.Column("signature_count", sa.Integer(), default=0),
        sa.Column("requires_signature", sa.Boolean(), default=False),
        sa.Column("signature_deadline", sa.DateTime(), nullable=True),

        # OCR e Indexacao
        sa.Column("is_ocr_processed", sa.Boolean(), default=False),
        sa.Column("ocr_text", sa.Text(), nullable=True),
        sa.Column("ocr_confidence", sa.Float(), nullable=True),
        sa.Column("ocr_processed_at", sa.DateTime(), nullable=True),
        sa.Column("is_indexed", sa.Boolean(), default=False),
        sa.Column("indexed_at", sa.DateTime(), nullable=True),
        sa.Column("search_keywords", ARRAY(sa.String()), nullable=True),

        # Metadados
        sa.Column("extra_metadata", JSONB(), nullable=True),
        sa.Column("custom_fields", JSONB(), nullable=True),
        sa.Column("external_reference", sa.String(100), nullable=True),

        # Estatisticas
        sa.Column("view_count", sa.Integer(), default=0),
        sa.Column("download_count", sa.Integer(), default=0),
        sa.Column("share_count", sa.Integer(), default=0),
        sa.Column("last_viewed_at", sa.DateTime(), nullable=True),
        sa.Column("last_downloaded_at", sa.DateTime(), nullable=True),

        # Timestamps
        sa.Column("created_at", sa.DateTime(), default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("archived_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),

        # Auditoria
        sa.Column("created_by", UUID(as_uuid=False), nullable=False),
        sa.Column("updated_by", UUID(as_uuid=False), nullable=True),
        sa.Column("archived_by", UUID(as_uuid=False), nullable=True),
    )

    op.create_index("ix_ged_documents_status", "ged_documents", ["status"])
    op.create_index("ix_ged_documents_document_type", "ged_documents", ["document_type"])

    # === GED_DOCUMENT_VERSIONS (Versoes) ===
    op.create_table(
        "ged_document_versions",
        sa.Column("id", UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column("document_id", UUID(as_uuid=False), sa.ForeignKey("ged_documents.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("version_type", sa.String(20), default="minor"),
        sa.Column("status", sa.String(20), default="ativo"),

        # Arquivo
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),

        # Metadados
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("change_notes", sa.Text(), nullable=True),
        sa.Column("is_current", sa.Boolean(), default=False),
        sa.Column("is_locked", sa.Boolean(), default=False),

        # Timestamps
        sa.Column("created_at", sa.DateTime(), default=sa.func.now()),
        sa.Column("created_by", UUID(as_uuid=False), nullable=False),
        sa.Column("restored_at", sa.DateTime(), nullable=True),
        sa.Column("restored_by", UUID(as_uuid=False), nullable=True),
    )

    # === GED_DOCUMENT_TAGS (Tags) ===
    op.create_table(
        "ged_document_tags",
        sa.Column("id", UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("slug", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tag_type", sa.String(20), default="geral"),
        sa.Column("color", sa.String(20), default="blue"),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("usage_count", sa.Integer(), default=0),
        sa.Column("is_system", sa.Boolean(), default=False),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now()),
        sa.Column("created_by", UUID(as_uuid=False), nullable=False),
    )

    op.create_index("ix_ged_document_tags_slug", "ged_document_tags", ["slug"])

    # === GED_DOCUMENT_TAG_ASSOCIATIONS (Associacao Documento-Tag) ===
    op.create_table(
        "ged_document_tag_associations",
        sa.Column("document_id", UUID(as_uuid=False), sa.ForeignKey("ged_documents.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", UUID(as_uuid=False), sa.ForeignKey("ged_document_tags.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("created_at", sa.DateTime(), default=sa.func.now()),
        sa.Column("created_by", UUID(as_uuid=False), nullable=True),
    )

    # === GED_DOCUMENT_SHARES (Compartilhamentos) ===
    op.create_table(
        "ged_document_shares",
        sa.Column("id", UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column("document_id", UUID(as_uuid=False), sa.ForeignKey("ged_documents.id", ondelete="CASCADE"), nullable=False, index=True),

        # Compartilhado com
        sa.Column("share_type", sa.String(20), nullable=False),
        sa.Column("shared_with_id", UUID(as_uuid=False), nullable=True),
        sa.Column("shared_with_email", sa.String(255), nullable=True),

        # Permissao
        sa.Column("permission", sa.String(20), default="leitura"),
        sa.Column("status", sa.String(20), default="ativo"),

        # Link publico
        sa.Column("access_token", sa.String(64), nullable=True, unique=True),
        sa.Column("public_url", sa.String(500), nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=True),

        # Validade
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("max_downloads", sa.Integer(), nullable=True),
        sa.Column("download_count", sa.Integer(), default=0),
        sa.Column("view_count", sa.Integer(), default=0),

        # Notificacao
        sa.Column("notify_on_access", sa.Boolean(), default=False),
        sa.Column("message", sa.Text(), nullable=True),

        # Timestamps
        sa.Column("created_at", sa.DateTime(), default=sa.func.now()),
        sa.Column("created_by", UUID(as_uuid=False), nullable=False),
        sa.Column("last_accessed_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_by", UUID(as_uuid=False), nullable=True),
    )

    # === GED_DOCUMENT_SIGNATURES (Assinaturas) ===
    op.create_table(
        "ged_document_signatures",
        sa.Column("id", UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column("document_id", UUID(as_uuid=False), sa.ForeignKey("ged_documents.id", ondelete="CASCADE"), nullable=False, index=True),

        # Signatario
        sa.Column("signer_id", UUID(as_uuid=False), nullable=True),
        sa.Column("signer_name", sa.String(255), nullable=False),
        sa.Column("signer_email", sa.String(255), nullable=False),
        sa.Column("signer_cpf", sa.String(14), nullable=True),
        sa.Column("signer_role", sa.String(30), default="signatario"),

        # Tipo e status
        sa.Column("signature_type", sa.String(20), default="eletronica"),
        sa.Column("status", sa.String(20), default="pendente"),

        # Dados da assinatura
        sa.Column("signature_data", sa.Text(), nullable=True),
        sa.Column("signature_hash", sa.String(64), nullable=True),
        sa.Column("certificate_data", sa.Text(), nullable=True),

        # Rastreabilidade
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("geolocation", JSONB(), nullable=True),

        # Ordem
        sa.Column("order", sa.Integer(), default=0),

        # Timestamps
        sa.Column("requested_at", sa.DateTime(), default=sa.func.now()),
        sa.Column("signed_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("rejected_at", sa.DateTime(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),

        # Auditoria
        sa.Column("created_by", UUID(as_uuid=False), nullable=False),
    )

    print("Tabelas GED criadas com sucesso!")


def downgrade() -> None:
    """Remove tabelas do modulo GED."""
    op.drop_table("ged_document_signatures")
    op.drop_table("ged_document_shares")
    op.drop_table("ged_document_tag_associations")
    op.drop_table("ged_document_tags")
    op.drop_table("ged_document_versions")
    op.drop_table("ged_documents")
    op.drop_table("ged_folders")
    print("Tabelas GED removidas!")
