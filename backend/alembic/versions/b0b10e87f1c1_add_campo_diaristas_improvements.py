"""add_campo_diaristas_improvements

Revision ID: b0b10e87f1c1
Revises: sprint32_diarists
Create Date: 2026-01-13 20:44:26.453871

Tabelas criadas:
- Campo: ordens_servico, visitas, checklist_templates, checklist_itens, checklist_preenchido, checklist_resposta
- Diaristas Fiscal: documentos_fiscais, retencoes_fiscais, eventos_esocial, tabela_inss, tabela_irrf
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b0b10e87f1c1"
down_revision: str | None = "sprint32_diarists"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Cria tabelas dos modulos Campo e Diaristas Fiscal."""

    # =========================================================================
    # CAMPO - ORDENS DE SERVICO
    # =========================================================================
    op.create_table(
        "ordens_servico",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("numero", sa.String(50), unique=True, nullable=False),
        sa.Column("tipo", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, default="aberta"),
        sa.Column("prioridade", sa.String(20), default="normal"),
        sa.Column("origem", sa.String(50)),
        # Cliente/Contrato
        sa.Column("cliente_id", postgresql.UUID(as_uuid=True)),
        sa.Column("contrato_id", postgresql.UUID(as_uuid=True)),
        sa.Column("cliente_nome", sa.String(255)),
        sa.Column("cliente_telefone", sa.String(20)),
        sa.Column("cliente_email", sa.String(255)),
        # Localizacao
        sa.Column("endereco_servico", sa.String(500)),
        sa.Column("complemento", sa.String(200)),
        sa.Column("bairro", sa.String(100)),
        sa.Column("cidade", sa.String(100)),
        sa.Column("estado", sa.String(2)),
        sa.Column("cep", sa.String(10)),
        sa.Column("latitude", sa.Numeric(10, 7)),
        sa.Column("longitude", sa.Numeric(10, 7)),
        # Agendamento
        sa.Column("data_agendada", sa.Date),
        sa.Column("horario_inicio_previsto", sa.Time),
        sa.Column("horario_fim_previsto", sa.Time),
        sa.Column("duracao_estimada_minutos", sa.Integer),
        sa.Column("janela_atendimento", sa.String(50)),
        # Execucao
        sa.Column("tecnico_id", postgresql.UUID(as_uuid=True)),
        sa.Column("tecnico_auxiliar_id", postgresql.UUID(as_uuid=True)),
        sa.Column("tecnico_nome", sa.String(255)),
        sa.Column("data_inicio", sa.DateTime),
        sa.Column("data_fim", sa.DateTime),
        sa.Column("checkin_at", sa.DateTime),
        sa.Column("checkout_at", sa.DateTime),
        sa.Column("checkin_latitude", sa.Numeric(10, 7)),
        sa.Column("checkin_longitude", sa.Numeric(10, 7)),
        sa.Column("checkout_latitude", sa.Numeric(10, 7)),
        sa.Column("checkout_longitude", sa.Numeric(10, 7)),
        sa.Column("duracao_real_minutos", sa.Integer),
        # Descricao
        sa.Column("titulo", sa.String(500)),
        sa.Column("descricao", sa.Text),
        sa.Column("observacoes_internas", sa.Text),
        sa.Column("instrucoes_cliente", sa.Text),
        sa.Column("solucao_aplicada", sa.Text),
        sa.Column("pendencias", sa.Text),
        # Materiais e Custos
        sa.Column("materiais_previstos", postgresql.JSONB),
        sa.Column("materiais_utilizados", postgresql.JSONB),
        sa.Column("valor_mao_obra", sa.Numeric(15, 2), default=0),
        sa.Column("valor_materiais", sa.Numeric(15, 2), default=0),
        sa.Column("valor_deslocamento", sa.Numeric(15, 2), default=0),
        sa.Column("valor_total", sa.Numeric(15, 2), default=0),
        sa.Column("cobranca_extra", sa.Boolean, default=False),
        sa.Column("motivo_cobranca_extra", sa.Text),
        # Avaliacao
        sa.Column("avaliacao_cliente", sa.Integer),
        sa.Column("comentario_cliente", sa.Text),
        sa.Column("assinatura_cliente_url", sa.String(500)),
        sa.Column("assinatura_cliente_nome", sa.String(255)),
        sa.Column("assinatura_cliente_at", sa.DateTime),
        # Fotos
        sa.Column("fotos_antes", postgresql.JSONB),
        sa.Column("fotos_durante", postgresql.JSONB),
        sa.Column("fotos_depois", postgresql.JSONB),
        # Relacionamentos
        sa.Column("checklist_template_id", postgresql.UUID(as_uuid=True)),
        sa.Column("os_origem_id", postgresql.UUID(as_uuid=True)),
        # Metadata
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("ativo", sa.Boolean, default=True),
    )

    op.create_index("ix_os_cliente_status", "ordens_servico", ["cliente_id", "status"])
    op.create_index("ix_os_tecnico_data", "ordens_servico", ["tecnico_id", "data_agendada"])
    op.create_index("ix_os_contrato", "ordens_servico", ["contrato_id"])
    op.create_index("ix_os_numero", "ordens_servico", ["numero"])

    # =========================================================================
    # CAMPO - VISITAS
    # =========================================================================
    op.create_table(
        "visitas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("numero", sa.String(50), unique=True, nullable=False),
        sa.Column("tipo", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, default="agendada"),
        sa.Column("origem", sa.String(50)),
        # Responsavel
        sa.Column("responsavel_id", postgresql.UUID(as_uuid=True)),
        sa.Column("responsavel_tipo", sa.String(20)),
        sa.Column("responsavel_nome", sa.String(255)),
        # Cliente/Prospect
        sa.Column("cliente_id", postgresql.UUID(as_uuid=True)),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True)),
        sa.Column("prospect_nome", sa.String(255)),
        sa.Column("prospect_telefone", sa.String(20)),
        sa.Column("prospect_email", sa.String(255)),
        sa.Column("contato_nome", sa.String(255)),
        sa.Column("contato_telefone", sa.String(20)),
        # Localizacao
        sa.Column("endereco", sa.String(500)),
        sa.Column("complemento", sa.String(200)),
        sa.Column("bairro", sa.String(100)),
        sa.Column("cidade", sa.String(100)),
        sa.Column("estado", sa.String(2)),
        sa.Column("cep", sa.String(10)),
        sa.Column("latitude", sa.Numeric(10, 7)),
        sa.Column("longitude", sa.Numeric(10, 7)),
        sa.Column("referencia", sa.Text),
        # Agendamento
        sa.Column("data_visita", sa.Date),
        sa.Column("horario_inicio", sa.Time),
        sa.Column("horario_fim", sa.Time),
        sa.Column("duracao_prevista_minutos", sa.Integer),
        # Execucao
        sa.Column("checkin_at", sa.DateTime),
        sa.Column("checkout_at", sa.DateTime),
        sa.Column("checkin_latitude", sa.Numeric(10, 7)),
        sa.Column("checkin_longitude", sa.Numeric(10, 7)),
        sa.Column("checkout_latitude", sa.Numeric(10, 7)),
        sa.Column("checkout_longitude", sa.Numeric(10, 7)),
        sa.Column("duracao_real_minutos", sa.Integer),
        # Resultado
        sa.Column("resultado", sa.String(50)),
        sa.Column("observacoes", sa.Text),
        sa.Column("proximos_passos", sa.Text),
        # Conversao Comercial
        sa.Column("proposta_gerada", sa.Boolean, default=False),
        sa.Column("proposta_id", postgresql.UUID(as_uuid=True)),
        sa.Column("valor_estimado", sa.Numeric(15, 2)),
        sa.Column("probabilidade_fechamento", sa.Integer),
        sa.Column("data_prevista_fechamento", sa.Date),
        # Documentos
        sa.Column("fotos", postgresql.JSONB),
        sa.Column("documentos", postgresql.JSONB),
        sa.Column("anotacoes", postgresql.JSONB),
        # Relacionamentos
        sa.Column("visita_origem_id", postgresql.UUID(as_uuid=True)),
        sa.Column("ordem_servico_id", postgresql.UUID(as_uuid=True)),
        # Metadata
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("ativo", sa.Boolean, default=True),
    )

    op.create_index("ix_visita_responsavel_data", "visitas", ["responsavel_id", "data_visita"])
    op.create_index("ix_visita_cliente_status", "visitas", ["cliente_id", "status"])
    op.create_index("ix_visita_data", "visitas", ["data_visita"])

    # =========================================================================
    # CAMPO - CHECKLIST TEMPLATES
    # =========================================================================
    op.create_table(
        "checklist_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("codigo", sa.String(50), unique=True, nullable=False),
        sa.Column("nome", sa.String(200), nullable=False),
        sa.Column("descricao", sa.Text),
        sa.Column("tipo_servico", sa.String(50)),
        sa.Column("versao", sa.String(20), default="1.0"),
        sa.Column("is_padrao", sa.Boolean, default=False),
        sa.Column("is_ativo", sa.Boolean, default=True),
        sa.Column("pontuacao_maxima", sa.Integer),
        sa.Column("tempo_estimado_minutos", sa.Integer),
        sa.Column("instrucoes_gerais", sa.Text),
        sa.Column("config", postgresql.JSONB),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
    )

    op.create_index("ix_checklist_template_tipo", "checklist_templates", ["tipo_servico"])

    # =========================================================================
    # CAMPO - CHECKLIST ITENS
    # =========================================================================
    op.create_table(
        "checklist_itens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "template_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("checklist_templates.id"), nullable=False
        ),
        sa.Column("codigo", sa.String(50)),
        sa.Column("secao", sa.String(100)),
        sa.Column("ordem_secao", sa.Integer, default=0),
        sa.Column("ordem", sa.Integer, nullable=False),
        sa.Column("pergunta", sa.String(500), nullable=False),
        sa.Column("descricao", sa.Text),
        sa.Column("tipo_resposta", sa.String(50), nullable=False),
        sa.Column("categoria", sa.String(50)),
        sa.Column("opcoes", postgresql.JSONB),
        sa.Column("valor_minimo", sa.Numeric(15, 4)),
        sa.Column("valor_maximo", sa.Numeric(15, 4)),
        sa.Column("unidade_medida", sa.String(20)),
        sa.Column("obrigatorio", sa.Boolean, default=True),
        sa.Column("peso", sa.Numeric(5, 2), default=1),
        sa.Column("condicional", sa.Boolean, default=False),
        sa.Column("condicional_item_id", postgresql.UUID(as_uuid=True)),
        sa.Column("condicional_valor", sa.String(100)),
        sa.Column("instrucoes", sa.Text),
        sa.Column("valor_padrao", sa.String(500)),
        sa.Column("is_ativo", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
    )

    op.create_index("ix_checklist_item_template", "checklist_itens", ["template_id"])

    # =========================================================================
    # CAMPO - CHECKLIST PREENCHIDO
    # =========================================================================
    op.create_table(
        "checklist_preenchido",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ordem_servico_id", postgresql.UUID(as_uuid=True), unique=True, nullable=False),
        sa.Column(
            "template_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("checklist_templates.id"), nullable=False
        ),
        sa.Column("status", sa.String(30), default="em_andamento"),
        sa.Column("iniciado_at", sa.DateTime),
        sa.Column("finalizado_at", sa.DateTime),
        sa.Column("total_itens", sa.Integer, default=0),
        sa.Column("itens_respondidos", sa.Integer, default=0),
        sa.Column("itens_conformes", sa.Integer, default=0),
        sa.Column("itens_nao_conformes", sa.Integer, default=0),
        sa.Column("pontuacao_obtida", sa.Numeric(10, 2)),
        sa.Column("pontuacao_maxima", sa.Numeric(10, 2)),
        sa.Column("percentual_conformidade", sa.Numeric(5, 2)),
        sa.Column("observacoes_gerais", sa.Text),
        sa.Column("assinatura_tecnico_url", sa.String(500)),
        sa.Column("assinatura_cliente_url", sa.String(500)),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
    )

    # =========================================================================
    # CAMPO - CHECKLIST RESPOSTAS
    # =========================================================================
    op.create_table(
        "checklist_respostas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "checklist_preenchido_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("checklist_preenchido.id"),
            nullable=False,
        ),
        sa.Column("item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("checklist_itens.id"), nullable=False),
        sa.Column("resposta_texto", sa.Text),
        sa.Column("resposta_numero", sa.Numeric(15, 4)),
        sa.Column("resposta_boolean", sa.Boolean),
        sa.Column("resposta_opcao", sa.String(200)),
        sa.Column("resposta_multipla", postgresql.JSONB),
        sa.Column("resposta_data", sa.Date),
        sa.Column("resposta_hora", sa.Time),
        sa.Column("resposta_datetime", sa.DateTime),
        sa.Column("resposta_latitude", sa.Numeric(10, 7)),
        sa.Column("resposta_longitude", sa.Numeric(10, 7)),
        sa.Column("foto_url", sa.String(500)),
        sa.Column("fotos_urls", postgresql.JSONB),
        sa.Column("assinatura_url", sa.String(500)),
        sa.Column("arquivo_url", sa.String(500)),
        sa.Column("arquivo_nome", sa.String(255)),
        sa.Column("arquivo_tipo", sa.String(50)),
        sa.Column("is_conforme", sa.Boolean),
        sa.Column("observacao", sa.Text),
        sa.Column("pontuacao", sa.Numeric(5, 2)),
        sa.Column("respondido_at", sa.DateTime, default=sa.func.now()),
        sa.Column("respondido_por", postgresql.UUID(as_uuid=True)),
    )

    op.create_index("ix_checklist_resposta_preenchido", "checklist_respostas", ["checklist_preenchido_id"])

    # =========================================================================
    # DIARISTAS - TABELA INSS
    # =========================================================================
    op.create_table(
        "tabela_inss",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("vigencia_inicio", sa.Date, nullable=False),
        sa.Column("vigencia_fim", sa.Date),
        sa.Column("faixas", postgresql.JSONB, nullable=False),
        sa.Column("teto_contribuicao", sa.Numeric(15, 2), nullable=False),
        sa.Column("aliquota_autonomo", sa.Numeric(5, 2), default=11.0),
        sa.Column("is_ativo", sa.Boolean, default=True),
        sa.Column("observacoes", sa.Text),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
    )

    # =========================================================================
    # DIARISTAS - TABELA IRRF
    # =========================================================================
    op.create_table(
        "tabela_irrf",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("vigencia_inicio", sa.Date, nullable=False),
        sa.Column("vigencia_fim", sa.Date),
        sa.Column("faixas", postgresql.JSONB, nullable=False),
        sa.Column("deducao_dependente", sa.Numeric(15, 2), nullable=False),
        sa.Column("is_ativo", sa.Boolean, default=True),
        sa.Column("observacoes", sa.Text),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
    )

    # =========================================================================
    # DIARISTAS - DOCUMENTOS FISCAIS
    # =========================================================================
    op.create_table(
        "documentos_fiscais",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("numero", sa.String(50), unique=True, nullable=False),
        sa.Column("tipo", sa.String(30), nullable=False),
        sa.Column("status", sa.String(30), default="rascunho"),
        sa.Column("diarista_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True)),
        sa.Column("competencia", sa.String(7), nullable=False),
        sa.Column("data_emissao", sa.Date),
        sa.Column("data_pagamento", sa.Date),
        sa.Column("valor_bruto", sa.Numeric(15, 2), nullable=False),
        sa.Column("valor_liquido", sa.Numeric(15, 2)),
        sa.Column("total_retencoes", sa.Numeric(15, 2), default=0),
        sa.Column("descricao_servico", sa.Text),
        sa.Column("codigo_servico", sa.String(20)),
        sa.Column("observacoes", sa.Text),
        sa.Column("pdf_url", sa.String(500)),
        sa.Column("xml_url", sa.String(500)),
        sa.Column("nfse_numero", sa.String(50)),
        sa.Column("nfse_codigo_verificacao", sa.String(50)),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
    )

    op.create_index("ix_doc_fiscal_diarista", "documentos_fiscais", ["diarista_id"])
    op.create_index("ix_doc_fiscal_competencia", "documentos_fiscais", ["competencia"])

    # =========================================================================
    # DIARISTAS - RETENCOES FISCAIS
    # =========================================================================
    op.create_table(
        "retencoes_fiscais",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "documento_fiscal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documentos_fiscais.id"), nullable=False
        ),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("base_calculo", sa.Numeric(15, 2), nullable=False),
        sa.Column("aliquota", sa.Numeric(5, 4), nullable=False),
        sa.Column("valor", sa.Numeric(15, 2), nullable=False),
        sa.Column("faixa_tabela", sa.String(100)),
        sa.Column("parcela_deduzir", sa.Numeric(15, 2), default=0),
        sa.Column("deducoes", sa.Numeric(15, 2), default=0),
        sa.Column("observacoes", sa.Text),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
    )

    # =========================================================================
    # DIARISTAS - EVENTOS ESOCIAL
    # =========================================================================
    op.create_table(
        "eventos_esocial",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tipo_evento", sa.String(10), nullable=False),
        sa.Column("status", sa.String(30), default="pendente"),
        sa.Column("diarista_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("condominio_id", postgresql.UUID(as_uuid=True)),
        sa.Column("documento_fiscal_id", postgresql.UUID(as_uuid=True)),
        sa.Column("competencia", sa.String(7)),
        sa.Column("data_geracao", sa.DateTime, default=sa.func.now()),
        sa.Column("data_envio", sa.DateTime),
        sa.Column("data_retorno", sa.DateTime),
        sa.Column("xml_envio", sa.Text),
        sa.Column("xml_retorno", sa.Text),
        sa.Column("protocolo", sa.String(100)),
        sa.Column("recibo", sa.String(100)),
        sa.Column("erro_codigo", sa.String(20)),
        sa.Column("erro_mensagem", sa.Text),
        sa.Column("tentativas", sa.Integer, default=0),
        sa.Column("observacoes", sa.Text),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, onupdate=sa.func.now()),
    )

    op.create_index("ix_esocial_diarista", "eventos_esocial", ["diarista_id"])
    op.create_index("ix_esocial_status", "eventos_esocial", ["status"])


def downgrade() -> None:
    """Remove tabelas dos modulos Campo e Diaristas Fiscal."""

    # Drop tables in reverse order
    op.drop_table("eventos_esocial")
    op.drop_table("retencoes_fiscais")
    op.drop_table("documentos_fiscais")
    op.drop_table("tabela_irrf")
    op.drop_table("tabela_inss")
    op.drop_table("checklist_respostas")
    op.drop_table("checklist_preenchido")
    op.drop_table("checklist_itens")
    op.drop_table("checklist_templates")
    op.drop_table("visitas")
    op.drop_table("ordens_servico")
