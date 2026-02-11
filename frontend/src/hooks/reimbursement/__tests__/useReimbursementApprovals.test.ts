import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

const mockListPending = vi.fn();
const mockStartAnalysis = vi.fn();
const mockApprove = vi.fn();
const mockReject = vi.fn();
const mockReturnToDraft = vi.fn();

vi.mock('@/services/reimbursement', () => ({
  reimbursementApprovalService: {
    listPending: (...args: any[]) => mockListPending(...args),
    startAnalysis: (...args: any[]) => mockStartAnalysis(...args),
    approve: (...args: any[]) => mockApprove(...args),
    reject: (...args: any[]) => mockReject(...args),
    returnToDraft: (...args: any[]) => mockReturnToDraft(...args),
  },
}));

import {
  approvalKeys,
  usePendingReimbursementApprovals,
  useStartReimbursementAnalysis,
  useApproveReimbursement,
  useRejectReimbursement,
  useReturnReimbursementToDraft,
} from '../useReimbursementApprovals';

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

describe('approvalKeys', () => {
  it('should generate correct query keys', () => {
    expect(approvalKeys.all).toEqual(['reimbursement-approvals']);
    expect(approvalKeys.pending()).toEqual(['reimbursement-approvals', 'pending', undefined]);
    expect(approvalKeys.pending({ page: 1 })).toEqual(['reimbursement-approvals', 'pending', { page: 1 }]);
  });
});

describe('usePendingReimbursementApprovals', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should fetch pending approvals', async () => {
    const mockData = { items: [], total: 0 };
    mockListPending.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => usePendingReimbursementApprovals({ page: 1 }), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockData);
    expect(mockListPending).toHaveBeenCalledWith({ page: 1 });
  });

  it('should work without params', async () => {
    const mockData = { items: [], total: 0 };
    mockListPending.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => usePendingReimbursementApprovals(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockListPending).toHaveBeenCalledWith(undefined);
  });

  it('should accept custom options', async () => {
    const mockData = { items: [], total: 0 };
    mockListPending.mockResolvedValueOnce(mockData);

    const { result } = renderHook(
      () => usePendingReimbursementApprovals(undefined, { enabled: false }),
      { wrapper: createWrapper() }
    );

    expect(result.current.isLoading).toBe(false);
  });
});

describe('useStartReimbursementAnalysis', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should start analysis and invalidate queries', async () => {
    const mockData = { id: '123', status: 'analyzing' };
    mockStartAnalysis.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useStartReimbursementAnalysis(), { wrapper: createWrapper() });

    await result.current.mutateAsync('123');

    expect(mockStartAnalysis).toHaveBeenCalledWith('123');
  });
});

describe('useApproveReimbursement', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should approve with data', async () => {
    const mockData = { id: '123', status: 'approved' };
    mockApprove.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useApproveReimbursement(), { wrapper: createWrapper() });

    await result.current.mutateAsync({ requestId: '123', data: { comments: 'Approved' } });

    expect(mockApprove).toHaveBeenCalledWith('123', { comments: 'Approved' });
  });

  it('should approve without data', async () => {
    const mockData = { id: '123', status: 'approved' };
    mockApprove.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useApproveReimbursement(), { wrapper: createWrapper() });

    await result.current.mutateAsync({ requestId: '123' });

    expect(mockApprove).toHaveBeenCalledWith('123', undefined);
  });
});

describe('useRejectReimbursement', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should reject with reason', async () => {
    const mockData = { id: '123', status: 'rejected' };
    mockReject.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useRejectReimbursement(), { wrapper: createWrapper() });

    await result.current.mutateAsync({ requestId: '123', data: { reason: 'Invalid' } });

    expect(mockReject).toHaveBeenCalledWith('123', { reason: 'Invalid' });
  });
});

describe('useReturnReimbursementToDraft', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should return to draft with reason', async () => {
    const mockData = { id: '123', status: 'draft' };
    mockReturnToDraft.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useReturnReimbursementToDraft(), { wrapper: createWrapper() });

    await result.current.mutateAsync({ requestId: '123', data: { reason: 'Need more info' } });

    expect(mockReturnToDraft).toHaveBeenCalledWith('123', { reason: 'Need more info' });
  });
});
