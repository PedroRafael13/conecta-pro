import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

const mockListReadyForPayment = vi.fn();
const mockProcess = vi.fn();

vi.mock('@/services/reimbursement', () => ({
  reimbursementPaymentService: {
    listReadyForPayment: (...args: any[]) => mockListReadyForPayment(...args),
    process: (...args: any[]) => mockProcess(...args),
  },
}));

import {
  paymentKeys,
  useReadyForPaymentReimbursements,
  useProcessReimbursementPayment,
} from '../useReimbursementPayments';

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

describe('paymentKeys', () => {
  it('should generate correct query keys', () => {
    expect(paymentKeys.all).toEqual(['reimbursement-payments']);
    expect(paymentKeys.readyForPayment()).toEqual(['reimbursement-payments', 'ready', undefined]);
    expect(paymentKeys.readyForPayment({ page: 1 })).toEqual(['reimbursement-payments', 'ready', { page: 1 }]);
  });
});

describe('useReadyForPaymentReimbursements', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should fetch ready for payment requests', async () => {
    const mockData = { items: [], total: 0 };
    mockListReadyForPayment.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useReadyForPaymentReimbursements({ page: 1 }), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockData);
    expect(mockListReadyForPayment).toHaveBeenCalledWith({ page: 1 });
  });

  it('should work without params', async () => {
    const mockData = { items: [], total: 0 };
    mockListReadyForPayment.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useReadyForPaymentReimbursements(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockListReadyForPayment).toHaveBeenCalledWith(undefined);
  });

  it('should accept custom options', async () => {
    const mockData = { items: [], total: 0 };
    mockListReadyForPayment.mockResolvedValueOnce(mockData);

    const { result } = renderHook(
      () => useReadyForPaymentReimbursements(undefined, { enabled: false }),
      { wrapper: createWrapper() }
    );

    expect(result.current.isLoading).toBe(false);
  });
});

describe('useProcessReimbursementPayment', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should process payment with data', async () => {
    const mockData = { id: '123', status: 'paid' };
    mockProcess.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useProcessReimbursementPayment(), { wrapper: createWrapper() });

    await result.current.mutateAsync({ requestId: '123', data: { payment_method: 'transfer' } as any });

    expect(mockProcess).toHaveBeenCalledWith('123', { payment_method: 'transfer' });
  });

  it('should process payment without data', async () => {
    const mockData = { id: '123', status: 'paid' };
    mockProcess.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useProcessReimbursementPayment(), { wrapper: createWrapper() });

    await result.current.mutateAsync({ requestId: '123' });

    expect(mockProcess).toHaveBeenCalledWith('123', undefined);
  });
});
