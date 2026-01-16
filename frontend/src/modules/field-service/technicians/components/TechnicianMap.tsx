'use client';

import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MapPin,
  Navigation,
  Users,
  RefreshCw,
  Maximize2,
  Minimize2,
  X,
} from 'lucide-react';
import { Card } from '@/core/components/ui';
import { Button } from '@/core/components/ui';
import { Badge } from '@/core/components/ui';
import type { Technician, StatusTecnico } from '../../types';
import { STATUS_TECNICO_CONFIG } from '../../types';

export interface TechnicianMapProps {
  technicians: Technician[];
  selectedTechnician?: string;
  onSelectTechnician?: (id: string | undefined) => void;
  onRefresh?: () => void;
  isLoading?: boolean;
  className?: string;
}

// Cores dos marcadores por status
const markerColors: Record<StatusTecnico, string> = {
  disponivel: '#22c55e', // green-500
  ocupado: '#ef4444', // red-500
  em_deslocamento: '#3b82f6', // blue-500
  offline: '#9ca3af', // gray-400
};

export function TechnicianMap({
  technicians,
  selectedTechnician,
  onSelectTechnician,
  onRefresh,
  isLoading = false,
  className = '',
}: TechnicianMapProps) {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showLegend, setShowLegend] = useState(true);

  // Filtrar técnicos com localização
  const techniciansWithLocation = useMemo(() => {
    return technicians.filter(t => t.localizacao);
  }, [technicians]);

  // Estatísticas por status
  const statusStats = useMemo(() => {
    const stats: Record<StatusTecnico, number> = {
      disponivel: 0,
      ocupado: 0,
      em_deslocamento: 0,
      offline: 0,
    };
    technicians.forEach(t => stats[t.status]++);
    return stats;
  }, [technicians]);

  // Técnico selecionado
  const selected = useMemo(() => {
    if (!selectedTechnician) return null;
    return technicians.find(t => t.id === selectedTechnician);
  }, [selectedTechnician, technicians]);

  // Calcular posição do marcador no mapa (simulado)
  const getMarkerPosition = (lat: number, lng: number) => {
    // Normalizar para o espaço do mapa placeholder (300x200 ou 600x400)
    // Centro: São Paulo (-23.55, -46.63)
    const centerLat = -23.55;
    const centerLng = -46.63;
    const scale = isFullscreen ? 4000 : 2000;

    const x = 50 + (lng - centerLng) * scale;
    const y = 50 + (lat - centerLat) * scale * -1;

    return {
      left: `${Math.max(5, Math.min(95, x))}%`,
      top: `${Math.max(5, Math.min(95, y))}%`,
    };
  };

  const mapContent = (
    <>
      {/* Mapa placeholder */}
      <div className="relative w-full h-full bg-gray-100 rounded-lg overflow-hidden">
        {/* Grid de fundo simulando mapa */}
        <div className="absolute inset-0 opacity-20">
          <svg width="100%" height="100%">
            <defs>
              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#94a3b8" strokeWidth="0.5" />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>

        {/* Label de desenvolvimento */}
        <div className="absolute top-2 left-2 px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">
          Mapa em desenvolvimento
        </div>

        {/* Marcadores dos técnicos */}
        <AnimatePresence>
          {techniciansWithLocation.map((tech) => {
            const position = getMarkerPosition(
              tech.localizacao!.lat,
              tech.localizacao!.lng
            );
            const isSelected = selectedTechnician === tech.id;

            return (
              <motion.div
                key={tech.id}
                className="absolute transform -translate-x-1/2 -translate-y-full cursor-pointer z-10"
                style={{
                  left: position.left,
                  top: position.top,
                }}
                initial={{ scale: 0, y: 20 }}
                animate={{
                  scale: isSelected ? 1.2 : 1,
                  y: 0,
                  zIndex: isSelected ? 20 : 10,
                }}
                exit={{ scale: 0, y: 20 }}
                whileHover={{ scale: 1.1 }}
                onClick={() => onSelectTechnician?.(isSelected ? undefined : tech.id)}
              >
                {/* Pin do marcador */}
                <div className="relative">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center shadow-lg
                      border-2 border-white transition-all ${isSelected ? 'ring-2 ring-blue-400' : ''}`}
                    style={{ backgroundColor: markerColors[tech.status] }}
                  >
                    {tech.status === 'em_deslocamento' ? (
                      <Navigation className="w-4 h-4 text-white" />
                    ) : (
                      <MapPin className="w-4 h-4 text-white" />
                    )}
                  </div>
                  {/* Ponta do pin */}
                  <div
                    className="absolute left-1/2 -bottom-1 w-0 h-0 transform -translate-x-1/2"
                    style={{
                      borderLeft: '6px solid transparent',
                      borderRight: '6px solid transparent',
                      borderTop: `8px solid ${markerColors[tech.status]}`,
                    }}
                  />
                </div>

                {/* Tooltip com nome */}
                <AnimatePresence>
                  {isSelected && (
                    <motion.div
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 5 }}
                      className="absolute left-1/2 transform -translate-x-1/2 -top-2
                        bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap shadow-lg"
                    >
                      {tech.nome}
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            );
          })}
        </AnimatePresence>

        {/* Mensagem se não houver técnicos com localização */}
        {techniciansWithLocation.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center text-gray-500">
              <MapPin className="w-8 h-8 mx-auto mb-2 text-gray-300" />
              <p>Nenhum técnico com localização disponível</p>
            </div>
          </div>
        )}
      </div>

      {/* Legenda */}
      {showLegend && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="absolute bottom-3 right-3 bg-white rounded-lg shadow-lg p-3 min-w-[140px]"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-medium text-gray-700">Legenda</span>
            <button
              onClick={() => setShowLegend(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
          <div className="space-y-1.5">
            {(Object.keys(STATUS_TECNICO_CONFIG) as StatusTecnico[]).map((status) => (
              <div key={status} className="flex items-center gap-2">
                <span
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: markerColors[status] }}
                />
                <span className="text-xs text-gray-600">
                  {STATUS_TECNICO_CONFIG[status].label}
                </span>
                <span className="text-xs text-gray-400 ml-auto">
                  ({statusStats[status]})
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Botão para mostrar legenda se estiver oculta */}
      {!showLegend && (
        <button
          onClick={() => setShowLegend(true)}
          className="absolute bottom-3 right-3 bg-white rounded-lg shadow-lg p-2
            text-gray-600 hover:text-gray-900 transition-colors"
          title="Mostrar legenda"
        >
          <Users className="w-4 h-4" />
        </button>
      )}

      {/* Controles */}
      <div className="absolute top-3 right-3 flex gap-2">
        {onRefresh && (
          <Button
            variant="secondary"
            size="sm"
            onClick={onRefresh}
            disabled={isLoading}
            className="bg-white shadow-lg"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        )}
        <Button
          variant="secondary"
          size="sm"
          onClick={() => setIsFullscreen(!isFullscreen)}
          className="bg-white shadow-lg"
        >
          {isFullscreen ? (
            <Minimize2 className="w-4 h-4" />
          ) : (
            <Maximize2 className="w-4 h-4" />
          )}
        </Button>
      </div>

      {/* Info do técnico selecionado */}
      <AnimatePresence>
        {selected && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="absolute bottom-3 left-3 bg-white rounded-lg shadow-lg p-3 max-w-[200px]"
          >
            <div className="flex items-start gap-2">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: markerColors[selected.status] }}
              >
                <span className="text-white text-xs font-medium">
                  {selected.nome.split(' ').map(n => n[0]).slice(0, 2).join('')}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-medium text-gray-900 text-sm truncate">
                  {selected.nome}
                </div>
                <Badge
                  variant={
                    selected.status === 'disponivel' ? 'success' :
                    selected.status === 'ocupado' ? 'danger' :
                    selected.status === 'em_deslocamento' ? 'info' : 'default'
                  }
                  size="sm"
                >
                  {STATUS_TECNICO_CONFIG[selected.status].label}
                </Badge>
                {selected.localizacao?.endereco && (
                  <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                    {selected.localizacao.endereco}
                  </p>
                )}
              </div>
              <button
                onClick={() => onSelectTechnician?.(undefined)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );

  // Modo fullscreen
  if (isFullscreen) {
    return (
      <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="relative w-full max-w-5xl h-[80vh] bg-white rounded-xl shadow-2xl overflow-hidden"
        >
          {mapContent}
        </motion.div>
      </div>
    );
  }

  return (
    <Card padding="none" className={`relative h-[300px] ${className}`}>
      {mapContent}
    </Card>
  );
}

export default TechnicianMap;
