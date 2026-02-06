"""Sprint 40: Create signature recognition tables.

Revision ID: sprint40_signature
Revises: sprint39_ocr
Create Date: 2026-01-05 17:30:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, ENUM

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "sprint40_signature"
down_revision: Union[str, None] = "sprint39_ocr"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create signature recognition tables."""

    # 1. Signature Templates table
    op.create_table(
        "sig_signature_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Template info
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("code", sa.String(50), nullable=True, index=True),
        # Owner information
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("owner_type", sa.String(50), nullable=False),
        sa.Column("owner_name", sa.String(255), nullable=True),
        sa.Column("owner_document", sa.String(50), nullable=True),
        # Type and status
        sa.Column("template_type", sa.String(50), nullable=False, default="personal"),
        sa.Column("status", sa.String(50), nullable=False, default="draft"),
        sa.Column("matching_mode", sa.String(50), nullable=False, default="normal"),
        # Sample info
        sa.Column("sample_count", sa.Integer, default=0),
        sa.Column("min_samples_required", sa.Integer, default=3),
        # Feature vectors
        sa.Column("master_feature_vector", postgresql.JSONB, nullable=True),
        sa.Column("feature_version", sa.String(20), nullable=True),
        sa.Column("master_contour", postgresql.JSONB, nullable=True),
        # Statistical data
        sa.Column("feature_mean", postgresql.JSONB, nullable=True),
        sa.Column("feature_std", postgresql.JSONB, nullable=True),
        sa.Column("feature_variance", postgresql.JSONB, nullable=True),
        # Thresholds
        sa.Column("similarity_threshold", sa.Float, default=0.75),
        sa.Column("min_confidence", sa.Float, default=0.70),
        sa.Column("max_false_positive_rate", sa.Float, default=0.01),
        # Quality requirements
        sa.Column("min_quality_score", sa.Float, default=0.5),
        sa.Column("min_contrast", sa.Float, default=0.3),
        sa.Column("min_clarity", sa.Float, default=0.4),
        # Size constraints
        sa.Column("min_width", sa.Integer, nullable=True),
        sa.Column("max_width", sa.Integer, nullable=True),
        sa.Column("min_height", sa.Integer, nullable=True),
        sa.Column("max_height", sa.Integer, nullable=True),
        sa.Column("aspect_ratio_tolerance", sa.Float, default=0.3),
        # Biometric thresholds
        sa.Column("pressure_variance_max", sa.Float, nullable=True),
        sa.Column("velocity_variance_max", sa.Float, nullable=True),
        sa.Column("timing_variance_max", sa.Float, nullable=True),
        # Usage limits
        sa.Column("max_daily_uses", sa.Integer, nullable=True),
        sa.Column("max_monthly_uses", sa.Integer, nullable=True),
        sa.Column("current_daily_uses", sa.Integer, default=0),
        sa.Column("current_monthly_uses", sa.Integer, default=0),
        sa.Column("last_usage_reset", sa.DateTime, nullable=True),
        # Statistics
        sa.Column("total_verifications", sa.Integer, default=0),
        sa.Column("successful_verifications", sa.Integer, default=0),
        sa.Column("failed_verifications", sa.Integer, default=0),
        sa.Column("average_match_score", sa.Float, nullable=True),
        # Validity
        sa.Column("valid_from", sa.DateTime, nullable=True),
        sa.Column("valid_until", sa.DateTime, nullable=True),
        sa.Column("is_active", sa.Boolean, default=True),
        # Approval
        sa.Column("approved_at", sa.DateTime, nullable=True),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approval_notes", sa.Text, nullable=True),
        # Revocation
        sa.Column("revoked_at", sa.DateTime, nullable=True),
        sa.Column("revoked_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("revocation_reason", sa.Text, nullable=True),
        # Allowed types
        sa.Column("allowed_document_types", postgresql.JSONB, nullable=True),
        sa.Column("allowed_purposes", postgresql.JSONB, nullable=True),
        # Delegation
        sa.Column("can_delegate", sa.Boolean, default=False),
        sa.Column("delegated_from", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("delegation_scope", postgresql.JSONB, nullable=True),
        # Metadata
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("tags", postgresql.JSONB, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        # Audit
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # 2. Signatures table
    op.create_table(
        "sig_signatures",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Owner information
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("owner_type", sa.String(50), nullable=True),
        sa.Column("owner_name", sa.String(255), nullable=True),
        sa.Column("owner_document", sa.String(50), nullable=True),
        # Type and status
        sa.Column("signature_type", sa.String(50), nullable=False, default="handwritten"),
        sa.Column("signature_format", sa.String(50), nullable=False, default="png"),
        sa.Column("status", sa.String(50), nullable=False, default="pending"),
        sa.Column("source", sa.String(50), nullable=False, default="upload"),
        # Image data
        sa.Column("image_path", sa.String(500), nullable=True),
        sa.Column("image_data", sa.Text, nullable=True),
        sa.Column("thumbnail_path", sa.String(500), nullable=True),
        sa.Column("original_filename", sa.String(255), nullable=True),
        # Image properties
        sa.Column("width", sa.Integer, nullable=True),
        sa.Column("height", sa.Integer, nullable=True),
        sa.Column("file_size", sa.Integer, nullable=True),
        sa.Column("dpi", sa.Integer, nullable=True),
        sa.Column("color_depth", sa.Integer, nullable=True),
        # Extraction info
        sa.Column("extracted_from_document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("extraction_region", postgresql.JSONB, nullable=True),
        sa.Column("extraction_method", sa.String(100), nullable=True),
        sa.Column("extraction_confidence", sa.Float, nullable=True),
        # Feature vectors
        sa.Column("feature_vector", postgresql.JSONB, nullable=True),
        sa.Column("feature_version", sa.String(20), nullable=True),
        sa.Column("contour_data", postgresql.JSONB, nullable=True),
        sa.Column("stroke_data", postgresql.JSONB, nullable=True),
        # Quality metrics
        sa.Column("quality_score", sa.Float, nullable=True),
        sa.Column("contrast_score", sa.Float, nullable=True),
        sa.Column("clarity_score", sa.Float, nullable=True),
        sa.Column("completeness_score", sa.Float, nullable=True),
        # Biometric data
        sa.Column("pressure_data", postgresql.JSONB, nullable=True),
        sa.Column("velocity_data", postgresql.JSONB, nullable=True),
        sa.Column("timing_data", postgresql.JSONB, nullable=True),
        # Digital signature info
        sa.Column("certificate_id", sa.String(255), nullable=True),
        sa.Column("certificate_issuer", sa.String(255), nullable=True),
        sa.Column("certificate_serial", sa.String(100), nullable=True),
        sa.Column("certificate_valid_from", sa.DateTime, nullable=True),
        sa.Column("certificate_valid_to", sa.DateTime, nullable=True),
        sa.Column("hash_algorithm", sa.String(50), nullable=True),
        sa.Column("signature_hash", sa.String(512), nullable=True),
        # Verification
        sa.Column("is_verified", sa.Boolean, default=False),
        sa.Column("verified_at", sa.DateTime, nullable=True),
        sa.Column("verified_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("verification_method", sa.String(100), nullable=True),
        sa.Column("verification_score", sa.Float, nullable=True),
        # Template reference
        sa.Column(
            "template_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sig_signature_templates.id"),
            nullable=True,
        ),
        sa.Column("is_template", sa.Boolean, default=False),
        # Usage tracking
        sa.Column("usage_count", sa.Integer, default=0),
        sa.Column("last_used_at", sa.DateTime, nullable=True),
        # Validity
        sa.Column("valid_from", sa.DateTime, nullable=True),
        sa.Column("valid_until", sa.DateTime, nullable=True),
        sa.Column("is_active", sa.Boolean, default=True),
        # Metadata
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("tags", postgresql.JSONB, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        # Capture info
        sa.Column("capture_ip", sa.String(45), nullable=True),
        sa.Column("capture_device", sa.String(255), nullable=True),
        sa.Column("capture_user_agent", sa.String(500), nullable=True),
        sa.Column("capture_location", postgresql.JSONB, nullable=True),
        # Audit
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # 3. Signature Requests table
    op.create_table(
        "sig_signature_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Request info
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("reference_code", sa.String(50), nullable=True, index=True),
        # Status
        sa.Column("status", sa.String(50), nullable=False, default="draft"),
        sa.Column("priority", sa.String(50), nullable=False, default="normal"),
        sa.Column("purpose", sa.String(50), nullable=False, default="approval"),
        # Document
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("document_type", sa.String(100), nullable=True),
        sa.Column("document_name", sa.String(255), nullable=True),
        sa.Column("document_path", sa.String(500), nullable=True),
        sa.Column("document_hash", sa.String(128), nullable=True),
        # Signer
        sa.Column("signer_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("signer_type", sa.String(50), nullable=True),
        sa.Column("signer_name", sa.String(255), nullable=False),
        sa.Column("signer_email", sa.String(255), nullable=True),
        sa.Column("signer_phone", sa.String(20), nullable=True),
        sa.Column("signer_document", sa.String(50), nullable=True),
        # Template
        sa.Column(
            "template_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sig_signature_templates.id"),
            nullable=True,
        ),
        # Placement
        sa.Column("signature_page", sa.Integer, nullable=True),
        sa.Column("signature_position", postgresql.JSONB, nullable=True),
        sa.Column("signature_field_name", sa.String(100), nullable=True),
        # Multi-sign
        sa.Column("signature_order", sa.Integer, default=1),
        sa.Column("total_signers", sa.Integer, default=1),
        sa.Column("parent_request_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Collected signature
        sa.Column(
            "signature_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sig_signatures.id"),
            nullable=True,
        ),
        sa.Column("signed_at", sa.DateTime, nullable=True),
        sa.Column("signed_document_path", sa.String(500), nullable=True),
        sa.Column("signed_document_hash", sa.String(128), nullable=True),
        # Deadlines
        sa.Column("due_date", sa.DateTime, nullable=True),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        # Reminders
        sa.Column("reminder_frequency", sa.String(50), nullable=False, default="none"),
        sa.Column("reminders_sent", sa.Integer, default=0),
        sa.Column("last_reminder_at", sa.DateTime, nullable=True),
        sa.Column("max_reminders", sa.Integer, default=5),
        # Access control
        sa.Column("access_token", sa.String(255), nullable=True, unique=True),
        sa.Column("access_code", sa.String(10), nullable=True),
        sa.Column("requires_authentication", sa.Boolean, default=False),
        sa.Column("allowed_ips", postgresql.ARRAY(sa.String), nullable=True),
        # Notifications
        sa.Column("notify_on_view", sa.Boolean, default=True),
        sa.Column("notify_on_sign", sa.Boolean, default=True),
        sa.Column("notify_on_reject", sa.Boolean, default=True),
        sa.Column("notification_emails", postgresql.ARRAY(sa.String), nullable=True),
        # Tracking
        sa.Column("viewed_at", sa.DateTime, nullable=True),
        sa.Column("view_count", sa.Integer, default=0),
        sa.Column("last_activity_at", sa.DateTime, nullable=True),
        # Rejection
        sa.Column("rejected_at", sa.DateTime, nullable=True),
        sa.Column("rejection_reason", sa.Text, nullable=True),
        # Cancellation
        sa.Column("cancelled_at", sa.DateTime, nullable=True),
        sa.Column("cancelled_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("cancellation_reason", sa.Text, nullable=True),
        # Signing info
        sa.Column("signing_ip", sa.String(45), nullable=True),
        sa.Column("signing_device", sa.String(255), nullable=True),
        sa.Column("signing_user_agent", sa.String(500), nullable=True),
        sa.Column("signing_location", postgresql.JSONB, nullable=True),
        # Audit trail
        sa.Column("audit_log", postgresql.JSONB, nullable=True),
        # Custom fields
        sa.Column("custom_fields", postgresql.JSONB, nullable=True),
        sa.Column("required_fields", postgresql.JSONB, nullable=True),
        # Metadata
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("tags", postgresql.JSONB, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        # Workflow
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("workflow_step", sa.String(100), nullable=True),
        # Requester
        sa.Column("requested_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("requested_by_name", sa.String(255), nullable=True),
        sa.Column("requested_by_email", sa.String(255), nullable=True),
        # Audit
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("sent_at", sa.DateTime, nullable=True),
    )

    # 4. Signature Verifications table
    op.create_table(
        "sig_signature_verifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # References
        sa.Column(
            "signature_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sig_signatures.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "template_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sig_signature_templates.id"),
            nullable=True,
            index=True,
        ),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column(
            "request_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sig_signature_requests.id"),
            nullable=True,
        ),
        # Status
        sa.Column("status", sa.String(50), nullable=False, default="pending"),
        sa.Column("result", sa.String(50), nullable=True),
        sa.Column("risk_level", sa.String(50), nullable=True),
        # Method
        sa.Column("method", sa.String(50), nullable=False, default="feature"),
        sa.Column("algorithm_version", sa.String(20), nullable=True),
        # Scores
        sa.Column("overall_score", sa.Float, nullable=True),
        sa.Column("similarity_score", sa.Float, nullable=True),
        sa.Column("feature_score", sa.Float, nullable=True),
        sa.Column("contour_score", sa.Float, nullable=True),
        sa.Column("biometric_score", sa.Float, nullable=True),
        # Confidence
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("confidence_interval_low", sa.Float, nullable=True),
        sa.Column("confidence_interval_high", sa.Float, nullable=True),
        # Threshold
        sa.Column("threshold_used", sa.Float, nullable=True),
        sa.Column("passed_threshold", sa.Boolean, nullable=True),
        # Detailed analysis
        sa.Column("feature_comparison", postgresql.JSONB, nullable=True),
        sa.Column("contour_analysis", postgresql.JSONB, nullable=True),
        sa.Column("biometric_analysis", postgresql.JSONB, nullable=True),
        # Quality
        sa.Column("input_quality_score", sa.Float, nullable=True),
        sa.Column("template_quality_score", sa.Float, nullable=True),
        sa.Column("quality_issues", postgresql.JSONB, nullable=True),
        # Anomalies
        sa.Column("anomalies_detected", postgresql.JSONB, nullable=True),
        sa.Column("anomaly_count", sa.Integer, default=0),
        sa.Column("fraud_indicators", postgresql.JSONB, nullable=True),
        # Processing
        sa.Column("processing_time_ms", sa.Integer, nullable=True),
        sa.Column("started_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        # Manual review
        sa.Column("requires_manual_review", sa.Boolean, default=False),
        sa.Column("manual_review_reason", sa.Text, nullable=True),
        sa.Column("manually_reviewed", sa.Boolean, default=False),
        sa.Column("manual_reviewer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("manual_review_result", sa.String(50), nullable=True),
        sa.Column("manual_review_notes", sa.Text, nullable=True),
        sa.Column("manual_reviewed_at", sa.DateTime, nullable=True),
        # Error info
        sa.Column("error_code", sa.String(50), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("error_details", postgresql.JSONB, nullable=True),
        # Context
        sa.Column("verification_purpose", sa.String(100), nullable=True),
        sa.Column("verification_context", postgresql.JSONB, nullable=True),
        # Request info
        sa.Column("request_ip", sa.String(45), nullable=True),
        sa.Column("request_device", sa.String(255), nullable=True),
        sa.Column("request_user_agent", sa.String(500), nullable=True),
        sa.Column("request_location", postgresql.JSONB, nullable=True),
        # Audit trail
        sa.Column("audit_log", postgresql.JSONB, nullable=True),
        # Metadata
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        # Audit
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # 5. Signed Documents table
    op.create_table(
        "sig_signed_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Document info
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("reference_code", sa.String(100), nullable=True, index=True),
        sa.Column("document_number", sa.String(100), nullable=True, index=True),
        # Status
        sa.Column("status", sa.String(50), nullable=False, default="pending"),
        sa.Column("integrity_status", sa.String(50), nullable=False, default="unknown"),
        # Original document
        sa.Column("original_document_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("original_path", sa.String(500), nullable=True),
        sa.Column("original_filename", sa.String(255), nullable=True),
        sa.Column("original_hash", sa.String(128), nullable=True),
        sa.Column("original_size", sa.Integer, nullable=True),
        sa.Column("original_pages", sa.Integer, nullable=True),
        sa.Column("original_mime_type", sa.String(100), nullable=True),
        # Signed document
        sa.Column("signed_path", sa.String(500), nullable=True),
        sa.Column("signed_filename", sa.String(255), nullable=True),
        sa.Column("signed_hash", sa.String(128), nullable=True),
        sa.Column("signed_size", sa.Integer, nullable=True),
        sa.Column("signed_mime_type", sa.String(100), nullable=True),
        # Request reference
        sa.Column(
            "request_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sig_signature_requests.id"),
            nullable=True,
        ),
        # Signatures
        sa.Column("total_signatures_required", sa.Integer, default=1),
        sa.Column("total_signatures_collected", sa.Integer, default=0),
        sa.Column("signature_ids", postgresql.ARRAY(postgresql.UUID), nullable=True),
        sa.Column("signature_positions", postgresql.JSONB, nullable=True),
        sa.Column("signers", postgresql.JSONB, nullable=True),
        # Timestamps
        sa.Column("first_signature_at", sa.DateTime, nullable=True),
        sa.Column("last_signature_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
        # Integrity
        sa.Column("last_integrity_check", sa.DateTime, nullable=True),
        sa.Column("integrity_check_count", sa.Integer, default=0),
        sa.Column("integrity_issues", postgresql.JSONB, nullable=True),
        # Certificate
        sa.Column("certificate_id", sa.String(255), nullable=True),
        sa.Column("certificate_chain", postgresql.JSONB, nullable=True),
        sa.Column("timestamp_token", sa.Text, nullable=True),
        sa.Column("timestamped_at", sa.DateTime, nullable=True),
        sa.Column("timestamp_authority", sa.String(255), nullable=True),
        # Legal
        sa.Column("is_legally_binding", sa.Boolean, default=False),
        sa.Column("legal_framework", sa.String(100), nullable=True),
        sa.Column("compliance_standards", postgresql.ARRAY(sa.String), nullable=True),
        # Retention
        sa.Column("retention_period_days", sa.Integer, nullable=True),
        sa.Column("retention_expires_at", sa.DateTime, nullable=True),
        sa.Column("is_permanent", sa.Boolean, default=False),
        # Archive
        sa.Column("archive_status", sa.String(50), nullable=False, default="not_archived"),
        sa.Column("archived_at", sa.DateTime, nullable=True),
        sa.Column("archive_location", sa.String(500), nullable=True),
        sa.Column("archive_reference", sa.String(255), nullable=True),
        # Access
        sa.Column("is_public", sa.Boolean, default=False),
        sa.Column("access_password", sa.String(255), nullable=True),
        sa.Column("allowed_viewers", postgresql.ARRAY(postgresql.UUID), nullable=True),
        sa.Column("access_count", sa.Integer, default=0),
        sa.Column("last_accessed_at", sa.DateTime, nullable=True),
        # Download
        sa.Column("download_count", sa.Integer, default=0),
        sa.Column("last_downloaded_at", sa.DateTime, nullable=True),
        sa.Column("download_log", postgresql.JSONB, nullable=True),
        # Verification
        sa.Column("verification_url", sa.String(500), nullable=True),
        sa.Column("verification_code", sa.String(50), nullable=True, unique=True),
        sa.Column("qr_code_path", sa.String(500), nullable=True),
        # Related documents
        sa.Column("parent_document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("related_documents", postgresql.ARRAY(postgresql.UUID), nullable=True),
        sa.Column("supersedes_document_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("superseded_by_document_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Workflow
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("workflow_status", sa.String(100), nullable=True),
        # External
        sa.Column("external_id", sa.String(255), nullable=True),
        sa.Column("external_system", sa.String(100), nullable=True),
        sa.Column("sync_status", sa.String(50), nullable=True),
        sa.Column("last_synced_at", sa.DateTime, nullable=True),
        # Audit trail
        sa.Column("audit_log", postgresql.JSONB, nullable=True),
        # Metadata
        sa.Column("metadata", postgresql.JSONB, nullable=True),
        sa.Column("tags", postgresql.JSONB, nullable=True),
        sa.Column("categories", postgresql.ARRAY(sa.String), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        # Audit
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Create indexes
    op.create_index("ix_sig_signatures_owner", "sig_signatures", ["owner_id", "owner_type"])
    op.create_index("ix_sig_signatures_status", "sig_signatures", ["tenant_id", "status"])
    op.create_index("ix_sig_templates_owner", "sig_signature_templates", ["owner_id", "owner_type"])
    op.create_index("ix_sig_templates_status", "sig_signature_templates", ["tenant_id", "status"])
    op.create_index("ix_sig_requests_signer", "sig_signature_requests", ["signer_id", "status"])
    op.create_index("ix_sig_requests_status", "sig_signature_requests", ["tenant_id", "status"])
    op.create_index("ix_sig_verifications_result", "sig_signature_verifications", ["tenant_id", "result"])
    op.create_index("ix_sig_documents_status", "sig_signed_documents", ["tenant_id", "status"])


def downgrade() -> None:
    """Drop signature recognition tables."""
    op.drop_index("ix_sig_documents_status")
    op.drop_index("ix_sig_verifications_result")
    op.drop_index("ix_sig_requests_status")
    op.drop_index("ix_sig_requests_signer")
    op.drop_index("ix_sig_templates_status")
    op.drop_index("ix_sig_templates_owner")
    op.drop_index("ix_sig_signatures_status")
    op.drop_index("ix_sig_signatures_owner")

    op.drop_table("sig_signed_documents")
    op.drop_table("sig_signature_verifications")
    op.drop_table("sig_signature_requests")
    op.drop_table("sig_signatures")
    op.drop_table("sig_signature_templates")
