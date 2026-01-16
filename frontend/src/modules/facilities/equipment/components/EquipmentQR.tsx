'use client';

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  QrCode,
  Download,
  Printer,
  Copy,
  Check,
  Tag
} from 'lucide-react';
import type { Equipment } from '../types/equipment.types';

interface EquipmentQRProps {
  equipment: Equipment;
  size?: 'sm' | 'md' | 'lg';
  showDetails?: boolean;
  onDownload?: () => void;
  onPrint?: () => void;
}

const sizeConfig = {
  sm: { qr: 120, container: 'w-36' },
  md: { qr: 180, container: 'w-52' },
  lg: { qr: 240, container: 'w-72' }
};

export function EquipmentQR({
  equipment,
  size = 'md',
  showDetails = true,
  onDownload,
  onPrint
}: EquipmentQRProps) {
  const [copied, setCopied] = React.useState(false);
  const config = sizeConfig[size];

  // Gerar SVG do QR Code (simplificado - em producao usar qrcode library)
  const qrCodeSVG = useMemo(() => {
    // Em producao, usar biblioteca como 'qrcode' ou 'react-qr-code'
    // Este e um placeholder visual
    const modules = 21; // QR code version 1
    // moduleSize removido - nao utilizado

    // Gerar pattern pseudo-aleatorio baseado no codigo
    const pattern: boolean[][] = [];
    const seed = equipment.qr_code.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);

    for (let row = 0; row < modules; row++) {
      pattern[row] = [];
      for (let col = 0; col < modules; col++) {
        // Finder patterns (cantos)
        const isFinderPattern =
          (row < 7 && col < 7) ||
          (row < 7 && col >= modules - 7) ||
          (row >= modules - 7 && col < 7);

        // Timing patterns
        const isTimingPattern = row === 6 || col === 6;

        if (isFinderPattern) {
          const innerRow = row % 7;
          const innerCol = col % 7;
          pattern[row][col] =
            innerRow === 0 || innerRow === 6 ||
            innerCol === 0 || innerCol === 6 ||
            (innerRow >= 2 && innerRow <= 4 && innerCol >= 2 && innerCol <= 4);
        } else if (isTimingPattern) {
          pattern[row][col] = (row + col) % 2 === 0;
        } else {
          // Data area - pseudo-random based on position and seed
          pattern[row][col] = ((row * modules + col + seed) % 3) === 0;
        }
      }
    }

    return (
      <svg
        width={config.qr}
        height={config.qr}
        viewBox={`0 0 ${modules} ${modules}`}
        className="rounded"
      >
        <rect width={modules} height={modules} fill="white" />
        {pattern.map((row, rowIndex) =>
          row.map((cell, colIndex) =>
            cell ? (
              <rect
                key={`${rowIndex}-${colIndex}`}
                x={colIndex}
                y={rowIndex}
                width={1}
                height={1}
                fill="#1f2937"
              />
            ) : null
          )
        )}
      </svg>
    );
  }, [equipment.qr_code, config.qr]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(equipment.qr_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Erro ao copiar:', err);
    }
  };

  const handleDownload = () => {
    // Em producao, gerar imagem PNG do QR code
    onDownload?.();
  };

  const handlePrint = () => {
    // Em producao, abrir dialog de impressao com etiqueta
    onPrint?.();
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`${config.container} bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden`}
    >
      {/* QR Code Display */}
      <div className="p-4 flex flex-col items-center bg-gradient-to-b from-gray-50 to-white">
        <div className="p-3 bg-white rounded-lg shadow-inner border border-gray-100">
          {qrCodeSVG}
        </div>

        {/* QR Code String */}
        <div className="mt-3 flex items-center space-x-2">
          <code className="text-xs font-mono text-gray-600 bg-gray-100 px-2 py-1 rounded">
            {equipment.qr_code}
          </code>
          <button
            onClick={handleCopy}
            className="p-1 hover:bg-gray-100 rounded transition-colors"
            title="Copiar codigo"
          >
            {copied ? (
              <Check className="w-4 h-4 text-green-500" />
            ) : (
              <Copy className="w-4 h-4 text-gray-400" />
            )}
          </button>
        </div>
      </div>

      {/* Equipment Details */}
      {showDetails && (
        <div className="p-3 border-t border-gray-100 bg-gray-50">
          <h4 className="font-medium text-gray-900 text-sm truncate">
            {equipment.nome}
          </h4>
          <p className="text-xs text-gray-500 mt-0.5">{equipment.codigo}</p>

          {equipment.rfid_tag && (
            <div className="mt-2 flex items-center space-x-1.5 text-xs text-blue-600">
              <Tag className="w-3 h-3" />
              <span className="font-mono">{equipment.rfid_tag}</span>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="px-3 py-2 border-t border-gray-100 flex items-center justify-center space-x-2">
        <button
          onClick={handleDownload}
          className="flex items-center space-x-1 px-2 py-1.5 text-xs text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          title="Baixar QR Code"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Baixar</span>
        </button>
        <button
          onClick={handlePrint}
          className="flex items-center space-x-1 px-2 py-1.5 text-xs text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          title="Imprimir etiqueta"
        >
          <Printer className="w-3.5 h-3.5" />
          <span>Imprimir</span>
        </button>
      </div>
    </motion.div>
  );
}

// Componente para scanner de QR
interface QRScannerProps {
  onScan: (code: string) => void;
  onClose: () => void;
}

export function QRScanner({ onScan, onClose }: QRScannerProps) {
  // Em producao, usar @zxing/browser ou html5-qrcode
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center"
    >
      <div className="bg-white rounded-xl p-6 max-w-sm w-full mx-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900">Escanear QR Code</h3>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <span className="sr-only">Fechar</span>
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Camera Preview Placeholder */}
        <div className="aspect-square bg-gray-900 rounded-lg flex items-center justify-center relative overflow-hidden">
          <div className="absolute inset-8 border-2 border-white/50 rounded-lg" />
          <QrCode className="w-16 h-16 text-white/30" />
          <div className="absolute inset-x-0 top-1/2 h-0.5 bg-blue-500/50 animate-pulse" />
        </div>

        <p className="text-sm text-gray-500 text-center mt-4">
          Posicione o QR Code dentro da area de leitura
        </p>

        {/* Manual Input */}
        <div className="mt-4 pt-4 border-t border-gray-200">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Ou digite o codigo manualmente:
          </label>
          <div className="flex space-x-2">
            <input
              type="text"
              placeholder="QR-EQP-001"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  const value = (e.target as HTMLInputElement).value;
                  if (value) onScan(value);
                }
              }}
            />
            <button
              onClick={() => {
                const input = document.querySelector('input') as HTMLInputElement;
                if (input?.value) onScan(input.value);
              }}
              className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              Buscar
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export default EquipmentQR;
