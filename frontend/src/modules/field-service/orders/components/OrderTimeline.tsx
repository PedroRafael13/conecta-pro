'use client';

import { useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  FileText,
  UserCheck,
  Navigation,
  MapPin,
  Play,
  CheckCircle,
  XCircle,
  Clock,
} from 'lucide-react';
import type { OrderTimelineEvent } from '../../types';

export interface OrderTimelineProps {
  events: OrderTimelineEvent[];
  className?: string;
}

// Configuração de ícones e cores por tipo de evento
const eventConfig: Record<OrderTimelineEvent['tipo'], {
  icon: React.ReactNode;
  color: string;
  bgColor: string;
  label: string;
}> = {
  abertura: {
    icon: <FileText className="w-4 h-4" />,
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
    label: 'Ordem Aberta',
  },
  atribuicao: {
    icon: <UserCheck className="w-4 h-4" />,
    color: 'text-purple-600',
    bgColor: 'bg-purple-100',
    label: 'Técnico Atribuído',
  },
  deslocamento: {
    icon: <Navigation className="w-4 h-4" />,
    color: 'text-orange-600',
    bgColor: 'bg-orange-100',
    label: 'Em Deslocamento',
  },
  chegada: {
    icon: <MapPin className="w-4 h-4" />,
    color: 'text-teal-600',
    bgColor: 'bg-teal-100',
    label: 'Chegada no Local',
  },
  inicio_atendimento: {
    icon: <Play className="w-4 h-4" />,
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-100',
    label: 'Atendimento Iniciado',
  },
  conclusao: {
    icon: <CheckCircle className="w-4 h-4" />,
    color: 'text-green-600',
    bgColor: 'bg-green-100',
    label: 'Concluído',
  },
  cancelamento: {
    icon: <XCircle className="w-4 h-4" />,
    color: 'text-red-600',
    bgColor: 'bg-red-100',
    label: 'Cancelado',
  },
};

export function OrderTimeline({ events, className = '' }: OrderTimelineProps) {
  // Ordenar eventos por data (mais recente primeiro)
  const sortedEvents = useMemo(() => {
    return [...events].sort((a, b) =>
      new Date(b.data).getTime() - new Date(a.data).getTime()
    );
  }, [events]);

  // Formatação de data/hora
  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return {
      date: date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      }),
      time: date.toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit',
      }),
    };
  };

  // Calcular tempo entre eventos
  const getTimeDiff = (current: string, previous: string | undefined): string | null => {
    if (!previous) return null;
    const diff = new Date(current).getTime() - new Date(previous).getTime();
    const minutes = Math.round(diff / (1000 * 60));

    if (minutes < 60) return `${minutes}min`;
    if (minutes < 1440) return `${Math.round(minutes / 60)}h`;
    return `${Math.round(minutes / 1440)}d`;
  };

  if (events.length === 0) {
    return (
      <div className={`text-center py-8 text-gray-500 ${className}`}>
        <Clock className="w-8 h-8 mx-auto mb-2 text-gray-300" />
        <p>Nenhum evento registrado</p>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      {/* Linha vertical */}
      <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-gray-200" />

      <div className="space-y-0">
        {sortedEvents.map((event, index) => {
          const config = eventConfig[event.tipo];
          const { date, time } = formatDateTime(event.data);
          const nextEvent = sortedEvents[index + 1];
          const timeDiff = nextEvent ? getTimeDiff(event.data, nextEvent.data) : null;

          return (
            <motion.div
              key={event.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="relative pl-12 pb-6"
            >
              {/* Ícone do evento */}
              <div className={`absolute left-0 w-10 h-10 rounded-full ${config.bgColor}
                flex items-center justify-center ${config.color} ring-4 ring-white z-10`}
              >
                {config.icon}
              </div>

              {/* Conteúdo do evento */}
              <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm">
                {/* Header */}
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div>
                    <span className={`font-semibold ${config.color}`}>
                      {config.label}
                    </span>
                    {event.usuario && (
                      <span className="text-sm text-gray-500 ml-2">
                        por {event.usuario}
                      </span>
                    )}
                  </div>
                  <div className="text-right text-sm text-gray-500 whitespace-nowrap">
                    <div className="font-medium">{time}</div>
                    <div>{date}</div>
                  </div>
                </div>

                {/* Descrição */}
                <p className="text-sm text-gray-600">{event.descricao}</p>

                {/* Detalhes adicionais */}
                {event.detalhes && Object.keys(event.detalhes).length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-100">
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(event.detalhes).map(([key, value]) => (
                        <span
                          key={key}
                          className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded"
                        >
                          {key}: {String(value)}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Tempo entre eventos */}
              {timeDiff && (
                <div className="absolute left-3.5 -bottom-1 text-xs text-gray-400 bg-white px-1">
                  {timeDiff}
                </div>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

// Versão compacta para cards
export function OrderTimelineCompact({ events, className = '' }: OrderTimelineProps) {
  const sortedEvents = useMemo(() => {
    return [...events].sort((a, b) =>
      new Date(a.data).getTime() - new Date(b.data).getTime()
    );
  }, [events]);

  if (events.length === 0) return null;

  return (
    <div className={`flex items-center gap-1 overflow-x-auto ${className}`}>
      {sortedEvents.map((event, index) => {
        const config = eventConfig[event.tipo];
        const isLast = index === sortedEvents.length - 1;

        return (
          <div key={event.id} className="flex items-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className={`w-6 h-6 rounded-full ${config.bgColor} ${config.color}
                flex items-center justify-center flex-shrink-0`}
              title={`${config.label} - ${new Date(event.data).toLocaleString('pt-BR')}`}
            >
              {config.icon}
            </motion.div>
            {!isLast && (
              <div className="w-4 h-0.5 bg-gray-300 mx-0.5" />
            )}
          </div>
        );
      })}
    </div>
  );
}

export default OrderTimeline;
