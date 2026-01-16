'use client';

import { useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  Clock,
  MapPin,
  User,
  Phone,
  AlertTriangle,
  Wrench,
  Package,
  ClipboardCheck,
  ChevronRight,
} from 'lucide-react';
import { Card } from '@/core/components/ui';
import { Badge } from '@/core/components/ui';
import type {
  ServiceOrder,
  TipoServico,
  PrioridadeServico,
  StatusOrdem
} from '../../types';
import {
  PRIORIDADE_CONFIG,
  STATUS_ORDEM_CONFIG,
  TIPO_SERVICO_CONFIG
} from '../../types';

export interface ServiceOrderCardProps {
  order: ServiceOrder;
  onClick?: (order: ServiceOrder) => void;
  showDetails?: boolean;
  className?: string;
}

// Ícones por tipo de serviço
const tipoIcons: Record<TipoServico, React.ReactNode> = {
  instalacao: <Package className="w-4 h-4" />,
  manutencao: <Wrench className="w-4 h-4" />,
  reparo: <AlertTriangle className="w-4 h-4" />,
  inspecao: <ClipboardCheck className="w-4 h-4" />,
};

// Variante de badge por prioridade
const prioridadeBadgeVariant: Record<PrioridadeServico, 'danger' | 'warning' | 'info' | 'default'> = {
  urgente: 'danger',
  alta: 'warning',
  normal: 'info',
  baixa: 'default',
};

// Variante de badge por status
const statusBadgeVariant: Record<StatusOrdem, 'warning' | 'info' | 'success' | 'default'> = {
  aberta: 'warning',
  em_atendimento: 'info',
  concluida: 'success',
  cancelada: 'default',
};

export function ServiceOrderCard({
  order,
  onClick,
  showDetails = true,
  className = '',
}: ServiceOrderCardProps) {
  // Cálculo do SLA
  const slaInfo = useMemo(() => {
    const abertura = new Date(order.data_abertura);
    const agora = new Date();
    const horasPassadas = (agora.getTime() - abertura.getTime()) / (1000 * 60 * 60);
    const horasRestantes = order.sla_horas - horasPassadas;
    const percentual = Math.min(100, (horasPassadas / order.sla_horas) * 100);

    let status: 'ok' | 'warning' | 'critical' = 'ok';
    if (horasRestantes <= 0) {
      status = 'critical';
    } else if (horasRestantes <= order.sla_horas * 0.25) {
      status = 'warning';
    }

    return {
      horasRestantes: Math.max(0, horasRestantes),
      percentual,
      status,
      expirado: horasRestantes <= 0,
    };
  }, [order.data_abertura, order.sla_horas]);

  // Formatação de data
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Formatação de horas restantes
  const formatHorasRestantes = (horas: number) => {
    if (horas < 1) {
      return `${Math.round(horas * 60)}min`;
    }
    if (horas < 24) {
      return `${Math.round(horas)}h`;
    }
    return `${Math.round(horas / 24)}d`;
  };

  const prioridadeConfig = PRIORIDADE_CONFIG[order.prioridade];
  const statusConfig = STATUS_ORDEM_CONFIG[order.status];
  const tipoConfig = TIPO_SERVICO_CONFIG[order.tipo];

  // Não mostrar SLA para ordens concluídas ou canceladas
  const showSLA = order.status !== 'concluida' && order.status !== 'cancelada';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: onClick ? 1.01 : 1 }}
      transition={{ duration: 0.2 }}
    >
      <Card
        className={`${onClick ? 'cursor-pointer hover:shadow-lg transition-shadow' : ''} ${className}`}
        onClick={() => onClick?.(order)}
        padding="none"
      >
        {/* Header */}
        <div className="p-4 border-b border-gray-100">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-2">
              <div className={`p-2 rounded-lg ${prioridadeConfig.bgColor}`}>
                {tipoIcons[order.tipo]}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-gray-900">{order.numero}</span>
                  <Badge variant={prioridadeBadgeVariant[order.prioridade]} size="sm">
                    {prioridadeConfig.label}
                  </Badge>
                </div>
                <span className="text-sm text-gray-500">{tipoConfig.label}</span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Badge variant={statusBadgeVariant[order.status]}>
                {statusConfig.label}
              </Badge>
              {onClick && <ChevronRight className="w-5 h-5 text-gray-400" />}
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="p-4 space-y-3">
          {/* Cliente e Endereço */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-gray-700">
              <User className="w-4 h-4 text-gray-400 flex-shrink-0" />
              <span className="font-medium truncate">{order.cliente}</span>
            </div>
            <div className="flex items-start gap-2 text-gray-600">
              <MapPin className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" />
              <span className="text-sm line-clamp-2">{order.endereco}</span>
            </div>
          </div>

          {/* Descrição */}
          {showDetails && (
            <p className="text-sm text-gray-600 line-clamp-2 border-t border-gray-100 pt-3">
              {order.descricao}
            </p>
          )}

          {/* Técnico atribuído */}
          {order.tecnico_nome && (
            <div className="flex items-center gap-2 p-2 bg-blue-50 rounded-lg">
              <div className="w-6 h-6 rounded-full bg-blue-200 flex items-center justify-center">
                <User className="w-3 h-3 text-blue-700" />
              </div>
              <span className="text-sm text-blue-700 font-medium">
                {order.tecnico_nome}
              </span>
            </div>
          )}

          {/* Contato */}
          {showDetails && order.telefone_cliente && (
            <div className="flex items-center gap-2 text-gray-600">
              <Phone className="w-4 h-4 text-gray-400" />
              <span className="text-sm">{order.telefone_cliente}</span>
            </div>
          )}
        </div>

        {/* Footer - SLA */}
        {showSLA && (
          <div className="px-4 pb-4">
            <div className="p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Clock className={`w-4 h-4 ${
                    slaInfo.status === 'critical' ? 'text-red-500' :
                    slaInfo.status === 'warning' ? 'text-yellow-500' :
                    'text-green-500'
                  }`} />
                  <span className="text-sm font-medium text-gray-700">SLA</span>
                </div>
                <span className={`text-sm font-semibold ${
                  slaInfo.status === 'critical' ? 'text-red-600' :
                  slaInfo.status === 'warning' ? 'text-yellow-600' :
                  'text-green-600'
                }`}>
                  {slaInfo.expirado
                    ? 'Expirado'
                    : `${formatHorasRestantes(slaInfo.horasRestantes)} restantes`
                  }
                </span>
              </div>

              {/* Progress bar */}
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <motion.div
                  className={`h-full rounded-full ${
                    slaInfo.status === 'critical' ? 'bg-red-500' :
                    slaInfo.status === 'warning' ? 'bg-yellow-500' :
                    'bg-green-500'
                  }`}
                  initial={{ width: 0 }}
                  animate={{ width: `${slaInfo.percentual}%` }}
                  transition={{ duration: 0.5, ease: 'easeOut' }}
                />
              </div>

              {/* Data de abertura */}
              <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                <span>Aberto: {formatDate(order.data_abertura)}</span>
                {order.data_agendamento && (
                  <span>Agendado: {formatDate(order.data_agendamento)}</span>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Footer - Ordem concluída */}
        {order.status === 'concluida' && order.data_conclusao && (
          <div className="px-4 pb-4">
            <div className="p-3 bg-green-50 rounded-lg">
              <div className="flex items-center gap-2">
                <ClipboardCheck className="w-4 h-4 text-green-600" />
                <span className="text-sm text-green-700">
                  Concluído em {formatDate(order.data_conclusao)}
                </span>
              </div>
            </div>
          </div>
        )}
      </Card>
    </motion.div>
  );
}

export default ServiceOrderCard;
