'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  QrCode,
  MapPin,
  Calendar,
  Wrench,
  AlertTriangle,
  CheckCircle,
  XCircle,
  MoreVertical,
  Tag,
  Building
} from 'lucide-react';
import type { Equipment, EquipmentStatus } from '../types/equipment.types';

interface EquipmentCardProps {
  equipment: Equipment;
  onView?: (equipment: Equipment) => void;
  onEdit?: (equipment: Equipment) => void;
  onScanQR?: (equipment: Equipment) => void;
  onScheduleMaintenance?: (equipment: Equipment) => void;
  compact?: boolean;
}

const statusConfig: Record<EquipmentStatus, {
  label: string;
  color: string;
  bgColor: string;
  icon: React.ElementType;
}> = {
  operacional: {
    label: 'Operacional',
    color: 'text-green-700',
    bgColor: 'bg-green-100',
    icon: CheckCircle
  },
  manutencao: {
    label: 'Em Manutencao',
    color: 'text-yellow-700',
    bgColor: 'bg-yellow-100',
    icon: Wrench
  },
  inativo: {
    label: 'Inativo',
    color: 'text-gray-700',
    bgColor: 'bg-gray-100',
    icon: XCircle
  },
  descartado: {
    label: 'Descartado',
    color: 'text-red-700',
    bgColor: 'bg-red-100',
    icon: AlertTriangle
  }
};

export function EquipmentCard({
  equipment,
  onView,
  onScanQR,
  onScheduleMaintenance,
  compact = false
}: EquipmentCardProps) {
  const status = statusConfig[equipment.status];
  const StatusIcon = status.icon;

  const isWarrantyExpiring = () => {
    if (!equipment.garantia_ate) return false;
    const garantiaDate = new Date(equipment.garantia_ate);
    const thirtyDaysFromNow = new Date();
    thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30);
    return garantiaDate <= thirtyDaysFromNow && garantiaDate >= new Date();
  };

  const isMaintenanceOverdue = () => {
    if (!equipment.proxima_manutencao) return false;
    return new Date(equipment.proxima_manutencao) < new Date();
  };

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

  if (compact) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
        onClick={() => onView?.(equipment)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-lg ${status.bgColor}`}>
              <StatusIcon className={`w-5 h-5 ${status.color}`} />
            </div>
            <div>
              <h4 className="font-medium text-gray-900 text-sm">{equipment.nome}</h4>
              <p className="text-xs text-gray-500">{equipment.codigo}</p>
            </div>
          </div>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${status.bgColor} ${status.color}`}>
            {status.label}
          </span>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-lg transition-all duration-200"
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div className={`p-2.5 rounded-lg ${status.bgColor}`}>
              <StatusIcon className={`w-6 h-6 ${status.color}`} />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">{equipment.nome}</h3>
              <div className="flex items-center space-x-2 mt-1">
                <span className="text-sm text-gray-500">{equipment.codigo}</span>
                <span className="text-gray-300">|</span>
                <span className="text-sm text-gray-500">{equipment.tipo}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${status.bgColor} ${status.color}`}>
              {status.label}
            </span>
            <button
              className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
              onClick={(e) => {
                e.stopPropagation();
                // Menu actions
              }}
            >
              <MoreVertical className="w-5 h-5 text-gray-400" />
            </button>
          </div>
        </div>
      </div>

      {/* Body */}
      <div className="p-4 space-y-4">
        {/* Info Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center space-x-2 text-sm">
            <Building className="w-4 h-4 text-gray-400" />
            <span className="text-gray-600">{equipment.fabricante}</span>
          </div>
          <div className="flex items-center space-x-2 text-sm">
            <Tag className="w-4 h-4 text-gray-400" />
            <span className="text-gray-600">{equipment.modelo}</span>
          </div>
          <div className="flex items-center space-x-2 text-sm col-span-2">
            <MapPin className="w-4 h-4 text-gray-400" />
            <span className="text-gray-600">{equipment.localizacao}</span>
          </div>
        </div>

        {/* Dates */}
        <div className="grid grid-cols-2 gap-3 pt-3 border-t border-gray-100">
          <div>
            <p className="text-xs text-gray-500 mb-1">Ultima Manutencao</p>
            <p className="text-sm font-medium text-gray-700">
              {formatDate(equipment.ultima_manutencao)}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Proxima Manutencao</p>
            <p className={`text-sm font-medium ${isMaintenanceOverdue() ? 'text-red-600' : 'text-gray-700'}`}>
              {formatDate(equipment.proxima_manutencao)}
              {isMaintenanceOverdue() && (
                <span className="ml-1 text-xs text-red-500">(Atrasada)</span>
              )}
            </p>
          </div>
        </div>

        {/* Warranty Alert */}
        {isWarrantyExpiring() && (
          <div className="flex items-center space-x-2 p-2 bg-amber-50 border border-amber-200 rounded-lg">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <span className="text-xs text-amber-700">
              Garantia expira em {formatDate(equipment.garantia_ate)}
            </span>
          </div>
        )}

        {/* RFID Tag */}
        {equipment.rfid_tag && (
          <div className="flex items-center space-x-2 p-2 bg-blue-50 border border-blue-200 rounded-lg">
            <Tag className="w-4 h-4 text-blue-600" />
            <span className="text-xs text-blue-700 font-mono">{equipment.rfid_tag}</span>
          </div>
        )}

        {/* Value */}
        {equipment.valor_aquisicao && (
          <div className="pt-2 border-t border-gray-100">
            <div className="flex justify-between items-center">
              <span className="text-xs text-gray-500">Valor de Aquisicao</span>
              <span className="text-sm font-semibold text-gray-900">
                {formatCurrency(equipment.valor_aquisicao)}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-100 rounded-b-xl">
        <div className="flex items-center justify-between">
          <button
            onClick={() => onScanQR?.(equipment)}
            className="flex items-center space-x-1.5 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <QrCode className="w-4 h-4" />
            <span>QR Code</span>
          </button>

          <div className="flex items-center space-x-2">
            {equipment.status === 'operacional' && (
              <button
                onClick={() => onScheduleMaintenance?.(equipment)}
                className="flex items-center space-x-1.5 px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              >
                <Calendar className="w-4 h-4" />
                <span>Agendar</span>
              </button>
            )}

            <button
              onClick={() => onView?.(equipment)}
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

export default EquipmentCard;
