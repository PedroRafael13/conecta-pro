import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

const mockList = vi.fn();
const mockListMy = vi.fn();
const mockGetById = vi.fn();
const mockGetStats = vi.fn();
const mockGetCategories = vi.fn();
const mockGetExpenseTypes = vi.fn();
const mockGetAttachmentTypes = vi.fn();
const mockCreate = vi.fn();
const mockUpdate = vi.fn();
const mockDelete = vi.fn();
const mockSubmit = vi.fn();
const mockCancel = vi.fn();

vi.mock('@/services/reimbursement', () => ({
  reimbursementRequestService: {
    list: (...args: any[]) => mockList(...args),
    listMy: (...args: any[]) => mockListMy(...args),
    getById: (...args: any[]) => mockGetById(...args),
    getStats: (...args: any[]) => mockGetStats(...args),
    getCategories: (...args: any[]) => mockGetCategories(...args),
    getExpenseTypes: (...args: any[]) => mockGetExpenseTypes(...args),
    getAttachmentTypes: (...args: any[]) => mockGetAttachmentTypes(...args),
    create: (...args: any[]) => mockCreate(...args),
    update: (...args: any[]) => mockUpdate(...args),
    delete: (...args: any[]) => mockDelete(...args),
    submit: (...args: any[]) => mockSubmit(...args),
    cancel: (...args: any[]) => mockCancel(...args),
  },
}));

import {
  reimbursementKeys,
  useReimbursementRequests,
  useMyReimbursementRequests,
  useReimbursementRequest,
  useReimbursementStats,
  useExpenseCategories,
  useExpenseTypes,
  useAttachmentTypes,
  useCreateReimbursementRequest,
  useUpdateReimbursementRequest,
  useDeleteReimbursementRequest,
  useSubmitReimbursementRequest,
  useCancelReimbursementRequest,
} from '../useReimbursementRequests';

const createTestQueryClient = () => new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const createWrapper = () => {
  const queryClient = createTestQueryClient();
  function TestWrapper({ children }: { children: React.ReactNode }) {
    return React.createElement(QueryClientProvider, { client: queryClient }, children);
  }
  return TestWrapper;
};

describe('reimbursementKeys', () => {
  it('should generate correct query keys', () => {
    expect(reimbursementKeys.all).toEqual(['reimbursements']);
    expect(reimbursementKeys.lists()).toEqual(['reimbursements', 'list']);
    expect(reimbursementKeys.list({ page: 1 })).toEqual(['reimbursements', 'list', { page: 1 }]);
    expect(reimbursementKeys.myLists()).toEqual(['reimbursements', 'my']);
    expect(reimbursementKeys.myList({ page: 1 })).toEqual(['reimbursements', 'my', { page: 1 }]);
    expect(reimbursementKeys.details()).toEqual(['reimbursements', 'detail']);
    expect(reimbursementKeys.detail('123')).toEqual(['reimbursements', 'detail', '123']);
    expect(reimbursementKeys.stats()).toEqual(['reimbursements', 'stats', undefined]);
    expect(reimbursementKeys.stats(true)).toEqual(['reimbursements', 'stats', true]);
    expect(reimbursementKeys.categories()).toEqual(['reimbursements', 'categories']);
    expect(reimbursementKeys.expenseTypes()).toEqual(['reimbursements', 'expense-types']);
    expect(reimbursementKeys.attachmentTypes()).toEqual(['reimbursements', 'attachment-types']);
  });
});

describe('useReimbursementRequests', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should fetch reimbursement requests', async () => {
    const mockData = { items: [], total: 0 };
    mockList.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useReimbursementRequests({ page: 1 }), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockData);
    expect(mockList).toHaveBeenCalledWith({ page: 1 });
  });

  it('should work without params', async () => {
    const mockData = { items: [], total: 0 };
    mockList.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useReimbursementRequests(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockList).toHaveBeenCalledWith(undefined);
  });

  it('should accept custom options', async () => {
    const mockData = { items: [], total: 0 };
    mockList.mockResolvedValueOnce(mockData);

    const { result } = renderHook(
      () => useReimbursementRequests(undefined, { enabled: false }),
      { wrapper: createWrapper() }
    );

    expect(result.current.isLoading).toBe(false);
    expect(result.current.fetchStatus).toBe('idle');
  });
});

describe('useMyReimbursementRequests', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should fetch my reimbursement requests', async () => {
    const mockData = { items: [], total: 0 };
    mockListMy.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useMyReimbursementRequests({ page: 1 }), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockData);
    expect(mockListMy).toHaveBeenCalledWith({ page: 1 });
  });

  it('should work without params', async () => {
    const mockData = { items: [], total: 0 };
    mockListMy.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useMyReimbursementRequests(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockListMy).toHaveBeenCalledWith(undefined);
  });
});

describe('useReimbursementRequest', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should fetch request by id', async () => {
    const mockData = { id: '123', title: 'Test' };
    mockGetById.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useReimbursementRequest('123'), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockData);
    expect(mockGetById).toHaveBeenCalledWith('123');
  });

  it('should be disabled when requestId is empty', async () => {
    const { result } = renderHook(() => useReimbursementRequest(''), { wrapper: createWrapper() });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.fetchStatus).toBe('idle');
    expect(mockGetById).not.toHaveBeenCalled();
  });

  it('should accept custom options', async () => {
    const mockData = { id: '123', title: 'Test' };
    mockGetById.mockResolvedValueOnce(mockData);

    const { result } = renderHook(
      () => useReimbursementRequest('123', { staleTime: 0 }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
  });
});

describe('useReimbursementStats', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should fetch stats with default myOnly=false', async () => {
    const mockData = { total: 100, approved: 50 };
    mockGetStats.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useReimbursementStats(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockData);
    expect(mockGetStats).toHaveBeenCalledWith(false);
  });

  it('should fetch stats with myOnly=true', async () => {
    const mockData = { total: 10, approved: 5 };
    mockGetStats.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useReimbursementStats(true), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockGetStats).toHaveBeenCalledWith(true);
  });
});

describe('useExpenseCategories', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should fetch categories with 30min staleTime', async () => {
    const mockData = [{ code: 'travel', name: 'Viagem' }];
    mockGetCategories.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useExpenseCategories(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockData);
    expect(mockGetCategories).toHaveBeenCalled();
  });

  it('should accept custom options', async () => {
    mockGetCategories.mockResolvedValueOnce([]);

    const { result } = renderHook(
      () => useExpenseCategories({ enabled: false }),
      { wrapper: createWrapper() }
    );

    expect(result.current.isLoading).toBe(false);
  });
});

describe('useExpenseTypes', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should fetch expense types with Infinity staleTime', async () => {
    const mockData = [{ value: 'food', label: 'Alimentação' }];
    mockGetExpenseTypes.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useExpenseTypes(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockData);
  });
});

describe('useAttachmentTypes', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should fetch attachment types with Infinity staleTime', async () => {
    const mockData = [{ value: 'receipt', label: 'Recibo' }];
    mockGetAttachmentTypes.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useAttachmentTypes(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockData);
  });
});

describe('useCreateReimbursementRequest', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should create request and invalidate queries', async () => {
    const mockData = { id: '123', title: 'New Request' };
    mockCreate.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useCreateReimbursementRequest(), { wrapper: createWrapper() });

    await result.current.mutateAsync({ title: 'New Request' } as any);

    expect(mockCreate).toHaveBeenCalledWith({ title: 'New Request' });
  });
});

describe('useUpdateReimbursementRequest', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should update request and invalidate queries', async () => {
    const mockData = { id: '123', title: 'Updated' };
    mockUpdate.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useUpdateReimbursementRequest(), { wrapper: createWrapper() });

    await result.current.mutateAsync({ requestId: '123', data: { title: 'Updated' } as any });

    expect(mockUpdate).toHaveBeenCalledWith('123', { title: 'Updated' });
  });
});

describe('useDeleteReimbursementRequest', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should delete request and invalidate queries', async () => {
    mockDelete.mockResolvedValueOnce(undefined);

    const { result } = renderHook(() => useDeleteReimbursementRequest(), { wrapper: createWrapper() });

    await result.current.mutateAsync('123');

    expect(mockDelete).toHaveBeenCalledWith('123');
  });
});

describe('useSubmitReimbursementRequest', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should submit request with notes', async () => {
    const mockData = { id: '123', status: 'submitted' };
    mockSubmit.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useSubmitReimbursementRequest(), { wrapper: createWrapper() });

    await result.current.mutateAsync({ requestId: '123', notes: 'Please approve' });

    expect(mockSubmit).toHaveBeenCalledWith('123', 'Please approve');
  });

  it('should submit request without notes', async () => {
    const mockData = { id: '123', status: 'submitted' };
    mockSubmit.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useSubmitReimbursementRequest(), { wrapper: createWrapper() });

    await result.current.mutateAsync({ requestId: '123' });

    expect(mockSubmit).toHaveBeenCalledWith('123', undefined);
  });
});

describe('useCancelReimbursementRequest', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should cancel request with reason', async () => {
    const mockData = { id: '123', status: 'cancelled' };
    mockCancel.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useCancelReimbursementRequest(), { wrapper: createWrapper() });

    await result.current.mutateAsync({ requestId: '123', reason: 'No longer needed' });

    expect(mockCancel).toHaveBeenCalledWith('123', 'No longer needed');
  });

  it('should cancel request without reason', async () => {
    const mockData = { id: '123', status: 'cancelled' };
    mockCancel.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useCancelReimbursementRequest(), { wrapper: createWrapper() });

    await result.current.mutateAsync({ requestId: '123' });

    expect(mockCancel).toHaveBeenCalledWith('123', undefined);
  });
});
