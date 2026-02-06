# Sprint 06: Business Intelligence Avançado

## 🎯 Objetivo Principal
Implementar um sistema completo de Business Intelligence que transforme dados em insights acionáveis através de dashboards interativos, relatórios automatizados, análise preditiva e visualizações em tempo real.

## 📋 Especificações Técnicas

### Funcionalidades Core
- **Data Warehouse**: Estrutura OLAP otimizada para analytics
- **ETL Pipeline**: Extração, transformação e carregamento automático
- **Dashboard Builder**: Editor drag-and-drop para dashboards personalizados
- **Report Engine**: Geração automática de relatórios com agendamento
- **Real-time Analytics**: Processamento de dados em tempo real
- **Data Mining**: Descoberta de padrões e correlações
- **Forecasting**: Previsões baseadas em machine learning
- **KPI Monitoring**: Monitoramento de indicadores-chave
- **Drill-down Analysis**: Análise detalhada multi-nível
- **Export Engine**: Múltiplos formatos de exportação

### Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     BUSINESS INTELLIGENCE PLATFORM                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                │
│  │ WEB CLIENT  │    │   MOBILE    │    │ REPORTING   │                │
│  │ DASHBOARD   │    │  DASHBOARD  │    │   PORTAL    │                │
│  └─────────────┘    └─────────────┘    └─────────────┘                │
│         │                   │                   │                       │
│         └─────────────────────┼───────────────────┘                       │
│                               │                                           │
│  ┌─────────────────────────────┼─────────────────────────────────────┐   │
│  │                    BI API LAYER                                   │   │
│  │                             │                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │ DASHBOARD   │  │   QUERY     │  │   REPORT    │              │   │
│  │  │    API      │  │ BUILDER API │  │ ENGINE API  │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                               │                                           │
│  ┌─────────────────────────────┼─────────────────────────────────────┐   │
│  │                 BI PROCESSING ENGINE                              │   │
│  │                             │                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │   QUERY     │  │  AGGREGATION│  │   CACHE     │              │   │
│  │  │ PROCESSOR   │  │   ENGINE    │  │  MANAGER    │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  │                                                                  │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │   REAL-TIME │  │ MACHINE     │  │   EXPORT    │              │   │
│  │  │ PROCESSOR   │  │ LEARNING    │  │   ENGINE    │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                               │                                           │
│  ┌─────────────────────────────┼─────────────────────────────────────┐   │
│  │                    DATA LAYER                                    │   │
│  │                             │                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │    DATA     │  │    OLAP     │  │    CACHE    │              │   │
│  │  │ WAREHOUSE   │  │    CUBES    │  │   LAYER     │              │   │
│  │  │(PostgreSQL) │  │             │  │  (Redis)    │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  │                                                                  │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │ OPERATIONAL │  │   STAGING   │  │   METADATA  │              │   │
│  │  │ DATABASE    │  │   AREA      │  │  CATALOG    │              │   │
│  │  │(PostgreSQL) │  │             │  │             │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                               │                                           │
│  ┌─────────────────────────────┼─────────────────────────────────────┐   │
│  │                    ETL PIPELINE                                   │   │
│  │                             │                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │ EXTRACTION  │  │TRANSFORMATION│  │  LOADING    │              │   │
│  │  │  MODULES    │  │   MODULES   │  │  MODULES    │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  │                                                                  │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │ SCHEDULER   │  │   DATA      │  │ QUALITY     │              │   │
│  │  │ SERVICE     │  │ VALIDATION  │  │ MONITOR     │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🗄️ Modelos de Data Warehouse

### Dimensões e Fatos
```sql
-- Dimensão Tempo
CREATE TABLE dim_time (
    time_key INTEGER PRIMARY KEY,
    date_value DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN NOT NULL,
    fiscal_year INTEGER NOT NULL,
    fiscal_quarter INTEGER NOT NULL
);

-- Dimensão Cliente
CREATE TABLE dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id UUID NOT NULL UNIQUE,
    customer_name VARCHAR(200) NOT NULL,
    customer_type VARCHAR(50) NOT NULL,
    segment VARCHAR(50),
    industry VARCHAR(100),
    company_size VARCHAR(50),
    location_city VARCHAR(100),
    location_state VARCHAR(100),
    location_country VARCHAR(100),
    registration_date DATE,
    status VARCHAR(50),
    lifetime_value DECIMAL(15,2),
    risk_score INTEGER,
    
    -- SCD Type 2 fields
    effective_date DATE NOT NULL DEFAULT CURRENT_DATE,
    expiry_date DATE DEFAULT '2999-12-31',
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    version_number INTEGER NOT NULL DEFAULT 1,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Dimensão Produto/Serviço
CREATE TABLE dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id UUID NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_code VARCHAR(50),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    unit_price DECIMAL(10,2),
    cost_price DECIMAL(10,2),
    margin_percent DECIMAL(5,2),
    status VARCHAR(50),
    
    -- SCD fields
    effective_date DATE NOT NULL DEFAULT CURRENT_DATE,
    expiry_date DATE DEFAULT '2999-12-31',
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Dimensão Canal
CREATE TABLE dim_channel (
    channel_key SERIAL PRIMARY KEY,
    channel_id VARCHAR(50) NOT NULL UNIQUE,
    channel_name VARCHAR(100) NOT NULL,
    channel_type VARCHAR(50), -- 'online', 'offline', 'mobile', 'partner'
    parent_channel VARCHAR(100),
    cost_per_acquisition DECIMAL(10,2),
    conversion_rate DECIMAL(5,4),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Dimensão Campanha
CREATE TABLE dim_campaign (
    campaign_key SERIAL PRIMARY KEY,
    campaign_id UUID NOT NULL,
    campaign_name VARCHAR(200) NOT NULL,
    campaign_type VARCHAR(50),
    channel_key INTEGER REFERENCES dim_channel(channel_key),
    start_date DATE,
    end_date DATE,
    budget DECIMAL(15,2),
    target_audience TEXT,
    goal_type VARCHAR(50),
    goal_value DECIMAL(15,2),
    status VARCHAR(50),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Fato Vendas
CREATE TABLE fact_sales (
    sales_key BIGSERIAL PRIMARY KEY,
    
    -- Foreign keys para dimensões
    time_key INTEGER REFERENCES dim_time(time_key),
    customer_key INTEGER REFERENCES dim_customer(customer_key),
    product_key INTEGER REFERENCES dim_product(product_key),
    channel_key INTEGER REFERENCES dim_channel(channel_key),
    campaign_key INTEGER REFERENCES dim_campaign(campaign_key),
    
    -- Chave do transação original
    transaction_id UUID NOT NULL,
    
    -- Métricas
    quantity INTEGER NOT NULL DEFAULT 0,
    unit_price DECIMAL(10,2) NOT NULL DEFAULT 0,
    discount_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    tax_amount DECIMAL(10,2) NOT NULL DEFAULT 0,
    total_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    cost_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    profit_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
    
    -- Flags e indicadores
    is_refunded BOOLEAN DEFAULT FALSE,
    is_first_purchase BOOLEAN DEFAULT FALSE,
    payment_method VARCHAR(50),
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Índices para performance
    CONSTRAINT fact_sales_unique UNIQUE (transaction_id, product_key)
);

-- Fato Marketing
CREATE TABLE fact_marketing (
    marketing_key BIGSERIAL PRIMARY KEY,
    
    -- Dimensões
    time_key INTEGER REFERENCES dim_time(time_key),
    channel_key INTEGER REFERENCES dim_channel(channel_key),
    campaign_key INTEGER REFERENCES dim_campaign(campaign_key),
    
    -- Métricas de marketing
    impressions BIGINT DEFAULT 0,
    clicks BIGINT DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    leads INTEGER DEFAULT 0,
    qualified_leads INTEGER DEFAULT 0,
    opportunities INTEGER DEFAULT 0,
    
    -- Valores financeiros
    spend_amount DECIMAL(15,2) DEFAULT 0,
    revenue_amount DECIMAL(15,2) DEFAULT 0,
    
    -- Métricas calculadas
    ctr DECIMAL(8,6) GENERATED ALWAYS AS (
        CASE WHEN impressions > 0 THEN clicks::decimal / impressions::decimal ELSE 0 END
    ) STORED,
    
    cpc DECIMAL(10,2) GENERATED ALWAYS AS (
        CASE WHEN clicks > 0 THEN spend_amount / clicks ELSE 0 END
    ) STORED,
    
    roas DECIMAL(8,2) GENERATED ALWAYS AS (
        CASE WHEN spend_amount > 0 THEN revenue_amount / spend_amount ELSE 0 END
    ) STORED,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Fato Atendimento
CREATE TABLE fact_support (
    support_key BIGSERIAL PRIMARY KEY,
    
    -- Dimensões
    time_key INTEGER REFERENCES dim_time(time_key),
    customer_key INTEGER REFERENCES dim_customer(customer_key),
    
    -- Identificadores
    ticket_id UUID NOT NULL UNIQUE,
    agent_id UUID,
    
    -- Métricas temporais (em minutos)
    first_response_time INTEGER,
    resolution_time INTEGER,
    total_interaction_time INTEGER,
    
    -- Categorização
    category VARCHAR(100),
    subcategory VARCHAR(100),
    priority VARCHAR(20), -- 'low', 'medium', 'high', 'critical'
    status VARCHAR(50),
    
    -- Satisfação
    satisfaction_score INTEGER CHECK (satisfaction_score BETWEEN 1 AND 5),
    
    -- Flags
    is_escalated BOOLEAN DEFAULT FALSE,
    is_resolved BOOLEAN DEFAULT FALSE,
    requires_followup BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para otimização de queries
CREATE INDEX idx_fact_sales_time ON fact_sales(time_key);
CREATE INDEX idx_fact_sales_customer ON fact_sales(customer_key);
CREATE INDEX idx_fact_sales_product ON fact_sales(product_key);
CREATE INDEX idx_fact_sales_date_customer ON fact_sales(time_key, customer_key);

CREATE INDEX idx_fact_marketing_time_campaign ON fact_marketing(time_key, campaign_key);
CREATE INDEX idx_fact_marketing_channel ON fact_marketing(channel_key);

CREATE INDEX idx_fact_support_time_customer ON fact_support(time_key, customer_key);

-- Views para análises comuns
CREATE OR REPLACE VIEW v_sales_summary AS
SELECT 
    dt.year,
    dt.quarter,
    dt.month,
    dt.month_name,
    dc.customer_type,
    dc.segment,
    dp.category as product_category,
    dch.channel_type,
    
    COUNT(*) as transaction_count,
    SUM(fs.quantity) as total_quantity,
    SUM(fs.total_amount) as total_revenue,
    SUM(fs.profit_amount) as total_profit,
    AVG(fs.total_amount) as avg_transaction_value,
    COUNT(DISTINCT fs.customer_key) as unique_customers
    
FROM fact_sales fs
JOIN dim_time dt ON fs.time_key = dt.time_key
JOIN dim_customer dc ON fs.customer_key = dc.customer_key AND dc.is_current = TRUE
JOIN dim_product dp ON fs.product_key = dp.product_key AND dp.is_current = TRUE
JOIN dim_channel dch ON fs.channel_key = dch.channel_key

WHERE fs.is_refunded = FALSE

GROUP BY CUBE (
    dt.year, dt.quarter, dt.month, dt.month_name,
    dc.customer_type, dc.segment,
    dp.category,
    dch.channel_type
);
```

### Metadados e Configuração
```sql
-- Catálogo de dashboards
CREATE TABLE bi_dashboards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    
    -- Configuração
    layout_config JSONB,
    filter_config JSONB,
    refresh_interval INTEGER DEFAULT 300, -- em segundos
    
    -- Permissões
    owner_id UUID REFERENCES users(id),
    is_public BOOLEAN DEFAULT FALSE,
    allowed_roles TEXT[],
    
    -- Estado
    is_active BOOLEAN DEFAULT TRUE,
    view_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Widgets dos dashboards
CREATE TABLE bi_dashboard_widgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dashboard_id UUID REFERENCES bi_dashboards(id) ON DELETE CASCADE,
    
    -- Configuração do widget
    widget_type VARCHAR(50) NOT NULL, -- 'chart', 'table', 'kpi', 'text'
    title VARCHAR(200),
    description TEXT,
    
    -- Posição e tamanho
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL,
    size_width INTEGER NOT NULL DEFAULT 4,
    size_height INTEGER NOT NULL DEFAULT 3,
    
    -- Configuração específica
    data_source JSONB, -- Query, filtros, etc
    visualization_config JSONB, -- Tipo de gráfico, cores, etc
    
    -- Estado
    is_active BOOLEAN DEFAULT TRUE,
    order_index INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Relatórios agendados
CREATE TABLE bi_scheduled_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Configuração do relatório
    dashboard_id UUID REFERENCES bi_dashboards(id),
    report_format VARCHAR(20) DEFAULT 'PDF', -- 'PDF', 'Excel', 'CSV'
    
    -- Agendamento
    schedule_cron VARCHAR(100) NOT NULL, -- Expressão cron
    timezone VARCHAR(50) DEFAULT 'UTC',
    next_run_at TIMESTAMPTZ,
    
    -- Destinatários
    email_recipients TEXT[],
    webhook_url VARCHAR(500),
    
    -- Estado
    is_active BOOLEAN DEFAULT TRUE,
    last_run_at TIMESTAMPTZ,
    last_status VARCHAR(50),
    run_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Log de execuções de relatórios
CREATE TABLE bi_report_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id UUID REFERENCES bi_scheduled_reports(id) ON DELETE CASCADE,
    
    -- Execução
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    status VARCHAR(50) NOT NULL, -- 'running', 'completed', 'failed'
    
    -- Resultado
    output_file_path VARCHAR(500),
    output_size_bytes BIGINT,
    error_message TEXT,
    
    -- Métricas
    processing_time_seconds INTEGER,
    rows_processed BIGINT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cache de consultas BI
CREATE TABLE bi_query_cache (
    cache_key VARCHAR(255) PRIMARY KEY,
    query_hash VARCHAR(64) NOT NULL,
    
    -- Dados em cache
    result_data JSONB,
    result_metadata JSONB,
    
    -- Controle de cache
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    hit_count INTEGER DEFAULT 0,
    last_hit_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analytics de uso do BI
CREATE TABLE bi_usage_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Evento
    event_type VARCHAR(50) NOT NULL, -- 'dashboard_view', 'widget_interact', 'export'
    user_id UUID REFERENCES users(id),
    session_id VARCHAR(100),
    
    -- Recursos acessados
    dashboard_id UUID,
    widget_id UUID,
    
    -- Contexto
    ip_address INET,
    user_agent TEXT,
    referrer VARCHAR(500),
    
    -- Métricas de performance
    load_time_ms INTEGER,
    query_time_ms INTEGER,
    
    -- Dados do evento
    event_data JSONB,
    
    occurred_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 🚀 Implementação Core

### 1. BI Engine Principal

```python
# app/bi/engine.py
from typing import Dict, List, Optional, Any, Union
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
from sqlalchemy import text, create_engine
import plotly.graph_objs as go
import plotly.express as px

@dataclass
class QueryResult:
    """Resultado de uma consulta BI"""
    data: List[Dict[str, Any]]
    columns: List[str]
    row_count: int
    execution_time_ms: int
    cache_hit: bool
    metadata: Dict[str, Any]

@dataclass
class ChartConfig:
    """Configuração de gráfico"""
    chart_type: str  # 'line', 'bar', 'pie', 'scatter', 'heatmap'
    x_axis: str
    y_axis: Union[str, List[str]]
    color_by: Optional[str] = None
    size_by: Optional[str] = None
    aggregation: str = 'sum'  # 'sum', 'avg', 'count', 'min', 'max'
    title: Optional[str] = None
    colors: Optional[List[str]] = None

class BIEngine:
    """Engine principal de Business Intelligence"""
    
    def __init__(self):
        self.query_cache = {}
        self.cache_ttl = 3600  # 1 hora
        self.metadata_catalog = {}
        
    async def initialize(self):
        """Inicializa o BI engine"""
        await self._load_metadata_catalog()
        await self._initialize_dimension_cache()
        
    async def execute_query(self, sql: str, parameters: Optional[Dict] = None,
                           use_cache: bool = True, cache_ttl: int = None) -> QueryResult:
        """Executa uma consulta SQL otimizada para BI"""
        
        # Gera chave de cache
        cache_key = self._generate_cache_key(sql, parameters)
        
        # Verifica cache se habilitado
        if use_cache and cache_key in self.query_cache:
            cached_result = self.query_cache[cache_key]
            if datetime.now() < cached_result['expires_at']:
                return QueryResult(
                    data=cached_result['data'],
                    columns=cached_result['columns'],
                    row_count=cached_result['row_count'],
                    execution_time_ms=0,
                    cache_hit=True,
                    metadata=cached_result['metadata']
                )
        
        # Executa query
        start_time = datetime.now()
        
        try:
            # Aqui conectaria com o banco real
            # Por enquanto, simula execução
            await asyncio.sleep(0.1)  # Simula latência do banco
            
            # Dados simulados baseados no tipo de query
            if 'fact_sales' in sql.lower():
                data = await self._simulate_sales_data()
            elif 'fact_marketing' in sql.lower():
                data = await self._simulate_marketing_data()
            elif 'fact_support' in sql.lower():
                data = await self._simulate_support_data()
            else:
                data = []
            
            columns = list(data[0].keys()) if data else []
            
            end_time = datetime.now()
            execution_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            result = QueryResult(
                data=data,
                columns=columns,
                row_count=len(data),
                execution_time_ms=execution_time_ms,
                cache_hit=False,
                metadata={'query_type': 'select', 'optimized': True}
            )
            
            # Cache do resultado
            if use_cache:
                ttl = cache_ttl or self.cache_ttl
                self.query_cache[cache_key] = {
                    'data': data,
                    'columns': columns,
                    'row_count': len(data),
                    'metadata': result.metadata,
                    'expires_at': datetime.now() + timedelta(seconds=ttl)
                }
            
            return result
            
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
    
    async def build_chart(self, data: List[Dict], config: ChartConfig) -> Dict:
        """Constrói gráfico a partir dos dados e configuração"""
        
        if not data:
            return {"error": "No data available"}
        
        # Converte para DataFrame para facilitar manipulação
        df = pd.DataFrame(data)
        
        # Aplica agregação se necessário
        if config.aggregation != 'none' and config.x_axis in df.columns:
            if isinstance(config.y_axis, list):
                # Múltiplas séries
                agg_df = df.groupby(config.x_axis)[config.y_axis].agg(config.aggregation).reset_index()
            else:
                # Série única
                agg_df = df.groupby(config.x_axis)[config.y_axis].agg(config.aggregation).reset_index()
        else:
            agg_df = df
        
        # Constrói gráfico baseado no tipo
        if config.chart_type == 'line':
            return await self._build_line_chart(agg_df, config)
        elif config.chart_type == 'bar':
            return await self._build_bar_chart(agg_df, config)
        elif config.chart_type == 'pie':
            return await self._build_pie_chart(agg_df, config)
        elif config.chart_type == 'scatter':
            return await self._build_scatter_chart(agg_df, config)
        elif config.chart_type == 'heatmap':
            return await self._build_heatmap(agg_df, config)
        else:
            return {"error": f"Unsupported chart type: {config.chart_type}"}
    
    async def _build_line_chart(self, df: pd.DataFrame, config: ChartConfig) -> Dict:
        """Constrói gráfico de linhas"""
        
        traces = []
        
        if isinstance(config.y_axis, list):
            # Múltiplas linhas
            for i, y_col in enumerate(config.y_axis):
                if y_col in df.columns:
                    color = config.colors[i] if config.colors and i < len(config.colors) else None
                    traces.append({
                        "x": df[config.x_axis].tolist(),
                        "y": df[y_col].tolist(),
                        "name": y_col,
                        "type": "scatter",
                        "mode": "lines+markers",
                        "line": {"color": color} if color else {}
                    })
        else:
            # Linha única
            traces.append({
                "x": df[config.x_axis].tolist(),
                "y": df[config.y_axis].tolist(),
                "type": "scatter",
                "mode": "lines+markers",
                "name": config.y_axis
            })
        
        layout = {
            "title": config.title or "Line Chart",
            "xaxis": {"title": config.x_axis},
            "yaxis": {"title": config.y_axis if isinstance(config.y_axis, str) else "Value"},
            "showlegend": len(traces) > 1
        }
        
        return {
            "data": traces,
            "layout": layout,
            "type": "plotly"
        }
    
    async def _build_bar_chart(self, df: pd.DataFrame, config: ChartConfig) -> Dict:
        """Constrói gráfico de barras"""
        
        if isinstance(config.y_axis, list):
            # Barras agrupadas
            traces = []
            for y_col in config.y_axis:
                if y_col in df.columns:
                    traces.append({
                        "x": df[config.x_axis].tolist(),
                        "y": df[y_col].tolist(),
                        "name": y_col,
                        "type": "bar"
                    })
        else:
            # Barras simples
            traces = [{
                "x": df[config.x_axis].tolist(),
                "y": df[config.y_axis].tolist(),
                "type": "bar",
                "name": config.y_axis
            }]
        
        layout = {
            "title": config.title or "Bar Chart",
            "xaxis": {"title": config.x_axis},
            "yaxis": {"title": config.y_axis if isinstance(config.y_axis, str) else "Value"},
            "barmode": "group" if isinstance(config.y_axis, list) else "relative"
        }
        
        return {
            "data": traces,
            "layout": layout,
            "type": "plotly"
        }
    
    async def _build_pie_chart(self, df: pd.DataFrame, config: ChartConfig) -> Dict:
        """Constrói gráfico de pizza"""
        
        trace = {
            "labels": df[config.x_axis].tolist(),
            "values": df[config.y_axis].tolist(),
            "type": "pie",
            "hole": 0.3,  # Donut chart
            "textinfo": "label+percent"
        }
        
        layout = {
            "title": config.title or "Pie Chart",
            "showlegend": True
        }
        
        return {
            "data": [trace],
            "layout": layout,
            "type": "plotly"
        }
    
    async def generate_dashboard_data(self, dashboard_id: str) -> Dict:
        """Gera dados completos de um dashboard"""
        
        # Simula configuração do dashboard
        widgets = await self._get_dashboard_widgets(dashboard_id)
        
        dashboard_data = {
            "dashboard_id": dashboard_id,
            "generated_at": datetime.now().isoformat(),
            "widgets": []
        }
        
        for widget in widgets:
            if widget['widget_type'] == 'kpi':
                widget_data = await self._generate_kpi_widget(widget)
            elif widget['widget_type'] == 'chart':
                widget_data = await self._generate_chart_widget(widget)
            elif widget['widget_type'] == 'table':
                widget_data = await self._generate_table_widget(widget)
            else:
                widget_data = {"error": "Unknown widget type"}
            
            dashboard_data["widgets"].append({
                "widget_id": widget['id'],
                "type": widget['widget_type'],
                "title": widget['title'],
                "position": {
                    "x": widget['position_x'],
                    "y": widget['position_y'],
                    "width": widget['size_width'],
                    "height": widget['size_height']
                },
                "data": widget_data
            })
        
        return dashboard_data
    
    async def _generate_kpi_widget(self, widget_config: Dict) -> Dict:
        """Gera dados para widget KPI"""
        
        # Simula diferentes KPIs baseados na configuração
        kpi_type = widget_config.get('data_source', {}).get('kpi_type', 'revenue')
        
        if kpi_type == 'revenue':
            current_value = 285750.50
            previous_value = 248920.30
        elif kpi_type == 'customers':
            current_value = 1247
            previous_value = 1180
        elif kpi_type == 'conversion_rate':
            current_value = 3.8
            previous_value = 3.2
        else:
            current_value = 100
            previous_value = 95
        
        change = ((current_value - previous_value) / previous_value) * 100
        
        return {
            "value": current_value,
            "previous_value": previous_value,
            "change_percent": round(change, 1),
            "trend": "up" if change > 0 else "down",
            "format": widget_config.get('visualization_config', {}).get('format', 'currency')
        }
    
    async def _generate_chart_widget(self, widget_config: Dict) -> Dict:
        """Gera dados para widget de gráfico"""
        
        # Executa query configurada no widget
        data_source = widget_config.get('data_source', {})
        query = data_source.get('query', 'SELECT * FROM v_sales_summary LIMIT 10')
        
        result = await self.execute_query(query)
        
        # Configuração de visualização
        viz_config = widget_config.get('visualization_config', {})
        chart_config = ChartConfig(
            chart_type=viz_config.get('chart_type', 'bar'),
            x_axis=viz_config.get('x_axis', 'month_name'),
            y_axis=viz_config.get('y_axis', 'total_revenue'),
            title=widget_config.get('title', 'Chart')
        )
        
        # Constrói gráfico
        return await self.build_chart(result.data, chart_config)
    
    async def _simulate_sales_data(self) -> List[Dict]:
        """Simula dados de vendas para demonstração"""
        
        return [
            {
                "month_name": "Janeiro",
                "total_revenue": 125850.75,
                "total_profit": 37755.23,
                "transaction_count": 342,
                "unique_customers": 187,
                "avg_transaction_value": 368.13
            },
            {
                "month_name": "Fevereiro", 
                "total_revenue": 143920.30,
                "total_profit": 43176.09,
                "transaction_count": 398,
                "unique_customers": 215,
                "avg_transaction_value": 361.66
            },
            {
                "month_name": "Março",
                "total_revenue": 158750.45,
                "total_profit": 47625.14,
                "transaction_count": 425,
                "unique_customers": 234,
                "avg_transaction_value": 373.53
            },
            {
                "month_name": "Abril",
                "total_revenue": 171230.20,
                "total_profit": 51369.06,
                "transaction_count": 467,
                "unique_customers": 251,
                "avg_transaction_value": 366.68
            },
            {
                "month_name": "Maio",
                "total_revenue": 189450.80,
                "total_profit": 56835.24,
                "transaction_count": 512,
                "unique_customers": 278,
                "avg_transaction_value": 369.92
            },
            {
                "month_name": "Junho",
                "total_revenue": 205180.15,
                "total_profit": 61554.05,
                "transaction_count": 548,
                "unique_customers": 295,
                "avg_transaction_value": 374.45
            }
        ]

# Singleton do BI engine
bi_engine = BIEngine()
```

### 2. Sistema ETL

```python
# app/bi/etl.py
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import pandas as pd
from sqlalchemy import text

@dataclass
class ETLJobConfig:
    """Configuração de um job ETL"""
    job_id: str
    name: str
    source_type: str  # 'database', 'api', 'file'
    source_config: Dict
    target_table: str
    transformation_rules: List[Dict]
    schedule: str  # Expressão cron
    is_incremental: bool = True
    batch_size: int = 1000

class ETLEngine:
    """Engine de ETL para alimentar o data warehouse"""
    
    def __init__(self):
        self.active_jobs = {}
        self.job_history = []
        
    async def register_etl_job(self, config: ETLJobConfig):
        """Registra um novo job ETL"""
        self.active_jobs[config.job_id] = config
        
    async def execute_job(self, job_id: str) -> Dict:
        """Executa um job ETL"""
        
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job_config = self.active_jobs[job_id]
        execution_start = datetime.now()
        
        try:
            # Extração
            extraction_result = await self._extract_data(job_config)
            
            # Transformação
            transformation_result = await self._transform_data(
                extraction_result, job_config.transformation_rules
            )
            
            # Carregamento
            loading_result = await self._load_data(
                transformation_result, job_config.target_table
            )
            
            execution_end = datetime.now()
            duration = (execution_end - execution_start).total_seconds()
            
            # Log da execução
            execution_log = {
                "job_id": job_id,
                "started_at": execution_start.isoformat(),
                "completed_at": execution_end.isoformat(),
                "duration_seconds": duration,
                "status": "success",
                "records_extracted": extraction_result["count"],
                "records_transformed": transformation_result["count"],
                "records_loaded": loading_result["count"],
                "errors": []
            }
            
            self.job_history.append(execution_log)
            
            return execution_log
            
        except Exception as e:
            execution_end = datetime.now()
            duration = (execution_end - execution_start).total_seconds()
            
            execution_log = {
                "job_id": job_id,
                "started_at": execution_start.isoformat(),
                "completed_at": execution_end.isoformat(),
                "duration_seconds": duration,
                "status": "failed",
                "error": str(e),
                "records_extracted": 0,
                "records_transformed": 0,
                "records_loaded": 0
            }
            
            self.job_history.append(execution_log)
            raise
    
    async def _extract_data(self, job_config: ETLJobConfig) -> Dict:
        """Extrai dados da fonte configurada"""
        
        source_type = job_config.source_type
        source_config = job_config.source_config
        
        if source_type == 'database':
            return await self._extract_from_database(source_config)
        elif source_type == 'api':
            return await self._extract_from_api(source_config)
        elif source_type == 'file':
            return await self._extract_from_file(source_config)
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
    
    async def _extract_from_database(self, config: Dict) -> Dict:
        """Extrai dados de uma fonte de banco de dados"""
        
        # Simula extração de dados transacionais
        # Na implementação real, conectaria com o banco operacional
        
        if config.get('table') == 'transactions':
            data = [
                {
                    "id": f"txn_{i}",
                    "customer_id": f"cust_{i % 100}",
                    "product_id": f"prod_{i % 50}",
                    "amount": 100 + (i * 10.50),
                    "quantity": i % 5 + 1,
                    "channel": ["online", "mobile", "store"][i % 3],
                    "created_at": datetime.now() - timedelta(days=i % 30)
                }
                for i in range(500)  # Simula 500 transações
            ]
        else:
            data = []
        
        return {"data": data, "count": len(data)}
    
    async def _extract_from_api(self, config: Dict) -> Dict:
        """Extrai dados de uma API externa"""
        
        # Simula chamada para API externa
        await asyncio.sleep(0.1)  # Simula latência de rede
        
        # Dados simulados baseados no endpoint
        endpoint = config.get('endpoint', '')
        
        if 'marketing' in endpoint:
            data = [
                {
                    "campaign_id": f"camp_{i}",
                    "impressions": (i + 1) * 1000,
                    "clicks": (i + 1) * 50,
                    "conversions": (i + 1) * 5,
                    "spend": (i + 1) * 100,
                    "date": datetime.now() - timedelta(days=i)
                }
                for i in range(30)  # 30 dias de dados
            ]
        else:
            data = []
        
        return {"data": data, "count": len(data)}
    
    async def _transform_data(self, extraction_result: Dict, 
                            transformation_rules: List[Dict]) -> Dict:
        """Aplica transformações aos dados extraídos"""
        
        data = extraction_result["data"]
        
        if not data:
            return {"data": [], "count": 0}
        
        # Converte para DataFrame para facilitar transformações
        df = pd.DataFrame(data)
        
        # Aplica cada regra de transformação
        for rule in transformation_rules:
            rule_type = rule.get('type')
            
            if rule_type == 'rename_column':
                old_name = rule['old_name']
                new_name = rule['new_name']
                if old_name in df.columns:
                    df = df.rename(columns={old_name: new_name})
                    
            elif rule_type == 'calculate_column':
                column_name = rule['column_name']
                expression = rule['expression']
                # Avalia expressão simples (em produção, usar parser mais seguro)
                df[column_name] = eval(expression, {"df": df, "pd": pd})
                
            elif rule_type == 'filter_rows':
                condition = rule['condition']
                df = df.query(condition)
                
            elif rule_type == 'aggregate':
                group_by = rule['group_by']
                aggregations = rule['aggregations']
                df = df.groupby(group_by).agg(aggregations).reset_index()
                
            elif rule_type == 'join':
                # Implementar joins com outras tabelas
                pass
                
            elif rule_type == 'format_date':
                column_name = rule['column_name']
                date_format = rule.get('format', '%Y-%m-%d')
                if column_name in df.columns:
                    df[column_name] = pd.to_datetime(df[column_name]).dt.strftime(date_format)
        
        # Converte de volta para lista de dicionários
        transformed_data = df.to_dict('records')
        
        return {"data": transformed_data, "count": len(transformed_data)}
    
    async def _load_data(self, transformation_result: Dict, target_table: str) -> Dict:
        """Carrega dados transformados no data warehouse"""
        
        data = transformation_result["data"]
        
        if not data:
            return {"count": 0}
        
        # Em produção, carregaria no banco real
        # Aqui apenas simula o carregamento
        
        # Simula inserção em lotes
        batch_size = 1000
        total_inserted = 0
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            
            # Simula inserção do lote
            await asyncio.sleep(0.01)  # Simula tempo de inserção
            total_inserted += len(batch)
            
            print(f"Inserted batch {i//batch_size + 1}: {len(batch)} records into {target_table}")
        
        return {"count": total_inserted}
    
    async def schedule_job(self, job_id: str, cron_expression: str):
        """Agenda execução de um job ETL"""
        
        # Em produção, integraria com scheduler como Celery ou APScheduler
        print(f"Job {job_id} scheduled with cron: {cron_expression}")
    
    async def get_job_history(self, job_id: Optional[str] = None) -> List[Dict]:
        """Obtém histórico de execuções"""
        
        if job_id:
            return [log for log in self.job_history if log["job_id"] == job_id]
        else:
            return self.job_history

# Jobs ETL pré-configurados
async def setup_default_etl_jobs():
    """Configura jobs ETL padrão"""
    
    etl_engine = ETLEngine()
    
    # Job para carregar dados de vendas
    sales_job = ETLJobConfig(
        job_id="load_sales_data",
        name="Load Sales Data",
        source_type="database",
        source_config={
            "connection": "operational_db",
            "table": "transactions",
            "query": "SELECT * FROM transactions WHERE created_at > :last_update"
        },
        target_table="fact_sales",
        transformation_rules=[
            {
                "type": "calculate_column",
                "column_name": "profit_amount",
                "expression": "df['amount'] * 0.3"  # 30% de margem
            },
            {
                "type": "format_date",
                "column_name": "created_at",
                "format": "%Y-%m-%d"
            }
        ],
        schedule="0 */6 * * *",  # A cada 6 horas
        is_incremental=True
    )
    
    # Job para dados de marketing
    marketing_job = ETLJobConfig(
        job_id="load_marketing_data",
        name="Load Marketing Data",
        source_type="api",
        source_config={
            "endpoint": "https://api.marketing.com/campaigns",
            "auth_token": "token_123"
        },
        target_table="fact_marketing",
        transformation_rules=[
            {
                "type": "calculate_column",
                "column_name": "ctr",
                "expression": "df['clicks'] / df['impressions']"
            },
            {
                "type": "calculate_column",
                "column_name": "cpc",
                "expression": "df['spend'] / df['clicks']"
            }
        ],
        schedule="0 2 * * *",  # Diariamente às 2h
        is_incremental=True
    )
    
    await etl_engine.register_etl_job(sales_job)
    await etl_engine.register_etl_job(marketing_job)
    
    return etl_engine

# Singleton do ETL engine
etl_engine = None

async def get_etl_engine():
    global etl_engine
    if etl_engine is None:
        etl_engine = await setup_default_etl_jobs()
    return etl_engine
```

### 3. APIs do BI

```python
# app/bi/routes.py
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from ..auth.dependencies import get_current_user
from ..models.user import User
from .engine import bi_engine, ChartConfig
from .etl import get_etl_engine

router = APIRouter(prefix="/bi", tags=["business-intelligence"])

# Modelos para requests/responses
class QueryRequest(BaseModel):
    sql: str
    parameters: Optional[Dict[str, Any]] = None
    use_cache: bool = True
    cache_ttl: Optional[int] = None

class ChartRequest(BaseModel):
    data_query: QueryRequest
    chart_config: Dict[str, Any]

class DashboardWidget(BaseModel):
    widget_type: str
    title: str
    position_x: int
    position_y: int
    size_width: int = 4
    size_height: int = 3
    data_source: Dict[str, Any]
    visualization_config: Dict[str, Any]

class CreateDashboardRequest(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    widgets: List[DashboardWidget]
    is_public: bool = False

class ScheduleReportRequest(BaseModel):
    dashboard_id: str
    name: str
    schedule_cron: str
    report_format: str = "PDF"
    email_recipients: List[str]
    timezone: str = "UTC"

@router.post("/query")
async def execute_bi_query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user)
):
    """Executa uma consulta BI customizada"""
    
    try:
        result = await bi_engine.execute_query(
            sql=request.sql,
            parameters=request.parameters,
            use_cache=request.use_cache,
            cache_ttl=request.cache_ttl
        )
        
        return {
            "data": result.data,
            "columns": result.columns,
            "row_count": result.row_count,
            "execution_time_ms": result.execution_time_ms,
            "cache_hit": result.cache_hit,
            "metadata": result.metadata
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Query failed: {str(e)}")

@router.post("/chart")
async def generate_chart(
    request: ChartRequest,
    current_user: User = Depends(get_current_user)
):
    """Gera um gráfico a partir de dados e configuração"""
    
    try:
        # Executa query para obter dados
        query_result = await bi_engine.execute_query(
            sql=request.data_query.sql,
            parameters=request.data_query.parameters,
            use_cache=request.data_query.use_cache
        )
        
        # Converte configuração em ChartConfig
        config = ChartConfig(
            chart_type=request.chart_config["chart_type"],
            x_axis=request.chart_config["x_axis"],
            y_axis=request.chart_config["y_axis"],
            color_by=request.chart_config.get("color_by"),
            size_by=request.chart_config.get("size_by"),
            aggregation=request.chart_config.get("aggregation", "sum"),
            title=request.chart_config.get("title"),
            colors=request.chart_config.get("colors")
        )
        
        # Gera gráfico
        chart_data = await bi_engine.build_chart(query_result.data, config)
        
        return {
            "chart": chart_data,
            "query_info": {
                "execution_time_ms": query_result.execution_time_ms,
                "row_count": query_result.row_count,
                "cache_hit": query_result.cache_hit
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Chart generation failed: {str(e)}")

@router.get("/dashboards")
async def list_dashboards(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user)
):
    """Lista dashboards disponíveis para o usuário"""
    
    # Dashboards simulados
    dashboards = [
        {
            "id": "sales_overview",
            "name": "Sales Overview",
            "description": "Visão geral de vendas e performance",
            "category": "Sales",
            "is_public": True,
            "widget_count": 6,
            "last_accessed": "2024-01-01T10:00:00Z",
            "created_at": "2023-12-01T09:00:00Z"
        },
        {
            "id": "marketing_performance", 
            "name": "Marketing Performance",
            "description": "Métricas de campanhas e conversões",
            "category": "Marketing",
            "is_public": True,
            "widget_count": 8,
            "last_accessed": "2024-01-01T11:30:00Z",
            "created_at": "2023-12-15T14:00:00Z"
        },
        {
            "id": "customer_analytics",
            "name": "Customer Analytics", 
            "description": "Análise de comportamento e satisfação",
            "category": "Customer",
            "is_public": False,
            "widget_count": 5,
            "last_accessed": "2024-01-01T09:15:00Z",
            "created_at": "2024-01-01T08:00:00Z"
        }
    ]
    
    # Aplica filtros
    filtered_dashboards = []
    for dashboard in dashboards:
        if category and dashboard["category"].lower() != category.lower():
            continue
        if search and search.lower() not in dashboard["name"].lower():
            continue
        filtered_dashboards.append(dashboard)
    
    return {
        "dashboards": filtered_dashboards,
        "total": len(filtered_dashboards)
    }

@router.get("/dashboards/{dashboard_id}")
async def get_dashboard_data(
    dashboard_id: str,
    current_user: User = Depends(get_current_user)
):
    """Obtém dados completos de um dashboard"""
    
    try:
        dashboard_data = await bi_engine.generate_dashboard_data(dashboard_id)
        return dashboard_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load dashboard: {str(e)}")

@router.post("/dashboards")
async def create_dashboard(
    request: CreateDashboardRequest,
    current_user: User = Depends(get_current_user)
):
    """Cria um novo dashboard personalizado"""
    
    # TODO: Implementar criação real no banco
    
    dashboard_id = f"dashboard_{int(datetime.now().timestamp())}"
    
    return {
        "dashboard_id": dashboard_id,
        "name": request.name,
        "status": "created",
        "widget_count": len(request.widgets),
        "message": "Dashboard created successfully"
    }

@router.get("/kpis")
async def get_kpis_overview(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(get_current_user)
):
    """Obtém overview dos principais KPIs"""
    
    # KPIs simulados
    kpis = {
        "revenue": {
            "current": 285750.50,
            "previous": 248920.30,
            "change_percent": 14.8,
            "trend": "up"
        },
        "new_customers": {
            "current": 347,
            "previous": 312,
            "change_percent": 11.2,
            "trend": "up"
        },
        "conversion_rate": {
            "current": 3.8,
            "previous": 3.2,
            "change_percent": 18.7,
            "trend": "up"
        },
        "avg_order_value": {
            "current": 423.85,
            "previous": 398.20,
            "change_percent": 6.4,
            "trend": "up"
        },
        "customer_satisfaction": {
            "current": 4.6,
            "previous": 4.4,
            "change_percent": 4.5,
            "trend": "up"
        },
        "support_resolution_time": {
            "current": 4.2,
            "previous": 5.1,
            "change_percent": -17.6,
            "trend": "up"  # Menor tempo é melhor
        }
    }
    
    return {
        "period": period,
        "kpis": kpis,
        "generated_at": datetime.now().isoformat()
    }

@router.post("/reports/schedule")
async def schedule_report(
    request: ScheduleReportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Agenda geração automática de relatórios"""
    
    # TODO: Implementar agendamento real
    
    # Adiciona tarefa em background para configurar agendamento
    background_tasks.add_task(
        _setup_scheduled_report,
        request.dashboard_id,
        request.schedule_cron,
        request.email_recipients
    )
    
    return {
        "status": "scheduled",
        "dashboard_id": request.dashboard_id,
        "schedule": request.schedule_cron,
        "next_run": "2024-01-02T06:00:00Z",  # Simulado
        "recipients": len(request.email_recipients)
    }

@router.get("/reports/history")
async def get_reports_history(
    dashboard_id: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user)
):
    """Obtém histórico de relatórios gerados"""
    
    # Histórico simulado
    reports = [
        {
            "id": "report_1",
            "dashboard_id": "sales_overview",
            "dashboard_name": "Sales Overview",
            "generated_at": "2024-01-01T06:00:00Z",
            "format": "PDF",
            "status": "completed",
            "file_size_mb": 2.5,
            "recipients": ["admin@empresa.com", "vendas@empresa.com"]
        },
        {
            "id": "report_2",
            "dashboard_id": "marketing_performance",
            "dashboard_name": "Marketing Performance", 
            "generated_at": "2024-01-01T07:00:00Z",
            "format": "Excel",
            "status": "completed",
            "file_size_mb": 1.8,
            "recipients": ["marketing@empresa.com"]
        }
    ]
    
    # Filtro por dashboard se especificado
    if dashboard_id:
        reports = [r for r in reports if r["dashboard_id"] == dashboard_id]
    
    return {
        "reports": reports[:limit],
        "total": len(reports),
        "has_more": len(reports) > limit
    }

@router.get("/analytics/usage")
async def get_bi_usage_analytics(
    period: str = Query("30d"),
    current_user: User = Depends(get_current_user)
):
    """Obtém analytics de uso da plataforma BI"""
    
    # Analytics simulados
    analytics = {
        "period": period,
        "total_queries": 1250,
        "unique_users": 45,
        "dashboard_views": 890,
        "report_exports": 23,
        "avg_query_time_ms": 285,
        "cache_hit_rate": 0.72,
        
        "top_dashboards": [
            {"name": "Sales Overview", "views": 320},
            {"name": "Marketing Performance", "views": 280},
            {"name": "Customer Analytics", "views": 180}
        ],
        
        "query_volume_by_day": [
            {"date": "2024-01-01", "queries": 85},
            {"date": "2024-01-02", "queries": 92},
            {"date": "2024-01-03", "queries": 78},
            {"date": "2024-01-04", "queries": 95},
            {"date": "2024-01-05", "queries": 110}
        ],
        
        "performance_metrics": {
            "p50_response_time_ms": 150,
            "p95_response_time_ms": 450,
            "p99_response_time_ms": 850,
            "error_rate_percent": 0.8
        }
    }
    
    return analytics

@router.get("/etl/jobs")
async def list_etl_jobs(current_user: User = Depends(get_current_user)):
    """Lista jobs ETL configurados"""
    
    etl_engine = await get_etl_engine()
    
    jobs_info = []
    for job_id, config in etl_engine.active_jobs.items():
        jobs_info.append({
            "job_id": config.job_id,
            "name": config.name,
            "source_type": config.source_type,
            "target_table": config.target_table,
            "schedule": config.schedule,
            "is_incremental": config.is_incremental,
            "last_run": None,  # TODO: Implementar
            "status": "active"
        })
    
    return {"jobs": jobs_info}

@router.post("/etl/jobs/{job_id}/run")
async def run_etl_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Executa um job ETL manualmente"""
    
    etl_engine = await get_etl_engine()
    
    if job_id not in etl_engine.active_jobs:
        raise HTTPException(status_code=404, detail="ETL job not found")
    
    # Executa em background
    background_tasks.add_task(_run_etl_job_background, job_id)
    
    return {
        "job_id": job_id,
        "status": "started",
        "message": "ETL job started in background"
    }

# Funções auxiliares para background tasks
async def _setup_scheduled_report(dashboard_id: str, cron_schedule: str, recipients: List[str]):
    """Configura agendamento de relatório"""
    print(f"Setting up scheduled report for dashboard {dashboard_id}")
    print(f"Schedule: {cron_schedule}")
    print(f"Recipients: {recipients}")

async def _run_etl_job_background(job_id: str):
    """Executa job ETL em background"""
    etl_engine = await get_etl_engine()
    try:
        result = await etl_engine.execute_job(job_id)
        print(f"ETL job {job_id} completed successfully")
        print(f"Result: {result}")
    except Exception as e:
        print(f"ETL job {job_id} failed: {str(e)}")
```

### 4. Sistema de Relatórios

```python
# app/bi/reports.py
import asyncio
from typing import Dict, List, Optional, BinaryIO
from datetime import datetime
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import openpyxl
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.chart.axis import DateAxis

class ReportGenerator:
    """Gerador de relatórios em múltiplos formatos"""
    
    def __init__(self):
        self.template_path = "app/bi/templates/"
        
    async def generate_dashboard_report(self, dashboard_id: str, 
                                      format: str = "PDF",
                                      filters: Optional[Dict] = None) -> BytesIO:
        """Gera relatório completo de um dashboard"""
        
        # Obtém dados do dashboard
        from .engine import bi_engine
        dashboard_data = await bi_engine.generate_dashboard_data(dashboard_id)
        
        if format.upper() == "PDF":
            return await self._generate_pdf_report(dashboard_data, filters)
        elif format.upper() == "EXCEL":
            return await self._generate_excel_report(dashboard_data, filters)
        elif format.upper() == "CSV":
            return await self._generate_csv_report(dashboard_data, filters)
        else:
            raise ValueError(f"Unsupported report format: {format}")
    
    async def _generate_pdf_report(self, dashboard_data: Dict, 
                                 filters: Optional[Dict] = None) -> BytesIO:
        """Gera relatório PDF com gráficos e tabelas"""
        
        buffer = BytesIO()
        
        with PdfPages(buffer) as pdf:
            # Página de título
            fig, ax = plt.subplots(figsize=(8.5, 11))
            ax.text(0.5, 0.8, "Relatório de Business Intelligence", 
                   ha='center', va='center', fontsize=20, weight='bold')
            ax.text(0.5, 0.7, f"Dashboard: {dashboard_data.get('dashboard_id', 'N/A')}", 
                   ha='center', va='center', fontsize=14)
            ax.text(0.5, 0.6, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                   ha='center', va='center', fontsize=12)
            ax.axis('off')
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            
            # Páginas de widgets
            for widget in dashboard_data.get('widgets', []):
                fig, ax = plt.subplots(figsize=(8.5, 11))
                
                widget_type = widget.get('type')
                widget_title = widget.get('title', 'Widget')
                widget_data = widget.get('data', {})
                
                if widget_type == 'kpi':
                    await self._add_kpi_to_pdf(ax, widget_title, widget_data)
                elif widget_type == 'chart':
                    await self._add_chart_to_pdf(ax, widget_title, widget_data)
                elif widget_type == 'table':
                    await self._add_table_to_pdf(ax, widget_title, widget_data)
                
                pdf.savefig(fig, bbox_inches='tight')
                plt.close(fig)
        
        buffer.seek(0)
        return buffer
    
    async def _add_kpi_to_pdf(self, ax, title: str, kpi_data: Dict):
        """Adiciona KPI ao PDF"""
        ax.text(0.5, 0.8, title, ha='center', va='center', 
               fontsize=16, weight='bold')
        
        value = kpi_data.get('value', 0)
        change = kpi_data.get('change_percent', 0)
        trend = kpi_data.get('trend', 'neutral')
        
        # Formata valor baseado no tipo
        format_type = kpi_data.get('format', 'number')
        if format_type == 'currency':
            formatted_value = f"R$ {value:,.2f}"
        elif format_type == 'percentage':
            formatted_value = f"{value:.1f}%"
        else:
            formatted_value = f"{value:,.0f}"
        
        ax.text(0.5, 0.6, formatted_value, ha='center', va='center',
               fontsize=24, weight='bold', color='green' if trend == 'up' else 'red')
        
        change_text = f"{'↗' if change > 0 else '↘'} {abs(change):.1f}%"
        ax.text(0.5, 0.4, change_text, ha='center', va='center',
               fontsize=14, color='green' if change > 0 else 'red')
        
        ax.axis('off')
    
    async def _add_chart_to_pdf(self, ax, title: str, chart_data: Dict):
        """Adiciona gráfico ao PDF"""
        ax.set_title(title, fontsize=14, weight='bold', pad=20)
        
        # Simula dados do gráfico
        x_data = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        y_data = [100, 120, 140, 110, 160, 180]
        
        ax.bar(x_data, y_data, color='steelblue', alpha=0.7)
        ax.set_xlabel('Período')
        ax.set_ylabel('Valor')
        ax.grid(True, alpha=0.3)
    
    async def _generate_excel_report(self, dashboard_data: Dict,
                                   filters: Optional[Dict] = None) -> BytesIO:
        """Gera relatório Excel com dados e gráficos"""
        
        buffer = BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Aba de resumo
            summary_data = {
                'Dashboard': [dashboard_data.get('dashboard_id', 'N/A')],
                'Gerado em': [datetime.now().strftime('%d/%m/%Y %H:%M')],
                'Widgets': [len(dashboard_data.get('widgets', []))]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Resumo', index=False)
            
            # Aba para cada widget com dados
            for i, widget in enumerate(dashboard_data.get('widgets', [])):
                widget_type = widget.get('type')
                widget_title = widget.get('title', f'Widget {i+1}')
                widget_data = widget.get('data', {})
                
                if widget_type in ['chart', 'table']:
                    # Cria dados simulados para o widget
                    data = {
                        'Período': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                        'Vendas': [100000, 120000, 140000, 110000, 160000, 180000],
                        'Lucro': [30000, 36000, 42000, 33000, 48000, 54000]
                    }
                    
                    df = pd.DataFrame(data)
                    sheet_name = widget_title[:31]  # Excel limita a 31 chars
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    # Adiciona gráfico na aba
                    workbook = writer.book
                    worksheet = writer.sheets[sheet_name]
                    
                    chart = BarChart()
                    chart.title = widget_title
                    
                    # Define dados do gráfico
                    data_ref = Reference(worksheet, min_col=2, min_row=1, 
                                       max_col=3, max_row=len(df) + 1)
                    cats = Reference(worksheet, min_col=1, min_row=2, 
                                   max_row=len(df) + 1)
                    
                    chart.add_data(data_ref, titles_from_data=True)
                    chart.set_categories(cats)
                    
                    worksheet.add_chart(chart, "E2")
        
        buffer.seek(0)
        return buffer
    
    async def _generate_csv_report(self, dashboard_data: Dict,
                                 filters: Optional[Dict] = None) -> BytesIO:
        """Gera relatório CSV com dados agregados"""
        
        # Compila dados de todos os widgets
        all_data = []
        
        for widget in dashboard_data.get('widgets', []):
            widget_type = widget.get('type')
            widget_title = widget.get('title', 'Widget')
            
            if widget_type in ['chart', 'table']:
                # Dados simulados
                widget_rows = [
                    {'Widget': widget_title, 'Período': 'Jan', 'Valor': 100000},
                    {'Widget': widget_title, 'Período': 'Feb', 'Valor': 120000},
                    {'Widget': widget_title, 'Período': 'Mar', 'Valor': 140000},
                ]
                all_data.extend(widget_rows)
        
        df = pd.DataFrame(all_data)
        
        buffer = BytesIO()
        df.to_csv(buffer, index=False, encoding='utf-8')
        buffer.seek(0)
        
        return buffer

# Gerador de relatórios singleton
report_generator = ReportGenerator()
```

## 🔧 Implementação de Fases

### Fase 1: Data Warehouse e ETL (Semanas 1-3)
- [ ] Modelagem dimensional completa (fatos e dimensões)
- [ ] Pipeline ETL com jobs configuráveis
- [ ] Extração de dados operacionais
- [ ] Transformações e validações de dados
- [ ] Carregamento incremental otimizado
- [ ] Agendamento automático de jobs

### Fase 2: BI Engine e Analytics (Semanas 4-6)
- [ ] Engine principal de consultas BI
- [ ] Sistema de cache inteligente
- [ ] Processamento de queries OLAP
- [ ] Geração de gráficos dinâmicos
- [ ] Cálculos de KPIs e métricas
- [ ] APIs REST para BI

### Fase 3: Dashboard Builder (Semanas 7-9)
- [ ] Interface drag-and-drop para dashboards
- [ ] Biblioteca de widgets pré-configurados
- [ ] Sistema de filtros e drill-down
- [ ] Compartilhamento e permissões
- [ ] Responsividade mobile
- [ ] Temas e personalização

### Fase 4: Relatórios e Exportação (Semanas 10-11)
- [ ] Gerador de relatórios PDF/Excel/CSV
- [ ] Agendamento automático de relatórios
- [ ] Templates customizáveis
- [ ] Distribuição por email
- [ ] Assinatura digital de relatórios
- [ ] Versionamento de relatórios

### Fase 5: ML e Análise Avançada (Semanas 12-13)
- [ ] Modelos preditivos integrados
- [ ] Análise de tendências automática
- [ ] Detecção de anomalias
- [ ] Segmentação automática de clientes
- [ ] Recomendações de ações
- [ ] Forecasting de métricas

## 📊 Métricas e KPIs

### Performance do Sistema
```python
# app/bi/monitoring.py
from typing import Dict, List
import time
from datetime import datetime, timedelta
from collections import defaultdict, deque

class BIPerformanceMonitor:
    """Monitor de performance da plataforma BI"""
    
    def __init__(self):
        self.query_metrics = deque(maxlen=10000)
        self.dashboard_metrics = deque(maxlen=5000)
        self.cache_metrics = {"hits": 0, "misses": 0}
        
    async def track_query_performance(self, query: str, execution_time_ms: int,
                                    row_count: int, cache_hit: bool):
        """Rastreia performance de queries"""
        
        self.query_metrics.append({
            "timestamp": time.time(),
            "query_hash": hash(query) % 1000000,
            "execution_time_ms": execution_time_ms,
            "row_count": row_count,
            "cache_hit": cache_hit
        })
        
        if cache_hit:
            self.cache_metrics["hits"] += 1
        else:
            self.cache_metrics["misses"] += 1
    
    async def track_dashboard_load(self, dashboard_id: str, load_time_ms: int,
                                 widget_count: int, user_id: str):
        """Rastreia carregamento de dashboards"""
        
        self.dashboard_metrics.append({
            "timestamp": time.time(),
            "dashboard_id": dashboard_id,
            "load_time_ms": load_time_ms,
            "widget_count": widget_count,
            "user_id": user_id
        })
    
    async def get_performance_summary(self) -> Dict:
        """Obtém resumo de performance"""
        
        now = time.time()
        last_hour = now - 3600
        
        # Métricas de queries da última hora
        recent_queries = [
            q for q in self.query_metrics 
            if q["timestamp"] > last_hour
        ]
        
        if recent_queries:
            avg_query_time = sum(q["execution_time_ms"] for q in recent_queries) / len(recent_queries)
            p95_query_time = sorted([q["execution_time_ms"] for q in recent_queries])[int(len(recent_queries) * 0.95)]
            total_cache_hits = sum(1 for q in recent_queries if q["cache_hit"])
            cache_hit_rate = total_cache_hits / len(recent_queries)
        else:
            avg_query_time = 0
            p95_query_time = 0
            cache_hit_rate = 0
        
        # Métricas de dashboards
        recent_dashboards = [
            d for d in self.dashboard_metrics
            if d["timestamp"] > last_hour
        ]
        
        if recent_dashboards:
            avg_dashboard_load = sum(d["load_time_ms"] for d in recent_dashboards) / len(recent_dashboards)
            unique_users = len(set(d["user_id"] for d in recent_dashboards))
        else:
            avg_dashboard_load = 0
            unique_users = 0
        
        return {
            "query_performance": {
                "total_queries_hour": len(recent_queries),
                "avg_execution_time_ms": round(avg_query_time, 2),
                "p95_execution_time_ms": p95_query_time,
                "cache_hit_rate": round(cache_hit_rate, 3)
            },
            "dashboard_performance": {
                "total_loads_hour": len(recent_dashboards),
                "avg_load_time_ms": round(avg_dashboard_load, 2),
                "unique_users_hour": unique_users
            },
            "overall_cache": {
                "total_hits": self.cache_metrics["hits"],
                "total_misses": self.cache_metrics["misses"],
                "hit_rate": round(self.cache_metrics["hits"] / 
                               (self.cache_metrics["hits"] + self.cache_metrics["misses"]), 3)
                               if (self.cache_metrics["hits"] + self.cache_metrics["misses"]) > 0 else 0
            }
        }

# Monitor singleton
bi_performance_monitor = BIPerformanceMonitor()
```

### KPIs de Negócio
- **Adoção de usuários**: % de usuários ativos usando BI
- **Engajamento**: Tempo médio gasto em dashboards
- **Self-service**: % de relatórios criados pelos próprios usuários
- **Data-driven decisions**: Número de decisões baseadas em insights do BI
- **ROI**: Valor gerado por decisões baseadas em dados

## ✅ Checklist de Entrega

### Data Layer
- [ ] Data warehouse modelado e implementado
- [ ] ETL pipelines funcionais e agendados
- [ ] Validação e qualidade de dados
- [ ] Backup e recovery procedures
- [ ] Performance optimization (índices, partitions)

### BI Engine
- [ ] Query engine otimizado
- [ ] Sistema de cache distribuído
- [ ] Suporte a queries OLAP complexas
- [ ] APIs REST completas e documentadas
- [ ] Sistema de permissões granular

### Frontend e UX
- [ ] Dashboard builder drag-and-drop
- [ ] Biblioteca completa de widgets
- [ ] Interface responsiva (mobile-first)
- [ ] Temas e personalização
- [ ] Exportação em múltiplos formatos

### Relatórios
- [ ] Geração de relatórios automatizada
- [ ] Agendamento flexível
- [ ] Templates customizáveis
- [ ] Distribuição por email/webhook
- [ ] Versionamento e auditoria

### Monitoramento
- [ ] Métricas de performance em tempo real
- [ ] Alertas de anomalias
- [ ] Logs estruturados
- [ ] Dashboard de saúde do sistema
- [ ] SLA monitoring

## 📈 Critérios de Sucesso

### Métricas Técnicas
- **Performance de queries**: 95% das queries < 2s
- **Disponibilidade**: > 99.5% uptime
- **Throughput**: > 100 queries concorrentes
- **Cache hit rate**: > 70%
- **Precisão dos dados**: > 99.9%

### Métricas de Produto
- **Tempo de criação de dashboard**: < 15 minutos
- **Self-service reports**: 80% dos relatórios criados pelos usuários
- **Mobile usage**: 30% dos acessos via mobile
- **Data freshness**: < 1 hora de latência para dados críticos

### KPIs de Negócio
- **Adoção**: 70% dos usuários ativos usando BI
- **Engagement**: 45+ minutos médios por sessão
- **Decision velocity**: 50% de redução no tempo de decisão
- **Data literacy**: 90% dos usuários capazes de criar reports básicos
- **ROI**: 300% de retorno em decisões baseadas em dados

---

*Esta documentação define uma plataforma completa de Business Intelligence que transforma dados brutos em insights acionáveis, permitindo decisões estratégicas baseadas em dados precisos e atualizados.*
EOF"