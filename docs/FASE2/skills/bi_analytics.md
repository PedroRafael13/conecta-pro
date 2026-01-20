# SKILL: BI E ANALYTICS
## ERP CONECTA MAIS - FASE 2

**Modulo:** Business Intelligence
**Sprints:** 30 (Dashboards)
**Prioridade:** ALTA

---

## CONTEXTO DO MODULO

Inteligencia de negocios e analiticos:
- Dashboards Executivos
- KPIs em Tempo Real
- Relatorios Automatizados
- Alertas Inteligentes
- Previsoes com IA

---

## ESTRUTURA DO MODULO

```
modules/bi/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── dashboard.py          # Dashboards
│   ├── widget.py             # Widgets
│   ├── report.py             # Relatorios
│   ├── report_schedule.py    # Agendamentos
│   ├── alert.py              # Alertas
│   └── kpi.py                # Definicoes de KPI
├── schemas/
│   ├── __init__.py
│   ├── dashboard.py
│   ├── report.py
│   └── analytics.py
├── repositories/
│   ├── __init__.py
│   ├── dashboard_repository.py
│   └── report_repository.py
├── services/
│   ├── __init__.py
│   ├── analytics_service.py   # Calculos analiticos
│   ├── kpi_calculator.py      # Calculador de KPIs
│   ├── report_generator.py    # Gerador de relatorios
│   ├── alert_service.py       # Servico de alertas
│   └── forecast_service.py    # Previsoes IA
└── controllers/
    ├── __init__.py
    ├── dashboard_controller.py
    ├── report_controller.py
    └── analytics_controller.py
```

---

## ENTIDADES PRINCIPAIS

### Dashboard

```python
class Dashboard(Base):
    """
    Dashboard personalizavel.

    Representa um painel com widgets
    configurados pelo usuario.
    """

    __tablename__ = "dashboards"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Identificacao
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    slug = Column(String(50), unique=True, nullable=False)

    # Tipo
    dashboard_type = Column(Enum(DashboardType), nullable=False)
    # CEO, FINANCIAL, HR, COMMERCIAL, OPERATIONAL, CUSTOM

    # Acesso
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    shared_with = Column(ARRAY(UUID), default=[])

    # Layout (JSON)
    layout = Column(JSONB, default={})
    # {
    #   "columns": 12,
    #   "rows": [],
    #   "widgets": [{"id": "xxx", "x": 0, "y": 0, "w": 6, "h": 4}]
    # }

    # Configuracoes
    refresh_interval = Column(Integer, default=300)  # segundos
    theme = Column(String(20), default="light")

    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    widgets = relationship("Widget", back_populates="dashboard")

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<Dashboard(name='{self.name}', type={self.dashboard_type})>"
```

### Widget

```python
class Widget(Base):
    """
    Widget de dashboard.

    Componente visual que exibe dados
    em diferentes formatos.
    """

    __tablename__ = "widgets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    dashboard_id = Column(UUID(as_uuid=True), ForeignKey("dashboards.id"), nullable=False)

    # Identificacao
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Tipo de visualizacao
    widget_type = Column(Enum(WidgetType), nullable=False)
    # NUMBER, CHART_LINE, CHART_BAR, CHART_PIE, CHART_DONUT,
    # TABLE, LIST, MAP, GAUGE, PROGRESS, TIMELINE

    # Fonte de dados
    data_source = Column(Enum(DataSource), nullable=False)
    # QUERY, API, KPI, CUSTOM
    query = Column(Text, nullable=True)
    api_endpoint = Column(String(200), nullable=True)
    kpi_id = Column(UUID(as_uuid=True), ForeignKey("kpis.id"), nullable=True)

    # Configuracoes visuais (JSON)
    config = Column(JSONB, default={})
    # {
    #   "title": "Faturamento",
    #   "colors": ["#3B82F6", "#10B981"],
    #   "format": "currency",
    #   "comparison": "previous_month"
    # }

    # Posicao no grid
    position_x = Column(Integer, default=0)
    position_y = Column(Integer, default=0)
    width = Column(Integer, default=4)
    height = Column(Integer, default=3)

    # Cache
    cache_ttl = Column(Integer, default=60)  # segundos
    last_cached = Column(DateTime, nullable=True)
    cached_data = Column(JSONB, nullable=True)

    # Relationships
    dashboard = relationship("Dashboard", back_populates="widgets")

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<Widget(name='{self.name}', type={self.widget_type})>"
```

### KPI

```python
class KPI(Base):
    """
    Definicao de KPI.

    Indicador chave de performance
    com formula e metas.
    """

    __tablename__ = "kpis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Identificacao
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Categoria
    category = Column(Enum(KPICategory), nullable=False)
    # FINANCIAL, COMMERCIAL, HR, OPERATIONAL, CUSTOMER

    # Formula
    formula = Column(Text, nullable=False)
    # Ex: "SUM(receivables.paid_value) / SUM(receivables.original_value) * 100"

    # Formato
    format_type = Column(Enum(FormatType), default=FormatType.NUMBER)
    # NUMBER, CURRENCY, PERCENT, DURATION
    decimal_places = Column(Integer, default=2)
    prefix = Column(String(10), nullable=True)
    suffix = Column(String(10), nullable=True)

    # Metas
    target_value = Column(Numeric(15, 2), nullable=True)
    target_type = Column(Enum(TargetType), default=TargetType.ABOVE)
    # ABOVE, BELOW, BETWEEN, EXACT

    # Thresholds para cores
    threshold_good = Column(Numeric(15, 2), nullable=True)
    threshold_warning = Column(Numeric(15, 2), nullable=True)
    threshold_critical = Column(Numeric(15, 2), nullable=True)

    # Frequencia de atualizacao
    update_frequency = Column(Enum(Frequency), default=Frequency.DAILY)
    # REALTIME, HOURLY, DAILY, WEEKLY, MONTHLY

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<KPI(code='{self.code}', name='{self.name}')>"
```

### Report

```python
class Report(Base):
    """
    Relatorio configuravel.

    Definicao de relatorio que pode
    ser gerado sob demanda ou agendado.
    """

    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    # Identificacao
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Tipo
    report_type = Column(Enum(ReportType), nullable=False)
    # FINANCIAL, HR, COMMERCIAL, OPERATIONAL, COMPLIANCE, CUSTOM

    # Formato de saida
    output_formats = Column(ARRAY(String), default=["PDF", "EXCEL"])

    # Query/Template
    query_template = Column(Text, nullable=False)
    template_file = Column(String(200), nullable=True)

    # Parametros (JSON)
    parameters = Column(JSONB, default=[])
    # [
    #   {"name": "start_date", "type": "date", "required": true},
    #   {"name": "client_id", "type": "uuid", "required": false}
    # ]

    # Permissoes
    allowed_roles = Column(ARRAY(String), default=["admin"])

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    schedules = relationship("ReportSchedule", back_populates="report")

    def __repr__(self) -> str:
        """Representacao string."""
        return f"<Report(code='{self.code}', name='{self.name}')>"
```

---

## SERVICES

### KPICalculator

```python
# modules/bi/services/kpi_calculator.py
"""Calculador de KPIs."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy.orm import Session

from core.logging import logger


@dataclass
class KPIValue:
    """Valor calculado de KPI."""
    kpi_code: str
    value: Decimal
    formatted_value: str
    target: Optional[Decimal]
    achievement: Optional[Decimal]  # % do target
    status: str  # good, warning, critical
    trend: str  # up, down, stable
    previous_value: Optional[Decimal]
    change_percent: Optional[Decimal]
    calculated_at: datetime


class KPICalculator:
    """
    Calculador de KPIs.

    Executa formulas e retorna valores
    formatados com status e tendencia.
    """

    def __init__(self, db: Session) -> None:
        """Inicializa calculador."""
        self.db = db

    def calculate(
        self,
        kpi_code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> KPIValue:
        """
        Calcula valor de um KPI.

        Args:
            kpi_code: Codigo do KPI
            start_date: Data inicial (opcional)
            end_date: Data final (opcional)

        Returns:
            Valor calculado do KPI
        """
        kpi = self._get_kpi(kpi_code)
        if not kpi:
            raise ValueError(f"KPI {kpi_code} nao encontrado")

        # Periodo padrao: mes atual
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date.replace(day=1)

        # Calcular valor atual
        current_value = self._execute_formula(kpi.formula, start_date, end_date)

        # Calcular valor anterior (mesmo periodo do mes anterior)
        prev_start = self._previous_period_start(start_date)
        prev_end = self._previous_period_end(start_date, end_date)
        previous_value = self._execute_formula(kpi.formula, prev_start, prev_end)

        # Calcular mudanca
        change_percent = self._calculate_change(current_value, previous_value)

        # Determinar status
        status = self._determine_status(kpi, current_value)

        # Determinar tendencia
        trend = self._determine_trend(current_value, previous_value)

        # Calcular achievement
        achievement = None
        if kpi.target_value:
            achievement = (current_value / kpi.target_value * 100).quantize(
                Decimal("0.01")
            )

        # Formatar valor
        formatted = self._format_value(kpi, current_value)

        logger.debug(
            f"KPI {kpi_code} calculado",
            extra={"value": str(current_value), "status": status}
        )

        return KPIValue(
            kpi_code=kpi_code,
            value=current_value,
            formatted_value=formatted,
            target=kpi.target_value,
            achievement=achievement,
            status=status,
            trend=trend,
            previous_value=previous_value,
            change_percent=change_percent,
            calculated_at=datetime.now()
        )

    def calculate_all(
        self,
        category: Optional[str] = None
    ) -> list[KPIValue]:
        """Calcula todos os KPIs de uma categoria."""
        kpis = self._get_kpis_by_category(category)
        return [self.calculate(kpi.code) for kpi in kpis]

    def _get_kpi(self, code: str) -> Any:
        """Busca definicao do KPI."""
        # Implementar busca no banco
        pass

    def _get_kpis_by_category(self, category: Optional[str]) -> list:
        """Lista KPIs por categoria."""
        pass

    def _execute_formula(
        self,
        formula: str,
        start_date: date,
        end_date: date
    ) -> Decimal:
        """Executa formula SQL."""
        # Substituir placeholders
        query = formula.replace("{start_date}", f"'{start_date}'")
        query = query.replace("{end_date}", f"'{end_date}'")

        # Executar query
        result = self.db.execute(query).scalar()

        return Decimal(str(result or 0))

    def _previous_period_start(self, current_start: date) -> date:
        """Calcula inicio do periodo anterior."""
        # Mes anterior
        if current_start.month == 1:
            return date(current_start.year - 1, 12, 1)
        return date(current_start.year, current_start.month - 1, 1)

    def _previous_period_end(self, current_start: date, current_end: date) -> date:
        """Calcula fim do periodo anterior."""
        days = (current_end - current_start).days
        prev_start = self._previous_period_start(current_start)
        return prev_start + timedelta(days=days)

    def _calculate_change(
        self,
        current: Decimal,
        previous: Optional[Decimal]
    ) -> Optional[Decimal]:
        """Calcula percentual de mudanca."""
        if not previous or previous == 0:
            return None
        change = ((current - previous) / previous * 100)
        return change.quantize(Decimal("0.01"))

    def _determine_status(self, kpi: Any, value: Decimal) -> str:
        """Determina status (cor) do KPI."""
        if kpi.threshold_critical and value <= kpi.threshold_critical:
            return "critical"
        if kpi.threshold_warning and value <= kpi.threshold_warning:
            return "warning"
        if kpi.threshold_good and value >= kpi.threshold_good:
            return "good"
        return "neutral"

    def _determine_trend(
        self,
        current: Decimal,
        previous: Optional[Decimal]
    ) -> str:
        """Determina tendencia."""
        if not previous:
            return "stable"
        diff = current - previous
        threshold = previous * Decimal("0.05")  # 5%

        if diff > threshold:
            return "up"
        elif diff < -threshold:
            return "down"
        return "stable"

    def _format_value(self, kpi: Any, value: Decimal) -> str:
        """Formata valor para exibicao."""
        # Arredondar
        rounded = value.quantize(Decimal(f"0.{'0' * kpi.decimal_places}"))

        # Aplicar formato
        if kpi.format_type == "CURRENCY":
            formatted = f"R$ {rounded:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        elif kpi.format_type == "PERCENT":
            formatted = f"{rounded}%"
        else:
            formatted = str(rounded)

        # Adicionar prefixo/sufixo
        if kpi.prefix:
            formatted = f"{kpi.prefix}{formatted}"
        if kpi.suffix:
            formatted = f"{formatted}{kpi.suffix}"

        return formatted
```

### AnalyticsService

```python
# modules/bi/services/analytics_service.py
"""Servico de Analytics."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from core.logging import logger


@dataclass
class TrendData:
    """Dados de tendencia."""
    labels: list[str]
    values: list[Decimal]
    trend_line: list[Decimal]


@dataclass
class ComparisonData:
    """Dados de comparacao."""
    current_period: dict
    previous_period: dict
    change: dict


class AnalyticsService:
    """
    Servico de analiticos.

    Fornece dados agregados e tendencias
    para visualizacoes.
    """

    def __init__(self, db: Session) -> None:
        """Inicializa servico."""
        self.db = db

    def get_revenue_trend(
        self,
        months: int = 12
    ) -> TrendData:
        """
        Obtem tendencia de faturamento.

        Args:
            months: Quantidade de meses

        Returns:
            Dados de tendencia
        """
        # Buscar faturamento por mes
        query = """
            SELECT
                TO_CHAR(received_date, 'YYYY-MM') as month,
                SUM(received_value) as total
            FROM receivables
            WHERE received_date >= CURRENT_DATE - INTERVAL '{months} months'
            AND status = 'RECEIVED'
            GROUP BY TO_CHAR(received_date, 'YYYY-MM')
            ORDER BY month
        """.format(months=months)

        results = self.db.execute(query).fetchall()

        labels = [r[0] for r in results]
        values = [Decimal(str(r[1])) for r in results]

        # Calcular linha de tendencia (media movel)
        trend_line = self._calculate_moving_average(values, window=3)

        return TrendData(
            labels=labels,
            values=values,
            trend_line=trend_line
        )

    def get_sales_funnel(self) -> dict:
        """
        Obtem dados do funil de vendas.

        Returns:
            Dados do funil por estagio
        """
        query = """
            SELECT
                status,
                COUNT(*) as count,
                SUM(estimated_value) as value
            FROM opportunities
            WHERE created_at >= CURRENT_DATE - INTERVAL '90 days'
            GROUP BY status
            ORDER BY
                CASE status
                    WHEN 'NEW' THEN 1
                    WHEN 'QUALIFIED' THEN 2
                    WHEN 'PROPOSAL' THEN 3
                    WHEN 'NEGOTIATION' THEN 4
                    WHEN 'WON' THEN 5
                    WHEN 'LOST' THEN 6
                END
        """

        results = self.db.execute(query).fetchall()

        return {
            "stages": [
                {
                    "name": r[0],
                    "count": r[1],
                    "value": Decimal(str(r[2] or 0))
                }
                for r in results
            ]
        }

    def get_top_clients(self, limit: int = 10) -> list[dict]:
        """
        Obtem top clientes por faturamento.

        Args:
            limit: Quantidade de clientes

        Returns:
            Lista de top clientes
        """
        query = """
            SELECT
                c.id,
                c.name,
                SUM(r.received_value) as total,
                COUNT(r.id) as invoices
            FROM companies c
            JOIN receivables r ON r.client_id = c.id
            WHERE r.status = 'RECEIVED'
            AND r.received_date >= CURRENT_DATE - INTERVAL '12 months'
            GROUP BY c.id, c.name
            ORDER BY total DESC
            LIMIT {limit}
        """.format(limit=limit)

        results = self.db.execute(query).fetchall()

        return [
            {
                "id": str(r[0]),
                "name": r[1],
                "total": Decimal(str(r[2])),
                "invoices": r[3]
            }
            for r in results
        ]

    def get_period_comparison(
        self,
        metric: str,
        current_start: date,
        current_end: date
    ) -> ComparisonData:
        """
        Compara periodos.

        Args:
            metric: Metrica a comparar
            current_start: Inicio periodo atual
            current_end: Fim periodo atual

        Returns:
            Dados de comparacao
        """
        # Calcular periodo anterior (mesmo tamanho)
        days = (current_end - current_start).days
        prev_end = current_start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=days)

        current = self._get_metric_value(metric, current_start, current_end)
        previous = self._get_metric_value(metric, prev_start, prev_end)

        change = {}
        for key in current:
            if previous.get(key) and previous[key] != 0:
                change[key] = ((current[key] - previous[key]) / previous[key] * 100)
            else:
                change[key] = None

        return ComparisonData(
            current_period=current,
            previous_period=previous,
            change=change
        )

    def _calculate_moving_average(
        self,
        values: list[Decimal],
        window: int
    ) -> list[Decimal]:
        """Calcula media movel."""
        if len(values) < window:
            return values

        result = []
        for i in range(len(values)):
            if i < window - 1:
                result.append(values[i])
            else:
                avg = sum(values[i - window + 1:i + 1]) / window
                result.append(avg.quantize(Decimal("0.01")))

        return result

    def _get_metric_value(
        self,
        metric: str,
        start: date,
        end: date
    ) -> dict:
        """Obtem valor de metrica."""
        # Implementar queries por metrica
        return {}
```

### ReportGenerator

```python
# modules/bi/services/report_generator.py
"""Gerador de Relatorios."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
import io

from sqlalchemy.orm import Session

from core.logging import logger


@dataclass
class GeneratedReport:
    """Relatorio gerado."""
    report_code: str
    format: str
    filename: str
    content: bytes
    generated_at: datetime
    parameters: dict


class ReportGenerator:
    """
    Gerador de relatorios.

    Gera relatorios em diferentes formatos
    baseado em templates e queries.
    """

    def __init__(self, db: Session) -> None:
        """Inicializa gerador."""
        self.db = db

    def generate(
        self,
        report_code: str,
        output_format: str = "PDF",
        parameters: Optional[dict] = None
    ) -> GeneratedReport:
        """
        Gera relatorio.

        Args:
            report_code: Codigo do relatorio
            output_format: Formato de saida
            parameters: Parametros do relatorio

        Returns:
            Relatorio gerado
        """
        report = self._get_report(report_code)
        if not report:
            raise ValueError(f"Relatorio {report_code} nao encontrado")

        # Validar parametros
        params = self._validate_parameters(report, parameters or {})

        # Executar query
        data = self._execute_query(report.query_template, params)

        # Gerar saida
        if output_format == "PDF":
            content = self._generate_pdf(report, data)
        elif output_format == "EXCEL":
            content = self._generate_excel(report, data)
        elif output_format == "CSV":
            content = self._generate_csv(report, data)
        else:
            raise ValueError(f"Formato {output_format} nao suportado")

        # Gerar nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_code}_{timestamp}.{output_format.lower()}"

        logger.info(
            "Relatorio gerado",
            extra={
                "report_code": report_code,
                "format": output_format,
                "rows": len(data)
            }
        )

        return GeneratedReport(
            report_code=report_code,
            format=output_format,
            filename=filename,
            content=content,
            generated_at=datetime.now(),
            parameters=params
        )

    def _get_report(self, code: str) -> Any:
        """Busca definicao do relatorio."""
        pass

    def _validate_parameters(
        self,
        report: Any,
        params: dict
    ) -> dict:
        """Valida parametros."""
        validated = {}

        for param_def in report.parameters:
            name = param_def["name"]
            required = param_def.get("required", False)

            if name in params:
                validated[name] = params[name]
            elif required:
                raise ValueError(f"Parametro obrigatorio: {name}")

        return validated

    def _execute_query(self, query: str, params: dict) -> list[dict]:
        """Executa query do relatorio."""
        # Substituir parametros
        for key, value in params.items():
            query = query.replace(f"{{{key}}}", str(value))

        result = self.db.execute(query).fetchall()

        # Converter para dict
        return [dict(row) for row in result]

    def _generate_pdf(self, report: Any, data: list[dict]) -> bytes:
        """Gera PDF."""
        # Usar reportlab ou weasyprint
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)

        # Criar tabela
        if data:
            headers = list(data[0].keys())
            table_data = [headers]
            for row in data:
                table_data.append([str(row.get(h, "")) for h in headers])

            table = Table(table_data)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))

            doc.build([table])

        return buffer.getvalue()

    def _generate_excel(self, report: Any, data: list[dict]) -> bytes:
        """Gera Excel."""
        import pandas as pd

        df = pd.DataFrame(data)
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        return buffer.getvalue()

    def _generate_csv(self, report: Any, data: list[dict]) -> bytes:
        """Gera CSV."""
        import csv

        buffer = io.StringIO()
        if data:
            writer = csv.DictWriter(buffer, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

        return buffer.getvalue().encode("utf-8")
```

---

## DASHBOARDS PRE-DEFINIDOS

### Dashboard CEO

```json
{
  "name": "Dashboard CEO",
  "slug": "ceo",
  "type": "CEO",
  "widgets": [
    {
      "name": "Faturamento Mensal",
      "type": "NUMBER",
      "kpi": "MONTHLY_REVENUE",
      "position": {"x": 0, "y": 0, "w": 3, "h": 2}
    },
    {
      "name": "Margem Liquida",
      "type": "GAUGE",
      "kpi": "NET_MARGIN",
      "position": {"x": 3, "y": 0, "w": 3, "h": 2}
    },
    {
      "name": "Contratos Ativos",
      "type": "NUMBER",
      "kpi": "ACTIVE_CONTRACTS",
      "position": {"x": 6, "y": 0, "w": 3, "h": 2}
    },
    {
      "name": "Inadimplencia",
      "type": "NUMBER",
      "kpi": "DEFAULT_RATE",
      "position": {"x": 9, "y": 0, "w": 3, "h": 2}
    },
    {
      "name": "Evolucao Faturamento",
      "type": "CHART_LINE",
      "source": "revenue_trend",
      "position": {"x": 0, "y": 2, "w": 8, "h": 4}
    },
    {
      "name": "Top Clientes",
      "type": "TABLE",
      "source": "top_clients",
      "position": {"x": 8, "y": 2, "w": 4, "h": 4}
    }
  ]
}
```

### KPIs Padrao

```python
KPIS = [
    {
        "code": "MONTHLY_REVENUE",
        "name": "Faturamento Mensal",
        "category": "FINANCIAL",
        "formula": "SELECT SUM(received_value) FROM receivables WHERE status='RECEIVED' AND DATE_TRUNC('month', received_date) = DATE_TRUNC('month', CURRENT_DATE)",
        "format": "CURRENCY",
        "target": 1000000,
        "threshold_good": 900000,
        "threshold_warning": 700000,
        "threshold_critical": 500000
    },
    {
        "code": "NET_MARGIN",
        "name": "Margem Liquida",
        "category": "FINANCIAL",
        "formula": "...",
        "format": "PERCENT",
        "target": 15,
        "threshold_good": 12,
        "threshold_warning": 8,
        "threshold_critical": 5
    },
    {
        "code": "DEFAULT_RATE",
        "name": "Taxa de Inadimplencia",
        "category": "FINANCIAL",
        "formula": "...",
        "format": "PERCENT",
        "target": 5,
        "target_type": "BELOW",
        "threshold_good": 3,
        "threshold_warning": 5,
        "threshold_critical": 10
    },
    {
        "code": "CONVERSION_RATE",
        "name": "Taxa de Conversao",
        "category": "COMMERCIAL",
        "formula": "...",
        "format": "PERCENT",
        "target": 30
    },
    {
        "code": "EMPLOYEE_TURNOVER",
        "name": "Turnover",
        "category": "HR",
        "formula": "...",
        "format": "PERCENT",
        "target": 5,
        "target_type": "BELOW"
    },
    {
        "code": "SLA_COMPLIANCE",
        "name": "Cumprimento SLA",
        "category": "OPERATIONAL",
        "formula": "...",
        "format": "PERCENT",
        "target": 99
    }
]
```

---

## ENDPOINTS

### Dashboards

```
GET    /api/v1/dashboards/                   - Listar dashboards
GET    /api/v1/dashboards/{id}               - Obter dashboard
POST   /api/v1/dashboards/                   - Criar dashboard
PATCH  /api/v1/dashboards/{id}               - Atualizar dashboard
DELETE /api/v1/dashboards/{id}               - Remover dashboard
POST   /api/v1/dashboards/{id}/widgets       - Adicionar widget
```

### KPIs

```
GET    /api/v1/kpis/                         - Listar KPIs
GET    /api/v1/kpis/{code}                   - Obter KPI
GET    /api/v1/kpis/{code}/value             - Calcular valor
GET    /api/v1/kpis/{code}/history           - Historico
```

### Relatorios

```
GET    /api/v1/reports/                      - Listar relatorios
POST   /api/v1/reports/{code}/generate       - Gerar relatorio
GET    /api/v1/reports/scheduled             - Listar agendados
POST   /api/v1/reports/{code}/schedule       - Agendar relatorio
```

### Analytics

```
GET    /api/v1/analytics/revenue-trend       - Tendencia faturamento
GET    /api/v1/analytics/sales-funnel        - Funil de vendas
GET    /api/v1/analytics/top-clients         - Top clientes
GET    /api/v1/analytics/comparison          - Comparacao periodos
```

---

## CHECKLIST MODULO BI

- [ ] Models
  - [ ] Dashboard
  - [ ] Widget
  - [ ] KPI
  - [ ] Report
  - [ ] Alert

- [ ] Services
  - [ ] KPICalculator
  - [ ] AnalyticsService
  - [ ] ReportGenerator
  - [ ] AlertService

- [ ] Dashboards pre-definidos
  - [ ] CEO
  - [ ] Financeiro
  - [ ] Comercial
  - [ ] RH
  - [ ] Operacional

- [ ] Relatorios padrao
- [ ] Testes >= 85%
- [ ] Pylint 100/100

---

*Skill BI e Analytics - ERP Conecta Mais Fase 2*
