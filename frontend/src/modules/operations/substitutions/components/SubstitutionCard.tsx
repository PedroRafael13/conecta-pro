import React from 'react';
import { motion } from 'framer-motion';
import {
  User,
  ArrowRight,
  Clock,
  MapPin,
  Calendar,
  AlertTriangle,
  CheckCircle,
  XCircle,
  HelpCircle,
  RotateCcw,
  Eye,
  FileText,
  UserCheck,
} from 'lucide-react';
import type { Substitution, SubstitutionStatus, SubstitutionReason } from '../types/substitutions.types';

interface SubstitutionCardProps {
  substitution: Substitution;
  onView?: (substitution: Substitution) => void;
  onApprove?: (substitution: Substitution) => void;
  onReject?: (substitution: Substitution) => void;
  onAssignSubstitute?: (substitution: Substitution) => void;
  onClick?: (substitution: Substitution) => void;
  variant?: 'default' | 'compact' | 'detailed';
  showActions?: boolean;
}

export const SubstitutionCard: React.FC<SubstitutionCardProps> = ({
  substitution,
  onView,
  onApprove,
  onReject,
  onAssignSubstitute,
  onClick,
  variant = 'default',
  showActions = true,
}) => {
  const getStatusConfig = (status: SubstitutionStatus) => {
    const configs = {
      pendente: {
        color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
        bgColor: 'bg-yellow-50',
        icon: HelpCircle,
        iconColor: 'text-yellow-600',
        label: 'Pendente',
      },
      aprovada: {
        color: 'bg-green-100 text-green-800 border-green-200',
        bgColor: 'bg-green-50',
        icon: CheckCircle,
        iconColor: 'text-green-600',
        label: 'Aprovada',
      },
      rejeitada: {
        color: 'bg-red-100 text-red-800 border-red-200',
        bgColor: 'bg-red-50',
        icon: XCircle,
        iconColor: 'text-red-600',
        label: 'Rejeitada',
      },
      cancelada: {
        color: 'bg-gray-100 text-gray-800 border-gray-200',
        bgColor: 'bg-gray-50',
        icon: XCircle,
        iconColor: 'text-gray-600',
        label: 'Cancelada',
      },
      aguardando_substituto: {
        color: 'bg-blue-100 text-blue-800 border-blue-200',
        bgColor: 'bg-blue-50',
        icon: UserCheck,
        iconColor: 'text-blue-600',
        label: 'Aguardando Substituto',
      },
      substituto_confirmado: {
        color: 'bg-purple-100 text-purple-800 border-purple-200',
        bgColor: 'bg-purple-50',
        icon: RotateCcw,
        iconColor: 'text-purple-600',
        label: 'Substituto Confirmado',
      },
      concluida: {
        color: 'bg-green-100 text-green-800 border-green-200',
        bgColor: 'bg-green-50',
        icon: CheckCircle,
        iconColor: 'text-green-600',
        label: 'Concluida',
      },
    };
    return configs[status] || configs.pendente;
  };

  const getReasonConfig = (reason: SubstitutionReason) => {
    const configs = {
      atestado_medico: { label: 'Atestado Medico', icon: FileText },
      emergencia_pessoal: { label: 'Emergencia Pessoal', icon: AlertTriangle },
      problema_transporte: { label: 'Problema de Transporte', icon: MapPin },
      ferias: { label: 'Ferias', icon: Calendar },
      licenca: { label: 'Licenca', icon: FileText },
      folga_compensatoria: { label: 'Folga Compensatoria', icon: Clock },
      troca_turno: { label: 'Troca de Turno', icon: RotateCcw },
      outro: { label: 'Outro', icon: HelpCircle },
    };
    return configs[reason] || configs.outro;
  };

  const statusConfig = getStatusConfig(substitution.status);
  const reasonConfig = getReasonConfig(substitution.motivo);
  const StatusIcon = statusConfig.icon;
  const ReasonIcon = reasonConfig.icon;

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'short',
    });
  };

  // Versao Compacta
  if (variant === 'compact') {
    return (
      <motion.div
        whileHover={{ scale: 1.01 }}
        onClick={() => onClick?.(substitution)}
        className={`flex items-center gap-3 p-3 rounded-lg border border-gray-200 cursor-pointer hover:border-blue-300 transition-colors ${statusConfig.bgColor}`}
      >
        <div className={`p-2 rounded-lg ${statusConfig.color}`}>
          <StatusIcon className="w-4 h-4" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <p className="font-medium text-gray-900 text-sm truncate">
              {substitution.solicitante_nome}
            </p>
            {substitution.urgente && (
              <span className="px-1.5 py-0.5 bg-red-500 text-white text-xs rounded font-medium">
                URGENTE
              </span>
            )}
          </div>
          <p className="text-xs text-gray-500">
            {formatDate(substitution.data)} - {substitution.turno}
          </p>
        </div>

        <span
          className={`px-2 py-1 rounded-full text-xs font-medium border ${statusConfig.color}`}
        >
          {statusConfig.label}
        </span>
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
        {/* Header */}
        <div className={`px-4 py-3 ${statusConfig.bgColor} border-b border-gray-200`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <StatusIcon className={`w-5 h-5 ${statusConfig.iconColor}`} />
              <span className={`text-sm font-medium ${statusConfig.iconColor}`}>
                {statusConfig.label}
              </span>
              {substitution.urgente && (
                <span className="px-2 py-0.5 bg-red-500 text-white text-xs rounded-full font-medium">
                  URGENTE
                </span>
              )}
            </div>
            <span className="text-sm text-gray-500">
              {new Date(substitution.created_at).toLocaleString('pt-BR')}
            </span>
          </div>
        </div>

        {/* Conteudo */}
        <div className="p-4">
          {/* Solicitante -> Substituto */}
          <div className="flex items-center gap-4 mb-4">
            {/* Solicitante */}
            <div className="flex-1 bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-1">Solicitante</p>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                  {substitution.solicitante_avatar ? (
                    <img
                      src={substitution.solicitante_avatar}
                      alt={substitution.solicitante_nome}
                      className="w-8 h-8 rounded-full object-cover"
                    />
                  ) : (
                    <User className="w-4 h-4 text-gray-500" />
                  )}
                </div>
                <div>
                  <p className="font-medium text-gray-900 text-sm">
                    {substitution.solicitante_nome}
                  </p>
                  <p className="text-xs text-gray-500">
                    {substitution.solicitante_funcao}
                  </p>
                </div>
              </div>
            </div>

            <ArrowRight className="w-5 h-5 text-gray-400 flex-shrink-0" />

            {/* Substituto */}
            <div className="flex-1 bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500 mb-1">Substituto</p>
              {substitution.substituto_nome ? (
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                    {substitution.substituto_avatar ? (
                      <img
                        src={substitution.substituto_avatar}
                        alt={substitution.substituto_nome}
                        className="w-8 h-8 rounded-full object-cover"
                      />
                    ) : (
                      <User className="w-4 h-4 text-green-600" />
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 text-sm">
                      {substitution.substituto_nome}
                    </p>
                    <p className="text-xs text-gray-500">
                      {substitution.substituto_funcao}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-gray-400">
                  <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center border-2 border-dashed border-gray-300">
                    <User className="w-4 h-4" />
                  </div>
                  <span className="text-sm">Nao definido</span>
                </div>
              )}
            </div>
          </div>

          {/* Info Grid */}
          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="flex items-center gap-2 text-gray-600 mb-1">
                <MapPin className="w-4 h-4" />
                <span className="text-xs font-medium">Posto</span>
              </div>
              <p className="text-sm text-gray-900 font-medium truncate">
                {substitution.posto_nome}
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-3">
              <div className="flex items-center gap-2 text-gray-600 mb-1">
                <Calendar className="w-4 h-4" />
                <span className="text-xs font-medium">Data</span>
              </div>
              <p className="text-sm text-gray-900 font-medium">
                {formatDate(substitution.data)}
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-3">
              <div className="flex items-center gap-2 text-gray-600 mb-1">
                <Clock className="w-4 h-4" />
                <span className="text-xs font-medium">Horario</span>
              </div>
              <p className="text-sm text-gray-900 font-medium">
                {substitution.horario_inicio} - {substitution.horario_fim}
              </p>
            </div>
          </div>

          {/* Motivo */}
          <div className="bg-amber-50 rounded-lg p-3 mb-4">
            <div className="flex items-center gap-2 mb-1">
              <ReasonIcon className="w-4 h-4 text-amber-600" />
              <span className="text-sm font-medium text-amber-800">
                {reasonConfig.label}
              </span>
            </div>
            {substitution.motivo_descricao && (
              <p className="text-sm text-amber-700 mt-1">
                {substitution.motivo_descricao}
              </p>
            )}
          </div>

          {/* Documentos */}
          {substitution.documentos && substitution.documentos.length > 0 && (
            <div className="mb-4">
              <p className="text-xs font-medium text-gray-500 mb-2">
                Documentos Anexados
              </p>
              <div className="flex flex-wrap gap-2">
                {substitution.documentos.map((doc) => (
                  <a
                    key={doc.id}
                    href={doc.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1.5 px-2 py-1.5 bg-gray-100 rounded-lg text-xs text-gray-700 hover:bg-gray-200 transition-colors"
                  >
                    <FileText className="w-3.5 h-3.5" />
                    {doc.nome}
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* Motivo de rejeicao */}
          {substitution.status === 'rejeitada' && substitution.motivo_rejeicao && (
            <div className="bg-red-50 rounded-lg p-3 mb-4">
              <p className="text-xs font-medium text-red-600 mb-1">
                Motivo da Rejeicao
              </p>
              <p className="text-sm text-red-800">{substitution.motivo_rejeicao}</p>
            </div>
          )}
        </div>

        {/* Footer com acoes */}
        {showActions && substitution.status === 'pendente' && (
          <div className="px-4 py-3 border-t border-gray-200 bg-gray-50 flex gap-2">
            {onReject && (
              <button
                onClick={() => onReject(substitution)}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-white border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors text-sm font-medium"
              >
                <XCircle className="w-4 h-4" />
                Rejeitar
              </button>
            )}
            {onApprove && (
              <button
                onClick={() => onApprove(substitution)}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium"
              >
                <CheckCircle className="w-4 h-4" />
                Aprovar
              </button>
            )}
          </div>
        )}

        {showActions && substitution.status === 'aguardando_substituto' && onAssignSubstitute && (
          <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
            <button
              onClick={() => onAssignSubstitute(substitution)}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              <UserCheck className="w-4 h-4" />
              Atribuir Substituto
            </button>
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
      onClick={() => onClick?.(substitution)}
      className="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-all cursor-pointer overflow-hidden"
    >
      {/* Indicador de urgencia */}
      {substitution.urgente && (
        <div className="bg-red-500 text-white text-xs font-medium text-center py-1">
          URGENTE
        </div>
      )}

      <div className="p-4">
        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
              {substitution.solicitante_avatar ? (
                <img
                  src={substitution.solicitante_avatar}
                  alt={substitution.solicitante_nome}
                  className="w-10 h-10 rounded-full object-cover"
                />
              ) : (
                <User className="w-5 h-5 text-gray-500" />
              )}
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 text-sm">
                {substitution.solicitante_nome}
              </h4>
              <p className="text-xs text-gray-500">{substitution.solicitante_funcao}</p>
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
        <div className="space-y-2 mb-3">
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <MapPin className="w-4 h-4 text-gray-400" />
            <span className="truncate">{substitution.posto_nome}</span>
          </div>

          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Calendar className="w-4 h-4 text-gray-400" />
            <span>{formatDate(substitution.data)}</span>
            <span className="text-gray-400">|</span>
            <Clock className="w-4 h-4 text-gray-400" />
            <span>
              {substitution.horario_inicio} - {substitution.horario_fim}
            </span>
          </div>
        </div>

        {/* Motivo */}
        <div className="flex items-center gap-2 mb-3">
          <ReasonIcon className="w-4 h-4 text-amber-500" />
          <span className="text-sm text-gray-700">{reasonConfig.label}</span>
        </div>

        {/* Substituto */}
        {substitution.substituto_nome && (
          <div className="flex items-center gap-2 p-2 bg-green-50 rounded-lg">
            <ArrowRight className="w-4 h-4 text-green-600" />
            <span className="text-sm text-green-700 font-medium">
              {substitution.substituto_nome}
            </span>
          </div>
        )}

        {/* Actions */}
        {showActions && (
          <div className="mt-4 pt-3 border-t border-gray-100 flex items-center justify-between">
            <span className="text-xs text-gray-400">
              {new Date(substitution.created_at).toLocaleDateString('pt-BR')}
            </span>

            <div className="flex items-center gap-2">
              {onView && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onView(substitution);
                  }}
                  className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  title="Ver detalhes"
                >
                  <Eye className="w-4 h-4" />
                </button>
              )}

              {substitution.status === 'pendente' && onApprove && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onApprove(substitution);
                  }}
                  className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                  title="Aprovar"
                >
                  <CheckCircle className="w-4 h-4" />
                </button>
              )}

              {substitution.status === 'pendente' && onReject && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onReject(substitution);
                  }}
                  className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  title="Rejeitar"
                >
                  <XCircle className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default SubstitutionCard;
