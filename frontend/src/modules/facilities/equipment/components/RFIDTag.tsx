'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  Tag,
  Wifi,
  CheckCircle,
  XCircle,
  RefreshCw,
  Copy,
  Check
} from 'lucide-react';

interface RFIDTagProps {
  tagId: string;
  equipmentName?: string;
  status?: 'active' | 'inactive' | 'reading';
  lastRead?: string;
  signalStrength?: number;
  size?: 'sm' | 'md' | 'lg';
  showDetails?: boolean;
  onRefresh?: () => void;
}

const sizeConfig = {
  sm: {
    container: 'px-2 py-1',
    icon: 'w-3 h-3',
    text: 'text-xs'
  },
  md: {
    container: 'px-3 py-2',
    icon: 'w-4 h-4',
    text: 'text-sm'
  },
  lg: {
    container: 'px-4 py-3',
    icon: 'w-5 h-5',
    text: 'text-base'
  }
};

const statusConfig = {
  active: {
    bg: 'bg-green-100',
    border: 'border-green-200',
    text: 'text-green-700',
    icon: CheckCircle,
    label: 'Ativo'
  },
  inactive: {
    bg: 'bg-gray-100',
    border: 'border-gray-200',
    text: 'text-gray-700',
    icon: XCircle,
    label: 'Inativo'
  },
  reading: {
    bg: 'bg-blue-100',
    border: 'border-blue-200',
    text: 'text-blue-700',
    icon: RefreshCw,
    label: 'Lendo...'
  }
};

export function RFIDTag({
  tagId,
  equipmentName,
  status = 'active',
  lastRead,
  signalStrength,
  size = 'md',
  showDetails = false,
  onRefresh
}: RFIDTagProps) {
  const [copied, setCopied] = React.useState(false);
  const sizeStyles = sizeConfig[size];
  const statusStyles = statusConfig[status];
  const StatusIcon = statusStyles.icon;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(tagId);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Erro ao copiar:', err);
    }
  };

  const formatLastRead = (dateStr?: string) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Agora';
    if (diffMins < 60) return `${diffMins}min atras`;
    if (diffHours < 24) return `${diffHours}h atras`;
    return `${diffDays}d atras`;
  };

  const getSignalBars = (strength?: number) => {
    if (!strength) return 0;
    if (strength >= 80) return 4;
    if (strength >= 60) return 3;
    if (strength >= 40) return 2;
    if (strength >= 20) return 1;
    return 0;
  };

  // Badge simples
  if (!showDetails) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className={`inline-flex items-center space-x-1.5 ${sizeStyles.container} ${statusStyles.bg} ${statusStyles.border} border rounded-full`}
      >
        <Tag className={`${sizeStyles.icon} ${statusStyles.text}`} />
        <span className={`font-mono ${sizeStyles.text} ${statusStyles.text}`}>
          {tagId}
        </span>
        {status === 'reading' && (
          <RefreshCw className={`${sizeStyles.icon} ${statusStyles.text} animate-spin`} />
        )}
      </motion.div>
    );
  }

  // Card detalhado
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden"
    >
      {/* Header */}
      <div className={`${statusStyles.bg} ${statusStyles.border} border-b px-4 py-3`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className={`p-1.5 rounded-lg bg-white/50`}>
              <Tag className={`w-5 h-5 ${statusStyles.text}`} />
            </div>
            <div>
              <p className={`font-semibold ${statusStyles.text}`}>RFID Tag</p>
              {equipmentName && (
                <p className="text-xs text-gray-600 mt-0.5">{equipmentName}</p>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium bg-white/50 ${statusStyles.text}`}>
              <StatusIcon className={`w-3 h-3 ${status === 'reading' ? 'animate-spin' : ''}`} />
              <span>{statusStyles.label}</span>
            </span>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="p-4 space-y-4">
        {/* Tag ID */}
        <div>
          <p className="text-xs text-gray-500 mb-1">Tag ID</p>
          <div className="flex items-center space-x-2">
            <code className="flex-1 px-3 py-2 bg-gray-100 rounded-lg font-mono text-sm text-gray-800">
              {tagId}
            </code>
            <button
              onClick={handleCopy}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Copiar"
            >
              {copied ? (
                <Check className="w-4 h-4 text-green-500" />
              ) : (
                <Copy className="w-4 h-4 text-gray-400" />
              )}
            </button>
          </div>
        </div>

        {/* Signal Strength */}
        {signalStrength !== undefined && (
          <div>
            <p className="text-xs text-gray-500 mb-1">Intensidade do Sinal</p>
            <div className="flex items-center space-x-3">
              <div className="flex items-end space-x-0.5 h-5">
                {[1, 2, 3, 4].map((bar) => (
                  <div
                    key={bar}
                    className={`w-1.5 rounded-sm transition-colors ${
                      bar <= getSignalBars(signalStrength)
                        ? 'bg-green-500'
                        : 'bg-gray-200'
                    }`}
                    style={{ height: `${bar * 25}%` }}
                  />
                ))}
              </div>
              <span className="text-sm font-medium text-gray-700">
                {signalStrength}%
              </span>
            </div>
          </div>
        )}

        {/* Last Read */}
        {lastRead && (
          <div className="flex items-center justify-between pt-3 border-t border-gray-100">
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <Wifi className="w-4 h-4" />
              <span>Ultima leitura</span>
            </div>
            <span className="text-sm font-medium text-gray-700">
              {formatLastRead(lastRead)}
            </span>
          </div>
        )}
      </div>

      {/* Actions */}
      {onRefresh && (
        <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">
          <button
            onClick={onRefresh}
            disabled={status === 'reading'}
            className="w-full flex items-center justify-center space-x-2 px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 disabled:text-gray-400 disabled:hover:bg-transparent rounded-lg transition-colors"
          >
            <RefreshCw className={`w-4 h-4 ${status === 'reading' ? 'animate-spin' : ''}`} />
            <span>{status === 'reading' ? 'Lendo...' : 'Ler Novamente'}</span>
          </button>
        </div>
      )}
    </motion.div>
  );
}

// Componente para listar multiplas tags
interface RFIDTagListProps {
  tags: Array<{
    id: string;
    tagId: string;
    equipmentName: string;
    status: 'active' | 'inactive';
    lastRead?: string;
  }>;
  onSelect?: (tagId: string) => void;
}

export function RFIDTagList({ tags, onSelect }: RFIDTagListProps) {
  return (
    <div className="space-y-2">
      {tags.map((tag) => (
        <motion.div
          key={tag.id}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-sm transition-all cursor-pointer"
          onClick={() => onSelect?.(tag.id)}
        >
          <div className="flex items-center space-x-3">
            <RFIDTag
              tagId={tag.tagId}
              status={tag.status}
              size="sm"
            />
            <span className="text-sm text-gray-700">{tag.equipmentName}</span>
          </div>
          {tag.lastRead && (
            <span className="text-xs text-gray-500">
              {new Date(tag.lastRead).toLocaleTimeString('pt-BR', {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </span>
          )}
        </motion.div>
      ))}
    </div>
  );
}

export default RFIDTag;
