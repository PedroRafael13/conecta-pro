'use client';

import { motion } from 'framer-motion';
import { clsx } from 'clsx';
import { CheckCircle, XCircle, Clock, Edit2, Trash2, Eye, RotateCcw } from 'lucide-react';
import { ComplianceStatusBadge, ConsentStatus } from './ComplianceStatusBadge';

interface ConsentCardProps {
  id: string;
  title: string;
  description: string;
  purpose: string;
  status: ConsentStatus;
  consentDate?: Date;
  expirationDate?: Date;
  lastUpdated?: Date;
  dataCategories: string[];
  legalBasis: string;
  onView?: (id: string) => void;
  onEdit?: (id: string) => void;
  onRevoke?: (id: string) => void;
  onRenew?: (id: string) => void;
  onDelete?: (id: string) => void;
  className?: string;
}

function formatDate(date: Date): string {
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

function isExpiringSoon(date: Date, daysThreshold: number = 30): boolean {
  const now = new Date();
  const diffTime = date.getTime() - now.getTime();
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  return diffDays > 0 && diffDays <= daysThreshold;
}

export function ConsentCard({
  id,
  title,
  description,
  purpose,
  status,
  consentDate,
  expirationDate,
  lastUpdated,
  dataCategories,
  legalBasis,
  onView,
  onEdit,
  onRevoke,
  onRenew,
  onDelete,
  className,
}: ConsentCardProps) {
  const isExpiring = expirationDate && isExpiringSoon(expirationDate);
  const isExpired = expirationDate && new Date() > expirationDate;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={clsx(
        'bg-white rounded-xl border shadow-sm overflow-hidden',
        'hover:shadow-md transition-shadow duration-200',
        isExpiring && !isExpired && 'border-yellow-300',
        isExpired && 'border-red-300',
        !isExpiring && !isExpired && 'border-gray-200',
        className
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <h3 className="text-lg font-semibold text-[#0A2540] truncate">
                {title}
              </h3>
              <ComplianceStatusBadge status={status} size="sm" />
            </div>
            <p className="text-sm text-gray-600 line-clamp-2">{description}</p>
          </div>

          {/* Status Icon */}
          <div className="flex-shrink-0">
            {status === 'active' && (
              <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-green-600" />
              </div>
            )}
            {status === 'revoked' && (
              <div className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
                <XCircle className="w-5 h-5 text-red-600" />
              </div>
            )}
            {status === 'pending' && (
              <div className="w-10 h-10 rounded-full bg-yellow-100 flex items-center justify-center">
                <Clock className="w-5 h-5 text-yellow-600" />
              </div>
            )}
            {status === 'expired' && (
              <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                <XCircle className="w-5 h-5 text-gray-600" />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="p-4 space-y-4">
        {/* Purpose */}
        <div>
          <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
            Finalidade
          </span>
          <p className="text-sm text-gray-700 mt-1">{purpose}</p>
        </div>

        {/* Legal Basis */}
        <div>
          <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
            Base Legal
          </span>
          <p className="text-sm text-gray-700 mt-1">{legalBasis}</p>
        </div>

        {/* Data Categories */}
        <div>
          <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
            Categorias de Dados
          </span>
          <div className="flex flex-wrap gap-1.5 mt-2">
            {dataCategories.map((category) => (
              <span
                key={category}
                className="px-2 py-0.5 text-xs font-medium bg-[#0A2540]/10 text-[#0A2540] rounded-full"
              >
                {category}
              </span>
            ))}
          </div>
        </div>

        {/* Dates */}
        <div className="grid grid-cols-2 gap-4 pt-2">
          {consentDate && (
            <div>
              <span className="text-xs text-gray-500">Data do Consentimento</span>
              <p className="text-sm font-medium text-gray-700">{formatDate(consentDate)}</p>
            </div>
          )}
          {expirationDate && (
            <div>
              <span className="text-xs text-gray-500">Validade</span>
              <p
                className={clsx(
                  'text-sm font-medium',
                  isExpired ? 'text-red-600' : isExpiring ? 'text-yellow-600' : 'text-gray-700'
                )}
              >
                {formatDate(expirationDate)}
                {isExpiring && !isExpired && ' (expirando)'}
                {isExpired && ' (expirado)'}
              </p>
            </div>
          )}
        </div>

        {lastUpdated && (
          <p className="text-xs text-gray-400">
            Ultima atualizacao: {formatDate(lastUpdated)}
          </p>
        )}
      </div>

      {/* Actions */}
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">
        <div className="flex items-center justify-end gap-2">
          {onView && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onView(id)}
              className="p-2 text-gray-500 hover:text-[#0A2540] hover:bg-gray-100 rounded-lg transition-colors"
              title="Visualizar"
            >
              <Eye className="w-4 h-4" />
            </motion.button>
          )}
          {onEdit && status !== 'revoked' && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onEdit(id)}
              className="p-2 text-gray-500 hover:text-[#FF6B35] hover:bg-orange-50 rounded-lg transition-colors"
              title="Editar"
            >
              <Edit2 className="w-4 h-4" />
            </motion.button>
          )}
          {onRenew && (status === 'expired' || isExpiring) && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onRenew(id)}
              className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              title="Renovar"
            >
              <RotateCcw className="w-4 h-4" />
            </motion.button>
          )}
          {onRevoke && status === 'active' && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onRevoke(id)}
              className="p-2 text-gray-500 hover:text-yellow-600 hover:bg-yellow-50 rounded-lg transition-colors"
              title="Revogar"
            >
              <XCircle className="w-4 h-4" />
            </motion.button>
          )}
          {onDelete && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onDelete(id)}
              className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              title="Excluir"
            >
              <Trash2 className="w-4 h-4" />
            </motion.button>
          )}
        </div>
      </div>
    </motion.div>
  );
}
