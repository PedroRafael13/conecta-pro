'use client';

import { useState, useCallback } from 'react';
import { motion, Reorder, AnimatePresence } from 'framer-motion';
import {
  Route as RouteIcon,
  MapPin,
  Clock,
  Navigation,
  Zap,
  GripVertical,
  Check,
  AlertCircle,
  Loader2,
  ChevronDown,
  ChevronUp,
  Trash2,
} from 'lucide-react';
import { Card } from '@/core/components/ui';
import { Button } from '@/core/components/ui';
import { Badge } from '@/core/components/ui';
import type { Route, ServiceOrder } from '../../types';
import { PRIORIDADE_CONFIG } from '../../types';

export interface RouteOptimizerProps {
  route: Route;
  orders?: ServiceOrder[];
  onOptimize?: (routeId: string) => Promise<void | Route>;
  onReorder?: (routeId: string, newOrder: string[]) => Promise<void | Route>;
  onRemoveOrder?: (routeId: string, orderId: string) => void;
  isOptimizing?: boolean;
  className?: string;
}

interface RouteOrderItem {
  id: string;
  order?: ServiceOrder;
}

export function RouteOptimizer({
  route,
  orders = [],
  onOptimize,
  onReorder,
  onRemoveOrder,
  isOptimizing = false,
  className = '',
}: RouteOptimizerProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [localOrder, setLocalOrder] = useState<string[]>(route.ordens);
  const [hasChanges, setHasChanges] = useState(false);

  // Mapear ordens com detalhes
  const orderItems: RouteOrderItem[] = localOrder.map(id => ({
    id,
    order: orders.find(o => o.id === id),
  }));

  // Formatar tempo
  const formatTempo = (min: number): string => {
    if (min < 60) return `${min}min`;
    const hours = Math.floor(min / 60);
    const mins = min % 60;
    return mins > 0 ? `${hours}h ${mins}min` : `${hours}h`;
  };

  // Formatar distância
  const formatDistancia = (km: number): string => {
    return `${km.toFixed(1)} km`;
  };

  // Handler de reordenação
  const handleReorder = useCallback((newOrder: string[]) => {
    setLocalOrder(newOrder);
    setHasChanges(true);
  }, []);

  // Salvar nova ordem
  const handleSaveOrder = async () => {
    if (onReorder && hasChanges) {
      await onReorder(route.id, localOrder);
      setHasChanges(false);
    }
  };

  // Resetar ordem
  const handleResetOrder = () => {
    setLocalOrder(route.ordens);
    setHasChanges(false);
  };

  // Remover ordem da rota
  const handleRemoveOrder = (orderId: string) => {
    const newOrder = localOrder.filter(id => id !== orderId);
    setLocalOrder(newOrder);
    setHasChanges(true);
    onRemoveOrder?.(route.id, orderId);
  };

  return (
    <Card padding="none" className={className}>
      {/* Header */}
      <div
        className="p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${route.otimizada ? 'bg-green-100' : 'bg-yellow-100'}`}>
              <RouteIcon className={`w-5 h-5 ${route.otimizada ? 'text-green-600' : 'text-yellow-600'}`} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-semibold text-gray-900">
                  Rota - {route.tecnico_nome || 'Técnico'}
                </span>
                {route.otimizada ? (
                  <Badge variant="success" size="sm">
                    <Check className="w-3 h-3 mr-1" />
                    Otimizada
                  </Badge>
                ) : (
                  <Badge variant="warning" size="sm">
                    <AlertCircle className="w-3 h-3 mr-1" />
                    Não otimizada
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-4 text-sm text-gray-500 mt-1">
                <span className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5" />
                  {localOrder.length} paradas
                </span>
                <span className="flex items-center gap-1">
                  <Navigation className="w-3.5 h-3.5" />
                  {formatDistancia(route.distancia_total_km)}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" />
                  {formatTempo(route.tempo_estimado_min)}
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {hasChanges && (
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); handleResetOrder(); }}>
                  Cancelar
                </Button>
                <Button variant="primary" size="sm" onClick={(e) => { e.stopPropagation(); handleSaveOrder(); }}>
                  Salvar
                </Button>
              </div>
            )}
            {!hasChanges && onOptimize && !route.otimizada && (
              <Button
                variant="secondary"
                size="sm"
                onClick={(e) => { e.stopPropagation(); onOptimize(route.id); }}
                disabled={isOptimizing}
              >
                {isOptimizing ? (
                  <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                ) : (
                  <Zap className="w-4 h-4 mr-1" />
                )}
                Otimizar
              </Button>
            )}
            {isExpanded ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </div>
        </div>
      </div>

      {/* Lista de ordens (reordenável) */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="p-4">
              {localOrder.length === 0 ? (
                <div className="text-center py-6 text-gray-500">
                  <MapPin className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                  <p>Nenhuma ordem na rota</p>
                </div>
              ) : (
                <Reorder.Group
                  axis="y"
                  values={localOrder}
                  onReorder={handleReorder}
                  className="space-y-2"
                >
                  {orderItems.map((item, index) => (
                    <Reorder.Item
                      key={item.id}
                      value={item.id}
                      className="list-none"
                    >
                      <motion.div
                        layout
                        className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200
                          hover:border-gray-300 hover:shadow-sm transition-all cursor-grab active:cursor-grabbing"
                      >
                        {/* Handle de arraste */}
                        <div className="text-gray-400">
                          <GripVertical className="w-4 h-4" />
                        </div>

                        {/* Número da parada */}
                        <div className="w-6 h-6 rounded-full bg-blue-600 text-white text-xs
                          flex items-center justify-center font-medium flex-shrink-0">
                          {index + 1}
                        </div>

                        {/* Info da ordem */}
                        <div className="flex-1 min-w-0">
                          {item.order ? (
                            <>
                              <div className="flex items-center gap-2">
                                <span className="font-medium text-gray-900 truncate">
                                  {item.order.numero}
                                </span>
                                <Badge
                                  variant={
                                    item.order.prioridade === 'urgente' ? 'danger' :
                                    item.order.prioridade === 'alta' ? 'warning' :
                                    item.order.prioridade === 'normal' ? 'info' : 'default'
                                  }
                                  size="sm"
                                >
                                  {PRIORIDADE_CONFIG[item.order.prioridade].label}
                                </Badge>
                              </div>
                              <div className="flex items-center gap-2 text-sm text-gray-500 mt-0.5">
                                <span className="truncate">{item.order.cliente}</span>
                              </div>
                              <div className="flex items-center gap-1 text-xs text-gray-400 mt-0.5">
                                <MapPin className="w-3 h-3" />
                                <span className="truncate">{item.order.endereco}</span>
                              </div>
                            </>
                          ) : (
                            <span className="text-gray-500">Ordem #{item.id}</span>
                          )}
                        </div>

                        {/* Botão remover */}
                        <button
                          onClick={(e) => { e.stopPropagation(); handleRemoveOrder(item.id); }}
                          className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50
                            rounded transition-colors"
                          title="Remover da rota"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </motion.div>
                    </Reorder.Item>
                  ))}
                </Reorder.Group>
              )}

              {/* Sumário */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-900">
                      {localOrder.length}
                    </div>
                    <div className="text-xs text-gray-500">Paradas</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-900">
                      {formatDistancia(route.distancia_total_km)}
                    </div>
                    <div className="text-xs text-gray-500">Distância</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-900">
                      {formatTempo(route.tempo_estimado_min)}
                    </div>
                    <div className="text-xs text-gray-500">Tempo Est.</div>
                  </div>
                </div>
              </div>

              {/* Dica */}
              <div className="mt-3 p-2 bg-blue-50 rounded-lg text-xs text-blue-700 flex items-center gap-2">
                <GripVertical className="w-4 h-4 flex-shrink-0" />
                Arraste os itens para reordenar a rota manualmente
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
}

export default RouteOptimizer;
