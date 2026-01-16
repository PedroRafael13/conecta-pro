import { useState, useEffect } from 'react';
import type { Document, SearchFilters } from '../types';
import { api } from '@/core/api';

interface DocumentsResponse {
  documents: Document[];
  total: number;
}

export const useDocuments = (filters?: SearchFilters) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const data = await api.get<DocumentsResponse>('/ged/documents', { params: filters });
      setDocuments(data.documents);
      setTotal(data.total);
      setError(null);
    } catch (err) {
      setError('Erro ao carregar documentos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]);

  const deleteDocument = async (id: string) => {
    try {
      await api.delete(`/ged/documents/${id}`);
      setDocuments(docs => docs.filter(doc => doc.id !== id));
    } catch (err) {
      console.error('Erro ao deletar documento:', err);
      throw err;
    }
  };

  const updateDocument = async (id: string, updates: Partial<Document>) => {
    try {
      const updatedDoc = await api.patch<Document>(`/ged/documents/${id}`, updates);
      setDocuments(docs =>
        docs.map(doc => doc.id === id ? { ...doc, ...updatedDoc } : doc)
      );
      return updatedDoc;
    } catch (err) {
      console.error('Erro ao atualizar documento:', err);
      throw err;
    }
  };

  return {
    documents,
    loading,
    error,
    total,
    loadDocuments,
    deleteDocument,
    updateDocument,
  };
};
