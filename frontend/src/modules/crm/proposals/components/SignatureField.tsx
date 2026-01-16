'use client';

import { useRef, useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  PenTool,
  Eraser,
  Check,
  RotateCcw,
  Download,
  AlertCircle,
} from 'lucide-react';
import { Button } from '@/core/components/ui/Button';

interface SignatureFieldProps {
  onSignatureChange?: (signature: string | null) => void;
  onConfirm?: (signature: string) => void;
  initialSignature?: string;
  width?: number;
  height?: number;
  strokeColor?: string;
  strokeWidth?: number;
  backgroundColor?: string;
  label?: string;
  required?: boolean;
  disabled?: boolean;
}

interface Point {
  x: number;
  y: number;
}

export function SignatureField({
  onSignatureChange,
  onConfirm,
  initialSignature,
  width = 500,
  height = 200,
  strokeColor = '#1E3A5F',
  strokeWidth = 2,
  backgroundColor = '#FAFAFA',
  label = 'Assinatura',
  required = false,
  disabled = false,
}: SignatureFieldProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [hasSignature, setHasSignature] = useState(false);
  const [isConfirmed, setIsConfirmed] = useState(false);
  const [currentSignature, setCurrentSignature] = useState<string | null>(initialSignature || null);
  const [canvasSize, setCanvasSize] = useState({ width, height });

  // Ajustar canvas ao container
  useEffect(() => {
    const updateCanvasSize = () => {
      if (containerRef.current) {
        const containerWidth = containerRef.current.clientWidth;
        const ratio = height / width;
        setCanvasSize({
          width: containerWidth,
          height: containerWidth * ratio,
        });
      }
    };

    updateCanvasSize();
    window.addEventListener('resize', updateCanvasSize);
    return () => window.removeEventListener('resize', updateCanvasSize);
  }, [width, height]);

  // Inicializar canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Configurar canvas
    ctx.fillStyle = backgroundColor;
    ctx.fillRect(0, 0, canvasSize.width, canvasSize.height);

    // Carregar assinatura inicial se existir
    if (initialSignature) {
      const img = new Image();
      img.onload = () => {
        ctx.drawImage(img, 0, 0);
        setHasSignature(true);
        setIsConfirmed(true);
      };
      img.src = initialSignature;
    }
  }, [canvasSize, backgroundColor, initialSignature]);

  const getCoordinates = useCallback((e: React.MouseEvent | React.TouchEvent): Point | null => {
    const canvas = canvasRef.current;
    if (!canvas) return null;

    const rect = canvas.getBoundingClientRect();

    if ('touches' in e) {
      return {
        x: e.touches[0].clientX - rect.left,
        y: e.touches[0].clientY - rect.top,
      };
    }

    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    };
  }, []);

  const startDrawing = useCallback((e: React.MouseEvent | React.TouchEvent) => {
    if (disabled || isConfirmed) return;

    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx) return;

    const point = getCoordinates(e);
    if (!point) return;

    setIsDrawing(true);
    ctx.beginPath();
    ctx.moveTo(point.x, point.y);
    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = strokeWidth;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
  }, [disabled, isConfirmed, getCoordinates, strokeColor, strokeWidth]);

  const draw = useCallback((e: React.MouseEvent | React.TouchEvent) => {
    if (!isDrawing || disabled || isConfirmed) return;

    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx) return;

    const point = getCoordinates(e);
    if (!point) return;

    ctx.lineTo(point.x, point.y);
    ctx.stroke();
    setHasSignature(true);
  }, [isDrawing, disabled, isConfirmed, getCoordinates]);

  const stopDrawing = useCallback(() => {
    if (!isDrawing) return;

    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (ctx) {
      ctx.closePath();
    }

    setIsDrawing(false);

    // Salvar assinatura
    if (canvas && hasSignature) {
      const signature = canvas.toDataURL('image/png');
      setCurrentSignature(signature);
      onSignatureChange?.(signature);
    }
  }, [isDrawing, hasSignature, onSignatureChange]);

  const clearCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!canvas || !ctx) return;

    ctx.fillStyle = backgroundColor;
    ctx.fillRect(0, 0, canvasSize.width, canvasSize.height);

    setHasSignature(false);
    setIsConfirmed(false);
    setCurrentSignature(null);
    onSignatureChange?.(null);
  }, [canvasSize, backgroundColor, onSignatureChange]);

  const confirmSignature = useCallback(() => {
    if (!hasSignature || !currentSignature) return;

    setIsConfirmed(true);
    onConfirm?.(currentSignature);
  }, [hasSignature, currentSignature, onConfirm]);

  const downloadSignature = useCallback(() => {
    if (!currentSignature) return;

    const link = document.createElement('a');
    link.download = 'assinatura.png';
    link.href = currentSignature;
    link.click();
  }, [currentSignature]);

  return (
    <div className="w-full">
      {/* Label */}
      <div className="flex items-center justify-between mb-2">
        <label className="label flex items-center gap-1">
          <PenTool className="w-4 h-4" />
          {label}
          {required && <span className="text-red-500">*</span>}
        </label>
        {hasSignature && !isConfirmed && (
          <span className="text-xs text-amber-600 flex items-center gap-1">
            <AlertCircle className="w-3 h-3" />
            Confirme sua assinatura
          </span>
        )}
      </div>

      {/* Canvas Container */}
      <div
        ref={containerRef}
        className={`
          relative border-2 rounded-lg overflow-hidden transition-all
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          ${isConfirmed ? 'border-green-400 bg-green-50' : 'border-gray-300 border-dashed'}
          ${!disabled && !isConfirmed ? 'hover:border-conecta-escuro' : ''}
        `}
      >
        <canvas
          ref={canvasRef}
          width={canvasSize.width}
          height={canvasSize.height}
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseLeave={stopDrawing}
          onTouchStart={startDrawing}
          onTouchMove={draw}
          onTouchEnd={stopDrawing}
          className={`
            block w-full touch-none
            ${!disabled && !isConfirmed ? 'cursor-crosshair' : ''}
          `}
          style={{ backgroundColor }}
        />

        {/* Placeholder */}
        <AnimatePresence>
          {!hasSignature && !disabled && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 flex items-center justify-center pointer-events-none"
            >
              <p className="text-gray-400 text-sm">
                Desenhe sua assinatura aqui
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Confirmed Badge */}
        <AnimatePresence>
          {isConfirmed && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded text-xs font-medium flex items-center gap-1"
            >
              <Check className="w-3 h-3" />
              Confirmada
            </motion.div>
          )}
        </AnimatePresence>

        {/* Guidelines */}
        <div className="absolute bottom-4 left-4 right-4 border-b border-gray-300 border-dashed pointer-events-none" />
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between mt-3">
        <div className="flex gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={clearCanvas}
            disabled={disabled || !hasSignature}
            leftIcon={<Eraser className="w-4 h-4" />}
          >
            Limpar
          </Button>
          {isConfirmed && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsConfirmed(false)}
              disabled={disabled}
              leftIcon={<RotateCcw className="w-4 h-4" />}
            >
              Editar
            </Button>
          )}
        </div>

        <div className="flex gap-2">
          {isConfirmed && (
            <Button
              variant="ghost"
              size="sm"
              onClick={downloadSignature}
              leftIcon={<Download className="w-4 h-4" />}
            >
              Baixar
            </Button>
          )}
          {!isConfirmed && (
            <Button
              variant="primary"
              size="sm"
              onClick={confirmSignature}
              disabled={disabled || !hasSignature}
              leftIcon={<Check className="w-4 h-4" />}
            >
              Confirmar
            </Button>
          )}
        </div>
      </div>

      {/* Info Text */}
      <p className="text-xs text-gray-500 mt-2">
        {isConfirmed
          ? 'Assinatura confirmada. Clique em "Editar" para modificar.'
          : 'Use o mouse ou toque na tela para desenhar sua assinatura.'
        }
      </p>
    </div>
  );
}

// Componente wrapper para uso em formularios
export function SignatureFormField({
  value,
  onChange,
  error,
  ...props
}: SignatureFieldProps & {
  name?: string;
  value?: string;
  onChange?: (value: string | null) => void;
  error?: string;
}) {
  return (
    <div className="w-full">
      <SignatureField
        {...props}
        initialSignature={value}
        onSignatureChange={onChange}
      />
      {error && (
        <p className="error-text mt-1">{error}</p>
      )}
    </div>
  );
}

export default SignatureField;
