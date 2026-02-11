import { describe, it, expect, vi, beforeEach } from 'vitest';
import { reimbursementRequestService } from '../reimbursementRequestService';

vi.mock('@/lib/api/client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  },
}));

import { apiClient } from '@/lib/api/client';

describe('reimbursementRequestService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('deve criar solicitação de reembolso', async () => {
    const mockData = { description: 'Test', amount: 100 };
    const mockResponse = { id: '1', ...mockData };
    vi.mocked(apiClient.post).mockResolvedValue({ data: mockResponse });

    const result = await reimbursementRequestService.create(mockData as any);

    expect(apiClient.post).toHaveBeenCalledWith('/api/v1/reimbursements', mockData);
    expect(result).toEqual(mockResponse);
  });

  it('deve listar solicitações', async () => {
    const mockResponse = { items: [{ id: '1' }], total: 1 };
    vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse });

    const result = await reimbursementRequestService.list({ status: 'pending' });

    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/reimbursements', { params: { status: 'pending' } });
    expect(result).toEqual(mockResponse);
  });

  it('deve listar minhas solicitações', async () => {
    const mockResponse = { items: [{ id: '1' }], total: 1 };
    vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse });

    const result = await reimbursementRequestService.listMy({ status: 'approved' });

    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/reimbursements/my', { params: { status: 'approved' } });
    expect(result).toEqual(mockResponse);
  });

  it('deve buscar solicitação por ID', async () => {
    const mockResponse = { id: '1', description: 'Test' };
    vi.mocked(apiClient.get).mockResolvedValue({ data: mockResponse });

    const result = await reimbursementRequestService.getById('1');

    expect(apiClient.get).toHaveBeenCalledWith('/api/v1/reimbursements/1');
    expect(result).toEqual(mockResponse);
  });

  it('deve atualizar solicitação', async () => {
    const mockData = { description: 'Updated' };
    const mockResponse = { id: '1', ...mockData };
    vi.mocked(apiClient.put).mockResolvedValue({ data: mockResponse });

    const result = await reimbursementRequestService.update('1', mockData as any);

    expect(apiClient.put).toHaveBeenCalledWith('/api/v1/reimbursements/1', mockData);
    expect(result).toEqual(mockResponse);
  });

  it('deve deletar solicitação', async () => {
    vi.mocked(apiClient.delete).mockResolvedValue({ data: undefined });

    await reimbursementRequestService.delete('1');

    expect(apiClient.delete).toHaveBeenCalledWith('/api/v1/reimbursements/1');
  });
});
