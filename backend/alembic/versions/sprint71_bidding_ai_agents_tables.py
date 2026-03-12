"""Create AI agents tables for bidding module evolution.

New tables:
- bidding_opportunities (Scout agent)
- bidding_analyses (Analyst agent)
- bidding_assessments (Assessor agent)
- bidding_pricing (Pricer agent)
- bidding_disputes (Warrior agent)
- bidding_price_history (PNCP cache)
- bidding_sync_jobs (sync tracking)

Revision ID: sprint71_bidding_ai_agents
Revises: sprint70_cost_by_type_tables
Create Date: 2026-03-12

"""

from alembic import op

revision = "sprint71_bidding_ai_agents"
down_revision = "sprint70_cost_by_type_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ===================================================================
    # TABLE: bidding_opportunities (Scout Agent)
    # ===================================================================
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS bidding_opportunities (
            id                  UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
            portal              VARCHAR(50) NOT NULL,
            portal_id           VARCHAR(100),
            objeto              TEXT NOT NULL,
            valor_estimado      DECIMAL(15,2),
            modalidade          VARCHAR(50),
            orgao_nome          VARCHAR(255),
            orgao_cnpj          VARCHAR(14),
            uf                  VARCHAR(2),
            municipio           VARCHAR(100),
            data_publicacao     TIMESTAMP,
            data_abertura       TIMESTAMP,
            data_encerramento   TIMESTAMP,
            url_edital          TEXT,
            url_portal          TEXT,
            status              VARCHAR(30) DEFAULT 'nova',
            relevancia_score    DOUBLE PRECISION DEFAULT 0.0,
            keywords_matched    JSONB DEFAULT '[]'::jsonb,
            raw_data            JSONB,
            created_at          TIMESTAMP DEFAULT NOW(),
            updated_at          TIMESTAMP,
            UNIQUE(portal, portal_id)
        );
        CREATE INDEX IF NOT EXISTS idx_opp_portal ON bidding_opportunities(portal);
        CREATE INDEX IF NOT EXISTS idx_opp_status ON bidding_opportunities(status);
        CREATE INDEX IF NOT EXISTS idx_opp_uf ON bidding_opportunities(uf);
        CREATE INDEX IF NOT EXISTS idx_opp_abertura ON bidding_opportunities(data_abertura);
        CREATE INDEX IF NOT EXISTS idx_opp_relevancia ON bidding_opportunities(relevancia_score DESC);
        CREATE INDEX IF NOT EXISTS idx_opp_objeto_gin ON bidding_opportunities
            USING GIN (to_tsvector('portuguese', objeto));
        """
    )

    # ===================================================================
    # TABLE: bidding_analyses (Analyst Agent)
    # ===================================================================
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS bidding_analyses (
            id                          UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
            tender_id                   UUID REFERENCES bidding_tenders(id) ON DELETE CASCADE,
            objeto_resumido             TEXT,
            modalidade_identificada     VARCHAR(50),
            criterio_julgamento         VARCHAR(50),
            valor_estimado              VARCHAR(50),
            requisitos_habilitacao      JSONB DEFAULT '{}'::jsonb,
            prazos                      JSONB DEFAULT '{}'::jsonb,
            red_flags                   JSONB DEFAULT '[]'::jsonb,
            documentos_necessarios      JSONB DEFAULT '[]'::jsonb,
            itens_extraidos             JSONB DEFAULT '[]'::jsonb,
            informacoes_adicionais      JSONB DEFAULT '{}'::jsonb,
            estimativa_esforco_horas    INTEGER,
            recomendacao_participacao   VARCHAR(20),
            justificativa_recomendacao  TEXT,
            raw_analysis                JSONB,
            modelo_ia                   VARCHAR(50) DEFAULT 'claude-sonnet-4-20250514',
            created_at                  TIMESTAMP DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_analysis_tender ON bidding_analyses(tender_id);
        """
    )

    # ===================================================================
    # TABLE: bidding_assessments (Assessor Agent)
    # ===================================================================
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS bidding_assessments (
            id                          UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
            tender_id                   UUID REFERENCES bidding_tenders(id) ON DELETE CASCADE,
            analysis_id                 UUID REFERENCES bidding_analyses(id) ON DELETE SET NULL,
            score                       DOUBLE PRECISION,
            scores_detalhados           JSONB DEFAULT '{}'::jsonb,
            recomendacao                VARCHAR(20),
            justificativa               TEXT,
            requisitos_nao_atendidos    JSONB DEFAULT '[]'::jsonb,
            acoes_necessarias           JSONB DEFAULT '[]'::jsonb,
            created_at                  TIMESTAMP DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_assessment_tender ON bidding_assessments(tender_id);
        """
    )

    # ===================================================================
    # TABLE: bidding_pricing (Pricer Agent)
    # ===================================================================
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS bidding_pricing (
            id                  UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
            tender_id           UUID REFERENCES bidding_tenders(id) ON DELETE CASCADE,
            proposal_id         UUID REFERENCES bidding_proposals(id) ON DELETE SET NULL,
            itens               JSONB DEFAULT '[]'::jsonb,
            custos_diretos      DECIMAL(15,2),
            custos_indiretos    DECIMAL(15,2),
            impostos            DECIMAL(15,2),
            margem_lucro        DOUBLE PRECISION,
            valor_total         DECIMAL(15,2),
            cenario             VARCHAR(20),
            cenarios_completos  JSONB DEFAULT '{}'::jsonb,
            comparativo_mercado JSONB DEFAULT '{}'::jsonb,
            regime_tributario   VARCHAR(30),
            bdi_percentual      DOUBLE PRECISION,
            created_at          TIMESTAMP DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_pricing_tender ON bidding_pricing(tender_id);
        """
    )

    # ===================================================================
    # TABLE: bidding_disputes (Warrior Agent)
    # ===================================================================
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS bidding_disputes (
            id              UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
            tender_id       UUID REFERENCES bidding_tenders(id) ON DELETE CASCADE,
            portal          VARCHAR(50) NOT NULL,
            sessao_id       VARCHAR(100),
            status          VARCHAR(30) DEFAULT 'configurado',
            estrategia      JSONB DEFAULT '{}'::jsonb,
            lances          JSONB DEFAULT '[]'::jsonb,
            posicao_final   INTEGER,
            resultado       VARCHAR(30),
            valor_final     VARCHAR(50),
            started_at      TIMESTAMP,
            finished_at     TIMESTAMP,
            created_at      TIMESTAMP DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_dispute_tender ON bidding_disputes(tender_id);
        """
    )

    # ===================================================================
    # TABLE: bidding_price_history (PNCP cache)
    # ===================================================================
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS bidding_price_history (
            id                  UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
            item_descricao      TEXT NOT NULL,
            item_catmat         VARCHAR(20),
            preco               DECIMAL(15,2),
            unidade             VARCHAR(30),
            quantidade          DECIMAL(15,4),
            orgao_nome          VARCHAR(255),
            orgao_cnpj          VARCHAR(14),
            orgao_uf            VARCHAR(2),
            data_homologacao    DATE,
            fonte               VARCHAR(50),
            fonte_id            VARCHAR(100),
            created_at          TIMESTAMP DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_ph_catmat ON bidding_price_history(item_catmat);
        CREATE INDEX IF NOT EXISTS idx_ph_data ON bidding_price_history(data_homologacao);
        CREATE INDEX IF NOT EXISTS idx_ph_descricao_gin ON bidding_price_history
            USING GIN (to_tsvector('portuguese', item_descricao));
        """
    )

    # ===================================================================
    # TABLE: bidding_sync_jobs
    # ===================================================================
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS bidding_sync_jobs (
            id                      UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
            portal                  VARCHAR(50) NOT NULL,
            tipo                    VARCHAR(30),
            status                  VARCHAR(20) DEFAULT 'pendente',
            registros_processados   INTEGER DEFAULT 0,
            registros_novos         INTEGER DEFAULT 0,
            registros_atualizados   INTEGER DEFAULT 0,
            erros                   JSONB DEFAULT '[]'::jsonb,
            filtros_utilizados      JSONB DEFAULT '{}'::jsonb,
            started_at              TIMESTAMP,
            finished_at             TIMESTAMP,
            created_at              TIMESTAMP DEFAULT NOW()
        );
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS bidding_sync_jobs CASCADE;")
    op.execute("DROP TABLE IF EXISTS bidding_price_history CASCADE;")
    op.execute("DROP TABLE IF EXISTS bidding_disputes CASCADE;")
    op.execute("DROP TABLE IF EXISTS bidding_pricing CASCADE;")
    op.execute("DROP TABLE IF EXISTS bidding_assessments CASCADE;")
    op.execute("DROP TABLE IF EXISTS bidding_analyses CASCADE;")
    op.execute("DROP TABLE IF EXISTS bidding_opportunities CASCADE;")
