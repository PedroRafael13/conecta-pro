import { describe, it, expect } from 'vitest';
import {
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
  reimbursementKeys,
  useCreateReimbursementItem,
  useUpdateReimbursementItem,
  useDeleteReimbursementItem,
  useReimbursementAttachments,
  useUploadReimbursementAttachment,
  useDeleteReimbursementAttachment,
  useDownloadReimbursementAttachment,
  attachmentKeys,
  usePendingReimbursementApprovals,
  useStartReimbursementAnalysis,
  useApproveReimbursement,
  useRejectReimbursement,
  useReturnReimbursementToDraft,
  approvalKeys,
  useReadyForPaymentReimbursements,
  useProcessReimbursementPayment,
  paymentKeys,
} from '../index';

describe('hooks/reimbursement/index re-exports', () => {
  it('should re-export all request hooks', () => {
    expect(useReimbursementRequests).toBeDefined();
    expect(useMyReimbursementRequests).toBeDefined();
    expect(useReimbursementRequest).toBeDefined();
    expect(useReimbursementStats).toBeDefined();
    expect(useExpenseCategories).toBeDefined();
    expect(useExpenseTypes).toBeDefined();
    expect(useAttachmentTypes).toBeDefined();
    expect(useCreateReimbursementRequest).toBeDefined();
    expect(useUpdateReimbursementRequest).toBeDefined();
    expect(useDeleteReimbursementRequest).toBeDefined();
    expect(useSubmitReimbursementRequest).toBeDefined();
    expect(useCancelReimbursementRequest).toBeDefined();
    expect(reimbursementKeys).toBeDefined();
  });

  it('should re-export all item hooks', () => {
    expect(useCreateReimbursementItem).toBeDefined();
    expect(useUpdateReimbursementItem).toBeDefined();
    expect(useDeleteReimbursementItem).toBeDefined();
  });

  it('should re-export all attachment hooks', () => {
    expect(useReimbursementAttachments).toBeDefined();
    expect(useUploadReimbursementAttachment).toBeDefined();
    expect(useDeleteReimbursementAttachment).toBeDefined();
    expect(useDownloadReimbursementAttachment).toBeDefined();
    expect(attachmentKeys).toBeDefined();
  });

  it('should re-export all approval hooks', () => {
    expect(usePendingReimbursementApprovals).toBeDefined();
    expect(useStartReimbursementAnalysis).toBeDefined();
    expect(useApproveReimbursement).toBeDefined();
    expect(useRejectReimbursement).toBeDefined();
    expect(useReturnReimbursementToDraft).toBeDefined();
    expect(approvalKeys).toBeDefined();
  });

  it('should re-export all payment hooks', () => {
    expect(useReadyForPaymentReimbursements).toBeDefined();
    expect(useProcessReimbursementPayment).toBeDefined();
    expect(paymentKeys).toBeDefined();
  });
});
