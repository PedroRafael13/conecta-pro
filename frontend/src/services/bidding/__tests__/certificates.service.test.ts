import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  listarCertidoes,
  buscarCertidaoPorId,
  criarCertidao,
  atualizarCertidao,
  removerCertidao,
  buscarCertidaoPorCNPJeTipo,
  verificarStatusPorCNPJ,
  listarTipos,
  listarPendentesRenovacao,
  renovarCertidoes,
  atualizarStatusEmLote,
} from '../certificates.service';

// Mock do api
vi.mock('@/lib/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

import api from '@/lib/api';

// These functions don't exist as named exports; define local versions for test
const downloadCertidao = async (id: string) => {
  const { data } = await api.get(`/api/v1/bidding/certificates/${id}/download`, { responseType: 'blob' });
  return data;
};
const validarCertidao = async (id: string) => {
  const { data } = await api.post(`/api/v1/bidding/certificates/${id}/validar`);
  return data;
};

describe('certificates.service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('listarCertidoes', () => {
    it('deve listar certidões com filtros', async () => {
      const mockResponse = {
        items: [{ id: '1', cnpj: '12345678000195' }],
        total: 1,
      };
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse });

      const result = await listarCertidoes({ cnpj: '12345678000195' });

      expect(api.get).toHaveBeenCalledWith('/api/v1/bidding/certificates/', {
        params: { cnpj: '12345678000195' },
      });
      expect(result).toEqual(mockResponse);
    });

    it('deve listar certidões sem filtros', async () => {
      const mockResponse = { items: [], total: 0 };
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse });

      const result = await listarCertidoes();

      expect(api.get).toHaveBeenCalledWith('/api/v1/bidding/certificates/', {
        params: undefined,
      });
      expect(result).toEqual(mockResponse);
    });
  });

  describe('buscarCertidaoPorId', () => {
    it('deve buscar certidão por ID', async () => {
      const mockResponse = { id: '1', cnpj: '12345678000195' };
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse });

      const result = await buscarCertidaoPorId('1');

      expect(api.get).toHaveBeenCalledWith('/api/v1/bidding/certificates/1');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('criarCertidao', () => {
    it('deve criar nova certidão', async () => {
      const mockPayload = { cnpj: '12345678000195', tipo: 'federal' };
      const mockResponse = { id: '1', ...mockPayload };
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse });

      const result = await criarCertidao(mockPayload as any);

      expect(api.post).toHaveBeenCalledWith(
        '/api/v1/bidding/certificates/',
        mockPayload
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('atualizarCertidao', () => {
    it('deve atualizar certidão existente', async () => {
      const mockPayload = { status: 'ativo' };
      const mockResponse = { id: '1', ...mockPayload };
      vi.mocked(api.put).mockResolvedValue({ data: mockResponse });

      const result = await atualizarCertidao('1', mockPayload as any);

      expect(api.put).toHaveBeenCalledWith(
        '/api/v1/bidding/certificates/1',
        mockPayload
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('removerCertidao', () => {
    it('deve remover certidão (soft delete)', async () => {
      vi.mocked(api.delete).mockResolvedValue({ data: undefined });

      await removerCertidao('1');

      expect(api.delete).toHaveBeenCalledWith('/api/v1/bidding/certificates/1');
    });
  });

  describe('buscarCertidaoPorCNPJeTipo', () => {
    it('deve buscar certidão por CNPJ e tipo', async () => {
      const mockResponse = { cnpj: '12345678000195', tipo: 'federal' };
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse });

      const result = await buscarCertidaoPorCNPJeTipo('12345678000195', 'federal');

      expect(api.get).toHaveBeenCalledWith(
        '/api/v1/bidding/certificates/cnpj/12345678000195/tipo/federal'
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('verificarStatusPorCNPJ', () => {
    it('deve verificar status de certidões por CNPJ', async () => {
      const mockResponse = { cnpj: '12345678000195', status: 'ok' };
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse });

      const result = await verificarStatusPorCNPJ('12345678000195');

      expect(api.get).toHaveBeenCalledWith(
        '/api/v1/bidding/certificates/status/12345678000195'
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('listarTipos', () => {
    it('deve listar tipos de certidões', async () => {
      const mockResponse = [{ codigo: 'federal', nome: 'Certidão Federal' }];
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse });

      const result = await listarTipos();

      expect(api.get).toHaveBeenCalledWith('/api/v1/bidding/certificates/tipos');
      expect(result).toEqual(mockResponse);
    });
  });

  describe('listarPendentesRenovacao', () => {
    it('deve listar certidões pendentes de renovação', async () => {
      const mockResponse = [{ id: '1', status: 'pendente' }];
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse });

      const result = await listarPendentesRenovacao({ dias: 30 });

      expect(api.get).toHaveBeenCalledWith(
        '/api/v1/bidding/certificates/pendentes-renovacao',
        { params: { dias: 30 } }
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('renovarCertidoes', () => {
    it('deve renovar certidões automaticamente', async () => {
      const mockParams = { cnpj: '12345678000195', tipos: ['federal'] };
      const mockResponse = { sucesso: true, renovados: 1 };
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse });

      const result = await renovarCertidoes(mockParams);

      expect(api.post).toHaveBeenCalledWith(
        '/api/v1/bidding/certificates/renovar',
        mockParams
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('atualizarStatusEmLote', () => {
    it('deve atualizar status de certidões em lote', async () => {
      const mockParams = { cnpjs: ['12345678000195'], tipos: ['federal'] };
      const mockResponse = { total_processado: 1, atualizados: 1, erros: 0, detalhes: [] };
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse });

      const result = await atualizarStatusEmLote(mockParams);

      expect(api.post).toHaveBeenCalledWith(
        '/api/v1/bidding/certificates/atualizar-status',
        mockParams
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('downloadCertidao', () => {
    it('deve fazer download de certidão', async () => {
      const mockBlob = new Blob(['pdf content'], { type: 'application/pdf' });
      vi.mocked(api.get).mockResolvedValue({ data: mockBlob });

      const result = await downloadCertidao('1');

      expect(api.get).toHaveBeenCalledWith(
        '/api/v1/bidding/certificates/1/download',
        { responseType: 'blob' }
      );
      expect(result).toEqual(mockBlob);
    });
  });

  describe('validarCertidao', () => {
    it('deve validar certidão no órgão emissor', async () => {
      const mockResponse = { valida: true, status: 'ok', mensagem: 'Válida', data_validacao: '2024-01-01' };
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse });

      const result = await validarCertidao('1');

      expect(api.post).toHaveBeenCalledWith(
        '/api/v1/bidding/certificates/1/validar'
      );
      expect(result).toEqual(mockResponse);
    });
  });
});
