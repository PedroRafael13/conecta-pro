import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Pause, Play, Filter } from 'lucide-react';
import { Avatar } from '@core/components/ui';
import { formatRelativeTime } from '@core/utils/formatters';
import { useSimulatedWebSocket } from '../hooks/useWebSocket';

interface ActivityItem {
  id: string;
  user: string;
  action: string;
  target?: string;
  timestamp: string;
  module?: string;
}

const mockActivities: ActivityItem[] = [
  { id: '1', user: 'Maria Silva', action: 'aprovou documento', target: 'Contrato #2847', timestamp: new Date(Date.now() - 1 * 60 * 1000).toISOString(), module: 'ged' },
  { id: '2', user: 'Joao Santos', action: 'criou proposta', target: 'Cliente ABC', timestamp: new Date(Date.now() - 3 * 60 * 1000).toISOString(), module: 'crm' },
  { id: '3', user: 'Ana Costa', action: 'finalizou auditoria', target: 'Q4 2025', timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(), module: 'audit' },
  { id: '4', user: 'Pedro Lima', action: 'atualizou cadastro', target: 'Fornecedor XYZ', timestamp: new Date(Date.now() - 8 * 60 * 1000).toISOString(), module: 'operations' },
  { id: '5', user: 'Carla Souza', action: 'enviou relatorio', target: 'Mensal Financeiro', timestamp: new Date(Date.now() - 12 * 60 * 1000).toISOString(), module: 'finance' },
];

const moduleColors: Record<string, string> = {
  ged: 'bg-blue-100 text-blue-700',
  crm: 'bg-green-100 text-green-700',
  audit: 'bg-purple-100 text-purple-700',
  operations: 'bg-orange-100 text-orange-700',
  finance: 'bg-yellow-100 text-yellow-700',
};

function ActivityItemComponent({ activity, index }: { activity: ActivityItem; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 10 }}
      transition={{ delay: index * 0.05 }}
      className="flex items-start gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors"
    >
      <Avatar name={activity.user} size="sm" />
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-900">
          <span className="font-medium">{activity.user}</span>{' '}
          <span className="text-gray-600">{activity.action}</span>
          {activity.target && (
            <>
              {' '}
              <span className="font-medium text-conecta-escuro">{activity.target}</span>
            </>
          )}
        </p>
        <div className="flex items-center gap-2 mt-1">
          <span className="text-xs text-gray-500">
            {formatRelativeTime(activity.timestamp)}
          </span>
          {activity.module && (
            <span className={`text-xs px-2 py-0.5 rounded-full ${moduleColors[activity.module]}`}>
              {activity.module}
            </span>
          )}
        </div>
      </div>
    </motion.div>
  );
}

export function LiveActivityFeed() {
  const [activities, setActivities] = useState<ActivityItem[]>(mockActivities);
  const [isPaused, setIsPaused] = useState(false);
  const [filter, setFilter] = useState<string>('all');
  const { lastMessage } = useSimulatedWebSocket('activity');
  const containerRef = useRef<HTMLDivElement>(null);

  // Handle new activities from WebSocket
  useEffect(() => {
    if (!isPaused && lastMessage?.type === 'activity' && lastMessage.data) {
      const data = lastMessage.data as { user: string; action: string };
      const newActivity: ActivityItem = {
        id: Date.now().toString(),
        user: data.user,
        action: data.action,
        timestamp: new Date().toISOString(),
        module: ['ged', 'crm', 'audit', 'operations', 'finance'][Math.floor(Math.random() * 5)],
      };

      // eslint-disable-next-line react-hooks/set-state-in-effect
      setActivities((prev) => [newActivity, ...prev].slice(0, 20));
    }
  }, [lastMessage, isPaused]);

  const filteredActivities = filter === 'all'
    ? activities
    : activities.filter((a) => a.module === filter);

  return (
    <div className="bg-white rounded-xl shadow-card p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-conecta-escuro" />
          <h3 className="text-lg font-semibold text-gray-900">Feed de Atividades</h3>
          {!isPaused && (
            <span className="flex items-center gap-1 text-xs text-green-600">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              Ao vivo
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {/* Module filter */}
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="text-xs border border-gray-200 rounded-lg px-2 py-1 focus:outline-none focus:ring-2 focus:ring-conecta-escuro"
          >
            <option value="all">Todos</option>
            <option value="ged">GED</option>
            <option value="crm">CRM</option>
            <option value="audit">Auditoria</option>
            <option value="operations">Operacoes</option>
            <option value="finance">Financeiro</option>
          </select>

          {/* Pause/Play */}
          <button
            onClick={() => setIsPaused(!isPaused)}
            className={`p-2 rounded-lg transition-colors ${
              isPaused
                ? 'bg-green-100 text-green-600'
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Activity List */}
      <div
        ref={containerRef}
        className="space-y-1 max-h-80 overflow-y-auto scrollbar-thin"
      >
        <AnimatePresence mode="popLayout">
          {filteredActivities.map((activity, index) => (
            <ActivityItemComponent
              key={activity.id}
              activity={activity}
              index={index}
            />
          ))}
        </AnimatePresence>

        {filteredActivities.length === 0 && (
          <div className="text-center py-8">
            <Filter className="w-12 h-12 text-gray-300 mx-auto mb-2" />
            <p className="text-sm text-gray-500">Nenhuma atividade encontrada</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default LiveActivityFeed;
