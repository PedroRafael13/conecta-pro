import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('@/lib/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

import api from '@/lib/api';

describe('bidding other services', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('contracts.service', () => {
    it('deve exportar funções do contrato', async () => {
      const contracts = await import('../contracts.service');
      expect(typeof contracts.listarContratos).toBe('function');
      expect(typeof contracts.buscarContratoPorId).toBe('function');
      expect(typeof contracts.criarContrato).toBe('function');
    });

    it('deve listar contratos', async () => {
      const { listarContratos } = await import('../contracts.service');
      const mockResponse = [{ id: '1', status: 'ativo' }];
      vi.mocked(api.get).mockResolvedValue({ data: mockResponse });

      const result = await listarContratos({ status: 'ativo' });

      expect(api.get).toHaveBeenCalledWith('/api/v1/bidding/contracts/', {
        params: { status: 'ativo' },
      });
      expect(result).toEqual(mockResponse);
    });

    it('deve criar contrato', async () => {
      const { criarContrato } = await import('../contracts.service');
      const mockPayload = { numero: '123' };
      const mockResponse = { id: '1', ...mockPayload };
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse });

      const result = await criarContrato(mockPayload as any);

      expect(api.post).toHaveBeenCalledWith('/api/v1/bidding/contracts/', mockPayload);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('proposals.service', () => {
    it('deve exportar funções de propostas', async () => {
      const proposals = await import('../proposals.service');
      expect(typeof proposals.listarPropostas).toBe('function');
      expect(typeof proposals.criarProposta).toBe('function');
    });

    it('deve criar proposta', async () => {
      const { criarProposta } = await import('../proposals.service');
      const mockPayload = { edital_id: '1', valor: 5000 };
      const mockResponse = { id: '1', ...mockPayload };
      vi.mocked(api.post).mockResolvedValue({ data: mockResponse });

      const result = await criarProposta(mockPayload as any);

      expect(api.post).toHaveBeenCalledWith('/api/v1/bidding/proposals/', mockPayload);
      expect(result).toEqual(mockResponse);
    });
  });
});
