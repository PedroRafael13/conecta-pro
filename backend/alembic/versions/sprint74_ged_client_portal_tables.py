"""Create GED (Kits Documentais) and Client Portal tables.

New tables:
- ged_clients: clients/condominiums for document kit delivery
- ged_document_kits: monthly document kits per client
- ged_kit_documents: individual documents within kits
- ged_kit_access_logs: audit log for kit access/actions
- client_portal_sessions: client portal login sessions
- client_tickets: support tickets from clients
- client_ticket_messages: messages within tickets

Revision ID: sprint74_ged_client_portal
Revises: sprint73_fix_column_types
Create Date: 2026-03-13

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "sprint74_ged_client_portal"
down_revision = "sprint73_fix_column_types"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ════════════════════════════════════════════
    # GED TABLES
    # ════════════════════════════════════════════

    # 1. ged_clients
    op.create_table(
        "ged_clients",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("cnpj", sa.String(18), unique=True, nullable=True),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("contact_name", sa.String(255), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("contact_phone", sa.String(20), nullable=True),
        sa.Column("google_drive_folder_id", sa.String(100), nullable=True),
        sa.Column("portal_access_enabled", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("portal_username", sa.String(100), nullable=True),
        sa.Column("portal_password_hash", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("idx_ged_clients_cnpj", "ged_clients", ["cnpj"])
    op.create_index("idx_ged_clients_type", "ged_clients", ["type"])
    op.create_index("idx_ged_clients_active", "ged_clients", ["is_active"])

    # 2. ged_document_kits
    op.create_table(
        "ged_document_kits",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ged_clients.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("reference_month", sa.Date, nullable=False),
        sa.Column("status", sa.String(30), server_default=sa.text("'EM_MONTAGEM'"), nullable=False),
        sa.Column("total_employees", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("total_documents", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("documents_signed", sa.Integer, server_default=sa.text("0"), nullable=False),
        sa.Column("completion_percentage", sa.Numeric(5, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_method", sa.String(50), nullable=True),
        sa.Column("sent_to", sa.String(255), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", sa.String(255), nullable=True),
        sa.Column("zip_file_path", sa.String(500), nullable=True),
        sa.Column("google_drive_link", sa.String(500), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.UniqueConstraint("client_id", "reference_month", name="uq_ged_kit_client_month"),
    )
    op.create_index("idx_ged_kits_client_month", "ged_document_kits", ["client_id", "reference_month"])
    op.create_index("idx_ged_kits_status", "ged_document_kits", ["status"])
    op.create_index("idx_ged_kits_reference_month", "ged_document_kits", ["reference_month"])

    # 3. ged_kit_documents
    op.create_table(
        "ged_kit_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column(
            "kit_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ged_document_kits.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("employee_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("document_type", sa.String(50), nullable=False),
        sa.Column("document_name", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=True),
        sa.Column("file_size_bytes", sa.BigInteger, nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("is_signed", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("signed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("signed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("signature_hash", sa.String(64), nullable=True),
        sa.Column("source_module", sa.String(50), nullable=True),
        sa.Column("source_record_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("auto_generated", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
    )
    op.create_index("idx_ged_documents_kit", "ged_kit_documents", ["kit_id"])
    op.create_index("idx_ged_documents_employee", "ged_kit_documents", ["employee_id"])
    op.create_index("idx_ged_documents_type", "ged_kit_documents", ["document_type"])
    op.create_index("idx_ged_documents_signed", "ged_kit_documents", ["is_signed"])

    # 4. ged_kit_access_logs
    op.create_table(
        "ged_kit_access_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column(
            "kit_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ged_document_kits.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("actor_type", sa.String(30), nullable=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_name", sa.String(255), nullable=True),
        sa.Column("actor_ip", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_ged_access_logs_kit", "ged_kit_access_logs", ["kit_id"])
    op.create_index("idx_ged_access_logs_action", "ged_kit_access_logs", ["action"])
    op.create_index("idx_ged_access_logs_created", "ged_kit_access_logs", ["created_at"])

    # ════════════════════════════════════════════
    # CLIENT PORTAL TABLES
    # ════════════════════════════════════════════

    # 5. client_portal_sessions
    op.create_table(
        "client_portal_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ged_clients.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token", sa.String(500), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_client_sessions_token", "client_portal_sessions", ["token"])
    op.create_index("idx_client_sessions_client", "client_portal_sessions", ["client_id"])
    op.create_index("idx_client_sessions_expires", "client_portal_sessions", ["expires_at"])

    # 6. client_tickets
    op.create_table(
        "client_tickets",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column(
            "client_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ged_clients.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "kit_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ged_document_kits.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("status", sa.String(30), server_default=sa.text("'ABERTO'"), nullable=False),
        sa.Column("priority", sa.String(20), server_default=sa.text("'NORMAL'"), nullable=False),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_client_tickets_client", "client_tickets", ["client_id"])
    op.create_index("idx_client_tickets_status", "client_tickets", ["status"])
    op.create_index("idx_client_tickets_priority", "client_tickets", ["priority"])

    # 7. client_ticket_messages
    op.create_table(
        "client_ticket_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column(
            "ticket_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("client_tickets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("sender_type", sa.String(20), nullable=False),
        sa.Column("sender_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("sender_name", sa.String(255), nullable=True),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("attachments", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("idx_client_messages_ticket", "client_ticket_messages", ["ticket_id"])
    op.create_index("idx_client_messages_sender", "client_ticket_messages", ["sender_type"])


def downgrade() -> None:
    # Drop in reverse order (respect foreign keys)
    op.drop_table("client_ticket_messages")
    op.drop_table("client_tickets")
    op.drop_table("client_portal_sessions")
    op.drop_table("ged_kit_access_logs")
    op.drop_table("ged_kit_documents")
    op.drop_table("ged_document_kits")
    op.drop_table("ged_clients")
