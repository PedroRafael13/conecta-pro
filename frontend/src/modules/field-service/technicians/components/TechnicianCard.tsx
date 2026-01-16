'use client';

import { motion } from 'framer-motion';
import {
  Phone,
  Mail,
  MapPin,
  Star,
  Briefcase,
  Car,
  ChevronRight,
} from 'lucide-react';
import { Card } from '@/core/components/ui';
import { Badge } from '@/core/components/ui';
import { Avatar } from '@/core/components/ui';
import type { Technician, StatusTecnico } from '../../types';
import { STATUS_TECNICO_CONFIG } from '../../types';

export interface TechnicianCardProps {
  technician: Technician;
  onClick?: (technician: Technician) => void;
  showDetails?: boolean;
  compact?: boolean;
  className?: string;
}

// Variante de badge por status
const statusBadgeVariant: Record<StatusTecnico, 'success' | 'danger' | 'info' | 'default'> = {
  disponivel: 'success',
  ocupado: 'danger',
  em_deslocamento: 'info',
  offline: 'default',
};

export function TechnicianCard({
  technician,
  onClick,
  showDetails = true,
  compact = false,
  className = '',
}: TechnicianCardProps) {
  const statusConfig = STATUS_TECNICO_CONFIG[technician.status];

  // Gerar iniciais do nome
  const initials = technician.nome
    .split(' ')
    .map(n => n[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();

  // Renderizar estrelas de rating
  const renderRating = (rating: number) => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-3.5 h-3.5 ${
              star <= rating
                ? 'text-yellow-400 fill-yellow-400'
                : star <= rating + 0.5
                ? 'text-yellow-400 fill-yellow-400/50'
                : 'text-gray-300'
            }`}
          />
        ))}
        <span className="text-sm text-gray-600 ml-1">{rating.toFixed(1)}</span>
      </div>
    );
  };

  // Versão compacta para listas
  if (compact) {
    return (
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        whileHover={{ scale: onClick ? 1.02 : 1 }}
      >
        <div
          className={`flex items-center gap-3 p-3 bg-white rounded-lg border border-gray-200
            ${onClick ? 'cursor-pointer hover:border-gray-300 hover:shadow-sm transition-all' : ''}
            ${className}`}
          onClick={() => onClick?.(technician)}
        >
          {/* Avatar com status */}
          <div className="relative">
            <Avatar
              name={technician.nome}
              src={technician.avatar}
              size="md"
            />
            <span
              className={`absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white
                ${statusConfig.dotColor}`}
            />
          </div>

          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-medium text-gray-900 truncate">
                {technician.nome}
              </span>
              <Badge variant={statusBadgeVariant[technician.status]} size="sm">
                {statusConfig.label}
              </Badge>
            </div>
            <div className="flex items-center gap-3 text-sm text-gray-500">
              <span>{technician.ordens_hoje} ordens hoje</span>
              <span className="flex items-center gap-1">
                <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" />
                {technician.rating.toFixed(1)}
              </span>
            </div>
          </div>

          {onClick && <ChevronRight className="w-5 h-5 text-gray-400" />}
        </div>
      </motion.div>
    );
  }

  // Versão completa
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: onClick ? 1.01 : 1 }}
      transition={{ duration: 0.2 }}
    >
      <Card
        className={`${onClick ? 'cursor-pointer hover:shadow-lg transition-shadow' : ''} ${className}`}
        onClick={() => onClick?.(technician)}
        padding="none"
      >
        {/* Header */}
        <div className="p-4 border-b border-gray-100">
          <div className="flex items-start gap-4">
            {/* Avatar com status */}
            <div className="relative">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-blue-600
                flex items-center justify-center text-white text-xl font-semibold">
                {technician.avatar ? (
                  <img
                    src={technician.avatar}
                    alt={technician.nome}
                    className="w-full h-full rounded-full object-cover"
                  />
                ) : (
                  initials
                )}
              </div>
              <span
                className={`absolute bottom-0 right-0 w-4 h-4 rounded-full border-2 border-white
                  ${statusConfig.dotColor}`}
              />
            </div>

            {/* Info */}
            <div className="flex-1">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h3 className="font-semibold text-gray-900">{technician.nome}</h3>
                  <Badge variant={statusBadgeVariant[technician.status]} size="sm" className="mt-1">
                    {statusConfig.label}
                  </Badge>
                </div>
                {onClick && <ChevronRight className="w-5 h-5 text-gray-400" />}
              </div>
              <div className="mt-2">
                {renderRating(technician.rating)}
              </div>
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="p-4 space-y-3">
          {/* Especialidades */}
          <div>
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">
              Especialidades
            </span>
            <div className="flex flex-wrap gap-1.5 mt-1.5">
              {technician.especialidades.map((esp) => (
                <span
                  key={esp}
                  className="px-2 py-0.5 text-xs bg-gray-100 text-gray-700 rounded-full"
                >
                  {esp}
                </span>
              ))}
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 gap-3 pt-2 border-t border-gray-100">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center">
                <Briefcase className="w-4 h-4 text-blue-600" />
              </div>
              <div>
                <div className="text-lg font-semibold text-gray-900">
                  {technician.ordens_hoje}
                </div>
                <div className="text-xs text-gray-500">Ordens hoje</div>
              </div>
            </div>

            {technician.veiculo && (
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-green-50 flex items-center justify-center">
                  <Car className="w-4 h-4 text-green-600" />
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-900 truncate">
                    {technician.veiculo}
                  </div>
                  <div className="text-xs text-gray-500">{technician.placa_veiculo}</div>
                </div>
              </div>
            )}
          </div>

          {/* Localização */}
          {technician.localizacao?.endereco && (
            <div className="flex items-start gap-2 p-2 bg-gray-50 rounded-lg">
              <MapPin className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
              <span className="text-sm text-gray-600 line-clamp-2">
                {technician.localizacao.endereco}
              </span>
            </div>
          )}

          {/* Contato */}
          {showDetails && (
            <div className="flex items-center gap-4 pt-2 border-t border-gray-100">
              {technician.telefone && (
                <a
                  href={`tel:${technician.telefone}`}
                  className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-blue-600 transition-colors"
                  onClick={(e) => e.stopPropagation()}
                >
                  <Phone className="w-4 h-4" />
                  {technician.telefone}
                </a>
              )}
              {technician.email && (
                <a
                  href={`mailto:${technician.email}`}
                  className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-blue-600 transition-colors truncate"
                  onClick={(e) => e.stopPropagation()}
                >
                  <Mail className="w-4 h-4 flex-shrink-0" />
                  <span className="truncate">{technician.email}</span>
                </a>
              )}
            </div>
          )}
        </div>
      </Card>
    </motion.div>
  );
}

export default TechnicianCard;
