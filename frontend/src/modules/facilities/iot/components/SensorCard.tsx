'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  Thermometer,
  Droplets,
  Gauge,
  Activity,
  Zap,
  Sun,
  Wind,
  Volume2,
  Wifi,
  WifiOff,
  AlertTriangle,
  Battery,
  BatteryLow,
  MoreVertical,
  TrendingUp,
  TrendingDown,
  MapPin
} from 'lucide-react';
import type { Sensor, SensorType, SensorStatus } from '../types/iot.types';

interface SensorCardProps {
  sensor: Sensor;
  onView?: (sensor: Sensor) => void;
  onConfigThreshold?: (sensor: Sensor) => void;
  showTrend?: boolean;
  trendValue?: number; // Positivo = subindo, negativo = descendo
  compact?: boolean;
}

const sensorTypeConfig: Record<SensorType, {
  icon: React.ElementType;
  color: string;
  bgColor: string;
  label: string;
}> = {
  temperatura: {
    icon: Thermometer,
    color: 'text-orange-600',
    bgColor: 'bg-orange-100',
    label: 'Temperatura'
  },
  umidade: {
    icon: Droplets,
    color: 'text-blue-600',
    bgColor: 'bg-blue-100',
    label: 'Umidade'
  },
  pressao: {
    icon: Gauge,
    color: 'text-purple-600',
    bgColor: 'bg-purple-100',
    label: 'Pressao'
  },
  movimento: {
    icon: Activity,
    color: 'text-green-600',
    bgColor: 'bg-green-100',
    label: 'Movimento'
  },
  energia: {
    icon: Zap,
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-100',
    label: 'Energia'
  },
  luminosidade: {
    icon: Sun,
    color: 'text-amber-600',
    bgColor: 'bg-amber-100',
    label: 'Luminosidade'
  },
  co2: {
    icon: Wind,
    color: 'text-teal-600',
    bgColor: 'bg-teal-100',
    label: 'CO2'
  },
  ruido: {
    icon: Volume2,
    color: 'text-pink-600',
    bgColor: 'bg-pink-100',
    label: 'Ruido'
  }
};

const statusConfig: Record<SensorStatus, {
  label: string;
  color: string;
  bgColor: string;
  icon: React.ElementType;
}> = {
  online: {
    label: 'Online',
    color: 'text-green-700',
    bgColor: 'bg-green-100',
    icon: Wifi
  },
  offline: {
    label: 'Offline',
    color: 'text-gray-700',
    bgColor: 'bg-gray-100',
    icon: WifiOff
  },
  alerta: {
    label: 'Alerta',
    color: 'text-red-700',
    bgColor: 'bg-red-100',
    icon: AlertTriangle
  }
};

export function SensorCard({
  sensor,
  onView,
  onConfigThreshold,
  showTrend = false,
  trendValue,
  compact = false
}: SensorCardProps) {
  const typeConfig = sensorTypeConfig[sensor.tipo];
  const sensorStatus = statusConfig[sensor.status];
  const TypeIcon = typeConfig.icon;
  const StatusIcon = sensorStatus.icon;

  const isOutOfRange = () => {
    if (sensor.limite_min !== undefined && sensor.valor_atual < sensor.limite_min) return true;
    if (sensor.limite_max !== undefined && sensor.valor_atual > sensor.limite_max) return true;
    return false;
  };

  const isBatteryLow = () => {
    return sensor.bateria_nivel !== undefined && sensor.bateria_nivel < 20;
  };

  const formatLastUpdate = () => {
    const date = new Date(sensor.ultima_leitura);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Agora';
    if (diffMins < 60) return `${diffMins}min`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h`;
    return date.toLocaleDateString('pt-BR');
  };

  // Versao compacta
  if (compact) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white border border-gray-200 rounded-lg p-3 hover:shadow-md transition-shadow cursor-pointer"
        onClick={() => onView?.(sensor)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className={`p-1.5 rounded-lg ${typeConfig.bgColor}`}>
              <TypeIcon className={`w-4 h-4 ${typeConfig.color}`} />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900 truncate max-w-[120px]">
                {sensor.nome}
              </p>
              <p className="text-xs text-gray-500">{typeConfig.label}</p>
            </div>
          </div>

          <div className="text-right">
            <p className={`text-lg font-bold ${isOutOfRange() ? 'text-red-600' : 'text-gray-900'}`}>
              {sensor.valor_atual}
              <span className="text-xs font-normal text-gray-500 ml-0.5">
                {sensor.unidade}
              </span>
            </p>
            <div className="flex items-center justify-end space-x-1">
              <span className={`w-2 h-2 rounded-full ${
                sensor.status === 'online' ? 'bg-green-500' :
                sensor.status === 'alerta' ? 'bg-red-500 animate-pulse' :
                'bg-gray-400'
              }`} />
              <span className="text-xs text-gray-400">{formatLastUpdate()}</span>
            </div>
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
      className="bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-lg transition-all duration-200"
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-100">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div className={`p-2.5 rounded-lg ${typeConfig.bgColor}`}>
              <TypeIcon className={`w-6 h-6 ${typeConfig.color}`} />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">{sensor.nome}</h3>
              <div className="flex items-center space-x-2 mt-1">
                <span className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-xs font-medium ${sensorStatus.bgColor} ${sensorStatus.color}`}>
                  <StatusIcon className="w-3 h-3" />
                  <span>{sensorStatus.label}</span>
                </span>
                {isBatteryLow() && (
                  <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700">
                    <BatteryLow className="w-3 h-3" />
                    <span>{sensor.bateria_nivel}%</span>
                  </span>
                )}
              </div>
            </div>
          </div>

          <button
            className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
            onClick={(e) => {
              e.stopPropagation();
              onConfigThreshold?.(sensor);
            }}
          >
            <MoreVertical className="w-5 h-5 text-gray-400" />
          </button>
        </div>
      </div>

      {/* Value Display */}
      <div className="p-6 flex flex-col items-center">
        <div className="relative">
          <span className={`text-5xl font-bold ${isOutOfRange() ? 'text-red-600' : 'text-gray-900'}`}>
            {sensor.valor_atual}
          </span>
          <span className="text-xl text-gray-500 ml-1">{sensor.unidade}</span>

          {showTrend && trendValue !== undefined && (
            <span className={`absolute -right-8 top-2 ${trendValue >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {trendValue >= 0 ? (
                <TrendingUp className="w-5 h-5" />
              ) : (
                <TrendingDown className="w-5 h-5" />
              )}
            </span>
          )}
        </div>

        {/* Range Indicator */}
        {(sensor.limite_min !== undefined || sensor.limite_max !== undefined) && (
          <div className="mt-4 w-full">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>{sensor.limite_min ?? 'Min'}</span>
              <span>Range</span>
              <span>{sensor.limite_max ?? 'Max'}</span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all ${isOutOfRange() ? 'bg-red-500' : 'bg-green-500'}`}
                style={{
                  width: `${Math.min(100, Math.max(0, (
                    (sensor.valor_atual - (sensor.limite_min ?? 0)) /
                    ((sensor.limite_max ?? 100) - (sensor.limite_min ?? 0))
                  ) * 100))}%`
                }}
              />
            </div>
          </div>
        )}

        {/* Out of range alert */}
        {isOutOfRange() && (
          <div className="mt-3 flex items-center space-x-1.5 text-sm text-red-600">
            <AlertTriangle className="w-4 h-4" />
            <span>Valor fora do limite!</span>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-100 rounded-b-xl">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-1">
            <MapPin className="w-3.5 h-3.5" />
            <span className="truncate max-w-[150px]">{sensor.localizacao}</span>
          </div>
          <div className="flex items-center space-x-3">
            {sensor.bateria_nivel !== undefined && !isBatteryLow() && (
              <div className="flex items-center space-x-1">
                <Battery className="w-3.5 h-3.5" />
                <span>{sensor.bateria_nivel}%</span>
              </div>
            )}
            <span>Atualizado {formatLastUpdate()}</span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// Grid de sensores
interface SensorGridProps {
  sensors: Sensor[];
  onSelectSensor?: (sensor: Sensor) => void;
  columns?: 2 | 3 | 4;
}

export function SensorGrid({ sensors, onSelectSensor, columns = 3 }: SensorGridProps) {
  const gridCols = {
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
  };

  return (
    <div className={`grid ${gridCols[columns]} gap-4`}>
      {sensors.map((sensor, index) => (
        <motion.div
          key={sensor.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 }}
        >
          <SensorCard
            sensor={sensor}
            onView={onSelectSensor}
          />
        </motion.div>
      ))}
    </div>
  );
}

export default SensorCard;
