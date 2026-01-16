import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Shield,
  Users,
  FileCheck,
  Clock,
  AlertTriangle,
  Plus,
  Download,
  User,
  Calendar,
  CheckCircle,
} from 'lucide-react';
import { useLGPDStats, useRightsRequests } from './hooks/useLGPD';
import { formatRelativeTime } from '@core/utils/formatters';
import { StatCard, ProgressRing } from '@modules/dashboards/widgets';

const requestTypeLabels = {
  acesso: 'Acesso',
  retificacao: 'Retificacao',
  portabilidade: 'Portabilidade',
  exclusao: 'Exclusao',
  oposicao: 'Oposicao',
};

const statusConfig = {
  pendente: { label: 'Pendente', color: 'bg-yellow-100 text-yellow-700', icon: Clock },
  em_andamento: { label: 'Em Andamento', color: 'bg-blue-100 text-blue-700', icon: User },
  concluida: { label: 'Concluida', color: 'bg-green-100 text-green-700', icon: CheckCircle },
  recusada: { label: 'Recusada', color: 'bg-red-100 text-red-700', icon: AlertTriangle },
};

export function LGPDDashboard() {
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const { data: stats } = useLGPDStats();
  const { data: requests, isLoading: requestsLoading } = useRightsRequests(
    statusFilter !== 'all' ? statusFilter : undefined
  );

  const getDaysRemaining = (deadline: string) => {
    const now = new Date();
    const days = Math.ceil((new Date(deadline).getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    return days;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center gap-2">
            <Shield className="w-7 h-7 text-purple-600" />
            <h1 className="text-2xl font-bold text-gray-900">LGPD Compliance</h1>
          </div>
          <p className="text-gray-600 mt-1">
            Gestao de consentimentos e direitos dos titulares
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex items-center gap-2"
        >
          <button className="btn-secondary flex items-center gap-2">
            <Download className="w-4 h-4" />
            <span className="hidden sm:inline">Relatorio</span>
          </button>
          <button className="btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">Novo Titular</span>
          </button>
        </motion.div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-5 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm">Score Compliance</p>
              <p className="text-3xl font-bold mt-1">{stats?.complianceScore || 0}%</p>
            </div>
            <ProgressRing value={stats?.complianceScore || 0} size="sm" color="#fff" />
          </div>
        </motion.div>

        <StatCard
          title="Titulares"
          value={stats?.totalSubjects.toLocaleString() || '0'}
          icon={Users}
          variant="default"
          size="sm"
        />
        <StatCard
          title="Consentimentos Ativos"
          value={stats?.activeConsents.toLocaleString() || '0'}
          icon={FileCheck}
          variant="default"
          size="sm"
        />
        <StatCard
          title="Requests Pendentes"
          value={stats?.pendingRequests.toString() || '0'}
          icon={Clock}
          variant="default"
          size="sm"
        />
        <StatCard
          title="Expirando em 30d"
          value={stats?.expiringConsents.toString() || '0'}
          icon={AlertTriangle}
          variant="default"
          size="sm"
        />
      </div>

      {/* Requests Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-xl shadow-card"
      >
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Solicitacoes de Direitos</h3>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="text-sm border border-gray-200 rounded-lg px-3 py-1.5"
            >
              <option value="all">Todas</option>
              <option value="pendente">Pendentes</option>
              <option value="em_andamento">Em Andamento</option>
              <option value="concluida">Concluidas</option>
            </select>
          </div>
        </div>

        <div className="divide-y divide-gray-100">
          {requestsLoading ? (
            <div className="p-6 animate-pulse">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-20 bg-gray-200 rounded-lg mb-3" />
              ))}
            </div>
          ) : requests && requests.length > 0 ? (
            requests.map((request) => {
              const status = statusConfig[request.status];
              const StatusIcon = status.icon;
              const daysRemaining = getDaysRemaining(request.deadline);
              const isUrgent = daysRemaining <= 5 && request.status !== 'concluida';

              return (
                <div
                  key={request.id}
                  className="p-4 hover:bg-gray-50 transition-colors cursor-pointer"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3">
                      <div className={`p-2 rounded-lg ${isUrgent ? 'bg-red-100' : 'bg-gray-100'}`}>
                        <StatusIcon className={`w-5 h-5 ${isUrgent ? 'text-red-600' : 'text-gray-600'}`} />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-medium text-gray-900">{request.subjectName}</p>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${status.color}`}>
                            {status.label}
                          </span>
                          <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-700">
                            {requestTypeLabels[request.type]}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{request.description}</p>
                        <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            Criado {formatRelativeTime(request.createdAt)}
                          </span>
                          <span className={`flex items-center gap-1 ${isUrgent ? 'text-red-600 font-medium' : ''}`}>
                            <Clock className="w-3 h-3" />
                            {daysRemaining > 0 ? `${daysRemaining} dias restantes` : 'Vencido!'}
                          </span>
                          {request.assignedTo && (
                            <span className="flex items-center gap-1">
                              <User className="w-3 h-3" />
                              {request.assignedTo.name}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <button className="text-sm text-conecta-escuro hover:underline">
                      Ver detalhes
                    </button>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="p-12 text-center text-gray-500">
              Nenhuma solicitacao encontrada
            </div>
          )}
        </div>
      </motion.div>
    </div>
  );
}

export default LGPDDashboard;
