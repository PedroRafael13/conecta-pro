'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  Wrench,
  AlertTriangle,
  Clock,
  CheckCircle,
  XCircle,
  Calendar,
  User,
  DollarSign,
  MapPin,
  ChevronRight,
  Play,
  MoreVertical
} from 'lucide-react';
import type {
  MaintenanceOrder,
  MaintenanceType,
  MaintenancePriority,
  MaintenanceStatus
} from '../types/maintenance.types';

interface MaintenanceCardProps {
  order: MaintenanceOrder;
  onView?: (order: MaintenanceOrder) => void;
  onStart?: (order: MaintenanceOrder) => void;
  onComplete?: (order: MaintenanceOrder) => void;
  onCancel?: (order: MaintenanceOrder) => void;
  compact?: boolean;
}

const typeConfig: Record<MaintenanceType, {
  label: string;
  color: string;
  bgColor: string;
}> = {
  preventiva: {
    label: 'Preventiva',
    color: 'text-blue-700',
    bgColor: 'bg-blue-100'
  },
  corretiva: {
    label: 'Corretiva',
    color: 'text-orange-700',
    bgColor: 'bg-orange-100'
  },
  preditiva: {
    label: 'Preditiva',
    color: 'text-purple-700',
    bgColor: 'bg-purple-100'
  }
};

const priorityConfig: Record<MaintenancePriority, {
  label: string;
  color: string;
  bgColor: string;
  borderColor: string;
}> = {
  urgente: {
    label: 'Urgente',
    color: 'text-red-700',
    bgColor: 'bg-red-100',
    borderColor: 'border-red-300'
  },
  alta: {
    label: 'Alta',
    color: 'text-orange-700',
    bgColor: 'bg-orange-100',
    borderColor: 'border-orange-300'
  },
  normal: {
    label: 'Normal',
    color: 'text-blue-700',
    bgColor: 'bg-blue-100',
    borderColor: 'border-blue-300'
  },
  baixa: {
    label: 'Baixa',
    color: 'text-gray-700',
    bgColor: 'bg-gray-100',
    borderColor: 'border-gray-300'
  }
};

const statusConfig: Record<MaintenanceStatus, {
  label: string;
  color: string;
  bgColor: string;
  icon: React.ElementType;
}> = {
  agendada: {
    label: 'Agendada',
    color: 'text-blue-700',
    bgColor: 'bg-blue-100',
    icon: Calendar
  },
  em_execucao: {
    label: 'Em Execucao',
    color: 'text-yellow-700',
    bgColor: 'bg-yellow-100',
    icon: Wrench
  },
  concluida: {
    label: 'Concluida',
    color: 'text-green-700',
    bgColor: 'bg-green-100',
    icon: CheckCircle
  },
  cancelada: {
    label: 'Cancelada',
    color: 'text-gray-700',
    bgColor: 'bg-gray-100',
    icon: XCircle
  },
  atrasada: {
    label: 'Atrasada',
    color: 'text-red-700',
    bgColor: 'bg-red-100',
    icon: AlertTriangle
  }
};

export function MaintenanceCard({
  order,
  onView,
  onStart,
  onComplete,
  compact = false
}: MaintenanceCardProps) {
  const type = typeConfig[order.tipo];
  const priority = priorityConfig[order.prioridade];
  const status = statusConfig[order.status];
  const StatusIcon = status.icon;

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR');
  };

  const formatCurrency = (value?: number) => {
    if (!value) return '-';
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const isOverdue = () => {
    if (order.status === 'concluida' || order.status === 'cancelada') return false;
    return new Date(order.data_agendada) < new Date();
  };

  // Versao compacta
  if (compact) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`bg-white border rounded-lg p-3 hover:shadow-md transition-all cursor-pointer ${
          isOverdue() ? 'border-red-300' : 'border-gray-200'
        }`}
        onClick={() => onView?.(order)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg ${status.bgColor}`}>
              <StatusIcon className={`w-4 h-4 ${status.color}`} />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">{order.numero}</p>
              <p className="text-xs text-gray-500">{order.equipment_nome}</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${priority.bgColor} ${priority.color}`}>
              {priority.label}
            </span>
            <ChevronRight className="w-4 h-4 text-gray-400" />
          </div>
        </div>
      </motion.div>
    );
  }

  // Versao completa
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-white border rounded-xl shadow-sm hover:shadow-lg transition-all ${
        isOverdue() ? 'border-red-300' : 'border-gray-200'
      }`}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div className={`p-2.5 rounded-lg ${status.bgColor}`}>
              <StatusIcon className={`w-6 h-6 ${status.color}`} />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="font-semibold text-gray-900">{order.numero}</h3>
                {isOverdue() && (
                  <span className="flex items-center space-x-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
                    <AlertTriangle className="w-3 h-3" />
                    <span>Atrasada</span>
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-500 mt-0.5">{order.equipment_nome}</p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${type.bgColor} ${type.color}`}>
              {type.label}
            </span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${priority.bgColor} ${priority.color}`}>
              {priority.label}
            </span>
            <button className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors">
              <MoreVertical className="w-5 h-5 text-gray-400" />
            </button>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="p-4 space-y-4">
        {/* Description */}
        <p className="text-sm text-gray-700">{order.descricao}</p>

        {/* Info Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center space-x-2 text-sm">
            <Calendar className="w-4 h-4 text-gray-400" />
            <div>
              <span className="text-gray-500">Agendada: </span>
              <span className={`font-medium ${isOverdue() ? 'text-red-600' : 'text-gray-900'}`}>
                {formatDate(order.data_agendada)}
              </span>
            </div>
          </div>

          {order.tecnico_responsavel && (
            <div className="flex items-center space-x-2 text-sm">
              <User className="w-4 h-4 text-gray-400" />
              <span className="text-gray-700">{order.tecnico_responsavel}</span>
            </div>
          )}

          {order.equipment_localizacao && (
            <div className="flex items-center space-x-2 text-sm col-span-2">
              <MapPin className="w-4 h-4 text-gray-400" />
              <span className="text-gray-700">{order.equipment_localizacao}</span>
            </div>
          )}
        </div>

        {/* Time and Cost */}
        <div className="grid grid-cols-2 gap-4 pt-3 border-t border-gray-100">
          <div>
            <p className="text-xs text-gray-500 mb-1">Tempo Estimado</p>
            <div className="flex items-center space-x-1">
              <Clock className="w-4 h-4 text-gray-400" />
              <span className="text-sm font-medium text-gray-900">
                {order.tempo_estimado_horas || '-'} horas
              </span>
            </div>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Custo Estimado</p>
            <div className="flex items-center space-x-1">
              <DollarSign className="w-4 h-4 text-gray-400" />
              <span className="text-sm font-medium text-gray-900">
                {formatCurrency(order.custo_estimado)}
              </span>
            </div>
          </div>
        </div>

        {/* Checklist Progress */}
        {order.checklist && order.checklist.length > 0 && (
          <div className="pt-3 border-t border-gray-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-gray-500">Progresso do Checklist</span>
              <span className="text-xs font-medium text-gray-700">
                {order.checklist.filter(c => c.concluido).length}/{order.checklist.length}
              </span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-green-500 transition-all"
                style={{
                  width: `${(order.checklist.filter(c => c.concluido).length / order.checklist.length) * 100}%`
                }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-100 rounded-b-xl">
        <div className="flex items-center justify-between">
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${status.bgColor} ${status.color}`}>
            {status.label}
          </span>

          <div className="flex items-center space-x-2">
            {order.status === 'agendada' && onStart && (
              <button
                onClick={() => onStart(order)}
                className="flex items-center space-x-1.5 px-3 py-1.5 text-sm text-green-600 hover:bg-green-50 rounded-lg transition-colors"
              >
                <Play className="w-4 h-4" />
                <span>Iniciar</span>
              </button>
            )}

            {order.status === 'em_execucao' && onComplete && (
              <button
                onClick={() => onComplete(order)}
                className="flex items-center space-x-1.5 px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              >
                <CheckCircle className="w-4 h-4" />
                <span>Concluir</span>
              </button>
            )}

            <button
              onClick={() => onView?.(order)}
              className="px-4 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
            >
              Detalhes
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// Lista de ordens de manutencao
interface MaintenanceListProps {
  orders: MaintenanceOrder[];
  onSelectOrder?: (order: MaintenanceOrder) => void;
  emptyMessage?: string;
}

export function MaintenanceList({
  orders,
  onSelectOrder,
  emptyMessage = 'Nenhuma ordem de manutencao encontrada'
}: MaintenanceListProps) {
  if (orders.length === 0) {
    return (
      <div className="text-center py-8">
        <Wrench className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {orders.map((order, index) => (
        <motion.div
          key={order.id}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 }}
        >
          <MaintenanceCard
            order={order}
            onView={onSelectOrder}
            compact
          />
        </motion.div>
      ))}
    </div>
  );
}

export default MaintenanceCard;
