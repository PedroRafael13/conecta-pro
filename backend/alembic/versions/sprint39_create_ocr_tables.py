"""Sprint 39: Create OCR tables.

Revision ID: sprint39_ocr
Revises: sprint38_chatbot
Create Date: 2026-01-05

Tabelas criadas:
- ocr_document_scans: Documentos escaneados
- ocr_results: Resultados OCR
- ocr_lines: Linhas de texto
- ocr_words: Palavras individuais
- ocr_extracted_fields: Campos extraidos
- ocr_document_templates: Templates de extracao
- ocr_template_fields: Campos dos templates
- ocr_extraction_rules: Regras de extracao
- ocr_validation_results: Resultados de validacao
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, ENUM

# revision identifiers
revision = "sprint39_ocr"
down_revision = "sprint37_push_notifications"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria tabelas do modulo OCR."""

    # ========================================
    # ocr_document_scans
    # ========================================
    op.create_table(
        "ocr_document_scans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Identificacao
        sa.Column("scan_id", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("external_id", sa.String(200), index=True),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True), index=True),
        # Arquivo
        sa.Column("file_name", sa.String(500), nullable=False),
        sa.Column("file_path", sa.String(1000)),
        sa.Column("file_url", sa.String(2000)),
        sa.Column("file_size", sa.Integer),
        sa.Column("file_hash", sa.String(64)),
        sa.Column("mime_type", sa.String(100)),
        sa.Column("file_extension", sa.String(20)),
        # Imagem
        sa.Column("image_width", sa.Integer),
        sa.Column("image_height", sa.Integer),
        sa.Column("image_dpi", sa.Integer),
        sa.Column("page_count", sa.Integer, default=1),
        sa.Column("current_page", sa.Integer, default=1),
        # Tipo
        sa.Column("document_type", sa.String(50), index=True),
        sa.Column("detected_type", sa.String(50)),
        sa.Column("type_confidence", sa.Float),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), index=True),
        # Status
        sa.Column("status", sa.String(50), default="pending", index=True),
        sa.Column("status_message", sa.String(500)),
        sa.Column("status_changed_at", sa.DateTime),
        # Preprocessamento
        sa.Column("preprocessing_applied", postgresql.JSONB, default=[]),
        sa.Column("rotation_angle", sa.Float, default=0),
        sa.Column("deskew_angle", sa.Float, default=0),
        sa.Column("quality_score", sa.Float),
        # OCR
        sa.Column("ocr_provider", sa.String(50)),
        sa.Column("ocr_language", sa.String(10), default="por"),
        sa.Column("ocr_languages", postgresql.ARRAY(sa.String), default=["por", "eng"]),
        sa.Column("ocr_started_at", sa.DateTime),
        sa.Column("ocr_completed_at", sa.DateTime),
        sa.Column("ocr_duration_ms", sa.Integer),
        sa.Column("ocr_confidence", sa.Float),
        # Extracao
        sa.Column("extraction_started_at", sa.DateTime),
        sa.Column("extraction_completed_at", sa.DateTime),
        sa.Column("extraction_duration_ms", sa.Integer),
        sa.Column("fields_extracted", sa.Integer, default=0),
        sa.Column("fields_validated", sa.Integer, default=0),
        sa.Column("fields_with_errors", sa.Integer, default=0),
        # Validacao
        sa.Column("validation_started_at", sa.DateTime),
        sa.Column("validation_completed_at", sa.DateTime),
        sa.Column("validation_score", sa.Float),
        sa.Column("requires_review", sa.Boolean, default=False),
        sa.Column("review_reason", sa.String(500)),
        # Revisao
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True)),
        sa.Column("reviewed_at", sa.DateTime),
        sa.Column("review_notes", sa.Text),
        sa.Column("corrections_made", sa.Integer, default=0),
        # Integracao
        sa.Column("source_module", sa.String(100)),
        sa.Column("source_entity", sa.String(100)),
        sa.Column("source_id", postgresql.UUID(as_uuid=True)),
        sa.Column("target_module", sa.String(100)),
        sa.Column("target_entity", sa.String(100)),
        sa.Column("target_id", postgresql.UUID(as_uuid=True)),
        sa.Column("ged_document_id", postgresql.UUID(as_uuid=True)),
        sa.Column("ged_folder_id", postgresql.UUID(as_uuid=True)),
        # Metricas
        sa.Column("processing_attempts", sa.Integer, default=0),
        sa.Column("last_error", sa.Text),
        sa.Column("total_processing_time_ms", sa.Integer),
        # Tags
        sa.Column("tags", postgresql.ARRAY(sa.String), default=[]),
        sa.Column("category", sa.String(100)),
        sa.Column("priority", sa.String(20), default="normal"),
        # Metadata
        sa.Column("extra_data", postgresql.JSONB, default={}),
        sa.Column("original_metadata", postgresql.JSONB, default={}),
        # Controle
        sa.Column("active", sa.Boolean, default=True, index=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime),
    )

    # ========================================
    # ocr_results
    # ========================================
    op.create_table(
        "ocr_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("scan_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Identificacao
        sa.Column("result_id", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("page_number", sa.Integer, default=1),
        # Provider
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("provider_version", sa.String(50)),
        sa.Column("provider_model", sa.String(100)),
        # Texto
        sa.Column("raw_text", sa.Text),
        sa.Column("normalized_text", sa.Text),
        sa.Column("text_length", sa.Integer),
        # Estrutura
        sa.Column("lines", postgresql.JSONB, default=[]),
        sa.Column("blocks", postgresql.JSONB, default=[]),
        sa.Column("tables", postgresql.JSONB, default=[]),
        sa.Column("key_value_pairs", postgresql.JSONB, default=[]),
        sa.Column("form_fields", postgresql.JSONB, default=[]),
        # Confianca
        sa.Column("overall_confidence", sa.Float),
        sa.Column("min_confidence", sa.Float),
        sa.Column("max_confidence", sa.Float),
        sa.Column("low_confidence_words", sa.Integer, default=0),
        # Idioma
        sa.Column("detected_language", sa.String(10)),
        sa.Column("language_confidence", sa.Float),
        sa.Column("languages_found", postgresql.ARRAY(sa.String), default=[]),
        # Orientacao
        sa.Column("detected_orientation", sa.Integer),
        sa.Column("orientation_confidence", sa.Float),
        # Qualidade
        sa.Column("image_quality_score", sa.Float),
        sa.Column("text_density", sa.Float),
        sa.Column("noise_level", sa.Float),
        # Processamento
        sa.Column("processing_time_ms", sa.Integer),
        sa.Column("api_request_id", sa.String(200)),
        sa.Column("api_response_size", sa.Integer),
        # Custos
        sa.Column("api_cost", sa.Float),
        sa.Column("cost_currency", sa.String(3), default="USD"),
        # Erros
        sa.Column("has_errors", sa.Boolean, default=False),
        sa.Column("errors", postgresql.JSONB, default=[]),
        sa.Column("warnings", postgresql.JSONB, default=[]),
        # Raw
        sa.Column("raw_response", postgresql.JSONB),
        # Controle
        sa.Column("active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    # ========================================
    # ocr_lines
    # ========================================
    op.create_table(
        "ocr_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("result_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("line_number", sa.Integer, nullable=False),
        sa.Column("page_number", sa.Integer, default=1),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("normalized_text", sa.Text),
        sa.Column("x", sa.Integer),
        sa.Column("y", sa.Integer),
        sa.Column("width", sa.Integer),
        sa.Column("height", sa.Integer),
        sa.Column("confidence", sa.Float),
        sa.Column("word_count", sa.Integer),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    # ========================================
    # ocr_words
    # ========================================
    op.create_table(
        "ocr_words",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("result_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("line_id", postgresql.UUID(as_uuid=True), index=True),
        sa.Column("word_index", sa.Integer, nullable=False),
        sa.Column("page_number", sa.Integer, default=1),
        sa.Column("line_number", sa.Integer),
        sa.Column("text", sa.String(500), nullable=False),
        sa.Column("normalized_text", sa.String(500)),
        sa.Column("x", sa.Integer),
        sa.Column("y", sa.Integer),
        sa.Column("width", sa.Integer),
        sa.Column("height", sa.Integer),
        sa.Column("confidence", sa.Float),
        sa.Column("is_numeric", sa.Boolean, default=False),
        sa.Column("is_date", sa.Boolean, default=False),
        sa.Column("is_currency", sa.Boolean, default=False),
        sa.Column("is_email", sa.Boolean, default=False),
        sa.Column("is_phone", sa.Boolean, default=False),
        sa.Column("is_cpf_cnpj", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    # ========================================
    # ocr_extracted_fields
    # ========================================
    op.create_table(
        "ocr_extracted_fields",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("scan_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("result_id", postgresql.UUID(as_uuid=True), index=True),
        # Identificacao
        sa.Column("field_id", sa.String(100), nullable=False, index=True),
        sa.Column("template_field_id", postgresql.UUID(as_uuid=True), index=True),
        # Definicao
        sa.Column("field_name", sa.String(100), nullable=False, index=True),
        sa.Column("field_label", sa.String(200)),
        sa.Column("field_type", sa.String(50), nullable=False),
        sa.Column("field_group", sa.String(100)),
        # Valor
        sa.Column("raw_value", sa.Text),
        sa.Column("extracted_value", sa.Text),
        sa.Column("normalized_value", sa.Text),
        sa.Column("formatted_value", sa.Text),
        sa.Column("typed_value", postgresql.JSONB),
        # Posicao
        sa.Column("page_number", sa.Integer, default=1),
        sa.Column("bounding_box", postgresql.JSONB),
        # Origem
        sa.Column("source_line_numbers", postgresql.ARRAY(sa.Integer), default=[]),
        sa.Column("source_text", sa.Text),
        sa.Column("extraction_method", sa.String(50)),
        # Confianca
        sa.Column("confidence", sa.Float),
        sa.Column("ocr_confidence", sa.Float),
        # Validacao
        sa.Column("validation_status", sa.String(50), default="pending"),
        sa.Column("validation_rules_applied", postgresql.ARRAY(sa.String), default=[]),
        sa.Column("validation_errors", postgresql.JSONB, default=[]),
        sa.Column("validation_warnings", postgresql.JSONB, default=[]),
        # Correcao
        sa.Column("was_corrected", sa.Boolean, default=False),
        sa.Column("original_value", sa.Text),
        sa.Column("corrected_by", postgresql.UUID(as_uuid=True)),
        sa.Column("corrected_at", sa.DateTime),
        sa.Column("correction_reason", sa.String(500)),
        # Mapeamento
        sa.Column("target_entity", sa.String(100)),
        sa.Column("target_field", sa.String(100)),
        sa.Column("mapped_successfully", sa.Boolean),
        # Flags
        sa.Column("is_required", sa.Boolean, default=False),
        sa.Column("is_key_field", sa.Boolean, default=False),
        sa.Column("is_calculated", sa.Boolean, default=False),
        sa.Column("is_from_table", sa.Boolean, default=False),
        # Contexto
        sa.Column("context_before", sa.Text),
        sa.Column("context_after", sa.Text),
        sa.Column("related_fields", postgresql.ARRAY(sa.String), default=[]),
        # Metadata
        sa.Column("extra_data", postgresql.JSONB, default={}),
        # Controle
        sa.Column("active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime),
    )

    # ========================================
    # ocr_document_templates
    # ========================================
    op.create_table(
        "ocr_document_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Identificacao
        sa.Column("template_id", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("version", sa.String(20), default="1.0.0"),
        # Tipo
        sa.Column("document_type", sa.String(50), nullable=False),
        sa.Column("document_subtype", sa.String(100)),
        # Deteccao
        sa.Column("detection_keywords", postgresql.ARRAY(sa.String), default=[]),
        sa.Column("detection_patterns", postgresql.JSONB, default=[]),
        sa.Column("detection_threshold", sa.Float, default=0.8),
        # Layout
        sa.Column("supported_layouts", postgresql.JSONB, default=[]),
        sa.Column("regions", postgresql.JSONB, default=[]),
        # OCR
        sa.Column("ocr_settings", postgresql.JSONB, default={}),
        sa.Column("preprocessing_steps", postgresql.JSONB, default=[]),
        # Validacao
        sa.Column("validation_rules", postgresql.JSONB, default=[]),
        sa.Column("field_mapping", postgresql.JSONB, default={}),
        # Metricas
        sa.Column("times_used", sa.Integer, default=0),
        sa.Column("success_rate", sa.Float),
        sa.Column("avg_confidence", sa.Float),
        sa.Column("avg_processing_time_ms", sa.Integer),
        sa.Column("last_used_at", sa.DateTime),
        # Versao
        sa.Column("parent_version_id", postgresql.UUID(as_uuid=True)),
        sa.Column("is_latest", sa.Boolean, default=True),
        sa.Column("published_at", sa.DateTime),
        sa.Column("published_by", postgresql.UUID(as_uuid=True)),
        # Tags
        sa.Column("tags", postgresql.ARRAY(sa.String), default=[]),
        sa.Column("category", sa.String(100)),
        # Metadata
        sa.Column("extra_data", postgresql.JSONB, default={}),
        # Controle
        sa.Column("active", sa.Boolean, default=True, index=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime),
    )

    # ========================================
    # ocr_template_fields
    # ========================================
    op.create_table(
        "ocr_template_fields",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Identificacao
        sa.Column("field_id", sa.String(100), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("label", sa.String(200)),
        sa.Column("description", sa.Text),
        # Tipo
        sa.Column("field_type", sa.String(50), nullable=False),
        sa.Column("field_group", sa.String(100)),
        # Extracao
        sa.Column("extraction_rules", postgresql.JSONB, default=[]),
        sa.Column("expected_region", sa.String(100)),
        sa.Column("expected_position", postgresql.JSONB),
        sa.Column("position_tolerance", sa.Integer, default=20),
        # Alternativas
        sa.Column("alternative_labels", postgresql.ARRAY(sa.String), default=[]),
        sa.Column("alternative_patterns", postgresql.JSONB, default=[]),
        # Validacao
        sa.Column("is_required", sa.Boolean, default=False),
        sa.Column("validation_rules", postgresql.JSONB, default=[]),
        # Transformacao
        sa.Column("transformations", postgresql.JSONB, default=[]),
        sa.Column("default_value", sa.Text),
        sa.Column("default_if_empty", sa.Boolean, default=False),
        # Mapeamento
        sa.Column("target_entity", sa.String(100)),
        sa.Column("target_field", sa.String(100)),
        # Dependencias
        sa.Column("depends_on", postgresql.ARRAY(sa.String), default=[]),
        sa.Column("related_fields", postgresql.ARRAY(sa.String), default=[]),
        # Ordem
        sa.Column("extraction_order", sa.Integer, default=0),
        sa.Column("priority", sa.Integer, default=50),
        # Flags
        sa.Column("is_key_field", sa.Boolean, default=False),
        sa.Column("is_calculated", sa.Boolean, default=False),
        sa.Column("allow_multiple", sa.Boolean, default=False),
        sa.Column("merge_strategy", sa.String(50)),
        # Metricas
        sa.Column("extraction_success_rate", sa.Float),
        sa.Column("avg_confidence", sa.Float),
        # Metadata
        sa.Column("extra_data", postgresql.JSONB, default={}),
        # Controle
        sa.Column("active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime),
    )

    # ========================================
    # ocr_extraction_rules
    # ========================================
    op.create_table(
        "ocr_extraction_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Identificacao
        sa.Column("rule_id", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text),
        # Tipo
        sa.Column("rule_type", sa.String(50), nullable=False),
        sa.Column("rule_definition", postgresql.JSONB, nullable=False),
        # Aplicabilidade
        sa.Column("applicable_field_types", postgresql.ARRAY(sa.String), default=[]),
        sa.Column("applicable_document_types", postgresql.ARRAY(sa.String), default=[]),
        # Transformacao
        sa.Column("transformations", postgresql.JSONB, default=[]),
        # Metricas
        sa.Column("times_used", sa.Integer, default=0),
        sa.Column("success_rate", sa.Float),
        sa.Column("avg_confidence", sa.Float),
        # Tags
        sa.Column("tags", postgresql.ARRAY(sa.String), default=[]),
        sa.Column("category", sa.String(100)),
        # Controle
        sa.Column("active", sa.Boolean, default=True),
        sa.Column("is_system", sa.Boolean, default=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime),
    )

    # ========================================
    # ocr_validation_results
    # ========================================
    op.create_table(
        "ocr_validation_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("scan_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Identificacao
        sa.Column("validation_id", sa.String(100), nullable=False, unique=True, index=True),
        # Status
        sa.Column("status", sa.String(50), default="pending"),
        sa.Column("action_taken", sa.String(50), default="none"),
        # Metricas
        sa.Column("total_fields", sa.Integer, default=0),
        sa.Column("valid_fields", sa.Integer, default=0),
        sa.Column("invalid_fields", sa.Integer, default=0),
        sa.Column("warning_fields", sa.Integer, default=0),
        sa.Column("skipped_fields", sa.Integer, default=0),
        # Scores
        sa.Column("overall_score", sa.Float),
        sa.Column("confidence_score", sa.Float),
        sa.Column("completeness_score", sa.Float),
        sa.Column("consistency_score", sa.Float),
        # Resultados
        sa.Column("field_results", postgresql.JSONB, default=[]),
        sa.Column("document_validations", postgresql.JSONB, default=[]),
        sa.Column("errors", postgresql.JSONB, default=[]),
        sa.Column("warnings", postgresql.JSONB, default=[]),
        sa.Column("auto_corrections", postgresql.JSONB, default=[]),
        # Campos
        sa.Column("missing_required_fields", postgresql.ARRAY(sa.String), default=[]),
        sa.Column("missing_optional_fields", postgresql.ARRAY(sa.String), default=[]),
        sa.Column("suspicious_fields", postgresql.JSONB, default=[]),
        # Cross-validation
        sa.Column("cross_validation_results", postgresql.JSONB, default=[]),
        sa.Column("external_validations", postgresql.JSONB, default=[]),
        # Tempo
        sa.Column("started_at", sa.DateTime),
        sa.Column("completed_at", sa.DateTime),
        sa.Column("duration_ms", sa.Integer),
        # Revisao
        sa.Column("needs_review", sa.Boolean, default=False),
        sa.Column("review_priority", sa.String(20)),
        sa.Column("review_notes", sa.Text),
        sa.Column("reviewed_by", postgresql.UUID(as_uuid=True)),
        sa.Column("reviewed_at", sa.DateTime),
        # Decisao
        sa.Column("final_decision", sa.String(50)),
        sa.Column("decision_by", postgresql.UUID(as_uuid=True)),
        sa.Column("decision_at", sa.DateTime),
        sa.Column("decision_notes", sa.Text),
        # Metadata
        sa.Column("extra_data", postgresql.JSONB, default={}),
        # Controle
        sa.Column("active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime),
    )

    # Indices compostos
    op.create_index(
        "ix_ocr_scans_tenant_status",
        "ocr_document_scans",
        ["tenant_id", "status"],
    )

    op.create_index(
        "ix_ocr_scans_tenant_type",
        "ocr_document_scans",
        ["tenant_id", "document_type"],
    )

    op.create_index(
        "ix_ocr_fields_scan_type",
        "ocr_extracted_fields",
        ["scan_id", "field_type"],
    )


def downgrade() -> None:
    """Remove tabelas do modulo OCR."""
    op.drop_index("ix_ocr_fields_scan_type")
    op.drop_index("ix_ocr_scans_tenant_type")
    op.drop_index("ix_ocr_scans_tenant_status")

    op.drop_table("ocr_validation_results")
    op.drop_table("ocr_extraction_rules")
    op.drop_table("ocr_template_fields")
    op.drop_table("ocr_document_templates")
    op.drop_table("ocr_extracted_fields")
    op.drop_table("ocr_words")
    op.drop_table("ocr_lines")
    op.drop_table("ocr_results")
    op.drop_table("ocr_document_scans")
