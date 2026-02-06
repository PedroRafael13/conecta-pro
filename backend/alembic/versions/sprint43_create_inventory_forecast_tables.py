"""Sprint 43: Create inventory forecast tables

Revision ID: sprint43_inventory_forecast
Revises: sprint40_signature
Create Date: 2025-01-05

Tabelas para previsao de estoque com IA:
- inventory_forecasts: Previsoes de demanda
- inventory_forecast_results: Resultados detalhados
- inventory_demand_patterns: Padroes de demanda identificados
"""

from alembic import op
from sqlalchemy.dialects import postgresql
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, ENUM


# revision identifiers
revision = 'sprint43_inventory_forecast'
down_revision = 'sprint40_signature'
branch_labels = None
depends_on = None


def create_enum_safe(name: str, values: list):
    """Cria enum de forma segura (ignora se já existir)."""
    values_str = ", ".join([f"'{v}'" for v in values])
    op.execute(f"""
        DO $$ BEGIN
            CREATE TYPE {name} AS ENUM ({values_str});
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)


def upgrade() -> None:
    """Criar tabelas de previsao de estoque."""

    # Enum types
    create_enum_safe("forecast_status", ["pending", "processing", "completed", "failed", "expired"])
    create_enum_safe("forecast_type", ["demand", "reorder", "seasonal", "trend"])
    create_enum_safe("pattern_type", ["constant", "trending", "seasonal", "cyclical", "irregular", "intermittent"])
    create_enum_safe("seasonality_type", ["none", "weekly", "monthly", "quarterly", "yearly", "custom"])
    create_enum_safe("trend_direction", ["stable", "increasing", "decreasing", "volatile"])

    # Tabela: inventory_forecasts
    op.create_table(
        'inventory_forecasts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),

        # Produto
        sa.Column('product_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('product_code', sa.String(50), nullable=False),
        sa.Column('product_name', sa.String(200), nullable=False),

        # Configuracao
        sa.Column('forecast_type', ENUM('demand', 'reorder', 'seasonal', 'trend',
                  name='forecast_type', create_type=False), server_default='demand', nullable=False),
        sa.Column('status', ENUM('pending', 'processing', 'completed', 'failed', 'expired',
                  name='forecast_status', create_type=False), server_default='pending', nullable=False, index=True),

        # Periodo
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=False),
        sa.Column('horizon_days', sa.Integer, server_default='30'),
        sa.Column('historical_days', sa.Integer, server_default='365'),
        sa.Column('data_points', sa.Integer, server_default='0'),

        # Modelo
        sa.Column('model_type', sa.String(50), server_default='prophet'),
        sa.Column('model_params', JSONB, server_default='{}'),

        # Metricas
        sa.Column('mae', sa.Float),
        sa.Column('mape', sa.Float),
        sa.Column('rmse', sa.Float),
        sa.Column('confidence_score', sa.Float),

        # Resultados agregados
        sa.Column('total_predicted_demand', sa.Float, server_default='0'),
        sa.Column('avg_daily_demand', sa.Float, server_default='0'),
        sa.Column('peak_demand', sa.Float, server_default='0'),
        sa.Column('peak_demand_date', sa.Date),
        sa.Column('min_demand', sa.Float, server_default='0'),
        sa.Column('min_demand_date', sa.Date),

        # Recomendacoes
        sa.Column('suggested_reorder_point', sa.Float),
        sa.Column('suggested_reorder_quantity', sa.Float),
        sa.Column('suggested_safety_stock', sa.Float),

        # Metadados
        sa.Column('created_by', UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),
        sa.Column('completed_at', sa.DateTime),
        sa.Column('expires_at', sa.DateTime),

        # Flags
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False),
        sa.Column('is_automated', sa.Boolean, server_default='false'),

        # Notas
        sa.Column('notes', sa.Text),
        sa.Column('error_message', sa.Text),
    )

    # Indices
    op.create_index(
        'ix_forecasts_product_status',
        'inventory_forecasts',
        ['product_id', 'status']
    )
    op.create_index(
        'ix_forecasts_dates',
        'inventory_forecasts',
        ['start_date', 'end_date']
    )

    # Tabela: inventory_forecast_results
    op.create_table(
        'inventory_forecast_results',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),

        # Relacionamento
        sa.Column('forecast_id', UUID(as_uuid=True),
                  sa.ForeignKey('inventory_forecasts.id', ondelete='CASCADE'),
                  nullable=False, index=True),

        # Periodo
        sa.Column('date', sa.Date, nullable=False, index=True),
        sa.Column('period_type', sa.String(20), server_default='daily'),

        # Valores previstos
        sa.Column('predicted_demand', sa.Float, nullable=False),
        sa.Column('lower_bound', sa.Float),
        sa.Column('upper_bound', sa.Float),
        sa.Column('confidence_level', sa.Float, server_default='0.95'),

        # Valores reais
        sa.Column('actual_demand', sa.Float),
        sa.Column('variance', sa.Float),
        sa.Column('variance_pct', sa.Float),

        # Componentes
        sa.Column('trend_component', sa.Float),
        sa.Column('seasonal_component', sa.Float),
        sa.Column('residual_component', sa.Float),

        # Flags
        sa.Column('is_anomaly', sa.Boolean, server_default='false'),
        sa.Column('anomaly_type', sa.String(50)),

        # Metadados
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # Indice composto para busca eficiente
    op.create_index(
        'ix_forecast_results_forecast_date',
        'inventory_forecast_results',
        ['forecast_id', 'date']
    )

    # Tabela: inventory_demand_patterns
    op.create_table(
        'inventory_demand_patterns',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),

        # Produto
        sa.Column('product_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('product_code', sa.String(50), nullable=False),
        sa.Column('product_name', sa.String(200), nullable=False),

        # Periodo analisado
        sa.Column('analysis_start_date', sa.Date, nullable=False),
        sa.Column('analysis_end_date', sa.Date, nullable=False),
        sa.Column('total_data_points', sa.Integer, server_default='0'),

        # Classificacao
        sa.Column('pattern_type', ENUM('constant', 'trending', 'seasonal', 'cyclical',
                  'irregular', 'intermittent', name='pattern_type', create_type=False),
                  server_default='constant', nullable=False),
        sa.Column('pattern_confidence', sa.Float, server_default='0'),

        # Sazonalidade
        sa.Column('seasonality_type', ENUM('none', 'weekly', 'monthly', 'quarterly',
                  'yearly', 'custom', name='seasonality_type', create_type=False),
                  server_default='none', nullable=False),
        sa.Column('seasonality_strength', sa.Float, server_default='0'),
        sa.Column('seasonal_periods', ARRAY(sa.Integer)),
        sa.Column('peak_periods', JSONB, server_default='[]'),

        # Tendencia
        sa.Column('trend_direction', ENUM('stable', 'increasing', 'decreasing', 'volatile',
                  name='trend_direction', create_type=False), server_default='stable', nullable=False),
        sa.Column('trend_slope', sa.Float, server_default='0'),
        sa.Column('trend_strength', sa.Float, server_default='0'),

        # Estatisticas
        sa.Column('avg_demand', sa.Float, server_default='0'),
        sa.Column('std_demand', sa.Float, server_default='0'),
        sa.Column('cv_demand', sa.Float, server_default='0'),
        sa.Column('median_demand', sa.Float, server_default='0'),
        sa.Column('min_demand', sa.Float, server_default='0'),
        sa.Column('max_demand', sa.Float, server_default='0'),

        # Analises
        sa.Column('volatility_index', sa.Float, server_default='0'),
        sa.Column('predictability_score', sa.Float, server_default='0'),
        sa.Column('anomalies_detected', sa.Integer, server_default='0'),
        sa.Column('anomaly_dates', JSONB, server_default='[]'),
        sa.Column('anomaly_impact', sa.Float, server_default='0'),

        # Ciclos
        sa.Column('cycle_length_days', sa.Integer),
        sa.Column('cycle_amplitude', sa.Float),

        # Distribuicoes
        sa.Column('weekday_distribution', JSONB, server_default='{}'),
        sa.Column('monthly_distribution', JSONB, server_default='{}'),

        # Recomendacoes
        sa.Column('recommended_model', sa.String(50)),
        sa.Column('recommended_safety_stock_days', sa.Integer),
        sa.Column('recommended_review_period_days', sa.Integer),

        # Metadados
        sa.Column('analyzed_by', UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, onupdate=sa.func.now()),

        # Flags
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False),
        sa.Column('needs_update', sa.Boolean, server_default='false'),
        sa.Column('last_validation_date', sa.Date),

        # Notas
        sa.Column('notes', sa.Text),
        sa.Column('insights', JSONB, server_default='[]'),
    )

    # Indices
    op.create_index(
        'ix_patterns_product_active',
        'inventory_demand_patterns',
        ['product_id', 'is_active']
    )
    op.create_index(
        'ix_patterns_predictability',
        'inventory_demand_patterns',
        ['predictability_score']
    )


def downgrade() -> None:
    """Remover tabelas de previsao de estoque."""

    # Remover tabelas
    op.drop_table('inventory_forecast_results')
    op.drop_table('inventory_forecasts')
    op.drop_table('inventory_demand_patterns')

    # Remover enums
    op.execute('DROP TYPE IF EXISTS forecast_status')
    op.execute('DROP TYPE IF EXISTS forecast_type')
    op.execute('DROP TYPE IF EXISTS pattern_type')
    op.execute('DROP TYPE IF EXISTS seasonality_type')
    op.execute('DROP TYPE IF EXISTS trend_direction')
