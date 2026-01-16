import { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, Plus,  Download, RefreshCw } from 'lucide-react';
import { ComplianceScoreCard, AnomalyCard, ComplianceTrend, ExecutionList } from './components';
import { useComplianceScore, useAnomalies, useAuditExecutions } from './hooks/useAudit';
import type { Anomaly } from './types/audit.types';

export function AuditDashboard() {
  const [selectedPriority, setSelectedPriority] = useState<string>('all');
  const { data: score, isLoading: scoreLoading } = useComplianceScore();
  const { data: anomalies, isLoading: anomaliesLoading } = useAnomalies(
    selectedPriority !== 'all' ? { status: selectedPriority } : undefined
  );
  const { data: executions, isLoading: executionsLoading } = useAuditExecutions();

  const handleViewAnomalyDetails = (anomaly: Anomaly) => {
    console.log('View anomaly:', anomaly);
  };

  const pendingAnomalies = anomalies?.filter(a => a.status === 'pendente') || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center gap-2">
            <Shield className="w-7 h-7 text-conecta-escuro" />
            <h1 className="text-2xl font-bold text-gray-900">Auditoria & Compliance</h1>
          </div>
          <p className="text-gray-600 mt-1">
            Monitoramento continuo com deteccao de anomalias por IA
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex items-center gap-2"
        >
          <button className="btn-ghost flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
          </button>
          <button className="btn-secondary flex items-center gap-2">
            <Download className="w-4 h-4" />
            <span className="hidden sm:inline">Exportar</span>
          </button>
          <button className="btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">Nova Regra</span>
          </button>
        </motion.div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Compliance Score */}
        <div className="lg:col-span-1">
          {score && <ComplianceScoreCard score={score} isLoading={scoreLoading} />}
        </div>

        {/* Compliance Trend */}
        <div className="lg:col-span-2">
          {score && <ComplianceTrend data={score.trend} isLoading={scoreLoading} />}
        </div>
      </div>

      {/* Second Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Executions */}
        <ExecutionList
          executions={executions || []}
          isLoading={executionsLoading}
        />

        {/* Anomalies */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl shadow-card p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-semibold text-gray-900">Anomalias Detectadas</h3>
              {pendingAnomalies.length > 0 && (
                <span className="px-2 py-0.5 text-xs bg-red-100 text-red-700 rounded-full">
                  {pendingAnomalies.length} pendentes
                </span>
              )}
            </div>
            <select
              value={selectedPriority}
              onChange={(e) => setSelectedPriority(e.target.value)}
              className="text-sm border border-gray-200 rounded-lg px-3 py-1.5"
            >
              <option value="all">Todas</option>
              <option value="pendente">Pendentes</option>
              <option value="em_analise">Em Analise</option>
              <option value="resolvida">Resolvidas</option>
            </select>
          </div>

          <div className="space-y-3 max-h-96 overflow-y-auto">
            {anomaliesLoading ? (
              <div className="animate-pulse space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-24 bg-gray-200 rounded-xl" />
                ))}
              </div>
            ) : anomalies && anomalies.length > 0 ? (
              anomalies.map((anomaly) => (
                <AnomalyCard
                  key={anomaly.id}
                  anomaly={anomaly}
                  onViewDetails={handleViewAnomalyDetails}
                />
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                Nenhuma anomalia encontrada
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
}

export default AuditDashboard;
