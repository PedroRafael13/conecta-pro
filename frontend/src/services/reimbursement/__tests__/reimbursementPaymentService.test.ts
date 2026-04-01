import { describe, it, expect, vi, beforeEach } from 'vitest';
import { reimbursementPaymentService } from '../reimbursementPaymentService';

const mockGet = vi.fn();
const mockPost = vi.fn();

vi.mock('@/lib/api/client', () => ({
  apiClient: {
    get: (...args: any[]) => mockGet(...args),
    post: (...args: any[]) => mockPost(...args),
  },
}));

describe('reimbursementPaymentService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('listReadyForPayment', () => {
    it('deve listar solicitações prontas para pagamento', async () => {
      const mockData = { items: [], total: 0 };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementPaymentService.listReadyForPayment();

      expect(mockGet).toHaveBeenCalledWith('/api/v1/reimbursements/ready-for-payment', { params: undefined });
      expect(result).toEqual(mockData);
    });

    it('deve listar com filtros', async () => {
      const mockData = { items: [], total: 0 };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementPaymentService.listReadyForPayment({ page: 1 });

      expect(mockGet).toHaveBeenCalledWith('/api/v1/reimbursements/ready-for-payment', { params: { page: 1 } });
      expect(result).toEqual(mockData);
    });
  });

  describe('process', () => {
    it('deve processar pagamento', async () => {
      const mockData = { id: 'req-1', status: 'paid' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementPaymentService.process('req-1', { notes: 'Pagamento via transferência' });

      expect(mockPost).toHaveBeenCalledWith('/api/v1/reimbursements/req-1/process', { notes: 'Pagamento via transferência' });
      expect(result).toEqual(mockData);
    });

    it('deve processar pagamento sem data opcional', async () => {
      const mockData = { id: 'req-1', status: 'paid' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementPaymentService.process('req-1');

      expect(mockPost).toHaveBeenCalledWith('/api/v1/reimbursements/req-1/process', {});
      expect(result).toEqual(mockData);
    });
  });
});
