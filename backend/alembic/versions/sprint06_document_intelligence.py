"""Sprint 06 - Document Intelligence

Revision ID: sprint06_documents
Revises:
Create Date: 2026-01-07

Cria tabelas para o modulo Document Intelligence:
- documents: Documentos processados
- ocr_results: Resultados de OCR
- extracted_fields: Campos extraidos
- extraction_templates: Templates de extracao
- template_fields: Campos dos templates
- validation_results: Resultados de validacao
"""
from alembic import op
from sqlalchemy import inspect
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY


# revision identifiers
revision = 'sprint06_documents'
down_revision = None
branch_labels = None
depends_on = None


def table_exists(table_name: str) -> bool:
    """Verifica se uma tabela existe no banco."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    """Cria tabelas do modulo Document Intelligence."""

    if not table_exists('documents'):
        op.create_table(
            'documents',
            sa.Column('id', UUID(as_uuid=True), primary_key=True),
            sa.Column('tenant_id', sa.String(100), nullable=False, index=True),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('original_name', sa.String(255)),
            sa.Column('document_type', sa.String(50), nullable=False, index=True),
            sa.Column('predicted_type', sa.String(50)),
            sa.Column('type_confidence', sa.Float, default=0),
            sa.Column('status', sa.String(30), nullable=False, default='uploaded', index=True),
            sa.Column('source', sa.String(30), default='upload'),
            sa.Column('file_path', sa.String(500)),
            sa.Column('file_url', sa.String(1000)),
            sa.Column('file_hash', sa.String(64)),
            sa.Column('mime_type', sa.String(100)),
            sa.Column('file_size', sa.BigInteger, default=0),
            sa.Column('image_width', sa.Integer),
            sa.Column('image_height', sa.Integer),
            sa.Column('image_format', sa.String(20)),
            sa.Column('image_dpi', sa.Integer),
            sa.Column('image_pages', sa.Integer, default=1),
            sa.Column('preprocessed_path', sa.String(500)),
            sa.Column('thumbnail_path', sa.String(500)),
            sa.Column('ocr_result_id', UUID(as_uuid=True)),
            sa.Column('processing_steps', JSONB),
            sa.Column('current_step', sa.String(50)),
            sa.Column('total_processing_time_ms', sa.Integer, default=0),
            sa.Column('extracted_fields_count', sa.Integer, default=0),
            sa.Column('validation_passed', sa.Boolean, default=False),
            sa.Column('confidence_score', sa.Float, default=0),
            sa.Column('needs_review', sa.Boolean, default=False, index=True),
            sa.Column('review_reason', sa.Text),
            sa.Column('review_notes', sa.Text),
            sa.Column('reviewed_by', sa.String(100)),
            sa.Column('reviewed_at', sa.DateTime),
            sa.Column('folder_id', UUID(as_uuid=True)),
            sa.Column('tags', ARRAY(sa.String(50))),
            sa.Column('reference_id', sa.String(100)),
            sa.Column('reference_type', sa.String(50)),
            sa.Column('metadata', JSONB, default={}),
            sa.Column('extracted_data', JSONB, default={}),
            sa.Column('is_active', sa.Boolean, default=True),
            sa.Column('is_archived', sa.Boolean, default=False),
            sa.Column('version', sa.Integer, default=1),
            sa.Column('parent_id', UUID(as_uuid=True)),
            sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
            sa.Column('processed_at', sa.DateTime),
            sa.Column('expires_at', sa.DateTime),
        )
        op.create_index('idx_documents_tenant_status', 'documents', ['tenant_id', 'status'])
        op.create_index('idx_documents_tenant_type', 'documents', ['tenant_id', 'document_type'])
        op.create_index('idx_documents_created_at', 'documents', ['created_at'])
        op.create_index('idx_documents_file_hash', 'documents', ['file_hash'])

    if not table_exists('ocr_results'):
        op.create_table(
            'ocr_results',
            sa.Column('id', UUID(as_uuid=True), primary_key=True),
            sa.Column('document_id', UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('provider', sa.String(30), nullable=False),
            sa.Column('provider_version', sa.String(50)),
            sa.Column('full_text', sa.Text),
            sa.Column('pages', JSONB),
            sa.Column('confidence', sa.Float, default=0),
            sa.Column('language', sa.String(10), default='pt'),
            sa.Column('language_confidence', sa.Float, default=0),
            sa.Column('detected_languages', ARRAY(sa.String(10))),
            sa.Column('total_pages', sa.Integer, default=0),
            sa.Column('total_blocks', sa.Integer, default=0),
            sa.Column('total_lines', sa.Integer, default=0),
            sa.Column('total_words', sa.Integer, default=0),
            sa.Column('total_characters', sa.Integer, default=0),
            sa.Column('tables_found', sa.Integer, default=0),
            sa.Column('barcodes_found', sa.Integer, default=0),
            sa.Column('signatures_found', sa.Integer, default=0),
            sa.Column('handwriting_found', sa.Integer, default=0),
            sa.Column('processing_time_ms', sa.Integer, default=0),
            sa.Column('preprocessing_time_ms', sa.Integer, default=0),
            sa.Column('raw_response', JSONB),
            sa.Column('metadata', JSONB, default={}),
            sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        )

    if not table_exists('extracted_fields'):
        op.create_table(
            'extracted_fields',
            sa.Column('id', UUID(as_uuid=True), primary_key=True),
            sa.Column('document_id', UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('ocr_result_id', UUID(as_uuid=True), sa.ForeignKey('ocr_results.id', ondelete='SET NULL')),
            sa.Column('template_id', UUID(as_uuid=True)),
            sa.Column('field_name', sa.String(100), nullable=False, index=True),
            sa.Column('field_label', sa.String(200)),
            sa.Column('field_type', sa.String(50), nullable=False),
            sa.Column('field_group', sa.String(100)),
            sa.Column('raw_value', sa.Text),
            sa.Column('normalized_value', sa.Text),
            sa.Column('display_value', sa.String(500)),
            sa.Column('original_text', sa.Text),
            sa.Column('confidence', sa.Float, default=0),
            sa.Column('confidence_level', sa.String(20)),
            sa.Column('method', sa.String(30)),
            sa.Column('page', sa.Integer),
            sa.Column('x', sa.Integer),
            sa.Column('y', sa.Integer),
            sa.Column('width', sa.Integer),
            sa.Column('height', sa.Integer),
            sa.Column('line_number', sa.Integer),
            sa.Column('anchor_text', sa.String(200)),
            sa.Column('is_valid', sa.Boolean, default=True),
            sa.Column('validation_errors', ARRAY(sa.String(500))),
            sa.Column('is_required', sa.Boolean, default=False),
            sa.Column('is_verified', sa.Boolean, default=False),
            sa.Column('verified_by', sa.String(100)),
            sa.Column('verified_at', sa.DateTime),
            sa.Column('is_editable', sa.Boolean, default=True),
            sa.Column('alternatives', JSONB),
            sa.Column('metadata', JSONB, default={}),
            sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        )
        op.create_index('idx_extracted_fields_doc_field', 'extracted_fields', ['document_id', 'field_name'])

    if not table_exists('extraction_templates'):
        op.create_table(
            'extraction_templates',
            sa.Column('id', UUID(as_uuid=True), primary_key=True),
            sa.Column('tenant_id', sa.String(100), index=True),
            sa.Column('name', sa.String(200), nullable=False),
            sa.Column('description', sa.Text),
            sa.Column('document_type', sa.String(50), nullable=False, index=True),
            sa.Column('category', sa.String(30), default='other'),
            sa.Column('status', sa.String(20), default='draft', index=True),
            sa.Column('detection_keywords', ARRAY(sa.String(100))),
            sa.Column('detection_patterns', ARRAY(sa.String(500))),
            sa.Column('min_detection_score', sa.Float, default=0.7),
            sa.Column('language', sa.String(10), default='pt'),
            sa.Column('preprocessing', JSONB),
            sa.Column('ocr_config', JSONB),
            sa.Column('version', sa.Integer, default=1),
            sa.Column('parent_version_id', UUID(as_uuid=True)),
            sa.Column('changelog', ARRAY(sa.String(500))),
            sa.Column('usage_count', sa.Integer, default=0),
            sa.Column('success_count', sa.Integer, default=0),
            sa.Column('avg_confidence', sa.Float, default=0),
            sa.Column('avg_processing_time_ms', sa.Integer, default=0),
            sa.Column('author', sa.String(100)),
            sa.Column('tags', ARRAY(sa.String(50))),
            sa.Column('metadata', JSONB, default={}),
            sa.Column('is_official', sa.Boolean, default=False),
            sa.Column('is_public', sa.Boolean, default=False),
            sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
            sa.Column('published_at', sa.DateTime),
        )
        op.create_index('idx_templates_tenant_type', 'extraction_templates', ['tenant_id', 'document_type'])

    if not table_exists('template_fields'):
        op.create_table(
            'template_fields',
            sa.Column('id', UUID(as_uuid=True), primary_key=True),
            sa.Column('template_id', UUID(as_uuid=True), sa.ForeignKey('extraction_templates.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('label', sa.String(200)),
            sa.Column('field_type', sa.String(50), default='text'),
            sa.Column('field_group', sa.String(100)),
            sa.Column('rules', JSONB),
            sa.Column('required', sa.Boolean, default=False),
            sa.Column('default_value', sa.String(500)),
            sa.Column('description', sa.Text),
            sa.Column('min_confidence', sa.Float, default=0.5),
            sa.Column('validators', ARRAY(sa.String(100))),
            sa.Column('format_pattern', sa.String(200)),
            sa.Column('display_format', sa.String(200)),
            sa.Column('depends_on', sa.String(100)),
            sa.Column('conditional_rules', JSONB),
            sa.Column('order_num', sa.Integer, default=0),
            sa.Column('is_key_field', sa.Boolean, default=False),
            sa.Column('is_searchable', sa.Boolean, default=True),
            sa.Column('metadata', JSONB, default={}),
        )

    if not table_exists('validation_results'):
        op.create_table(
            'validation_results',
            sa.Column('id', UUID(as_uuid=True), primary_key=True),
            sa.Column('document_id', UUID(as_uuid=True), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('template_id', UUID(as_uuid=True)),
            sa.Column('status', sa.String(20), nullable=False, default='pending'),
            sa.Column('is_valid', sa.Boolean, default=True),
            sa.Column('overall_score', sa.Float, default=0),
            sa.Column('field_results', JSONB),
            sa.Column('total_fields', sa.Integer, default=0),
            sa.Column('fields_validated', sa.Integer, default=0),
            sa.Column('fields_passed', sa.Integer, default=0),
            sa.Column('fields_failed', sa.Integer, default=0),
            sa.Column('fields_with_warnings', sa.Integer, default=0),
            sa.Column('fields_auto_corrected', sa.Integer, default=0),
            sa.Column('global_errors', ARRAY(sa.String(500))),
            sa.Column('global_warnings', ARRAY(sa.String(500))),
            sa.Column('cross_field_results', JSONB),
            sa.Column('total_validation_time_ms', sa.Integer, default=0),
            sa.Column('rules_executed', sa.Integer, default=0),
            sa.Column('validated_by', sa.String(100)),
            sa.Column('metadata', JSONB, default={}),
            sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        )

    if not table_exists('document_folders'):
        op.create_table(
            'document_folders',
            sa.Column('id', UUID(as_uuid=True), primary_key=True),
            sa.Column('tenant_id', sa.String(100), nullable=False, index=True),
            sa.Column('parent_id', UUID(as_uuid=True), sa.ForeignKey('document_folders.id', ondelete='CASCADE')),
            sa.Column('name', sa.String(200), nullable=False),
            sa.Column('description', sa.Text),
            sa.Column('path', sa.String(1000)),
            sa.Column('color', sa.String(20)),
            sa.Column('icon', sa.String(50)),
            sa.Column('document_count', sa.Integer, default=0),
            sa.Column('is_system', sa.Boolean, default=False),
            sa.Column('metadata', JSONB, default={}),
            sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        )
        op.create_index('idx_folders_tenant_parent', 'document_folders', ['tenant_id', 'parent_id'])


def downgrade() -> None:
    """Remove tabelas do modulo Document Intelligence."""
    op.drop_table('validation_results')
    op.drop_table('template_fields')
    op.drop_table('extraction_templates')
    op.drop_table('extracted_fields')
    op.drop_table('ocr_results')
    op.drop_table('document_folders')
    op.drop_table('documents')
