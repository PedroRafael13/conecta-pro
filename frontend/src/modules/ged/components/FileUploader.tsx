import React, { useCallback, useState } from 'react';
import { Upload, X, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { useUpload } from '../hooks';
import type { UploadProgress } from '../types';

interface FileUploaderProps {
  onUploadComplete?: () => void;
  acceptedTypes?: string[];
  maxSize?: number; // MB
}

export const FileUploader: React.FC<FileUploaderProps> = ({
  acceptedTypes = ['.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg'],
  maxSize = 10,
}) => {
  const [dragActive, setDragActive] = useState(false);
  const { uploads, uploadFiles, removeUpload } = useUpload();

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleFiles = useCallback((files: File[]) => {
    const validFiles = files.filter(file => {
      // Verificar tipo
      const extension = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!acceptedTypes.includes(extension)) {
        alert(`Tipo de arquivo não suportado: ${extension}`);
        return false;
      }

      // Verificar tamanho
      if (file.size > maxSize * 1024 * 1024) {
        alert(`Arquivo muito grande: ${file.name}. Máximo ${maxSize}MB`);
        return false;
      }

      return true;
    });

    if (validFiles.length > 0) {
      uploadFiles(validFiles);
    }
  }, [acceptedTypes, maxSize, uploadFiles]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(Array.from(e.dataTransfer.files));
    }
  }, [handleFiles]);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(Array.from(e.target.files));
    }
  };

  const getStatusIcon = (upload: UploadProgress) => {
    switch (upload.status) {
      case 'uploading':
      case 'processing':
        return <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-600" />;
      default:
        return <FileText className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusText = (upload: UploadProgress) => {
    switch (upload.status) {
      case 'uploading':
        return `Enviando... ${upload.progress}%`;
      case 'processing':
        return 'Processando OCR + IA...';
      case 'completed':
        return 'Concluído';
      case 'error':
        return upload.error || 'Erro';
      default:
        return 'Aguardando...';
    }
  };

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <div
        className={`border-2 border-dashed rounded-lg p-6 transition-colors ${
          dragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <div className="text-center">
          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <div className="text-sm text-gray-600">
            <label
              htmlFor="file-upload"
              className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500"
            >
              <span>Clique para enviar</span>
              <input
                id="file-upload"
                name="file-upload"
                type="file"
                className="sr-only"
                multiple
                accept={acceptedTypes.join(',')}
                onChange={handleFileInput}
              />
            </label>
            <p className="pl-1 inline">ou arraste arquivos aqui</p>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Tipos aceitos: {acceptedTypes.join(', ')} | Máximo: {maxSize}MB por arquivo
          </p>
        </div>
      </div>

      {/* Upload Progress */}
      {uploads.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Uploads</h4>
          <div className="space-y-3">
            {uploads.map((upload) => (
              <div
                key={upload.fileId}
                className="flex items-center justify-between p-2 bg-gray-50 rounded"
              >
                <div className="flex items-center space-x-3 flex-1">
                  {getStatusIcon(upload)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {upload.fileName}
                    </p>
                    <p className="text-xs text-gray-500">
                      {getStatusText(upload)}
                    </p>
                  </div>
                </div>

                {/* Progress Bar */}
                {(upload.status === 'uploading' || upload.status === 'processing') && (
                  <div className="w-24 bg-gray-200 rounded-full h-2 mx-3">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ 
                        width: `${upload.status === 'processing' ? 100 : upload.progress}%` 
                      }}
                    />
                  </div>
                )}

                {/* Remove Button */}
                <button
                  onClick={() => removeUpload(upload.fileId)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
