// Executive Dashboard
export { ExecutiveDashboard } from './executive/ExecutiveDashboard';
export { KPICards } from './executive/KPICards';
export { RevenueChart } from './executive/RevenueChart';
export { ComplianceChart } from './executive/ComplianceChart';
export { OperationsChart } from './executive/OperationsChart';
export { ActivityFeed } from './executive/ActivityFeed';

// Analytics Dashboard
export { AnalyticsDashboard, PredictiveChart, AnomalyDetection, TrendAnalysis } from './analytics';

// Real-time Components
export { RealtimeMetrics, LiveAlerts, LiveActivityFeed } from './realtime';

// Reusable Widgets
export {
  ChartWidget,
  StatCard,
  ProgressRing,
  SuccessRing,
  WarningRing,
  DangerRing,
  MiniChart,
  MiniStat,
  TableWidget,
} from './widgets';

// Hooks
export { useDashboardData } from './hooks/useDashboardData';
export { useWebSocket, useSimulatedWebSocket } from './hooks/useWebSocket';

// Types
export type * from './types/dashboard.types';
