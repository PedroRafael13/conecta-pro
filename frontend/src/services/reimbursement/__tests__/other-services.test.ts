import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('@/lib/api/client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

import { apiClient } from '@/lib/api/client';

describe('reimbursement services', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('reimbursementItemService', () => {
    it('deve exportar funções', async () => {
      const { reimbursementItemService } = await import('../reimbursementItemService');
      expect(typeof reimbursementItemService.create).toBe('function');
      expect(typeof reimbursementItemService.update).toBe('function');
      expect(typeof reimbursementItemService.delete).toBe('function');
    });

    it('deve criar item', async () => {
      const { reimbursementItemService } = await import('../reimbursementItemService');
      const mockData = { description: 'Item', amount: 50 };
      const mockResponse = { id: '1', ...mockData };
      vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

      const result = await reimbursementItemService.create('req-1', mockData as any);

      expect(apiClient.post).toHaveBeenCalledWith('/api/v1/reimbursements/req-1/items', mockData);
      expect(result).toEqual(mockResponse);
    });
  });

  describe('reimbursementApprovalService', () => {
    it('deve exportar funções', async () => {
      const { reimbursementApprovalService } = await import('../reimbursementApprovalService');
      expect(typeof reimbursementApprovalService.listPending).toBe('function');
    });

    it('deve listar aprovações pendentes', async () => {
      const { reimbursementApprovalService } = await import('../reimbursementApprovalService');
      const mockResponse = { items: [{ id: '1' }], total: 1 };
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse });

      const result = await reimbursementApprovalService.listPending({ page: 1 });

      expect(result).toEqual(mockResponse);
    });
  });

  describe('reimbursementAttachmentService', () => {
    it('deve exportar funções', async () => {
      const { reimbursementAttachmentService } = await import('../reimbursementAttachmentService');
      expect(typeof reimbursementAttachmentService.upload).toBe('function');
    });
  });

  describe('reimbursementPaymentService', () => {
    it('deve exportar funções', async () => {
      const { reimbursementPaymentService } = await import('../reimbursementPaymentService');
      expect(typeof reimbursementPaymentService.listReadyForPayment).toBe('function');
    });

    it('deve listar pagamentos prontos', async () => {
      const { reimbursementPaymentService } = await import('../reimbursementPaymentService');
      const mockResponse = { items: [{ id: '1' }], total: 1 };
      vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse });

      const result = await reimbursementPaymentService.listReadyForPayment();

      expect(result).toEqual(mockResponse);
    });
  });
});
