'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AlertTriangle,
  Bell,
  BellOff,
  Mail,
  MessageSquare,
  Smartphone,
  Save,
  X,
  Info,
  Sliders
} from 'lucide-react';
import type { Sensor, SensorThreshold } from '../types/iot.types';

interface AlertThresholdProps {
  sensor: Sensor;
  onSave: (threshold: SensorThreshold) => Promise<void>;
  onClose: () => void;
}

export function AlertThreshold({ sensor, onSave, onClose }: AlertThresholdProps) {
  const [limiteMin, setLimiteMin] = useState<string>(sensor.limite_min?.toString() || '');
  const [limiteMax, setLimiteMax] = useState<string>(sensor.limite_max?.toString() || '');
  const [alertaDelay, setAlertaDelay] = useState<string>('60');
  const [notificarEmail, setNotificarEmail] = useState(true);
  const [notificarSms, setNotificarSms] = useState(false);
  const [notificarPush, setNotificarPush] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSave = async () => {
    setError(null);

    // Validacoes
    const min = limiteMin ? parseFloat(limiteMin) : undefined;
    const max = limiteMax ? parseFloat(limiteMax) : undefined;

    if (min !== undefined && max !== undefined && min >= max) {
      setError('O limite minimo deve ser menor que o limite maximo');
      return;
    }

    setIsSaving(true);

    try {
      await onSave({
        sensor_id: sensor.id,
        limite_min: min,
        limite_max: max,
        alerta_delay_segundos: parseInt(alertaDelay) || 60,
        notificar_email: notificarEmail,
        notificar_sms: notificarSms,
        notificar_push: notificarPush
      });
      onClose();
    } catch {
      setError('Erro ao salvar configuracoes. Tente novamente.');
    } finally {
      setIsSaving(false);
    }
  };

  // Preview do range
  const getPreviewColor = () => {
    const valor = sensor.valor_atual;
    const min = limiteMin ? parseFloat(limiteMin) : undefined;
    const max = limiteMax ? parseFloat(limiteMax) : undefined;

    if (min !== undefined && valor < min) return 'text-red-600';
    if (max !== undefined && valor > max) return 'text-red-600';
    return 'text-green-600';
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="bg-white rounded-xl shadow-xl max-w-md w-full overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Sliders className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h2 className="font-semibold text-gray-900">Configurar Alertas</h2>
                <p className="text-sm text-gray-500">{sensor.nome}</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          {/* Content */}
          <div className="p-4 space-y-5">
            {/* Current Value Preview */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Valor Atual</span>
                <span className={`text-2xl font-bold ${getPreviewColor()}`}>
                  {sensor.valor_atual}{sensor.unidade}
                </span>
              </div>
              <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all ${
                    getPreviewColor() === 'text-green-600' ? 'bg-green-500' : 'bg-red-500'
                  }`}
                  style={{
                    width: `${Math.min(100, Math.max(0, (
                      (sensor.valor_atual - (limiteMin ? parseFloat(limiteMin) : 0)) /
                      ((limiteMax ? parseFloat(limiteMax) : 100) - (limiteMin ? parseFloat(limiteMin) : 0))
                    ) * 100))}%`
                  }}
                />
              </div>
            </div>

            {/* Threshold Inputs */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Limites de Alerta
              </label>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Limite Minimo</label>
                  <div className="relative">
                    <input
                      type="number"
                      value={limiteMin}
                      onChange={(e) => setLimiteMin(e.target.value)}
                      placeholder="Min"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-gray-400">
                      {sensor.unidade}
                    </span>
                  </div>
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Limite Maximo</label>
                  <div className="relative">
                    <input
                      type="number"
                      value={limiteMax}
                      onChange={(e) => setLimiteMax(e.target.value)}
                      placeholder="Max"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-gray-400">
                      {sensor.unidade}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Alert Delay */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tempo para Disparo do Alerta
              </label>
              <select
                value={alertaDelay}
                onChange={(e) => setAlertaDelay(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="0">Imediato</option>
                <option value="30">30 segundos</option>
                <option value="60">1 minuto</option>
                <option value="300">5 minutos</option>
                <option value="600">10 minutos</option>
                <option value="1800">30 minutos</option>
              </select>
              <p className="mt-1 text-xs text-gray-500 flex items-center">
                <Info className="w-3 h-3 mr-1" />
                Tempo que o valor deve permanecer fora do limite antes de alertar
              </p>
            </div>

            {/* Notification Channels */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Canais de Notificacao
              </label>
              <div className="space-y-2">
                <label className="flex items-center justify-between p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
                  <div className="flex items-center space-x-3">
                    <Mail className="w-5 h-5 text-gray-500" />
                    <span className="text-sm text-gray-700">E-mail</span>
                  </div>
                  <input
                    type="checkbox"
                    checked={notificarEmail}
                    onChange={(e) => setNotificarEmail(e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                </label>

                <label className="flex items-center justify-between p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
                  <div className="flex items-center space-x-3">
                    <MessageSquare className="w-5 h-5 text-gray-500" />
                    <span className="text-sm text-gray-700">SMS</span>
                  </div>
                  <input
                    type="checkbox"
                    checked={notificarSms}
                    onChange={(e) => setNotificarSms(e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                </label>

                <label className="flex items-center justify-between p-3 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100 transition-colors">
                  <div className="flex items-center space-x-3">
                    <Smartphone className="w-5 h-5 text-gray-500" />
                    <span className="text-sm text-gray-700">Push Notification</span>
                  </div>
                  <input
                    type="checkbox"
                    checked={notificarPush}
                    onChange={(e) => setNotificarPush(e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                </label>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
                <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end space-x-3 p-4 border-t border-gray-200 bg-gray-50">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              Cancelar
            </button>
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 rounded-lg transition-colors"
            >
              {isSaving ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Salvando...</span>
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  <span>Salvar</span>
                </>
              )}
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

// Badge de alerta para sensores
interface AlertBadgeProps {
  count: number;
  severity?: 'critica' | 'alta' | 'media' | 'baixa';
  onClick?: () => void;
}

export function AlertBadge({ count, severity = 'media', onClick }: AlertBadgeProps) {
  const severityStyles = {
    critica: 'bg-red-500 text-white animate-pulse',
    alta: 'bg-orange-500 text-white',
    media: 'bg-yellow-500 text-white',
    baixa: 'bg-blue-500 text-white'
  };

  if (count === 0) return null;

  return (
    <button
      onClick={onClick}
      className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${severityStyles[severity]}`}
    >
      <Bell className="w-3 h-3" />
      <span>{count}</span>
    </button>
  );
}

// Lista de alertas
interface AlertListProps {
  alerts: Array<{
    id: string;
    sensor_nome: string;
    mensagem: string;
    severidade: 'critica' | 'alta' | 'media' | 'baixa';
    created_at: string;
    acknowledged: boolean;
  }>;
  onAcknowledge?: (alertId: string) => void;
  onResolve?: (alertId: string) => void;
}

export function AlertList({ alerts, onAcknowledge, onResolve }: AlertListProps) {
  const severityConfig = {
    critica: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-700', icon: 'text-red-500' },
    alta: { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-700', icon: 'text-orange-500' },
    media: { bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'text-yellow-700', icon: 'text-yellow-500' },
    baixa: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-700', icon: 'text-blue-500' }
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Agora';
    if (diffMins < 60) return `${diffMins}min atras`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h atras`;
    return date.toLocaleDateString('pt-BR');
  };

  if (alerts.length === 0) {
    return (
      <div className="text-center py-8">
        <BellOff className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500">Nenhum alerta ativo</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {alerts.map((alert) => {
        const styles = severityConfig[alert.severidade];

        return (
          <motion.div
            key={alert.id}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className={`${styles.bg} ${styles.border} border rounded-lg p-3`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3">
                <AlertTriangle className={`w-5 h-5 mt-0.5 ${styles.icon} ${
                  alert.severidade === 'critica' ? 'animate-pulse' : ''
                }`} />
                <div>
                  <p className={`font-medium ${styles.text}`}>{alert.sensor_nome}</p>
                  <p className="text-sm text-gray-600 mt-0.5">{alert.mensagem}</p>
                  <p className="text-xs text-gray-500 mt-1">{formatTime(alert.created_at)}</p>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                {!alert.acknowledged && onAcknowledge && (
                  <button
                    onClick={() => onAcknowledge(alert.id)}
                    className="text-xs text-gray-600 hover:text-gray-900 underline"
                  >
                    Reconhecer
                  </button>
                )}
                {onResolve && (
                  <button
                    onClick={() => onResolve(alert.id)}
                    className="text-xs text-blue-600 hover:text-blue-700 underline"
                  >
                    Resolver
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}

export default AlertThreshold;
