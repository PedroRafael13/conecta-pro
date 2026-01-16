import { motion } from 'framer-motion';
import {
  Building,
  FileText,
  Users,
  Receipt,
  UserPlus,
  Calendar,
  Wallet,
  Shield,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  RefreshCw,
  ArrowRight,
} from 'lucide-react';
import { useGovernmentAPIs, useObligations, useGovernmentStats } from './hooks/useGovernment';
import { formatRelativeTime } from '@core/utils/formatters';
import { StatCard } from '@modules/dashboards/widgets';

const iconMap: Record<string, React.ElementType> = {
  building: Building,
  'file-text': FileText,
  users: Users,
  receipt: Receipt,
  'user-plus': UserPlus,
  calendar: Calendar,
  wallet: Wallet,
  shield: Shield,
};

const statusConfig = {
  online: { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-100', label: 'Online' },
  offline: { icon: XCircle, color: 'text-red-500', bg: 'bg-red-100', label: 'Offline' },
  manutencao: { icon: AlertTriangle, color: 'text-yellow-500', bg: 'bg-yellow-100', label: 'Manutencao' },
};

const obligationStatusConfig = {
  pendente: { color: 'bg-yellow-100 text-yellow-700' },
  enviado: { color: 'bg-blue-100 text-blue-700' },
  aprovado: { color: 'bg-green-100 text-green-700' },
  rejeitado: { color: 'bg-red-100 text-red-700' },
};

export function GovernmentDashboard() {
  const { data: apis, isLoading: apisLoading } = useGovernmentAPIs();
  const { data: obligations, isLoading: obligationsLoading } = useObligations();
  const { data: stats } = useGovernmentStats();

  const getDaysRemaining = (deadline: string) => {
    const now = new Date();
    return Math.ceil((new Date(deadline).getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-2">
            <Building className="w-7 h-7 text-conecta-escuro" />
            <h1 className="text-2xl font-bold text-gray-900">Integracoes Governamentais</h1>
          </div>
          <p className="text-gray-600 mt-1">8 APIs conectadas e monitoradas em tempo real</p>
        </motion.div>

        <button className="btn-primary flex items-center gap-2">
          <RefreshCw className="w-4 h-4" />
          Sincronizar Todas
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
        <StatCard title="APIs Conectadas" value={`${stats?.apisConnected || 0}/8`} icon={CheckCircle} size="sm" />
        <StatCard title="Obrigacoes Pendentes" value={stats?.obligationsPending.toString() || '0'} icon={Clock} size="sm" />
        <StatCard title="Taxa de Sucesso" value={`${stats?.syncSuccess || 0}%`} icon={RefreshCw} size="sm" />
        <StatCard title="Prazos Proximos" value={stats?.nearDeadlines.toString() || '0'} icon={AlertTriangle} size="sm" />
      </div>

      {/* APIs Grid */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-white rounded-xl shadow-card p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Status das APIs</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {apisLoading ? (
            Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded-lg animate-pulse" />
            ))
          ) : (
            apis?.map((apiItem, index) => {
              const status = statusConfig[apiItem.status];
              const StatusIcon = status.icon;
              const ApiIcon = iconMap[apiItem.icon] || Building;

              return (
                <motion.div
                  key={apiItem.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.05 }}
                  className={`${status.bg} rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-3">
                      <ApiIcon className={`w-8 h-8 ${status.color}`} />
                      <div>
                        <p className="font-medium text-gray-900">{apiItem.name}</p>
                        <p className="text-xs text-gray-600">{apiItem.code}</p>
                      </div>
                    </div>
                    <StatusIcon className={`w-5 h-5 ${status.color}`} />
                  </div>
                  <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                    <span>Sync: {formatRelativeTime(apiItem.lastSync)}</span>
                    <span className="font-medium">{apiItem.successRate}%</span>
                  </div>
                </motion.div>
              );
            })
          )}
        </div>
      </motion.div>

      {/* Obligations */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-white rounded-xl shadow-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Obrigacoes Governamentais</h3>
          <button className="text-sm text-conecta-escuro hover:underline flex items-center gap-1">
            Ver todas <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-3">
          {obligationsLoading ? (
            Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 rounded-lg animate-pulse" />
            ))
          ) : (
            obligations?.map((obligation) => {
              const days = getDaysRemaining(obligation.deadline);
              const isUrgent = days <= 7 && obligation.status === 'pendente';
              const statusStyle = obligationStatusConfig[obligation.status];

              return (
                <div
                  key={obligation.id}
                  className={`flex items-center justify-between p-4 rounded-lg ${isUrgent ? 'bg-red-50 border border-red-200' : 'bg-gray-50'}`}
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-medium text-gray-900">{obligation.name}</p>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${statusStyle.color}`}>
                        {obligation.status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mt-0.5">{obligation.apiName}</p>
                  </div>
                  <div className="text-right">
                    <p className={`text-sm font-medium ${isUrgent ? 'text-red-600' : 'text-gray-700'}`}>
                      {days > 0 ? `${days} dias` : 'Vencido'}
                    </p>
                    <p className="text-xs text-gray-500">Prazo</p>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </motion.div>
    </div>
  );
}

export default GovernmentDashboard;
