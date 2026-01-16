import { RealtimeMetrics, LiveAlerts, LiveActivityFeed } from '@modules/dashboards';

export function RealtimePage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Monitoramento em Tempo Real
        </h1>
        <p className="text-gray-600 mt-1">
          Metricas e atividades atualizadas automaticamente
        </p>
      </div>

      {/* Real-time Metrics */}
      <RealtimeMetrics />

      {/* Live Feeds */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LiveAlerts maxAlerts={5} />
        <LiveActivityFeed />
      </div>
    </div>
  );
}

export default RealtimePage;
