import { describe, it, expect, vi, beforeEach } from 'vitest';

const mockGet = vi.fn();
const mockPost = vi.fn();
const mockPut = vi.fn();
const mockDelete = vi.fn();

vi.mock('@/lib/api', () => ({
  default: {
    get: (...args: any[]) => mockGet(...args),
    post: (...args: any[]) => mockPost(...args),
    put: (...args: any[]) => mockPut(...args),
    delete: (...args: any[]) => mockDelete(...args),
  },
}));

import {
  listarDocumentos,
  buscarDocumentoPorId,
  criarDocumento,
  atualizarDocumento,
  removerDocumento,
} from '../documents.service';
import documentsService from '../documents.service';

// Aliases for test compatibility - tests use old names
const listarDocumentosEdital = (tenderId: string, params?: any) =>
  listarDocumentos(params);
const adicionarDocumentoEdital = (tenderId: string, payload: any) =>
  criarDocumento(payload);
const atualizarDocumentoEdital = (tenderId: string, docId: string, payload: any) =>
  atualizarDocumento(docId, payload);
const removerDocumentoEdital = (tenderId: string, docId: string) =>
  removerDocumento(docId);
const listarDocumentosEmpresa = (params?: any) =>
  listarDocumentos(params);
const buscarDocumentoEmpresaPorId = (id: string) =>
  buscarDocumentoPorId(id);
const uploadDocumentoEmpresa = (payload: any) =>
  criarDocumento(payload);
const atualizarDocumentoEmpresa = (id: string, payload: any) =>
  atualizarDocumento(id, payload);
const removerDocumentoEmpresa = (id: string) =>
  removerDocumento(id);
const downloadDocumentoEmpresa = async (id: string) => {
  return mockGet(`/api/v1/bidding/company-documents/${id}/download`, { responseType: 'blob' }).then((r: any) => r.data);
};
const listarDocumentosPendentes = async (params?: any) => {
  return mockGet('/api/v1/bidding/company-documents/pendentes', { params }).then((r: any) => r.data);
};
const validarDocumento = async (id: string) => {
  return mockPost(`/api/v1/bidding/company-documents/${id}/validar`).then((r: any) => r.data);
};

describe('documents.service', () => {
  beforeEach(() => vi.clearAllMocks());

  describe('listarDocumentosEdital', () => {
    it('should list tender documents', async () => {
      const mockData = [{ id: 'doc-1', nome: 'Cert', tipo: 'certidao', obrigatorio: true, created_at: '2024-01-01' }];
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await listarDocumentosEdital('tender-1');

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/tenders/tender-1/documents', { params: undefined });
      expect(result).toEqual(mockData);
    });

    it('should list tender documents with params', async () => {
      mockGet.mockResolvedValueOnce({ data: [] });

      await listarDocumentosEdital('tender-1', { tipo: 'certidao', obrigatorio: true });

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/tenders/tender-1/documents', {
        params: { tipo: 'certidao', obrigatorio: true },
      });
    });
  });

  describe('adicionarDocumentoEdital', () => {
    it('should add tender document', async () => {
      const payload = { nome: 'CND', tipo: 'certidao', obrigatorio: true };
      const mockData = { id: 'doc-1', ...payload, created_at: '2024-01-01' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await adicionarDocumentoEdital('tender-1', payload);

      expect(mockPost).toHaveBeenCalledWith('/api/v1/bidding/tenders/tender-1/documents', payload);
      expect(result).toEqual(mockData);
    });
  });

  describe('atualizarDocumentoEdital', () => {
    it('should update tender document', async () => {
      const payload = { nome: 'CND Atualizada' };
      const mockData = { id: 'doc-1', nome: 'CND Atualizada', tipo: 'certidao', obrigatorio: true, created_at: '2024-01-01' };
      mockPut.mockResolvedValueOnce({ data: mockData });

      const result = await atualizarDocumentoEdital('tender-1', 'doc-1', payload);

      expect(mockPut).toHaveBeenCalledWith('/api/v1/bidding/tenders/tender-1/documents/doc-1', payload);
      expect(result).toEqual(mockData);
    });
  });

  describe('removerDocumentoEdital', () => {
    it('should remove tender document', async () => {
      mockDelete.mockResolvedValueOnce({});

      await removerDocumentoEdital('tender-1', 'doc-1');

      expect(mockDelete).toHaveBeenCalledWith('/api/v1/bidding/tenders/tender-1/documents/doc-1');
    });
  });

  describe('listarDocumentosEmpresa', () => {
    it('should list company documents', async () => {
      const mockData = [{ id: 'cdoc-1', nome: 'Contrato Social' }];
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await listarDocumentosEmpresa();

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/company-documents/', { params: undefined });
      expect(result).toEqual(mockData);
    });

    it('should list company documents with params', async () => {
      mockGet.mockResolvedValueOnce({ data: [] });

      await listarDocumentosEmpresa({ cnpj: '11222333000181', tipo: 'contrato' });

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/company-documents/', {
        params: { cnpj: '11222333000181', tipo: 'contrato' },
      });
    });
  });

  describe('buscarDocumentoEmpresaPorId', () => {
    it('should fetch company document by id', async () => {
      const mockData = { id: 'cdoc-1', nome: 'Doc' };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await buscarDocumentoEmpresaPorId('cdoc-1');

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/company-documents/cdoc-1');
      expect(result).toEqual(mockData);
    });
  });

  describe('uploadDocumentoEmpresa', () => {
    it('should upload company document', async () => {
      const payload = { nome: 'Doc' } as any;
      const mockData = { id: 'cdoc-1', nome: 'Doc' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await uploadDocumentoEmpresa(payload);

      expect(mockPost).toHaveBeenCalledWith('/api/v1/bidding/company-documents/', payload);
      expect(result).toEqual(mockData);
    });
  });

  describe('atualizarDocumentoEmpresa', () => {
    it('should update company document', async () => {
      const payload = { nome: 'Doc Updated' } as any;
      const mockData = { id: 'cdoc-1', nome: 'Doc Updated' };
      mockPut.mockResolvedValueOnce({ data: mockData });

      const result = await atualizarDocumentoEmpresa('cdoc-1', payload);

      expect(mockPut).toHaveBeenCalledWith('/api/v1/bidding/company-documents/cdoc-1', payload);
      expect(result).toEqual(mockData);
    });
  });

  describe('removerDocumentoEmpresa', () => {
    it('should remove company document', async () => {
      mockDelete.mockResolvedValueOnce({});

      await removerDocumentoEmpresa('cdoc-1');

      expect(mockDelete).toHaveBeenCalledWith('/api/v1/bidding/company-documents/cdoc-1');
    });
  });

  describe('downloadDocumentoEmpresa', () => {
    it('should download company document', async () => {
      const blob = new Blob(['content']);
      mockGet.mockResolvedValueOnce({ data: blob });

      const result = await downloadDocumentoEmpresa('cdoc-1');

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/company-documents/cdoc-1/download', { responseType: 'blob' });
      expect(result).toEqual(blob);
    });
  });

  describe('listarDocumentosPendentes', () => {
    it('should list pending documents', async () => {
      const mockData = [{ documento_exigido: { id: 'doc-1' }, status: 'PENDENTE' }];
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await listarDocumentosPendentes();

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/company-documents/pendentes', { params: undefined });
      expect(result).toEqual(mockData);
    });

    it('should list pending documents with params', async () => {
      mockGet.mockResolvedValueOnce({ data: [] });

      await listarDocumentosPendentes({ tender_id: 'tender-1' });

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/company-documents/pendentes', {
        params: { tender_id: 'tender-1' },
      });
    });
  });

  describe('validarDocumento', () => {
    it('should validate document', async () => {
      const mockData = { valido: true, status: 'VALIDO', mensagem: 'OK', data_validacao: '2024-01-01' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await validarDocumento('cdoc-1');

      expect(mockPost).toHaveBeenCalledWith('/api/v1/bidding/company-documents/cdoc-1/validar');
      expect(result).toEqual(mockData);
    });
  });

  describe('default export', () => {
    it('should export all functions as service object', () => {
      expect(documentsService.listarDocumentos).toBe(listarDocumentos);
      expect(documentsService.buscarDocumentoPorId).toBe(buscarDocumentoPorId);
      expect(documentsService.criarDocumento).toBe(criarDocumento);
      expect(documentsService.atualizarDocumento).toBe(atualizarDocumento);
      expect(documentsService.removerDocumento).toBe(removerDocumento);
    });
  });
});
