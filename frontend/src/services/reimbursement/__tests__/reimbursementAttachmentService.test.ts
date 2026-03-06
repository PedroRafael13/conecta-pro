import { describe, it, expect, vi, beforeEach } from 'vitest';
import { reimbursementAttachmentService } from '../reimbursementAttachmentService';

const mockGet = vi.fn();
const mockPost = vi.fn();
const mockDelete = vi.fn();

vi.mock('@/lib/api/client', () => ({
  apiClient: {
    get: (...args: any[]) => mockGet(...args),
    post: (...args: any[]) => mockPost(...args),
    delete: (...args: any[]) => mockDelete(...args),
  },
}));

describe('reimbursementAttachmentService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('list', () => {
    it('deve listar anexos de uma solicitação', async () => {
      const mockData = [{ id: 'att-1', filename: 'receipt.pdf' }];
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementAttachmentService.list('req-1');

      expect(mockGet).toHaveBeenCalledWith('/api/v1/reimbursements/req-1/attachments', { params: { item_id: undefined } });
      expect(result).toEqual(mockData);
    });

    it('deve listar anexos com itemId', async () => {
      const mockData = [{ id: 'att-1', filename: 'receipt.pdf' }];
      mockGet.mockResolvedValueOnce({ data: mockData });

      const result = await reimbursementAttachmentService.list('req-1', 'item-1');

      expect(mockGet).toHaveBeenCalledWith('/api/v1/reimbursements/req-1/attachments', { params: { item_id: 'item-1' } });
      expect(result).toEqual(mockData);
    });
  });

  describe('upload', () => {
    it('deve fazer upload de anexo', async () => {
      const mockData = { id: 'att-1', filename: 'receipt.pdf' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const file = new File(['content'], 'receipt.pdf', { type: 'application/pdf' });
      const result = await reimbursementAttachmentService.upload('req-1', file, { attachmentType: 'receipt' });

      expect(mockPost).toHaveBeenCalledWith(
        '/api/v1/reimbursements/req-1/attachments',
        expect.any(FormData),
        expect.objectContaining({ headers: expect.objectContaining({ 'Content-Type': 'multipart/form-data' }) })
      );
      expect(result).toEqual(mockData);
    });

    it('deve fazer upload com todas as opções', async () => {
      const mockData = { id: 'att-1', filename: 'receipt.pdf' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const file = new File(['content'], 'receipt.pdf', { type: 'application/pdf' });
      const result = await reimbursementAttachmentService.upload('req-1', file, {
        itemId: 'item-1',
        attachmentType: 'receipt',
        description: 'Hotel receipt'
      });

      expect(mockPost).toHaveBeenCalledWith(
        '/api/v1/reimbursements/req-1/attachments',
        expect.any(FormData),
        expect.objectContaining({ headers: expect.objectContaining({ 'Content-Type': 'multipart/form-data' }) })
      );
      expect(result).toEqual(mockData);
    });
  });

  describe('delete', () => {
    it('deve excluir anexo', async () => {
      mockDelete.mockResolvedValueOnce({});

      await reimbursementAttachmentService.delete('att-1');

      expect(mockDelete).toHaveBeenCalledWith('/api/v1/reimbursements/attachments/att-1');
    });
  });

  describe('getDownloadUrl', () => {
    it('deve retornar URL de download', () => {
      const result = reimbursementAttachmentService.getDownloadUrl('att-1');

      expect(result).toBe('/api/v1/reimbursements/attachments/att-1/download');
    });
  });

  describe('download', () => {
    it('deve fazer download do anexo', async () => {
      const mockBlob = new Blob(['content'], { type: 'application/pdf' });
      mockGet.mockResolvedValueOnce({ data: mockBlob });

      const result = await reimbursementAttachmentService.download('att-1');

      expect(mockGet).toHaveBeenCalledWith('/api/v1/reimbursements/attachments/att-1/download', { responseType: 'blob' });
      expect(result).toEqual(mockBlob);
    });
  });

  describe('Branch Coverage - Upload Validation', () => {
    it('deve fazer upload sem opções adicionais', async () => {
      const mockData = { id: 'att-1', filename: 'receipt.pdf' };
      mockPost.mockResolvedValueOnce({ data: mockData });

      const file = new File(['content'], 'receipt.pdf', { type: 'application/pdf' });
      const result = await reimbursementAttachmentService.upload('req-1', file);

      expect(mockPost).toHaveBeenCalledWith(
        '/api/v1/reimbursements/req-1/attachments',
        expect.any(FormData),
        expect.objectContaining({ headers: expect.objectContaining({ 'Content-Type': 'multipart/form-data' }) })
      );
      expect(result).toEqual(mockData);
    });
  });
});
