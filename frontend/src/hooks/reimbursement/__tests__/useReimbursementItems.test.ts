import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

const mockCreate = vi.fn();
const mockUpdate = vi.fn();
const mockDelete = vi.fn();

vi.mock('@/services/reimbursement', () => ({
  reimbursementItemService: {
    create: (...args: any[]) => mockCreate(...args),
    update: (...args: any[]) => mockUpdate(...args),
    delete: (...args: any[]) => mockDelete(...args),
  },
}));

import {
  useCreateReimbursementItem,
  useUpdateReimbursementItem,
  useDeleteReimbursementItem,
} from '../useReimbursementItems';

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

describe('useCreateReimbursementItem', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should create item and invalidate queries', async () => {
    const mockData = { id: 'item-1', description: 'Hotel' };
    mockCreate.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useCreateReimbursementItem(), { wrapper: createWrapper() });

    await result.current.mutateAsync({ requestId: 'req-1', data: { description: 'Hotel' } as any });

    expect(mockCreate).toHaveBeenCalledWith('req-1', { description: 'Hotel' });
  });
});

describe('useUpdateReimbursementItem', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should update item and invalidate queries', async () => {
    const mockData = { id: 'item-1', description: 'Hotel Updated' };
    mockUpdate.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useUpdateReimbursementItem(), { wrapper: createWrapper() });

    await result.current.mutateAsync({ requestId: 'req-1', itemId: 'item-1', data: { description: 'Hotel Updated' } as any });

    expect(mockUpdate).toHaveBeenCalledWith('req-1', 'item-1', { description: 'Hotel Updated' });
  });
});

describe('useDeleteReimbursementItem', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should delete item and invalidate queries', async () => {
    mockDelete.mockResolvedValueOnce(undefined);

    const { result } = renderHook(() => useDeleteReimbursementItem(), { wrapper: createWrapper() });

    await result.current.mutateAsync({ requestId: 'req-1', itemId: 'item-1' });

    expect(mockDelete).toHaveBeenCalledWith('req-1', 'item-1');
  });
});
