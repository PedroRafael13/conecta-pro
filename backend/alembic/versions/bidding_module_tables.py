"""Create bidding module tables

Revision ID: bidding_001
Revises: None
Create Date: 2026-01-11

Tabelas do modulo de licitacoes publicas:
- bidding_tenders (Editais)
- bidding_tender_documents (Documentos do Edital)
- bidding_company_documents (Documentos da Empresa)
- bidding_proposals (Propostas)
- bidding_proposal_items (Itens da Proposta)
- bidding_public_contracts (Contratos Publicos)
- bidding_measurements (Medicoes)
- bidding_certificates (Certidoes)
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision = "bidding_001"
down_revision = None
branch_labels = ("bidding",)
depends_on = None


def upgrade():
    # ===================================================================
    # TABELA: bidding_tenders (Editais)
    # ===================================================================
    op.create_table(
        "bidding_tenders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("numero", sa.String(50), nullable=False, index=True),
        sa.Column("numero_processo", sa.String(50), nullable=True),
        sa.Column("ano", sa.Integer(), nullable=False, index=True),
        # Orgao/Entidade
        sa.Column("orgao_cnpj", sa.String(18), nullable=False, index=True),
        sa.Column("orgao_nome", sa.String(255), nullable=False),
        sa.Column("orgao_uf", sa.String(2), nullable=False, default="AM", index=True),
        sa.Column("orgao_municipio", sa.String(100), nullable=True),
        sa.Column("unidade_gestora", sa.String(100), nullable=True),
        # Modalidade e Tipo
        sa.Column("modalidade", sa.String(50), nullable=False, index=True),
        sa.Column("criterio_julgamento", sa.String(50), nullable=False, default="menor_preco"),
        sa.Column("tipo_contratacao", sa.String(50), nullable=True),
        sa.Column("regime_execucao", sa.String(50), nullable=True),
        # Objeto
        sa.Column("objeto", sa.Text(), nullable=False),
        sa.Column("objeto_resumido", sa.String(500), nullable=True),
        # Valores
        sa.Column("valor_estimado", sa.Numeric(15, 2), nullable=True),
        sa.Column("valor_homologado", sa.Numeric(15, 2), nullable=True),
        # Datas
        sa.Column("data_publicacao", sa.DateTime(), nullable=True, index=True),
        sa.Column("data_abertura", sa.DateTime(), nullable=True, index=True),
        sa.Column("data_encerramento_propostas", sa.DateTime(), nullable=True),
        sa.Column("data_impugnacao_limite", sa.DateTime(), nullable=True),
        sa.Column("data_esclarecimentos_limite", sa.DateTime(), nullable=True),
        sa.Column("data_resultado", sa.DateTime(), nullable=True),
        sa.Column("data_homologacao", sa.DateTime(), nullable=True),
        # Status e controle
        sa.Column("status", sa.String(30), nullable=False, default="draft", index=True),
        sa.Column("ativo", sa.Boolean(), default=True, nullable=False, index=True),
        # Integracao PNCP
        sa.Column("pncp_id", sa.String(100), nullable=True, unique=True, index=True),
        sa.Column("pncp_link", sa.String(500), nullable=True),
        sa.Column("pncp_ultima_sync", sa.DateTime(), nullable=True),
        # Participacao da empresa
        sa.Column("participando", sa.Boolean(), default=False, index=True),
        sa.Column("interesse", sa.Boolean(), default=False),
        sa.Column("motivo_nao_participacao", sa.Text(), nullable=True),
        # Segmentacao
        sa.Column("segmento", sa.String(100), nullable=True, index=True),
        sa.Column("tags", postgresql.JSONB(), default=[]),
        # Requisitos e documentos
        sa.Column("requisitos", postgresql.JSONB(), default=[]),
        sa.Column("documentos_exigidos", postgresql.JSONB(), default=[]),
        # Anexos
        sa.Column("anexos", postgresql.JSONB(), default=[]),
        # Informacoes adicionais
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("fonte", sa.String(50), default="manual"),
        # Auditoria
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Indices compostos para tenders
    op.create_index("idx_tender_orgao_ano", "bidding_tenders", ["orgao_cnpj", "ano"])
    op.create_index("idx_tender_modalidade_status", "bidding_tenders", ["modalidade", "status"])
    op.create_index("idx_tender_uf_segmento", "bidding_tenders", ["orgao_uf", "segmento"])
    op.create_index("idx_tender_participando", "bidding_tenders", ["participando", "status"])

    # ===================================================================
    # TABELA: bidding_tender_documents (Documentos do Edital)
    # ===================================================================
    op.create_table(
        "bidding_tender_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tender_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bidding_tenders.id"), nullable=False, index=True
        ),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("tipo", sa.String(50), nullable=False),
        sa.Column("arquivo_url", sa.String(500), nullable=True),
        sa.Column("arquivo_nome", sa.String(255), nullable=True),
        sa.Column("arquivo_tamanho", sa.Integer(), nullable=True),
        sa.Column("arquivo_hash", sa.String(64), nullable=True),
        sa.Column("ordem", sa.Integer(), default=0),
        sa.Column("obrigatorio", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # ===================================================================
    # TABELA: bidding_company_documents (Documentos da Empresa)
    # ===================================================================
    op.create_table(
        "bidding_company_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tipo", sa.String(50), nullable=False, index=True),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("numero", sa.String(100), nullable=True),
        sa.Column("data_emissao", sa.Date(), nullable=True),
        sa.Column("data_validade", sa.Date(), nullable=True, index=True),
        sa.Column("arquivo_url", sa.String(500), nullable=True),
        sa.Column("arquivo_nome", sa.String(255), nullable=True),
        sa.Column("arquivo_tamanho", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, default="pending", index=True),
        sa.Column("ativo", sa.Boolean(), default=True, nullable=False, index=True),
        sa.Column("certidao_automatica", sa.Boolean(), default=False),
        sa.Column("ultima_verificacao", sa.DateTime(), nullable=True),
        sa.Column("ultima_renovacao", sa.DateTime(), nullable=True),
        sa.Column("erro_renovacao", sa.Text(), nullable=True),
        sa.Column("orgao_emissor", sa.String(255), nullable=True),
        sa.Column("metadados", postgresql.JSONB(), default={}),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.create_index("idx_company_doc_tipo_status", "bidding_company_documents", ["tipo", "status"])
    op.create_index("idx_company_doc_validade", "bidding_company_documents", ["data_validade"])

    # ===================================================================
    # TABELA: bidding_proposals (Propostas)
    # ===================================================================
    op.create_table(
        "bidding_proposals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tender_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bidding_tenders.id"), nullable=False, index=True
        ),
        sa.Column("numero", sa.String(50), nullable=False),
        sa.Column("versao", sa.Integer(), default=1, nullable=False),
        sa.Column("valor_total", sa.Numeric(15, 2), nullable=False),
        sa.Column("valor_unitario", sa.Numeric(15, 4), nullable=True),
        sa.Column("desconto_percentual", sa.Numeric(5, 2), nullable=True),
        sa.Column("bdi_percentual", sa.Numeric(5, 2), nullable=True),
        sa.Column("bdi_detalhamento", postgresql.JSONB(), default={}),
        sa.Column("encargos_sociais", sa.Numeric(5, 2), nullable=True),
        sa.Column("encargos_detalhamento", postgresql.JSONB(), default={}),
        sa.Column("itens", postgresql.JSONB(), default=[]),
        sa.Column("status", sa.String(30), nullable=False, default="draft", index=True),
        sa.Column("ativo", sa.Boolean(), default=True, nullable=False),
        sa.Column("posicao_classificacao", sa.Integer(), nullable=True),
        sa.Column("valor_lance_final", sa.Numeric(15, 2), nullable=True),
        sa.Column("arquivo_pdf_url", sa.String(500), nullable=True),
        sa.Column("arquivo_planilha_url", sa.String(500), nullable=True),
        sa.Column("data_envio", sa.DateTime(), nullable=True),
        sa.Column("data_resultado", sa.DateTime(), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        sa.Column("justificativa_preco", sa.Text(), nullable=True),
        sa.Column("historico_lances", postgresql.JSONB(), default=[]),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.create_index("idx_proposal_tender_status", "bidding_proposals", ["tender_id", "status"])
    op.create_index("idx_proposal_versao", "bidding_proposals", ["tender_id", "versao"])

    # ===================================================================
    # TABELA: bidding_proposal_items (Itens da Proposta)
    # ===================================================================
    op.create_table(
        "bidding_proposal_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "proposal_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("bidding_proposals.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("numero_item", sa.Integer(), nullable=False),
        sa.Column("codigo", sa.String(50), nullable=True),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("unidade", sa.String(20), nullable=False),
        sa.Column("quantidade", sa.Numeric(15, 4), nullable=False),
        sa.Column("valor_unitario", sa.Numeric(15, 4), nullable=False),
        sa.Column("valor_total", sa.Numeric(15, 2), nullable=False),
        sa.Column("custo_direto", sa.Numeric(15, 2), nullable=True),
        sa.Column("custo_indireto", sa.Numeric(15, 2), nullable=True),
        sa.Column("margem", sa.Numeric(15, 2), nullable=True),
        sa.Column("composicao", postgresql.JSONB(), default={}),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # ===================================================================
    # TABELA: bidding_public_contracts (Contratos Publicos)
    # ===================================================================
    op.create_table(
        "bidding_public_contracts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tender_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bidding_tenders.id"), nullable=True, index=True
        ),
        sa.Column("numero_contrato", sa.String(50), nullable=False, index=True),
        sa.Column("ano_contrato", sa.Integer(), nullable=False, index=True),
        sa.Column("objeto", sa.Text(), nullable=False),
        sa.Column("objeto_resumido", sa.String(500), nullable=True),
        # Orgao contratante
        sa.Column("orgao_cnpj", sa.String(18), nullable=False, index=True),
        sa.Column("orgao_nome", sa.String(255), nullable=False),
        sa.Column("orgao_uf", sa.String(2), nullable=False, default="AM"),
        sa.Column("unidade_gestora", sa.String(100), nullable=True),
        sa.Column("gestor_contrato", sa.String(255), nullable=True),
        sa.Column("fiscal_contrato", sa.String(255), nullable=True),
        # Valores
        sa.Column("valor_contrato", sa.Numeric(15, 2), nullable=False),
        sa.Column("valor_empenhado", sa.Numeric(15, 2), nullable=True, default=0),
        sa.Column("valor_executado", sa.Numeric(15, 2), nullable=True, default=0),
        sa.Column("valor_pago", sa.Numeric(15, 2), nullable=True, default=0),
        sa.Column("saldo_contrato", sa.Numeric(15, 2), nullable=True),
        # Empenho
        sa.Column("numero_empenho", sa.String(50), nullable=True, index=True),
        sa.Column("data_empenho", sa.Date(), nullable=True),
        sa.Column("nota_empenho_url", sa.String(500), nullable=True),
        # Vigencia
        sa.Column("data_assinatura", sa.Date(), nullable=True),
        sa.Column("data_publicacao", sa.Date(), nullable=True),
        sa.Column("data_vigencia_inicio", sa.Date(), nullable=False),
        sa.Column("data_vigencia_fim", sa.Date(), nullable=False, index=True),
        sa.Column("prazo_meses", sa.Integer(), nullable=True),
        # Reajuste
        sa.Column("indice_reajuste", sa.String(20), nullable=True, default="igpm"),
        sa.Column("data_base_reajuste", sa.Date(), nullable=True),
        sa.Column("ultimo_reajuste", sa.Date(), nullable=True),
        sa.Column("percentual_ultimo_reajuste", sa.Numeric(5, 2), nullable=True),
        # Garantia
        sa.Column("garantia_tipo", sa.String(30), nullable=True),
        sa.Column("garantia_valor", sa.Numeric(15, 2), nullable=True),
        sa.Column("garantia_percentual", sa.Numeric(5, 2), nullable=True),
        sa.Column("garantia_vencimento", sa.Date(), nullable=True),
        sa.Column("garantia_documento_url", sa.String(500), nullable=True),
        # Status e controle
        sa.Column("status", sa.String(30), nullable=False, default="draft", index=True),
        sa.Column("ativo", sa.Boolean(), default=True, nullable=False, index=True),
        # Aditivos
        sa.Column("aditivos", postgresql.JSONB(), default=[]),
        sa.Column("quantidade_aditivos", sa.Integer(), default=0),
        # Integracao PNCP
        sa.Column("pncp_id", sa.String(100), nullable=True, unique=True, index=True),
        sa.Column("pncp_link", sa.String(500), nullable=True),
        # Arquivos
        sa.Column("arquivo_contrato_url", sa.String(500), nullable=True),
        sa.Column("arquivo_publicacao_url", sa.String(500), nullable=True),
        # Observacoes
        sa.Column("observacoes", sa.Text(), nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.create_index("idx_contract_orgao_ano", "bidding_public_contracts", ["orgao_cnpj", "ano_contrato"])
    op.create_index("idx_contract_status_vigencia", "bidding_public_contracts", ["status", "data_vigencia_fim"])
    op.create_index("idx_contract_tender", "bidding_public_contracts", ["tender_id"])

    # ===================================================================
    # TABELA: bidding_measurements (Medicoes)
    # ===================================================================
    op.create_table(
        "bidding_measurements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "contrato_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("bidding_public_contracts.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("numero_medicao", sa.Integer(), nullable=False),
        sa.Column("competencia", sa.String(7), nullable=False),
        sa.Column("tipo", sa.String(30), nullable=False, default="mensal"),
        # Periodo
        sa.Column("periodo_inicio", sa.Date(), nullable=False),
        sa.Column("periodo_fim", sa.Date(), nullable=False),
        # Valores
        sa.Column("valor_bruto", sa.Numeric(15, 2), nullable=False),
        sa.Column("valor_retencoes", sa.Numeric(15, 2), nullable=True, default=0),
        sa.Column("valor_glosas", sa.Numeric(15, 2), nullable=True, default=0),
        sa.Column("valor_liquido", sa.Numeric(15, 2), nullable=False),
        # Retencoes detalhadas
        sa.Column("retencao_iss", sa.Numeric(15, 2), nullable=True, default=0),
        sa.Column("retencao_inss", sa.Numeric(15, 2), nullable=True, default=0),
        sa.Column("retencao_irrf", sa.Numeric(15, 2), nullable=True, default=0),
        sa.Column("retencao_pis_cofins_csll", sa.Numeric(15, 2), nullable=True, default=0),
        sa.Column("outras_retencoes", sa.Numeric(15, 2), nullable=True, default=0),
        # Glosas
        sa.Column("glosas_detalhamento", postgresql.JSONB(), default=[]),
        # Itens
        sa.Column("itens_medidos", postgresql.JSONB(), default=[]),
        # Status
        sa.Column("status", sa.String(30), nullable=False, default="draft", index=True),
        sa.Column("ativo", sa.Boolean(), default=True, nullable=False),
        # Datas do processo
        sa.Column("data_envio", sa.Date(), nullable=True),
        sa.Column("data_ateste", sa.Date(), nullable=True),
        sa.Column("data_aprovacao", sa.Date(), nullable=True),
        sa.Column("data_pagamento", sa.Date(), nullable=True),
        # Aprovacao
        sa.Column("aprovador_nome", sa.String(255), nullable=True),
        sa.Column("aprovador_cargo", sa.String(100), nullable=True),
        sa.Column("observacoes_aprovador", sa.Text(), nullable=True),
        # Nota Fiscal
        sa.Column("nota_fiscal_numero", sa.String(50), nullable=True),
        sa.Column("nota_fiscal_data", sa.Date(), nullable=True),
        sa.Column("nota_fiscal_url", sa.String(500), nullable=True),
        # Arquivos
        sa.Column("relatorio_url", sa.String(500), nullable=True),
        sa.Column("planilha_url", sa.String(500), nullable=True),
        sa.Column("fotos_url", postgresql.JSONB(), default=[]),
        # Observacoes
        sa.Column("descricao_servicos", sa.Text(), nullable=True),
        sa.Column("observacoes", sa.Text(), nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.create_index("idx_measurement_contrato_numero", "bidding_measurements", ["contrato_id", "numero_medicao"])
    op.create_index("idx_measurement_competencia", "bidding_measurements", ["competencia"])
    op.create_index("idx_measurement_status", "bidding_measurements", ["status"])

    # ===================================================================
    # TABELA: bidding_certificates (Certidoes)
    # ===================================================================
    op.create_table(
        "bidding_certificates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tipo", sa.String(50), nullable=False, index=True),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("codigo_verificacao", sa.String(100), nullable=True),
        # Empresa
        sa.Column("cnpj", sa.String(18), nullable=False, index=True),
        sa.Column("razao_social", sa.String(255), nullable=True),
        # Datas
        sa.Column("data_emissao", sa.DateTime(), nullable=True),
        sa.Column("data_validade", sa.DateTime(), nullable=True, index=True),
        sa.Column("hora_emissao", sa.String(8), nullable=True),
        # Conteudo
        sa.Column("situacao", sa.String(100), nullable=True),
        sa.Column("texto_certidao", sa.Text(), nullable=True),
        sa.Column("observacoes_orgao", sa.Text(), nullable=True),
        # Arquivo
        sa.Column("arquivo_url", sa.String(500), nullable=True),
        sa.Column("arquivo_nome", sa.String(255), nullable=True),
        sa.Column("arquivo_hash", sa.String(64), nullable=True),
        # Status e controle
        sa.Column("status", sa.String(30), nullable=False, default="pending", index=True),
        sa.Column("ativo", sa.Boolean(), default=True, nullable=False, index=True),
        # Obtencao automatica
        sa.Column("fonte", sa.String(30), nullable=False, default="manual"),
        sa.Column("obtencao_automatica", sa.Boolean(), default=False),
        sa.Column("ultima_tentativa", sa.DateTime(), nullable=True),
        sa.Column("proxima_tentativa", sa.DateTime(), nullable=True),
        sa.Column("tentativas_falha", sa.Integer(), default=0),
        sa.Column("erro_obtencao", sa.Text(), nullable=True),
        # Alertas
        sa.Column("alerta_enviado_30d", sa.Boolean(), default=False),
        sa.Column("alerta_enviado_15d", sa.Boolean(), default=False),
        sa.Column("alerta_enviado_7d", sa.Boolean(), default=False),
        # Orgao emissor
        sa.Column("orgao_emissor", sa.String(255), nullable=True),
        sa.Column("orgao_uf", sa.String(2), nullable=True),
        sa.Column("orgao_url", sa.String(500), nullable=True),
        # Metadados
        sa.Column("metadados", postgresql.JSONB(), default={}),
        # Observacoes
        sa.Column("observacoes", sa.Text(), nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.create_index("idx_certificate_cnpj_tipo", "bidding_certificates", ["cnpj", "tipo"])
    op.create_index("idx_certificate_validade", "bidding_certificates", ["data_validade"])
    op.create_index("idx_certificate_status", "bidding_certificates", ["status"])
    op.create_index("idx_certificate_obtencao", "bidding_certificates", ["obtencao_automatica", "proxima_tentativa"])


def downgrade():
    op.drop_table("bidding_certificates")
    op.drop_table("bidding_measurements")
    op.drop_table("bidding_public_contracts")
    op.drop_table("bidding_proposal_items")
    op.drop_table("bidding_proposals")
    op.drop_table("bidding_company_documents")
    op.drop_table("bidding_tender_documents")
    op.drop_table("bidding_tenders")
