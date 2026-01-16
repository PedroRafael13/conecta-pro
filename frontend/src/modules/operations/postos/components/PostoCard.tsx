import React from 'react';
import { motion } from 'framer-motion';
import {
  MapPin,
  Users,
  Clock,
  Building2,
  Phone,
  Mail,
  MoreVertical,
  Edit,
  Trash2,
  Eye,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Pause,
} from 'lucide-react';
import type { Posto, PostoStatus } from '../types/postos.types';

interface PostoCardProps {
  posto: Posto;
  onView?: (posto: Posto) => void;
  onEdit?: (posto: Posto) => void;
  onDelete?: (posto: Posto) => void;
  onClick?: (posto: Posto) => void;
}

export const PostoCard: React.FC<PostoCardProps> = ({
  posto,
  onView,
  onEdit,
  onDelete,
  onClick,
}) => {
  const getStatusConfig = (status: PostoStatus) => {
    const configs = {
      ativo: {
        color: 'bg-green-100 text-green-800 border-green-200',
        icon: CheckCircle,
        label: 'Ativo',
      },
      inativo: {
        color: 'bg-gray-100 text-gray-800 border-gray-200',
        icon: XCircle,
        label: 'Inativo',
      },
      em_implantacao: {
        color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
        icon: AlertTriangle,
        label: 'Em Implantacao',
      },
      suspenso: {
        color: 'bg-red-100 text-red-800 border-red-200',
        icon: Pause,
        label: 'Suspenso',
      },
    };
    return configs[status] || configs.inativo;
  };

  const statusConfig = getStatusConfig(posto.status);
  const StatusIcon = statusConfig.icon;

  // Calcular ocupacao total
  const totalAlocados = posto.turnos.reduce(
    (acc, t) => acc + t.profissionais_alocados,
    0
  );
  const totalNecessarios = posto.turnos.reduce(
    (acc, t) => acc + t.profissionais_necessarios,
    0
  );
  const taxaOcupacao =
    totalNecessarios > 0 ? (totalAlocados / totalNecessarios) * 100 : 0;

  const getOcupacaoColor = () => {
    if (taxaOcupacao >= 100) return 'bg-green-500';
    if (taxaOcupacao >= 75) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      transition={{ duration: 0.2 }}
      className="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-all cursor-pointer overflow-hidden"
      onClick={() => onClick?.(posto)}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="font-semibold text-gray-900 truncate">
                {posto.nome}
              </h3>
              <span
                className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${statusConfig.color}`}
              >
                <StatusIcon className="w-3 h-3" />
                {statusConfig.label}
              </span>
            </div>
            <p className="text-sm text-gray-500 truncate flex items-center gap-1">
              <Building2 className="w-4 h-4 flex-shrink-0" />
              {posto.cliente}
            </p>
          </div>

          {/* Actions Menu */}
          <div className="relative group ml-2">
            <button
              onClick={(e) => e.stopPropagation()}
              className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <MoreVertical className="w-4 h-4" />
            </button>

            <div className="absolute right-0 top-8 w-44 bg-white rounded-lg shadow-lg border border-gray-200 z-20 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
              <div className="py-1">
                {onView && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onView(posto);
                    }}
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    Ver Detalhes
                  </button>
                )}
                {onEdit && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onEdit(posto);
                    }}
                    className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Editar
                  </button>
                )}
                {onDelete && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(posto);
                    }}
                    className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Excluir
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Endereco */}
        <div className="flex items-start gap-1.5 mt-3 text-sm text-gray-600">
          <MapPin className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span className="line-clamp-2">{posto.endereco}</span>
        </div>
      </div>

      {/* Turnos Info */}
      <div className="p-4 bg-gray-50">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-gray-700">
            Ocupacao de Turnos
          </span>
          <span className="text-sm font-semibold text-gray-900">
            {totalAlocados}/{totalNecessarios}
          </span>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${Math.min(taxaOcupacao, 100)}%` }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className={`h-2 rounded-full ${getOcupacaoColor()}`}
          />
        </div>

        {/* Turnos List */}
        <div className="space-y-2">
          {posto.turnos.slice(0, 3).map((turno) => (
            <div
              key={turno.id}
              className="flex items-center justify-between text-sm"
            >
              <div className="flex items-center gap-2 text-gray-600">
                <Clock className="w-3.5 h-3.5" />
                <span className="truncate max-w-[120px]">{turno.nome}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Users className="w-3.5 h-3.5 text-gray-400" />
                <span
                  className={`font-medium ${
                    turno.profissionais_alocados >= turno.profissionais_necessarios
                      ? 'text-green-600'
                      : 'text-orange-600'
                  }`}
                >
                  {turno.profissionais_alocados}/{turno.profissionais_necessarios}
                </span>
              </div>
            </div>
          ))}
          {posto.turnos.length > 3 && (
            <p className="text-xs text-gray-500 text-center pt-1">
              +{posto.turnos.length - 3} turno(s)
            </p>
          )}
          {posto.turnos.length === 0 && (
            <p className="text-xs text-gray-400 text-center py-2">
              Nenhum turno configurado
            </p>
          )}
        </div>
      </div>

      {/* Footer - Contato */}
      {posto.contato_responsavel && (
        <div className="px-4 py-3 border-t border-gray-100">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center gap-1.5 truncate">
              <Phone className="w-3.5 h-3.5" />
              <span>{posto.contato_responsavel.telefone}</span>
            </div>
            {posto.contato_responsavel.email && (
              <div className="flex items-center gap-1.5 truncate ml-2">
                <Mail className="w-3.5 h-3.5" />
                <span className="truncate max-w-[100px]">
                  {posto.contato_responsavel.email}
                </span>
              </div>
            )}
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default PostoCard;
