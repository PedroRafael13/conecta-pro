"""Create empresas and liminares tables for Multi-CNPJ module.

Revision ID: sprint67_create_empresas_module
Revises: sprint66_add_contract_costs
Create Date: 2026-03-09

"""

from alembic import op

revision = "sprint67_create_empresas_module"
down_revision = "sprint66_add_contract_costs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ===================================================================
    # TABLE: empresas
    # ===================================================================
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS empresas (
            id                              UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
            condominio_id                   UUID NOT NULL REFERENCES condominios(id),

            -- Identificação
            slug                            VARCHAR(50) NOT NULL,
            razao_social                    VARCHAR(200) NOT NULL,
            nome_fantasia                   VARCHAR(200),
            cnpj                            VARCHAR(18) UNIQUE,

            -- Inscrições
            inscricao_municipal             VARCHAR(30),
            inscricao_estadual              VARCHAR(30),
            inscricao_suframa               VARCHAR(20),
            codigo_municipio_ibge           VARCHAR(10) DEFAULT '1302603',

            -- Regime tributário (VARCHAR — sem enum nativo)
            regime_tributario               VARCHAR(30) NOT NULL,
            anexo_simples                   VARCHAR(5),
            data_opcao_simples              DATE,
            data_desenquadramento_simples   DATE,

            -- Regime futuro
            regime_futuro                   VARCHAR(30),
            data_prevista_mudanca_regime    DATE,

            -- Certificado digital
            certificado_a1_path             VARCHAR(500),
            certificado_a1_senha            VARCHAR(200),
            certificado_validade            DATE,

            -- Contador
            contador_software               VARCHAR(100),
            contador_email                  VARCHAR(200),
            contador_nome                   VARCHAR(200),

            -- Serviços e NFS-e
            tipos_servicos                  JSONB DEFAULT '[]'::jsonb,
            nfse_ambiente                   VARCHAR(20) DEFAULT 'homologacao',
            nfse_serie_rps                  VARCHAR(5) DEFAULT '1',
            nfse_numero_inicial             VARCHAR(10) DEFAULT '1',

            -- Status e flags
            status                          VARCHAR(20) DEFAULT 'ativa',
            is_principal                    BOOLEAN DEFAULT false,

            -- Metadados
            observacoes                     TEXT,
            created_at                      DATE DEFAULT CURRENT_DATE,
            updated_at                      DATE DEFAULT CURRENT_DATE
        )
        """
    )

    # Indexes — empresas
    op.execute("CREATE INDEX IF NOT EXISTS ix_empresas_condominio_id ON empresas (condominio_id)")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_empresas_cnpj ON empresas (cnpj) WHERE cnpj IS NOT NULL")
    op.execute("CREATE INDEX IF NOT EXISTS ix_empresas_slug_condominio ON empresas (slug, condominio_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_empresas_status ON empresas (status)")

    # ===================================================================
    # TABLE: liminares
    # ===================================================================
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS liminares (
            id                  UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
            empresa_id          UUID NOT NULL REFERENCES empresas(id) ON DELETE CASCADE,

            tipo                VARCHAR(30) NOT NULL,
            descricao           VARCHAR(500) NOT NULL,

            -- Processo judicial
            numero_processo     VARCHAR(100),
            vara                VARCHAR(200),
            tribunal            VARCHAR(100),
            advogado            VARCHAR(200),

            -- Datas
            data_solicitacao    DATE,
            data_concessao      DATE,
            data_validade       DATE,

            -- Status e efeitos
            status              VARCHAR(20) DEFAULT 'a_solicitar',
            efeitos             JSONB DEFAULT '{}'::jsonb,

            fundamento_legal    TEXT,
            observacoes         TEXT,

            created_at          DATE DEFAULT CURRENT_DATE,
            updated_at          DATE DEFAULT CURRENT_DATE
        )
        """
    )

    # Indexes — liminares
    op.execute("CREATE INDEX IF NOT EXISTS ix_liminares_empresa_id ON liminares (empresa_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_liminares_status ON liminares (status)")

    # ===================================================================
    # SEED: Conecta Eletrônica (empresa principal — já em operação)
    # ===================================================================
    op.execute(
        """
        INSERT INTO empresas (
            id, condominio_id, slug, razao_social, nome_fantasia, cnpj,
            inscricao_municipal, inscricao_suframa, codigo_municipio_ibge,
            regime_tributario,
            certificado_a1_path, certificado_a1_senha,
            contador_software,
            tipos_servicos, nfse_ambiente,
            status, is_principal,
            created_at, updated_at
        )
        SELECT
            gen_random_uuid(),
            id,
            'conecta_eletronica',
            'Jordan Santos de Jesus Ltda',
            'Conecta Mais Eletrônica',
            '35.710.481/0001-03',
            '45177801',
            '210140500',
            '1302603',
            'lucro_real',
            '/opt/conecta-pro/credentials/certificates/certificado.pfx',
            'Conecta123',
            'Domínio Sistemas (TOTVS)',
            '["portaria_remota", "monitoramento", "cftv", "alarmes", "controle_acesso", "automacao", "seguranca_eletronica"]'::jsonb,
            'homologacao',
            'ativa',
            true,
            CURRENT_DATE,
            CURRENT_DATE
        FROM condominios
        LIMIT 1
        ON CONFLICT (cnpj) DO NOTHING
        """
    )

    # ===================================================================
    # SEED: Conecta Patrimonial (em abertura — Simples Nacional Anexo III)
    # ===================================================================
    op.execute(
        """
        INSERT INTO empresas (
            id, condominio_id, slug, razao_social, nome_fantasia, cnpj,
            regime_tributario, anexo_simples,
            tipos_servicos, nfse_ambiente,
            status, is_principal,
            created_at, updated_at
        )
        SELECT
            gen_random_uuid(),
            id,
            'conecta_patrimonial',
            'Conecta Mais Patrimonial Ltda',
            'Conecta Mais Patrimonial',
            NULL,
            'simples_nacional',
            'III',
            '["vigilancia", "portaria_presencial", "portaria_24h", "portaria_12x36", "limpeza", "jardinagem", "facilities", "recepcao", "zeladoria"]'::jsonb,
            'homologacao',
            'em_abertura',
            false,
            CURRENT_DATE,
            CURRENT_DATE
        FROM condominios
        LIMIT 1
        """
    )

    # ===================================================================
    # SEED: Liminares para Conecta Patrimonial (a solicitar)
    # ===================================================================
    op.execute(
        """
        INSERT INTO liminares (
            id, empresa_id, tipo, descricao, fundamento_legal, status, efeitos,
            created_at, updated_at
        )
        SELECT
            gen_random_uuid(),
            e.id,
            'pis_cofins_zero',
            'Não cobrança de PIS e COFINS nas notas de serviço',
            'Bitributação — PIS e COFINS já estão inclusos no DAS do Simples Nacional (Lei Complementar 123/2006)',
            'a_solicitar',
            '{"pis": 0.0, "cofins": 0.0}'::jsonb,
            CURRENT_DATE,
            CURRENT_DATE
        FROM empresas e
        WHERE e.slug = 'conecta_patrimonial'
        """
    )

    op.execute(
        """
        INSERT INTO liminares (
            id, empresa_id, tipo, descricao, fundamento_legal, status, efeitos,
            created_at, updated_at
        )
        SELECT
            gen_random_uuid(),
            e.id,
            'inss_nao_retido',
            'Não retenção de INSS nas notas de serviço de vigilância',
            'INSS (CPP) já está incluso no DAS do Simples Nacional. A retenção na fonte configura bitributação (Lei Complementar 123/2006, Art. 18)',
            'a_solicitar',
            '{"inss_retido": false, "aliquota_retencao": 0.0}'::jsonb,
            CURRENT_DATE,
            CURRENT_DATE
        FROM empresas e
        WHERE e.slug = 'conecta_patrimonial'
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS liminares")
    op.execute("DROP TABLE IF EXISTS empresas")
