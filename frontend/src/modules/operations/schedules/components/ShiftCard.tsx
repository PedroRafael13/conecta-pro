import React from 'react';
import { motion } from 'framer-motion';
import {
  Clock,
  User,
  MapPin,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Play,
  RotateCcw,
  Edit,
  Trash2,
  Eye,
  LogIn,
  LogOut,
} from 'lucide-react';
import type { Schedule, ScheduleStatus } from '../types/schedules.types';

interface ShiftCardProps {
  schedule: Schedule;
  variant?: 'default' | 'compact' | 'detailed';
  onView?: (schedule: Schedule) => void;
  onEdit?: (schedule: Schedule) => void;
  onDelete?: (schedule: Schedule) => void;
  onClick?: (schedule: Schedule) => void;
  showActions?: boolean;
}

export const ShiftCard: React.FC<ShiftCardProps> = ({
  schedule,
  variant = 'default',
  onView,
  onEdit,
  onDelete,
  onClick,
  showActions = true,
}) => {
  const getStatusConfig = (status: ScheduleStatus) => {
    const configs = {
      confirmado: {
        color: 'bg-green-100 text-green-800 border-green-200',
        bgColor: 'bg-green-50',
        icon: CheckCircle,
        iconColor: 'text-green-600',
        label: 'Confirmado',
      },
      pendente: {
        color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
        bgColor: 'bg-yellow-50',
        icon: AlertTriangle,
        iconColor: 'text-yellow-600',
        label: 'Pendente',
      },
      cancelado: {
        color: 'bg-red-100 text-red-800 border-red-200',
        bgColor: 'bg-red-50',
        icon: XCircle,
        iconColor: 'text-red-600',
        label: 'Cancelado',
      },
      em_andamento: {
        color: 'bg-blue-100 text-blue-800 border-blue-200',
        bgColor: 'bg-blue-50',
        icon: Play,
        iconColor: 'text-blue-600',
        label: 'Em Andamento',
      },
      concluido: {
        color: 'bg-gray-100 text-gray-800 border-gray-200',
        bgColor: 'bg-gray-50',
        icon: CheckCircle,
        iconColor: 'text-gray-600',
        label: 'Concluido',
      },
      falta: {
        color: 'bg-red-100 text-red-800 border-red-200',
        bgColor: 'bg-red-50',
        icon: XCircle,
        iconColor: 'text-red-600',
        label: 'Falta',
      },
      substituido: {
        color: 'bg-purple-100 text-purple-800 border-purple-200',
        bgColor: 'bg-purple-50',
        icon: RotateCcw,
        iconColor: 'text-purple-600',
        label: 'Substituido',
      },
    };
    return configs[status] || configs.pendente;
  };

  const statusConfig = getStatusConfig(schedule.status);
  const StatusIcon = statusConfig.icon;

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Versao Compacta
  if (variant === 'compact') {
    return (
      <motion.div
        whileHover={{ scale: 1.01 }}
        onClick={() => onClick?.(schedule)}
        className={`flex items-center gap-3 p-3 rounded-lg border border-gray-200 cursor-pointer hover:border-blue-300 transition-colors ${statusConfig.bgColor}`}
      >
        <div className={`p-2 rounded-lg ${statusConfig.color}`}>
          <StatusIcon className="w-4 h-4" />
        </div>

        <div className="flex-1 min-w-0">
          <p className="font-medium text-gray-900 text-sm truncate">
            {schedule.profissional_nome}
          </p>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <Clock className="w-3 h-3" />
            {schedule.horario_inicio} - {schedule.horario_fim}
          </div>
        </div>

        <div className="text-right">
          <p className="text-xs text-gray-500 truncate max-w-[100px]">
            {schedule.posto_nome}
          </p>
        </div>
      </motion.div>
    );
  }

  // Versao Detalhada
  if (variant === 'detailed') {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden"
      >
        {/* Header com status */}
        <div className={`px-4 py-3 ${statusConfig.bgColor} border-b border-gray-200`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <StatusIcon className={`w-5 h-5 ${statusConfig.iconColor}`} />
              <span className={`text-sm font-medium ${statusConfig.iconColor}`}>
                {statusConfig.label}
              </span>
            </div>
            <span className="text-sm text-gray-500">{schedule.data}</span>
          </div>
        </div>

        {/* Conteudo */}
        <div className="p-4">
          {/* Profissional */}
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center">
              {schedule.profissional_avatar ? (
                <img
                  src={schedule.profissional_avatar}
                  alt={schedule.profissional_nome}
                  className="w-12 h-12 rounded-full object-cover"
                />
              ) : (
                <User className="w-6 h-6 text-gray-500" />
              )}
            </div>
            <div>
              <h4 className="font-semibold text-gray-900">
                {schedule.profissional_nome}
              </h4>
              <p className="text-sm text-gray-500">{schedule.profissional_funcao}</p>
            </div>
          </div>

          {/* Info Grid */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="flex items-center gap-2 text-gray-600 mb-1">
                <MapPin className="w-4 h-4" />
                <span className="text-xs font-medium">Posto</span>
              </div>
              <p className="text-sm text-gray-900 font-medium">
                {schedule.posto_nome}
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-3">
              <div className="flex items-center gap-2 text-gray-600 mb-1">
                <Clock className="w-4 h-4" />
                <span className="text-xs font-medium">Turno</span>
              </div>
              <p className="text-sm text-gray-900 font-medium">{schedule.turno}</p>
              <p className="text-xs text-gray-500">
                {schedule.horario_inicio} - {schedule.horario_fim}
              </p>
            </div>
          </div>

          {/* Check-in/out */}
          <div className="space-y-2">
            {schedule.check_in && (
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <LogIn className="w-4 h-4 text-green-600" />
                  <span className="text-sm font-medium text-green-800">Check-in</span>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-green-800">
                    {formatTime(schedule.check_in.timestamp)}
                  </p>
                  <p className="text-xs text-green-600 capitalize">
                    {schedule.check_in.metodo}
                  </p>
                </div>
              </div>
            )}

            {schedule.check_out && (
              <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <LogOut className="w-4 h-4 text-blue-600" />
                  <span className="text-sm font-medium text-blue-800">Check-out</span>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-blue-800">
                    {formatTime(schedule.check_out.timestamp)}
                  </p>
                  <p className="text-xs text-blue-600 capitalize">
                    {schedule.check_out.metodo}
                  </p>
                </div>
              </div>
            )}

            {!schedule.check_in && schedule.status === 'pendente' && (
              <div className="flex items-center justify-center p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-500">Aguardando check-in</p>
              </div>
            )}
          </div>

          {/* Observacoes */}
          {schedule.observacoes && (
            <div className="mt-4 p-3 bg-yellow-50 rounded-lg">
              <p className="text-sm text-yellow-800">{schedule.observacoes}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        {showActions && (
          <div className="px-4 py-3 border-t border-gray-200 bg-gray-50 flex gap-2">
            {onView && (
              <button
                onClick={() => onView(schedule)}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
              >
                <Eye className="w-4 h-4" />
                Detalhes
              </button>
            )}
            {onEdit && (
              <button
                onClick={() => onEdit(schedule)}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
              >
                <Edit className="w-4 h-4" />
                Editar
              </button>
            )}
          </div>
        )}
      </motion.div>
    );
  }

  // Versao Default
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      onClick={() => onClick?.(schedule)}
      className="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-all cursor-pointer overflow-hidden"
    >
      {/* Indicador de status */}
      <div className={`h-1 ${statusConfig.color.split(' ')[0]}`} />

      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
              {schedule.profissional_avatar ? (
                <img
                  src={schedule.profissional_avatar}
                  alt={schedule.profissional_nome}
                  className="w-10 h-10 rounded-full object-cover"
                />
              ) : (
                <User className="w-5 h-5 text-gray-500" />
              )}
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 text-sm">
                {schedule.profissional_nome}
              </h4>
              <p className="text-xs text-gray-500">{schedule.profissional_funcao}</p>
            </div>
          </div>

          {/* Status Badge */}
          <span
            className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border ${statusConfig.color}`}
          >
            <StatusIcon className="w-3 h-3" />
            {statusConfig.label}
          </span>
        </div>

        {/* Info */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <MapPin className="w-4 h-4 text-gray-400" />
            <span className="truncate">{schedule.posto_nome}</span>
          </div>

          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Clock className="w-4 h-4 text-gray-400" />
            <span>
              {schedule.horario_inicio} - {schedule.horario_fim}
            </span>
            <span className="text-gray-400">|</span>
            <span className="text-gray-500">{schedule.turno}</span>
          </div>
        </div>

        {/* Check-in indicator */}
        {schedule.check_in && (
          <div className="mt-3 flex items-center gap-2 text-xs text-green-600">
            <CheckCircle className="w-3.5 h-3.5" />
            <span>Check-in: {formatTime(schedule.check_in.timestamp)}</span>
          </div>
        )}

        {/* Actions */}
        {showActions && (onView || onEdit || onDelete) && (
          <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-end gap-2">
            {onView && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onView(schedule);
                }}
                className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Ver detalhes"
              >
                <Eye className="w-4 h-4" />
              </button>
            )}
            {onEdit && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onEdit(schedule);
                }}
                className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                title="Editar"
              >
                <Edit className="w-4 h-4" />
              </button>
            )}
            {onDelete && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(schedule);
                }}
                className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Excluir"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default ShiftCard;
