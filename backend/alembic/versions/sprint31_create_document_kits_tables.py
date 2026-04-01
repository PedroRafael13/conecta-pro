"""Sprint 31: Create document_kits tables.

Revision ID: sprint31_document_kits
Revises: sprint30_bi_dashboard
Create Date: 2026-01-01 16:00:00.000000
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "sprint31_document_kits"
down_revision = "sprint30_bi_dashboard"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria tabelas de Kits Documentais."""
    # Criar enums
    kit_type_enum = postgresql.ENUM(
        "ADMISSAO",
        "DEMISSAO",
        "FERIAS",
        "AFASTAMENTO",
        "PROMOCAO",
        "TRANSFERENCIA",
        "CONTRATO_CLIENTE",
        "ENCERRAMENTO_CONTRATO",
        "TREINAMENTO",
        "CERTIFICACAO",
        "VIGILANTE",
        "EQUIPAMENTO",
        "AUDITORIA",
        "LICITACAO",
        "RENOVACAO",
        "OUTRO",
        name="kit_type_enum",
        create_type=True,
    )

    kit_status_enum = postgresql.ENUM(
        "RASCUNHO",
        "ATIVO",
        "INATIVO",
        "ARQUIVADO",
        "OBSOLETO",
        name="kit_status_enum",
        create_type=True,
    )

    item_type_enum = postgresql.ENUM(
        "DOCUMENTO_PESSOAL",
        "CERTIFICADO",
        "COMPROVANTE",
        "DECLARACAO",
        "CONTRATO",
        "TERMO",
        "FORMULARIO",
        "FOTO",
        "LAUDO",
        "ATESTADO",
        "REGISTRO",
        "AUTORIZACAO",
        "PROCURACAO",
        "OUTRO",
        name="item_type_enum",
        create_type=True,
    )

    item_priority_enum = postgresql.ENUM(
        "OBRIGATORIO",
        "IMPORTANTE",
        "DESEJAVEL",
        "OPCIONAL",
        name="item_priority_enum",
        create_type=True,
    )

    assignment_status_enum = postgresql.ENUM(
        "PENDENTE",
        "EM_ANDAMENTO",
        "AGUARDANDO_DOCUMENTOS",
        "EM_ANALISE",
        "APROVADO",
        "REPROVADO",
        "COMPLETO",
        "INCOMPLETO",
        "CANCELADO",
        "EXPIRADO",
        name="assignment_status_enum",
        create_type=True,
    )

    item_status_enum = postgresql.ENUM(
        "PENDENTE",
        "ENVIADO",
        "EM_ANALISE",
        "APROVADO",
        "REPROVADO",
        "VENCIDO",
        "NAO_APLICAVEL",
        name="item_status_enum",
        create_type=True,
    )

    entity_type_enum = postgresql.ENUM(
        "FUNCIONARIO",
        "CANDIDATO",
        "CONTRATO",
        "CLIENTE",
        "FORNECEDOR",
        "EQUIPAMENTO",
        "POSTO",
        "TREINAMENTO",
        "OUTRO",
        name="entity_type_enum",
        create_type=True,
    )

    # Criar enums no banco
    kit_type_enum.create(op.get_bind(), checkfirst=True)
    kit_status_enum.create(op.get_bind(), checkfirst=True)
    item_type_enum.create(op.get_bind(), checkfirst=True)
    item_priority_enum.create(op.get_bind(), checkfirst=True)
    assignment_status_enum.create(op.get_bind(), checkfirst=True)
    item_status_enum.create(op.get_bind(), checkfirst=True)
    entity_type_enum.create(op.get_bind(), checkfirst=True)

    # Tabela document_kits
    op.create_table(
        "document_kits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("condominios.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("codigo", sa.String(50), nullable=False, index=True),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text),
        sa.Column(
            "tipo",
            kit_type_enum,
            nullable=False,
            server_default="OUTRO",
            index=True,
        ),
        sa.Column(
            "status",
            kit_status_enum,
            nullable=False,
            server_default="RASCUNHO",
            index=True,
        ),
        sa.Column("is_template", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_obrigatorio", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("prazo_dias", sa.Integer, server_default="30"),
        sa.Column("permite_parcial", sa.Boolean, server_default="false"),
        sa.Column("requer_aprovacao", sa.Boolean, server_default="true"),
        sa.Column("entity_types", postgresql.JSONB, server_default="[]"),
        sa.Column("departamentos", postgresql.JSONB, server_default="[]"),
        sa.Column("cargos", postgresql.JSONB, server_default="[]"),
        sa.Column("total_itens", sa.Integer, nullable=False, server_default="0"),
        sa.Column("itens_obrigatorios", sa.Integer, nullable=False, server_default="0"),
        sa.Column("uso_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("versao", sa.Integer, nullable=False, server_default="1"),
        sa.Column(
            "versao_anterior_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("document_kits.id"),
        ),
        sa.Column("tags", postgresql.JSONB, server_default="[]"),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
        ),
        sa.Column(
            "updated_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    # Tabela document_kit_items
    op.create_table(
        "document_kit_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "kit_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("document_kits.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("condominios.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("codigo", sa.String(50), nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text),
        sa.Column("instrucoes", sa.Text),
        sa.Column(
            "tipo",
            item_type_enum,
            nullable=False,
            server_default="DOCUMENTO_PESSOAL",
        ),
        sa.Column(
            "prioridade",
            item_priority_enum,
            nullable=False,
            server_default="OBRIGATORIO",
        ),
        sa.Column("ordem", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_ativo", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("formatos_aceitos", postgresql.JSONB, server_default="[]"),
        sa.Column("tamanho_max_mb", sa.Integer, server_default="10"),
        sa.Column("requer_validade", sa.Boolean, server_default="false"),
        sa.Column("validade_minima_dias", sa.Integer),
        sa.Column("requer_autenticacao", sa.Boolean, server_default="false"),
        sa.Column("template_url", sa.String(500)),
        sa.Column("exemplo_url", sa.String(500)),
        sa.Column(
            "depende_de",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("document_kit_items.id"),
        ),
        sa.Column("tags", postgresql.JSONB, server_default="[]"),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    # Tabela document_kit_assignments
    op.create_table(
        "document_kit_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "kit_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("document_kits.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("condominios.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("entity_type", entity_type_enum, nullable=False, index=True),
        sa.Column(
            "entity_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
            index=True,
        ),
        sa.Column("entity_nome", sa.String(200)),
        sa.Column(
            "status",
            assignment_status_enum,
            nullable=False,
            server_default="PENDENTE",
            index=True,
        ),
        sa.Column(
            "data_inicio",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("data_limite", sa.DateTime),
        sa.Column("data_conclusao", sa.DateTime),
        sa.Column("total_itens", sa.Integer, nullable=False, server_default="0"),
        sa.Column("itens_pendentes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("itens_aprovados", sa.Integer, nullable=False, server_default="0"),
        sa.Column("itens_reprovados", sa.Integer, nullable=False, server_default="0"),
        sa.Column("percentual_completo", sa.Integer, nullable=False, server_default="0"),
        sa.Column(
            "responsavel_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
        ),
        sa.Column(
            "aprovador_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
        ),
        sa.Column("observacoes", sa.Text),
        sa.Column("motivo_reprovacao", sa.Text),
        sa.Column("notificacao_enviada", sa.Boolean, server_default="false"),
        sa.Column("ultima_notificacao_at", sa.DateTime),
        sa.Column("notificacoes_count", sa.Integer, server_default="0"),
        sa.Column("metadata", postgresql.JSONB, server_default="{}"),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
        ),
        sa.Column(
            "approved_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
        ),
        sa.Column("approved_at", sa.DateTime),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    # Tabela document_kit_item_statuses
    op.create_table(
        "document_kit_item_statuses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "assignment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("document_kit_assignments.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("document_kit_items.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "condominio_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("condominios.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "status",
            item_status_enum,
            nullable=False,
            server_default="PENDENTE",
            index=True,
        ),
        sa.Column("documento_id", postgresql.UUID(as_uuid=True)),
        sa.Column("arquivo_url", sa.String(500)),
        sa.Column("arquivo_nome", sa.String(255)),
        sa.Column("arquivo_tamanho", sa.Integer),
        sa.Column("arquivo_tipo", sa.String(100)),
        sa.Column("data_validade", sa.DateTime),
        sa.Column("is_vencido", sa.Boolean, server_default="false"),
        sa.Column(
            "analisado_por",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
        ),
        sa.Column("analisado_at", sa.DateTime),
        sa.Column("observacoes_analise", sa.Text),
        sa.Column("motivo_reprovacao", sa.Text),
        sa.Column("tentativas", sa.Integer, nullable=False, server_default="0"),
        sa.Column("historico", postgresql.JSONB, server_default="[]"),
        sa.Column(
            "enviado_por",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
        ),
        sa.Column("enviado_at", sa.DateTime),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    # Criar indices adicionais
    op.create_index(
        "ix_document_kits_codigo_condominio",
        "document_kits",
        ["codigo", "condominio_id"],
        unique=True,
    )
    op.create_index(
        "ix_document_kit_assignments_entity",
        "document_kit_assignments",
        ["entity_type", "entity_id"],
    )
    op.create_index(
        "ix_document_kit_item_statuses_assignment_item",
        "document_kit_item_statuses",
        ["assignment_id", "item_id"],
        unique=True,
    )


def downgrade() -> None:
    """Remove tabelas de Kits Documentais."""
    # Remover indices
    op.drop_index("ix_document_kit_item_statuses_assignment_item")
    op.drop_index("ix_document_kit_assignments_entity")
    op.drop_index("ix_document_kits_codigo_condominio")

    # Remover tabelas
    op.drop_table("document_kit_item_statuses")
    op.drop_table("document_kit_assignments")
    op.drop_table("document_kit_items")
    op.drop_table("document_kits")

    # Remover enums
    op.execute("DROP TYPE IF EXISTS entity_type_enum")
    op.execute("DROP TYPE IF EXISTS item_status_enum")
    op.execute("DROP TYPE IF EXISTS assignment_status_enum")
    op.execute("DROP TYPE IF EXISTS item_priority_enum")
    op.execute("DROP TYPE IF EXISTS item_type_enum")
    op.execute("DROP TYPE IF EXISTS kit_status_enum")
    op.execute("DROP TYPE IF EXISTS kit_type_enum")
