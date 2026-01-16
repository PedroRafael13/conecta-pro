'use client';

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  Thermometer,
  Droplets,
  AlertTriangle
} from 'lucide-react';

interface SensorGaugeProps {
  value: number;
  min: number;
  max: number;
  unit: string;
  type: 'temperatura' | 'umidade' | 'pressao' | 'energia' | 'default';
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  showLimits?: boolean;
  limitMin?: number;
  limitMax?: number;
  animated?: boolean;
}

const typeConfig = {
  temperatura: {
    icon: Thermometer,
    gradient: ['#3B82F6', '#10B981', '#EF4444'], // Frio -> Normal -> Quente
    colors: {
      low: '#3B82F6',
      normal: '#10B981',
      high: '#EF4444'
    }
  },
  umidade: {
    icon: Droplets,
    gradient: ['#FCD34D', '#10B981', '#3B82F6'], // Seco -> Normal -> Umido
    colors: {
      low: '#FCD34D',
      normal: '#10B981',
      high: '#3B82F6'
    }
  },
  pressao: {
    icon: null,
    gradient: ['#EF4444', '#10B981', '#EF4444'], // Baixa -> Normal -> Alta
    colors: {
      low: '#EF4444',
      normal: '#10B981',
      high: '#EF4444'
    }
  },
  energia: {
    icon: null,
    gradient: ['#10B981', '#FCD34D', '#EF4444'], // Baixo -> Medio -> Alto
    colors: {
      low: '#10B981',
      normal: '#FCD34D',
      high: '#EF4444'
    }
  },
  default: {
    icon: null,
    gradient: ['#3B82F6', '#10B981', '#EF4444'],
    colors: {
      low: '#3B82F6',
      normal: '#10B981',
      high: '#EF4444'
    }
  }
};

const sizeConfig = {
  sm: { size: 120, stroke: 8, fontSize: '1.5rem', labelSize: '0.65rem' },
  md: { size: 160, stroke: 10, fontSize: '2rem', labelSize: '0.75rem' },
  lg: { size: 200, stroke: 12, fontSize: '2.5rem', labelSize: '0.875rem' }
};

export function SensorGauge({
  value,
  min,
  max,
  unit,
  type = 'default',
  label,
  size = 'md',
  showLimits = false,
  limitMin,
  limitMax,
  animated = true
}: SensorGaugeProps) {
  const config = typeConfig[type];
  const sizeStyle = sizeConfig[size];

  // Calcular porcentagem
  const percentage = useMemo(() => {
    return Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100));
  }, [value, min, max]);

  // Determinar cor baseado no valor
  const currentColor = useMemo(() => {
    if (limitMin !== undefined && value < limitMin) return config.colors.low;
    if (limitMax !== undefined && value > limitMax) return config.colors.high;
    return config.colors.normal;
  }, [value, limitMin, limitMax, config]);

  // Verificar se esta fora dos limites
  const isOutOfRange = useMemo(() => {
    if (limitMin !== undefined && value < limitMin) return true;
    if (limitMax !== undefined && value > limitMax) return true;
    return false;
  }, [value, limitMin, limitMax]);

  // Calculos SVG
  const radius = (sizeStyle.size - sizeStyle.stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference * 0.75; // 270 graus

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: sizeStyle.size, height: sizeStyle.size }}>
        <svg
          width={sizeStyle.size}
          height={sizeStyle.size}
          className="transform -rotate-135"
        >
          {/* Background arc */}
          <circle
            cx={sizeStyle.size / 2}
            cy={sizeStyle.size / 2}
            r={radius}
            fill="none"
            stroke="#e5e7eb"
            strokeWidth={sizeStyle.stroke}
            strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`}
            strokeLinecap="round"
          />

          {/* Gradient definition */}
          <defs>
            <linearGradient id={`gauge-gradient-${type}`} x1="0%" y1="0%" x2="100%" y2="0%">
              {config.gradient.map((color, index) => (
                <stop
                  key={index}
                  offset={`${index * 50}%`}
                  stopColor={color}
                />
              ))}
            </linearGradient>
          </defs>

          {/* Value arc */}
          <motion.circle
            cx={sizeStyle.size / 2}
            cy={sizeStyle.size / 2}
            r={radius}
            fill="none"
            stroke={currentColor}
            strokeWidth={sizeStyle.stroke}
            strokeDasharray={`${circumference * 0.75} ${circumference * 0.25}`}
            strokeLinecap="round"
            initial={animated ? { strokeDashoffset: circumference } : { strokeDashoffset }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1, ease: 'easeOut' }}
          />
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className="font-bold"
            style={{
              fontSize: sizeStyle.fontSize,
              color: isOutOfRange ? currentColor : '#1f2937'
            }}
            initial={animated ? { scale: 0.5, opacity: 0 } : {}}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            {value}
          </motion.span>
          <span className="text-gray-500" style={{ fontSize: sizeStyle.labelSize }}>
            {unit}
          </span>

          {isOutOfRange && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute -top-1 -right-1"
            >
              <AlertTriangle className="w-5 h-5 text-red-500" />
            </motion.div>
          )}
        </div>
      </div>

      {/* Label */}
      {label && (
        <p className="mt-2 text-sm font-medium text-gray-700 text-center">
          {label}
        </p>
      )}

      {/* Limits */}
      {showLimits && (
        <div className="mt-1 flex items-center justify-between w-full px-4">
          <span className="text-xs text-gray-500">{min}{unit}</span>
          <span className="text-xs text-gray-500">{max}{unit}</span>
        </div>
      )}
    </div>
  );
}

// Componente de gauge linear (barra)
interface LinearGaugeProps {
  value: number;
  min: number;
  max: number;
  unit: string;
  label?: string;
  limitMin?: number;
  limitMax?: number;
  showValue?: boolean;
  height?: number;
  colorScheme?: 'default' | 'temperature' | 'humidity';
}

export function LinearGauge({
  value,
  min,
  max,
  unit,
  label,
  limitMin,
  limitMax,
  showValue = true,
  height = 8,
  colorScheme = 'default'
}: LinearGaugeProps) {
  const percentage = Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100));

  const isOutOfRange = (limitMin !== undefined && value < limitMin) ||
                       (limitMax !== undefined && value > limitMax);

  const getColor = () => {
    if (isOutOfRange) return 'bg-red-500';

    switch (colorScheme) {
      case 'temperature':
        if (percentage < 30) return 'bg-blue-500';
        if (percentage > 70) return 'bg-red-500';
        return 'bg-green-500';
      case 'humidity':
        if (percentage < 30) return 'bg-yellow-500';
        if (percentage > 70) return 'bg-blue-500';
        return 'bg-green-500';
      default:
        return 'bg-blue-500';
    }
  };

  return (
    <div className="w-full">
      {(label || showValue) && (
        <div className="flex justify-between items-center mb-1">
          {label && <span className="text-sm text-gray-600">{label}</span>}
          {showValue && (
            <span className={`text-sm font-medium ${isOutOfRange ? 'text-red-600' : 'text-gray-900'}`}>
              {value}{unit}
            </span>
          )}
        </div>
      )}

      <div
        className="w-full bg-gray-200 rounded-full overflow-hidden"
        style={{ height }}
      >
        <motion.div
          className={`h-full rounded-full ${getColor()}`}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>

      {/* Limit markers */}
      {(limitMin !== undefined || limitMax !== undefined) && (
        <div className="relative mt-0.5" style={{ height: 4 }}>
          {limitMin !== undefined && (
            <div
              className="absolute w-0.5 h-full bg-yellow-500"
              style={{ left: `${((limitMin - min) / (max - min)) * 100}%` }}
            />
          )}
          {limitMax !== undefined && (
            <div
              className="absolute w-0.5 h-full bg-red-500"
              style={{ left: `${((limitMax - min) / (max - min)) * 100}%` }}
            />
          )}
        </div>
      )}
    </div>
  );
}

// Componente de temperatura com termometro visual
interface ThermometerGaugeProps {
  value: number;
  min?: number;
  max?: number;
  unit?: string;
}

export function ThermometerGauge({
  value,
  min = -10,
  max = 50,
  unit = 'C'
}: ThermometerGaugeProps) {
  const percentage = Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100));

  const getColor = () => {
    if (value < 10) return 'from-blue-500 to-blue-400';
    if (value < 25) return 'from-green-500 to-green-400';
    if (value < 35) return 'from-yellow-500 to-orange-400';
    return 'from-red-500 to-red-400';
  };

  return (
    <div className="flex items-end space-x-3">
      {/* Thermometer visual */}
      <div className="relative w-8">
        {/* Tube */}
        <div className="w-4 h-32 bg-gray-200 rounded-t-full mx-auto relative overflow-hidden">
          <motion.div
            className={`absolute bottom-0 left-0 right-0 bg-gradient-to-t ${getColor()} rounded-t-full`}
            initial={{ height: 0 }}
            animate={{ height: `${percentage}%` }}
            transition={{ duration: 1, ease: 'easeOut' }}
          />
        </div>
        {/* Bulb */}
        <div className={`w-8 h-8 rounded-full bg-gradient-to-br ${getColor()} -mt-2 relative z-10`} />
      </div>

      {/* Value */}
      <div className="pb-2">
        <span className="text-3xl font-bold text-gray-900">{value}</span>
        <span className="text-lg text-gray-500">{unit}</span>
      </div>
    </div>
  );
}

export default SensorGauge;
