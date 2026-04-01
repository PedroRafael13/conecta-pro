import { describe, it, expect, vi, beforeEach } from 'vitest';
import { reimbursementRequestService } from '../reimbursementRequestService';

// Mock do apiClient
const mockGet = vi.fn();
const mockPost = vi.fn();
const mockPut = vi.fn();
const mockDelete = vi.fn();

vi.mock('@/lib/api/client', () => ({
  apiClient: {
    get: (...args: any[]) => mockGet(...args),
    post: (...args: any[]) => mockPost(...args),
    put: (...args: any[]) => mockPut(...args),
    delete: (...args: any[]) => mockDelete(...args),
  },
}));

describe('reimbursementRequestService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('create', () => {
    it('deve criar nova solicitação de reembolso', async () => {
      const mockData = { id: '1', title: 'Test' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementRequestService.create({ title: 'Test' } as any);

      expect(mockPost).toHaveBeenCalledWith('/api/v1/reimbursements', { title: 'Test' });
      expect(result).toEqual(mockData);
    });
  });

  describe('list', () => {
    it('deve listar solicitações sem filtros', async () => {
      const mockData = { items: [], total: 0 };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementRequestService.list();

      expect(mockGet).toHaveBeenCalledWith('/api/v1/reimbursements', { params: undefined });
      expect(result).toEqual(mockData);
    });

    it('deve listar solicitações com filtros', async () => {
      const mockData = { items: [], total: 0 };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const params = { page: 1, status: 'pending' };
      const result = await reimbursementRequestService.list(params);

      expect(mockGet).toHaveBeenCalledWith('/api/v1/reimbursements', { params });
      expect(result).toEqual(mockData);
    });
  });

  describe('listMy', () => {
    it('deve listar solicitações do usuário autenticado', async () => {
      const mockData = { items: [], total: 0 };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementRequestService.listMy({ page: 1 });

      expect(mockGet).toHaveBeenCalledWith('/api/v1/reimbursements/my', { params: { page: 1 } });
      expect(result).toEqual(mockData);
    });

    it('deve listar sem parâmetros', async () => {
      const mockData = { items: [], total: 0 };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementRequestService.listMy();

      expect(mockGet).toHaveBeenCalledWith('/api/v1/reimbursements/my', { params: undefined });
      expect(result).toEqual(mockData);
    });
  });

  describe('getById', () => {
    it('deve buscar solicitação por ID', async () => {
      const mockData = { id: '123', title: 'Test' };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementRequestService.getById('123');

      expect(mockGet).toHaveBeenCalledWith('/api/v1/reimbursements/123');
      expect(result).toEqual(mockData);
    });
  });

  describe('update', () => {
    it('deve atualizar solicitação', async () => {
      const mockData = { id: '123', title: 'Updated' };
      mockPut.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementRequestService.update('123', { title: 'Updated' } as any);

      expect(mockPut).toHaveBeenCalledWith('/api/v1/reimbursements/123', { title: 'Updated' });
      expect(result).toEqual(mockData);
    });
  });

  describe('delete', () => {
    it('deve excluir solicitação', async () => {
      mockDelete.mockResolvedValueOnce({});

      await reimbursementRequestService.delete('123');

      expect(mockDelete).toHaveBeenCalledWith('/api/v1/reimbursements/123');
    });
  });

  describe('submit', () => {
    it('deve submeter solicitação com notas', async () => {
      const mockData = { id: '123', status: 'submitted' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementRequestService.submit('123', 'Submit notes');

      expect(mockPost).toHaveBeenCalledWith('/api/v1/reimbursements/123/submit', { notes: 'Submit notes' });
      expect(result).toEqual(mockData);
    });

    it('deve submeter solicitação sem notas', async () => {
      const mockData = { id: '123', status: 'submitted' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementRequestService.submit('123');

      expect(mockPost).toHaveBeenCalledWith('/api/v1/reimbursements/123/submit', { notes: undefined });
      expect(result).toEqual(mockData);
    });
  });

  describe('cancel', () => {
    it('deve cancelar solicitação com motivo', async () => {
      const mockData = { id: '123', status: 'cancelled' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementRequestService.cancel('123', 'Cancel reason');

      expect(mockPost).toHaveBeenCalledWith('/api/v1/reimbursements/123/cancel', null, { params: { reason: 'Cancel reason' } });
      expect(result).toEqual(mockData);
    });

    it('deve cancelar solicitação sem motivo', async () => {
      const mockData = { id: '123', status: 'cancelled' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementRequestService.cancel('123');

      expect(mockPost).toHaveBeenCalledWith('/api/v1/reimbursements/123/cancel', null, { params: { reason: undefined } });
      expect(result).toEqual(mockData);
    });
  });

  describe('getStats', () => {
    it('deve retornar estatísticas gerais', async () => {
      const mockData = { total: 100, approved: 50 };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementRequestService.getStats();

      expect(mockGet).toHaveBeenCalledWith('/api/v1/reimbursements/stats', { params: { my_only: false } });
      expect(result).toEqual(mockData);
    });

    it('deve retornar estatísticas do usuário', async () => {
      const mockData = { total: 10, approved: 5 };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementRequestService.getStats(true);

      expect(mockGet).toHaveBeenCalledWith('/api/v1/reimbursements/stats', { params: { my_only: true } });
      expect(result).toEqual(mockData);
    });
  });

  describe('getCategories', () => {
    it('deve listar categorias de despesa', async () => {
      const mockData = [{ code: 'travel', name: 'Viagem' }];
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementRequestService.getCategories();

      expect(mockGet).toHaveBeenCalledWith('/api/v1/reimbursements/categories');
      expect(result).toEqual(mockData);
    });
  });

  describe('getExpenseTypes', () => {
    it('deve listar tipos de despesa', async () => {
      const mockData = [{ value: 'food', label: 'Alimentação' }];
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementRequestService.getExpenseTypes();

      expect(mockGet).toHaveBeenCalledWith('/api/v1/reimbursements/expense-types');
      expect(result).toEqual(mockData);
    });
  });

  describe('getAttachmentTypes', () => {
    it('deve listar tipos de anexo', async () => {
      const mockData = [{ value: 'receipt', label: 'Recibo' }];
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementRequestService.getAttachmentTypes();

      expect(mockGet).toHaveBeenCalledWith('/api/v1/reimbursements/attachment-types');
      expect(result).toEqual(mockData);
    });
  });
});
