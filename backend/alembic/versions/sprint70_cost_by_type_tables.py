"""Create cost-by-service-type tables (Phase 3 Financial).

Revision ID: sprint70_cost_by_type_tables
Revises: sprint67_create_empresas_module
Create Date: 2026-03-09

"""

from alembic import op

revision = "sprint70_cost_by_type_tables"
down_revision = "sprint67_create_empresas_module"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ===================================================================
    # TABLE: custos_postos_portaria
    # ===================================================================
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS custos_postos_portaria (
            id                      UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
            posto_id                INTEGER,
            contrato_id             INTEGER,
            mes_referencia          DATE NOT NULL,
            tipo_escala             VARCHAR(20),
            qtd_funcionarios        INTEGER DEFAULT 1,
            custo_salarios          DECIMAL(12,2) DEFAULT 0,
            custo_encargos          DECIMAL(12,2) DEFAULT 0,
            custo_beneficios        DECIMAL(12,2) DEFAULT 0,
            custo_adicional_noturno DECIMAL(12,2) DEFAULT 0,
            custo_horas_extras      DECIMAL(12,2) DEFAULT 0,
            custo_uniformes         DECIMAL(12,2) DEFAULT 0,
            custo_equipamentos      DECIMAL(12,2) DEFAULT 0,
            custo_supervisao        DECIMAL(12,2) DEFAULT 0,
            custo_overhead          DECIMAL(12,2) DEFAULT 0,
            custo_total             DECIMAL(12,2) DEFAULT 0,
            margem_contratual       DECIMAL(12,2) DEFAULT 0,
            created_at              TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at              TIMESTAMP DEFAULT NOW()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_custos_postos_portaria_posto ON custos_postos_portaria(posto_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_custos_postos_portaria_contrato ON custos_postos_portaria(contrato_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_custos_postos_portaria_mes ON custos_postos_portaria(mes_referencia)")

    # ===================================================================
    # TABLE: custos_postos_limpeza
    # ===================================================================
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS custos_postos_limpeza (
            id                  UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
            posto_id            INTEGER,
            contrato_id         INTEGER,
            mes_referencia      DATE NOT NULL,
            area_m2             DECIMAL(10,2),
            tipo_limpeza        VARCHAR(30),
            custo_mao_obra      DECIMAL(12,2) DEFAULT 0,
            custo_encargos      DECIMAL(12,2) DEFAULT 0,
            custo_beneficios    DECIMAL(12,2) DEFAULT 0,
            custo_materiais     DECIMAL(12,2) DEFAULT 0,
            custo_equipamentos  DECIMAL(12,2) DEFAULT 0,
            custo_supervisao    DECIMAL(12,2) DEFAULT 0,
            custo_overhead      DECIMAL(12,2) DEFAULT 0,
            custo_total         DECIMAL(12,2) DEFAULT 0,
            custo_m2            DECIMAL(10,4),
            margem_contratual   DECIMAL(12,2) DEFAULT 0,
            created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMP DEFAULT NOW()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_custos_postos_limpeza_posto ON custos_postos_limpeza(posto_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_custos_postos_limpeza_contrato ON custos_postos_limpeza(contrato_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_custos_postos_limpeza_mes ON custos_postos_limpeza(mes_referencia)")

    # ===================================================================
    # TABLE: custos_postos_jardinagem
    # ===================================================================
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS custos_postos_jardinagem (
            id                  UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
            posto_id            INTEGER,
            contrato_id         INTEGER,
            mes_referencia      DATE NOT NULL,
            area_verde_m2       DECIMAL(10,2),
            frequencia_visitas  INTEGER DEFAULT 4,
            custo_mao_obra      DECIMAL(12,2) DEFAULT 0,
            custo_encargos      DECIMAL(12,2) DEFAULT 0,
            custo_beneficios    DECIMAL(12,2) DEFAULT 0,
            custo_insumos       DECIMAL(12,2) DEFAULT 0,
            custo_equipamentos  DECIMAL(12,2) DEFAULT 0,
            custo_combustivel   DECIMAL(12,2) DEFAULT 0,
            custo_supervisao    DECIMAL(12,2) DEFAULT 0,
            custo_overhead      DECIMAL(12,2) DEFAULT 0,
            custo_total         DECIMAL(12,2) DEFAULT 0,
            custo_m2            DECIMAL(10,4),
            margem_contratual   DECIMAL(12,2) DEFAULT 0,
            created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMP DEFAULT NOW()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_custos_postos_jardinagem_posto ON custos_postos_jardinagem(posto_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_custos_postos_jardinagem_mes ON custos_postos_jardinagem(mes_referencia)")

    # ===================================================================
    # TABLE: custos_contratos_seg_eletronica
    # ===================================================================
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS custos_contratos_seg_eletronica (
            id                      UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
            contrato_id             INTEGER,
            mes_referencia          DATE NOT NULL,
            qtd_cameras             INTEGER DEFAULT 0,
            qtd_pontos_monitorados  INTEGER DEFAULT 0,
            custo_monitoramento     DECIMAL(12,2) DEFAULT 0,
            custo_operadores        DECIMAL(12,2) DEFAULT 0,
            custo_manutencao        DECIMAL(12,2) DEFAULT 0,
            custo_conectividade     DECIMAL(12,2) DEFAULT 0,
            custo_software          DECIMAL(12,2) DEFAULT 0,
            custo_depreciacao       DECIMAL(12,2) DEFAULT 0,
            custo_overhead          DECIMAL(12,2) DEFAULT 0,
            custo_total             DECIMAL(12,2) DEFAULT 0,
            custo_por_camera        DECIMAL(10,4),
            margem_contratual       DECIMAL(12,2) DEFAULT 0,
            created_at              TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at              TIMESTAMP DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_custos_seg_eletronica_contrato ON custos_contratos_seg_eletronica(contrato_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_custos_seg_eletronica_mes ON custos_contratos_seg_eletronica(mes_referencia)"
    )

    # ===================================================================
    # TABLE: custos_contratos_portaria_remota
    # ===================================================================
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS custos_contratos_portaria_remota (
            id                      UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
            contrato_id             INTEGER,
            mes_referencia          DATE NOT NULL,
            qtd_unidades            INTEGER DEFAULT 1,
            qtd_acessos_mes         INTEGER DEFAULT 0,
            custo_central           DECIMAL(12,2) DEFAULT 0,
            custo_operadores        DECIMAL(12,2) DEFAULT 0,
            custo_equipamentos      DECIMAL(12,2) DEFAULT 0,
            custo_conectividade     DECIMAL(12,2) DEFAULT 0,
            custo_manutencao        DECIMAL(12,2) DEFAULT 0,
            custo_backup_presencial DECIMAL(12,2) DEFAULT 0,
            custo_overhead          DECIMAL(12,2) DEFAULT 0,
            custo_total             DECIMAL(12,2) DEFAULT 0,
            custo_por_unidade       DECIMAL(10,4),
            margem_contratual       DECIMAL(12,2) DEFAULT 0,
            created_at              TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at              TIMESTAMP DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_custos_portaria_remota_contrato ON custos_contratos_portaria_remota(contrato_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_custos_portaria_remota_mes ON custos_contratos_portaria_remota(mes_referencia)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS custos_contratos_portaria_remota")
    op.execute("DROP TABLE IF EXISTS custos_contratos_seg_eletronica")
    op.execute("DROP TABLE IF EXISTS custos_postos_jardinagem")
    op.execute("DROP TABLE IF EXISTS custos_postos_limpeza")
    op.execute("DROP TABLE IF EXISTS custos_postos_portaria")
