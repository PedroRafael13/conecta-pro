'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  Package,
  Wrench,
  ArrowRightLeft,
  Power,
  Trash2,
  FileText,
  DollarSign,
  User,
  Calendar
} from 'lucide-react';
import type { EquipmentLifecycleEvent } from '../types/equipment.types';

interface LifecycleTimelineProps {
  events: EquipmentLifecycleEvent[];
  isLoading?: boolean;
}

const eventTypeConfig: Record<EquipmentLifecycleEvent['tipo'], {
  label: string;
  icon: React.ElementType;
  color: string;
  bgColor: string;
  borderColor: string;
}> = {
  aquisicao: {
    label: 'Aquisicao',
    icon: Package,
    color: 'text-green-600',
    bgColor: 'bg-green-100',
    borderColor: 'border-green-200'
  },
  manutencao: {
    label: 'Manutencao',
    icon: Wrench,
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
    borderColor: 'border-blue-200'
  },
  transferencia: {
    label: 'Transferencia',
    icon: ArrowRightLeft,
    color: 'text-purple-600',
    bgColor: 'bg-purple-100',
    borderColor: 'border-purple-200'
  },
  inativacao: {
    label: 'Inativacao',
    icon: Power,
    color: 'text-amber-600',
    bgColor: 'bg-amber-100',
    borderColor: 'border-amber-200'
  },
  descarte: {
    label: 'Descarte',
    icon: Trash2,
    color: 'text-red-600',
    bgColor: 'bg-red-100',
    borderColor: 'border-red-200'
  }
};

export function LifecycleTimeline({ events, isLoading }: LifecycleTimelineProps) {
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const formatCurrency = (value?: number) => {
    if (!value) return null;
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex space-x-4 animate-pulse">
            <div className="w-10 h-10 rounded-full bg-gray-200" />
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-1/3" />
              <div className="h-3 bg-gray-200 rounded w-2/3" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="text-center py-8">
        <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500">Nenhum evento registrado</p>
      </div>
    );
  }

  // Ordenar eventos por data (mais recente primeiro)
  const sortedEvents = [...events].sort(
    (a, b) => new Date(b.data).getTime() - new Date(a.data).getTime()
  );

  return (
    <div className="relative">
      {/* Timeline line */}
      <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-gray-200" />

      <div className="space-y-6">
        {sortedEvents.map((event, index) => {
          const config = eventTypeConfig[event.tipo];
          const Icon = config.icon;

          return (
            <motion.div
              key={event.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="relative flex items-start space-x-4"
            >
              {/* Icon */}
              <div
                className={`relative z-10 flex items-center justify-center w-10 h-10 rounded-full ${config.bgColor} ${config.borderColor} border-2`}
              >
                <Icon className={`w-5 h-5 ${config.color}`} />
              </div>

              {/* Content */}
              <div className="flex-1 bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${config.bgColor} ${config.color}`}>
                        {config.label}
                      </span>
                      <span className="flex items-center text-xs text-gray-500">
                        <Calendar className="w-3 h-3 mr-1" />
                        {formatDate(event.data)}
                      </span>
                    </div>
                    <p className="mt-2 text-sm text-gray-700">{event.descricao}</p>
                  </div>

                  {event.custo && (
                    <div className="flex items-center space-x-1 text-sm font-medium text-gray-700">
                      <DollarSign className="w-4 h-4 text-gray-400" />
                      <span>{formatCurrency(event.custo)}</span>
                    </div>
                  )}
                </div>

                {/* Additional info */}
                <div className="mt-3 flex items-center space-x-4 text-xs text-gray-500">
                  {event.responsavel && (
                    <div className="flex items-center space-x-1">
                      <User className="w-3 h-3" />
                      <span>{event.responsavel}</span>
                    </div>
                  )}

                  {event.documentos && event.documentos.length > 0 && (
                    <div className="flex items-center space-x-1">
                      <FileText className="w-3 h-3" />
                      <span>{event.documentos.length} documento(s)</span>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Timeline end marker */}
      <div className="absolute left-5 bottom-0 transform translate-x-[-4px]">
        <div className="w-3 h-3 rounded-full bg-gray-300" />
      </div>
    </div>
  );
}

// Componente de resumo do ciclo de vida
interface LifecycleSummaryProps {
  totalEvents: number;
  totalCost: number;
  lastEventDate?: string;
  acquisitionDate?: string;
}

export function LifecycleSummary({
  totalEvents,
  totalCost,
  lastEventDate,
  acquisitionDate
}: LifecycleSummaryProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('pt-BR');
  };

  const calculateAge = (dateStr?: string) => {
    if (!dateStr) return '-';
    const acquisition = new Date(dateStr);
    const now = new Date();
    const years = Math.floor((now.getTime() - acquisition.getTime()) / (365.25 * 24 * 60 * 60 * 1000));
    const months = Math.floor(((now.getTime() - acquisition.getTime()) % (365.25 * 24 * 60 * 60 * 1000)) / (30.44 * 24 * 60 * 60 * 1000));

    if (years === 0) return `${months} meses`;
    if (months === 0) return `${years} anos`;
    return `${years} anos e ${months} meses`;
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="bg-gray-50 rounded-lg p-3">
        <p className="text-xs text-gray-500 mb-1">Total de Eventos</p>
        <p className="text-xl font-bold text-gray-900">{totalEvents}</p>
      </div>

      <div className="bg-gray-50 rounded-lg p-3">
        <p className="text-xs text-gray-500 mb-1">Custo Total</p>
        <p className="text-xl font-bold text-gray-900">{formatCurrency(totalCost)}</p>
      </div>

      <div className="bg-gray-50 rounded-lg p-3">
        <p className="text-xs text-gray-500 mb-1">Idade do Equipamento</p>
        <p className="text-xl font-bold text-gray-900">{calculateAge(acquisitionDate)}</p>
      </div>

      <div className="bg-gray-50 rounded-lg p-3">
        <p className="text-xs text-gray-500 mb-1">Ultima Atividade</p>
        <p className="text-xl font-bold text-gray-900">{formatDate(lastEventDate)}</p>
      </div>
    </div>
  );
}

export default LifecycleTimeline;
