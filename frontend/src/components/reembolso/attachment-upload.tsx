'use client';

import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { getErrorMessage } from '@/lib/api';
import { Upload, Loader2, AlertCircle, FileImage, FileText, X } from 'lucide-react';

interface AttachmentUploadProps {
  onUpload: (file: File) => Promise<void>;
  disabled?: boolean;
  accept?: string;
  maxSize?: number; // em MB
}

export function AttachmentUpload({
  onUpload,
  disabled = false,
  accept = '.pdf,.jpg,.jpeg,.png,.gif,.webp',
  maxSize = 10, // 10MB padrao
}: AttachmentUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    // Valida tamanho
    const maxBytes = maxSize * 1024 * 1024;
    if (file.size > maxBytes) {
      return `Arquivo muito grande. Maximo: ${maxSize}MB`;
    }

    // Valida tipo
    const allowedTypes = [
      'image/jpeg',
      'image/png',
      'image/gif',
      'image/webp',
      'application/pdf',
    ];
    if (!allowedTypes.includes(file.type)) {
      return 'Tipo de arquivo nao permitido. Use: PDF, JPG, PNG, GIF ou WebP';
    }

    return null;
  };

  const handleFileSelect = (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setError(null);
    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setError(null);

    try {
      await onUpload(selectedFile);
      setSelectedFile(null);
      if (inputRef.current) {
        inputRef.current.value = '';
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const clearSelection = () => {
    setSelectedFile(null);
    setError(null);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) {
      return <FileImage className="w-8 h-8 text-blue-500" />;
    }
    return <FileText className="w-8 h-8 text-red-500" />;
  };

  return (
    <div className="space-y-3">
      {/* Drop zone */}
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-6 text-center transition-colors
          ${dragActive ? 'border-[hsl(var(--primary))] bg-[hsl(var(--primary))]/5' : 'border-[hsl(var(--border))]'}
          ${disabled || isUploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:border-[hsl(var(--primary))]/50'}
        `}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !disabled && !isUploading && inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleChange}
          disabled={disabled || isUploading}
          className="hidden"
        />

        {selectedFile ? (
          <div className="flex items-center justify-center gap-3">
            {getFileIcon(selectedFile.type)}
            <div className="text-left">
              <p className="text-sm font-medium text-[hsl(var(--foreground))]">
                {selectedFile.name}
              </p>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                {formatFileSize(selectedFile.size)}
              </p>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                clearSelection();
              }}
              className="text-red-500 hover:text-red-600 hover:bg-red-500/10"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        ) : (
          <>
            <Upload className="w-8 h-8 text-[hsl(var(--muted-foreground))] mx-auto mb-2" />
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              Arraste um arquivo aqui ou{' '}
              <span className="text-[hsl(var(--primary))]">clique para selecionar</span>
            </p>
            <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">
              PDF, JPG, PNG, GIF, WebP (max {maxSize}MB)
            </p>
          </>
        )}
      </div>

      {/* Error message */}
      {error && (
        <div className="flex items-center gap-2 text-red-500 text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Upload button */}
      {selectedFile && (
        <Button
          type="button"
          variant="primary"
          onClick={handleUpload}
          disabled={isUploading || disabled}
          className="w-full"
        >
          {isUploading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Enviando...
            </>
          ) : (
            <>
              <Upload className="w-4 h-4 mr-2" />
              Enviar Anexo
            </>
          )}
        </Button>
      )}
    </div>
  );
}
