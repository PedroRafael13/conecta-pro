import { describe, it, expect, vi, beforeEach } from 'vitest';
import { reimbursementApprovalService } from '../reimbursementApprovalService';

const mockGet = vi.fn();
const mockPost = vi.fn();

vi.mock('@/lib/api/client', () => ({
  apiClient: {
    get: (...args: any[]) => mockGet(...args),
    post: (...args: any[]) => mockPost(...args),
  },
}));

describe('reimbursementApprovalService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('listPending', () => {
    it('deve listar aprovações pendentes', async () => {
      const mockData = { items: [], total: 0 };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementApprovalService.listPending();

      expect(mockGet).toHaveBeenCalledWith('/api/v1/reimbursements/approvals/pending', { params: undefined });
      expect(result).toEqual(mockData);
    });

    it('deve listar aprovações pendentes com filtros', async () => {
      const mockData = { items: [], total: 0 };
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementApprovalService.listPending({ page: 1, approval_level: 'manager' });

      expect(mockGet).toHaveBeenCalledWith('/api/v1/reimbursements/approvals/pending', { params: { page: 1, approval_level: 'manager' } });
      expect(result).toEqual(mockData);
    });
  });

  describe('startAnalysis', () => {
    it('deve iniciar análise de solicitação', async () => {
      const mockData = { id: 'req-1', status: 'analyzing' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementApprovalService.startAnalysis('req-1');

      expect(mockPost).toHaveBeenCalledWith('/api/v1/reimbursements/req-1/analyze');
      expect(result).toEqual(mockData);
    });
  });

  describe('approve', () => {
    it('deve aprovar solicitação com notas', async () => {
      const mockData = { id: 'req-1', status: 'approved' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementApprovalService.approve('req-1', { comments: 'Approved' });

      expect(mockPost).toHaveBeenCalledWith('/api/v1/reimbursements/req-1/approve', { comments: 'Approved' });
      expect(result).toEqual(mockData);
    });

    it('deve aprovar solicitação sem notas', async () => {
      const mockData = { id: 'req-1', status: 'approved' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementApprovalService.approve('req-1');

      expect(mockPost).toHaveBeenCalledWith('/api/v1/reimbursements/req-1/approve', {});
      expect(result).toEqual(mockData);
    });
  });

  describe('reject', () => {
    it('deve rejeitar solicitação com motivo', async () => {
      const mockData = { id: 'req-1', status: 'rejected' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementApprovalService.reject('req-1', { reason: 'Invalid receipt' });

      expect(mockPost).toHaveBeenCalledWith('/api/v1/reimbursements/req-1/reject', { reason: 'Invalid receipt' });
      expect(result).toEqual(mockData);
    });
  });

  describe('returnToDraft', () => {
    it('deve retornar solicitação ao rascunho', async () => {
      const mockData = { id: 'req-1', status: 'returned' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementApprovalService.returnToDraft('req-1', { reason: 'Need more info' });

      expect(mockPost).toHaveBeenCalledWith('/api/v1/reimbursements/req-1/return', { reason: 'Need more info' });
      expect(result).toEqual(mockData);
    });
  });
});
