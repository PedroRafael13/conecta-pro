import { motion } from 'framer-motion';
import { CheckCircle, AlertTriangle, Info, XCircle, ExternalLink } from 'lucide-react';
import { formatRelativeTime } from '@core/utils/formatters';
import { Avatar } from '@core/components/ui';
import { Skeleton } from '@core/components/feedback';
import type { Activity } from '../types/dashboard.types';

interface ActivityFeedProps {
  activities: Activity[];
  isLoading?: boolean;
  maxItems?: number;
}

const typeConfig = {
  success: {
    icon: CheckCircle,
    color: 'text-green-500',
    bg: 'bg-green-100',
  },
  warning: {
    icon: AlertTriangle,
    color: 'text-yellow-500',
    bg: 'bg-yellow-100',
  },
  info: {
    icon: Info,
    color: 'text-blue-500',
    bg: 'bg-blue-100',
  },
  error: {
    icon: XCircle,
    color: 'text-red-500',
    bg: 'bg-red-100',
  },
};

function ActivityItem({ activity, index }: { activity: Activity; index: number }) {
  const config = typeConfig[activity.type];
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      className="flex items-start gap-3 p-3 hover:bg-gray-50 rounded-lg transition-colors group"
    >
      {/* Avatar or Icon */}
      <div className="flex-shrink-0">
        {activity.user.avatar ? (
          <Avatar src={activity.user.avatar} name={activity.user.name} size="sm" />
        ) : (
          <Avatar name={activity.user.name} size="sm" />
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <p className="text-sm text-gray-900">
            <span className="font-medium">{activity.user.name}</span>{' '}
            <span className="text-gray-600">{activity.action}</span>
            {activity.target && (
              <>
                {' '}
                <span className="font-medium text-conecta-escuro">
                  {activity.target}
                </span>
              </>
            )}
          </p>
          <div className={`p-1 rounded-full ${config.bg}`}>
            <Icon className={`w-3 h-3 ${config.color}`} />
          </div>
        </div>
        <div className="flex items-center gap-2 mt-1">
          <span className="text-xs text-gray-500">
            {formatRelativeTime(activity.timestamp)}
          </span>
          {activity.link && (
            <a
              href={activity.link}
              className="text-xs text-conecta-escuro hover:text-conecta-medio flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
            >
              Ver detalhes
              <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </div>
      </div>
    </motion.div>
  );
}

export function ActivityFeed({ activities, isLoading, maxItems = 10 }: ActivityFeedProps) {
  const displayedActivities = activities.slice(0, maxItems);

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-card p-6">
        <Skeleton height={24} className="w-40 mb-4" />
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex items-start gap-3 p-3">
              <Skeleton width={32} height={32} rounded="full" />
              <div className="flex-1">
                <Skeleton height={16} className="w-3/4 mb-2" />
                <Skeleton height={12} className="w-24" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Atividades Recentes
        </h3>
        <button className="text-sm text-conecta-escuro hover:text-conecta-medio font-medium">
          Ver todas
        </button>
      </div>

      <div className="space-y-1">
        {displayedActivities.length > 0 ? (
          displayedActivities.map((activity, index) => (
            <ActivityItem key={activity.id} activity={activity} index={index} />
          ))
        ) : (
          <div className="text-center py-8">
            <Info className="w-12 h-12 text-gray-300 mx-auto mb-2" />
            <p className="text-sm text-gray-500">Nenhuma atividade recente</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default ActivityFeed;
