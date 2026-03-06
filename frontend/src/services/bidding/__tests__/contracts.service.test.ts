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
  listarContratos,
  buscarContratoPorId,
  criarContrato,
  atualizarContrato,
  removerContrato,
  listarContratosVigentes,
  listarContratosVencendo,
  alterarStatus,
  aditivar,
  getDashboard,
} from '../contracts.service';
import contractsService from '../contracts.service';

describe('contracts.service', () => {
  beforeEach(() => vi.clearAllMocks());

  describe('listarContratos', () => {
    it('should list contracts without params', async () => {
      const mockData = [{ id: 'c-1', status: 'vigente' }];
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await listarContratos();

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/contracts/', { params: undefined });
      expect(result).toEqual(mockData);
    });

    it('should list contracts with filters', async () => {
      mockGet.mockResolvedValueOnce({ data: [] });

      await listarContratos({ status: 'vigente', orgao: 'PMC', page: 1, size: 10 });

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/contracts/', {
        params: { status: 'vigente', orgao: 'PMC', page: 1, size: 10 },
      });
    });
  });

  describe('buscarContratoPorId', () => {
    it('should fetch contract by id', async () => {
      const mockData = { id: 'c-1', status: 'vigente' };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await buscarContratoPorId('c-1');

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/contracts/c-1');
      expect(result).toEqual(mockData);
    });
  });

  describe('criarContrato', () => {
    it('should create contract', async () => {
      const payload = { numero: 'CT-001', objeto: 'Servicos' } as any;
      const mockData = { id: 'c-1', ...payload };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await criarContrato(payload);

      expect(mockPost).toHaveBeenCalledWith('/api/v1/bidding/contracts/', payload);
      expect(result).toEqual(mockData);
    });
  });

  describe('atualizarContrato', () => {
    it('should update contract', async () => {
      const payload = { objeto: 'Servicos Updated' } as any;
      const mockData = { id: 'c-1', ...payload };
      mockPut.mockResolvedValueOnce({ data: mockData });

      const result = await atualizarContrato('c-1', payload);

      expect(mockPut).toHaveBeenCalledWith('/api/v1/bidding/contracts/c-1', payload);
      expect(result).toEqual(mockData);
    });
  });

  describe('removerContrato', () => {
    it('should remove contract', async () => {
      mockDelete.mockResolvedValueOnce({});

      await removerContrato('c-1');

      expect(mockDelete).toHaveBeenCalledWith('/api/v1/bidding/contracts/c-1');
    });
  });

  describe('listarContratosVigentes', () => {
    it('should list active contracts', async () => {
      const mockData = [{ id: 'c-1' }];
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await listarContratosVigentes();

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/contracts/vigentes', { params: undefined });
      expect(result).toEqual(mockData);
    });

    it('should list active contracts with pagination', async () => {
      mockGet.mockResolvedValueOnce({ data: [] });

      await listarContratosVigentes({ page: 2, size: 10 });

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/contracts/vigentes', {
        params: { page: 2, size: 10 },
      });
    });
  });

  describe('listarContratosVencendo', () => {
    it('should list expiring contracts', async () => {
      const mockData = [{ id: 'c-2' }];
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await listarContratosVencendo();

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/contracts/vencendo', { params: undefined });
      expect(result).toEqual(mockData);
    });

    it('should list expiring contracts with days param', async () => {
      mockGet.mockResolvedValueOnce({ data: [] });

      await listarContratosVencendo({ dias: 30 });

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/contracts/vencendo', {
        params: { dias: 30 },
      });
    });
  });

  describe('alterarStatus', () => {
    it('should change contract status', async () => {
      const mockData = { id: 'c-1', status: 'encerrado' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await alterarStatus({
        contract_id: 'c-1',
        novo_status: 'encerrado',
        observacoes: 'Finalizado',
      });

      expect(mockPost).toHaveBeenCalledWith('/api/v1/bidding/contracts/c-1/status', {
        novo_status: 'encerrado',
        observacoes: 'Finalizado',
      });
      expect(result).toEqual(mockData);
    });
  });

  describe('aditivar', () => {
    it('should create contract addendum', async () => {
      const mockData = { id: 'c-1', status: 'vigente' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await aditivar({
        contract_id: 'c-1',
        tipo_aditivo: 'VALOR',
        descricao: 'Reajuste',
        novo_valor: 150000,
      });

      expect(mockPost).toHaveBeenCalledWith('/api/v1/bidding/contracts/c-1/aditivo', {
        tipo_aditivo: 'VALOR',
        descricao: 'Reajuste',
        novo_valor: 150000,
      });
      expect(result).toEqual(mockData);
    });
  });

  describe('getDashboard', () => {
    it('should get dashboard without params', async () => {
      const mockData = { total_contratos: 5, vigentes: 3, vencidos: 1, em_execucao: 2, valor_total: 500000 };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await getDashboard();

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/contracts/dashboard', { params: undefined });
      expect(result).toEqual(mockData);
    });

    it('should get dashboard with periodo_dias', async () => {
      mockGet.mockResolvedValueOnce({ data: {} });

      await getDashboard({ periodo_dias: 90 });

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/contracts/dashboard', {
        params: { periodo_dias: 90 },
      });
    });
  });

  describe('default export', () => {
    it('should export all functions as service object', () => {
      expect(contractsService.listarContratos).toBe(listarContratos);
      expect(contractsService.buscarContratoPorId).toBe(buscarContratoPorId);
      expect(contractsService.criarContrato).toBe(criarContrato);
      expect(contractsService.atualizarContrato).toBe(atualizarContrato);
      expect(contractsService.removerContrato).toBe(removerContrato);
      expect(contractsService.listarContratosVigentes).toBe(listarContratosVigentes);
      expect(contractsService.listarContratosVencendo).toBe(listarContratosVencendo);
      expect(contractsService.alterarStatus).toBe(alterarStatus);
      expect(contractsService.aditivar).toBe(aditivar);
      expect(contractsService.getDashboard).toBe(getDashboard);
    });
  });
});
