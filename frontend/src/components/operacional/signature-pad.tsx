'use client';

import { Eraser, Download, Check, RotateCcw } from 'lucide-react';
import { useRef, useEffect, useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';

interface SignaturePadProps {
  onSign: (signatureData: string, location?: { latitude: number; longitude: number }) => void;
  onCancel?: () => void;
  width?: number;
  height?: number;
  disabled?: boolean;
  showLocationRequest?: boolean;
  signerName?: string;
  documentTitle?: string;
}

export function SignaturePad({
  onSign,
  onCancel,
  width = 500,
  height = 200,
  disabled = false,
  showLocationRequest = true,
  signerName,
  documentTitle,
}: SignaturePadProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [hasSignature, setHasSignature] = useState(false);
  const [location, setLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [locationError, setLocationError] = useState<string | null>(null);
  const [isGettingLocation, setIsGettingLocation] = useState(false);

  // Inicializa o canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Configura o canvas
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, width, height);
    ctx.strokeStyle = '#1a1a1a';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    // Desenha linha guia
    ctx.beginPath();
    ctx.strokeStyle = '#e5e5e5';
    ctx.lineWidth = 1;
    ctx.moveTo(20, height - 40);
    ctx.lineTo(width - 20, height - 40);
    ctx.stroke();

    // Texto "Assine aqui"
    ctx.fillStyle = '#999999';
    ctx.font = '12px sans-serif';
    ctx.fillText('Assine acima da linha', 20, height - 20);

    // Restaura configurações para desenho
    ctx.strokeStyle = '#1a1a1a';
    ctx.lineWidth = 2;
  }, [width, height]);

  // Obtém localização
  const getLocation = useCallback(() => {
    if (!showLocationRequest) return;

    setIsGettingLocation(true);
    setLocationError(null);

    if (!navigator.geolocation) {
      setLocationError('Geolocalização não suportada');
      setIsGettingLocation(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
        setIsGettingLocation(false);
      },
      (error) => {
        setLocationError('Não foi possível obter localização');
        setIsGettingLocation(false);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }, [showLocationRequest]);

  useEffect(() => {
    if (showLocationRequest) {
      getLocation();
    }
  }, [showLocationRequest, getLocation]);

  // Funções de desenho
  const getCoordinates = (e: React.MouseEvent | React.TouchEvent) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };

    const rect = canvas.getBoundingClientRect();

    if ('touches' in e) {
      return {
        x: e.touches[0]!.clientX - rect.left,
        y: e.touches[0]!.clientY - rect.top,
      };
    }

    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    };
  };

  const startDrawing = (e: React.MouseEvent | React.TouchEvent) => {
    if (disabled) return;

    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!ctx) return;

    const { x, y } = getCoordinates(e);

    ctx.beginPath();
    ctx.moveTo(x, y);
    setIsDrawing(true);
  };

  const draw = (e: React.MouseEvent | React.TouchEvent) => {
    if (!isDrawing || disabled) return;

    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!ctx) return;

    const { x, y } = getCoordinates(e);

    ctx.lineTo(x, y);
    ctx.stroke();
    setHasSignature(true);
  };

  const stopDrawing = () => {
    setIsDrawing(false);
  };

  // Limpa o canvas
  const clearCanvas = () => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    if (!ctx) return;

    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, width, height);

    // Redesenha linha guia
    ctx.beginPath();
    ctx.strokeStyle = '#e5e5e5';
    ctx.lineWidth = 1;
    ctx.moveTo(20, height - 40);
    ctx.lineTo(width - 20, height - 40);
    ctx.stroke();

    ctx.fillStyle = '#999999';
    ctx.font = '12px sans-serif';
    ctx.fillText('Assine acima da linha', 20, height - 20);

    ctx.strokeStyle = '#1a1a1a';
    ctx.lineWidth = 2;

    setHasSignature(false);
  };

  // Confirma assinatura
  const handleConfirm = () => {
    if (!hasSignature) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const signatureData = canvas.toDataURL('image/png');
    onSign(signatureData, location || undefined);
  };

  return (
    <div className="space-y-4">
      {/* Informações do documento */}
      {(signerName || documentTitle) && (
        <div className="bg-[hsl(var(--muted))] rounded-lg p-4 space-y-2">
          {documentTitle && (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              <strong>Documento:</strong> {documentTitle}
            </p>
          )}
          {signerName && (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              <strong>Signatário:</strong> {signerName}
            </p>
          )}
        </div>
      )}

      {/* Canvas de assinatura */}
      <div className="border border-[hsl(var(--border))] rounded-lg overflow-hidden">
        <canvas
          ref={canvasRef}
          width={width}
          height={height}
          className={`touch-none ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-crosshair'}`}
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseLeave={stopDrawing}
          onTouchStart={startDrawing}
          onTouchMove={draw}
          onTouchEnd={stopDrawing}
        />
      </div>

      {/* Localização */}
      {showLocationRequest && (
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            {isGettingLocation ? (
              <span className="text-[hsl(var(--muted-foreground))]">Obtendo localização...</span>
            ) : location ? (
              <span className="text-green-500">
                Localização registrada ({location.latitude.toFixed(4)}, {location.longitude.toFixed(4)})
              </span>
            ) : locationError ? (
              <span className="text-yellow-500">{locationError}</span>
            ) : null}
          </div>
          {!location && !isGettingLocation && (
            <Button variant="ghost" size="sm" onClick={getLocation}>
              <RotateCcw className="w-4 h-4 mr-1" />
              Tentar novamente
            </Button>
          )}
        </div>
      )}

      {/* Ações */}
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          size="sm"
          onClick={clearCanvas}
          disabled={disabled || !hasSignature}
        >
          <Eraser className="w-4 h-4 mr-2" />
          Limpar
        </Button>

        <div className="flex items-center gap-2">
          {onCancel && (
            <Button variant="outline" onClick={onCancel} disabled={disabled}>
              Cancelar
            </Button>
          )}
          <Button
            variant="primary"
            onClick={handleConfirm}
            disabled={disabled || !hasSignature}
          >
            <Check className="w-4 h-4 mr-2" />
            Confirmar Assinatura
          </Button>
        </div>
      </div>

      {/* Aviso legal */}
      <p className="text-xs text-[hsl(var(--muted-foreground))] text-center">
        Ao assinar, você declara estar ciente e de acordo com o conteúdo do documento.
        Esta assinatura tem validade jurídica conforme MP 2.200-2/2001.
      </p>
    </div>
  );
}
