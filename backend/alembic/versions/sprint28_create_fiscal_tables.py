"""Sprint 28 - Create fiscal tables (NF-e, NFS-e, SPED, CFOP, NCM, Retencoes)

Revision ID: sprint28_fiscal
Revises: sprint27_accounting
Create Date: 2024-12-31

Tabelas criadas:
- cfops: Codigo Fiscal de Operacoes e Prestacoes
- ncms: Nomenclatura Comum do Mercosul
- retencoes_federais: Configuracao de retencoes federais (INSS, IR, PCC)
- tax_configurations: Configuracoes tributarias
- tax_tables: Tabelas de impostos progressivos
- simples_nacional_configs: Configuracao do Simples Nacional
- nfes: Notas Fiscais Eletronicas
- nfe_itens: Itens das NF-e
- nfses: Notas Fiscais de Servico Eletronicas
- nfse_lotes: Lotes de NFS-e
- codigos_servico: Codigos de servico LC 116/2003
- sped_files: Arquivos SPED
- sped_registros: Registros SPED
- fiscal_obligations: Obrigacoes fiscais
- simples_nacional_das: Guias DAS
- suframa_configs: Configuracao SUFRAMA
- suframa_operacoes: Operacoes com beneficio ZFM
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "sprint28_fiscal"
down_revision = "sprint27_accounting"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create fiscal tables."""

    # === CFOP ===
    op.create_table(
        "cfops",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("codigo", sa.String(4), nullable=False, unique=True, index=True),
        sa.Column("descricao", sa.Text, nullable=False),
        sa.Column("descricao_resumida", sa.String(100), nullable=True),
        sa.Column("tipo", sa.String(10), nullable=False),  # entrada, saida
        sa.Column("grupo", sa.String(1), nullable=False),  # 1,2,3,5,6,7
        sa.Column("natureza", sa.String(30), nullable=True),
        # Tributacao
        sa.Column("gera_credito_icms", sa.Boolean, default=False),
        sa.Column("gera_debito_icms", sa.Boolean, default=False),
        sa.Column("gera_credito_ipi", sa.Boolean, default=False),
        sa.Column("gera_debito_ipi", sa.Boolean, default=False),
        sa.Column("gera_pis_cofins", sa.Boolean, default=True),
        # Movimentacao
        sa.Column("movimenta_estoque", sa.Boolean, default=True),
        sa.Column("movimenta_financeiro", sa.Boolean, default=True),
        sa.Column("movimenta_contabilidade", sa.Boolean, default=True),
        # Zona Franca
        sa.Column("zfm_aplicavel", sa.Boolean, default=False),
        sa.Column("zfm_isenta_icms", sa.Boolean, default=False),
        sa.Column("zfm_isenta_ipi", sa.Boolean, default=False),
        sa.Column("zfm_suspende_pis_cofins", sa.Boolean, default=False),
        # CFOP correspondente
        sa.Column("cfop_correspondente", sa.String(4), nullable=True),
        # Contas contabeis
        sa.Column("conta_contabil_debito", sa.String(20), nullable=True),
        sa.Column("conta_contabil_credito", sa.String(20), nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("active", sa.Boolean, default=True, nullable=False),
    )

    # === NCM ===
    op.create_table(
        "ncms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("codigo", sa.String(8), nullable=False, unique=True, index=True),
        sa.Column("descricao", sa.Text, nullable=False),
        sa.Column("descricao_resumida", sa.String(200), nullable=True),
        # Classificacao
        sa.Column("capitulo", sa.String(2), nullable=True),
        sa.Column("posicao", sa.String(4), nullable=True),
        sa.Column("subposicao", sa.String(6), nullable=True),
        # IPI
        sa.Column("ipi_aliquota", sa.Numeric(8, 4), nullable=True),
        sa.Column("ipi_codigo_enquadramento", sa.String(5), nullable=True),
        sa.Column("ipi_unidade_tributavel", sa.String(6), nullable=True),
        # PIS/COFINS
        sa.Column("pis_aliquota", sa.Numeric(8, 4), nullable=True),
        sa.Column("cofins_aliquota", sa.Numeric(8, 4), nullable=True),
        sa.Column("pis_cofins_cst_entrada", sa.String(2), nullable=True),
        sa.Column("pis_cofins_cst_saida", sa.String(2), nullable=True),
        # ICMS
        sa.Column("icms_cest", sa.String(7), nullable=True),
        sa.Column("icms_st_mva", sa.Numeric(8, 4), nullable=True),
        # II
        sa.Column("ii_aliquota", sa.Numeric(8, 4), nullable=True),
        # Tributacao Monofasica
        sa.Column("tributacao_monofasica", sa.Boolean, default=False),
        sa.Column("aliquota_monofasica", sa.Numeric(8, 4), nullable=True),
        # Zona Franca
        sa.Column("zfm_isento_ipi", sa.Boolean, default=False),
        sa.Column("zfm_reduz_ii", sa.Boolean, default=False),
        sa.Column("zfm_percentual_reducao_ii", sa.Numeric(8, 4), nullable=True),
        # TIPI
        sa.Column("tipi_unidade", sa.String(10), nullable=True),
        sa.Column("tipi_nota", sa.String(500), nullable=True),
        # Vigencia
        sa.Column("valid_from", sa.Date, nullable=True),
        sa.Column("valid_until", sa.Date, nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("active", sa.Boolean, default=True, nullable=False),
    )

    # === Retencoes Federais ===
    op.create_table(
        "retencoes_federais",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        # Identificacao
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("codigo_servico", sa.String(20), nullable=True),
        sa.Column("descricao", sa.Text, nullable=True),
        # Tipo de servico
        sa.Column("servico_vigilancia", sa.Boolean, default=False),
        sa.Column("servico_limpeza", sa.Boolean, default=False),
        sa.Column("servico_locacao_mao_obra", sa.Boolean, default=False),
        sa.Column("servico_construcao_civil", sa.Boolean, default=False),
        # INSS (11%)
        sa.Column("inss_retido", sa.Boolean, default=True),
        sa.Column("inss_aliquota", sa.Numeric(8, 4), nullable=False),
        sa.Column("inss_base_minima", sa.Numeric(15, 2), nullable=True),
        # Liminar INSS
        sa.Column("inss_liminar_ativa", sa.Boolean, default=False),
        sa.Column("inss_liminar_numero", sa.String(50), nullable=True),
        sa.Column("inss_liminar_vara", sa.String(100), nullable=True),
        sa.Column("inss_liminar_data", sa.Date, nullable=True),
        sa.Column("inss_liminar_validade", sa.Date, nullable=True),
        sa.Column("inss_liminar_texto", sa.Text, nullable=True),
        # IR (1.5%)
        sa.Column("ir_retido", sa.Boolean, default=True),
        sa.Column("ir_aliquota", sa.Numeric(8, 4), nullable=False),
        sa.Column("ir_base_minima", sa.Numeric(15, 2), nullable=True),
        # CSLL (1%)
        sa.Column("csll_retido", sa.Boolean, default=True),
        sa.Column("csll_aliquota", sa.Numeric(8, 4), nullable=False),
        # PIS (0.65%)
        sa.Column("pis_retido", sa.Boolean, default=True),
        sa.Column("pis_aliquota", sa.Numeric(8, 4), nullable=False),
        # COFINS (3%)
        sa.Column("cofins_retido", sa.Boolean, default=True),
        sa.Column("cofins_aliquota", sa.Numeric(8, 4), nullable=False),
        # PCC base minima
        sa.Column("pcc_base_minima", sa.Numeric(15, 2), nullable=True),
        # ISS
        sa.Column("iss_retido", sa.Boolean, default=False),
        sa.Column("iss_aliquota", sa.Numeric(8, 4), nullable=True),
        # Cliente especifico
        sa.Column("cliente_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("cliente_aceita_liminar", sa.Boolean, nullable=True),
        # Vigencia
        sa.Column("valid_from", sa.Date, nullable=False),
        sa.Column("valid_until", sa.Date, nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("active", sa.Boolean, default=True, nullable=False),
    )

    # === NF-e ===
    op.create_table(
        "nfes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("tipo", sa.String(10), nullable=False),  # entrada, saida
        sa.Column("finalidade", sa.String(1), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, default="rascunho"),
        # Identificacao
        sa.Column("serie", sa.Integer, nullable=False),
        sa.Column("numero", sa.Integer, nullable=True),
        sa.Column("chave_acesso", sa.String(44), nullable=True, unique=True),
        sa.Column("natureza_operacao", sa.String(60), nullable=False),
        sa.Column("data_emissao", sa.DateTime, nullable=False),
        sa.Column("data_saida_entrada", sa.DateTime, nullable=True),
        # Emitente
        sa.Column("emitente_cnpj", sa.String(14), nullable=False),
        sa.Column("emitente_razao_social", sa.String(60), nullable=False),
        sa.Column("emitente_ie", sa.String(14), nullable=True),
        sa.Column("emitente_uf", sa.String(2), nullable=False),
        sa.Column("emitente_crt", sa.String(1), nullable=False),
        # Destinatario
        sa.Column("destinatario_cpf_cnpj", sa.String(14), nullable=False),
        sa.Column("destinatario_razao_social", sa.String(60), nullable=False),
        sa.Column("destinatario_ie", sa.String(14), nullable=True),
        sa.Column("destinatario_email", sa.String(60), nullable=True),
        sa.Column("destinatario_uf", sa.String(2), nullable=False),
        sa.Column("destinatario_logradouro", sa.String(60), nullable=False),
        sa.Column("destinatario_numero", sa.String(60), nullable=False),
        sa.Column("destinatario_bairro", sa.String(60), nullable=False),
        sa.Column("destinatario_municipio", sa.String(60), nullable=False),
        sa.Column("destinatario_cep", sa.String(8), nullable=False),
        sa.Column("destinatario_telefone", sa.String(14), nullable=True),
        # Frete
        sa.Column("modalidade_frete", sa.String(1), nullable=False),
        sa.Column("transportadora_cnpj", sa.String(14), nullable=True),
        sa.Column("transportadora_razao_social", sa.String(60), nullable=True),
        # Pagamento
        sa.Column("forma_pagamento", sa.String(2), nullable=False),
        sa.Column("meio_pagamento", sa.String(2), nullable=False),
        sa.Column("valor_pagamento", sa.Numeric(15, 2), nullable=True),
        # Totais
        sa.Column("valor_total_produtos", sa.Numeric(15, 2), nullable=True),
        sa.Column("valor_total_icms", sa.Numeric(15, 2), nullable=True),
        sa.Column("valor_total_ipi", sa.Numeric(15, 2), nullable=True),
        sa.Column("valor_total_pis", sa.Numeric(15, 2), nullable=True),
        sa.Column("valor_total_cofins", sa.Numeric(15, 2), nullable=True),
        sa.Column("valor_total_frete", sa.Numeric(15, 2), nullable=True),
        sa.Column("valor_total_seguro", sa.Numeric(15, 2), nullable=True),
        sa.Column("valor_total_desconto", sa.Numeric(15, 2), nullable=True),
        sa.Column("valor_total_outros", sa.Numeric(15, 2), nullable=True),
        sa.Column("valor_total_nota", sa.Numeric(15, 2), nullable=True),
        # Informacoes adicionais
        sa.Column("informacoes_complementares", sa.Text, nullable=True),
        sa.Column("informacoes_fisco", sa.Text, nullable=True),
        # Zona Franca
        sa.Column("is_zfm", sa.Boolean, default=False),
        sa.Column("suframa_destinatario", sa.String(9), nullable=True),
        # Autorizacao
        sa.Column("protocolo_autorizacao", sa.String(15), nullable=True),
        sa.Column("data_autorizacao", sa.DateTime, nullable=True),
        sa.Column("motivo_rejeicao", sa.Text, nullable=True),
        # XML
        sa.Column("xml_enviado", sa.Text, nullable=True),
        sa.Column("xml_autorizado", sa.Text, nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("active", sa.Boolean, default=True, nullable=False),
    )

    op.create_index("ix_nfes_numero_serie", "nfes", ["numero", "serie", "condominio_id"])

    # === NF-e Itens ===
    op.create_table(
        "nfe_itens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nfe_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("nfes.id"), nullable=False),
        sa.Column("numero_item", sa.Integer, nullable=False),
        sa.Column("produto_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("codigo_produto", sa.String(60), nullable=False),
        sa.Column("descricao", sa.String(120), nullable=False),
        sa.Column("ncm", sa.String(8), nullable=False),
        sa.Column("cfop", sa.String(4), nullable=False),
        sa.Column("unidade", sa.String(6), nullable=False),
        sa.Column("quantidade", sa.Numeric(15, 4), nullable=False),
        sa.Column("valor_unitario", sa.Numeric(15, 10), nullable=False),
        sa.Column("valor_total", sa.Numeric(15, 2), nullable=False),
        # Descontos
        sa.Column("valor_desconto", sa.Numeric(15, 2), default=0),
        sa.Column("valor_frete", sa.Numeric(15, 2), default=0),
        sa.Column("valor_seguro", sa.Numeric(15, 2), default=0),
        sa.Column("valor_outros", sa.Numeric(15, 2), default=0),
        # ICMS
        sa.Column("icms_origem", sa.String(1), nullable=True),
        sa.Column("icms_cst", sa.String(3), nullable=True),
        sa.Column("icms_csosn", sa.String(3), nullable=True),
        sa.Column("icms_base_calculo", sa.Numeric(15, 2), default=0),
        sa.Column("icms_aliquota", sa.Numeric(8, 4), default=0),
        sa.Column("icms_valor", sa.Numeric(15, 2), default=0),
        # IPI
        sa.Column("ipi_cst", sa.String(2), nullable=True),
        sa.Column("ipi_base_calculo", sa.Numeric(15, 2), default=0),
        sa.Column("ipi_aliquota", sa.Numeric(8, 4), default=0),
        sa.Column("ipi_valor", sa.Numeric(15, 2), default=0),
        # PIS
        sa.Column("pis_cst", sa.String(2), nullable=True),
        sa.Column("pis_base_calculo", sa.Numeric(15, 2), default=0),
        sa.Column("pis_aliquota", sa.Numeric(8, 4), default=0),
        sa.Column("pis_valor", sa.Numeric(15, 2), default=0),
        # COFINS
        sa.Column("cofins_cst", sa.String(2), nullable=True),
        sa.Column("cofins_base_calculo", sa.Numeric(15, 2), default=0),
        sa.Column("cofins_aliquota", sa.Numeric(8, 4), default=0),
        sa.Column("cofins_valor", sa.Numeric(15, 2), default=0),
        # Auditoria
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # === NFS-e ===
    op.create_table(
        "nfses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("status", sa.String(20), nullable=False, default="rascunho"),
        # RPS
        sa.Column("numero_rps", sa.Integer, nullable=True),
        sa.Column("serie_rps", sa.String(5), nullable=False),
        sa.Column("tipo_rps", sa.String(1), nullable=False),
        # Dados NFS-e
        sa.Column("numero_nfse", sa.String(20), nullable=True),
        sa.Column("codigo_verificacao", sa.String(20), nullable=True),
        sa.Column("link_nfse", sa.String(500), nullable=True),
        # Datas
        sa.Column("data_emissao", sa.DateTime, nullable=False),
        sa.Column("data_competencia", sa.Date, nullable=False),
        sa.Column("data_processamento", sa.DateTime, nullable=True),
        # Natureza
        sa.Column("natureza_operacao", sa.String(1), nullable=False),
        sa.Column("regime_especial", sa.String(1), nullable=True),
        # Prestador
        sa.Column("prestador_cnpj", sa.String(14), nullable=False),
        sa.Column("prestador_inscricao_municipal", sa.String(15), nullable=True),
        sa.Column("prestador_razao_social", sa.String(150), nullable=False),
        # Tomador
        sa.Column("tomador_cpf_cnpj", sa.String(14), nullable=False),
        sa.Column("tomador_razao_social", sa.String(150), nullable=False),
        sa.Column("tomador_email", sa.String(80), nullable=True),
        sa.Column("tomador_inscricao_municipal", sa.String(15), nullable=True),
        sa.Column("tomador_logradouro", sa.String(125), nullable=False),
        sa.Column("tomador_numero", sa.String(10), nullable=False),
        sa.Column("tomador_complemento", sa.String(60), nullable=True),
        sa.Column("tomador_bairro", sa.String(60), nullable=False),
        sa.Column("tomador_municipio", sa.String(60), nullable=False),
        sa.Column("tomador_uf", sa.String(2), nullable=False),
        sa.Column("tomador_cep", sa.String(8), nullable=False),
        sa.Column("tomador_telefone", sa.String(20), nullable=True),
        # Servico
        sa.Column("codigo_servico", sa.String(20), nullable=False),
        sa.Column("descricao_servico", sa.Text, nullable=False),
        sa.Column("codigo_cnae", sa.String(7), nullable=True),
        sa.Column("codigo_tributacao_municipio", sa.String(20), nullable=True),
        # Valores
        sa.Column("valor_servicos", sa.Numeric(15, 2), nullable=False),
        sa.Column("valor_deducoes", sa.Numeric(15, 2), default=0),
        sa.Column("valor_desconto_condicionado", sa.Numeric(15, 2), default=0),
        sa.Column("valor_desconto_incondicionado", sa.Numeric(15, 2), default=0),
        # ISS
        sa.Column("iss_aliquota", sa.Numeric(8, 4), nullable=False),
        sa.Column("iss_valor", sa.Numeric(15, 2), nullable=True),
        sa.Column("iss_retido", sa.Boolean, default=False),
        # Retencoes federais
        sa.Column("pis_valor", sa.Numeric(15, 2), default=0),
        sa.Column("cofins_valor", sa.Numeric(15, 2), default=0),
        sa.Column("inss_valor", sa.Numeric(15, 2), default=0),
        sa.Column("ir_valor", sa.Numeric(15, 2), default=0),
        sa.Column("csll_valor", sa.Numeric(15, 2), default=0),
        sa.Column("outras_retencoes", sa.Numeric(15, 2), default=0),
        # Liminar INSS
        sa.Column("inss_liminar_aplicada", sa.Boolean, default=False),
        sa.Column("inss_liminar_numero", sa.String(50), nullable=True),
        sa.Column("inss_liminar_texto", sa.String(500), nullable=True),
        # Informacoes adicionais
        sa.Column("discriminacao", sa.Text, nullable=True),
        sa.Column("observacao", sa.String(1000), nullable=True),
        # Processamento
        sa.Column("protocolo", sa.String(50), nullable=True),
        sa.Column("mensagem_retorno", sa.Text, nullable=True),
        # XML
        sa.Column("xml_enviado", sa.Text, nullable=True),
        sa.Column("xml_retorno", sa.Text, nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("active", sa.Boolean, default=True, nullable=False),
    )

    op.create_index("ix_nfses_competencia", "nfses", ["data_competencia", "condominio_id"])

    # === Codigos de Servico ===
    op.create_table(
        "codigos_servico",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("codigo", sa.String(20), nullable=False, unique=True, index=True),
        sa.Column("descricao", sa.Text, nullable=False),
        sa.Column("iss_aliquota_padrao", sa.Numeric(8, 4), nullable=True),
        sa.Column("cnae_principal", sa.String(7), nullable=True),
        sa.Column("active", sa.Boolean, default=True, nullable=False),
    )

    # === SPED Files ===
    op.create_table(
        "sped_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("tipo", sa.String(30), nullable=False),  # efd_icms_ipi, efd_contribuicoes, etc
        sa.Column("status", sa.String(20), nullable=False, default="gerando"),
        sa.Column("ano", sa.Integer, nullable=False),
        sa.Column("mes", sa.Integer, nullable=True),
        sa.Column("finalidade", sa.String(1), nullable=False),  # 0-Original, 1-Retificadora
        sa.Column("perfil", sa.String(1), nullable=True),  # A, B, C
        # Arquivo
        sa.Column("nome_arquivo", sa.String(255), nullable=True),
        sa.Column("hash_arquivo", sa.String(64), nullable=True),
        sa.Column("tamanho_bytes", sa.BigInteger, nullable=True),
        sa.Column("conteudo", sa.Text, nullable=True),
        # Transmissao
        sa.Column("recibo_transmissao", sa.String(50), nullable=True),
        sa.Column("data_transmissao", sa.DateTime, nullable=True),
        sa.Column("protocolo_entrega", sa.String(50), nullable=True),
        sa.Column("data_processamento", sa.DateTime, nullable=True),
        # Erros
        sa.Column("total_erros", sa.Integer, default=0),
        sa.Column("total_avisos", sa.Integer, default=0),
        sa.Column("erros", postgresql.JSONB, nullable=True),
        sa.Column("avisos", postgresql.JSONB, nullable=True),
        # Resumo
        sa.Column("resumo", postgresql.JSONB, nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("active", sa.Boolean, default=True, nullable=False),
    )

    # === Fiscal Obligations ===
    op.create_table(
        "fiscal_obligations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("tipo", sa.String(30), nullable=False),  # DAS, DCTF, DIRF, etc
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("descricao", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, default="pendente"),
        sa.Column("competencia_mes", sa.Integer, nullable=True),
        sa.Column("competencia_ano", sa.Integer, nullable=False),
        sa.Column("data_vencimento", sa.Date, nullable=False),
        sa.Column("valor_devido", sa.Numeric(15, 2), nullable=True),
        sa.Column("valor_pago", sa.Numeric(15, 2), nullable=True),
        sa.Column("data_pagamento", sa.Date, nullable=True),
        sa.Column("numero_recibo", sa.String(50), nullable=True),
        sa.Column("observacoes", sa.Text, nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("active", sa.Boolean, default=True, nullable=False),
    )

    op.create_index("ix_fiscal_obligations_vencimento", "fiscal_obligations", ["data_vencimento"])

    # === Simples Nacional DAS ===
    op.create_table(
        "simples_nacional_das",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("status", sa.String(20), nullable=False, default="pendente"),
        sa.Column("competencia_mes", sa.Integer, nullable=False),
        sa.Column("competencia_ano", sa.Integer, nullable=False),
        sa.Column("data_vencimento", sa.Date, nullable=False),
        # Receita
        sa.Column("receita_bruta_mes", sa.Numeric(15, 2), nullable=False),
        sa.Column("receita_bruta_12_meses", sa.Numeric(15, 2), nullable=False),
        # Faixa e aliquota
        sa.Column("anexo", sa.String(5), nullable=False),
        sa.Column("faixa", sa.Integer, nullable=False),
        sa.Column("aliquota_nominal", sa.Numeric(8, 4), nullable=False),
        sa.Column("aliquota_efetiva", sa.Numeric(8, 4), nullable=False),
        sa.Column("parcela_deduzir", sa.Numeric(15, 2), nullable=False),
        # Valor
        sa.Column("valor_devido", sa.Numeric(15, 2), nullable=False),
        sa.Column("valor_pago", sa.Numeric(15, 2), nullable=True),
        sa.Column("data_pagamento", sa.Date, nullable=True),
        # Documento
        sa.Column("numero_documento", sa.String(50), nullable=True),
        sa.Column("codigo_barras", sa.String(50), nullable=True),
        sa.Column("numero_recibo", sa.String(50), nullable=True),
        # Reparticao tributos
        sa.Column("reparticao_irpj", sa.Numeric(8, 4), nullable=True),
        sa.Column("reparticao_csll", sa.Numeric(8, 4), nullable=True),
        sa.Column("reparticao_cofins", sa.Numeric(8, 4), nullable=True),
        sa.Column("reparticao_pis", sa.Numeric(8, 4), nullable=True),
        sa.Column("reparticao_cpp", sa.Numeric(8, 4), nullable=True),
        sa.Column("reparticao_iss", sa.Numeric(8, 4), nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("active", sa.Boolean, default=True, nullable=False),
    )

    op.create_index(
        "ix_das_competencia",
        "simples_nacional_das",
        ["competencia_ano", "competencia_mes", "condominio_id"],
        unique=True,
    )

    # === SUFRAMA Config ===
    op.create_table(
        "suframa_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("inscricao_suframa", sa.String(9), nullable=False),
        sa.Column("data_validade", sa.Date, nullable=False),
        sa.Column("tipo_incentivo", sa.String(20), nullable=False),
        # Beneficios
        sa.Column("isento_ipi", sa.Boolean, default=True),
        sa.Column("reducao_icms", sa.Boolean, default=True),
        sa.Column("percentual_reducao_icms", sa.Numeric(8, 4), nullable=True),
        sa.Column("suspensao_pis_cofins", sa.Boolean, default=True),
        # Produtos incentivados
        sa.Column("ncms_incentivados", postgresql.JSONB, nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("active", sa.Boolean, default=True, nullable=False),
    )

    # === SUFRAMA Operacoes ===
    op.create_table(
        "suframa_operacoes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("nfe_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("data_operacao", sa.Date, nullable=False),
        sa.Column("valor_operacao", sa.Numeric(15, 2), nullable=False),
        # Economia
        sa.Column("valor_ipi_desonerado", sa.Numeric(15, 2), default=0),
        sa.Column("valor_icms_desonerado", sa.Numeric(15, 2), default=0),
        sa.Column("valor_pis_suspenso", sa.Numeric(15, 2), default=0),
        sa.Column("valor_cofins_suspenso", sa.Numeric(15, 2), default=0),
        # PIN
        sa.Column("numero_pin", sa.String(20), nullable=True),
        sa.Column("data_pin", sa.Date, nullable=True),
        sa.Column("status_pin", sa.String(20), nullable=True),
        # Auditoria
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("active", sa.Boolean, default=True, nullable=False),
    )

    op.create_index("ix_suframa_operacoes_data", "suframa_operacoes", ["data_operacao"])


def downgrade() -> None:
    """Drop fiscal tables."""
    op.drop_table("suframa_operacoes")
    op.drop_table("suframa_configs")
    op.drop_table("simples_nacional_das")
    op.drop_table("fiscal_obligations")
    op.drop_table("sped_files")
    op.drop_table("codigos_servico")
    op.drop_table("nfses")
    op.drop_table("nfe_itens")
    op.drop_table("nfes")
    op.drop_table("retencoes_federais")
    op.drop_table("ncms")
    op.drop_table("cfops")
