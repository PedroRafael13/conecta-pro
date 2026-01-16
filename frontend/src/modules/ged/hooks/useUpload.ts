import { useState, useCallback } from 'react';
import type { UploadProgress } from '../types';
import { api } from '@/core/api';

interface UploadResponse {
  id: string;
}

interface StatusResponse {
  status: 'processing' | 'completed' | 'error';
}

export const useUpload = () => {
  const [uploads, setUploads] = useState<UploadProgress[]>([]);

  const pollProcessing = async (documentId: string, uploadId: string) => {
    const checkStatus = async () => {
      try {
        const data = await api.get<StatusResponse>(`/ged/documents/${documentId}/status`);

        if (data.status === 'completed') {
          setUploads(prev =>
            prev.map(upload =>
              upload.fileId === uploadId
                ? { ...upload, status: 'completed' }
                : upload
            )
          );
        } else if (data.status === 'error') {
          setUploads(prev =>
            prev.map(upload =>
              upload.fileId === uploadId
                ? {
                    ...upload,
                    status: 'error',
                    error: 'Erro no processamento'
                  }
                : upload
            )
          );
        } else {
          // Ainda processando, tentar novamente
          setTimeout(checkStatus, 2000);
        }
      } catch (error) {
        console.error('Erro ao verificar status:', error);
      }
    };

    setTimeout(checkStatus, 1000);
  };

  const uploadFiles = useCallback(async (files: File[]) => {
    const newUploads: UploadProgress[] = files.map(file => ({
      fileId: crypto.randomUUID(),
      fileName: file.name,
      progress: 0,
      status: 'uploading',
    }));

    setUploads(prev => [...prev, ...newUploads]);

    // Upload cada arquivo
    const uploadPromises = files.map(async (file, index) => {
      const formData = new FormData();
      formData.append('file', file);

      const uploadId = newUploads[index].fileId;

      try {
        const uploadData = await api.post<UploadResponse>('/ged/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
              setUploads(prev =>
                prev.map(upload =>
                  upload.fileId === uploadId
                    ? { ...upload, progress }
                    : upload
                )
              );
            }
          },
        });

        // Marcar como processando (OCR + IA)
        setUploads(prev =>
          prev.map(upload =>
            upload.fileId === uploadId
              ? { ...upload, status: 'processing', progress: 100 }
              : upload
          )
        );

        // Aguardar processamento OCR
        await pollProcessing(uploadData.id, uploadId);

      } catch {
        setUploads(prev =>
          prev.map(upload =>
            upload.fileId === uploadId
              ? {
                  ...upload,
                  status: 'error',
                  error: 'Erro no upload'
                }
              : upload
          )
        );
      }
    });

    await Promise.all(uploadPromises);
  }, []);

  const clearCompleted = useCallback(() => {
    setUploads(prev => prev.filter(upload => upload.status !== 'completed'));
  }, []);

  const removeUpload = useCallback((fileId: string) => {
    setUploads(prev => prev.filter(upload => upload.fileId !== fileId));
  }, []);

  return {
    uploads,
    uploadFiles,
    clearCompleted,
    removeUpload,
  };
};
