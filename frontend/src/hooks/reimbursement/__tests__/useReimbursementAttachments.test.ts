import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

const mockList = vi.fn();
const mockUpload = vi.fn();
const mockDelete = vi.fn();
const mockDownload = vi.fn();

vi.mock('@/services/reimbursement', () => ({
  reimbursementAttachmentService: {
    list: (...args: any[]) => mockList(...args),
    upload: (...args: any[]) => mockUpload(...args),
    delete: (...args: any[]) => mockDelete(...args),
    download: (...args: any[]) => mockDownload(...args),
  },
}));

import {
  attachmentKeys,
  useReimbursementAttachments,
  useUploadReimbursementAttachment,
  useDeleteReimbursementAttachment,
  useDownloadReimbursementAttachment,
} from '../useReimbursementAttachments';

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

describe('attachmentKeys', () => {
  it('should generate correct query keys', () => {
    expect(attachmentKeys.all).toEqual(['reimbursement-attachments']);
    expect(attachmentKeys.lists()).toEqual(['reimbursement-attachments', 'list']);
    expect(attachmentKeys.list('req-1')).toEqual(['reimbursement-attachments', 'list', 'req-1', undefined]);
    expect(attachmentKeys.list('req-1', 'item-1')).toEqual(['reimbursement-attachments', 'list', 'req-1', 'item-1']);
  });
});

describe('useReimbursementAttachments', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should fetch attachments', async () => {
    const mockData = [{ id: 'att-1', filename: 'receipt.pdf' }];
    mockList.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useReimbursementAttachments('req-1'), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual(mockData);
    expect(mockList).toHaveBeenCalledWith('req-1', undefined);
  });

  it('should fetch attachments with itemId', async () => {
    const mockData = [{ id: 'att-1', filename: 'receipt.pdf' }];
    mockList.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useReimbursementAttachments('req-1', 'item-1'), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockList).toHaveBeenCalledWith('req-1', 'item-1');
  });

  it('should be disabled when requestId is empty', async () => {
    const { result } = renderHook(() => useReimbursementAttachments(''), { wrapper: createWrapper() });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.fetchStatus).toBe('idle');
  });
});

describe('useUploadReimbursementAttachment', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should upload attachment and invalidate queries', async () => {
    const mockData = { id: 'att-1', filename: 'receipt.pdf' };
    mockUpload.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useUploadReimbursementAttachment(), { wrapper: createWrapper() });

    const file = new File(['content'], 'receipt.pdf', { type: 'application/pdf' });
    await result.current.mutateAsync({ requestId: 'req-1', file, options: { attachmentType: 'receipt' } });

    expect(mockUpload).toHaveBeenCalledWith('req-1', file, { attachmentType: 'receipt' });
  });
});

describe('useDeleteReimbursementAttachment', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should delete attachment and invalidate queries', async () => {
    mockDelete.mockResolvedValueOnce(undefined);

    const { result } = renderHook(() => useDeleteReimbursementAttachment(), { wrapper: createWrapper() });

    await result.current.mutateAsync('att-1');

    expect(mockDelete).toHaveBeenCalledWith('att-1');
  });
});

describe('useDownloadReimbursementAttachment', () => {
  beforeEach(() => vi.clearAllMocks());

  it('should download attachment', async () => {
    const mockBlob = new Blob(['content'], { type: 'application/pdf' });
    mockDownload.mockResolvedValueOnce(mockBlob);

    const { result } = renderHook(() => useDownloadReimbursementAttachment(), { wrapper: createWrapper() });

    await result.current.mutateAsync('att-1');

    expect(mockDownload).toHaveBeenCalledWith('att-1');
  });
});
