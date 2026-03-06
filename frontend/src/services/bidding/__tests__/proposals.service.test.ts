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
  listarPropostas,
  buscarPropostaPorId,
  criarProposta,
  atualizarProposta,
  removerProposta,
  listarPropostasPorEdital,
  submeterProposta,
  alterarStatusProposta,
  listarPropostasEmAndamento,
  listarPropostasAprovadas,
  getDashboard,
  adicionarItem,
  atualizarItem,
  removerItem,
  listarItens,
} from '../proposals.service';
import proposalsService from '../proposals.service';

describe('proposals.service', () => {
  beforeEach(() => vi.clearAllMocks());

  describe('listarPropostas', () => {
    it('should list proposals without params', async () => {
      const mockData = { items: [], total: 0, page: 1, size: 10, pages: 0 };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await listarPropostas();

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/proposals/', { params: undefined });
      expect(result).toEqual(mockData);
    });

    it('should list proposals with params', async () => {
      mockGet.mockResolvedValueOnce({ data: { items: [], total: 0, page: 1, size: 10, pages: 0 } });

      await listarPropostas({ status: 'aprovada', page: 2 });

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/proposals/', {
        params: { status: 'aprovada', page: 2 },
      });
    });
  });

  describe('buscarPropostaPorId', () => {
    it('should fetch proposal by id', async () => {
      const mockData = { id: 'prop-1', tender_id: 't-1', cnpj: '11222333000181', razao_social: 'Empresa', valor_global: 1000, status: 'draft', created_at: '2024-01-01' };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await buscarPropostaPorId('prop-1');

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/proposals/prop-1');
      expect(result).toEqual(mockData);
    });
  });

  describe('criarProposta', () => {
    it('should create proposal', async () => {
      const payload = { tender_id: 't-1', cnpj: '11222333000181', razao_social: 'Empresa', valor_global: 5000 };
      const mockData = { id: 'prop-1', ...payload, status: 'draft', created_at: '2024-01-01' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await criarProposta(payload);

      expect(mockPost).toHaveBeenCalledWith('/api/v1/bidding/proposals/', payload);
      expect(result).toEqual(mockData);
    });
  });

  describe('atualizarProposta', () => {
    it('should update proposal', async () => {
      const payload = { valor_global: 6000 };
      const mockData = { id: 'prop-1', valor_global: 6000, status: 'draft' };
      mockPut.mockResolvedValueOnce({ data: mockData });

      const result = await atualizarProposta('prop-1', payload);

      expect(mockPut).toHaveBeenCalledWith('/api/v1/bidding/proposals/prop-1', payload);
      expect(result).toEqual(mockData);
    });
  });

  describe('removerProposta', () => {
    it('should remove proposal', async () => {
      mockDelete.mockResolvedValueOnce({});

      await removerProposta('prop-1');

      expect(mockDelete).toHaveBeenCalledWith('/api/v1/bidding/proposals/prop-1');
    });
  });

  describe('listarPropostasPorEdital', () => {
    it('should list proposals by tender', async () => {
      const mockData = { items: [], total: 0, page: 1, size: 10, pages: 0 };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await listarPropostasPorEdital('tender-1');

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/proposals/tender/tender-1', { params: undefined });
      expect(result).toEqual(mockData);
    });

    it('should list proposals by tender with pagination', async () => {
      mockGet.mockResolvedValueOnce({ data: { items: [], total: 0, page: 2, size: 20, pages: 0 } });

      await listarPropostasPorEdital('tender-1', { page: 2, size: 20 });

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/proposals/tender/tender-1', {
        params: { page: 2, size: 20 },
      });
    });
  });

  describe('submeterProposta', () => {
    it('should submit proposal', async () => {
      const mockData = { id: 'prop-1', status: 'submitted' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await submeterProposta({ proposal_id: 'prop-1', observacoes: 'Ready' });

      expect(mockPost).toHaveBeenCalledWith('/api/v1/bidding/proposals/prop-1/submeter', { observacoes: 'Ready' });
      expect(result).toEqual(mockData);
    });

    it('should submit proposal without observacoes', async () => {
      const mockData = { id: 'prop-1', status: 'submitted' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await submeterProposta({ proposal_id: 'prop-1' });

      expect(mockPost).toHaveBeenCalledWith('/api/v1/bidding/proposals/prop-1/submeter', {});
      expect(result).toEqual(mockData);
    });
  });

  describe('alterarStatusProposta', () => {
    it('should change proposal status', async () => {
      const mockData = { id: 'prop-1', status: 'aprovada' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await alterarStatusProposta({ proposal_id: 'prop-1', novo_status: 'aprovada', observacoes: 'OK' });

      expect(mockPost).toHaveBeenCalledWith('/api/v1/bidding/proposals/prop-1/status', {
        novo_status: 'aprovada',
        observacoes: 'OK',
      });
      expect(result).toEqual(mockData);
    });
  });

  describe('listarPropostasEmAndamento', () => {
    it('should list in-progress proposals', async () => {
      const mockData = { items: [], total: 0, page: 1, size: 10, pages: 0 };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await listarPropostasEmAndamento();

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/proposals/em-andamento', { params: undefined });
      expect(result).toEqual(mockData);
    });

    it('should list in-progress proposals with pagination', async () => {
      mockGet.mockResolvedValueOnce({ data: { items: [], total: 0, page: 2, size: 5, pages: 0 } });

      await listarPropostasEmAndamento({ page: 2, size: 5 });

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/proposals/em-andamento', {
        params: { page: 2, size: 5 },
      });
    });
  });

  describe('listarPropostasAprovadas', () => {
    it('should list approved proposals', async () => {
      const mockData = { items: [], total: 0, page: 1, size: 10, pages: 0 };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await listarPropostasAprovadas();

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/proposals/aprovadas', { params: undefined });
      expect(result).toEqual(mockData);
    });
  });

  describe('getDashboard', () => {
    it('should get dashboard without params', async () => {
      const mockData = { total_propostas: 10, em_andamento: 3, aprovadas: 5, rejeitadas: 2, valor_total: 50000, taxa_aprovacao: 71 };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await getDashboard();

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/proposals/dashboard', { params: undefined });
      expect(result).toEqual(mockData);
    });

    it('should get dashboard with periodo_dias', async () => {
      mockGet.mockResolvedValueOnce({ data: {} });

      await getDashboard({ periodo_dias: 30 });

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/proposals/dashboard', {
        params: { periodo_dias: 30 },
      });
    });
  });

  describe('adicionarItem', () => {
    it('should add item to proposal', async () => {
      const payload = { descricao: 'Material', quantidade: 10, valor_unitario: 100 };
      const mockData = { id: 'item-1', proposta_id: 'prop-1', ...payload, valor_total: 1000, created_at: '2024-01-01' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await adicionarItem('prop-1', payload);

      expect(mockPost).toHaveBeenCalledWith('/api/v1/bidding/proposals/prop-1/items', payload);
      expect(result).toEqual(mockData);
    });
  });

  describe('atualizarItem', () => {
    it('should update proposal item', async () => {
      const payload = { descricao: 'Material Updated' };
      const mockData = { id: 'item-1', descricao: 'Material Updated' };
      mockPut.mockResolvedValueOnce({ data: mockData });

      const result = await atualizarItem('prop-1', 'item-1', payload);

      expect(mockPut).toHaveBeenCalledWith('/api/v1/bidding/proposals/prop-1/items/item-1', payload);
      expect(result).toEqual(mockData);
    });
  });

  describe('removerItem', () => {
    it('should remove proposal item', async () => {
      mockDelete.mockResolvedValueOnce({});

      await removerItem('prop-1', 'item-1');

      expect(mockDelete).toHaveBeenCalledWith('/api/v1/bidding/proposals/prop-1/items/item-1');
    });
  });

  describe('listarItens', () => {
    it('should list proposal items', async () => {
      const mockData = [{ id: 'item-1', descricao: 'Material', quantidade: 10, valor_unitario: 100, valor_total: 1000 }];
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await listarItens('prop-1');

      expect(mockGet).toHaveBeenCalledWith('/api/v1/bidding/proposals/prop-1/items');
      expect(result).toEqual(mockData);
    });
  });

  describe('default export', () => {
    it('should export all functions as service object', () => {
      expect(proposalsService.listarPropostas).toBe(listarPropostas);
      expect(proposalsService.buscarPropostaPorId).toBe(buscarPropostaPorId);
      expect(proposalsService.criarProposta).toBe(criarProposta);
      expect(proposalsService.atualizarProposta).toBe(atualizarProposta);
      expect(proposalsService.removerProposta).toBe(removerProposta);
      expect(proposalsService.listarPropostasPorEdital).toBe(listarPropostasPorEdital);
      expect(proposalsService.submeterProposta).toBe(submeterProposta);
      expect(proposalsService.alterarStatusProposta).toBe(alterarStatusProposta);
      expect(proposalsService.listarPropostasEmAndamento).toBe(listarPropostasEmAndamento);
      expect(proposalsService.listarPropostasAprovadas).toBe(listarPropostasAprovadas);
      expect(proposalsService.getDashboard).toBe(getDashboard);
      expect(proposalsService.adicionarItem).toBe(adicionarItem);
      expect(proposalsService.atualizarItem).toBe(atualizarItem);
      expect(proposalsService.removerItem).toBe(removerItem);
      expect(proposalsService.listarItens).toBe(listarItens);
    });
  });
});
