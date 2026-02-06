"""Criar tabelas de sincronizacao governamental completas.

Revision ID: sprint56_gov_sync
Revises:
Create Date: 2026-01-16

Tabelas criadas:
- gov_extratos_fgts
- gov_debitos_fgts
- gov_movimentacoes_fgts
- gov_eventos_reinf
- gov_totalizadores_reinf
- gov_retencoes_reinf
- gov_declaracoes_dctfweb
- gov_debitos_dctfweb
- gov_creditos_dctfweb
- gov_escrituracoes_sped
- gov_contas_contabeis
- gov_saldos_contabeis
- gov_apuracoes_icms
- gov_apuracoes_ipi
- gov_dps_pendentes
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid


revision = 'sprint56_gov_sync'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # =========================================================================
    # FGTS DIGITAL
    # =========================================================================

    op.create_table(
        'gov_extratos_fgts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.Column('ativo', sa.Boolean(), default=True, nullable=False),

        sa.Column('cnpj_empresa', sa.String(14), nullable=False, index=True),
        sa.Column('cpf_funcionario', sa.String(11), nullable=False, index=True),
        sa.Column('nome_funcionario', sa.String(200)),
        sa.Column('pis', sa.String(11)),
        sa.Column('numero_conta', sa.String(30)),
        sa.Column('data_abertura', sa.Date()),

        sa.Column('saldo_anterior', sa.Numeric(15, 2), default=0),
        sa.Column('depositos', sa.Numeric(15, 2), default=0),
        sa.Column('saques', sa.Numeric(15, 2), default=0),
        sa.Column('juros_jam', sa.Numeric(15, 2), default=0),
        sa.Column('saldo_atual', sa.Numeric(15, 2), default=0),

        sa.Column('movimentacoes', JSONB),
        sa.Column('sync_id', UUID(as_uuid=True)),
    )
    op.create_index('ix_extrato_fgts_cnpj_cpf', 'gov_extratos_fgts', ['cnpj_empresa', 'cpf_funcionario'])

    op.create_table(
        'gov_debitos_fgts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.Column('ativo', sa.Boolean(), default=True, nullable=False),

        sa.Column('cnpj_empresa', sa.String(14), nullable=False, index=True),
        sa.Column('numero_debito', sa.String(50), index=True),
        sa.Column('competencia', sa.String(7)),
        sa.Column('origem', sa.String(100)),

        sa.Column('valor_original', sa.Numeric(15, 2), nullable=False),
        sa.Column('valor_atualizado', sa.Numeric(15, 2)),
        sa.Column('data_vencimento', sa.Date()),
        sa.Column('situacao', sa.String(50)),
        sa.Column('parcelado', sa.Boolean(), default=False),
        sa.Column('numero_parcelamento', sa.String(50)),

        sa.Column('sync_id', UUID(as_uuid=True)),
    )

    op.create_table(
        'gov_movimentacoes_fgts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.Column('ativo', sa.Boolean(), default=True, nullable=False),

        sa.Column('cnpj_empresa', sa.String(14), nullable=False, index=True),
        sa.Column('cpf_funcionario', sa.String(11), nullable=False, index=True),
        sa.Column('nome_funcionario', sa.String(200)),
        sa.Column('tipo_movimentacao', sa.String(50)),
        sa.Column('codigo_movimentacao', sa.String(10)),
        sa.Column('descricao', sa.String(200)),
        sa.Column('data_movimentacao', sa.Date()),

        sa.Column('valor_base', sa.Numeric(15, 2), default=0),
        sa.Column('valor_deposito', sa.Numeric(15, 2), default=0),
        sa.Column('processado', sa.Boolean(), default=False),

        sa.Column('sync_id', UUID(as_uuid=True)),
    )

    # =========================================================================
    # EFD-REINF
    # =========================================================================

    op.create_table(
        'gov_eventos_reinf',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.Column('ativo', sa.Boolean(), default=True, nullable=False),

        sa.Column('cnpj_empresa', sa.String(14), nullable=False, index=True),
        sa.Column('id_evento', sa.String(50), unique=True, index=True),
        sa.Column('tipo_evento', sa.String(20), nullable=False, index=True),
        sa.Column('descricao_evento', sa.String(200)),
        sa.Column('periodo_apuracao', sa.String(7)),

        sa.Column('data_envio', sa.DateTime()),
        sa.Column('status', sa.String(20), default='pendente'),
        sa.Column('protocolo', sa.String(50)),
        sa.Column('recibo', sa.String(50)),

        sa.Column('dados_evento', JSONB),
        sa.Column('xml_envio', sa.LargeBinary()),

        sa.Column('sync_id', UUID(as_uuid=True)),
    )
    op.create_index('ix_reinf_cnpj_periodo', 'gov_eventos_reinf', ['cnpj_empresa', 'periodo_apuracao'])

    op.create_table(
        'gov_totalizadores_reinf',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.Column('ativo', sa.Boolean(), default=True, nullable=False),

        sa.Column('cnpj_empresa', sa.String(14), nullable=False, index=True),
        sa.Column('tipo_evento', sa.String(20), nullable=False),
        sa.Column('periodo_apuracao', sa.String(7), nullable=False),

        sa.Column('base_calculo_cp', sa.Numeric(15, 2), default=0),
        sa.Column('valor_cp_patronal', sa.Numeric(15, 2), default=0),
        sa.Column('valor_cp_descontada', sa.Numeric(15, 2), default=0),
        sa.Column('valor_cprb', sa.Numeric(15, 2), default=0),

        sa.Column('base_calculo_ir', sa.Numeric(15, 2), default=0),
        sa.Column('valor_ir_retido', sa.Numeric(15, 2), default=0),
        sa.Column('valor_csll_retido', sa.Numeric(15, 2), default=0),
        sa.Column('valor_cofins_retido', sa.Numeric(15, 2), default=0),
        sa.Column('valor_pis_retido', sa.Numeric(15, 2), default=0),

        sa.Column('dados_completos', JSONB),
        sa.Column('sync_id', UUID(as_uuid=True)),

        sa.UniqueConstraint('cnpj_empresa', 'tipo_evento', 'periodo_apuracao', name='uq_totalizador_reinf'),
    )

    op.create_table(
        'gov_retencoes_reinf',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.Column('ativo', sa.Boolean(), default=True, nullable=False),

        sa.Column('cnpj_empresa', sa.String(14), nullable=False, index=True),
        sa.Column('tipo_retencao', sa.String(20)),
        sa.Column('cnpj_prestador', sa.String(14), index=True),
        sa.Column('cnpj_tomador', sa.String(14)),
        sa.Column('periodo_apuracao', sa.String(7)),
        sa.Column('data_pagamento', sa.Date()),

        sa.Column('valor_bruto', sa.Numeric(15, 2), default=0),
        sa.Column('base_retencao', sa.Numeric(15, 2), default=0),
        sa.Column('valor_retencao_cp', sa.Numeric(15, 2), default=0),
        sa.Column('valor_retencao_ir', sa.Numeric(15, 2), default=0),
        sa.Column('valor_retencao_csll', sa.Numeric(15, 2), default=0),
        sa.Column('valor_retencao_cofins', sa.Numeric(15, 2), default=0),
        sa.Column('valor_retencao_pis', sa.Numeric(15, 2), default=0),

        sa.Column('numero_nf', sa.String(20)),
        sa.Column('serie_nf', sa.String(5)),

        sa.Column('sync_id', UUID(as_uuid=True)),
    )

    # =========================================================================
    # DCTFWeb
    # =========================================================================

    op.create_table(
        'gov_declaracoes_dctfweb',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.Column('ativo', sa.Boolean(), default=True, nullable=False),

        sa.Column('cnpj_empresa', sa.String(14), nullable=False, index=True),
        sa.Column('numero_recibo', sa.String(50), unique=True, index=True),
        sa.Column('tipo_declaracao', sa.String(10)),
        sa.Column('descricao_tipo', sa.String(50)),
        sa.Column('periodo_apuracao', sa.String(7), nullable=False),

        sa.Column('data_transmissao', sa.DateTime()),
        sa.Column('situacao', sa.String(50)),
        sa.Column('retificadora', sa.Boolean(), default=False),
        sa.Column('numero_recibo_retificada', sa.String(50)),

        sa.Column('valor_total_debitos', sa.Numeric(15, 2), default=0),
        sa.Column('valor_total_creditos', sa.Numeric(15, 2), default=0),
        sa.Column('valor_total_pagar', sa.Numeric(15, 2), default=0),

        sa.Column('sync_id', UUID(as_uuid=True)),
    )
    op.create_index('ix_dctfweb_cnpj_periodo', 'gov_declaracoes_dctfweb', ['cnpj_empresa', 'periodo_apuracao'])

    op.create_table(
        'gov_debitos_dctfweb',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.Column('ativo', sa.Boolean(), default=True, nullable=False),

        sa.Column('cnpj_empresa', sa.String(14), nullable=False, index=True),
        sa.Column('periodo_apuracao', sa.String(7), nullable=False),
        sa.Column('codigo_receita', sa.String(10), nullable=False),
        sa.Column('descricao_receita', sa.String(200)),

        sa.Column('valor_principal', sa.Numeric(15, 2), default=0),
        sa.Column('valor_multa', sa.Numeric(15, 2), default=0),
        sa.Column('valor_juros', sa.Numeric(15, 2), default=0),
        sa.Column('valor_total', sa.Numeric(15, 2), default=0),

        sa.Column('data_vencimento', sa.Date()),
        sa.Column('situacao', sa.String(50)),
        sa.Column('suspenso', sa.Boolean(), default=False),
        sa.Column('processo_suspensao', sa.String(50)),

        sa.Column('sync_id', UUID(as_uuid=True)),
    )
    op.create_index('ix_debito_dctfweb_periodo', 'gov_debitos_dctfweb', ['cnpj_empresa', 'periodo_apuracao'])

    op.create_table(
        'gov_creditos_dctfweb',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.Column('ativo', sa.Boolean(), default=True, nullable=False),

        sa.Column('cnpj_empresa', sa.String(14), nullable=False, index=True),
        sa.Column('tipo_credito', sa.String(50)),
        sa.Column('origem', sa.String(100)),
        sa.Column('periodo_apuracao', sa.String(7)),

        sa.Column('valor_original', sa.Numeric(15, 2), default=0),
        sa.Column('valor_utilizado', sa.Numeric(15, 2), default=0),
        sa.Column('valor_disponivel', sa.Numeric(15, 2), default=0),

        sa.Column('data_vinculacao', sa.Date()),
        sa.Column('debito_vinculado', sa.String(100)),

        sa.Column('sync_id', UUID(as_uuid=True)),
    )

    # =========================================================================
    # SPED FISCAL E CONTABIL
    # =========================================================================

    op.create_table(
        'gov_escrituracoes_sped',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.Column('ativo', sa.Boolean(), default=True, nullable=False),

        sa.Column('cnpj_empresa', sa.String(14), nullable=False, index=True),
        sa.Column('tipo_sped', sa.String(10), nullable=False),
        sa.Column('numero_recibo', sa.String(50), unique=True, index=True),

        sa.Column('ano_calendario', sa.Integer()),
        sa.Column('periodo_apuracao', sa.String(7)),
        sa.Column('data_inicial', sa.Date()),
        sa.Column('data_final', sa.Date()),

        sa.Column('perfil', sa.String(5)),
        sa.Column('descricao_perfil', sa.String(100)),
        sa.Column('finalidade', sa.String(50)),

        sa.Column('tipo_livro', sa.String(5)),
        sa.Column('descricao_livro', sa.String(100)),

        sa.Column('data_transmissao', sa.DateTime()),
        sa.Column('situacao', sa.String(50)),
        sa.Column('hash_arquivo', sa.String(64)),
        sa.Column('retificadora', sa.Boolean(), default=False),
        sa.Column('recibo_substituido', sa.String(50)),
        sa.Column('recibo_retificado', sa.String(50)),

        sa.Column('sync_id', UUID(as_uuid=True)),
    )
    op.create_index('ix_escrituracao_sped_cnpj', 'gov_escrituracoes_sped', ['cnpj_empresa', 'tipo_sped'])

    op.create_table(
        'gov_contas_contabeis',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.Column('ativo', sa.Boolean(), default=True, nullable=False),

        sa.Column('cnpj_empresa', sa.String(14), nullable=False, index=True),
        sa.Column('codigo_conta', sa.String(50), nullable=False),
        sa.Column('descricao', sa.String(200)),
        sa.Column('tipo_conta', sa.String(20)),
        sa.Column('natureza', sa.String(20)),
        sa.Column('nivel', sa.Integer()),
        sa.Column('codigo_superior', sa.String(50)),
        sa.Column('codigo_referencial', sa.String(50)),
        sa.Column('ano_referencia', sa.Integer()),

        sa.Column('sync_id', UUID(as_uuid=True)),
    )
    op.create_index('ix_conta_contabil_cnpj', 'gov_contas_contabeis', ['cnpj_empresa', 'codigo_conta'])

    op.create_table(
        'gov_saldos_contabeis',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.Column('ativo', sa.Boolean(), default=True, nullable=False),

        sa.Column('cnpj_empresa', sa.String(14), nullable=False, index=True),
        sa.Column('codigo_conta', sa.String(50), nullable=False),
        sa.Column('periodo', sa.String(7), nullable=False),

        sa.Column('saldo_inicial_debito', sa.Numeric(15, 2), default=0),
        sa.Column('saldo_inicial_credito', sa.Numeric(15, 2), default=0),
        sa.Column('movimento_debito', sa.Numeric(15, 2), default=0),
        sa.Column('movimento_credito', sa.Numeric(15, 2), default=0),
        sa.Column('saldo_final_debito', sa.Numeric(15, 2), default=0),
        sa.Column('saldo_final_credito', sa.Numeric(15, 2), default=0),

        sa.Column('sync_id', UUID(as_uuid=True)),

        sa.UniqueConstraint('cnpj_empresa', 'codigo_conta', 'periodo', name='uq_saldo_contabil'),
    )

    op.create_table(
        'gov_apuracoes_icms',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.Column('ativo', sa.Boolean(), default=True, nullable=False),

        sa.Column('cnpj_empresa', sa.String(14), nullable=False, index=True),
        sa.Column('periodo_apuracao', sa.String(7), nullable=False),

        sa.Column('valor_total_debitos', sa.Numeric(15, 2), default=0),
        sa.Column('valor_ajustes_debitos', sa.Numeric(15, 2), default=0),
        sa.Column('valor_total_creditos', sa.Numeric(15, 2), default=0),
        sa.Column('valor_ajustes_creditos', sa.Numeric(15, 2), default=0),
        sa.Column('saldo_credor_anterior', sa.Numeric(15, 2), default=0),
        sa.Column('valor_total_deducoes', sa.Numeric(15, 2), default=0),
        sa.Column('icms_recolher', sa.Numeric(15, 2), default=0),
        sa.Column('saldo_credor_transportar', sa.Numeric(15, 2), default=0),
        sa.Column('icms_st_recolher', sa.Numeric(15, 2), default=0),
        sa.Column('difal_recolher', sa.Numeric(15, 2), default=0),
        sa.Column('fcp_recolher', sa.Numeric(15, 2), default=0),

        sa.Column('sync_id', UUID(as_uuid=True)),

        sa.UniqueConstraint('cnpj_empresa', 'periodo_apuracao', name='uq_apuracao_icms'),
    )

    op.create_table(
        'gov_apuracoes_ipi',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.Column('ativo', sa.Boolean(), default=True, nullable=False),

        sa.Column('cnpj_empresa', sa.String(14), nullable=False, index=True),
        sa.Column('periodo_apuracao', sa.String(7), nullable=False),

        sa.Column('valor_total_debitos', sa.Numeric(15, 2), default=0),
        sa.Column('valor_total_creditos', sa.Numeric(15, 2), default=0),
        sa.Column('saldo_credor_anterior', sa.Numeric(15, 2), default=0),
        sa.Column('ipi_recolher', sa.Numeric(15, 2), default=0),
        sa.Column('saldo_credor_transportar', sa.Numeric(15, 2), default=0),

        sa.Column('sync_id', UUID(as_uuid=True)),

        sa.UniqueConstraint('cnpj_empresa', 'periodo_apuracao', name='uq_apuracao_ipi'),
    )

    # =========================================================================
    # NFS-E NACIONAL
    # =========================================================================

    op.create_table(
        'gov_dps_pendentes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
        sa.Column('ativo', sa.Boolean(), default=True, nullable=False),

        sa.Column('cnpj_empresa', sa.String(14), nullable=False, index=True),
        sa.Column('id_dps', sa.String(50), unique=True, index=True),
        sa.Column('data_emissao', sa.Date()),
        sa.Column('competencia', sa.String(7)),

        sa.Column('valor_servicos', sa.Numeric(15, 2), default=0),
        sa.Column('situacao', sa.String(50)),
        sa.Column('motivo_pendencia', sa.Text()),
        sa.Column('xml_dps', sa.LargeBinary()),

        sa.Column('sync_id', UUID(as_uuid=True)),
    )

    # =========================================================================
    # ADICIONAR COLUNAS NAS TABELAS EXISTENTES
    # =========================================================================

    # Adicionar colunas em gov_documentos_fiscais (se existir)
    try:
        op.add_column('gov_documentos_fiscais', sa.Column('dados_adicionais', JSONB))
        op.add_column('gov_documentos_fiscais', sa.Column('tipo_documento', sa.String(20)))
        op.add_column('gov_documentos_fiscais', sa.Column('nome_emitente', sa.String(200)))
        op.add_column('gov_documentos_fiscais', sa.Column('nome_destinatario', sa.String(200)))
        op.add_column('gov_documentos_fiscais', sa.Column('direcao', sa.String(20)))
        op.add_column('gov_documentos_fiscais', sa.Column('codigo_servico', sa.String(20)))
        op.add_column('gov_documentos_fiscais', sa.Column('xml_documento', sa.LargeBinary()))
    except Exception:
        pass  # Tabela pode nao existir ainda

    # Adicionar coluna em gov_eventos_documentos_fiscais (se existir)
    try:
        op.add_column('gov_eventos_documentos_fiscais', sa.Column('dados_adicionais', JSONB))
    except Exception:
        pass

    # Adicionar coluna em gov_guias_recolhimento (se existir)
    try:
        op.add_column('gov_guias_recolhimento', sa.Column('dados_adicionais', JSONB))
    except Exception:
        pass


def downgrade():
    # Remover tabelas na ordem reversa
    op.drop_table('gov_dps_pendentes')
    op.drop_table('gov_apuracoes_ipi')
    op.drop_table('gov_apuracoes_icms')
    op.drop_table('gov_saldos_contabeis')
    op.drop_table('gov_contas_contabeis')
    op.drop_table('gov_escrituracoes_sped')
    op.drop_table('gov_creditos_dctfweb')
    op.drop_table('gov_debitos_dctfweb')
    op.drop_table('gov_declaracoes_dctfweb')
    op.drop_table('gov_retencoes_reinf')
    op.drop_table('gov_totalizadores_reinf')
    op.drop_table('gov_eventos_reinf')
    op.drop_table('gov_movimentacoes_fgts')
    op.drop_table('gov_debitos_fgts')
    op.drop_table('gov_extratos_fgts')

    # Remover colunas adicionadas
    try:
        op.drop_column('gov_documentos_fiscais', 'dados_adicionais')
        op.drop_column('gov_documentos_fiscais', 'tipo_documento')
        op.drop_column('gov_documentos_fiscais', 'nome_emitente')
        op.drop_column('gov_documentos_fiscais', 'nome_destinatario')
        op.drop_column('gov_documentos_fiscais', 'direcao')
        op.drop_column('gov_documentos_fiscais', 'codigo_servico')
        op.drop_column('gov_documentos_fiscais', 'xml_documento')
    except Exception:
        pass

    try:
        op.drop_column('gov_eventos_documentos_fiscais', 'dados_adicionais')
    except Exception:
        pass

    try:
        op.drop_column('gov_guias_recolhimento', 'dados_adicionais')
    except Exception:
        pass
