import { describe, it, expect, vi, beforeEach } from 'vitest';
import { reimbursementItemService } from '../reimbursementItemService';

const mockPost = vi.fn();
const mockPut = vi.fn();
const mockDelete = vi.fn();

vi.mock('@/lib/api/client', () => ({
  apiClient: {
    post: (...args: any[]) => mockPost(...args),
    put: (...args: any[]) => mockPut(...args),
    delete: (...args: any[]) => mockDelete(...args),
  },
}));

describe('reimbursementItemService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('create', () => {
    it('deve criar item de reembolso', async () => {
      const mockData = { id: 'item-1', description: 'Hotel' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementItemService.create('req-1', { description: 'Hotel' } as any);

      expect(mockPost).toHaveBeenCalledWith('/api/v1/reimbursements/req-1/items', { description: 'Hotel' });
      expect(result).toEqual(mockData);
    });
  });

  describe('update', () => {
    it('deve atualizar item de reembolso', async () => {
      const mockData = { id: 'item-1', description: 'Hotel Updated' };
      mockPut.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementItemService.update('req-1', 'item-1', { description: 'Hotel Updated' } as any);

      expect(mockPut).toHaveBeenCalledWith('/api/v1/reimbursements/req-1/items/item-1', { description: 'Hotel Updated' });
      expect(result).toEqual(mockData);
    });
  });

  describe('delete', () => {
    it('deve excluir item de reembolso', async () => {
      mockDelete.mockResolvedValueOnce({});

      await reimbursementItemService.delete('req-1', 'item-1');

      expect(mockDelete).toHaveBeenCalledWith('/api/v1/reimbursements/req-1/items/item-1');
    });
  });
});
