import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MapPin,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Navigation,
  Building2,
  Users,
  X,
} from 'lucide-react';
import type { Posto } from '../types/postos.types';

interface PostoMapProps {
  postos: Posto[];
  selectedPosto?: Posto | null;
  onSelectPosto?: (posto: Posto) => void;
  height?: string;
  showControls?: boolean;
}

export const PostoMap: React.FC<PostoMapProps> = ({
  postos,
  selectedPosto,
  onSelectPosto,
  height = '400px',
  showControls = true,
}) => {
  const [zoom, setZoom] = useState(1);
  const [hoveredPosto, setHoveredPosto] = useState<Posto | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Calcular bounds do mapa baseado nos postos
  const getMapBounds = () => {
    const postosComCoordenadas = postos.filter((p) => p.coordenadas);
    if (postosComCoordenadas.length === 0) {
      return { minLat: -23.6, maxLat: -23.5, minLng: -46.8, maxLng: -46.5 };
    }

    const lats = postosComCoordenadas.map((p) => p.coordenadas!.lat);
    const lngs = postosComCoordenadas.map((p) => p.coordenadas!.lng);

    return {
      minLat: Math.min(...lats) - 0.05,
      maxLat: Math.max(...lats) + 0.05,
      minLng: Math.min(...lngs) - 0.05,
      maxLng: Math.max(...lngs) + 0.05,
    };
  };

  const bounds = getMapBounds();

  // Converter coordenadas para posicao no mapa (0-100%)
  const coordsToPosition = (lat: number, lng: number) => {
    const x = ((lng - bounds.minLng) / (bounds.maxLng - bounds.minLng)) * 100;
    const y = ((bounds.maxLat - lat) / (bounds.maxLat - bounds.minLat)) * 100;
    return { x, y };
  };

  const getStatusColor = (status: string) => {
    const colors = {
      ativo: 'bg-green-500 border-green-600',
      inativo: 'bg-gray-400 border-gray-500',
      em_implantacao: 'bg-yellow-500 border-yellow-600',
      suspenso: 'bg-red-500 border-red-600',
    };
    return colors[status as keyof typeof colors] || colors.inativo;
  };

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 0.25, 2));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 0.25, 0.5));

  const mapContent = (
    <div
      className="relative w-full h-full bg-gradient-to-br from-blue-50 to-blue-100 overflow-hidden"
      style={{ transform: `scale(${zoom})`, transformOrigin: 'center' }}
    >
      {/* Grid de fundo simulando mapa */}
      <div className="absolute inset-0">
        <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern
              id="grid"
              width="40"
              height="40"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 40 0 L 0 0 0 40"
                fill="none"
                stroke="#e0e7ff"
                strokeWidth="1"
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>
      </div>

      {/* Ruas simuladas */}
      <svg className="absolute inset-0 w-full h-full">
        <line
          x1="10%"
          y1="30%"
          x2="90%"
          y2="30%"
          stroke="#cbd5e1"
          strokeWidth="4"
          strokeLinecap="round"
        />
        <line
          x1="10%"
          y1="60%"
          x2="90%"
          y2="60%"
          stroke="#cbd5e1"
          strokeWidth="4"
          strokeLinecap="round"
        />
        <line
          x1="30%"
          y1="10%"
          x2="30%"
          y2="90%"
          stroke="#cbd5e1"
          strokeWidth="4"
          strokeLinecap="round"
        />
        <line
          x1="70%"
          y1="10%"
          x2="70%"
          y2="90%"
          stroke="#cbd5e1"
          strokeWidth="4"
          strokeLinecap="round"
        />
        {/* Avenida principal */}
        <line
          x1="0%"
          y1="50%"
          x2="100%"
          y2="50%"
          stroke="#94a3b8"
          strokeWidth="8"
          strokeLinecap="round"
        />
      </svg>

      {/* Marcadores dos postos */}
      {postos
        .filter((p) => p.coordenadas)
        .map((posto) => {
          const pos = coordsToPosition(
            posto.coordenadas!.lat,
            posto.coordenadas!.lng
          );
          const isSelected = selectedPosto?.id === posto.id;
          const isHovered = hoveredPosto?.id === posto.id;

          return (
            <motion.div
              key={posto.id}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute transform -translate-x-1/2 -translate-y-full cursor-pointer"
              style={{ left: `${pos.x}%`, top: `${pos.y}%` }}
              onMouseEnter={() => setHoveredPosto(posto)}
              onMouseLeave={() => setHoveredPosto(null)}
              onClick={() => onSelectPosto?.(posto)}
            >
              {/* Marcador */}
              <motion.div
                animate={{
                  scale: isSelected || isHovered ? 1.2 : 1,
                }}
                className="relative"
              >
                <div
                  className={`w-8 h-8 rounded-full ${getStatusColor(
                    posto.status
                  )} border-2 shadow-lg flex items-center justify-center`}
                >
                  <MapPin className="w-4 h-4 text-white" />
                </div>

                {/* Pulso animado para posto selecionado */}
                {isSelected && (
                  <motion.div
                    className="absolute inset-0 rounded-full bg-blue-400"
                    initial={{ scale: 1, opacity: 0.5 }}
                    animate={{ scale: 2, opacity: 0 }}
                    transition={{
                      duration: 1.5,
                      repeat: Infinity,
                      ease: 'easeOut',
                    }}
                  />
                )}

                {/* Pin inferior */}
                <div
                  className={`absolute left-1/2 -bottom-1 w-0 h-0 transform -translate-x-1/2 border-l-4 border-r-4 border-t-8 border-l-transparent border-r-transparent ${
                    posto.status === 'ativo'
                      ? 'border-t-green-600'
                      : posto.status === 'em_implantacao'
                      ? 'border-t-yellow-600'
                      : posto.status === 'suspenso'
                      ? 'border-t-red-600'
                      : 'border-t-gray-500'
                  }`}
                />
              </motion.div>

              {/* Tooltip */}
              <AnimatePresence>
                {(isHovered || isSelected) && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 z-10"
                  >
                    <div className="bg-white rounded-lg shadow-xl border border-gray-200 p-3 min-w-[200px]">
                      <h4 className="font-semibold text-gray-900 text-sm mb-1">
                        {posto.nome}
                      </h4>
                      <div className="flex items-center gap-1 text-xs text-gray-500 mb-2">
                        <Building2 className="w-3 h-3" />
                        {posto.cliente}
                      </div>
                      <div className="flex items-center gap-1 text-xs text-gray-500">
                        <Users className="w-3 h-3" />
                        {posto.turnos.reduce(
                          (acc, t) => acc + t.profissionais_alocados,
                          0
                        )}{' '}
                        profissionais
                      </div>
                      {/* Triangulo */}
                      <div className="absolute left-1/2 -bottom-2 transform -translate-x-1/2 w-0 h-0 border-l-8 border-r-8 border-t-8 border-l-transparent border-r-transparent border-t-white" />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}

      {/* Label do mapa */}
      <div className="absolute bottom-2 left-2 bg-white/80 backdrop-blur-sm rounded-lg px-3 py-1.5 text-xs text-gray-600 flex items-center gap-1.5">
        <Navigation className="w-3.5 h-3.5" />
        Regiao Metropolitana de Sao Paulo
      </div>
    </div>
  );

  return (
    <div className="relative" style={{ height: isFullscreen ? '100vh' : height }}>
      {/* Container do Mapa */}
      <div
        className={`w-full h-full rounded-xl border border-gray-200 overflow-hidden ${
          isFullscreen ? 'fixed inset-0 z-50' : ''
        }`}
      >
        {mapContent}

        {/* Controles */}
        {showControls && (
          <div className="absolute top-4 right-4 flex flex-col gap-2">
            <button
              onClick={handleZoomIn}
              className="p-2 bg-white rounded-lg shadow-md hover:bg-gray-50 transition-colors"
              title="Aumentar zoom"
            >
              <ZoomIn className="w-4 h-4 text-gray-600" />
            </button>
            <button
              onClick={handleZoomOut}
              className="p-2 bg-white rounded-lg shadow-md hover:bg-gray-50 transition-colors"
              title="Diminuir zoom"
            >
              <ZoomOut className="w-4 h-4 text-gray-600" />
            </button>
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 bg-white rounded-lg shadow-md hover:bg-gray-50 transition-colors"
              title={isFullscreen ? 'Sair da tela cheia' : 'Tela cheia'}
            >
              {isFullscreen ? (
                <X className="w-4 h-4 text-gray-600" />
              ) : (
                <Maximize2 className="w-4 h-4 text-gray-600" />
              )}
            </button>
          </div>
        )}

        {/* Legenda */}
        <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg shadow-md p-3">
          <h4 className="text-xs font-semibold text-gray-700 mb-2">Legenda</h4>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2 text-xs text-gray-600">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              Ativo
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-600">
              <div className="w-3 h-3 rounded-full bg-yellow-500" />
              Em Implantacao
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-600">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              Suspenso
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-600">
              <div className="w-3 h-3 rounded-full bg-gray-400" />
              Inativo
            </div>
          </div>
        </div>
      </div>

      {/* Contador de postos */}
      <div className="absolute top-4 left-4 bg-white rounded-lg shadow-md px-4 py-2">
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-blue-600" />
          <span className="text-sm font-medium text-gray-700">
            {postos.filter((p) => p.coordenadas).length} postos no mapa
          </span>
        </div>
      </div>
    </div>
  );
};

export default PostoMap;
