export interface KPI {
  id: string;
  label: string;
  value: number;
  format: 'currency' | 'percent' | 'number';
  change: number;
  trend: 'up' | 'down' | 'stable';
  sparkline?: number[];
  icon?: string;
  color?: 'blue' | 'green' | 'orange' | 'purple' | 'red';
}

export interface ChartDataPoint {
  date: string;
  label?: string;
  value: number;
  [key: string]: string | number | undefined;
}

export interface RevenueChartData {
  date: string;
  revenue: number;
  forecast: number;
  label?: string;
}

export interface ComplianceScore {
  category: string;
  score: number;
  color: string;
  label: string;
  [key: string]: string | number;
}

export interface OperationStatus {
  module: string;
  status: 'ok' | 'warning' | 'critical';
  percentage: number;
  label: string;
}

export interface Activity {
  id: string;
  user: {
    name: string;
    avatar?: string;
  };
  action: string;
  target?: string;
  timestamp: string;
  type: 'success' | 'warning' | 'info' | 'error';
  link?: string;
}

export interface DashboardFilters {
  dateRange: {
    start: string;
    end: string;
  };
  modules?: string[];
  status?: string[];
}

export interface PredictiveData {
  date: string;
  actual?: number;
  predicted: number;
  lowerBound: number;
  upperBound: number;
}

export interface AnomalyData {
  id: string;
  metric: string;
  value: number;
  expected: number;
  deviation: number;
  severity: 'low' | 'medium' | 'high';
  timestamp: string;
  description: string;
}

export interface TrendData {
  id: string;
  metric: string;
  direction: 'up' | 'down' | 'stable';
  change: number;
  period: string;
  significance: 'low' | 'medium' | 'high';
  insight: string;
}

export interface WebSocketMessage {
  type: 'metric.update' | 'alert.critical' | 'activity' | 'heartbeat';
  data: Record<string, unknown>;
  timestamp: string;
}

export interface RealtimeMetric {
  key: string;
  label: string;
  value: number;
  format: 'number' | 'percent' | 'currency';
  icon: string;
  color: string;
}

export interface LiveAlert {
  id: string;
  type: 'anomaly' | 'compliance' | 'security' | 'document';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  timestamp: string;
  acknowledged: boolean;
}
